"""Resolver orchestration: query sources in parallel and merge results.

When related names are discovered through bounded CT, CNAME, Exchange/identity
endpoint, autodiscover, or DKIM tenant-domain breadcrumbs, the resolver
automatically runs bounded DNS-only enrichment and merges claim-safe service
indicators into the primary result.
This means `recon gamma.invalid` automatically picks up services configured
on `gamma-internal.invalid` without the user needing to know about the internal domain.

NOTE: Related domain enrichment is intentionally non-recursive. If a related
domain's DNS records point to yet another domain, those second-level related
domains are not followed. This prevents unbounded lookup chains and keeps
resolution time predictable.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import replace
from datetime import UTC, datetime
from typing import Any

import httpx

from recon_tool import collection_progress
from recon_tool.http import collect_refusal_markers
from recon_tool.merger import merge_results
from recon_tool.models import InsightClaim, ReconLookupError, SourceResult, TenantInfo
from recon_tool.sources.base import LookupSource


def _inventory_only_related_result(result: SourceResult) -> SourceResult:
    """Keep related-namespace inventory labels; drop apex-scoped observations.

    Related lookups are appended so a later rematch can keep inventory slugs.
    Their raw DNS, email-control records, identity scalars, and CT payload
    describe the *related* namespace. Merging them as if they were another
    apex source lent that namespace's DMARC, SPF, tokens, and certs to the
    queried domain, and a failed related DNS lookup marked the apex DNS
    channel unavailable.
    """
    from recon_tool.email_security import claim_safe_email_services, claim_safe_email_slugs

    services = {
        name
        for name in claim_safe_email_services(result.detected_services, ())
        if not name.startswith("SPF complexity:")
    }
    slugs = claim_safe_email_slugs(result.detected_slugs, ())
    return replace(
        result,
        tenant_id=None,
        display_name=None,
        default_domain=None,
        region=None,
        m365_detected=False,
        error=None,
        detected_services=tuple(sorted(services)),
        auth_type=None,
        dmarc_policy=None,
        tenant_domains=(),
        detected_slugs=tuple(sorted(slugs)),
        related_domains=(),
        degraded_sources=(),
        cert_summary=None,
        evidence=(),
        bimi_identity=None,
        site_verification_tokens=(),
        mta_sts_mode=None,
        google_auth_type=None,
        google_idp_name=None,
        dmarc_pct=None,
        dmarc_testing=False,
        dmarc_np=None,
        raw_dns_records=(),
        spf_include_count=0,
        ct_provider_used=None,
        ct_subdomain_count=0,
        ct_related_domains=(),
        ct_cache_age_days=None,
        ct_attempt_outcome=None,
        cloud_instance=None,
        tenant_region_sub_scope=None,
        msgraph_host=None,
        surface_attributions=(),
        unclassified_cname_chains=(),
        dns_catalog_summaries=(),
        unclassified_dns_observations=(),
        chain_motifs=(),
        infrastructure_clusters=None,
        source_unavailable=False,
        dns_name_status=None,
    )


def _collect_related_inventory(
    raw_result: SourceResult,
    extra_services: set[str],
    extra_slugs: set[str],
) -> SourceResult | None:
    """Return a related inventory result that adds new apex-safe labels."""
    from recon_tool.collection_view import collection_observable_result

    result = collection_observable_result(raw_result)
    if result.error is not None or result.source_unavailable:
        return None
    inventory = _inventory_only_related_result(result)
    new_services = set(inventory.detected_services) - extra_services
    new_slugs = set(inventory.detected_slugs) - extra_slugs
    if not new_services and not new_slugs:
        return None
    extra_services.update(inventory.detected_services)
    extra_slugs.update(inventory.detected_slugs)
    return inventory


__all__ = [
    "RESOLVE_TIMEOUT",
    "SourcePool",
    "default_pool",
    "resolve_tenant",
]

logger = logging.getLogger("recon")

# Maximum wall-clock time for the entire resolve_tenant pipeline, including
# all source queries and related domain enrichment. Prevents runaway lookups
# from blocking the CLI or MCP server indefinitely.
# Default aggregate wall-clock timeout for a full resolve (all sources +
# related-domain enrichment). Raised from 60s to 120s after
# observing that CT-heavy domains with degraded crt.sh fell back to
# CertSpotter pagination, then ran related-domain enrichment, and
# consistently blew past 60s — producing catastrophic 25–93% batch
# failure rates. 120s gives a realistic ceiling while still catching
# runaway lookups. Override per call via resolve_tenant(timeout=...)
# or CLI --timeout.
RESOLVE_TIMEOUT = 120.0


class SourcePool:
    """Ordered collection of LookupSources. Supports registration and iteration."""

    def __init__(self, sources: list[LookupSource] | None = None) -> None:
        """Initialize with optional list of sources in priority order."""
        self._sources: list[LookupSource] = list(sources) if sources else []

    def register(self, source: LookupSource) -> None:
        """Add a source to the end of the pool."""
        self._sources.append(source)

    def __iter__(self):
        """Iterate over sources in priority order."""
        return iter(self._sources)

    def __len__(self) -> int:
        """Return number of sources."""
        return len(self._sources)


def default_pool() -> SourcePool:
    """Return a SourcePool with the standard sources."""
    from recon_tool.sources.dns import DNSSource
    from recon_tool.sources.google import GoogleSource
    from recon_tool.sources.google_identity import GoogleIdentitySource
    from recon_tool.sources.oidc import OIDCSource
    from recon_tool.sources.userrealm import UserRealmSource

    return SourcePool(
        [
            OIDCSource(),
            UserRealmSource(),
            GoogleSource(),
            GoogleIdentitySource(),
            DNSSource(),
        ]
    )


async def _safe_lookup(
    source: LookupSource,
    domain: str,
    **kwargs: Any,
) -> SourceResult:
    """Run a single source lookup, capturing any unexpected exceptions.

    Reports the source's start and settled result to an optional progress
    listener (``collection_progress``); with no listener this is a no-op.
    """
    collection_progress.emit(source.name, "start")
    with collect_refusal_markers() as markers:
        try:
            result = await source.lookup(domain, **kwargs)
        except Exception as exc:
            result = SourceResult(
                source_name=source.name,
                error=f"Unexpected error: {exc}",
                source_unavailable=True,
            )
    if markers:
        result = replace(result, degraded_sources=tuple(sorted(markers.union(result.degraded_sources))))
    collection_progress.emit(source.name, "done", result=result)
    return result


async def _enrich_from_related(
    info: TenantInfo,
    all_results: list[SourceResult],
    skip_ct: bool = False,
    active_probes: bool = False,
) -> tuple[TenantInfo, list[SourceResult]]:
    """If related domains were found, run lookups on them and merge.

    Two-tier enrichment:
    - Subdomains of the queried domain (from crt.sh): lightweight CNAME+TXT only.
      These are high-volume (dozens of subdomains) and most DNS record types
      (MX, NS, DKIM, SRV, M365 CNAMEs) are meaningless for subdomains.
    - Separate domains (from autodiscover/DKIM breadcrumbs): full DNS lookup.
      These are rare (1-2 typically) and may have their own TXT/MX/NS records.

    Caps at MAX_RELATED_ENRICHMENTS total to prevent runaway lookups.

    ``skip_ct`` is forwarded to the separate-domain DNSSource lookups so
    that operators using ``--no-ct`` for privacy/load reasons do not
    silently issue CT-provider queries for related domains discovered
    via cross-domain CNAME breadcrumbs.
    """
    from recon_tool.sources.dns import DNSSource, lightweight_subdomain_lookup, medium_subdomain_lookup

    # Total concurrent subdomain-enrichment lookups per primary resolve.
    # Each lightweight lookup fires ~2 DNS queries and each medium-tier
    # lookup fires ~6. At batch concurrency (-c 5) the combined fan-out
    # was contributing to 120s aggregate-timeout failures on big
    # enterprises. Dropped from 25 → 15 after validation on a 100-domain
    # corpus. The prioritization (high-signal prefixes first) ensures
    # the most useful subdomains still make the cap.
    MAX_RELATED_ENRICHMENTS = 15
    # Top-signal subdomain prefixes get deeper DNS enrichment
    # (adds MX + DKIM probing). Capped small so we don't blow the DNS
    # budget — only the prefixes most likely to publish their own
    # verification records distinct from the apex.
    _MEDIUM_TIER_PREFIXES: frozenset[str] = frozenset(
        {
            "auth",
            "sso",
            "login",
            "idp",
            "api",
            "mail",
        }
    )
    MAX_MEDIUM_TIER = 6

    # Filter to actionable related domains (skip onmicrosoft — they're just
    # the tenant's internal M365 domain with no SaaS verification records)
    all_candidates = [d for d in info.related_domains if not d.endswith(".onmicrosoft.com")]

    if not all_candidates:
        return info, all_results

    # Split into subdomains vs separate domains
    base_domain = info.queried_domain.lower() if info.queried_domain else ""
    all_subdomains = [d for d in all_candidates if base_domain and d.endswith(f".{base_domain}")]
    separate_domains = [d for d in all_candidates if d not in all_subdomains]

    # Prioritize subdomains by signal value before capping.
    # High-signal prefixes (auth, login, shop, api, em) sort first so they
    # survive the enrichment cap. Low-signal or deep subdomains sort last.
    _HIGH_SIGNAL_PREFIXES = (
        "auth",
        "login",
        "sso",
        "secure",
        "id",
        "identity",
        "shop",
        "store",
        "checkout",
        "pay",
        "api",
        "app",
        "portal",
        "dashboard",
        "admin",
        "support",
        "help",
        "status",
        "click",
        "image",
        "view",
        "email",
        "em",
        "cdn",
        "assets",
        "static",
        "media",
        "blog",
        "docs",
        "stage",
        "staging",
        "dev",
    )

    def _enrich_priority(name: str) -> tuple[int, int, str]:
        prefix = name.split(f".{base_domain}")[0] if base_domain else name
        is_high = 0 if any(prefix == p or prefix.startswith((p + ".", p + "-")) for p in _HIGH_SIGNAL_PREFIXES) else 1
        depth = prefix.count(".")
        return (is_high, depth, name)

    prioritized_subs = sorted(all_subdomains, key=_enrich_priority)

    # Cap total enrichment lookups, but separate domains always get a slot
    sep_cap = min(len(separate_domains), MAX_RELATED_ENRICHMENTS)
    sub_cap = MAX_RELATED_ENRICHMENTS - sep_cap
    capped_subs = prioritized_subs[: max(sub_cap, 0)]
    capped_separate = separate_domains[:sep_cap]

    logger.debug(
        "Enriching from %d related (%d/%d subdomains, %d separate): %s",
        len(capped_subs) + len(capped_separate),
        len(capped_subs),
        len(all_subdomains),
        len(capped_separate),
        ", ".join((capped_subs + capped_separate)[:5]) + ("..." if len(capped_subs) + len(capped_separate) > 5 else ""),
    )

    # Split capped subdomains into medium-tier (MX + DKIM) and
    # lightweight (CNAME + TXT only). Medium tier gets the top-signal
    # prefixes most likely to publish their own verification records.
    def _is_medium_tier(name: str) -> bool:
        prefix = name.split(f".{base_domain}", 1)[0] if base_domain else name
        head = prefix.split(".")[0].split("-")[0]
        return head in _MEDIUM_TIER_PREFIXES

    medium_subs = [s for s in capped_subs if _is_medium_tier(s)][:MAX_MEDIUM_TIER]
    medium_set = set(medium_subs)
    lightweight_subs = [s for s in capped_subs if s not in medium_set]

    # Run all tiers concurrently
    dns_source = DNSSource()
    separate_kwargs: dict[str, Any] = {}
    if skip_ct:
        separate_kwargs["skip_ct"] = True
    if active_probes:
        # Carry the opt-in direct-probe choice to separate-domain DNS lookups so a
        # related apex's BIMI VMC is fetched only when the operator opted in.
        separate_kwargs["active_probes"] = True
    all_tasks = [
        *(medium_subdomain_lookup(d) for d in medium_subs),
        *(lightweight_subdomain_lookup(d) for d in lightweight_subs),
        *(_safe_lookup(dns_source, d, **separate_kwargs) for d in capped_separate),
    ]
    # Related lookups reuse the DNS source on other names. Their progress
    # events must not settle the queried domain's rows, so silence them.
    with collection_progress.suppressed():
        related_results = await asyncio.gather(*all_tasks)

    # Collect additional services and slugs from related domains
    extra_services: set[str] = set(info.services)
    extra_slugs: set[str] = set(info.slugs)
    inventory_results: list[SourceResult] = []
    found_new = False

    for raw_result in related_results:
        # A related-host subchannel failure limits only that enrichment result.
        # Project it locally, but do not mark the apex channel unavailable.
        inventory = _collect_related_inventory(raw_result, extra_services, extra_slugs)
        if inventory is None:
            continue
        found_new = True
        inventory_results.append(inventory)

    if not found_new:
        return info, all_results

    # Scrub control characters from related-domain service strings before they
    # reach insight generation and the enriched TenantInfo. The main merge path
    # scrubs all_services the same way (merger Round 6 / Track D); the enrichment
    # path must not bypass it, or an attacker-controlled related subdomain's DNS
    # data could inject ANSI/OSC sequences into services, insights, and output.
    from recon_tool.validator import strip_control_chars

    extra_services = {strip_control_chars(s) for s in extra_services}

    # Re-run insight generation with the enriched data to get updated signals
    from recon_tool.constants import effective_dmarc_policy, email_security_score
    from recon_tool.email_security import (
        claim_safe_email_services,
        claim_safe_email_slugs,
        observed_email_control_services,
    )
    from recon_tool.merger import build_insights_with_signals

    inventory_services = claim_safe_email_services(extra_services, info.evidence)
    inventory_slugs = claim_safe_email_slugs(extra_slugs, info.evidence)
    apex_claim_services = claim_safe_email_services(set(info.services), info.evidence)
    apex_claim_slugs = claim_safe_email_slugs(set(info.slugs), info.evidence)
    enriched_claims: list[InsightClaim] = []
    enriched_insights = build_insights_with_signals(
        apex_claim_services,
        apex_claim_slugs,
        info.auth_type,
        info.dmarc_policy,
        info.domain_count,
        # Re-pass the metadata the main path supplies; omitting these defaulted
        # has_mx_records to False (spurious "no email infrastructure") and
        # silenced the score / SPF / issuance signals on enriched-then-cached
        # results.
        email_security_score=email_security_score(
            observed_email_control_services(info.evidence),
            info.dmarc_policy,
            info.dmarc_pct,
            info.dmarc_testing,
        ),
        spf_include_count=info.spf_include_count or None,
        issuance_velocity=(info.cert_summary.issuance_velocity if info.cert_summary else None),
        dmarc_pct=info.dmarc_pct,
        has_mx_records=any(e.source_type == "MX" for e in info.evidence),
        google_auth_type=info.google_auth_type,
        google_idp_name=info.google_idp_name,
        primary_email_provider=info.primary_email_provider,
        likely_primary_email_provider=info.likely_primary_email_provider,
        email_gateway=info.email_gateway,
        cloud_instance=info.cloud_instance,
        tenant_region_sub_scope=info.tenant_region_sub_scope,
        msgraph_host=info.msgraph_host,
        dmarc_effective_policy=effective_dmarc_policy(info.dmarc_policy, info.dmarc_pct, info.dmarc_testing),
        evidence=info.evidence,
        degraded_sources=info.degraded_sources,
        insight_claims_out=enriched_claims,
        name_nxdomain=info.dns_name_status == "nxdomain",
    )

    # Build enriched TenantInfo, keeping identity fields and updating
    # services, slugs, and insights.
    #
    # Persist the claim-safe projection rather than the raw union. Enrichment
    # merges a related namespace's detections into this one, and an
    # email-control label asserts that this namespace publishes that record.
    # Storing the union let a neighbouring domain's DMARC, DKIM, SPF, MTA-STS,
    # and BIMI appear as the queried domain's own while its dmarc_policy stayed
    # null and its email-control score stayed zero, so one record contradicted
    # itself. The projection was already computed for the insight arguments;
    # the stored tuples must not bypass it.
    enriched = replace(
        info,
        services=tuple(sorted(inventory_services)),
        slugs=tuple(sorted(inventory_slugs)),
        insights=tuple(enriched_insights),
        insight_claims=tuple(enriched_claims),
    )
    # Related inventory is intentionally stored without lending its evidence to
    # the apex. Reproject the generated-claim fields once against the final
    # inventory and the apex's collection availability. This drops support from
    # unavailable channels and refreshes exact evidence when an added inventory
    # slug was already backed by retained apex evidence. Raw evidence and every
    # non-claim field remain unchanged.
    from recon_tool.collection_view import collection_observable_info

    observable_enriched = collection_observable_info(enriched)
    enriched = replace(
        enriched,
        insights=observable_enriched.insights,
        insight_claims=observable_enriched.insight_claims,
    )

    return enriched, all_results + inventory_results


async def _resolve_tenant_inner(
    domain: str,
    pool: SourcePool,
    client: httpx.AsyncClient | None = None,
    skip_ct: bool = False,
    active_probes: bool = False,
) -> tuple[TenantInfo, list[SourceResult]]:
    """Inner resolution logic — no timeout wrapper."""
    sources = list(pool)

    if len(sources) == 0:
        raise ReconLookupError(
            domain=domain,
            message="No lookup sources configured",
            error_type="not_found",
        )

    kwargs: dict[str, Any] = {}
    if client is not None:
        kwargs["client"] = client
    if skip_ct:
        # Threaded through to DNSSource.lookup; other sources ignore the kwarg.
        kwargs["skip_ct"] = True
    if active_probes:
        # Opt-in direct probes to target-controlled hosts (Google CSE at
        # cse.<domain>, the BIMI VMC fetch). Off by default, DNS still uses the
        # configured recursive resolver and authoritative DNS may observe the
        # resulting traffic. MTA-STS remains the only default target-owned
        # HTTP/application request. The opt-in is threaded to GoogleSource and
        # DNSSource; other sources ignore it.
        kwargs["active_probes"] = True

    # Run all sources concurrently
    results = await asyncio.gather(*(_safe_lookup(source, domain, **kwargs) for source in sources))

    info = merge_results(list(results), domain)

    # Auto-enrich from related domains (e.g. gamma-internal.invalid discovered via
    # autodiscover CNAME when looking up gamma.invalid)
    info, all_results = await _enrich_from_related(info, list(results), skip_ct=skip_ct, active_probes=active_probes)

    return info, all_results


async def resolve_tenant(
    domain: str,
    pool: SourcePool | None = None,
    client: httpx.AsyncClient | None = None,
    timeout: float = RESOLVE_TIMEOUT,
    skip_ct: bool = False,
    active_probes: bool = False,
) -> tuple[TenantInfo, list[SourceResult]]:
    """Orchestrates tenant lookup across the SourcePool.

    All sources are queried concurrently using asyncio.gather.
    Individual source failures do NOT abort — every source gets a chance.
    After all sources complete, results are merged via merge_results.

    If related names are discovered through bounded CT, CNAME,
    Exchange/identity endpoint, autodiscover, or DKIM tenant-domain
    breadcrumbs, the resolver automatically runs bounded DNS-only enrichment
    and merges claim-safe service indicators into the result.

    The entire pipeline is wrapped in an aggregate timeout (default 120s)
    to prevent runaway lookups from blocking indefinitely.

    Args:
        domain: A validated domain string.
        pool: Optional SourcePool (defaults to standard pool with all sources).
        client: Optional httpx client (for testing/injection).
        timeout: Max wall-clock seconds for the entire resolution pipeline.
        skip_ct: When True, skip the cert-transparency providers.
        active_probes: When True, opt in to direct HTTPS probes of
            target-controlled hosts (the Google CSE discovery probe at
            cse.<domain> and the BIMI VMC certificate fetch). Off by default,
            DNS queries still use the configured recursive resolver, so
            authoritative DNS may observe the resulting traffic. The standard
            MTA-STS policy fetch is the only default target-owned
            HTTP/application request.

    Returns:
        Tuple of (TenantInfo, list[SourceResult]) so the CLI can show verbose info.

    Raises:
        ReconLookupError: If all sources fail, no sources are configured, or timeout.
    """
    from recon_tool.collection_limits import admit_namespace
    from recon_tool.network_policy import current_policy

    admit_namespace(domain)
    # A bound but unusable view (disabled, or invalid saved settings) refuses
    # before any collector runs; it never falls back to host DNS.
    if not current_policy().available:
        raise ReconLookupError(
            domain=domain,
            message="The encrypted DNS view is disabled or its RECON_DNS_* settings are invalid; "
            "fix them, or unset RECON_DNS_VIEW to use the system resolver",
            error_type="dns_view_unavailable",
        )
    if pool is None:
        pool = default_pool()

    try:
        info, all_results = await asyncio.wait_for(
            _resolve_tenant_inner(domain, pool, client, skip_ct=skip_ct, active_probes=active_probes),
            timeout=timeout,
        )
    except TimeoutError:
        raise ReconLookupError(
            domain=domain,
            message=f"Resolution timed out after {timeout:.0f}s for {domain}",
            error_type="timeout",
        ) from None

    # Stamp the fresh-resolution timestamp so downstream consumers (CLI,
    # MCP, cache serializer) can distinguish a live-resolved result from
    # a cache hit. cached_at is set only by the cache read path.
    policy = current_policy()
    info = replace(
        info,
        resolved_at=datetime.now(UTC).isoformat(),
        resolution_vantage=policy.mode,
        resolution_policy_id=policy.identity,
    )
    return info, all_results
