"""Collection warnings, resolver wording and progress events (issue #227).

A DNS failure reads as "could not resolve", never as an SSRF refusal; a real
private-address refusal keeps its "skipped" wording. Without --debug the CLI
captures library warnings during collection and prints one deduplicated,
bounded, sanitized summary on stderr. Progress events reach a listener only
inside its scope and never from related-domain enrichment.
"""

from __future__ import annotations

import asyncio
import io
import json
import logging
import socket
from typing import Any
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from rich.console import Console
from typer.testing import CliRunner

from recon_tool import collection_progress
from recon_tool import http as http_mod
from recon_tool.cli import app
from recon_tool.cli.collection_warnings import (
    CollectionWarnings,
    capture_collection_warnings,
    debug_logging_active,
    print_collection_warnings,
)
from recon_tool.collection_progress import ProgressEvent, UnitOutcome, ct_outcome, mta_sts_outcome
from recon_tool.formatter import format_tenant_json, format_tenant_markdown, render_tenant_panel
from recon_tool.models import SourceResult, TenantInfo
from recon_tool.resolver import SourcePool, resolve_tenant

_LOGGER = logging.getLogger("recon")


def _fail_resolution(*_args: object, **_kwargs: object) -> list[Any]:
    raise socket.gaierror("synthetic DNS failure")


# ── Wording ────────────────────────────────────────────────────────────────


def test_unresolved_host_is_worded_as_a_resolution_failure(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr("recon_tool.http.socket.getaddrinfo", _fail_resolution)
    with caplog.at_level(logging.WARNING, logger="recon"):
        refusal = asyncio.run(http_mod._destination_refusal_async("login.example.com"))  # pyright: ignore[reportPrivateUsage]
    assert refusal is not None
    assert refusal.condition == "unresolved_host"
    assert caplog.messages == ["could not resolve login.example.com"]
    assert "SSRF" not in caplog.text
    assert caplog.records[0].recon_condition == "unresolved_host"  # type: ignore[attr-defined]


def test_private_address_refusal_keeps_skipped_wording(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    def private_answer(*_args: object, **_kwargs: object) -> list[Any]:
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.5", 0))]

    monkeypatch.setattr("recon_tool.http.socket.getaddrinfo", private_answer)
    with caplog.at_level(logging.WARNING, logger="recon"):
        assert asyncio.run(http_mod._is_private_ip_async("mta-sts.example.com")) is True  # pyright: ignore[reportPrivateUsage]
    assert caplog.messages == ["mta-sts.example.com skipped: resolves to a private address (10.0.0.5)"]


def test_sync_check_shares_the_wording(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    monkeypatch.setattr("recon_tool.http.socket.getaddrinfo", _fail_resolution)
    with caplog.at_level(logging.WARNING, logger="recon"):
        assert http_mod._is_private_ip("unresolved.example") is True  # pyright: ignore[reportPrivateUsage]
    assert caplog.messages == ["could not resolve unresolved.example"]


def test_transport_errors_name_the_condition(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("recon_tool.http.socket.getaddrinfo", _fail_resolution)
    transport = http_mod._SSRFSafeTransport()  # pyright: ignore[reportPrivateUsage]
    with pytest.raises(httpx.ConnectError) as unresolved:
        asyncio.run(transport.handle_async_request(httpx.Request("GET", "https://unresolved.example/")))
    assert str(unresolved.value).startswith("could not resolve unresolved.example")
    assert "SSRF" not in str(unresolved.value)
    with pytest.raises(httpx.ConnectError, match=r"SSRF blocked, 127\.0\.0\.1 skipped: a private address"):
        asyncio.run(transport.handle_async_request(httpx.Request("GET", "http://127.0.0.1/")))


# ── Capture and summary ────────────────────────────────────────────────────


def _log_unresolved(host: str) -> None:
    _LOGGER.warning("could not resolve %s", host, extra={"recon_condition": "unresolved_host", "recon_host": host})


def test_capture_dedupes_bounds_and_summarizes(capsys: pytest.CaptureFixture[str]) -> None:
    with capture_collection_warnings() as sink:
        for _ in range(8):
            _log_unresolved("login.microsoftonline.com")
        _log_unresolved("autodiscover.example.com")
        for index in range(5):
            _log_unresolved(f"host{index}.example.com")
        _LOGGER.warning(
            "x",
            extra={
                "recon_condition": "private_address",
                "recon_host": "mta-sts.example.com",
                "recon_address": "10.0.0.5",
            },
        )
        logging.getLogger("recon_tool.sources").warning("DNS detector failed")
    # The last-resort handler stayed quiet: nothing raw reached stderr.
    assert capsys.readouterr().err == ""
    assert sink.summary_lines() == [
        "7 hosts could not be resolved (login.microsoftonline.com, autodiscover.example.com, "
        "host0.example.com, and 4 more). Run recon doctor.",
        "1 host skipped: resolves to a private address (mta-sts.example.com 10.0.0.5). Run recon doctor.",
        "1 other collection warning. Run with --debug for details.",
    ]


def test_singular_unresolved_summary() -> None:
    sink = CollectionWarnings()
    sink.unresolved_hosts.append("login.microsoftonline.com")
    assert sink.summary_lines() == ["1 host could not be resolved (login.microsoftonline.com). Run recon doctor."]


def test_hostnames_are_sanitized_as_untrusted_data() -> None:
    with capture_collection_warnings() as sink:
        _log_unresolved("evil\x1b[2J\x1b]8;;x\x07.example.com\nsecond line " + "a" * 200)
    [line] = sink.summary_lines()
    assert "\x1b" not in line
    assert "\n" not in line
    assert "\x07" not in line
    assert "..." in line
    assert len(line) < 160


def test_capture_is_removed_after_the_scope() -> None:
    with capture_collection_warnings():
        assert any(handler.get_name() == "recon-cli-collection" for handler in _LOGGER.handlers)
    assert all(handler.get_name() != "recon-cli-collection" for handler in _LOGGER.handlers)


def test_debug_keeps_detailed_logging() -> None:
    handler = logging.StreamHandler(io.StringIO())
    handler.set_name("recon-cli-debug")
    _LOGGER.addHandler(handler)
    try:
        assert debug_logging_active()
        with capture_collection_warnings() as sink:
            _log_unresolved("login.example.com")
        assert sink.summary_lines() == []
        assert "could not resolve login.example.com" in handler.stream.getvalue()  # type: ignore[attr-defined]
    finally:
        _LOGGER.removeHandler(handler)


def test_summary_prints_one_marked_line_per_condition() -> None:
    sink = CollectionWarnings(unresolved_hosts=["a.example.com", "b.example.com"])
    buffer = io.StringIO()
    print_collection_warnings(sink, Console(file=buffer, width=40, no_color=True))
    assert buffer.getvalue() == "! 2 hosts could not be resolved (a.example.com, b.example.com). Run recon doctor.\n"


# ── CLI streams ────────────────────────────────────────────────────────────

_INFO = TenantInfo(
    tenant_id=None,
    display_name="example.com",
    default_domain="example.com",
    queried_domain="example.com",
    services=("DMARC",),
    sources=("dns_records",),
)


def _results() -> list[SourceResult]:
    return [
        SourceResult(source_name="oidc_discovery", error="No M365 tenant"),
        SourceResult(source_name="user_realm", error="Network error", source_unavailable=True),
        SourceResult(source_name="google_identity", error="No federated IdP redirect observed"),
        SourceResult(source_name="google_workspace", not_attempted=True),
        SourceResult(source_name="dns_records", detected_services=("DMARC",)),
    ]


async def _resolve_with_warning(*_args: object, **_kwargs: object) -> tuple[TenantInfo, list[SourceResult]]:
    _log_unresolved("login.microsoftonline.com")
    _log_unresolved("login.microsoftonline.com")
    return _INFO, _results()


def test_panel_lookup_routes_ladder_and_summary_to_stderr() -> None:
    with patch("recon_tool.resolver.resolve_tenant", new=AsyncMock(side_effect=_resolve_with_warning)):
        result = CliRunner().invoke(app, ["example.com", "--no-cache"])
    assert result.exit_code == 0, result.output
    assert result.stderr.splitlines() == [
        "6 sources: 1 matched, 4 no match, 1 unavailable (user realm: error)",
        "! 1 host could not be resolved (login.microsoftonline.com). Run recon doctor.",
    ]
    assert "sources:" not in result.stdout
    assert "could not be resolved" not in result.stdout
    assert "\x1b" not in result.stdout + result.stderr


def test_json_lookup_keeps_stdout_pure_and_skips_the_ladder() -> None:
    with patch("recon_tool.resolver.resolve_tenant", new=AsyncMock(side_effect=_resolve_with_warning)):
        result = CliRunner().invoke(app, ["example.com", "--json", "--no-cache"])
    assert result.exit_code == 0, result.output
    json.loads(result.stdout)
    assert "sources:" not in result.stderr
    assert result.stderr.splitlines() == [
        "! 1 host could not be resolved (login.microsoftonline.com). Run recon doctor."
    ]


# ── Progress events ────────────────────────────────────────────────────────


def test_emit_without_a_listener_is_a_no_op() -> None:
    assert not collection_progress.listening()
    collection_progress.emit("dns_records", "start")


def test_listener_follows_tasks_and_suppression_blocks_nested_work() -> None:
    seen: list[tuple[str, str]] = []

    async def scenario() -> None:
        async def unit(name: str) -> None:
            collection_progress.emit(name, "done", outcome=UnitOutcome("match"))

        with collection_progress.progress_listener(lambda event: seen.append((event.unit, event.phase))):
            await asyncio.gather(unit("a"), unit("b"))
            with collection_progress.suppressed():
                await asyncio.gather(unit("related"))
        await unit("after")

    asyncio.run(scenario())
    assert sorted(seen) == [("a", "done"), ("b", "done")]


class _FakeSource:
    def __init__(self, name: str, result: SourceResult | Exception) -> None:
        self._name = name
        self._result = result

    @property
    def name(self) -> str:
        return self._name

    async def lookup(self, domain: str, **kwargs: Any) -> SourceResult:
        if isinstance(self._result, Exception):
            raise self._result
        return self._result


def test_resolver_reports_each_source_start_and_result() -> None:
    from recon_tool.resolver import SourcePool, resolve_tenant

    pool = SourcePool(
        [
            _FakeSource(
                "oidc_discovery", SourceResult(source_name="oidc_discovery", tenant_id="t", m365_detected=True)
            ),
            _FakeSource("user_realm", RuntimeError("boom")),
        ]
    )
    events: list[ProgressEvent] = []

    async def scenario() -> None:
        with collection_progress.progress_listener(events.append):
            await resolve_tenant("example.com", pool=pool)

    asyncio.run(scenario())
    phases = [(event.unit, event.phase) for event in events]
    assert phases.count(("oidc_discovery", "start")) == 1
    assert phases.count(("user_realm", "done")) == 1
    failed = next(event for event in events if event.unit == "user_realm" and event.phase == "done")
    assert failed.result is not None
    assert failed.result.source_unavailable


@pytest.mark.parametrize(
    ("fields", "expected"),
    [
        (
            {"subdomain_count": 3, "has_summary": False, "degraded": (), "attempt_outcome": "live_success"},
            UnitOutcome("match"),
        ),
        (
            {"subdomain_count": 0, "has_summary": True, "degraded": ("crt.sh",), "attempt_outcome": None},
            UnitOutcome("match"),
        ),
        (
            {"subdomain_count": 0, "has_summary": False, "degraded": (), "attempt_outcome": None},
            UnitOutcome("no_match"),
        ),
        (
            {
                "subdomain_count": 0,
                "has_summary": False,
                "degraded": ("certspotter", "crt.sh"),
                "attempt_outcome": "live_rate_limited",
            },
            UnitOutcome("unavailable", "certspotter, crt.sh rate limited"),
        ),
        (
            {"subdomain_count": 0, "has_summary": False, "degraded": ("crt.sh",), "attempt_outcome": None},
            UnitOutcome("unavailable", "crt.sh failed"),
        ),
        (
            {"subdomain_count": 0, "has_summary": False, "degraded": ("detector:cert_intel",), "attempt_outcome": None},
            UnitOutcome("unavailable", "collector error"),
        ),
    ],
)
def test_ct_outcome(fields: dict[str, Any], expected: UnitOutcome) -> None:
    assert ct_outcome(**fields) == expected


@pytest.mark.parametrize(
    ("fields", "expected"),
    [
        ({"mode": "enforce", "record_observed": True, "degraded": ()}, UnitOutcome("match")),
        ({"mode": None, "record_observed": True, "degraded": ()}, UnitOutcome("match")),
        ({"mode": None, "record_observed": False, "degraded": ()}, UnitOutcome("no_match")),
        (
            {"mode": None, "record_observed": False, "degraded": ("dns:mta_sts",)},
            UnitOutcome("unavailable", "DNS query failed"),
        ),
        (
            {"mode": None, "record_observed": True, "degraded": ("http:mta_sts_policy",)},
            UnitOutcome("unavailable", "policy fetch failed"),
        ),
    ],
)
def test_mta_sts_outcome(fields: dict[str, Any], expected: UnitOutcome) -> None:
    assert mta_sts_outcome(**fields) == expected


@pytest.mark.asyncio
async def test_public_endpoint_refusal_is_local_to_its_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    async def reserved_answer(_host: str) -> tuple[str, ...]:
        return ("198.18.0.1",)

    class Source:
        name = "fixture"

        async def lookup(self, domain: str, **kwargs: Any) -> SourceResult:
            host = "accounts.google.com" if domain == "public.test" else "mta-sts.private.test"
            async with http_mod.http_client() as client:
                with pytest.raises(httpx.ConnectError):
                    await client.get(f"https://{host}/")
            return SourceResult(source_name=self.name)

    monkeypatch.setattr("recon_tool.network_policy.selected_addresses", reserved_answer)
    pool = SourcePool([Source()])
    (public, _), (private, _) = await asyncio.gather(
        resolve_tenant("public.test", pool=pool), resolve_tenant("private.test", pool=pool)
    )
    assert json.loads(format_tenant_json(public))["degraded_sources"] == ["resolver:public_endpoint_private_address"]
    assert private.degraded_sources == ()
    console = Console(file=io.StringIO(), width=100, record=True)
    console.print(render_tenant_panel(public))
    for rendered in (console.export_text(), format_tenant_markdown(public)):
        assert "Related domains may be artifacts" in " ".join(rendered.split())
        assert "Run recon doctor" in " ".join(rendered.split())
