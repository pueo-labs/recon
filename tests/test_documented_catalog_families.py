# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportPrivateUsage=none, reportUnknownArgumentType=none, reportUnknownVariableType=none
"""Documented routing/marker families preserve record and namespace roles."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

import pytest

from recon_tool.bayesian import infer_from_tenant_info
from recon_tool.fingerprints import get_cname_target_rules, load_builtin_fingerprints
from recon_tool.formatter.classify import category_for_slug
from recon_tool.formatter.serialize import format_tenant_dict, format_tenant_plain
from recon_tool.fusion import compute_slug_posteriors
from recon_tool.merger import merge_results
from recon_tool.models import EvidenceRecord, SourceResult, TenantInfo
from recon_tool.source_status import SourceStatus
from recon_tool.sources import dns as dns_source
from recon_tool.sources import dns_base, dns_email, dns_replay
from recon_tool.sources.dns_tables import classify_chain

FAMILIES = (("improvmx", "ImprovMX", "improvmx.com"), ("forward-email", "Forward Email", "forwardemail.net"))


def _fixture(
    monkeypatch: pytest.MonkeyPatch,
    records: dict[tuple[str, str], list[str]],
    failures: frozenset[tuple[str, str]] = frozenset(),
) -> list[tuple[str, str]]:
    queries: list[tuple[str, str]] = []

    async def resolve(
        name: str,
        record_type: str,
        *,
        degraded_sources: set[str] | None = None,
        degraded_name: str = "",
        **_kwargs: object,
    ) -> list[str]:
        key = (name.lower().rstrip("."), record_type)
        queries.append(key)
        if key in failures:
            if degraded_sources is not None:
                degraded_sources.add(degraded_name)
            return []
        return records.get(key, [])

    monkeypatch.setattr(dns_base, "safe_resolve", resolve)
    return queries


def _info(ctx: dns_base.DetectionCtx) -> TenantInfo:
    return TenantInfo(
        tenant_id=None,
        display_name="Synthetic",
        default_domain="example.com",
        queried_domain="example.com",
        services=tuple(sorted(ctx.services)),
        slugs=tuple(sorted(ctx.slugs)),
        evidence=tuple(ctx.evidence),
        surface_attributions=tuple(ctx.surface_attributions),
        degraded_sources=tuple(sorted(ctx.degraded_sources)),
    )


def test_families_have_current_documented_basis_scoped_descriptions_and_classification() -> None:
    expected = {"convex": (1, "Cloud"), "improvmx": (3, "Email"), "forward-email": (4, "Email")}
    for fp in load_builtin_fingerprints():
        if fp.slug not in expected:
            continue
        count, category = expected.pop(fp.slug)
        assert len(fp.detections) == count
        assert category_for_slug(fp.slug) == category
        for rule in fp.detections:
            assert rule.verified == "2026-10-23"
            assert rule.reference.startswith("https://")
            assert "Does not" in rule.description
        assert fp.match_mode == "any"
    assert not expected


@pytest.mark.parametrize("target", ["convex.domains", "CONVEX.DOMAINS."])
def test_convex_exact_documented_target_retains_matching_rule(target: str) -> None:
    application, infrastructure = classify_chain([target], get_cname_target_rules())
    assert application is not None
    assert application.slug == "convex"
    assert application.pattern == r"^convex\.domains\.?$"
    assert infrastructure is None


@pytest.mark.parametrize(
    "target", ["convex.domains.attacker.invalid", "notconvex.domains", "foo.convex.domains", "convexXdomains"]
)
def test_convex_lookalikes_and_child_hosts_do_not_match(target: str) -> None:
    application, infrastructure = classify_chain([target], get_cname_target_rules())
    assert application is None
    assert infrastructure is None


def test_convex_backend_behind_a_proxy_only_attributes_the_visible_route() -> None:
    application, infrastructure = classify_chain(["cname.vercel-dns.com."], get_cname_target_rules())
    assert application is not None
    assert application.slug == "vercel"
    assert infrastructure is None


@pytest.mark.asyncio
async def test_convex_surface_keeps_queried_host_and_chain_without_apex_claim(monkeypatch: pytest.MonkeyPatch) -> None:
    queries = _fixture(monkeypatch, {("api.example.com", "CNAME"): ["CONVEX.DOMAINS."]})
    ctx = dns_base.DetectionCtx()
    ctx.related_domains.add("api.example.com")
    await dns_source._classify_related_surface(ctx, "example.com")
    (surface,) = ctx.surface_attributions
    assert surface.subdomain == "api.example.com"
    assert surface.primary_slug == "convex"
    assert surface.primary_tier == "application"
    assert not ctx.slugs
    assert not ctx.services
    assert ctx.evidence == [EvidenceRecord("CNAME", "api.example.com: convex.domains", "Convex", "convex")]
    serialized = format_tenant_dict(_info(ctx))
    assert serialized["surface_attributions"][0]["subdomain"] == "api.example.com"
    assert "convex" not in serialized["slugs"]
    assert all(kind == "CNAME" for _, kind in queries)
    assert not any(name.startswith("_convex_domains.") for name, _ in queries)


@pytest.mark.asyncio
@pytest.mark.parametrize("family", FAMILIES, ids=lambda family: family[0])
@pytest.mark.parametrize("prefix", ["mx1", "mx2", "child.mx1"])
@pytest.mark.parametrize("root_dot", ["", "."])
async def test_mx_documents_suffix_semantics_and_preserves_exact_record(
    monkeypatch: pytest.MonkeyPatch, family: tuple[str, str, str], prefix: str, root_dot: str
) -> None:
    slug, name, suffix = family
    target = f"{prefix}.{suffix}"
    value = f"10 {target.upper()}{root_dot}"
    queries = _fixture(monkeypatch, {("example.com", "MX"): [value, value]})
    ctx = dns_base.DetectionCtx()
    await dns_email.detect_mx(ctx, "example.com")
    assert ctx.slugs == {slug}
    evidence = EvidenceRecord("MX", value, name, slug)
    assert set(ctx.evidence) == {evidence}
    pattern = f"{prefix.split('.')[-1]}.{suffix}"
    assert (slug, "mx", pattern) in ctx._matched_fp_detections
    assert compute_slug_posteriors(tuple(ctx.evidence)) == compute_slug_posteriors((evidence,))
    replayed = dns_replay.replay_cached_dns_fingerprints(
        SourceResult(source_name="dns_records", raw_dns_records=(("MX", value),))
    )
    assert set(replayed.detected_slugs) == {slug}
    assert evidence in replayed.evidence
    info = _info(ctx)
    serialized = format_tenant_dict(info)
    assert serialized["queried_domain"] == "example.com"
    assert any(record["raw_value"] == value and record["source_type"] == "MX" for record in serialized["evidence"])
    assert queries == [("example.com", "MX")]
    rendered = format_tenant_plain(info).lower()
    assert name.lower() in rendered
    for unsupported in ("active use confirmed", "verified ownership", "healthy forwarding", "delivery confirmed"):
        assert unsupported not in rendered
    # Inventory does not create M365/GWS/federation role support.
    assert infer_from_tenant_info(info, priors_override={}).evidence_count == 0


@pytest.mark.asyncio
@pytest.mark.parametrize(("slug", "_name", "suffix"), FAMILIES)
@pytest.mark.parametrize("template", ["mx1.{suffix}.attacker.invalid", "notmx1.{suffix}", "mx3.{suffix}", "{suffix}"])
async def test_mx_lookalikes_do_not_attribute(
    monkeypatch: pytest.MonkeyPatch, slug: str, _name: str, suffix: str, template: str
) -> None:
    _fixture(monkeypatch, {("example.com", "MX"): ["10 " + template.format(suffix=suffix)]})
    ctx = dns_base.DetectionCtx()
    await dns_email.detect_mx(ctx, "example.com")
    assert slug not in ctx.slugs
    assert not any(record.slug == slug for record in ctx.evidence)


@pytest.mark.asyncio
@pytest.mark.parametrize(("slug", "name", "suffix"), FAMILIES)
@pytest.mark.parametrize("accepted", [True, False])
async def test_spf_is_parsed_reachable_policy_reference_with_exact_provenance(
    monkeypatch: pytest.MonkeyPatch, slug: str, name: str, suffix: str, accepted: bool
) -> None:
    target = f"spf.{suffix}"
    value = f"v=spf1 include:{target} -all" if accepted else f"v=spf1 -all include:{target}"
    _fixture(monkeypatch, {("example.com", "TXT"): [value, value]})
    ctx = dns_base.DetectionCtx()
    await dns_email.detect_txt(ctx, "example.com")
    assert (slug in ctx.slugs) is accepted
    matches = tuple(record for record in ctx.evidence if record.slug == slug)
    if accepted:
        record = EvidenceRecord("SPF", value, name, slug)
        assert set(matches) == {record}
        assert (slug, "spf", target) in ctx._matched_fp_detections
        assert compute_slug_posteriors(matches) == compute_slug_posteriors((record,))
    else:
        assert not matches
    replayed = dns_replay.replay_cached_dns_fingerprints(
        SourceResult(source_name="dns_records", raw_dns_records=(("TXT", value),))
    )
    assert (slug in replayed.detected_slugs) is accepted


@pytest.mark.asyncio
@pytest.mark.parametrize(("slug", "_name", "suffix"), FAMILIES)
@pytest.mark.parametrize(
    "template",
    [
        "v=spf1 include:spf.{suffix}.attacker.invalid -all",
        "v=spf1 include:notspf.{suffix} -all",
        "note=include:spf.{suffix}",
    ],
)
async def test_spf_lookalikes_and_non_policy_mentions_do_not_attribute(
    monkeypatch: pytest.MonkeyPatch, slug: str, _name: str, suffix: str, template: str
) -> None:
    value = template.format(suffix=suffix)
    _fixture(monkeypatch, {("example.com", "TXT"): [value]})
    ctx = dns_base.DetectionCtx()
    await dns_email.detect_txt(ctx, "example.com")
    assert slug not in ctx.slugs
    assert not any(record.slug == slug for record in ctx.evidence)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value",
    [
        "forward-email-site-verification=synthetic-token",
        "forward-email-site-verification=",
        "note=forward-email-site-verification=synthetic-token",
        "forward-email=synthetic@example.net",
        "forward-email-site-verification= ",
    ],
)
async def test_forward_email_verification_marker_has_no_routing_or_active_use_claim(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    accepted = value == "forward-email-site-verification=synthetic-token"
    _fixture(monkeypatch, {("example.com", "TXT"): [value, value]})
    ctx = dns_base.DetectionCtx()
    await dns_email.detect_txt(ctx, "example.com")
    assert ("forward-email" in ctx.slugs) is accepted
    if accepted:
        evidence = EvidenceRecord("TXT", value, "Forward Email", "forward-email")
        assert set(ctx.evidence) == {evidence}
        assert compute_slug_posteriors(tuple(ctx.evidence)) == compute_slug_posteriors((evidence,))
        assert ("forward-email", "txt", r"^forward-email-site-verification=\S+$") in ctx._matched_fp_detections
        result = infer_from_tenant_info(_info(ctx), priors_override={})
        assert result.evidence_count == 0
        rendered = format_tenant_plain(_info(ctx)).lower()
        assert "forward email" in rendered
        assert "completed verification" not in rendered
        assert "active use confirmed" not in rendered
    else:
        assert not ctx.evidence


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("detector", "kind", "marker"),
    [(dns_email.detect_mx, "MX", "dns:mx"), (dns_email.detect_txt, "TXT", "dns:apex_txt")],
)
@pytest.mark.parametrize("failed", [False, True])
async def test_sparse_or_failed_collection_never_invents_family_or_absence(
    monkeypatch: pytest.MonkeyPatch,
    detector: Callable[[dns_base.DetectionCtx, str], Awaitable[None]],
    kind: str,
    marker: str,
    failed: bool,
) -> None:
    failures = frozenset({("example.com", kind)}) if failed else frozenset()
    _fixture(monkeypatch, {}, failures)
    ctx = dns_base.DetectionCtx()
    await detector(ctx, "example.com")
    assert not ctx.services
    assert not ctx.slugs
    assert not ctx.evidence
    assert (marker in ctx.degraded_sources) is failed
    info = _info(ctx)
    assert format_tenant_dict(info)["partial"] is failed
    assert format_tenant_dict(info).get("degraded_sources", []) == ([marker] if failed else [])
    assert (
        SourceStatus.from_degraded_sources(info.degraded_sources).channel_unavailable(
            "mx" if kind == "MX" else "apex_txt"
        )
        is failed
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("failed", [False, True])
async def test_convex_missing_or_failed_cname_keeps_the_host_unresolved(
    monkeypatch: pytest.MonkeyPatch, failed: bool
) -> None:
    failures = frozenset({("api.example.com", "CNAME")}) if failed else frozenset()
    _fixture(monkeypatch, {}, failures)
    ctx = dns_base.DetectionCtx()
    ctx.related_domains.add("api.example.com")
    await dns_source._classify_related_surface(ctx, "example.com")
    assert not ctx.surface_attributions
    assert not ctx.slugs
    assert not ctx.evidence
    assert ("dns:cname" in ctx.degraded_sources) is failed


@pytest.mark.asyncio
async def test_complete_dns_source_and_merge_preserve_the_three_families_offline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    queries = _fixture(
        monkeypatch,
        {
            ("example.com", "MX"): ["10 mx1.improvmx.com.", "20 mx2.forwardemail.net."],
            ("example.com", "TXT"): [
                "forward-email-site-verification=synthetic-token",
                "v=spf1 include:spf.improvmx.com include:spf.forwardemail.net -all",
            ],
            ("api.example.com", "CNAME"): ["convex.domains."],
        },
    )
    result = await dns_source.DNSSource().lookup("example.com", skip_ct=True, active_probes=False)
    assert result.error is None
    assert not result.degraded_sources
    assert {"improvmx", "forward-email"} <= set(result.detected_slugs)
    assert "convex" not in result.detected_slugs
    assert any(
        surface.subdomain == "api.example.com" and surface.primary_slug == "convex"
        for surface in result.surface_attributions
    )
    merged = merge_results([result], "example.com")
    serialized = format_tenant_dict(merged)
    assert {"improvmx", "forward-email"} <= set(serialized["slugs"])
    assert "convex" not in serialized["slugs"]
    assert any(
        record["slug"] == "convex" and record["raw_value"].startswith("api.example.com:")
        for record in serialized["evidence"]
    )
    assert not any(host.startswith("_convex_domains.") for host, _ in queries)
    assert len(queries) < 500
