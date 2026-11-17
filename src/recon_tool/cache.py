# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportUnknownArgumentType=none, reportUnknownMemberType=none, reportUnknownVariableType=none
"""Lightweight JSON disk cache for serialized ``TenantInfo`` values.

Entries expire lazily and cache I/O degrades to misses instead of escaping errors.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from recon_tool.cache_catalog import (
    catalog_discovery_to_cache_dict,
    dns_catalog_summaries_from_dict,
    unclassified_chains_from_dict,
    unclassified_dns_observations_from_dict,
)
from recon_tool.cache_contract import DEFAULT_TTL, MAX_RESULT_CACHE_FILE_BYTES, RESULT_CACHE_VERSION
from recon_tool.cache_insights import (
    insight_claims_from_cache,
    insight_claims_to_cache,
    validate_insight_claim_coverage,
)
from recon_tool.cache_paths import (
    resolve_cache_directory,
    unlink_cache_entry,
    write_cache_json,
)
from recon_tool.cache_paths import (
    resolve_result_cache_path as _safe_cache_path,
)
from recon_tool.cache_paths import (
    validated_cache_path as _cache_path_in,
)
from recon_tool.cache_values import (
    CacheClearResult,
    cache_object_tuple,
    cache_string,
    cache_string_tuple,
    clear_cache_directory,
    required_cache_float,
)
from recon_tool.cache_values import cache_bool as _cache_bool
from recon_tool.cache_values import cache_count as _cache_count
from recon_tool.cache_values import cache_dns_name_status as _cache_dns_name_status
from recon_tool.cache_values import cache_float as _cache_float
from recon_tool.cache_values import optional_cache_count as _optional_cache_count
from recon_tool.cache_values import optional_cache_string as _optional_cache_string
from recon_tool.cache_values import parse_confidence as _parse_confidence
from recon_tool.models import (
    CandidateValue,
    CertBurst,
    CertSummary,
    ChainMotifObservation,
    EvidenceRecord,
    InfrastructureCluster,
    InfrastructureClusterReport,
    InfrastructureEdge,
    MergeConflicts,
    NodeConflict,
    NodeEvidence,
    NodeUnitCounterfactual,
    PosteriorObservation,
    SurfaceAttribution,
    TenantInfo,
    serialize_conflicts,
)
from recon_tool.validator import validate_domain

__all__ = [
    "DEFAULT_TTL",
    "cache_clear",
    "cache_clear_all",
    "cache_dir",
    "cache_get",
    "cache_put",
    "tenant_info_from_dict",
    "tenant_info_to_dict",
]

logger = logging.getLogger("recon")

# A cache entry is a serialized TenantInfo (a few KB, up to ~100 KB with CT
# data). Reject a file larger than this before descriptor-bound decoding so a
# corrupt or hostile oversized file cannot be read whole into memory. Pairs with the
# RecursionError catch below: a deeply-nested JSON file raises RecursionError
# (a RuntimeError, not a ValueError), so without the catch a poisoned cache file
# would crash the next lookup instead of degrading to a clean cache miss.
_MAX_CACHE_FILE_BYTES = MAX_RESULT_CACHE_FILE_BYTES
_CACHE_VERSION = RESULT_CACHE_VERSION


def cache_dir() -> Path:
    """Return the result-cache directory (RECON_CONFIG_DIR / legacy / XDG cache)."""
    from recon_tool.paths import cache_root

    return cache_root() / "cache"


def cache_get(domain: str, ttl: int = DEFAULT_TTL, *, admit_incomplete: bool = False) -> TenantInfo | None:
    """Read cached TenantInfo for domain. Returns None unless it is admitted.

    Missing, expired, corrupt, lineage-invalid, and (by default)
    collection-incomplete entries all read as a miss. ``admit_incomplete`` is
    for ``recon delta``, which compares against the previous collection and
    already suppresses changes an incomplete collection cannot confirm; an
    ordinary lookup never reuses a result whose collection recorded a collector
    failure, so a later run on a recovered network collects again.

    The returned ``TenantInfo`` carries ``cached_at`` set from the
    on-disk ``_cached_at`` field so downstream can distinguish a
    cache-served result from a freshly-resolved one. ``resolved_at``
    is preserved from the time the result was first produced.
    """
    try:
        from recon_tool.cache_admission import read_result_cache_entry

        entry = read_result_cache_entry(domain, ttl=ttl, skip_expired=True)
    except Exception:
        # Cache reads are best-effort by contract. Validation re-evaluates
        # generated claims, so malformed state and any ordinary decoder or
        # generator failure must degrade to a clean miss.
        logger.debug("Cache read failed for %s", domain, exc_info=True)
        return None
    if entry.admission == "reusable" or (admit_incomplete and entry.admission == "collection_incomplete"):
        return entry.info
    logger.debug("Cache entry for %s not admitted: %s", domain, entry.admission)
    return None


def cache_put(domain: str, info: TenantInfo) -> None:
    """Write TenantInfo to cache as JSON. Creates dir if needed. Logs on failure."""
    try:
        expected_domain = validate_domain(domain, apex=False)
        if info.queried_domain != expected_domain:
            raise ValueError("Cache payload domain does not match its cache key")
        validate_insight_claim_coverage(info)
        d = resolve_cache_directory(create=True)
        if d is None:
            logger.debug("Cache write rejected redirected cache directory")
            return
        path = _cache_path_in(d, domain)
        if path is None:
            logger.debug("Cache write rejected invalid domain: %r", domain)
            return
        data = tenant_info_to_dict(info)
        from recon_tool.network_policy import current_policy

        policy_id = current_policy().identity
        if info.resolution_policy_id is not None and info.resolution_policy_id != policy_id:
            raise ValueError("Cache payload belongs to a different collection policy")
        data["_resolution_policy_id"] = policy_id
        write_cache_json(path, data)
    except Exception:
        # Cache persistence must never turn a successful lookup into a caller
        # failure. The debug record preserves the exception for maintainers.
        logger.debug("Cache write failed for %s", domain, exc_info=True)


def _cache_clear_detailed(domain: str) -> CacheClearResult:
    """Remove one cached TenantInfo and distinguish absence from I/O failure."""
    try:
        path = _safe_cache_path(domain)
        if path is None:
            logger.debug("Cache clear rejected invalid domain or cache directory: %r", domain)
            return CacheClearResult(failed=True)
        return CacheClearResult(removed=int(unlink_cache_entry(path)))
    except OSError:
        logger.debug("Cache clear failed for %s", domain, exc_info=True)
        return CacheClearResult(failed=True)


def cache_clear(domain: str) -> bool:
    """Remove the cached TenantInfo for domain. Returns True if a file was deleted.

    Input is sanitised via ``_safe_cache_path`` — crafted traversal
    strings like ``../settings`` are rejected and the function
    returns ``False`` rather than deleting a file outside the cache
    directory.
    """
    return _cache_clear_detailed(domain).removed > 0


def _cache_clear_all_detailed() -> CacheClearResult:
    """Remove every TenantInfo entry and interrupted-write artifact."""
    try:
        d = resolve_cache_directory()
        if d is None:
            logger.debug("Cache clear-all rejected redirected or inaccessible cache directory")
            return CacheClearResult(failed=True)
        if not d.is_dir():
            return CacheClearResult()
        return clear_cache_directory(d, layer="Result")
    except OSError:
        logger.debug("Cache clear-all failed", exc_info=True)
        return CacheClearResult(failed=True)


def cache_clear_all() -> int:
    """Remove all TenantInfo cache files. Returns the total file count."""
    result = _cache_clear_all_detailed()
    return result.removed + result.temporary_removed


def cert_summary_to_cache_dict(cert_summary: CertSummary | None) -> dict[str, Any] | None:
    """Serialize the complete certificate summary for either cache."""
    if cert_summary is None:
        return None
    return {
        "cert_count": cert_summary.cert_count,
        "issuer_diversity": cert_summary.issuer_diversity,
        "issuance_velocity": cert_summary.issuance_velocity,
        "newest_cert_age_days": cert_summary.newest_cert_age_days,
        "oldest_cert_age_days": cert_summary.oldest_cert_age_days,
        "top_issuers": list(cert_summary.top_issuers),
        "wildcard_sibling_clusters": [{"names": list(cluster)} for cluster in cert_summary.wildcard_sibling_clusters],
        "deployment_bursts": [
            {
                "window_start": burst.window_start,
                "window_end": burst.window_end,
                "span_seconds": burst.span_seconds,
                "names": list(burst.names),
            }
            for burst in cert_summary.deployment_bursts
        ],
    }


def infrastructure_clusters_to_cache_dict(
    report: InfrastructureClusterReport | None,
) -> dict[str, Any] | None:
    """Serialize the complete CT infrastructure report for either cache."""
    if report is None:
        return None
    return {
        "algorithm": report.algorithm,
        "modularity": report.modularity,
        "partition_stability": report.partition_stability,
        "stability_runs": report.stability_runs,
        "node_count": report.node_count,
        "edge_count": report.edge_count,
        "clusters": [
            {
                "cluster_id": cluster.cluster_id,
                "size": cluster.size,
                "members": list(cluster.members),
                "shared_cert_count": cluster.shared_cert_count,
                "dominant_issuer": cluster.dominant_issuer,
            }
            for cluster in report.clusters
        ],
        "edges": [
            {
                "source": edge.source,
                "target": edge.target,
                "shared_cert_count": edge.shared_cert_count,
            }
            for edge in report.edges
        ],
    }


def tenant_info_to_dict(info: TenantInfo) -> dict[str, Any]:
    """Serialize TenantInfo to a JSON-serializable dict with cache metadata.

    Handles: ConfidenceLevel to string, CertSummary to nested dict,
    EvidenceRecord tuple → list of dicts, detection_scores tuple-of-tuples → dict,
    all tuple fields → lists.
    """
    now_iso = datetime.now(UTC).isoformat()
    d: dict[str, Any] = {
        "_cached_at": now_iso,
        "_cache_version": _CACHE_VERSION,
        "resolution_vantage": info.resolution_vantage,
        "resolution_policy_id": info.resolution_policy_id,
        # resolved_at is the original resolution timestamp. Preserve it
        # across cache round-trips so agents can tell when the data was
        # first produced, not just when it was last written to disk.
        "resolved_at": info.resolved_at or now_iso,
        "tenant_id": info.tenant_id,
        "display_name": info.display_name,
        "default_domain": info.default_domain,
        "queried_domain": info.queried_domain,
        "confidence": info.confidence.value,
        "region": info.region,
        "sources": list(info.sources),
        "services": list(info.services),
        "slugs": list(info.slugs),
        "auth_type": info.auth_type,
        "dmarc_policy": info.dmarc_policy,
        "domain_count": info.domain_count,
        "tenant_domains": list(info.tenant_domains),
        "related_domains": list(info.related_domains),
        "insights": list(info.insights),
        "crtsh_degraded": info.crtsh_degraded,
        "degraded_sources": list(info.degraded_sources),
        "evidence_confidence": info.evidence_confidence.value,
        "inference_confidence": info.inference_confidence.value,
        "site_verification_tokens": list(info.site_verification_tokens),
        "mta_sts_mode": info.mta_sts_mode,
        "google_auth_type": info.google_auth_type,
        "google_idp_name": info.google_idp_name,
        "primary_email_provider": info.primary_email_provider,
        "email_gateway": info.email_gateway,
        "dmarc_pct": info.dmarc_pct,
        "dmarc_testing": info.dmarc_testing,
        "spf_include_count": info.spf_include_count,
        "likely_primary_email_provider": info.likely_primary_email_provider,
        "ct_provider_used": info.ct_provider_used,
        "ct_subdomain_count": info.ct_subdomain_count,
        "ct_related_domains": list(info.ct_related_domains),
        "ct_cache_age_days": info.ct_cache_age_days,
        "ct_attempt_outcome": info.ct_attempt_outcome,
        "dns_name_status": info.dns_name_status,
        "merge_conflicts": (
            serialize_conflicts(info.merge_conflicts)
            if info.merge_conflicts and info.merge_conflicts.has_conflicts
            else None
        ),
        "slug_confidences": dict(info.slug_confidences),
        "posterior_observations": [
            {
                "name": p.name,
                "description": p.description,
                "posterior": p.posterior,
                "interval_low": p.interval_low,
                "interval_high": p.interval_high,
                "evidence_used": list(p.evidence_used),
                "n_eff": p.n_eff,
                "sparse": p.sparse,
                "conflict_provenance": [
                    {
                        "field": c.field,
                        "sources": list(c.sources),
                        "magnitude": c.magnitude,
                    }
                    for c in p.conflict_provenance
                ],
                "evidence_ranked": [
                    {
                        "kind": e.kind,
                        "name": e.name,
                        "llr": e.llr,
                        "influence_pct": e.influence_pct,
                    }
                    for e in p.evidence_ranked
                ],
                "entropy_reduction_nats": p.entropy_reduction_nats,
                "unit_counterfactuals": [
                    {
                        "unit": c.unit,
                        "kind": c.kind,
                        "observed": c.observed,
                        "posterior_without": c.posterior_without,
                        "delta": c.delta,
                    }
                    for c in p.unit_counterfactuals
                ],
            }
            for p in info.posterior_observations
        ],
        "cloud_instance": info.cloud_instance,
        "tenant_region_sub_scope": info.tenant_region_sub_scope,
        "msgraph_host": info.msgraph_host,
        "lexical_observations": list(info.lexical_observations),
        # shared_verification_tokens is intentionally NOT cached — it is
        # batch-scope only and a per-domain lookup should never inherit
        # peers from a previous batch run.
    }

    # CertSummary → nested dict or None. Include the v1.7
    # additions (wildcard_sibling_clusters, deployment_bursts) so a
    # cache hit doesn't silently drop signal that was present in the
    # original lookup.
    d["cert_summary"] = cert_summary_to_cache_dict(info.cert_summary)

    # Reserved for a future chain-validated VMC identity implementation. Legacy
    # subject fields were unvalidated and must not cross a cache boundary.
    d["bimi_identity"] = None

    # EvidenceRecord tuple → list of dicts
    d["evidence"] = [
        {
            "source_type": ev.source_type,
            "raw_value": ev.raw_value,
            "rule_name": ev.rule_name,
            "slug": ev.slug,
        }
        for ev in info.evidence
    ]

    # Internal generation-time lineage is cache state, not stable public JSON.
    # Persist it with the insight strings so a cache hit never falls back to
    # heuristic text reconstruction.
    d["insight_claims"] = insight_claims_to_cache(info.insight_claims)

    # detection_scores tuple-of-tuples → dict
    d["detection_scores"] = dict(info.detection_scores)

    # SurfaceAttribution tuple → list of dicts
    d["surface_attributions"] = [
        {
            "subdomain": sa.subdomain,
            "primary_slug": sa.primary_slug,
            "primary_name": sa.primary_name,
            "primary_tier": sa.primary_tier,
            "infra_slug": sa.infra_slug,
            "infra_name": sa.infra_name,
        }
        for sa in info.surface_attributions
    ]

    # InfrastructureClusterReport → nested dict or None.
    d["infrastructure_clusters"] = infrastructure_clusters_to_cache_dict(info.infrastructure_clusters)

    # Every catalog-discovery collection travels together; see cache_catalog.
    d.update(catalog_discovery_to_cache_dict(info))

    # ChainMotifObservation tuple → list of dicts. These were being
    # dropped on cache write, so a cached lookup served motif_count = 0
    # even when the original resolve produced matches.
    d["chain_motifs"] = [
        {
            "motif_name": cm.motif_name,
            "display_name": cm.display_name,
            "confidence": cm.confidence,
            "subdomain": cm.subdomain,
            "chain": list(cm.chain),
        }
        for cm in info.chain_motifs
    ]

    return d


def _parse_conflict_provenance(entry: dict[str, Any]) -> tuple[NodeConflict, ...]:
    conflicts: list[NodeConflict] = []
    for raw_conflict in cache_object_tuple(
        entry.get("conflict_provenance", []), "posterior_observations.conflict_provenance"
    ):
        sources_raw = raw_conflict.get("sources", [])
        if sources_raw is None:
            raise ValueError("Cache conflict_provenance.sources must be an array of strings")
        conflicts.append(
            NodeConflict(
                field=cache_string(raw_conflict.get("field"), "conflict_provenance.field", nonempty=True),
                sources=cache_string_tuple(sources_raw, "conflict_provenance.sources"),
                magnitude=_cache_float(
                    raw_conflict.get("magnitude"),
                    "conflict_provenance.magnitude",
                    minimum=0.0,
                ),
            )
        )
    return tuple(conflicts)


def _parse_ranked_evidence(entry: dict[str, Any]) -> tuple[NodeEvidence, ...]:
    ranked: list[NodeEvidence] = []
    for raw_ranked in cache_object_tuple(entry.get("evidence_ranked", []), "posterior_observations.evidence_ranked"):
        ranked.append(
            NodeEvidence(
                kind=cache_string(raw_ranked.get("kind"), "evidence_ranked.kind", nonempty=True),
                name=cache_string(raw_ranked.get("name"), "evidence_ranked.name", nonempty=True),
                llr=required_cache_float(raw_ranked.get("llr"), "evidence_ranked.llr"),
                influence_pct=_cache_float(
                    raw_ranked.get("influence_pct"),
                    "evidence_ranked.influence_pct",
                    minimum=0.0,
                    maximum=100.0,
                ),
            )
        )
    return tuple(ranked)


def _parse_unit_counterfactuals(entry: dict[str, Any]) -> tuple[NodeUnitCounterfactual, ...]:
    counterfactuals: list[NodeUnitCounterfactual] = []
    for raw_counterfactual in cache_object_tuple(
        entry.get("unit_counterfactuals", []), "posterior_observations.unit_counterfactuals"
    ):
        counterfactuals.append(
            NodeUnitCounterfactual(
                unit=cache_string(raw_counterfactual.get("unit"), "unit_counterfactuals.unit", nonempty=True),
                kind=cache_string(raw_counterfactual.get("kind"), "unit_counterfactuals.kind", nonempty=True),
                observed=cache_string(raw_counterfactual.get("observed"), "unit_counterfactuals.observed"),
                posterior_without=required_cache_float(
                    raw_counterfactual.get("posterior_without"),
                    "unit_counterfactuals.posterior_without",
                    minimum=0.0,
                    maximum=1.0,
                ),
                delta=required_cache_float(
                    raw_counterfactual.get("delta"),
                    "unit_counterfactuals.delta",
                    minimum=-1.0,
                    maximum=1.0,
                ),
            )
        )
    return tuple(counterfactuals)


def _posterior_observation_from_cache(entry: dict[str, Any]) -> PosteriorObservation:
    conflicts = _parse_conflict_provenance(entry)
    ranked = _parse_ranked_evidence(entry)
    counterfactuals = _parse_unit_counterfactuals(entry)
    try:
        name = _optional_cache_string(entry["name"], "posterior_observations.name")
        if not name:
            raise ValueError("Cache field 'posterior_observations.name' must be a nonempty string")
        posterior = required_cache_float(
            entry.get("posterior"), "posterior_observations.posterior", minimum=0.0, maximum=1.0
        )
        interval_low = required_cache_float(
            entry.get("interval_low"), "posterior_observations.interval_low", minimum=0.0, maximum=1.0
        )
        interval_high = required_cache_float(
            entry.get("interval_high"), "posterior_observations.interval_high", minimum=0.0, maximum=1.0
        )
        if not interval_low <= posterior <= interval_high:
            raise ValueError("Cache posterior interval must satisfy interval_low <= posterior <= interval_high")
        return PosteriorObservation(
            name=name,
            description=_optional_cache_string(entry.get("description"), "posterior_observations.description") or "",
            posterior=posterior,
            interval_low=interval_low,
            interval_high=interval_high,
            evidence_used=cache_string_tuple(entry.get("evidence_used", []), "posterior_observations.evidence_used"),
            n_eff=_cache_float(entry.get("n_eff"), "posterior_observations.n_eff", minimum=0.0),
            sparse=_cache_bool(entry.get("sparse"), "posterior_observations.sparse"),
            conflict_provenance=conflicts,
            evidence_ranked=ranked,
            # Pre-2.2 cache entries lack the diagnostics; defaults apply
            # under the load-known and ignore-missing cache discipline.
            entropy_reduction_nats=_cache_float(
                entry.get("entropy_reduction_nats"), "posterior_observations.entropy_reduction_nats"
            ),
            unit_counterfactuals=counterfactuals,
        )
    except (KeyError, TypeError) as exc:
        raise ValueError("Cache field 'posterior_observations' contains a malformed observation") from exc


def _parse_posterior_observations(data: dict[str, Any]) -> tuple[PosteriorObservation, ...]:
    """Parse cached posterior observations while accepting pre-v1.9 entries."""
    raw = data.get("posterior_observations")
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise ValueError("Cache field 'posterior_observations' must be an array")
    if not all(isinstance(entry, dict) for entry in raw):
        raise ValueError("Cache field 'posterior_observations' must contain objects")
    return tuple(_posterior_observation_from_cache(entry) for entry in raw)


def _parse_degraded_sources(data: dict[str, Any]) -> tuple[str, ...]:
    """Parse degraded_sources from cache data, with backward compat for crtsh_degraded."""
    # New format: degraded_sources list
    ds = data.get("degraded_sources")
    if ds is not None:
        return cache_string_tuple(ds, "degraded_sources")
    # Old format: crtsh_degraded bool
    if _cache_bool(data.get("crtsh_degraded"), "crtsh_degraded"):
        return ("crt.sh",)
    return ()


def _wildcard_clusters_from_cache(raw: Any) -> tuple[tuple[str, ...], ...]:
    if not isinstance(raw, list):
        raise ValueError("Cache field 'cert_summary.wildcard_sibling_clusters' must be an array")
    clusters: list[tuple[str, ...]] = []
    for cluster in raw:
        if isinstance(cluster, dict):  # v2.0 {names: [...]}
            clusters.append(
                cache_string_tuple(cluster.get("names", []), "cert_summary.wildcard_sibling_clusters.names")
            )
        elif isinstance(cluster, list):  # legacy [name, ...]
            clusters.append(cache_string_tuple(cluster, "cert_summary.wildcard_sibling_clusters"))
        else:
            raise ValueError("Cache wildcard sibling cluster must be an object or array")
    return tuple(clusters)


def _cert_burst_from_cache(entry: Any) -> CertBurst:
    if not isinstance(entry, dict):
        raise ValueError("Cache deployment burst must be an object")
    window_start = entry.get("window_start", "")
    window_end = entry.get("window_end", "")
    if not isinstance(window_start, str) or not isinstance(window_end, str):
        raise ValueError("Cache deployment burst windows must be strings")
    return CertBurst(
        window_start=window_start,
        window_end=window_end,
        span_seconds=_cache_count(entry.get("span_seconds"), "cert_summary.deployment_bursts.span_seconds"),
        names=cache_string_tuple(entry.get("names", []), "cert_summary.deployment_bursts.names"),
    )


def _deployment_bursts_from_cache(raw: Any) -> tuple[CertBurst, ...]:
    if not isinstance(raw, list):
        raise ValueError("Cache field 'cert_summary.deployment_bursts' must be an array")
    return tuple(_cert_burst_from_cache(entry) for entry in raw)


def cert_summary_from_cache_dict(data: dict[str, Any]) -> CertSummary | None:
    """Restore complete certificate intelligence from a result-cache object."""
    cs_data = data.get("cert_summary")
    if cs_data is None:
        return None
    if not isinstance(cs_data, dict):
        raise ValueError("Cache field 'cert_summary' must be an object or null")
    wildcard_sibling_clusters = _wildcard_clusters_from_cache(cs_data.get("wildcard_sibling_clusters", []))
    deployment_bursts = _deployment_bursts_from_cache(cs_data.get("deployment_bursts", []))
    return CertSummary(
        cert_count=_cache_count(cs_data.get("cert_count"), "cert_summary.cert_count"),
        issuer_diversity=_cache_count(cs_data.get("issuer_diversity"), "cert_summary.issuer_diversity"),
        issuance_velocity=_cache_count(cs_data.get("issuance_velocity"), "cert_summary.issuance_velocity"),
        newest_cert_age_days=_cache_count(cs_data.get("newest_cert_age_days"), "cert_summary.newest_cert_age_days"),
        oldest_cert_age_days=_cache_count(cs_data.get("oldest_cert_age_days"), "cert_summary.oldest_cert_age_days"),
        top_issuers=cache_string_tuple(cs_data.get("top_issuers", []), "cert_summary.top_issuers"),
        wildcard_sibling_clusters=wildcard_sibling_clusters,
        deployment_bursts=deployment_bursts,
    )


def _surface_attributions_from_dict(data: dict[str, Any]) -> tuple[SurfaceAttribution, ...]:
    """Deserialize the ``surface_attributions`` list. Entries missing a
    subdomain / primary slug / primary name are skipped."""
    surface_list = data.get("surface_attributions", [])
    if not isinstance(surface_list, list):
        return ()
    sa_records: list[SurfaceAttribution] = []
    for item in surface_list:
        if not isinstance(item, dict):
            continue
        subdomain = item.get("subdomain")
        primary_slug = item.get("primary_slug")
        primary_name = item.get("primary_name")
        primary_tier = item.get("primary_tier", "application")
        if not subdomain or not primary_slug or not primary_name:
            continue
        sa_records.append(
            SurfaceAttribution(
                subdomain=str(subdomain),
                primary_slug=str(primary_slug),
                primary_name=str(primary_name),
                primary_tier=str(primary_tier),
                infra_slug=item.get("infra_slug"),
                infra_name=item.get("infra_name"),
            )
        )
    return tuple(sa_records)


def infrastructure_clusters_from_cache_dict(data: dict[str, Any]) -> InfrastructureClusterReport | None:
    """Deserialize the ``infrastructure_clusters`` envelope, or None
    when absent. A missing algorithm maps to ``skipped`` so the contract
    matches a live run that did not build clusters."""
    ic_data = data.get("infrastructure_clusters")
    if ic_data is None:
        return None
    if not isinstance(ic_data, dict):
        raise ValueError("Cache field 'infrastructure_clusters' must be an object or null")
    algorithm = ic_data.get("algorithm", "skipped")
    if not isinstance(algorithm, str) or algorithm not in ("louvain", "connected_components", "skipped"):
        raise ValueError("Cache infrastructure algorithm is invalid")
    clusters_raw = ic_data.get("clusters")
    cluster_records: list[InfrastructureCluster] = []
    if isinstance(clusters_raw, list):
        for entry in clusters_raw:
            if not isinstance(entry, dict):
                raise ValueError("Cache infrastructure cluster must be an object")
            members = cache_string_tuple(entry.get("members", []), "infrastructure_clusters.clusters.members")
            dominant_issuer = entry.get("dominant_issuer")
            if dominant_issuer is not None and not isinstance(dominant_issuer, str):
                raise ValueError("Cache cluster dominant_issuer must be a string or null")
            cluster_records.append(
                InfrastructureCluster(
                    cluster_id=_cache_count(entry.get("cluster_id"), "infrastructure_clusters.cluster_id"),
                    members=members,
                    size=_cache_count(entry.get("size"), "infrastructure_clusters.size", default=len(members)),
                    shared_cert_count=_cache_count(
                        entry.get("shared_cert_count"), "infrastructure_clusters.shared_cert_count"
                    ),
                    dominant_issuer=dominant_issuer,
                )
            )
    elif clusters_raw is not None:
        raise ValueError("Cache field 'infrastructure_clusters.clusters' must be an array")
    edges_raw = ic_data.get("edges", [])
    edge_records: list[InfrastructureEdge] = []
    if isinstance(edges_raw, list):
        for entry in edges_raw:
            if not isinstance(entry, dict):
                raise ValueError("Cache infrastructure edge must be an object")
            src = entry.get("source")
            dst = entry.get("target")
            if not isinstance(src, str) or not src or not isinstance(dst, str) or not dst:
                raise ValueError("Cache infrastructure edge endpoints must be nonempty strings")
            edge_records.append(
                InfrastructureEdge(
                    source=src,
                    target=dst,
                    shared_cert_count=_cache_count(
                        entry.get("shared_cert_count"), "infrastructure_clusters.edges.shared_cert_count", default=1
                    ),
                )
            )
    elif edges_raw is not None:
        raise ValueError("Cache field 'infrastructure_clusters.edges' must be an array")
    stability_raw = ic_data.get("partition_stability")
    partition_stability = (
        _cache_float(stability_raw, "infrastructure_clusters.partition_stability")
        if stability_raw is not None
        else None
    )
    return InfrastructureClusterReport(
        clusters=tuple(cluster_records),
        modularity=_cache_float(ic_data.get("modularity"), "infrastructure_clusters.modularity"),
        algorithm=algorithm,
        node_count=_cache_count(ic_data.get("node_count"), "infrastructure_clusters.node_count"),
        edge_count=_cache_count(ic_data.get("edge_count"), "infrastructure_clusters.edge_count"),
        edges=tuple(edge_records),
        # Pre-2.2 cache entries lack the stability fields; None/0 is the
        # honest "not measured" default, not a fabricated 1.0.
        partition_stability=partition_stability,
        stability_runs=_cache_count(ic_data.get("stability_runs"), "infrastructure_clusters.stability_runs"),
    )


def _chain_motifs_from_dict(data: dict[str, Any]) -> tuple[ChainMotifObservation, ...]:
    """Deserialize the ``chain_motifs`` list."""
    motifs_list = data.get("chain_motifs", [])
    if not isinstance(motifs_list, list):
        return ()
    cm_records: list[ChainMotifObservation] = []
    for item in motifs_list:
        if not isinstance(item, dict):
            continue
        motif_chain = item.get("chain", [])
        if not isinstance(motif_chain, list):
            continue
        cm_records.append(
            ChainMotifObservation(
                motif_name=str(item.get("motif_name", "")),
                display_name=str(item.get("display_name", "")),
                confidence=str(item.get("confidence", "medium")),
                subdomain=str(item.get("subdomain", "")),
                chain=tuple(str(h) for h in motif_chain),
            )
        )
    return tuple(cm_records)


def _read_slug_confidences(raw: object) -> tuple[tuple[str, float], ...]:
    """Read ``slug_confidences`` from a cache record.

    Accepts the v2.0 object-map form ``{slug: posterior}`` and the legacy
    ``[[slug, posterior], ...]`` list form, so pre-v2.0 cache entries still load.
    """
    if raw is None:
        return ()
    if isinstance(raw, dict):
        if not all(isinstance(key, str) for key in raw):
            raise ValueError("Cache field 'slug_confidences' must have string keys")
        return tuple(
            (key, _cache_float(value, f"slug_confidences.{key}", minimum=0.0, maximum=1.0))
            for key, value in raw.items()
        )
    if isinstance(raw, list | tuple):
        parsed: list[tuple[str, float]] = []
        for entry in raw:
            if not isinstance(entry, list | tuple) or len(entry) != 2 or not isinstance(entry[0], str):
                raise ValueError("Legacy cache field 'slug_confidences' must contain string-number pairs")
            parsed.append((entry[0], _cache_float(entry[1], f"slug_confidences.{entry[0]}", minimum=0.0, maximum=1.0)))
        return tuple(parsed)
    raise ValueError("Cache field 'slug_confidences' must be an object or pair array")


_MERGE_CONFLICT_FIELDS = frozenset(
    {"display_name", "auth_type", "region", "tenant_id", "dmarc_policy", "google_auth_type"}
)


def _parse_merge_conflicts(raw: object) -> MergeConflicts | None:
    """Rebuild MergeConflicts from a cached dict; None on absence or corruption.

    The to_dict path serializes conflicts via serialize_conflicts; without this
    inverse a cached result silently lost all conflict data (and the Bayesian
    n_eff conflict penalty) on read.
    """
    if not isinstance(raw, dict):
        return None
    kwargs: dict[str, tuple[CandidateValue, ...]] = {}
    for fname, cands in raw.items():
        if fname not in _MERGE_CONFLICT_FIELDS or not isinstance(cands, list):
            continue
        parsed = tuple(
            CandidateValue(
                value=str(c["value"]),
                source=str(c.get("source", "")),
                confidence=str(c.get("confidence", "")),
            )
            for c in cands
            if isinstance(c, dict) and isinstance(c.get("value"), str)
        )
        if parsed:
            kwargs[fname] = parsed
    return MergeConflicts(**kwargs) if kwargs else None


def tenant_info_from_dict(data: dict[str, Any]) -> TenantInfo:
    """Deserialize a dict back to TenantInfo. Raises ValueError on invalid data.

    Handles: string → ConfidenceLevel (fallback MEDIUM), nested dicts → frozen
    dataclasses, lists → tuples, dict → tuple-of-tuples for detection_scores.
    """
    if not isinstance(data, dict):  # pyright: ignore[reportUnnecessaryIsInstance, reportUnreachable]
        msg = "Cache data must be a dict"  # pyright: ignore[reportUnreachable]
        raise ValueError(msg)

    # Required string fields
    display_name = data.get("display_name")
    default_domain = data.get("default_domain")
    queried_domain = data.get("queried_domain")
    if (
        not isinstance(display_name, str)
        or not isinstance(default_domain, str)
        or not default_domain
        or not isinstance(queried_domain, str)
        or not queried_domain
    ):
        msg = "Missing required fields: display_name, default_domain, queried_domain"
        raise ValueError(msg)

    # CertSummary
    cert_summary = cert_summary_from_cache_dict(data)

    # Legacy cache entries carried unvalidated certificate-subject identity.
    # The stable field remains schema-compatible but is intentionally cleared.
    bimi_identity = None

    insights = cache_string_tuple(data.get("insights", []), "insights")

    # EvidenceRecord list
    evidence_list = data.get("evidence", [])
    evidence: tuple[EvidenceRecord, ...] = ()
    if isinstance(evidence_list, list):
        records = []
        for ev in evidence_list:
            if isinstance(ev, dict):
                records.append(
                    EvidenceRecord(
                        source_type=_optional_cache_string(ev.get("source_type"), "evidence.source_type") or "",
                        raw_value=_optional_cache_string(ev.get("raw_value"), "evidence.raw_value") or "",
                        rule_name=_optional_cache_string(ev.get("rule_name"), "evidence.rule_name") or "",
                        slug=_optional_cache_string(ev.get("slug"), "evidence.slug") or "",
                    )
                )
        evidence = tuple(records)

    insight_claims = insight_claims_from_cache(
        data.get("insight_claims"),
        insights=insights,
        evidence=evidence,
    )

    # detection_scores dict → tuple of tuples
    ds_data = data.get("detection_scores", {})
    detection_scores: tuple[tuple[str, str], ...] = ()
    if isinstance(ds_data, dict):
        if not all(isinstance(key, str) and isinstance(value, str) for key, value in ds_data.items()):
            raise ValueError("Cache field 'detection_scores' must be a string map")
        detection_scores = tuple(ds_data.items())
    elif ds_data is not None:
        raise ValueError("Cache field 'detection_scores' must be an object")

    # SurfaceAttribution / InfrastructureClusterReport / Unclassified
    # chains / ChainMotif observations — each deserialized by a helper so
    # this function stays a flat sequence of field reads.
    surface_attributions = _surface_attributions_from_dict(data)
    infrastructure_clusters = infrastructure_clusters_from_cache_dict(data)
    unclassified_cname_chains = unclassified_chains_from_dict(data)
    dns_catalog_summaries = dns_catalog_summaries_from_dict(data)
    unclassified_dns_observations = unclassified_dns_observations_from_dict(data)
    chain_motifs = _chain_motifs_from_dict(data)

    return TenantInfo(
        tenant_id=_optional_cache_string(data.get("tenant_id"), "tenant_id"),
        display_name=display_name,
        default_domain=default_domain,
        queried_domain=queried_domain,
        confidence=_parse_confidence(data.get("confidence"), "confidence"),
        region=_optional_cache_string(data.get("region"), "region"),
        sources=cache_string_tuple(data.get("sources", []), "sources"),
        services=cache_string_tuple(data.get("services", []), "services"),
        slugs=cache_string_tuple(data.get("slugs", []), "slugs"),
        auth_type=_optional_cache_string(data.get("auth_type"), "auth_type"),
        dmarc_policy=_optional_cache_string(data.get("dmarc_policy"), "dmarc_policy"),
        domain_count=_cache_count(data.get("domain_count"), "domain_count"),
        tenant_domains=cache_string_tuple(data.get("tenant_domains", []), "tenant_domains"),
        related_domains=cache_string_tuple(data.get("related_domains", []), "related_domains"),
        insights=insights,
        insight_claims=insight_claims,
        degraded_sources=_parse_degraded_sources(data),
        merge_conflicts=_parse_merge_conflicts(data.get("merge_conflicts")),
        cert_summary=cert_summary,
        evidence=evidence,
        evidence_confidence=_parse_confidence(data.get("evidence_confidence"), "evidence_confidence"),
        inference_confidence=_parse_confidence(data.get("inference_confidence"), "inference_confidence"),
        detection_scores=detection_scores,
        bimi_identity=bimi_identity,
        site_verification_tokens=cache_string_tuple(
            data.get("site_verification_tokens", []), "site_verification_tokens"
        ),
        mta_sts_mode=_optional_cache_string(data.get("mta_sts_mode"), "mta_sts_mode"),
        google_auth_type=_optional_cache_string(data.get("google_auth_type"), "google_auth_type"),
        google_idp_name=_optional_cache_string(data.get("google_idp_name"), "google_idp_name"),
        primary_email_provider=_optional_cache_string(data.get("primary_email_provider"), "primary_email_provider"),
        email_gateway=_optional_cache_string(data.get("email_gateway"), "email_gateway"),
        dmarc_pct=_optional_cache_count(data.get("dmarc_pct"), "dmarc_pct", maximum=100),
        dmarc_testing=_cache_bool(data.get("dmarc_testing"), "dmarc_testing"),
        spf_include_count=_cache_count(data.get("spf_include_count"), "spf_include_count"),
        likely_primary_email_provider=_optional_cache_string(
            data.get("likely_primary_email_provider"), "likely_primary_email_provider"
        ),
        ct_provider_used=_optional_cache_string(data.get("ct_provider_used"), "ct_provider_used"),
        ct_subdomain_count=_cache_count(data.get("ct_subdomain_count"), "ct_subdomain_count"),
        ct_related_domains=cache_string_tuple(data.get("ct_related_domains", []), "ct_related_domains"),
        ct_cache_age_days=_optional_cache_count(data.get("ct_cache_age_days"), "ct_cache_age_days"),
        ct_attempt_outcome=_optional_cache_string(data.get("ct_attempt_outcome"), "ct_attempt_outcome"),
        dns_name_status=_cache_dns_name_status(data.get("dns_name_status")),
        slug_confidences=_read_slug_confidences(data.get("slug_confidences")),
        posterior_observations=_parse_posterior_observations(data),
        cloud_instance=_optional_cache_string(data.get("cloud_instance"), "cloud_instance"),
        tenant_region_sub_scope=_optional_cache_string(data.get("tenant_region_sub_scope"), "tenant_region_sub_scope"),
        msgraph_host=_optional_cache_string(data.get("msgraph_host"), "msgraph_host"),
        lexical_observations=cache_string_tuple(data.get("lexical_observations", []), "lexical_observations"),
        surface_attributions=surface_attributions,
        unclassified_cname_chains=unclassified_cname_chains,
        dns_catalog_summaries=dns_catalog_summaries,
        unclassified_dns_observations=unclassified_dns_observations,
        chain_motifs=chain_motifs,
        infrastructure_clusters=infrastructure_clusters,
        resolved_at=_optional_cache_string(data.get("resolved_at"), "resolved_at"),
        resolution_vantage=_optional_cache_string(data.get("resolution_vantage"), "resolution_vantage"),
        resolution_policy_id=_optional_cache_string(data.get("resolution_policy_id"), "resolution_policy_id"),
        # cached_at is stamped by cache_get from _cached_at; not populated
        # from arbitrary dict input so round-tripping an uncached dict
        # does not spuriously mark the result as cache-served.
    )
