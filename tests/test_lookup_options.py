# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportMissingParameterType=none, reportUnknownArgumentType=none, reportUnknownMemberType=none
# pyright: reportUnknownParameterType=none, reportUnknownVariableType=none
from __future__ import annotations

import pytest

from recon_tool.cli.options import (
    LookupDisplayOptions,
    LookupExecutionOptions,
    LookupInferenceOptions,
    LookupOperationMode,
    LookupOperationOptions,
    LookupOptions,
    LookupOutputMode,
    LookupOutputOptions,
)


def _options(
    *,
    output: LookupOutputOptions | None = None,
    operation: LookupOperationOptions | None = None,
    display: LookupDisplayOptions | None = None,
) -> LookupOptions:
    return LookupOptions(
        output=output or LookupOutputOptions(),
        display=display or LookupDisplayOptions(),
        operation=operation or LookupOperationOptions(),
        inference=LookupInferenceOptions(),
        execution=LookupExecutionOptions(),
    )


def test_output_mode_selects_first_explicit_renderer() -> None:
    assert LookupOutputOptions().mode is LookupOutputMode.PANEL
    assert LookupOutputOptions(json_output=True).mode is LookupOutputMode.JSON
    assert LookupOutputOptions(markdown=True).mode is LookupOutputMode.MARKDOWN
    assert LookupOutputOptions(plain=True).mode is LookupOutputMode.PLAIN


def test_output_options_reject_multiple_renderers() -> None:
    options = _options(output=LookupOutputOptions(json_output=True, plain=True))

    assert options.validation_error() == "--json, --md, and --plain are mutually exclusive"


def test_display_options_normalize_full_and_profile() -> None:
    full = LookupDisplayOptions.from_flags(
        services=False,
        domains=False,
        full=True,
        verbose=False,
        sources=False,
        posture=False,
        explain=False,
        profile=None,
        confidence_mode="hedged",
    )
    profiled = LookupDisplayOptions.from_flags(
        services=False,
        domains=False,
        full=False,
        verbose=False,
        sources=False,
        posture=False,
        explain=False,
        profile="fintech",
        confidence_mode="strict",
    )

    assert full.show_services
    assert full.show_domains
    assert full.verbose
    assert full.show_posture
    assert profiled.show_posture
    assert profiled.profile_name == "fintech"
    assert profiled.confidence_mode == "strict"


def test_operation_mode_selects_requested_pipeline() -> None:
    assert LookupOperationOptions().mode is LookupOperationMode.STANDARD
    assert LookupOperationOptions(compare_file="snapshot.json").mode is LookupOperationMode.COMPARE
    assert LookupOperationOptions(chain_mode=True).mode is LookupOperationMode.CHAIN
    assert LookupOperationOptions(show_exposure=True).mode is LookupOperationMode.EXPOSURE
    assert LookupOperationOptions(show_gaps=True).mode is LookupOperationMode.GAPS


def test_operation_options_reject_ambiguous_modes() -> None:
    assert (
        _options(operation=LookupOperationOptions(chain_mode=True, compare_file="snapshot.json")).validation_error()
        == "--chain and --compare are mutually exclusive"
    )
    assert (
        _options(operation=LookupOperationOptions(show_exposure=True, show_gaps=True)).validation_error()
        == "--exposure and --gaps are mutually exclusive"
    )
    assert _options(operation=LookupOperationOptions(chain_depth=2)).validation_error() == "--depth requires --chain"


def test_non_standard_modes_reject_unimplemented_renderers() -> None:
    markdown_chain = _options(
        output=LookupOutputOptions(markdown=True),
        operation=LookupOperationOptions(chain_mode=True),
    )
    plain_exposure = _options(
        output=LookupOutputOptions(plain=True),
        operation=LookupOperationOptions(show_exposure=True),
    )

    assert markdown_chain.validation_error() == "--md cannot be combined with --chain/--compare/--exposure/--gaps"
    assert plain_exposure.validation_error() == "--plain cannot be combined with --chain/--compare/--exposure/--gaps"


class TestCollectionScopeIsNotSharedThroughTheCache:
    """The disk cache key is the domain alone, so scope must gate sharing.

    A --skip-ct result is CT-degraded and a --direct-probes result carries
    opt-in probe data. Writing either under the shared domain key let a later
    full lookup be answered from the degraded entry for the whole TTL window,
    with no network call and no signal. The MCP server already refuses to share
    a skip_ct result for exactly this reason.
    """

    @staticmethod
    def _scoped(*, skip_ct: bool = False, active_probes: bool = False) -> LookupOptions:
        return LookupOptions(
            output=LookupOutputOptions(),
            display=LookupDisplayOptions(),
            operation=LookupOperationOptions(),
            inference=LookupInferenceOptions(),
            execution=LookupExecutionOptions(skip_ct=skip_ct, active_probes=active_probes),
        )

    def test_skip_ct_result_is_not_written_to_the_shared_cache(self, monkeypatch, tmp_path) -> None:
        import asyncio
        import importlib

        from recon_tool.models import ConfidenceLevel, TenantInfo

        monkeypatch.setenv("RECON_CONFIG_DIR", str(tmp_path))
        cli_lookup = importlib.import_module("recon_tool.cli.lookup")

        calls: list[bool] = []

        async def _fake_resolve(_console: object, _validated: str, **kwargs: object):
            skip_ct = bool(kwargs["skip_ct"])
            calls.append(skip_ct)
            return (
                TenantInfo(
                    tenant_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                    display_name="Synthetic Alpha",
                    default_domain="alpha.onmicrosoft.com",
                    queried_domain="alpha.invalid",
                    confidence=ConfidenceLevel.HIGH,
                    ct_subdomain_count=0 if skip_ct else 42,
                ),
                [],
            )

        monkeypatch.setattr(cli_lookup, "_resolve_with_spinner", _fake_resolve)

        asyncio.run(cli_lookup._lookup_resolve_standard(None, "alpha.invalid", self._scoped(skip_ct=True)))
        info, _results, collected = asyncio.run(
            cli_lookup._lookup_resolve_standard(None, "alpha.invalid", self._scoped())
        )
        assert collected is True

        # The full lookup must resolve rather than reuse the degraded entry.
        assert calls == [True, False]
        assert info.ct_subdomain_count == 42


class TestFlagCombinationsAreRejectedNotIgnored:
    """A supplied flag must never be silently discarded.

    ``--compare ""`` is a supplied path, not an absent flag, but truthiness
    treated it as absent: the run fell back to a standard lookup, and the
    ``--chain``/``--compare`` exclusion could not see it either.
    ``--explain-dag`` renders its own report and returns before the output
    branches, so pairing it with a renderer discarded the requested format and
    still exited 0 - a scripted ``--json --explain-dag | jq`` received prose.
    """

    def test_empty_compare_path_selects_compare_mode(self) -> None:
        from recon_tool.cli.options import LookupOperationMode, LookupOperationOptions

        assert LookupOperationOptions(compare_file="").mode is LookupOperationMode.COMPARE

    def test_empty_compare_path_still_conflicts_with_chain(self) -> None:
        from recon_tool.cli.options import LookupOperationOptions

        error = LookupOperationOptions(compare_file="", chain_mode=True).validation_error()
        assert error is not None
        assert "mutually exclusive" in error

    def test_absent_compare_remains_standard(self) -> None:
        from recon_tool.cli.options import LookupOperationMode, LookupOperationOptions

        assert LookupOperationOptions().mode is LookupOperationMode.STANDARD

    @pytest.mark.parametrize("renderer", ["json_output", "markdown", "plain"])
    def test_explain_dag_conflicts_with_an_output_renderer(self, renderer: str) -> None:
        from recon_tool.cli.options import (
            LookupDisplayOptions,
            LookupExecutionOptions,
            LookupInferenceOptions,
            LookupOperationOptions,
            LookupOptions,
            LookupOutputOptions,
        )

        options = LookupOptions(
            output=LookupOutputOptions(**{renderer: True}),
            display=LookupDisplayOptions(),
            operation=LookupOperationOptions(),
            inference=LookupInferenceOptions(explain_dag=True),
            execution=LookupExecutionOptions(),
        )

        error = options.validation_error()
        assert error is not None
        assert "--explain-dag" in error


class TestBatchInputBounds:
    """Batch input bounds must describe the input, not its terminator.

    The per-line cap counted the trailing newline, so a 1024-byte line was
    rejected mid-file but accepted as the final unterminated line: the same
    content produced different verdicts depending on where it sat. An
    unreadable path also exited as an internal fault rather than bad input.
    """

    @staticmethod
    def _line(content_bytes: int, *, newline: bool) -> str:
        suffix = ".example.com"
        body = "a" * (content_bytes - len(suffix)) + suffix
        return body + ("\n" if newline else "")

    @pytest.mark.parametrize("newline", [True, False])
    def test_cap_is_independent_of_line_position(self, newline: bool) -> None:
        import importlib
        import io

        batch = importlib.import_module("recon_tool.cli.batch")

        accepted = batch.read_batch_domains(io.StringIO(self._line(1024, newline=newline)))
        assert len(accepted) == 1

    def test_line_over_the_cap_is_rejected(self) -> None:
        import importlib
        import io

        batch = importlib.import_module("recon_tool.cli.batch")

        with pytest.raises(Exception, match="exceeds maximum length"):
            batch.read_batch_domains(io.StringIO(self._line(1025, newline=True)))


def test_chain_depth_outside_the_documented_range_is_rejected() -> None:
    """`--depth` is documented as 1 to 3 and the engine clamps to that.

    Out-of-range values used to be accepted and silently clamped, so
    `--depth 99` exited 0 having run a traversal the operator did not request
    and `--depth 0` ran depth 1.
    """
    for depth in (0, 4, 99, -1):
        assert (
            _options(operation=LookupOperationOptions(chain_mode=True, chain_depth=depth)).validation_error()
            == "--depth must be between 1 and 3"
        )

    for depth in (1, 2, 3):
        assert _options(operation=LookupOperationOptions(chain_mode=True, chain_depth=depth)).validation_error() is None
