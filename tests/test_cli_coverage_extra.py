# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportMissingParameterType=none, reportPrivateUsage=none, reportUnknownArgumentType=none
# pyright: reportUnknownParameterType=none
"""CLI coverage tests for paths not exercised by existing tests.

Targets: version callback, debug callback, doctor --fix template
scaffolding, batch error paths, MCP entrypoint import path. Uses
mocked resolver where network would be required.
"""

from __future__ import annotations

import importlib
import os
import tempfile
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

import click
import pytest
import typer
from typer.testing import CliRunner

from recon_tool.cli import _debug_callback, _doctor_fix, app, version_callback
from recon_tool.models import ConfidenceLevel, ReconLookupError, SourceResult, TenantInfo

runner = CliRunner()


def _fake_info() -> TenantInfo:
    return TenantInfo(
        tenant_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        display_name="Synthetic Alpha Ltd",
        default_domain="alpha.onmicrosoft.com",
        queried_domain="alpha.invalid",
        confidence=ConfidenceLevel.HIGH,
        region="NA",
        sources=("oidc_discovery", "user_realm", "dns_records"),
        services=("Microsoft 365",),
        slugs=("microsoft365",),
        auth_type="Managed",
        dmarc_policy="reject",
        domain_count=1,
    )


def _fake_source_results() -> list[SourceResult]:
    return [
        SourceResult(source_name="oidc_discovery", tenant_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890"),
        SourceResult(source_name="user_realm", display_name="Synthetic Alpha Ltd", m365_detected=True),
        SourceResult(source_name="dns_records", dmarc_policy="reject", detected_services=("Microsoft 365",)),
    ]


class TestVersionCallback:
    def test_version_false_is_noop(self) -> None:
        # Should not raise
        version_callback(False)

    def test_version_true_exits(self) -> None:
        with pytest.raises(typer.Exit):
            version_callback(True)


class TestDebugCallback:
    def test_debug_false_is_noop(self) -> None:
        _debug_callback(False)

    def test_debug_true_configures_logger(self) -> None:
        import logging

        loggers = [logging.getLogger(name) for name in ("recon", "recon_tool")]
        snapshots = [(logger.level, list(logger.handlers), logger.propagate) for logger in loggers]
        try:
            _debug_callback(True)
            assert all(logger.level == logging.DEBUG for logger in loggers)
            assert all(not logger.propagate for logger in loggers)
        finally:
            for logger, (level, handlers, propagate) in zip(loggers, snapshots, strict=True):
                logger.handlers[:] = handlers
                logger.setLevel(level)
                logger.propagate = propagate


class TestDoctorFix:
    @pytest.fixture(autouse=True)
    def _isolated_config(self, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
        with tempfile.TemporaryDirectory() as tmp:
            monkeypatch.setenv("RECON_CONFIG_DIR", tmp)
            yield

    def test_creates_fingerprints_and_signals_templates(self) -> None:
        assert _doctor_fix() is True
        config_dir = Path(os.environ["RECON_CONFIG_DIR"])
        assert (config_dir / "fingerprints.yaml").exists()
        assert (config_dir / "signals.yaml").exists()

    def test_does_not_overwrite_existing_files(self) -> None:
        config_dir = Path(os.environ["RECON_CONFIG_DIR"])
        existing = "custom content"
        (config_dir / "fingerprints.yaml").write_text(existing, encoding="utf-8")
        assert _doctor_fix() is True
        # Existing file preserved
        assert (config_dir / "fingerprints.yaml").read_text(encoding="utf-8") == existing
        # Other template still created
        assert (config_dir / "signals.yaml").exists()

    def test_handles_unwritable_config_dir(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A config-directory failure is visible to shell automation."""
        # Force mkdir to raise
        from pathlib import Path as _P

        original_mkdir = _P.mkdir

        def fail_mkdir(self, *args: object, **kwargs: object) -> None:
            raise OSError("permission denied")

        monkeypatch.setattr(_P, "mkdir", fail_mkdir)
        try:
            result = runner.invoke(app, ["doctor", "--fix"])
        finally:
            monkeypatch.setattr(_P, "mkdir", original_mkdir)

        assert result.exit_code == 1
        assert "Cannot create config directory" in result.output

    def test_reports_partial_template_write_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A partial staged write leaves no target and does not block its sibling."""
        config_dir = Path(os.environ["RECON_CONFIG_DIR"])

        class StagedTemplate:
            def __init__(self, path: Path, *, fail: bool) -> None:
                self.name = str(path)
                self._path = path
                self._fail = fail

            def __enter__(self) -> StagedTemplate:
                return self

            def __exit__(self, *args: object) -> None:
                return None

            def write(self, content: str) -> int:
                if self._fail:
                    self._path.write_text(content[:12], encoding="utf-8")
                    raise OSError("disk full")
                self._path.write_text(content, encoding="utf-8")
                return len(content)

        def staged_file(**kwargs: object) -> StagedTemplate:
            prefix = str(kwargs["prefix"])
            path = config_dir / f"{prefix}test.tmp"
            return StagedTemplate(path, fail="fingerprints.yaml" in prefix)

        doctor_module = importlib.import_module("recon_tool.cli.doctor")
        with monkeypatch.context() as patch_context:
            patch_context.setattr(doctor_module.tempfile, "NamedTemporaryFile", staged_file)
            result = runner.invoke(app, ["doctor", "--fix"])

        assert result.exit_code == 1
        assert "failed to create" in result.output
        assert "1 template could not be created" in result.output
        assert not (config_dir / "fingerprints.yaml").exists()
        assert (config_dir / "signals.yaml").is_file()
        assert not list(config_dir.glob(".*.tmp"))

    def test_rejects_template_path_that_is_not_a_file(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A directory collision is not reported as an existing template."""
        config_dir = Path(os.environ["RECON_CONFIG_DIR"]) / ("long-config-path-" + "x" * 64)
        config_dir.mkdir()
        monkeypatch.setenv("RECON_CONFIG_DIR", str(config_dir))
        (config_dir / "fingerprints.yaml").mkdir()

        result = runner.invoke(app, ["doctor", "--fix"])

        assert result.exit_code == 1
        assert "is not a regular file" in " ".join(result.output.split())
        assert (config_dir / "signals.yaml").is_file()

    def test_concurrent_template_creation_is_never_overwritten(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """No-replace publication preserves a file that appears at the boundary."""
        config_dir = Path(os.environ["RECON_CONFIG_DIR"])
        target = config_dir / "fingerprints.yaml"
        original_link = os.link
        injected = False

        def create_before_link(source: Path, destination: Path) -> None:
            nonlocal injected
            if destination == target and not injected:
                injected = True
                target.write_text("custom concurrent content\n", encoding="utf-8")
            original_link(source, destination)

        doctor_module = importlib.import_module("recon_tool.cli.doctor")
        monkeypatch.setattr(doctor_module.os, "link", create_before_link)

        assert _doctor_fix() is True
        assert target.read_text(encoding="utf-8") == "custom concurrent content\n"
        assert (config_dir / "signals.yaml").is_file()
        assert not list(config_dir.glob(".*.tmp"))

    def test_publish_and_collision_probe_errors_are_contained(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """An inaccessible path returns failure instead of escaping the repair command."""

        def deny_link(source: Path, destination: Path) -> None:
            raise PermissionError("publish denied")

        def deny_exists(self: Path) -> bool:
            raise PermissionError("probe denied")

        doctor_module = importlib.import_module("recon_tool.cli.doctor")
        monkeypatch.setattr(doctor_module.os, "link", deny_link)
        monkeypatch.setattr(Path, "exists", deny_exists)

        result = runner.invoke(app, ["doctor", "--fix"])

        assert result.exit_code == 1
        assert "failed to create" in result.output
        assert "publish denied" in result.output


class TestCliLookupErrorPaths:
    def test_lookup_with_all_sources_failed_exits_4(self) -> None:
        """A caught all-source pipeline failure exits with code 4."""

        async def fake_resolve(*args: object, **kwargs: object):
            raise ReconLookupError(
                domain="does-not-exist.example",
                message="No information",
                error_type="all_sources_failed",
                source_errors=(("dns_records", "DNS error"),),
            )

        with patch("recon_tool.resolver.resolve_tenant", side_effect=fake_resolve):
            result = runner.invoke(
                app,
                ["lookup", "does-not-exist.example", "--no-cache"],
            )
        assert result.exit_code == 4

    def test_lookup_with_internal_error_exits_4(self) -> None:
        """Generic exceptions during resolve produce exit code 4."""

        async def fake_resolve(*args: object, **kwargs: object):
            raise RuntimeError("unexpected failure")

        with patch("recon_tool.resolver.resolve_tenant", side_effect=fake_resolve):
            result = runner.invoke(
                app,
                ["lookup", "example.com", "--no-cache"],
            )
        assert result.exit_code == 4


class TestCliTimeoutFlag:
    def test_custom_timeout_accepted(self) -> None:
        info = _fake_info()
        results = _fake_source_results()

        async def fake_resolve(*args: object, **kwargs: object):
            return info, results

        with patch("recon_tool.resolver.resolve_tenant", side_effect=fake_resolve):
            result = runner.invoke(
                app,
                ["lookup", "alpha.invalid", "--no-cache", "--timeout", "30"],
            )
        assert result.exit_code == 0


class TestCliSourcesFlag:
    def test_sources_flag_renders_detail_table(self) -> None:
        info = _fake_info()
        results = _fake_source_results()

        async def fake_resolve(*args: object, **kwargs: object):
            return info, results

        with patch("recon_tool.resolver.resolve_tenant", side_effect=fake_resolve):
            result = runner.invoke(
                app,
                ["lookup", "alpha.invalid", "--no-cache", "--sources"],
            )
        assert result.exit_code == 0


class TestBatchValidation:
    def test_batch_missing_file_exits(self) -> None:
        result = runner.invoke(app, ["batch", "/definitely-not-a-real-path/domains.txt"])
        assert result.exit_code == 2

    def test_batch_empty_file_exits(self, tmp_path: Path) -> None:
        empty = tmp_path / "empty.txt"
        empty.write_text("", encoding="utf-8")
        result = runner.invoke(app, ["batch", str(empty)])
        assert result.exit_code == 2

    def test_batch_only_comments_exits(self, tmp_path: Path) -> None:
        f = tmp_path / "comments.txt"
        f.write_text("# just comments\n# and more\n", encoding="utf-8")
        result = runner.invoke(app, ["batch", str(f)])
        assert result.exit_code == 2

    def test_batch_conflicting_output_formats_exits(self, tmp_path: Path) -> None:
        f = tmp_path / "d.txt"
        f.write_text("example.com\n", encoding="utf-8")
        result = runner.invoke(app, ["batch", str(f), "--json", "--md"])
        assert result.exit_code == 2


class TestBatchJsonMode:
    def test_batch_with_mocked_resolver(self, tmp_path: Path) -> None:
        f = tmp_path / "d.txt"
        f.write_text("example.com\nexample.org\n", encoding="utf-8")

        async def fake_resolve(*args: object, **kwargs: object):
            return _fake_info(), _fake_source_results()

        with patch("recon_tool.resolver.resolve_tenant", side_effect=fake_resolve):
            result = runner.invoke(app, ["batch", str(f), "--json", "-c", "2"])
        assert result.exit_code == 0
        # Output should be valid JSON
        import json

        parsed = json.loads(result.stdout)
        assert isinstance(parsed, list)
        assert len(parsed) == 2

    def test_batch_csv_mode(self, tmp_path: Path) -> None:
        f = tmp_path / "d.txt"
        f.write_text("example.com\n", encoding="utf-8")

        async def fake_resolve(*args: object, **kwargs: object):
            return _fake_info(), _fake_source_results()

        with patch("recon_tool.resolver.resolve_tenant", side_effect=fake_resolve):
            result = runner.invoke(app, ["batch", str(f), "--csv"])
        assert result.exit_code == 0
        assert "example.com" in result.stdout or "Synthetic Alpha" in result.stdout


class TestCliExposureMode:
    def test_exposure_mode_with_mocked_resolver(self) -> None:
        info = _fake_info()
        results = _fake_source_results()

        async def fake_resolve(*args: object, **kwargs: object):
            return info, results

        with patch("recon_tool.resolver.resolve_tenant", side_effect=fake_resolve):
            result = runner.invoke(app, ["lookup", "alpha.invalid", "--no-cache", "--exposure"])
        assert result.exit_code == 0

    def test_exposure_mode_json(self) -> None:
        async def fake_resolve(*args: object, **kwargs: object):
            return _fake_info(), _fake_source_results()

        with patch("recon_tool.resolver.resolve_tenant", side_effect=fake_resolve):
            result = runner.invoke(app, ["lookup", "alpha.invalid", "--no-cache", "--exposure", "--json"])
        assert result.exit_code == 0


class TestCliGapsMode:
    def test_gaps_mode_with_mocked_resolver(self) -> None:
        async def fake_resolve(*args: object, **kwargs: object):
            return _fake_info(), _fake_source_results()

        with patch("recon_tool.resolver.resolve_tenant", side_effect=fake_resolve):
            result = runner.invoke(app, ["lookup", "alpha.invalid", "--no-cache", "--gaps"])
        assert result.exit_code == 0

    def test_gaps_mode_json(self) -> None:
        async def fake_resolve(*args: object, **kwargs: object):
            return _fake_info(), _fake_source_results()

        with patch("recon_tool.resolver.resolve_tenant", side_effect=fake_resolve):
            result = runner.invoke(app, ["lookup", "alpha.invalid", "--no-cache", "--gaps", "--json"])
        assert result.exit_code == 0


class TestCliPostureAndExplainFlags:
    def test_posture_flag(self) -> None:
        async def fake_resolve(*args: object, **kwargs: object):
            return _fake_info(), _fake_source_results()

        with patch("recon_tool.resolver.resolve_tenant", side_effect=fake_resolve):
            result = runner.invoke(app, ["lookup", "alpha.invalid", "--no-cache", "--posture"])
        assert result.exit_code == 0

    def test_explain_renders_source_status_panel(self) -> None:
        """Phase 1 regression guard: --explain must render the Source
        Status panel above the Explanations panel. Caught a v0.9.2 bug
        where the cache-hit path produced an empty results list and
        nothing rendered."""

        async def fake_resolve(*args: object, **kwargs: object):
            return _fake_info(), _fake_source_results()

        with patch("recon_tool.resolver.resolve_tenant", side_effect=fake_resolve):
            result = runner.invoke(app, ["lookup", "alpha.invalid", "--no-cache", "--explain"])
        assert result.exit_code == 0
        assert "Source Status" in result.stdout
        assert "oidc_discovery" in result.stdout

    def test_source_panels_project_unavailable_channel_payloads(self) -> None:
        info = TenantInfo(
            tenant_id=None,
            display_name="Synthetic Alpha",
            default_domain="alpha.invalid",
            queried_domain="alpha.invalid",
            confidence=ConfidenceLevel.LOW,
            degraded_sources=("dns:dmarc",),
        )
        sources = [
            SourceResult(
                source_name="dns_records",
                dmarc_policy="reject",
                detected_services=("DMARC",),
                detected_slugs=("dmarc",),
                degraded_sources=("dns:dmarc",),
            )
        ]

        async def fake_resolve(*args: object, **kwargs: object):
            return info, sources

        with patch("recon_tool.resolver.resolve_tenant", side_effect=fake_resolve):
            result = runner.invoke(
                app,
                ["lookup", "alpha.invalid", "--no-cache", "--sources", "--explain"],
            )

        assert result.exit_code == 0
        assert "dns:dmarc" in result.stdout
        assert "DMARC: reject" not in result.stdout

    def test_explain_on_cache_hit_synthesizes_source_status(self, tmp_path: Path) -> None:
        """Phase 1 regression guard: --explain must render Source Status
        even when the lookup is served from cache (results list is empty
        on cache hit). v0.9.2 fix synthesizes minimal SourceResults from
        TenantInfo.sources and degraded_sources when results is empty."""
        # Pre-populate the cache with our fake info
        import os

        from recon_tool.cache import cache_put

        env_orig = os.environ.get("RECON_CONFIG_DIR")
        os.environ["RECON_CONFIG_DIR"] = str(tmp_path)
        try:
            cache_put("alpha.invalid", _fake_info())
            # Resolver should NOT be called — cache hit
            from unittest.mock import MagicMock

            unused_mock = MagicMock(side_effect=AssertionError("resolver should not be called on cache hit"))
            with patch("recon_tool.resolver.resolve_tenant", unused_mock):
                result = runner.invoke(app, ["lookup", "alpha.invalid", "--explain"])
            assert result.exit_code == 0
            # Source Status panel must appear with synthesized entries
            assert "Source Status" in result.stdout
            # At least one source from the fake info must be visible
            assert "oidc_discovery" in result.stdout or "user_realm" in result.stdout
            assert "Final confidence" in result.stdout
        finally:
            if env_orig is None:
                os.environ.pop("RECON_CONFIG_DIR", None)
            else:
                os.environ["RECON_CONFIG_DIR"] = env_orig

    def test_cache_ttl_rejects_negative_values(self) -> None:
        result = runner.invoke(app, ["lookup", "alpha.invalid", "--cache-ttl", "-1"])
        assert result.exit_code == 2
        assert "non-negative" in (result.stdout + result.stderr).lower()

    def test_explain_flag_basic(self) -> None:
        async def fake_resolve(*args: object, **kwargs: object):
            return _fake_info(), _fake_source_results()

        with patch("recon_tool.resolver.resolve_tenant", side_effect=fake_resolve):
            result = runner.invoke(app, ["lookup", "alpha.invalid", "--no-cache", "--explain"])
        assert result.exit_code == 0

    def test_full_flag(self) -> None:
        async def fake_resolve(*args: object, **kwargs: object):
            return _fake_info(), _fake_source_results()

        with patch("recon_tool.resolver.resolve_tenant", side_effect=fake_resolve):
            result = runner.invoke(app, ["lookup", "alpha.invalid", "--no-cache", "--full"])
        assert result.exit_code == 0

    def test_md_flag(self) -> None:
        async def fake_resolve(*args: object, **kwargs: object):
            return _fake_info(), _fake_source_results()

        with patch("recon_tool.resolver.resolve_tenant", side_effect=fake_resolve):
            result = runner.invoke(app, ["lookup", "alpha.invalid", "--no-cache", "--md"])
        assert result.exit_code == 0
        assert "#" in result.stdout  # markdown header

    def test_mutually_exclusive_output_flags_rejected(self) -> None:
        result = runner.invoke(app, ["lookup", "alpha.invalid", "--json", "--md"])
        assert result.exit_code != 0


class TestVersionFlag:
    def test_version_flag_prints_and_exits(self) -> None:
        from recon_tool import __version__

        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "recon" in result.stdout
        assert __version__ in result.stdout


class TestHelpOutput:
    def test_help_flag_shows_help(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "recon" in result.stdout.lower()

    def test_lookup_help(self) -> None:
        result = runner.invoke(app, ["lookup", "--help"])
        assert result.exit_code == 0
        assert "domain" in result.stdout.lower()

    def test_batch_help(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("FORCE_COLOR", "1")
        result = runner.invoke(app, ["batch", "--help"])
        output = click.unstyle(result.output)
        normalized_output = " ".join(output.replace("│", " ").split())
        assert result.exit_code == 0
        for option in (
            "--json",
            "--md",
            "--csv",
            "--ndjson",
            "--include-unclassified",
            "--concurrency",
            "--timeout",
            "--no-ct",
            "--include-ecosystem",
            "--summary",
            "--summary-schema",
            "--fusion",
            "--no-fusion",
        ):
            assert option in output
        assert "Output" in output
        assert "Collection, cache, and scope" in output
        assert "Analysis modes" in output
        assert "Evidence model" in output
        assert "clamped to 1-20" in output
        assert "Per-domain failures are output records" in output
        assert "record_type" in output
        assert "By default this replaces per-domain records" in normalized_output
        assert "attach the summary as cohort_summary" in normalized_output
        assert "Enabled by default; pass --no-fusion for deterministic output" in normalized_output
        assert "transition notice" not in normalized_output
        assert "across future releases" not in normalized_output

    def test_root_help_warns_before_sharing_debug_diagnostics(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("FORCE_COLOR", "1")
        result = runner.invoke(app, ["--help"])
        normalized = " ".join(click.unstyle(result.output).replace("│", " ").split())

        assert result.exit_code == 0
        assert "Review before sharing" in normalized
        assert "domain inputs and local details" in normalized

    def test_doctor_help_discloses_default_contacts_and_local_modes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("FORCE_COLOR", "1")
        result = runner.invoke(app, ["doctor", "--help"])
        normalized = " ".join(click.unstyle(result.output).replace("│", " ").split())

        assert result.exit_code == 0
        assert "Microsoft identity endpoints" in normalized
        assert "DNS for example.com" in normalized
        assert "crt.sh" in normalized
        assert "CertSpotter" in normalized
        assert "No user-supplied target is queried" in normalized
        assert "local-only" in normalized
