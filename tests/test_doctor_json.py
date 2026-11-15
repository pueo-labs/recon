# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportPrivateUsage=none
"""`recon doctor` status vocabulary, JSON rendering, summary, and resolver probe.

Every network edge is stubbed: httpx.AsyncClient, dns.resolver.resolve, the
PATH launcher, and the PyPI release lookup. No test touches the network.
"""

from __future__ import annotations

import json
import re
from io import StringIO
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import dns.exception
import dns.resolver
import httpx
import pytest
from rich.console import Console
from typer.testing import CliRunner

import recon_tool.mcp_client.client_doctor as client_doctor
from recon_tool.cli import app
from recon_tool.cli.doctor import (
    RESOLVER_ANSWERS_NONEXISTENT,
    RESOLVER_PROBE_PREFIX,
    _doctor_dns_check,
    _doctor_render,
    _doctor_resolver_probe,
)
from recon_tool.cli.doctor_report import DoctorCheck, doctor_json_payload, summarize_checks
from recon_tool.cli.shared import DIAGNOSTIC_STATUS_STYLES, render_status_row
from recon_tool.exit_codes import EXIT_ERROR, EXIT_NO_DATA, EXIT_VALIDATION

runner = CliRunner()
_ROOT = Path(__file__).resolve().parents[1]

_ANSI = re.compile(r"\x1b\[[0-9;]*m")
_ROW = re.compile(r"^  (?P<mark>  ok|warn|fail|info)  (?P<name>[^:]+):")

MIXED_CHECKS = [
    DoctorCheck("Launcher", "ok", "matches"),
    DoctorCheck("Release status", "warn", "newer release available", "recon update"),
    DoctorCheck("DNS resolution", "fail", "the resolver did not answer in time", "check the resolver"),
    DoctorCheck("Nonexistent-name probe", "info", "could not run the probe"),
]


def _response(status: int = 200) -> MagicMock:
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status
    return resp


def _http_client() -> AsyncMock:
    client = AsyncMock()
    client.get = AsyncMock(return_value=_response(200))
    client.post = AsyncMock(return_value=_response(200))
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    return client


def _resolver(*, answers_everything: bool = False, fail_example: BaseException | None = None) -> Any:
    """Stub resolver. Honest by default; optionally answers every name."""

    def _resolve(qname: str, rdtype: str = "A", *args: object, **kwargs: object) -> list[MagicMock]:
        name = str(qname).rstrip(".")
        if name == "example.com" and fail_example is not None:
            raise fail_example
        if name.endswith(".invalid") and not answers_everything:
            raise dns.resolver.NXDOMAIN()
        return [MagicMock(), MagicMock()]

    return _resolve


@pytest.fixture(autouse=True)
def _stable_environment():
    from recon_tool import updater

    with (
        patch(
            "recon_tool.cli.doctor._doctor_path_launcher_check",
            return_value=DoctorCheck("PATH recon launcher", "ok", "test launcher matches running package"),
        ),
        patch("recon_tool.updater.fetch_latest_version", return_value=updater.current_version()),
        patch("httpx.AsyncClient", return_value=_http_client()),
    ):
        yield


def _human_statuses(output: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for line in _ANSI.sub("", output).splitlines():
        match = _ROW.match(line)
        if match is not None:
            statuses[match.group("name")] = match.group("mark").strip()
    return statuses


class TestStatusVocabulary:
    def test_one_map_covers_the_four_words(self) -> None:
        assert DIAGNOSTIC_STATUS_STYLES == {"ok": "green", "warn": "yellow", "fail": "red", "info": "blue"}

    @pytest.mark.parametrize("status", ["ok", "warn", "fail", "info"])
    def test_rows_are_lowercase_right_aligned_and_colored(self, status: str) -> None:
        stream = StringIO()
        console = Console(file=stream, force_terminal=True, color_system="standard", width=100)

        render_status_row(console, status, "Probe", "detail")  # pyright: ignore[reportArgumentType]

        raw = stream.getvalue()
        assert _ANSI.sub("", raw).startswith(f"  {status:>4}  Probe: detail")
        color = {"ok": "32", "warn": "33", "fail": "31", "info": "34"}[status]
        assert f"\x1b[{color}m{status:>4}" in raw

    def test_doctor_module_has_no_status_marks_outside_the_shared_map(self) -> None:
        source = (_ROOT / "src" / "recon_tool" / "cli" / "doctor.py").read_text(encoding="utf-8")
        assert not re.search(r'"WARN"|"FAIL"|"·"', source)


class TestHumanAndJsonAgree:
    def test_renderers_agree_on_every_status_for_the_same_check_list(self) -> None:
        stream = StringIO()
        _doctor_render(Console(file=stream, color_system=None, width=120), MIXED_CHECKS)
        payload = doctor_json_payload(MIXED_CHECKS, summarize_checks(MIXED_CHECKS, mode="doctor"), mode="doctor")

        human = _human_statuses(stream.getvalue())
        machine = {check["name"]: check["status"] for check in payload["checks"]}
        assert human == machine == {check.name: check.status for check in MIXED_CHECKS}

    def test_commands_agree_end_to_end(self) -> None:
        with patch("dns.resolver.resolve", side_effect=_resolver(fail_example=dns.exception.Timeout())):
            human = runner.invoke(app, ["doctor"])
            machine = runner.invoke(app, ["doctor", "--json"])

        payload = json.loads(machine.stdout)
        assert human.exit_code == machine.exit_code == EXIT_ERROR
        assert payload["summary"]["exit_code"] == EXIT_ERROR
        assert _human_statuses(human.stdout) == {check["name"]: check["status"] for check in payload["checks"]}


class TestSummary:
    def test_failure_summary_is_red_and_ends_with_next_command(self) -> None:
        stream = StringIO()
        console = Console(file=stream, force_terminal=True, color_system="standard", width=200)
        checks = [
            DoctorCheck("DNS resolution", "fail", "timed out", "rerun `recon doctor`"),
            DoctorCheck("OIDC discovery", "fail", "HTTP 503", "check the proxy"),
        ]

        assert _doctor_render(console, checks) is True

        summary_line = next(line for line in stream.getvalue().splitlines() if "failed" in line)
        assert "\x1b[31m" in summary_line
        assert _ANSI.sub("", summary_line).strip() == (
            "2 checks failed. Lookups may be incomplete. Next: rerun `recon doctor`"
        )

    def test_warning_only_summary_is_yellow_with_an_honest_count(self) -> None:
        stream = StringIO()
        console = Console(file=stream, force_terminal=True, color_system="standard", width=200)
        checks = [
            DoctorCheck("PATH recon launcher", "warn", "stale"),
            DoctorCheck("Release status", "warn", "old", "recon update"),
            DoctorCheck("Nonexistent-name probe", "info", "could not run"),
        ]

        assert _doctor_render(console, checks) is False

        summary_line = next(line for line in stream.getvalue().splitlines() if "Core checks" in line)
        assert "\x1b[33m" in summary_line
        assert "Core checks passed with 2 warnings." in summary_line

    def test_info_rows_do_not_change_an_all_clear(self) -> None:
        summary = summarize_checks(
            [DoctorCheck("A", "ok", ""), DoctorCheck("B", "info", "")],
            mode="doctor",
        )
        assert (summary.status, summary.message, summary.exit_code) == ("ok", "All checks passed.", 0)

    def test_failed_dns_names_its_next_step(self) -> None:
        with patch("dns.resolver.resolve", side_effect=_resolver(fail_example=dns.exception.Timeout())):
            result = runner.invoke(app, ["doctor"])

        collapsed = " ".join(_ANSI.sub("", result.stdout).split())
        assert result.exit_code == EXIT_ERROR
        assert "1 check failed. Lookups may be incomplete. Next: check the system resolver and network" in collapsed
        assert collapsed.endswith("then rerun `recon doctor`")

    def test_mcp_and_client_modes_have_their_own_next_step(self) -> None:
        mcp = summarize_checks([DoctorCheck("Server module", "fail", "boom")], mode="mcp")
        client = summarize_checks([DoctorCheck("recon stanza", "fail", "missing")], mode="client", client="cursor")
        assert mcp.message.endswith("Next: pip install -U recon-tool, then rerun `recon doctor --mcp`")
        assert client.message.endswith("Next: recon mcp install --client=cursor")
        assert client.exit_code == EXIT_NO_DATA


class TestDoctorJson:
    def test_json_shape_and_success_exit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("FORCE_COLOR", "1")
        with patch("dns.resolver.resolve", side_effect=_resolver()):
            result = runner.invoke(app, ["doctor", "--json"])

        assert result.exit_code == 0
        assert "\x1b" not in result.stdout
        payload = json.loads(result.stdout)
        assert set(payload) == {"schema_version", "mode", "recon_version", "checks", "summary", "notes"}
        assert payload["schema_version"] == 1
        assert payload["mode"] == "doctor"
        for check in payload["checks"]:
            assert set(check) == {"name", "status", "detail", "next"}
            assert check["status"] in {"ok", "warn", "fail", "info"}
        names = {check["name"] for check in payload["checks"]}
        assert "crt.sh (cert transparency)" in names
        assert "certspotter (cert transparency)" in names
        summary = payload["summary"]
        assert summary["status"] == "ok"
        assert summary["exit_code"] == 0
        assert summary["total"] == len(payload["checks"])
        assert summary["fail"] == 0
        assert summary["next"] is None

    def test_json_failure_keeps_the_human_exit_code(self) -> None:
        with patch("dns.resolver.resolve", side_effect=_resolver(fail_example=dns.resolver.NoNameservers())):
            result = runner.invoke(app, ["doctor", "--json"])

        assert result.exit_code == EXIT_ERROR
        payload = json.loads(result.stdout)
        dns_row = next(check for check in payload["checks"] if check["name"] == "DNS resolution")
        assert dns_row["status"] == "fail"
        assert dns_row["next"]
        assert payload["summary"]["status"] == "fail"
        assert payload["summary"]["next"] == dns_row["next"]

    @pytest.mark.parametrize("mode", [["--mcp"], ["--fix"]])
    def test_json_is_refused_for_modes_without_a_check_report(self, mode: list[str]) -> None:
        result = runner.invoke(app, ["doctor", *mode, "--json"])
        assert result.exit_code == EXIT_VALIDATION
        assert result.stdout == ""
        assert "--json works with recon doctor and --client" in result.stderr

    def test_client_json_reports_rows_notes_and_exit(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
        monkeypatch.setenv("APPDATA", str(tmp_path / "AppData" / "Roaming"))
        monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)

        missing = runner.invoke(app, ["doctor", "--client", "claude-code", "--json"])
        assert missing.exit_code == EXIT_NO_DATA
        payload = json.loads(missing.stdout)
        assert payload["mode"] == "client"
        assert payload["client"] == "claude-code"
        assert payload["notes"]
        assert payload["summary"]["next"] == "recon mcp install --client=claude-code"

        def _which(_name: str) -> str:
            return "/usr/local/bin/recon"

        monkeypatch.setattr(client_doctor.shutil, "which", _which)
        (tmp_path / ".claude.json").write_text(
            json.dumps({"mcpServers": {"recon": {"command": "recon", "args": ["mcp"]}}}), encoding="utf-8"
        )
        found = runner.invoke(app, ["doctor", "--client", "claude-code", "--json"])
        assert found.exit_code == 0
        assert json.loads(found.stdout)["summary"]["fail"] == 0


class TestResolverCondition:
    def test_resolver_that_answers_every_name_draws_the_named_warning(self) -> None:
        with patch("dns.resolver.resolve", side_effect=_resolver(answers_everything=True)):
            result = runner.invoke(app, ["doctor"])
            machine = runner.invoke(app, ["doctor", "--json"])

        collapsed = " ".join(result.stdout.split())
        assert result.exit_code == 0
        assert (
            "warn Nonexistent-name probe: Resolver answers names that should not exist; "
            "related-domain results will be unreliable. See docs/limitations.md"
        ) in collapsed
        row = next(c for c in json.loads(machine.stdout)["checks"] if c["name"] == "Nonexistent-name probe")
        assert row["status"] == "warn"
        assert row["detail"] == RESOLVER_ANSWERS_NONEXISTENT

    def test_probe_uses_a_random_reserved_invalid_name(self) -> None:
        seen: list[tuple[str, str]] = []

        def _resolve(qname: str, rdtype: str = "A", *args: object, **kwargs: object) -> list[object]:
            seen.append((qname, rdtype))
            raise dns.resolver.NXDOMAIN()

        with patch("dns.resolver.resolve", side_effect=_resolve):
            first = _doctor_resolver_probe()
            _doctor_resolver_probe()

        assert first.status == "ok"
        assert all(q.startswith(RESOLVER_PROBE_PREFIX) and q.endswith(".invalid") for q, _ in seen)
        assert seen[0][0] != seen[1][0]
        assert {rdtype for _, rdtype in seen} == {"A"}

    def test_nodata_for_a_reserved_name_is_also_named(self) -> None:
        with patch("dns.resolver.resolve", side_effect=dns.resolver.NoAnswer()):
            check = _doctor_resolver_probe()
        assert check.status == "warn"
        assert check.detail == RESOLVER_ANSWERS_NONEXISTENT
        assert check.next

    def test_unreachable_resolver_leaves_the_probe_inconclusive(self) -> None:
        with patch("dns.resolver.resolve", side_effect=dns.exception.Timeout()):
            check = _doctor_resolver_probe()
        assert check.status == "info"
        assert "could not run the probe" in check.detail

    def test_limitations_doc_carries_the_linked_anchor(self) -> None:
        text = (_ROOT / "docs" / "limitations.md").read_text(encoding="utf-8")
        assert "### Resolvers that answer names that should not exist" in text


class TestPlainDnsDetail:
    @pytest.mark.parametrize(
        ("exc", "expected"),
        [
            (dns.resolver.NoAnswer(), "the resolver returned no TXT records for example.com, although it publishes"),
            (dns.resolver.NXDOMAIN(), "the resolver says example.com does not exist"),
            (dns.resolver.NoNameservers(), "no configured resolver could answer"),
            (dns.exception.Timeout(), "the resolver did not answer in time"),
            (OSError("network unreachable"), "could not reach the resolver (network unreachable)"),
        ],
    )
    def test_dns_failures_read_as_plain_language(self, exc: BaseException, expected: str) -> None:
        with patch("dns.resolver.resolve", side_effect=exc):
            check = _doctor_dns_check()
        assert check.status == "fail"
        assert expected in check.detail
        assert "does not contain an answer to the question" not in check.detail
        assert "IN TXT" not in check.detail
