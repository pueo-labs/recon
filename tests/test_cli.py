# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportMissingParameterType=none, reportUnknownArgumentType=none, reportUnknownMemberType=none
# pyright: reportUnknownParameterType=none
"""Unit tests for CLI application."""

from __future__ import annotations

import json
import re
from dataclasses import replace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import typer
import typer.rich_utils as typer_rich_utils
from typer.core import TyperGroup, TyperOption
from typer.main import get_command
from typer.testing import CliRunner

from recon_tool.cli import app
from recon_tool.cli.doctor import DoctorCheck
from recon_tool.collection_view import collection_observable_results
from recon_tool.formatter.source_ladder import LadderState
from recon_tool.models import (
    ConfidenceLevel,
    ReconLookupError,
    SourceResult,
    TenantInfo,
)

runner = CliRunner()


def _strip_ansi(value: str) -> str:
    """Return Rich-rendered help text without terminal color sequences."""
    return re.sub(r"\x1b\[[0-9;]*m", "", value)


SAMPLE_INFO = TenantInfo(
    tenant_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    display_name="Synthetic Alpha Ltd",
    default_domain="alpha.onmicrosoft.com",
    queried_domain="alpha.invalid",
    confidence=ConfidenceLevel.HIGH,
    region="NA",
    sources=("oidc_discovery", "azure_ad_metadata"),
    services=("Exchange Online", "Microsoft 365"),
    slugs=("microsoft365",),
)

SAMPLE_RESULTS = [
    SourceResult(source_name="oidc_discovery", tenant_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", region="NA"),
    SourceResult(source_name="azure_ad_metadata", tenant_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee", region="NA"),
    SourceResult(source_name="dns_records", error="no indicators"),
]

RESOLVE_PATH = "recon_tool.resolver.resolve_tenant"


class TestHelp:
    def test_help_shows_usage(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        collapsed = " ".join(_strip_ansi(result.output).replace("│", " ").split())
        assert "Usage: recon [OPTIONS] [DOMAIN | COMMAND [ARGS]...]" in collapsed
        assert "recon" in collapsed.lower()
        assert "Start with recon DOMAIN" in collapsed
        assert "run recon with no arguments for examples" in collapsed

    def test_lookup_help(self) -> None:
        result = runner.invoke(app, ["lookup", "--help"])
        assert result.exit_code == 0
        plain = _strip_ansi(result.output)
        assert "--json" in plain
        assert "--md" in plain
        assert "--full" in plain
        assert "--strict" in plain
        collapsed = " ".join(plain.replace("│", " ").split())
        assert "Services are shown by default; retained for compatibility" in collapsed
        assert "Grouped Markdown report; --full is the connection map" in collapsed
        assert "Expanded evidence, all domains, posture, and host classes" in collapsed
        assert "configured recursive resolver" in collapsed
        assert "authoritative DNS may observe the resulting traffic" in collapsed
        assert "MTA-STS policy fetch is the only default target-owned HTTP/application request" in collapsed
        assert "High confidence with at least three sources" in collapsed
        assert "Evidence and validation remain unchanged, as do confidence values" in collapsed
        assert "Enabled by default; pass --no-fusion for deterministic output" in collapsed
        assert "transition notice" not in collapsed
        assert "v3-ready" not in collapsed
        assert "across future releases" not in collapsed

    def test_doctor_help_distinguishes_online_connectivity(self) -> None:
        result = runner.invoke(app, ["doctor", "--help"])

        assert result.exit_code == 0
        collapsed = " ".join(_strip_ansi(result.output).replace("│", " ").split())
        assert "installation health" in collapsed
        assert "online source connectivity" in collapsed
        assert "emit an mcpServers reference config" in collapsed
        assert "copy-pasteable client config" not in collapsed

    def test_lookup_help_groups_options_by_user_task(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(typer_rich_utils, "MAX_WIDTH", 80)
        result = runner.invoke(app, ["lookup", "--help"])

        assert result.exit_code == 0
        plain = _strip_ansi(result.output)
        collapsed = " ".join(plain.replace("│", " ").split())
        assert (
            "Start with recon DOMAIN. Add --full for detail, --explain for evidence, "
            "or --json for automation. Google CSE and BIMI probes require --direct-probes; "
            "MTA-STS is the only default target-owned HTTP request." in collapsed
        )

        headings = (
            "Output",
            "Report detail and wording",
            "Collection, cache, and scope",
            "Analysis modes",
            "Evidence model",
        )
        positions = tuple(plain.index(heading) for heading in headings)
        assert positions == tuple(sorted(positions))
        output, detail, collection, analysis, evidence = positions
        assert output < plain.index("--plain") < detail
        assert detail < plain.index("--services") < collection
        assert detail < plain.index("--confidence-mode") < collection
        assert collection < plain.index("--no-cache") < analysis
        assert analysis < plain.index("--compare") < evidence
        assert evidence < plain.index("--fusion")

        root_command = get_command(app)
        assert isinstance(root_command, TyperGroup)
        lookup_command = root_command.commands["lookup"]
        options = tuple(param for param in lookup_command.params if isinstance(param, TyperOption))
        assert len(options) == 28
        primary_tokens = tuple(next(token for token in option.opts if token.startswith("--")) for option in options)
        assert all(token in plain for token in primary_tokens)

    @pytest.mark.parametrize(
        "args",
        [
            ["--fix", "--mcp"],
            ["--fix", "--client", "cursor"],
            ["--mcp", "--client", "cursor"],
        ],
    )
    def test_doctor_modes_are_mutually_exclusive(self, args: list[str]) -> None:
        result = runner.invoke(app, ["doctor", *args])

        assert result.exit_code == 2
        assert "choose exactly one" in result.output.lower()

    def test_welcome_prioritizes_primary_accessible_and_automation_paths(self) -> None:
        result = runner.invoke(app, [])

        assert result.exit_code == 0
        collapsed = " ".join(_strip_ansi(result.output).split())
        assert "--plain" in collapsed
        assert "screen readers and grep" in collapsed
        assert "--md" in collapsed
        assert "--full is the connection map" in collapsed
        assert "--json" in collapsed
        assert "structured automation" in collapsed
        assert "--explain → evidence and explanation" in collapsed
        assert "full reasoning" not in collapsed
        assert "mcp install --help" in collapsed
        assert "connect an MCP client" in collapsed
        assert "recon mcp → start" not in collapsed
        assert "→ everything" not in collapsed
        assert "offline install check" in collapsed
        assert "python -m recon_tool --version" in collapsed
        assert "public-suffix domain" in collapsed
        assert "DNS queries" in collapsed
        assert "MTA-STS" in collapsed
        assert "Google CSE and BIMI direct probes run only with --direct-probes" in collapsed
        assert "stray public residue" in collapsed
        assert "High confidence" in collapsed
        assert "real lookup commands, not an offline demo" in collapsed
        assert "default 24-hour result cache" in collapsed
        assert "--no-cache for fresh collection" in collapsed
        assert "publish little or nothing" not in collapsed

    def test_version_flag(self) -> None:
        from recon_tool.cli import version_callback

        with pytest.raises(typer.Exit):
            version_callback(True)


class TestDirectDomainLookup:
    """``recon alpha.invalid`` (no ``lookup`` subcommand) routes to the lookup
    command via ``_DomainGroup``. This is exercised through CliRunner: the
    routing runs inside Click's command resolution, which CliRunner drives."""

    @patch(RESOLVE_PATH, new_callable=AsyncMock)
    def test_bare_domain_routes_to_lookup(self, mock_resolve) -> None:
        # Regression guard for the shorthand routing. Typer >=0.25 vendors its
        # own Click, so the group's domain-to-lookup routing must not depend on
        # catching the top-level ``click.UsageError`` (it does not see the
        # vendored one). A bare domain must reach the lookup command, not error
        # with "No such command".
        mock_resolve.return_value = (SAMPLE_INFO, SAMPLE_RESULTS)
        result = runner.invoke(app, ["alpha.invalid", "--no-cache"])
        assert result.exit_code == 0, result.output
        assert "No such command" not in result.output
        assert "Synthetic Alpha Ltd" in result.output

    def test_undotted_domain_attempt_uses_domain_validation(self) -> None:
        # Hostnames without a dot (or other invalid tokens) must not fall through
        # as Click "No such command". Route them to lookup so the user gets a
        # domain-format rejection.
        result = runner.invoke(app, ["alpha"])
        assert result.exit_code == 2
        assert "No such command" not in result.output
        assert "Invalid domain format" in result.output
        collapsed = " ".join(result.output.split())
        assert "Expected a domain with a public suffix, such as example.com." in collapsed
        assert "Run recon with no arguments for examples." in collapsed

    def test_malformed_undotted_token_is_not_unknown_command(self) -> None:
        result = runner.invoke(app, ["not-a-valid-domain!!!"])
        assert result.exit_code == 2
        assert "No such command" not in result.output
        assert "Invalid domain format" in result.output
        collapsed = " ".join(result.output.split())
        assert collapsed.count("Run recon with no arguments for examples.") == 1

    def test_root_help_uses_passive_public_sources_summary(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Passive domain intelligence from public sources" in result.output
        assert "Start with recon DOMAIN" in result.output

    @patch(RESOLVE_PATH, new_callable=AsyncMock)
    def test_lookup_default(self, mock_resolve) -> None:
        mock_resolve.return_value = (SAMPLE_INFO, SAMPLE_RESULTS)
        # ``--no-cache`` ensures the mocked resolver is actually called
        # rather than the test reading whatever is in the developer's
        # ``~/.recon/cache/`` from prior real runs.
        result = runner.invoke(app, ["lookup", "alpha.invalid", "--no-cache"])
        assert result.exit_code == 0
        assert "Synthetic Alpha Ltd" in result.output

    @patch(RESOLVE_PATH, new_callable=AsyncMock)
    def test_lookup_json(self, mock_resolve) -> None:
        mock_resolve.return_value = (SAMPLE_INFO, SAMPLE_RESULTS)
        result = runner.invoke(app, ["lookup", "alpha.invalid", "--json", "--no-cache"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["display_name"] == "Synthetic Alpha Ltd"

    @patch(RESOLVE_PATH, new_callable=AsyncMock)
    def test_lookup_md(self, mock_resolve) -> None:
        mock_resolve.return_value = (SAMPLE_INFO, SAMPLE_RESULTS)
        result = runner.invoke(app, ["lookup", "alpha.invalid", "--md", "--no-cache"])
        assert result.exit_code == 0
        assert "# " in result.output

    @patch(RESOLVE_PATH, new_callable=AsyncMock)
    def test_lookup_plain(self, mock_resolve) -> None:
        mock_resolve.return_value = (SAMPLE_INFO, SAMPLE_RESULTS)
        result = runner.invoke(app, ["lookup", "alpha.invalid", "--plain", "--no-cache"])
        assert result.exit_code == 0
        assert "queried_domain: alpha.invalid" in result.output
        # Linear text — no box-drawing characters.
        assert "─" not in result.output
        assert "│" not in result.output

    def test_lookup_json_plain_mutually_exclusive(self) -> None:
        result = runner.invoke(app, ["lookup", "alpha.invalid", "--json", "--plain"])
        assert result.exit_code == 2

    def test_lookup_plain_rejected_with_alternate_modes(self) -> None:
        # --plain only governs the standard render; combining it with a mode
        # that has its own output is rejected, not silently ignored.
        for mode in ("--exposure", "--gaps", "--chain"):
            result = runner.invoke(app, ["lookup", "alpha.invalid", "--plain", mode])
            assert result.exit_code == 2, f"--plain {mode} should be rejected"


class TestLookupSubcommand:
    @patch(RESOLVE_PATH, new_callable=AsyncMock)
    def test_lookup_subcommand(self, mock_resolve) -> None:
        mock_resolve.return_value = (SAMPLE_INFO, SAMPLE_RESULTS)
        result = runner.invoke(app, ["lookup", "alpha.invalid", "--no-cache"])
        assert result.exit_code == 0
        assert "Synthetic Alpha Ltd" in result.output

    @patch(RESOLVE_PATH, new_callable=AsyncMock)
    def test_verbose_flag(self, mock_resolve) -> None:
        mock_resolve.return_value = (SAMPLE_INFO, SAMPLE_RESULTS)
        result = runner.invoke(app, ["lookup", "alpha.invalid", "--verbose", "--no-cache"])
        assert result.exit_code == 0
        assert "oidc_discovery" in result.output

    @patch(RESOLVE_PATH, new_callable=AsyncMock)
    def test_verbose_keeps_a_match_the_observable_projection_would_drop(self, mock_resolve: AsyncMock) -> None:
        """The health line and --verbose both classify the resolver results.

        Projecting this result clears the tenant id because the OIDC channel
        is marked degraded, which would turn the ladder match into no match.
        """
        raw = SourceResult(
            source_name="oidc_discovery",
            tenant_id="synthetic-tenant",
            degraded_sources=("oidc_discovery",),
        )
        projected = LadderState.planned(skip_ct=False, active_probes=False)
        projected.finalize(collection_observable_results([raw]))
        projected_outcome = projected.outcome("oidc_discovery")
        assert projected_outcome is not None
        assert projected_outcome.state == "no_match"

        mock_resolve.return_value = (SAMPLE_INFO, [raw])
        result = runner.invoke(app, ["lookup", "alpha.invalid", "--verbose", "--no-cache"])
        assert result.exit_code == 0
        assert "1 source: 1 matched" in result.output
        assert "match oidc_discovery: tenant ID found" in result.output
        assert "no match oidc_discovery" not in result.output

    @patch("recon_tool.cache.cache_get")
    @patch(RESOLVE_PATH, new_callable=AsyncMock)
    def test_verbose_cache_hit_does_not_invent_unit_states(
        self, mock_resolve: AsyncMock, mock_cache_get: MagicMock
    ) -> None:
        """A reused result has no resolver list and no source-health line.

        The synthetic reconstruction omits certificate-transparency counts
        and the MTA-STS mode, so ladder rows would call both no match.
        """
        mock_cache_get.return_value = replace(
            SAMPLE_INFO,
            sources=("oidc_discovery", "dns_records"),
            ct_subdomain_count=4,
            mta_sts_mode="enforce",
            cached_at="2026-11-16T00:00:00+00:00",
        )
        mock_resolve.side_effect = AssertionError("a cache hit must not resolve")
        result = runner.invoke(app, ["lookup", "alpha.invalid", "--verbose"])
        assert result.exit_code == 0, result.output
        assert "Synthetic Alpha Ltd" in result.output
        assert " ct:" not in result.output
        assert " mta_sts:" not in result.output
        mock_resolve.assert_not_called()

    @patch(RESOLVE_PATH, new_callable=AsyncMock)
    def test_sources_flag(self, mock_resolve) -> None:
        mock_resolve.return_value = (SAMPLE_INFO, SAMPLE_RESULTS)
        result = runner.invoke(app, ["lookup", "alpha.invalid", "--sources"])
        assert result.exit_code == 0
        assert "Source Details" in result.output

    def test_strict_alias_sets_confidence_mode(self, monkeypatch) -> None:
        seen = {}

        async def fake_lookup(_domain, options) -> None:
            seen["confidence_mode"] = options.confidence_mode

        monkeypatch.setattr("recon_tool.cli._lookup", fake_lookup)
        result = runner.invoke(app, ["lookup", "alpha.invalid", "--strict"])
        assert result.exit_code == 0
        assert seen["confidence_mode"] == "strict"

    def test_confidence_mode_rejects_typo(self) -> None:
        result = runner.invoke(app, ["lookup", "alpha.invalid", "--confidence-mode", "scrict"])
        assert result.exit_code == 2
        assert "hedged" in result.output
        assert "strict" in result.output


class TestErrors:
    def test_invalid_domain(self) -> None:
        result = runner.invoke(app, ["lookup", "not a domain"])
        assert result.exit_code == 2

    def test_empty_domain(self) -> None:
        result = runner.invoke(app, ["lookup", "   "])
        assert result.exit_code == 2

    @patch(RESOLVE_PATH, new_callable=AsyncMock)
    def test_all_sources_failed(self, mock_resolve) -> None:
        mock_resolve.side_effect = ReconLookupError(
            domain="unknown.invalid",
            message="No tenant found",
            error_type="all_sources_failed",
        )
        result = runner.invoke(app, ["lookup", "unknown.invalid"])
        assert result.exit_code == 4
        assert "No tenant found" in result.output

    @patch(RESOLVE_PATH, new_callable=AsyncMock)
    def test_unexpected_error(self, mock_resolve) -> None:
        mock_resolve.side_effect = RuntimeError("connection failed")
        result = runner.invoke(app, ["lookup", "example.com", "--no-cache"])
        assert result.exit_code == 4
        assert "connection failed" in result.output


class TestDoctor:
    @patch("dns.resolver.resolve")
    @patch("httpx.AsyncClient")
    def test_doctor_all_pass(self, mock_http_cls, mock_dns) -> None:
        import dns.resolver

        def _resolve(qname: str, *args: object, **kwargs: object) -> list[MagicMock]:
            # Reserved `.invalid` names never exist; a stub that answered them
            # would correctly draw the doctor's resolver warning.
            if str(qname).endswith(".invalid"):
                raise dns.resolver.NXDOMAIN()
            return [MagicMock()]

        mock_dns.side_effect = _resolve
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_http_cls.return_value = mock_client

        from recon_tool import __version__

        with (
            patch(
                "recon_tool.cli.doctor._doctor_path_launcher_check",
                return_value=DoctorCheck("PATH recon launcher", "ok", "test launcher matches running package"),
            ),
            patch("recon_tool.updater.fetch_latest_version", return_value=__version__),
        ):
            result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0
        assert "All checks passed" in result.output


class TestRootOptionPlacement:
    """Root ``--color/--no-color`` work after the domain or command (#224), other
    root-only options name the working form, and a near-miss command typo
    followed by more arguments gets a suggestion instead of an extra-argument error."""

    @pytest.fixture
    def color_calls(self, monkeypatch: pytest.MonkeyPatch) -> list[bool | None]:
        calls: list[bool | None] = []
        monkeypatch.setattr("recon_tool.formatter.set_color_override", calls.append)
        return calls

    @pytest.fixture
    def looked_up(self, monkeypatch: pytest.MonkeyPatch) -> list[str]:
        domains: list[str] = []

        async def fake_lookup(domain, _options) -> None:
            domains.append(domain)

        monkeypatch.setattr("recon_tool.cli._lookup", fake_lookup)
        return domains

    @pytest.mark.parametrize(
        ("args", "expected"),
        [
            (["--no-color", "example.com"], False),
            (["example.com", "--no-color"], False),
            (["lookup", "example.com", "--no-color"], False),
            (["lookup", "example.com", "--json", "--color"], True),
            (["--color", "example.com", "--no-color"], False),
            (["--no-color", "lookup", "example.com", "--color"], True),
        ],
    )
    def test_color_flag_position_is_equivalent_and_last_wins(
        self, args: list[str], expected: bool, color_calls: list[bool | None], looked_up: list[str]
    ) -> None:
        result = runner.invoke(app, args)
        assert result.exit_code == 0, result.output
        assert color_calls == [expected]
        assert looked_up == ["example.com"]

    @pytest.mark.parametrize(
        "args",
        [["doctor", "--no-color", "--help"], ["cache", "show", "--no-color", "--help"], ["review", "-h", "--no-color"]],
    )
    def test_trailing_no_color_is_accepted_by_other_commands(
        self, args: list[str], color_calls: list[bool | None]
    ) -> None:
        result = runner.invoke(app, args)
        assert result.exit_code == 0, result.output
        assert color_calls == [False]

    def test_trailing_no_color_disables_console_color(self, looked_up: list[str]) -> None:
        from recon_tool.formatter import get_console, set_color_override

        try:
            result = runner.invoke(app, ["example.com", "--no-color"])
            assert result.exit_code == 0, result.output
            assert get_console().no_color is True
        finally:
            set_color_override(None)

    @pytest.mark.parametrize("command", [[], ["lookup"]])
    @pytest.mark.parametrize("value", ["--ascii", "--color", "--no-color", "--debug", "--version", "-V"])
    def test_lookup_keeps_flag_shaped_snapshot_path(
        self, monkeypatch: pytest.MonkeyPatch, command: list[str], value: str, color_calls: list[bool | None]
    ) -> None:
        snapshots: list[str | None] = []

        async def fake_lookup(_domain, options) -> None:
            snapshots.append(options.compare_file)

        monkeypatch.setattr("recon_tool.cli._lookup", fake_lookup)
        result = runner.invoke(app, [*command, "example.com", "--compare", value])

        assert result.exit_code == 0, result.output
        assert snapshots == [value]
        assert color_calls == []

    def test_root_flag_after_separator_spelling_used_as_value(
        self, looked_up: list[str], color_calls: list[bool | None]
    ) -> None:
        result = runner.invoke(app, ["example.com", "--compare", "--", "--no-color"])
        assert result.exit_code == 0, result.output
        assert looked_up == ["example.com"]
        assert color_calls == [False]

    @pytest.mark.parametrize(
        "args",
        [
            ["fingerprints", "new", "-p", "--debug", "--help"],
            ["mcp", "install", "-s", "--debug", "--help"],
            ["lookup", "example.com", "-st", "--debug", "--help"],
        ],
    )
    def test_nested_aliases_and_short_clusters_keep_their_values(self, args: list[str]) -> None:
        result = runner.invoke(app, args)
        assert result.exit_code == 0, result.output
        assert "Usage:" in result.output

    @pytest.mark.parametrize("args", [["example.com", "-p", "--no-color"], ["example.com", "-s", "--no-color"]])
    def test_lookup_boolean_alias_does_not_consume_root_flag(
        self, args: list[str], looked_up: list[str], color_calls: list[bool | None]
    ) -> None:
        result = runner.invoke(app, args)
        assert result.exit_code == 0, result.output
        assert looked_up == ["example.com"]
        assert color_calls == [False]

    @pytest.mark.parametrize("option", ["--compare=baseline.json", "-t30", "-st30"])
    def test_attached_option_value_does_not_consume_following_root_flag(
        self, option: str, looked_up: list[str], color_calls: list[bool | None]
    ) -> None:
        result = runner.invoke(app, ["example.com", option, "--no-color"])
        assert result.exit_code == 0, result.output
        assert looked_up == ["example.com"]
        assert color_calls == [False]

    def test_tokens_after_double_dash_are_not_hoisted(
        self, color_calls: list[bool | None], looked_up: list[str]
    ) -> None:
        result = runner.invoke(app, ["lookup", "--", "--no-color"])
        assert result.exit_code == 0, result.output
        assert color_calls == []
        assert looked_up == ["--no-color"]

    @pytest.mark.parametrize(
        ("args", "expected"),
        [
            (["example.com", "--debug"], "--debug is a global option. Place it before the domain or command"),
            (["lookup", "example.com", "--debug"], "for example: recon --debug example.com"),
            (
                ["lookup", "example.com", "--version"],
                "--version is a global option. Run it on its own: recon --version",
            ),
            (["example.com", "-V"], "Run it on its own: recon -V"),
        ],
    )
    def test_misplaced_root_only_option_names_working_form(
        self, args: list[str], expected: str, looked_up: list[str]
    ) -> None:
        result = runner.invoke(app, args)
        assert result.exit_code == 2
        assert expected in " ".join(_strip_ansi(result.output).replace("│", " ").split())
        assert "No such option" not in result.output
        assert looked_up == []

    def test_misplaced_root_option_check_is_skipped_while_completing(self) -> None:
        ctx = get_command(app).make_context("recon", ["example.com", "--debug"], resilient_parsing=True)
        assert ctx.resilient_parsing

    @pytest.mark.parametrize(
        ("args", "typo", "command"),
        [
            (["lookpu", "example.com"], "lookpu", "lookup"),
            (["Lookup", "example.com"], "Lookup", "lookup"),
            (["batc", "domains.txt", "--json"], "batc", "batch"),
            (["doctr", "--no-color", "extra"], "doctr", "doctor"),
        ],
    )
    def test_command_typo_with_extra_arguments_suggests_command(
        self, args: list[str], typo: str, command: str, color_calls: list[bool | None], looked_up: list[str]
    ) -> None:
        result = runner.invoke(app, args)
        assert result.exit_code == 2
        collapsed = " ".join(_strip_ansi(result.output).replace("│", " ").split())
        assert f'Unknown command "{typo}". Did you mean "{command}"?' in collapsed
        assert "unexpected extra argument" not in collapsed
        assert looked_up == []

    @pytest.mark.parametrize(
        "args",
        [["lookpu"], ["lookpu", "--json"], ["lookpu", "--profile", "fintech"], ["lookup.example"]],
    )
    def test_near_miss_without_extra_arguments_stays_domain_input(self, args: list[str], looked_up: list[str]) -> None:
        result = runner.invoke(app, args)
        assert result.exit_code == 0, result.output
        assert looked_up == [args[0]]

    def test_distant_first_token_keeps_extra_argument_error(self, looked_up: list[str]) -> None:
        result = runner.invoke(app, ["lookup.example", "extra"])
        assert result.exit_code == 2
        assert "Got unexpected extra argument(s) (extra)" in result.output
        assert "Unknown command" not in result.output
        assert looked_up == []

    def test_typo_suggestion_is_skipped_while_completing(self) -> None:
        ctx = get_command(app).make_context("recon", ["lookpu", "example.com"], resilient_parsing=True)
        group = ctx.command
        assert isinstance(group, TyperGroup)
        name, _command, _args = group.resolve_command(ctx, ["lookpu", "example.com"])
        assert name == "lookup"


class TestRoutingHelpers:
    def test_hoist_leaves_option_only_and_separator_first_args_alone(self) -> None:
        from recon_tool.cli.routing import hoist_trailing_color_flags

        assert hoist_trailing_color_flags(["--no-color"]) == ["--no-color"]
        assert hoist_trailing_color_flags(["--", "--no-color"]) == ["--", "--no-color"]
        assert hoist_trailing_color_flags(["--debug", "-", "--color"]) == ["--debug", "--color", "-"]

    def test_misplaced_root_option_ignores_leading_and_separated_tokens(self) -> None:
        from recon_tool.cli.routing import misplaced_root_option

        assert misplaced_root_option(["--debug", "example.com"]) is None
        assert misplaced_root_option(["--debug"]) is None
        assert misplaced_root_option(["lookup", "--", "--debug"]) is None
        assert misplaced_root_option(["lookup", "example.com", "-V"]) == "-V"

    @pytest.mark.parametrize(
        ("token", "expected"),
        [("lookpu", "lookup"), ("revew", "review"), ("MCP", "mcp"), ("deltaa", "delta"), ("example.com", None)],
    )
    def test_near_miss_command_uses_edit_distance_two(self, token: str, expected: str | None) -> None:
        from recon_tool.cli import _SUBCOMMANDS  # pyright: ignore[reportPrivateUsage]
        from recon_tool.cli.routing import near_miss_command

        assert near_miss_command(token, _SUBCOMMANDS) == expected

    def test_near_miss_command_rejects_distance_three(self) -> None:
        from recon_tool.cli.routing import near_miss_command

        assert near_miss_command("lkpu", ["lookup"]) is None
        assert near_miss_command("lookup", []) is None
