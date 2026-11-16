"""Offline regression cases for equivalent operator-facing status views."""

from __future__ import annotations

from dataclasses import replace
from io import StringIO

import pytest
from rich.console import Console

from recon_tool.formatter import format_tenant_dict, format_tenant_plain, render_tenant_panel
from recon_tool.formatter.collection_status import source_display_state
from recon_tool.formatter.panel import render_source_status_panel, render_sources_detail, render_verbose_sources
from recon_tool.models import ConfidenceLevel, SourceResult, TenantInfo

_BASE = TenantInfo(
    tenant_id=None,
    display_name="Synthetic Alpha",
    default_domain="alpha.invalid",
    queried_domain="alpha.invalid",
    confidence=ConfidenceLevel.MEDIUM,
    sources=("dns_records",),
)


@pytest.mark.parametrize(
    ("overrides", "expected"),
    [
        ({}, None),
        ({"degraded_sources": ("dns:dmarc",)}, "1 source unavailable (dns:dmarc)"),
        (
            {"degraded_sources": ("crt.sh", "certspotter")},
            "All CT providers unavailable (crt.sh, certspotter)",
        ),
        (
            {"degraded_sources": ("crt.sh",), "ct_provider_used": "certspotter", "ct_subdomain_count": 12},
            None,
        ),
        (
            {
                "degraded_sources": ("crt.sh", "certspotter"),
                "ct_provider_used": "crt.sh (cached)",
                "ct_subdomain_count": 12,
                "ct_cache_age_days": 2,
            },
            "CT: from local cache, 2 days old (12 subdomains)",
        ),
        (
            {
                "degraded_sources": ("crt.sh",),
                "ct_provider_used": "crt.sh (cached)",
                "ct_subdomain_count": 4,
                "ct_cache_age_days": 0,
            },
            "CT: from local cache, today (4 subdomains)",
        ),
    ],
)
def test_default_plain_keeps_material_panel_collection_caveats(
    overrides: dict[str, object], expected: str | None
) -> None:
    info = replace(_BASE, **overrides)
    plain = format_tenant_plain(info)
    buffer = StringIO()
    console = Console(file=buffer, width=120, no_color=True)
    console.print(render_tenant_panel(info))
    panel = buffer.getvalue()

    if expected is None:
        assert "collection_note:" not in plain
        assert "sources unavailable" not in panel
        assert "source unavailable" not in panel
        assert "All CT providers unavailable" not in panel
        assert "CT: from local cache" not in panel
    else:
        assert f"collection_note: {expected}." in plain
        assert expected in panel
    assert "collection_note" not in format_tenant_dict(info)
    assert "collection_note:" not in format_tenant_plain(info, full=True)


@pytest.mark.parametrize("confidence", list(ConfidenceLevel))
@pytest.mark.parametrize("detailed", [False, True])
def test_sparse_plain_guidance_only_appears_before_diagnostics(confidence: ConfidenceLevel, detailed: bool) -> None:
    info = replace(_BASE, confidence=confidence)
    rendered = format_tenant_plain(info, detailed=detailed)
    expected = confidence is ConfidenceLevel.LOW and not detailed
    assert ("next: Use --explain to inspect evidence or --verbose to review source status." in rendered) is expected
    assert "next:" not in format_tenant_plain(info, full=True)


@pytest.mark.parametrize(
    ("result", "panel_state", "verbose_state"),
    [
        (SourceResult(source_name="oidc_discovery", tenant_id="synthetic-tenant"), "match", "match"),
        (SourceResult(source_name="oidc_discovery"), "no_match", "no_match"),
        (
            SourceResult(source_name="oidc_discovery", error="No Google Workspace configuration found"),
            "no_match",
            "no_match",
        ),
        (SourceResult(source_name="oidc_discovery", error="HTTP 400 from OIDC discovery"), "no_match", "no_match"),
        (
            SourceResult(source_name="oidc_discovery", error="request timed out", source_unavailable=True),
            "unavailable",
            "unavailable",
        ),
        # The panel treats a non-soft error as unavailable. The source ladder,
        # which --verbose and the source-health line share, counts that row as
        # no match unless source_unavailable is set.
        (
            SourceResult(source_name="oidc_discovery", error="request timed out", tenant_id="synthetic"),
            "unavailable",
            "no_match",
        ),
        (
            SourceResult(source_name="oidc_discovery", error="No Google Workspace response", source_unavailable=True),
            "unavailable",
            "unavailable",
        ),
        (SourceResult(source_name="oidc_discovery", source_unavailable=True), "unavailable", "unavailable"),
    ],
)
def test_source_views_share_match_miss_and_unavailable_states(
    result: SourceResult,
    panel_state: str,
    verbose_state: str,
) -> None:
    assert source_display_state(result) == panel_state
    buffer = StringIO()
    console = Console(file=buffer, width=180, no_color=True)
    render_verbose_sources([result], console=console)
    verbose = buffer.getvalue()
    buffer.truncate(0)
    buffer.seek(0)
    console.print(render_sources_detail([result]))
    detail = buffer.getvalue()
    buffer.truncate(0)
    buffer.seek(0)
    console.print(render_source_status_panel([result]))
    status = buffer.getvalue()

    assert {
        "match": "match oidc_discovery",
        "no_match": "no match oidc_discovery",
        "unavailable": "unavailable oidc_discovery",
    }[verbose_state] in verbose
    assert {"match": "success", "no_match": "no match", "unavailable": "unavailable"}[panel_state] in detail
    marker = {"match": "\u2713", "no_match": "\u2013", "unavailable": "\u2717"}[panel_state]
    assert f"{marker} oidc_discovery" in status
    if verbose_state == "unavailable":
        assert "no match" not in verbose
    if panel_state == "unavailable":
        assert "no match" not in detail
