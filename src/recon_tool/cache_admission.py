"""Read admission for the lookup-result cache.

One rule decides whether a stored ``TenantInfo`` may answer an ordinary
lookup. ``cache.cache_get`` and ``cache_inspection`` (``recon cache show``)
both use it, so inspection metadata always agrees with what a lookup does.
"""

from __future__ import annotations

import dataclasses
import logging
from typing import Literal

from recon_tool.cache import tenant_info_from_dict
from recon_tool.cache_contract import DEFAULT_TTL, MAX_RESULT_CACHE_FILE_BYTES, RESULT_CACHE_VERSION
from recon_tool.cache_insights import validate_insight_claim_coverage
from recon_tool.cache_paths import read_cache_json, resolve_result_cache_path
from recon_tool.cache_values import require_cache_policy
from recon_tool.json_limits import is_json_object
from recon_tool.models import TenantInfo
from recon_tool.source_status import collection_incomplete
from recon_tool.sources.cert_issuer import normalize_cert_summary
from recon_tool.validator import validate_domain

__all__ = [
    "ResultCacheAdmission",
    "ResultCacheRead",
    "read_result_cache_entry",
    "result_cache_admission",
]

logger = logging.getLogger("recon")

ResultCacheAdmission = Literal["reusable", "expired", "lineage_invalid", "collection_incomplete"]
"""Read-admission decision for one result-cache entry.

``reusable`` is the only state an ordinary lookup serves. ``expired`` is past
the caller's TTL. ``lineage_invalid`` means generated insights no longer
validate against their recorded lineage. ``collection_incomplete`` means the
stored collection recorded a collector failure (see
``source_status.collection_incomplete``); it stays on disk as a ``recon delta``
baseline but never answers an ordinary lookup.
"""


@dataclasses.dataclass(frozen=True)
class ResultCacheRead:
    """One structurally valid result-cache entry with its admission decision."""

    info: TenantInfo
    cached_at: str | None
    age_seconds: float
    file_size_bytes: int
    admission: ResultCacheAdmission


def result_cache_admission(
    info: TenantInfo,
    *,
    age_seconds: float,
    ttl: int,
    has_lineage: bool = True,
) -> ResultCacheAdmission:
    """Decide whether an ordinary lookup may reuse a stored result.

    Sparse or observed-empty results (low confidence, no services) are
    reusable: only a recorded collector failure blocks reuse, so the next
    lookup after a network recovery collects again. Expiry is reported first
    because an expired entry is refreshed whatever else it holds.
    """
    if age_seconds > ttl:
        return "expired"
    if not has_lineage:
        return "lineage_invalid"
    try:
        validate_insight_claim_coverage(info)
    except Exception:
        logger.debug("Cached insight lineage failed validation for %s", info.queried_domain, exc_info=True)
        return "lineage_invalid"
    if collection_incomplete(info.degraded_sources, ct_provider_used=info.ct_provider_used):
        return "collection_incomplete"
    return "reusable"


def read_result_cache_entry(
    domain: str,
    *,
    ttl: int = DEFAULT_TTL,
    skip_expired: bool = False,
) -> ResultCacheRead:
    """Read and admission-check one entry, raising on missing or invalid state.

    ``FileNotFoundError`` means no entry. Structural problems (size, nesting,
    version, decoding, a payload bound to another domain) raise ``ValueError``
    or a decoder error. A structurally valid entry returns with its admission
    decision, so callers can report why it is not reused. ``skip_expired``
    rejects an expired file from descriptor metadata before parsing it, for
    readers that only want a reusable entry.
    """
    expected_domain = validate_domain(domain, apex=False)
    path = resolve_result_cache_path(expected_domain)
    if path is None:
        raise ValueError("Result cache path is outside its configured boundary")
    data, file_stat, age_seconds = read_cache_json(
        path,
        maximum_bytes=MAX_RESULT_CACHE_FILE_BYTES,
        maximum_age_seconds=ttl if skip_expired else None,
    )
    if not is_json_object(data):
        raise ValueError("Result cache payload must be a JSON object")
    if data.get("_cache_version") != RESULT_CACHE_VERSION:
        raise ValueError("Result cache version does not match the current format")
    if data.get("queried_domain") != expected_domain:
        raise ValueError("Result cache payload domain does not match its cache key")
    require_cache_policy(data)
    info = tenant_info_from_dict(data)
    if info.queried_domain != expected_domain:
        raise ValueError("Result cache payload domain does not match its cache key")
    admission = result_cache_admission(
        info,
        age_seconds=age_seconds,
        ttl=ttl,
        has_lineage="insight_claims" in data,
    )
    info = dataclasses.replace(info, cert_summary=normalize_cert_summary(info.cert_summary))
    raw_cached_at = data.get("_cached_at")
    cached_at = raw_cached_at if isinstance(raw_cached_at, str) and raw_cached_at else None
    if cached_at is not None:
        info = dataclasses.replace(info, cached_at=cached_at)
    return ResultCacheRead(
        info=info,
        cached_at=cached_at,
        age_seconds=age_seconds,
        file_size_bytes=file_stat.st_size,
        admission=admission,
    )
