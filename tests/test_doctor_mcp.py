# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportMissingParameterType=none, reportPrivateUsage=none, reportUnknownArgumentType=none
# pyright: reportUnknownMemberType=none, reportUnknownParameterType=none
"""Tests for `recon doctor --mcp` flag (v0.10.3)."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from unittest.mock import AsyncMock, PropertyMock, patch

import pytest
from rich.console import Console

pytest.importorskip("mcp")

from typer.testing import CliRunner

from recon_tool.cli import app
from recon_tool.cli.doctor import DoctorCheck, _render_mcp_checks
from recon_tool.mcp_client.install import build_recon_block

runner = CliRunner()


class TestDoctorMcp:
    def test_importing_server_does_not_install_a_shared_logger_handler(self) -> None:
        probe = (
            "import logging; "
            "logger = logging.getLogger('recon'); logger.handlers.clear(); "
            "root = logging.getLogger(); before = (root.handlers[:], root.level); "
            "import recon_tool.server; "
            "assert (root.handlers, root.level) == before; "
            "print(len(logger.handlers)); "
            "logging.getLogger().handlers.clear(); "
            "ctx = recon_tool.server._runtime_logging(); ctx.__enter__(); "
            "print(len(logger.handlers), logger.level); "
            "ctx.__exit__(None, None, None); "
            "print(len(logger.handlers), logger.level)"
        )
        result = subprocess.run(  # noqa: S603 - fixed interpreter and test-owned probe.
            [sys.executable, "-c", probe],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        assert result.returncode == 0, result.stderr
        assert result.stdout.splitlines() == ["0", "1 30", "0 0"]

    def test_mcp_request_logging_explicit_opt_in(self) -> None:
        probe = (
            "import os, logging; "
            "os.environ['RECON_MCP_LOG_REQUESTS'] = '1'; "
            "logger = logging.getLogger('recon'); logger.handlers.clear(); "
            "import recon_tool.server; "
            "logging.getLogger().handlers.clear(); "
            "ctx = recon_tool.server._runtime_logging(); ctx.__enter__(); "
            "print(logger.level); "
            "ctx.__exit__(None, None, None)"
        )
        result = subprocess.run(  # noqa: S603 - fixed interpreter and test-owned probe.
            [sys.executable, "-c", probe],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == "20"

    def test_doctor_mcp_succeeds(self) -> None:
        """With MCP installed, --mcp should run all checks and emit config snippet."""
        result = runner.invoke(app, ["doctor", "--mcp"])
        assert result.exit_code == 0
        out = result.output
        # Core checks
        assert "MCP package" in out
        assert "Server module" in out
        assert "Server Instructions" in out
        assert "Tools enumerated" in out
        assert "Resources enumerated" in out
        # Parseable reference config block
        assert "mcpServers" in out
        assert "recon" in out
        assert '"autoApprove": []' in out
        assert "Security note" in out
        # Per-client comments
        assert "Claude Desktop" in out
        assert "Cursor" in out
        assert "Windsurf" in out
        collapsed = " ".join(out.split())
        assert "VS Code uses a different top-level `servers` key" in collapsed
        assert "recon mcp install --client=vscode" in collapsed
        assert "Prefer `recon mcp install --client=<name>`" in collapsed

        config_start = out.index("{")
        config, _ = json.JSONDecoder().raw_decode(out[config_start:])
        assert config == {"mcpServers": {"recon": build_recon_block()}}
        launcher = " ".join(config["mcpServers"]["recon"]["args"])
        assert "sys.path[:] = [" in launcher

    def test_doctor_mcp_stdout_carries_only_the_json_config(self) -> None:
        """`recon doctor --mcp > config.json` must capture valid JSON: check
        rows and guidance are diagnostics and belong on stderr, leaving the
        reference config as the sole stdout payload."""
        result = runner.invoke(app, ["doctor", "--mcp"])
        assert result.exit_code == 0
        config = json.loads(result.stdout)
        assert config == {"mcpServers": {"recon": build_recon_block()}}
        assert "MCP package" in result.stderr
        assert "Security note" in result.stderr

    def test_doctor_mcp_no_regular_checks(self) -> None:
        """--mcp should only run MCP checks, not the full connectivity suite."""
        result = runner.invoke(app, ["doctor", "--mcp"])
        assert result.exit_code == 0
        # These appear in regular --doctor but not in --mcp
        assert "OIDC discovery" not in result.output
        assert "crt.sh" not in result.output
        assert "certspotter" not in result.output

    def test_doctor_mcp_exits_one_when_mcp_missing(self) -> None:
        """A missing MCP package cannot produce a working setup, so --mcp exits 1
        instead of always reading success."""
        import importlib

        real_import = importlib.import_module

        def fake_import(name, *args, **kwargs):
            if name == "mcp" or name.startswith("mcp."):
                raise ImportError("No module named 'mcp'")
            return real_import(name, *args, **kwargs)

        with patch("importlib.import_module", side_effect=fake_import):
            result = runner.invoke(app, ["doctor", "--mcp"])

        assert result.exit_code == 1
        assert "MCP package" in result.output
        assert "not installed" in result.output

    def test_doctor_mcp_exits_one_when_no_tools_registered(self) -> None:
        """A server that loads but registers no tools is broken, so --mcp exits 1
        while still printing the checks."""
        from recon_tool.server import mcp as server_mcp

        with patch.object(server_mcp, "list_tools", new=AsyncMock(return_value=[])):
            result = runner.invoke(app, ["doctor", "--mcp"])

        assert result.exit_code == 1
        assert "missing canonical" in result.output

    def test_doctor_mcp_exits_one_when_instructions_are_missing(self) -> None:
        from recon_tool.server import mcp as server_mcp

        with patch.object(type(server_mcp), "instructions", new_callable=PropertyMock, return_value=""):
            result = runner.invoke(app, ["doctor", "--mcp"])

        assert result.exit_code == 1
        assert "Server Instructions" in result.output
        assert "agents may misuse tools" in result.output

    def test_doctor_mcp_exits_one_when_only_unrelated_tool_is_registered(self) -> None:
        unrelated = type("Tool", (), {"name": "unrelated_tool"})()

        from recon_tool.server import mcp as server_mcp

        with patch.object(server_mcp, "list_tools", new=AsyncMock(return_value=[unrelated])):
            result = runner.invoke(app, ["doctor", "--mcp"])

        assert result.exit_code == 1
        assert "missing canonical" in result.output
        assert "lookup_tenant" in result.output

    def test_doctor_mcp_exits_one_when_required_resources_are_missing(self) -> None:
        from recon_tool.server import mcp as server_mcp

        with patch.object(server_mcp, "list_resources", new=AsyncMock(return_value=[])):
            result = runner.invoke(app, ["doctor", "--mcp"])

        assert result.exit_code == 1
        assert "Resources enumerated" in result.output
        assert "missing canonical" in result.output
        assert "recon://fingerprints" in result.output

    def test_resource_check_still_runs_when_tool_listing_fails(self) -> None:
        from recon_tool.server import mcp as server_mcp

        with patch.object(
            server_mcp,
            "list_tools",
            new=AsyncMock(side_effect=RuntimeError("synthetic tool failure")),
        ):
            result = runner.invoke(app, ["doctor", "--mcp"])

        assert result.exit_code == 1
        assert "synthetic tool failure" in result.output
        assert "Resources enumerated" in result.output

    def test_tool_check_remains_visible_when_resource_listing_fails(self) -> None:
        from recon_tool.server import mcp as server_mcp

        with patch.object(
            server_mcp,
            "list_resources",
            new=AsyncMock(side_effect=RuntimeError("synthetic resource failure")),
        ):
            result = runner.invoke(app, ["doctor", "--mcp"])

        assert result.exit_code == 1
        assert "Tools enumerated" in result.output
        assert "synthetic resource failure" in result.output

    def test_long_static_failure_uses_an_indented_detail_block(self) -> None:
        output = io.StringIO()
        console = Console(file=output, width=40, color_system=None)
        detail = "missing canonical: " + ", ".join(
            (
                "recon://fingerprints",
                "recon://signals",
                "recon://profiles",
                "recon://schema",
                "recon://surface-inventory",
            )
        )

        with patch("recon_tool.cli.doctor.get_err_console", return_value=console):
            _render_mcp_checks([DoctorCheck("Resources enumerated", "fail", detail)])

        lines = output.getvalue().splitlines()
        assert lines[0].strip() == "fail  Resources enumerated:"
        assert all(line.startswith("        ") for line in lines[1:])
        assert "recon://surface-inventory" in output.getvalue()

    def test_long_phase_name_stays_indented_at_narrow_width(self) -> None:
        output = io.StringIO()
        console = Console(file=output, width=40, color_system=None)

        with patch("recon_tool.cli.doctor.get_err_console", return_value=console):
            _render_mcp_checks([DoctorCheck("resources/read recon://surface-inventory", "fail", "timed out after 30s")])

        lines = output.getvalue().splitlines()
        assert lines[0].strip() == "fail"
        assert all(line.startswith("        ") for line in lines[1:3])
        assert lines[-1].startswith("            ")
        assert not any(line.startswith("recon://") for line in lines)

    def test_long_diagnostic_token_stays_on_one_indented_line(self) -> None:
        output = io.StringIO()
        console = Console(file=output, width=40, color_system=None)
        token = "x" * 100

        with patch("recon_tool.cli.doctor.get_err_console", return_value=console):
            _render_mcp_checks([DoctorCheck("Resources enumerated", "fail", token)])

        lines = output.getvalue().splitlines()
        assert len(lines) == 2
        assert lines[1] == f"        {token}"
