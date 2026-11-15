# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportMissingParameterType=none, reportPrivateUsage=none, reportUnknownArgumentType=none
# pyright: reportUnknownMemberType=none, reportUnknownParameterType=none, reportUnknownVariableType=none
"""Phase 2c: tests for the `recon doctor` command.

Mocks httpx + dnspython + the fingerprint/signal loaders so the doctor
checks run without touching the real network. Pushes cli.py coverage.
"""

from __future__ import annotations

import importlib
import os
import sys
from io import StringIO
from pathlib import Path
from typing import NamedTuple
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from rich.console import Console
from typer.testing import CliRunner

from recon_tool.cli import app
from recon_tool.cli.doctor import (
    DoctorCheck,
    _doctor_path_launcher_check,
    _doctor_print_header,
    _doctor_release_check,
    _doctor_render,
    _launcher_is_in_current_workspace,
    _launcher_version,
    _render_mcp_checks,
)

runner = CliRunner()


def _ok_response(status: int = 200) -> MagicMock:
    """Build a fake httpx.Response with the given status code."""
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status
    return resp


def _honest_resolver(record_count: int = 2) -> MagicMock:
    """A stub resolver: example.com answers, reserved `.invalid` names do not exist."""
    import dns.resolver

    def _resolve(qname: str, rdtype: str = "A", *args: object, **kwargs: object) -> list[MagicMock]:
        if str(qname).rstrip(".").endswith(".invalid"):
            raise dns.resolver.NXDOMAIN()
        return [MagicMock() for _ in range(record_count)]

    fake = MagicMock()
    fake.resolve.side_effect = _resolve
    return fake


@pytest.fixture
def fake_httpx_client():
    """A fake httpx.AsyncClient that returns 200s for every request."""
    client = AsyncMock()
    client.get = AsyncMock(return_value=_ok_response(200))
    client.post = AsyncMock(return_value=_ok_response(200))
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    return client


@pytest.fixture
def patched_doctor_environment(fake_httpx_client):
    """Patch httpx.AsyncClient and dns.resolver.resolve so doctor runs offline."""
    fake_dns = _honest_resolver(2)
    with (
        patch("httpx.AsyncClient", return_value=fake_httpx_client),
        patch("dns.resolver.resolve", fake_dns.resolve),
    ):
        yield fake_httpx_client, fake_dns


@pytest.fixture(autouse=True)
def stable_doctor_path_launcher():
    """Keep command tests independent of launchers installed on the test host."""
    from recon_tool import updater

    with (
        patch(
            "recon_tool.cli.doctor._doctor_path_launcher_check",
            return_value=DoctorCheck("PATH recon launcher", "ok", "test launcher matches running package"),
        ),
        patch("recon_tool.updater.fetch_latest_version", return_value=updater.current_version()),
    ):
        yield


@pytest.mark.parametrize(
    ("latest", "status", "detail"),
    [
        ("2.19.4", "ok", "up to date on PyPI"),
        ("2.19.5", "warn", "2.19.5 available on PyPI; run `recon update`"),
        ("2.19.3", "ok", "newer than PyPI (2.19.3); no downgrade offered"),
        (None, "warn", "could not check PyPI"),
    ],
)
def test_doctor_release_status(latest: str | None, status: str, detail: str) -> None:
    with (
        patch("recon_tool.updater.current_version", return_value="2.19.4"),
        patch("recon_tool.updater.fetch_latest_version", return_value=latest) as fetch,
    ):
        name, actual_status, actual_detail, _next = _doctor_release_check()
    assert name == "Release status"
    assert actual_status == status
    assert detail in actual_detail
    fetch.assert_called_once_with(timeout=3.0)


@pytest.mark.parametrize("latest", ["999.0.0", None])
def test_doctor_release_warning_does_not_fail_health_check(patched_doctor_environment, latest: str | None) -> None:
    with patch("recon_tool.updater.fetch_latest_version", return_value=latest):
        result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0, result.output
    assert "Release status" in result.output
    assert "Core checks passed with 1 warning. Review the rows above." in result.output


class TestDoctorCommandHappyPath:
    """All checks pass — every probe returns 200, DNS resolves cleanly."""

    def test_doctor_runs_without_crashing(self, patched_doctor_environment) -> None:
        result = runner.invoke(app, ["doctor"])
        # Doctor command might exit 0 or non-zero depending on whether the
        # mocked checks were sufficient. We just need it to not crash.
        assert result.exit_code in (0, 1)
        assert "recon" in result.stdout.lower()

    def test_doctor_shows_version(self, patched_doctor_environment) -> None:
        from recon_tool import __version__

        result = runner.invoke(app, ["doctor"])
        assert __version__ in result.stdout

    def test_doctor_shows_python_version(self, patched_doctor_environment) -> None:
        import sys

        result = runner.invoke(app, ["doctor"])
        assert sys.version.split()[0] in result.stdout

    def test_doctor_shows_install_identity(self, patched_doctor_environment) -> None:
        import sys

        result = runner.invoke(app, ["doctor"])
        rendered = " ".join(result.output.split())

        assert str(Path(sys.executable).resolve()) in rendered
        assert "Package" in rendered
        assert "recon_tool" in rendered
        assert "Install method" in rendered

    def test_install_identity_paths_remain_copyable_in_narrow_output(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import sys

        import recon_tool
        from recon_tool import updater

        directory = tmp_path / ("synthetic-long-path-" * 8) / "[literal]"
        executable = directory / "python"
        package = directory / "recon_tool" / "__init__.py"
        monkeypatch.setattr(sys, "executable", str(executable))
        monkeypatch.setattr(recon_tool, "__file__", str(package))
        monkeypatch.setattr(updater, "detect_install_method", lambda: updater.PIP)
        output = StringIO()

        _doctor_print_header(Console(file=output, width=30, color_system=None))

        assert str(executable.resolve()) in output.getvalue()
        assert str(package.resolve().parent) in output.getvalue()

    @pytest.mark.parametrize(
        ("minor", "releaselevel", "warning"),
        [(11, "final", False), (15, "final", False), (16, "final", True), (15, "candidate", True)],
    )
    def test_interpreter_support_advisory(
        self, minor: int, releaselevel: str, warning: bool, patched_doctor_environment
    ) -> None:
        class Version(NamedTuple):
            major: int
            minor: int
            micro: int
            releaselevel: str
            serial: int

        with patch("recon_tool.cli.doctor.sys.version_info", Version(3, minor, 1, releaselevel, 0)):
            result = runner.invoke(app, ["doctor"])
        assert ("outside the tested stable range (3.11 through 3.15)" in result.output) is warning
        assert result.exit_code == 0
        assert "All checks passed." in result.output

    def test_doctor_prints_schema_stability_label(self, patched_doctor_environment) -> None:
        """The v2.0 quality bar wants the schema-stability indicator
        on the first version line so operators can tell at a glance
        whether the build is pre-v2.0 or v2.0+."""
        from recon_tool import __version__

        result = runner.invoke(app, ["doctor"])
        # v1.9.x builds show "pre-v2.0 schema"; v2.x builds show "v2.0 stable schema".
        expected = "v2.0 stable schema" if __version__.startswith("2.") else "pre-v2.0 schema"
        assert expected in result.stdout, (
            f"Expected schema-stability label {expected!r} not found in doctor output for v{__version__}"
        )

    def test_doctor_reports_schema_fields_check(self, patched_doctor_environment) -> None:
        """Doctor verifies the locked top-level fields are
        all emitted by ``format_tenant_json``. The "Schema fields" row
        must appear in the doctor output and report the count."""
        from recon_tool.schema_contract import REQUIRED_TOP_LEVEL_FIELDS

        result = runner.invoke(app, ["doctor"])
        assert "Schema fields" in result.output
        # When the contract holds, the row reports the count of locked fields.
        assert f"{len(REQUIRED_TOP_LEVEL_FIELDS)} locked top-level fields present" in result.output

    def test_doctor_mcp_emits_canonical_safe_launcher(self) -> None:
        result = runner.invoke(app, ["doctor", "--mcp"])

        assert result.exit_code == 0
        assert '"args": [' in result.output
        assert '"-c",' in result.output
        assert '"PYTHONSAFEPATH": "1"' in result.output
        assert "python -m recon_tool.server" not in result.output
        assert "fallback" not in result.output.lower()


class TestDoctorCommandFailures:
    """When various probes fail, doctor reports them and continues."""

    def test_doctor_handles_oidc_timeout(self) -> None:
        """A timeout on the OIDC probe should be reported but not crash."""
        client = AsyncMock()
        client.get = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("httpx.AsyncClient", return_value=client),
            patch("dns.resolver.resolve", side_effect=Exception("offline")),
        ):
            result = runner.invoke(app, ["doctor"])

        # Should not crash even with everything failing
        assert "recon" in result.stdout.lower()

    def test_doctor_handles_dns_failure(self, fake_httpx_client) -> None:
        """A DNS resolver failure is reported in the checks output."""
        import dns.resolver

        with (
            patch("httpx.AsyncClient", return_value=fake_httpx_client),
            patch("dns.resolver.resolve", side_effect=dns.resolver.NXDOMAIN()),
        ):
            result = runner.invoke(app, ["doctor"])

        assert "recon" in result.stdout.lower()

    @pytest.mark.parametrize(
        "request_error",
        [
            httpx.RemoteProtocolError("synthetic protocol failure"),
            httpx.ProxyError("synthetic proxy failure"),
        ],
    )
    def test_doctor_reports_request_errors_and_continues(
        self,
        fake_httpx_client,
        request_error: httpx.RequestError,
    ) -> None:
        fake_dns = _honest_resolver(1)
        fake_httpx_client.get = AsyncMock(
            side_effect=[
                request_error,
                _ok_response(200),
                _ok_response(200),
                _ok_response(200),
            ]
        )
        fake_httpx_client.post = AsyncMock(return_value=_ok_response(200))

        with (
            patch("httpx.AsyncClient", return_value=fake_httpx_client),
            patch("dns.resolver.resolve", fake_dns.resolve),
        ):
            result = runner.invoke(app, ["doctor"])

        assert result.exit_code == 1
        assert not isinstance(result.exception, httpx.RequestError)
        assert "fail  OIDC discovery" in result.output
        assert "ok  GetUserRealm" in result.output
        assert "ok  Autodiscover" in result.output
        assert "ok  DNS resolution" in result.output
        assert "ok  crt.sh (cert transparency)" in result.output
        assert "ok  certspotter (cert transparency)" in result.output
        assert "1 check failed. Lookups may be incomplete. Next:" in " ".join(result.output.split())

    def test_doctor_treats_crtsh_request_error_as_warning(self, fake_httpx_client) -> None:
        fake_dns = _honest_resolver(1)
        fake_httpx_client.get = AsyncMock(
            side_effect=[
                _ok_response(200),
                _ok_response(200),
                httpx.RemoteProtocolError("synthetic CT protocol failure"),
                _ok_response(200),
            ]
        )
        fake_httpx_client.post = AsyncMock(return_value=_ok_response(200))

        with (
            patch("httpx.AsyncClient", return_value=fake_httpx_client),
            patch("dns.resolver.resolve", fake_dns.resolve),
        ):
            result = runner.invoke(app, ["doctor"])

        assert result.exit_code == 0
        assert not isinstance(result.exception, httpx.RequestError)
        assert "warn  crt.sh (cert transparency)" in result.output
        assert "ok  certspotter (cert transparency)" in result.output
        assert "crt.sh is degraded; CertSpotter is reachable" in result.output
        assert "Certificate transparency is unavailable" not in result.output
        assert "Optional enrichment sources are degraded" not in result.output

    def test_doctor_treats_crtsh_http_error_as_warning(self, fake_httpx_client) -> None:
        """crt.sh is optional enrichment; outage should not fail doctor."""
        fake_dns = _honest_resolver(2)
        fake_httpx_client.get = AsyncMock(
            side_effect=[
                _ok_response(200),  # OIDC discovery
                _ok_response(200),  # GetUserRealm
                _ok_response(502),  # crt.sh
                _ok_response(200),  # CertSpotter
            ]
        )
        fake_httpx_client.post = AsyncMock(return_value=_ok_response(503))

        with (
            patch("httpx.AsyncClient", return_value=fake_httpx_client),
            patch("dns.resolver.resolve", fake_dns.resolve),
        ):
            result = runner.invoke(app, ["doctor"])

        assert result.exit_code == 0
        assert "warn  crt.sh (cert transparency): HTTP 502" in result.output
        assert "ok  certspotter (cert transparency)" in result.output
        assert "fail  crt.sh" not in result.output
        assert "crt.sh is degraded; CertSpotter is reachable" in result.output
        assert "Certificate transparency is unavailable" not in result.output
        assert "failed" not in result.output

    def test_doctor_reports_ct_unavailable_only_when_both_providers_fail(self, fake_httpx_client: AsyncMock) -> None:
        """One live provider is a fallback. Both warnings are an outage."""
        fake_dns = _honest_resolver(2)
        fake_httpx_client.get = AsyncMock(
            side_effect=[
                _ok_response(200),
                _ok_response(200),
                _ok_response(502),
                _ok_response(503),
            ]
        )
        fake_httpx_client.post = AsyncMock(return_value=_ok_response(200))

        with (
            patch("httpx.AsyncClient", return_value=fake_httpx_client),
            patch("dns.resolver.resolve", fake_dns.resolve),
        ):
            result = runner.invoke(app, ["doctor"])

        assert result.exit_code == 0
        assert "warn  crt.sh (cert transparency): HTTP 502" in result.output
        assert "warn  certspotter (cert transparency): HTTP 503" in result.output
        assert "fail  crt.sh" not in result.output
        assert "Certificate transparency is unavailable (2 warnings)." in result.output

    def test_doctor_reports_certspotter_fallback_when_crtsh_is_reachable(self, fake_httpx_client: AsyncMock) -> None:
        fake_dns = _honest_resolver(1)
        fake_httpx_client.get = AsyncMock(
            side_effect=[
                _ok_response(200),
                _ok_response(200),
                _ok_response(200),
                httpx.TimeoutException("synthetic certspotter timeout"),
            ]
        )
        fake_httpx_client.post = AsyncMock(return_value=_ok_response(200))

        with (
            patch("httpx.AsyncClient", return_value=fake_httpx_client),
            patch("dns.resolver.resolve", fake_dns.resolve),
        ):
            result = runner.invoke(app, ["doctor"])

        assert result.exit_code == 0
        assert "ok  crt.sh (cert transparency)" in result.output
        assert "warn  certspotter (cert transparency)" in result.output
        assert "CertSpotter is degraded; crt.sh is reachable" in result.output
        assert "Certificate transparency is unavailable" not in result.output


class TestDoctorPathLauncher:
    @pytest.mark.parametrize("location", ["home", "nested", "outside"])
    def test_home_launcher_shim_dispatches_through_lexical_path(self, tmp_path: Path, location: str) -> None:
        if os.name == "nt":
            pytest.skip("Unix executable symlink dispatch")
        home = tmp_path / "home" / "user"
        shim = home / ".local" / "share" / "mise" / "shims" / "recon"
        shim.parent.mkdir(parents=True)
        target = tmp_path / "system" / "mise"
        target.parent.mkdir()
        target.write_text(
            f"#!{sys.executable}\nfrom pathlib import Path\nimport sys\n"
            "print('recon 2.17.10' if Path(sys.argv[0]).name == 'recon' else 'mise 2026.10.8')\n",
            encoding="utf-8",
        )
        target.chmod(0o755)
        shim.symlink_to(target)
        cwd = {"home": home, "nested": home / ".cache" / "qa" / "recon", "outside": tmp_path / "outside"}[location]
        cwd.mkdir(parents=True, exist_ok=True)
        with (
            patch("pathlib.Path.home", return_value=home),
            patch("pathlib.Path.cwd", return_value=cwd),
            patch("recon_tool.cli.doctor.shutil.which", return_value=str(shim)),
            patch("recon_tool.updater.current_version", return_value="2.17.11"),
        ):
            _, status, detail, _next = _doctor_path_launcher_check()

        assert status == "warn"
        assert f"{shim} reports 2.17.10, but this process is 2.17.11" in detail
        assert str(target) not in detail

    def test_home_sibling_launcher_is_not_treated_as_project_content(self, tmp_path: Path) -> None:
        home = tmp_path / "home" / "user"
        project = home / "project" / "nested"
        project.mkdir(parents=True)
        launcher = home.parent / "other-user" / "bin" / "recon"
        with patch("pathlib.Path.home", return_value=home), patch("pathlib.Path.cwd", return_value=project):
            assert not _launcher_is_in_current_workspace(launcher)

    def test_project_under_home_still_refuses_planted_launcher(self, tmp_path: Path) -> None:
        home = tmp_path / "home"
        project = home / "project"
        nested = project / "nested"
        nested.mkdir(parents=True)
        launcher = project / "bin" / "recon"
        with (
            patch("pathlib.Path.home", return_value=home),
            patch("pathlib.Path.cwd", return_value=nested),
            patch("recon_tool.cli.doctor.shutil.which", return_value=str(launcher)),
            patch("recon_tool.cli.doctor._launcher_version") as probe,
        ):
            _, status, detail, _next = _doctor_path_launcher_check()
        assert status == "warn"
        assert "inside the current workspace" in detail
        probe.assert_not_called()

    def test_workspace_launcher_is_not_executed(self, tmp_path: Path) -> None:
        workspace = tmp_path / "repo"
        workspace.mkdir()
        (workspace / ".git").mkdir()
        launcher = (workspace / "recon").resolve()

        with patch("pathlib.Path.cwd", return_value=workspace):
            assert _launcher_is_in_current_workspace(launcher)

        with (
            patch("recon_tool.cli.doctor.shutil.which", return_value=str(launcher)),
            patch("pathlib.Path.cwd", return_value=workspace),
            patch("recon_tool.cli.doctor._launcher_version") as probe,
        ):
            _, status, detail, _next = _doctor_path_launcher_check()

        assert status == "warn"
        assert "inside the current workspace" in detail
        probe.assert_not_called()

    def test_no_git_nested_ancestor_launcher_is_not_executed(self, tmp_path: Path) -> None:
        workspace = tmp_path / "project"
        nested = workspace / "nested" / "checkout"
        nested.mkdir(parents=True)
        planted_bin = workspace / "bin"
        planted_bin.mkdir()
        launcher = planted_bin / ("recon.exe" if sys.platform == "win32" else "recon")
        launcher.write_text("", encoding="utf-8")

        with (
            patch("recon_tool.cli.doctor.shutil.which", return_value=str(launcher)),
            patch("pathlib.Path.cwd", return_value=nested),
            patch("recon_tool.cli.doctor._launcher_version") as probe,
        ):
            _, status, detail, _next = _doctor_path_launcher_check()

        assert status == "warn"
        assert "inside the current workspace" in detail
        probe.assert_not_called()

    def test_relative_path_launcher_is_not_executed(self, tmp_path: Path) -> None:
        with (
            patch("recon_tool.cli.doctor.shutil.which", return_value="../bin/recon"),
            patch("pathlib.Path.cwd", return_value=tmp_path),
            patch("recon_tool.cli.doctor._launcher_version") as probe,
        ):
            _, status, detail, _next = _doctor_path_launcher_check()

        assert status == "warn"
        assert "inside the current workspace" in detail
        probe.assert_not_called()

    def test_git_workspace_launcher_symlink_is_not_executed(self, tmp_path: Path) -> None:
        workspace = tmp_path / "repo"
        workspace.mkdir()
        (workspace / ".git").mkdir()
        outside = tmp_path / "outside_bin"
        outside.mkdir()
        outside_target = outside / ("recon.exe" if sys.platform == "win32" else "recon")
        outside_target.write_text("", encoding="utf-8")
        link = workspace / "recon"
        try:
            link.symlink_to(outside_target)
        except OSError as exc:
            pytest.skip(f"symlinks unavailable: {exc}")

        with (
            patch("recon_tool.cli.doctor.shutil.which", return_value=str(link)),
            patch("pathlib.Path.cwd", return_value=workspace),
            patch("recon_tool.cli.doctor._launcher_version") as probe,
        ):
            _, status, detail, _next = _doctor_path_launcher_check()

        assert status == "warn"
        assert "inside the current workspace" in detail
        probe.assert_not_called()

    def test_version_probe_uses_direct_absolute_launcher_without_a_shell(self, tmp_path: Path) -> None:
        import subprocess

        launcher = (tmp_path / "recon").resolve()
        completed = subprocess.CompletedProcess(
            args=[str(launcher), "--version"],
            returncode=0,
            stdout="recon 2.17.11\n",
            stderr="",
        )
        with patch("recon_tool.cli.doctor.subprocess.run", return_value=completed) as run:
            version, error = _launcher_version(launcher)

        assert version == "2.17.11"
        assert error is None
        run.assert_called_once_with(
            [str(launcher), "--version"],
            capture_output=True,
            check=False,
            shell=False,
            timeout=5.0,
        )

    def test_version_probe_handles_invalid_utf8_without_crashing(self, tmp_path: Path) -> None:
        import subprocess

        launcher = (tmp_path / "recon").resolve()
        completed = subprocess.CompletedProcess(
            args=[str(launcher), "--version"],
            returncode=0,
            stdout=b"recon \xff\xfe\n",
            stderr=b"\x80",
        )
        with patch("recon_tool.cli.doctor.subprocess.run", return_value=completed):
            version, error = _launcher_version(launcher)

        assert version is None
        assert error == "version output was not recognized"

    def test_matching_path_launcher_is_ok(self, tmp_path: Path) -> None:
        launcher = tmp_path / "recon"
        with (
            patch("recon_tool.cli.doctor.shutil.which", return_value=str(launcher)),
            patch("recon_tool.cli.doctor._launcher_version", return_value=("2.17.11", None)),
            patch("recon_tool.updater.current_version", return_value="2.17.11"),
        ):
            name, status, detail, _next = _doctor_path_launcher_check()

        assert name == "PATH recon launcher"
        assert status == "ok"
        assert str(launcher) in detail
        assert "2.17.11" in detail

    def test_stale_path_launcher_warns_with_recovery(self, tmp_path: Path) -> None:
        launcher = tmp_path / "recon"
        with (
            patch("recon_tool.cli.doctor.shutil.which", return_value=str(launcher)),
            patch("recon_tool.cli.doctor._launcher_version", return_value=("2.6.3", None)),
            patch("recon_tool.updater.current_version", return_value="2.17.11"),
        ):
            name, status, detail, _next = _doctor_path_launcher_check()

        assert name == "PATH recon launcher"
        assert status == "warn"
        assert str(launcher) in detail
        assert "reports 2.6.3" in detail
        assert "this process is 2.17.11" in detail
        assert "activate the intended environment" in detail
        assert "reinstall recon-tool" in detail
        assert "recon doctor" in detail

    def test_missing_path_launcher_keeps_module_invocation_available(self) -> None:
        with patch("recon_tool.cli.doctor.shutil.which", return_value=None):
            name, status, detail, _next = _doctor_path_launcher_check()

        assert name == "PATH recon launcher"
        assert status == "ok"
        assert "-m recon_tool" in detail


class TestDoctorDiagnosticRendering:
    def test_non_enrichment_warning_gets_a_generic_review_summary(self) -> None:
        stream = StringIO()
        console = Console(file=stream, force_terminal=False, color_system=None, width=120)

        has_failures = _doctor_render(
            console,
            [DoctorCheck("PATH recon launcher", "warn", "stale launcher")],
        )

        assert not has_failures
        assert "Core checks passed with 1 warning. Review the rows above." in stream.getvalue()

    def test_default_rows_escape_markup_strip_controls_and_bound_detail(self) -> None:
        stream = StringIO()
        console = Console(file=stream, force_terminal=False, color_system=None, width=120)
        hostile = "[red]forged[/red]\n  ok  forged-row\x1b]52;c;cGF5bG9hZA==\x07" + "x" * 2500

        has_failures = _doctor_render(console, [DoctorCheck("Probe [name]", "fail", hostile)])

        output = stream.getvalue()
        normalized = " ".join(output.split())
        assert has_failures
        assert "Probe [name]" in output
        assert "[red]forged[/red] ok forged-row]52;c;cGF5bG9hZA==" in normalized
        assert "\n  ok  forged-row" not in output
        assert "\x1b" not in output
        assert "\x07" not in output
        assert "[truncated]" in output

    def test_mcp_rows_use_the_same_safe_rendering_boundary(self) -> None:
        stream = StringIO()
        console = Console(file=stream, force_terminal=False, color_system=None, width=120)

        with patch("recon_tool.cli.doctor.get_err_console", return_value=console):
            _render_mcp_checks([DoctorCheck("Tools [name]", "fail", "[red]forged[/red]\n  ok  forged-row")])

        output = stream.getvalue()
        assert "Tools [name]" in output
        assert "[red]forged[/red]  ok  forged-row" in output
        assert "\n  ok  forged-row" not in output


class TestDoctorExitCode:
    """The exit code gates scriptable and CI health checks: 0 when every check
    passes or only optional enrichment is degraded, 1 when a core check fails.
    """

    def test_doctor_exits_zero_when_all_checks_pass(self, patched_doctor_environment) -> None:
        result = runner.invoke(app, ["doctor"])

        assert result.exit_code == 0
        assert "All checks passed." in result.output

    def test_doctor_exits_one_when_a_core_check_fails(self, fake_httpx_client) -> None:
        """A DNS resolution failure is a core failure, so the process exits 1
        even though every network probe returned 200."""
        import dns.resolver

        with (
            patch("httpx.AsyncClient", return_value=fake_httpx_client),
            patch("dns.resolver.resolve", side_effect=dns.resolver.NXDOMAIN()),
        ):
            result = runner.invoke(app, ["doctor"])

        assert result.exit_code == 1
        assert "fail  DNS resolution" in result.output
        assert "1 check failed. Lookups may be incomplete. Next:" in " ".join(result.output.split())


class TestDoctorFixSubcommand:
    """`recon doctor --fix` scaffolds template config files."""

    def test_doctor_fix_creates_templates(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setenv("RECON_CONFIG_DIR", str(tmp_path))
        result = runner.invoke(app, ["doctor", "--fix"])
        # The subcommand may run a doctor check too — just confirm the
        # template files exist after invocation.
        assert (tmp_path / "fingerprints.yaml").exists()
        assert (tmp_path / "signals.yaml").exists()
        # Result code reflects whether checks pass (0) or some failed (1) —
        # we don't assert a specific code since it depends on the mocked
        # network state.
        assert result.exit_code in (0, 1)

    def test_doctor_fix_renders_markup_like_config_path_as_literal(self, tmp_path, monkeypatch) -> None:
        config_dir = tmp_path / "[bold]config"
        monkeypatch.setenv("RECON_CONFIG_DIR", str(config_dir))

        result = runner.invoke(app, ["doctor", "--fix"])

        assert result.exit_code == 0
        assert "[bold]config" in "".join(result.output.split())
        assert (config_dir / "fingerprints.yaml").exists()

    def test_doctor_fix_renders_hostile_write_error_as_bounded_literal(self, tmp_path, monkeypatch) -> None:
        hostile = "[red]forged[/red]\n  ok  forged-row\x1b]52;c;cGF5bG9hZA==\x07" + "x" * 2500
        monkeypatch.setenv("RECON_CONFIG_DIR", str(tmp_path))

        def _fail(*_args: object, **_kwargs: object) -> object:
            raise OSError(hostile)

        doctor_module = importlib.import_module("recon_tool.cli.doctor")
        monkeypatch.setattr(doctor_module, "_create_template_atomically", _fail)
        result = runner.invoke(app, ["doctor", "--fix"])

        assert result.exit_code == 1
        assert "[red]forged[/red]" in result.output
        assert "\n  ok  forged-row" not in result.output
        assert "\x1b]52" not in result.output
        assert "[truncated]" in result.output

    def test_doctor_fix_documents_every_supported_fingerprint_type(self, tmp_path, monkeypatch) -> None:
        from recon_tool.fingerprints import _VALID_DETECTION_TYPES  # pyright: ignore[reportPrivateUsage]

        monkeypatch.setenv("RECON_CONFIG_DIR", str(tmp_path))
        runner.invoke(app, ["doctor", "--fix"])

        template = (tmp_path / "fingerprints.yaml").read_text(encoding="utf-8")
        type_line = next(line for line in template.splitlines() if line.startswith("#   type:"))
        documented = {item.strip() for item in type_line.partition("Detection type:")[2].split(",")}

        assert documented == set(_VALID_DETECTION_TYPES)
        assert "http" not in documented

    def test_doctor_fix_idempotent(self, tmp_path, monkeypatch) -> None:
        """Running `doctor --fix` twice doesn't overwrite existing files."""
        monkeypatch.setenv("RECON_CONFIG_DIR", str(tmp_path))
        # First run creates files
        runner.invoke(app, ["doctor", "--fix"])
        original = (tmp_path / "fingerprints.yaml").read_text(encoding="utf-8")
        # Modify the file to detect overwrite
        (tmp_path / "fingerprints.yaml").write_text("custom user content\n", encoding="utf-8")
        # Second run — should NOT overwrite
        runner.invoke(app, ["doctor", "--fix"])
        current = (tmp_path / "fingerprints.yaml").read_text(encoding="utf-8")
        assert current == "custom user content\n"
        assert current != original
