# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportPrivateUsage=none
"""Synthetic retained-record tests for narrowly supported catalog claims."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import replace

import pytest

from recon_tool.cache import tenant_info_from_dict, tenant_info_to_dict
from recon_tool.collection_view import collection_observable_evidence, collection_observable_info
from recon_tool.email_security import compute_email_security_score
from recon_tool.fingerprints import (
    DetectionRule,
    clear_ephemeral,
    get_cname_target_rules,
    get_subdomain_txt_patterns,
    load_fingerprints,
    reload_fingerprints,
)
from recon_tool.formatter.classify import provider_line
from recon_tool.merger import merge_results
from recon_tool.models import EvidenceRecord, SignalContext, SourceResult, TenantInfo, UnclassifiedCnameChain
from recon_tool.posture import analyze_posture, load_posture_rules, reload_posture
from recon_tool.signals import evaluate_signals, load_signals, reload_signals
from recon_tool.sources import dns as dns_source
from recon_tool.sources import dns_base, dns_email, dns_infra
from recon_tool.sources.dns_tables import classify_chain

_DOCUMENTED_TARGETS = (
    ("Retool", "retool", "custom-domain.retool.com", r"^custom-domain\.retool\.com\.?$"),
    ("Postmark", "postmark", "pm.mtasv.net", r"^pm\.mtasv\.net\.?$"),
)


@pytest.fixture(autouse=True)
def _clean_catalog_state() -> Iterator[None]:
    clear_ephemeral()
    reload_fingerprints()
    reload_signals()
    reload_posture()
    yield
    clear_ephemeral()
    reload_fingerprints()
    reload_signals()
    reload_posture()


def _dns_fixture(monkeypatch: pytest.MonkeyPatch, records: dict[tuple[str, str], list[str]]) -> list[tuple[str, str]]:
    queries: list[tuple[str, str]] = []

    async def resolve(name: str, record_type: str, **_kwargs: object) -> list[str]:
        key = (name.lower().rstrip("."), record_type)
        queries.append(key)
        return records.get(key, [])

    monkeypatch.setattr(dns_base, "safe_resolve", resolve)
    return queries


def _rules(slug: str, kind: str) -> dict[str, DetectionRule]:
    return {
        rule.pattern: rule
        for fingerprint in load_fingerprints()
        if fingerprint.slug == slug
        for rule in fingerprint.detections
        if rule.type == kind
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value",
    [
        "v=aid2;u=https://agent.example.com/mcp;p=mcp",
        "p=a2a; version = aid2 ; uri=https://agent.example.com/a2a",
        " VERSION = aid2 ; p=local; u=docker:synthetic/agent:1",
        "v=aid1;uri=https://agent.example.com/mcp;proto=mcp",
        "v=aid2",  # A declaration alone does not prove a valid AID record.
    ],
)
async def test_aid_declaration_preserves_dns_provenance_without_vendor_attribution(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    queries = _dns_fixture(monkeypatch, {("_agent.example.com", "TXT"): [value, value]})
    ctx = dns_base.DetectionCtx()
    await dns_infra.detect_subdomain_txt(ctx, "example.com")
    name, slug = "Agent Identity & Discovery (AID)", "crewai-aid"
    assert ctx.services == {name}
    assert ctx.slugs == {slug}
    assert ctx.evidence == [EvidenceRecord("SUBDOMAIN_TXT", value, name, slug)]
    ((pattern, rule),) = _rules(slug, "subdomain_txt").items()
    assert (slug, "subdomain_txt", pattern) in ctx._matched_fp_detections
    assert rule.verified == "2026-09-30"
    assert "agentcommunity/agent-identity-discovery" in rule.reference
    assert "does not identify CrewAI" in rule.description
    assert all(kind == "TXT" and host.endswith(".example.com") for host, kind in queries)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("owner", "value"),
    [
        ("_agent", "v=aid20;u=https://agent.example.com/mcp;p=mcp"),
        ("_agent", "v=aid2preview;u=https://agent.example.com/mcp;p=mcp"),
        ("_agent", "desc=v=aid2;u=https://agent.example.com/mcp;p=mcp"),
        ("_agent", "notversion=aid2;u=https://agent.example.com/mcp;p=mcp"),
        ("_agent", "version=notaid2;u=https://agent.example.com/mcp;p=mcp"),
        ("_agent", "uri=https://agent.example.com/mcp;p=mcp"),
        ("_agent", ""),
        ("_agent.lookalike", "v=aid2;u=https://agent.example.com/mcp;p=mcp"),
        ("_mcp", "v=aid2;u=https://agent.example.com/mcp;p=mcp"),
    ],
)
async def test_aid_lookalikes_and_empty_records_do_not_match(
    monkeypatch: pytest.MonkeyPatch, owner: str, value: str
) -> None:
    _dns_fixture(monkeypatch, {(f"{owner}.example.com", "TXT"): [value]})
    ctx = dns_base.DetectionCtx()
    await dns_infra.detect_subdomain_txt(ctx, "example.com")
    assert "crewai-aid" not in ctx.slugs
    assert not any(record.slug == "crewai-aid" for record in ctx.evidence)


def test_discovery_declarations_cannot_establish_ai_platform_or_agent_deployment() -> None:
    slugs = ("crewai-aid", "mcp-discovery")
    info = TenantInfo(
        tenant_id=None,
        display_name="",
        default_domain="example.com",
        queried_domain="example.com",
        slugs=slugs,
        evidence=tuple(EvidenceRecord("SUBDOMAIN_TXT", "synthetic-declaration", slug, slug) for slug in slugs),
    )
    assert not {"ai_tooling_detected", "agentic_ai_detected"}.intersection(
        observation.source_name for observation in analyze_posture(info)
    )
    ctx = SignalContext(detected_slugs=frozenset(slugs))
    assert not {"AI Adoption", "Agentic AI Infrastructure"}.intersection(
        signal.name for signal in evaluate_signals(ctx)
    )
    failed = replace(info, degraded_sources=("dns:subdomain_txt",))
    assert not collection_observable_evidence(failed)
    assert not collection_observable_info(failed).slugs
    assert failed.evidence == info.evidence


@pytest.mark.parametrize(
    ("hostname", "pattern"),
    [
        ("synthetic.vercel-dns-017.com", "vercel-dns-017.com"),
        ("SYNTHETIC.VERCEL-DNS-017.COM.", "vercel-dns-017.com"),
        ("cname.vercel-dns-0.com", r"^cname\.vercel-dns-0\.com\.?$"),
        ("CNAME.VERCEL-DNS-0.COM.", r"^cname\.vercel-dns-0\.com\.?$"),
        ("cname.vercel-dns.com", "cname.vercel-dns.com"),
        ("synthetic.vercel.app", "vercel.app"),
    ],
)
def test_vercel_supported_targets_select_the_specific_rule(hostname: str, pattern: str) -> None:
    rules = tuple(sorted(get_cname_target_rules(), key=lambda rule: -len(rule.pattern)))
    application, infrastructure = classify_chain([hostname], rules)
    assert application is not None
    assert application.slug == "vercel"
    assert application.pattern == pattern
    assert infrastructure is None
    assert "vercel-dns-" not in _rules("vercel", "cname_target")


@pytest.mark.parametrize(
    "hostname",
    [
        "vercel-dns-attacker.invalid",
        "synthetic.vercel-dns-999.com",
        "synthetic.vercel-dns-017.com.lookalike.invalid",
        "synthetic.notvercel-dns-017.com",
        "synthetic.vercel-dns-017.com.evil.com",
        "cname.vercel-dns-0.com.lookalike.invalid",
        "prefix.cname.vercel-dns-0.com",
        "notcname.vercel-dns-0.com",
        "cnameXvercel-dns-0Xcom",
    ],
)
def test_vercel_fragments_and_unconfirmed_numbered_families_do_not_match(hostname: str) -> None:
    application, infrastructure = classify_chain([hostname], get_cname_target_rules())
    assert application is None or application.slug != "vercel"
    assert infrastructure is None or infrastructure.slug != "vercel"


@pytest.mark.asyncio
@pytest.mark.parametrize("target", ["synthetic.vercel-dns-017.com", "cname.vercel-dns-0.com"])
async def test_vercel_application_and_edge_keep_the_observed_chain_separate_from_apex(
    monkeypatch: pytest.MonkeyPatch, target: str
) -> None:
    edge = "synthetic.cloudfront.net"
    queries = _dns_fixture(
        monkeypatch,
        {("app.example.com", "CNAME"): [target.upper() + "."], (target, "CNAME"): [edge]},
    )
    ctx = dns_base.DetectionCtx()
    ctx.related_domains.add("app.example.com")
    await dns_source._classify_related_surface(ctx, "example.com")

    (surface,) = ctx.surface_attributions
    assert surface.subdomain == "app.example.com"
    assert surface.primary_slug == "vercel"
    assert surface.primary_tier == "application"
    assert surface.infra_slug == "aws-cloudfront"
    assert not ctx.slugs
    assert not ctx.services
    assert ctx.evidence == [EvidenceRecord("CNAME", f"app.example.com: {target} -> {edge}", "Vercel", "vercel")]
    assert not ctx.unclassified_cname_chains
    assert all(record_type == "CNAME" for _, record_type in queries)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "target", ["synthetic.awsapps.com", "SYNTHETIC.AWSAPPS.COM.", "synthetic.awsapps.com.lookalike.invalid"]
)
async def test_generic_awsapps_routing_does_not_establish_ses(monkeypatch: pytest.MonkeyPatch, target: str) -> None:
    application, infrastructure = classify_chain([target], get_cname_target_rules())
    assert application is None or application.slug != "aws-ses"
    assert infrastructure is None or infrastructure.slug != "aws-ses"
    _dns_fixture(monkeypatch, {("example.com", "MX"): [f"10 {target}"]})
    ctx = dns_base.DetectionCtx()
    await dns_email.detect_mx(ctx, "example.com")
    assert "aws-ses" not in ctx.slugs
    assert not any(evidence.slug == "aws-ses" for evidence in ctx.evidence)
    assert "awsapps.com" not in _rules("aws-ses", "cname_target")


@pytest.mark.asyncio
@pytest.mark.parametrize("target", ["inbound-smtp.us-east-1.amazonaws.com", "INBOUND-SMTP.EU-WEST-1.AMAZONAWS.COM."])
async def test_specific_ses_receiving_mx_retains_exact_observed_record(
    monkeypatch: pytest.MonkeyPatch, target: str
) -> None:
    value = f"10 {target}"
    _dns_fixture(monkeypatch, {("example.com", "MX"): [value]})
    ctx = dns_base.DetectionCtx()
    await dns_email.detect_mx(ctx, "example.com")
    assert "aws-ses" in ctx.slugs
    assert any(evidence.source_type == "MX" and evidence.raw_value == value for evidence in ctx.evidence)
    assert not ctx.m365


@pytest.mark.asyncio
@pytest.mark.parametrize("value", ["_oktaverification=synthetic", "_OKTAVERIFICATION=synthetic", "unrelated TXT"])
async def test_okta_owner_name_is_not_an_apex_value_fingerprint(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    _dns_fixture(monkeypatch, {("example.com", "TXT"): [value]})
    ctx = dns_base.DetectionCtx()
    await dns_email.detect_txt(ctx, "example.com")
    assert "okta" not in ctx.slugs
    assert not any(evidence.slug == "okta" for evidence in ctx.evidence)
    assert "^_oktaverification=" not in _rules("okta", "txt")


@pytest.mark.parametrize("target", ["synthetic.customdomains.okta.com", "SYNTHETIC.CUSTOMDOMAINS.OKTA.COM."])
def test_okta_supported_custom_domain_routing_remains(target: str) -> None:
    application, _infrastructure = classify_chain([target], get_cname_target_rules())
    assert application is not None
    assert application.slug == "okta"
    assert application.pattern == "customdomains.okta.com"
    lookalike = target.rstrip(".") + ".lookalike.invalid"
    application, infrastructure = classify_chain([lookalike], get_cname_target_rules())
    assert application is None
    assert infrastructure is None


@pytest.mark.asyncio
async def test_okta_separate_legacy_txt_rule_is_retained_without_a_verification_date(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value = "okta-domain-verification=synthetic"
    _dns_fixture(monkeypatch, {("example.com", "TXT"): [value]})
    ctx = dns_base.DetectionCtx()
    await dns_email.detect_txt(ctx, "example.com")
    assert "okta" in ctx.slugs
    assert EvidenceRecord("TXT", value, "Okta", "okta") in ctx.evidence
    assert _rules("okta", "txt")["^okta-domain-verification"].verified == ""


@pytest.mark.asyncio
@pytest.mark.parametrize("owner", ["_github-challenge", "_github-challenge-synthetic", "_github-challenge.lookalike"])
async def test_generic_github_challenge_does_not_claim_advanced_security_or_add_probes(
    monkeypatch: pytest.MonkeyPatch, owner: str
) -> None:
    queries = _dns_fixture(monkeypatch, {(f"{owner}.example.com", "TXT"): ["synthetic-verification-token"]})
    ctx = dns_base.DetectionCtx()
    await dns_infra.detect_subdomain_txt(ctx, "example.com")
    assert "github-advanced-security" not in ctx.slugs
    assert not any(evidence.slug == "github-advanced-security" for evidence in ctx.evidence)
    assert not any(name.startswith("_github-challenge") for name, _record_type in queries)
    assert not any(rule.slug == "github-advanced-security" for rule in get_subdomain_txt_patterns())


@pytest.mark.asyncio
@pytest.mark.parametrize("owner", ["_slack-challenge", "_slack-challenge.lookalike", "@"])
async def test_slack_challenge_is_an_owner_qualified_administrative_indicator(
    monkeypatch: pytest.MonkeyPatch, owner: str
) -> None:
    value = "synthetic-slack-verification-token"
    name = "example.com" if owner == "@" else f"{owner}.example.com"
    _dns_fixture(monkeypatch, {(name, "TXT"): [value]})
    ctx = dns_base.DetectionCtx()
    await dns_email.detect_txt(ctx, "example.com")
    await dns_infra.detect_subdomain_txt(ctx, "example.com")
    assert ("slack" in ctx.slugs) is (owner == "_slack-challenge")
    if owner == "_slack-challenge":
        assert ctx.services == {"Slack"}
        assert ctx.evidence == [EvidenceRecord("SUBDOMAIN_TXT", value, "Slack", "slack")]
    rule = _rules("slack", "subdomain_txt")["_slack-challenge:."]
    assert "Pro, Business+, and Enterprise" in rule.description
    assert "does not establish" in rule.description
    assert "active use" in rule.description


_CHALLENGE_OWNERS = (
    (
        "Tailscale",
        "tailscale",
        "_tailscale-challenge",
        "2026-09-08",
        "https://tailscale.com/docs/account/domain-verification",
    ),
    (
        "PostHog",
        "posthog",
        "_posthog-challenge",
        "2026-09-08",
        "https://posthog.com/docs/settings/sso",
    ),
    (
        "Shopify",
        "shopify",
        "shopify_verification",
        "2026-09-13",
        "https://help.shopify.com/en/manual/domains/add-a-domain/connecting-domains/verify-domain-ownership",
    ),
)


def test_shopify_rules_do_not_claim_account_or_live_service_state() -> None:
    token = _rules("shopify", "txt")["^shopify-verification-code="]
    assert token.verified == ""
    assert "does not establish account binding, SSO, completed verification, or active use" in token.description
    route = _rules("shopify", "cname")["myshopify.com"]
    assert route.verified == "2026-11-17"
    assert (
        route.reference
        == "https://help.shopify.com/en/manual/domains/add-a-domain/connecting-domains/connect-domain-manual"
    )
    assert "does not establish" in route.description
    assert "a currently published storefront" in route.description
    related = _rules("shopify", "cname_target")["myshopify.com"]
    assert related.verified == ""
    assert "does not establish" in related.description
    assert "a currently published storefront" in related.description
    assets = _rules("shopify", "cname_target")["shopifycdn.com"]
    assert assets.verified == ""
    assert "does not establish current asset delivery" in assets.description


@pytest.mark.asyncio
@pytest.mark.parametrize("owner_case", _CHALLENGE_OWNERS)
@pytest.mark.parametrize("shape", ["exact", "lookalike", "apex", "prefix", "subdomain", "empty"])
async def test_documented_challenge_owners_are_owner_qualified(
    monkeypatch: pytest.MonkeyPatch,
    owner_case: tuple[str, str, str, str, str],
    shape: str,
) -> None:
    name, slug, owner, verified, reference = owner_case
    value = "" if shape == "empty" else f"synthetic-{slug}-verification-token"
    queried = {
        "exact": f"{owner}.example.com",
        "lookalike": f"{owner}.lookalike.example.com",
        "apex": "example.com",
        "prefix": f"not{owner}.example.com",
        "subdomain": f"{owner}_shop.example.com",
        "empty": f"{owner}.example.com",
    }[shape]
    _dns_fixture(monkeypatch, {(queried, "TXT"): [value]})
    ctx = dns_base.DetectionCtx()
    await dns_email.detect_txt(ctx, "example.com")
    await dns_infra.detect_subdomain_txt(ctx, "example.com")
    assert (slug in ctx.slugs) is (shape == "exact")
    if shape == "exact":
        assert ctx.services == {name}
        assert ctx.evidence == [EvidenceRecord("SUBDOMAIN_TXT", value, name, slug)]
        assert (slug, "subdomain_txt", f"{owner}:.") in ctx._matched_fp_detections
    rule = _rules(slug, "subdomain_txt")[f"{owner}:."]
    assert rule.verified == verified
    assert rule.reference == reference
    assert "does not establish" in rule.description


@pytest.mark.asyncio
async def test_documented_challenge_owners_abstain_on_wildcard_txt(monkeypatch: pytest.MonkeyPatch) -> None:
    _dns_fixture(
        monkeypatch,
        {(f"{owner}.example.com", "TXT"): ["synthetic-wildcard"] for _, _, owner, _, _ in _CHALLENGE_OWNERS},
    )
    ctx = dns_base.DetectionCtx()
    await dns_infra.detect_subdomain_txt(ctx, "example.com")
    assert not ctx.slugs.intersection(slug for _, slug, _, _, _ in _CHALLENGE_OWNERS)


@pytest.mark.parametrize("owner_case", _CHALLENGE_OWNERS)
def test_unavailable_challenge_collection_cannot_corroborate_retained_tokens(
    owner_case: tuple[str, str, str, str, str],
) -> None:
    name, slug, _, _, _ = owner_case
    info = TenantInfo(
        tenant_id=None,
        display_name="",
        default_domain="example.com",
        queried_domain="example.com",
        slugs=(slug,),
        services=(name,),
        evidence=(EvidenceRecord("SUBDOMAIN_TXT", "synthetic-token", name, slug),),
    )
    assert collection_observable_evidence(info) == info.evidence
    failed = replace(info, degraded_sources=("dns:subdomain_txt",))
    assert collection_observable_evidence(failed) == ()
    assert slug not in collection_observable_info(failed).slugs
    assert failed.evidence == info.evidence


@pytest.mark.parametrize(
    "hostname",
    [
        "proxy-us.posthog.com",
        "synthetic.proxy-us.posthog.com.lookalike.invalid",
        "notproxy-us.posthog.com",
        "synthetic.proxy-eu.posthog.com",
        "proxy-us.posthog.com.evil.com",
    ],
)
def test_posthog_proxy_does_not_match_undocumented_or_lookalike_zones(hostname: str) -> None:
    application, infrastructure = classify_chain([hostname], get_cname_target_rules())
    assert application is None or application.slug != "posthog"
    assert infrastructure is None or infrastructure.slug != "posthog"


def test_posthog_proxy_matches_the_documented_us_zone() -> None:
    application, infrastructure = classify_chain(
        ["4854cf84789d8596ad01.proxy-us.posthog.com"], get_cname_target_rules()
    )
    assert application is not None
    assert application.slug == "posthog"
    assert application.pattern == r"\.proxy-us\.posthog\.com\.?$"
    assert infrastructure is None
    rule = _rules("posthog", "cname_target")[application.pattern]
    assert rule.verified == "2026-09-08"
    assert "does not establish" in rule.description


@pytest.mark.parametrize(
    "hostname",
    [
        "links1.resend-dns.com",
        "LINKS1.RESEND-DNS.COM.",
    ],
)
def test_resend_tracking_matches_the_documented_host(hostname: str) -> None:
    application, infrastructure = classify_chain([hostname], get_cname_target_rules())
    assert application is not None
    assert application.slug == "resend"
    assert application.pattern == r"^links1\.resend-dns\.com\.?$"
    assert infrastructure is None
    rule = _rules("resend", "cname_target")[application.pattern]
    assert rule.verified == "2026-09-08"
    assert "does not establish" in rule.description


@pytest.mark.parametrize(
    "hostname",
    [
        "links2.resend-dns.com",
        "synthetic.links1.resend-dns.com",
        "links1.resend-dns.com.lookalike.invalid",
        "notlinks1.resend-dns.com",
        "links1.resend-dns.com.evil.com",
        "resend-dns.com",
    ],
)
def test_resend_tracking_does_not_match_undocumented_hosts(hostname: str) -> None:
    application, infrastructure = classify_chain([hostname], get_cname_target_rules())
    assert application is None or application.slug != "resend"
    assert infrastructure is None or infrastructure.slug != "resend"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "case",
    [
        (
            "PostHog",
            "posthog",
            "e.example.com",
            "4854cf84789d8596ad01.proxy-us.posthog.com",
            r"\.proxy-us\.posthog\.com\.?$",
        ),
        ("Resend", "resend", "links.example.com", "links1.resend-dns.com", r"^links1\.resend-dns\.com\.?$"),
    ],
)
async def test_documented_2026_09_08_targets_keep_related_host_evidence(
    monkeypatch: pytest.MonkeyPatch,
    case: tuple[str, str, str, str, str],
) -> None:
    name, slug, host, target, pattern = case
    _dns_fixture(monkeypatch, {(host, "CNAME"): [target.upper() + "."]})
    ctx = dns_base.DetectionCtx()
    ctx.related_domains.add(host)
    await dns_source._classify_related_surface(ctx, "example.com")
    (surface,) = ctx.surface_attributions
    assert (surface.subdomain, surface.primary_slug, surface.primary_name) == (host, slug, name)
    assert surface.primary_tier == "application"
    assert ctx.evidence == [EvidenceRecord("CNAME", f"{host}: {target}", name, slug)]
    assert not ctx.slugs
    assert not ctx.services
    rule = _rules(slug, "cname_target")[pattern]
    assert rule.verified == "2026-09-08"


@pytest.mark.parametrize("target", ["synthetic.glitch.me", "SYNTHETIC.GLITCH.ME."])
def test_glitch_is_legacy_routing_not_application_hosting(target: str) -> None:
    application, infrastructure = classify_chain([target], get_cname_target_rules())
    assert application is None
    assert infrastructure is not None
    assert infrastructure.slug == "glitch"
    rule = _rules("glitch", "cname_target")["glitch.me"]
    assert "Legacy" in rule.description
    assert "redirect or stale configuration" in rule.description
    assert "does not establish a running Glitch application" in rule.description
    application, infrastructure = classify_chain([target.rstrip(".") + ".lookalike.invalid"], get_cname_target_rules())
    assert application is None
    assert infrastructure is None


def test_retired_security_slug_cannot_drive_signals_or_posture_even_from_old_retained_data() -> None:
    retired = "github-advanced-security"
    assert not any(retired in signal.candidates for signal in load_signals())
    assert not any(retired in rule.slugs_any for rule in load_posture_rules())
    info = TenantInfo(
        tenant_id=None,
        display_name="Synthetic Alpha",
        default_domain="alpha.invalid",
        queried_domain="alpha.invalid",
        slugs=(retired,),
        evidence=(EvidenceRecord("SUBDOMAIN_TXT", "synthetic", "GitHub Advanced Security", retired),),
    )
    assert not any("supply-chain" in observation.statement.lower() for observation in analyze_posture(info))
    for slugs, expected in [({retired, "snyk"}, False), ({"sonatype", "snyk"}, True)]:
        matches = evaluate_signals(SignalContext(detected_slugs=frozenset(slugs)))
        assert any(match.name == "Software Supply Chain Maturity" for match in matches) is expected
    current = replace(info, slugs=("snyk",), evidence=(EvidenceRecord("TXT", "snyk=synthetic", "Snyk", "snyk"),))
    assert any("supply-chain" in observation.statement.lower() for observation in analyze_posture(current))


@pytest.mark.asyncio
async def test_sparse_empty_records_do_not_synthesize_researched_vendor_claims(monkeypatch: pytest.MonkeyPatch) -> None:
    _dns_fixture(monkeypatch, {})
    ctx = dns_base.DetectionCtx()
    await dns_email.detect_txt(ctx, "example.com")
    await dns_email.detect_mx(ctx, "example.com")
    await dns_infra.detect_subdomain_txt(ctx, "example.com")
    assert not ctx.slugs.intersection(
        {"okta", "slack", "github-advanced-security", "aws-ses", "tailscale", "posthog", "resend", "shopify"}
    )
    assert classify_chain([], get_cname_target_rules()) == (None, None)


@pytest.mark.parametrize(("name", "slug", "target", "pattern"), _DOCUMENTED_TARGETS)
@pytest.mark.parametrize("uppercase", [False, True])
def test_documented_fixed_targets_match_only_the_exact_rule(
    name: str, slug: str, target: str, pattern: str, uppercase: bool
) -> None:
    hostname = target.upper() + "." if uppercase else target
    application, infrastructure = classify_chain([hostname], get_cname_target_rules())
    assert application is not None
    assert (application.name, application.slug, application.pattern) == (name, slug, pattern)
    assert infrastructure is None
    rule = _rules(slug, "cname_target")[pattern]
    assert rule.verified == "2026-09-05"
    assert rule.reference.startswith("https://")
    assert "does not establish" in rule.description


@pytest.mark.parametrize(("name", "slug", "target", "pattern"), _DOCUMENTED_TARGETS)
@pytest.mark.parametrize("shape", ["suffix", "child", "prefix", "parent", "regex-lookalike"])
def test_documented_fixed_targets_do_not_expand_into_neighboring_names(
    name: str, slug: str, target: str, pattern: str, shape: str
) -> None:
    hostname = {
        "suffix": target + ".lookalike.invalid",
        "child": "synthetic." + target,
        "prefix": "not" + target,
        "parent": target.split(".", 1)[1],
        "regex-lookalike": target.replace(".", "x"),
    }[shape]
    application, infrastructure = classify_chain([hostname], get_cname_target_rules())
    assert application is None or application.slug != slug, (name, pattern, hostname)
    assert infrastructure is None or infrastructure.slug != slug


@pytest.mark.parametrize("pattern", ["postmarkapp.com", "pstmrk.com"])
def test_unsupported_postmark_suffixes_are_not_customer_cname_rules(pattern: str) -> None:
    assert pattern not in _rules("postmark", "cname_target")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "target", ["postmarkapp.com", "synthetic.postmarkapp.com", "postmarkapp.com.lookalike.invalid"]
)
async def test_postmark_spf_owner_is_not_the_documented_include_target(
    monkeypatch: pytest.MonkeyPatch, target: str
) -> None:
    raw = f"v=spf1 include:{target} include:_spf.google.com -all"
    _dns_fixture(monkeypatch, {("example.com", "TXT"): [raw]})
    ctx = dns_base.DetectionCtx()
    await dns_email.detect_txt(ctx, "example.com")
    assert "postmark" not in ctx.slugs
    assert not any(evidence.slug == "postmark" for evidence in ctx.evidence)
    assert "google-workspace" in ctx.slugs
    assert any(evidence.source_type == "SPF" and evidence.raw_value == raw for evidence in ctx.evidence)
    assert "postmarkapp.com" not in _rules("postmark", "spf")


@pytest.mark.asyncio
@pytest.mark.parametrize("term", ["include:spf.mtasv.net", "INCLUDE:SPF.MTASV.NET.", "-include:spf.mtasv.net"])
async def test_existing_postmark_policy_reference_remains_without_authorization_claim(
    monkeypatch: pytest.MonkeyPatch, term: str
) -> None:
    raw = f"v=spf1 {term} -all"
    _dns_fixture(monkeypatch, {("example.com", "TXT"): [raw]})
    ctx = dns_base.DetectionCtx()
    await dns_email.detect_txt(ctx, "example.com")
    assert "postmark" in ctx.slugs
    assert any(evidence.slug == "postmark" and evidence.raw_value == raw for evidence in ctx.evidence)
    rule = _rules("postmark", "spf")["mtasv.net"]
    assert not rule.verified
    assert "does not establish positive authorization" in rule.description


@pytest.mark.asyncio
@pytest.mark.parametrize("target", ["synthetic.postmarkapp.com", "synthetic.pstmrk.com"])
@pytest.mark.parametrize("with_edge", [False, True])
async def test_retired_postmark_routes_preserve_observation_without_application_claim(
    monkeypatch: pytest.MonkeyPatch, target: str, with_edge: bool
) -> None:
    host = "app.example.com"
    edge = "synthetic.cloudfront.net"
    records = {(host, "CNAME"): [target.upper() + "."]}
    if with_edge:
        records[(target, "CNAME")] = [edge]
    _dns_fixture(monkeypatch, records)
    ctx = dns_base.DetectionCtx()
    ctx.related_domains.add(host)
    await dns_source._classify_related_surface(ctx, "example.com")
    assert not any(surface.primary_slug == "postmark" for surface in ctx.surface_attributions)
    assert not any(evidence.slug == "postmark" for evidence in ctx.evidence)
    if with_edge:
        (surface,) = ctx.surface_attributions
        assert surface.primary_slug == "aws-cloudfront"
        assert ctx.evidence[0].raw_value == f"{host}: {target} -> {edge}"
        assert not ctx.unclassified_cname_chains
    else:
        assert not ctx.surface_attributions
        assert ctx.unclassified_cname_chains == [UnclassifiedCnameChain(subdomain=host, chain=(target,))]
    info = TenantInfo(
        tenant_id=None,
        display_name="Synthetic Alpha",
        default_domain="example.com",
        queried_domain="example.com",
        surface_attributions=tuple(ctx.surface_attributions),
        evidence=tuple(ctx.evidence),
        unclassified_cname_chains=tuple(ctx.unclassified_cname_chains),
    )
    restored = tenant_info_from_dict(tenant_info_to_dict(info))
    assert restored.surface_attributions == info.surface_attributions
    assert restored.evidence == info.evidence
    assert restored.unclassified_cname_chains == info.unclassified_cname_chains
    assert compute_email_security_score(restored) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("candidate", _DOCUMENTED_TARGETS)
@pytest.mark.parametrize("with_edge", [False, True])
async def test_documented_targets_keep_owner_evidence_and_do_not_promote_apex_claims(
    monkeypatch: pytest.MonkeyPatch, candidate: tuple[str, str, str, str], with_edge: bool
) -> None:
    name, slug, target, pattern = candidate
    host = "app.example.com" if slug == "retool" else "pm-bounces.example.com"
    edge = "synthetic.cloudfront.net"
    records = {(host, "CNAME"): [target.upper() + "."]}
    if with_edge:
        records[(target, "CNAME")] = [edge]
    queries = _dns_fixture(monkeypatch, records)
    ctx = dns_base.DetectionCtx()
    ctx.related_domains.add(host)
    await dns_source._classify_related_surface(ctx, "example.com")

    (surface,) = ctx.surface_attributions
    assert (surface.subdomain, surface.primary_slug, surface.primary_name) == (host, slug, name)
    assert surface.primary_tier == "application"
    assert surface.infra_slug == ("aws-cloudfront" if with_edge else None)
    chain = f"{target} -> {edge}" if with_edge else target
    assert ctx.evidence == [EvidenceRecord("CNAME", f"{host}: {chain}", name, slug)]
    assert not ctx.slugs
    assert not ctx.services
    assert not ctx.m365
    assert not ctx.unclassified_cname_chains
    (summary,) = ctx.catalog_summaries()
    assert (summary.record_type, summary.opportunity_count, summary.observed_count, summary.classified_count) == (
        "cname_target",
        1,
        1,
        1,
    )
    assert not summary.truncated
    assert _rules(slug, "cname_target")[pattern].tier == "application"
    assert all(kind == "CNAME" for _, kind in queries)
    assert all(
        queried in {host, target, edge} or queried.startswith("nonsense-classifier-guard-")
        for queried, _kind in queries
    )
    baseline = merge_results([SourceResult(source_name="dns")], "example.com")
    merged = merge_results(
        [
            SourceResult(
                source_name="dns",
                evidence=tuple(ctx.evidence),
                surface_attributions=tuple(ctx.surface_attributions),
                detected_services=tuple(ctx.services),
                detected_slugs=tuple(ctx.slugs),
                m365_detected=ctx.m365,
            )
        ],
        "example.com",
    )
    assert provider_line(merged) == provider_line(baseline)
    assert merged.primary_email_provider is None
    assert merged.likely_primary_email_provider is None
    assert merged.email_gateway is None
    assert compute_email_security_score(merged) == compute_email_security_score(baseline) == 0
    assert not merged.services
    assert not merged.slugs
    assert merged.surface_attributions == (surface,)
    info = TenantInfo(
        tenant_id=None,
        display_name="Synthetic Alpha",
        default_domain="example.com",
        queried_domain="example.com",
        surface_attributions=tuple(ctx.surface_attributions),
        evidence=tuple(ctx.evidence),
        degraded_sources=("dns:cname",),
    )
    observable = collection_observable_info(info)
    assert not observable.surface_attributions
    assert observable.evidence == info.evidence
    assert not collection_observable_evidence(observable)
    assert not observable.services
    assert not observable.slugs


@pytest.mark.asyncio
@pytest.mark.parametrize("candidate", _DOCUMENTED_TARGETS)
@pytest.mark.parametrize("wildcard", [False, True])
async def test_empty_or_wildcard_target_observations_cannot_create_a_service(
    monkeypatch: pytest.MonkeyPatch, candidate: tuple[str, str, str, str], wildcard: bool
) -> None:
    name, slug, target, pattern = candidate

    async def resolve(_host: str, **_kwargs: object) -> list[str]:
        return [target] if wildcard else []

    monkeypatch.setattr(dns_source, "_resolve_cname_chain", resolve)
    ctx = dns_base.DetectionCtx()
    ctx.related_domains.add("app.alpha.invalid")
    await dns_source._classify_related_surface(ctx, "alpha.invalid")
    assert not ctx.surface_attributions, (name, slug, pattern)
    assert not ctx.evidence
    assert not ctx.slugs
    assert not ctx.services
    assert not ctx.unclassified_cname_chains
