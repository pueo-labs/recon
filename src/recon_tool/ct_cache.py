# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportUnknownArgumentType=none
"""Per-domain CT subdomain cache.

Stores CT provider results as JSON files in {Config_Dir}/ct-cache/.
One file per domain, 30-day default TTL, lazy eviction via mtime.
All I/O wrapped in try/except — never raises to caller.

Separate from the main TenantInfo cache (cache.py): the CT cache stores
the reusable provider output, certificate summary, and infrastructure
cluster report so it can serve as a fallback when live CT providers are
degraded without needing a full TenantInfo round-trip.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from recon_tool.cache import (
    cache_string_tuple,
    cert_summary_from_cache_dict,
    cert_summary_to_cache_dict,
    infrastructure_clusters_from_cache_dict,
    infrastructure_clusters_to_cache_dict,
)
from recon_tool.cache_paths import read_cache_json, resolve_cache_directory, unlink_cache_entry, write_cache_json
from recon_tool.cache_values import (
    CacheClearResult,
    CacheInspection,
    CacheListing,
    CachePolicyMismatch,
    clear_cache_directory,
    require_cache_policy,
    select_cache_file_stems,
)
from recon_tool.models import CertSummary, InfrastructureClusterReport
from recon_tool.sources.cert_issuer import normalize_cert_summary
from recon_tool.validator import validate_domain

__all__ = [
    "CT_CACHE_TTL",
    "CTCacheEntry",
    "CTCacheInfo",
    "ct_cache_clear",
    "ct_cache_clear_all",
    "ct_cache_dir",
    "ct_cache_get",
    "ct_cache_list",
    "ct_cache_put",
    "ct_cache_show",
]

logger = logging.getLogger("recon")

CT_CACHE_TTL: int = 2592000  # 30 days in seconds.
# Bumped from 7 days in v1.9.25 alongside the CT pipeline resilience
# work. Free-tier rate limits (crt.sh 5/min IP, CertSpotter 10/day
# for subdomain queries) make full-corpus CT enumeration a multi-
# session operation; a 30-day window keeps prior fetches usable
# across the build-up runs without forcing re-fetch when nothing
# meaningful about a domain's cert posture is likely to have changed.

# A CT cache entry is small (up to ~100 subdomains plus a cert summary). The
# descriptor loader rejects files above this bound before reading their body.
_MAX_CT_CACHE_FILE_BYTES = 5 * 1024 * 1024
_CT_CACHE_VERSION = 1


@dataclass(frozen=True)
class CTCacheEntry:
    """Data returned from a CT cache hit."""

    subdomains: tuple[str, ...]
    cert_summary: CertSummary | None
    provider_used: str
    cached_at: str  # ISO timestamp
    age_days: int
    infrastructure_clusters: InfrastructureClusterReport | None = None


@dataclass(frozen=True)
class CTCacheInfo:
    """Metadata about a cached CT entry (for `recon cache show`)."""

    domain: str
    provider_used: str
    subdomain_count: int
    cached_at: str
    age_days: int
    file_size_bytes: int
    age_seconds: float = 0.0


def ct_cache_dir() -> Path:
    """Return the CT cache directory (RECON_CONFIG_DIR / legacy / XDG cache)."""
    from recon_tool.paths import cache_root

    return cache_root() / "ct-cache"


def _safe_path(domain: str) -> Path:
    """Resolve a cache file path, rejecting path traversal attempts.

    Domain validation rejects malformed and traversal-shaped input before path
    construction. ``Path.is_relative_to`` compares path components, so sibling
    directories cannot pass a string-prefix check. The final component remains
    unresolved so the descriptor loader can reject a symbolic link rather than
    silently following it.
    """
    d = resolve_cache_directory("ct-cache")
    if d is None:
        raise ValueError("CT cache directory resolves outside its configured root")
    return _path_in(d, domain)


def _path_in(directory: Path, domain: str) -> Path:
    """Return a validated CT cache path in one already-resolved directory."""
    try:
        normalized = validate_domain(domain, apex=False)
    except ValueError as exc:
        msg = f"Invalid domain for cache path: {domain}"
        raise ValueError(msg) from exc
    d = directory
    path = d / f"{normalized}.json"
    try:
        if not path.is_relative_to(d):
            msg = f"Invalid domain for cache path: {domain}"
            raise ValueError(msg)
    except (ValueError, OSError) as exc:
        msg = f"Invalid domain for cache path: {domain}"
        raise ValueError(msg) from exc
    return path


def ct_cache_get(domain: str, ttl: int = CT_CACHE_TTL) -> CTCacheEntry | None:
    """Read cached CT data for domain. Returns None if missing/stale/corrupt."""
    try:
        expected_domain = validate_domain(domain, apex=False)
        path = _safe_path(domain)
        data, _file_stat, age_seconds = read_cache_json(
            path,
            maximum_bytes=_MAX_CT_CACHE_FILE_BYTES,
            maximum_age_seconds=ttl,
        )
        if not isinstance(data, dict):
            raise ValueError("CT cache payload must be a JSON object")
        return _entry_from_dict(data, age_seconds, expected_domain)
    except (OSError, OverflowError, TypeError, ValueError, json.JSONDecodeError, RecursionError):
        # RecursionError (a deeply-nested poisoned file) escapes the other
        # entries; degrade to a clean miss rather than crash the caller.
        logger.debug("CT cache read failed for %s", domain, exc_info=True)
        return None


def ct_cache_put(
    domain: str,
    subdomains: list[str],
    cert_summary: CertSummary | None,
    provider_used: str,
    *,
    infrastructure_clusters: InfrastructureClusterReport | None = None,
) -> None:
    """Write CT results to cache. Creates dir if needed. Logs on failure."""
    try:
        normalized_domain = validate_domain(domain, apex=False)
        d = resolve_cache_directory("ct-cache", create=True)
        if d is None:
            logger.debug("CT cache write rejected redirected cache directory")
            return
        path = _path_in(d, domain)
        data = _entry_to_dict(
            normalized_domain,
            subdomains,
            cert_summary,
            provider_used,
            infrastructure_clusters,
        )
        write_cache_json(path, data)
        logger.debug("CT cache written for %s (%d subdomains)", domain, len(subdomains))
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        logger.debug("CT cache write failed for %s", domain, exc_info=True)


def _ct_cache_clear_detailed(domain: str) -> CacheClearResult:
    """Remove one CT cache entry and distinguish absence from I/O failure."""
    try:
        path = _safe_path(domain)
        return CacheClearResult(removed=int(unlink_cache_entry(path)))
    except (OSError, ValueError):
        logger.debug("CT cache clear failed for %s", domain, exc_info=True)
        return CacheClearResult(failed=True)


def ct_cache_clear(domain: str) -> bool:
    """Remove cached CT data for a domain. Returns True if file existed."""
    return _ct_cache_clear_detailed(domain).removed > 0


def _ct_cache_clear_all_detailed() -> CacheClearResult:
    """Remove all CT entries and interrupted-write artifacts."""
    try:
        d = resolve_cache_directory("ct-cache")
        if d is None:
            logger.debug("CT cache clear-all rejected redirected or inaccessible cache directory")
            return CacheClearResult(failed=True)
        if not d.is_dir():
            return CacheClearResult()
        return clear_cache_directory(d, layer="CT")
    except OSError:
        logger.debug("CT cache clear-all failed", exc_info=True)
        return CacheClearResult(failed=True)


def ct_cache_clear_all() -> int:
    """Remove all cached CT data. Returns the total file count removed."""
    result = _ct_cache_clear_all_detailed()
    return result.removed + result.temporary_removed


def _ct_cache_inspect(domain: str) -> CacheInspection[CTCacheInfo]:
    """Inspect one CT entry while distinguishing absence from read failure."""
    try:
        expected_domain = validate_domain(domain, apex=False)
        path = _safe_path(domain)
        data, file_stat, age_seconds = read_cache_json(path, maximum_bytes=_MAX_CT_CACHE_FILE_BYTES)
        if not isinstance(data, dict):
            raise ValueError("CT cache payload must be a JSON object")
        entry = _entry_from_dict(data, age_seconds, expected_domain)
        return CacheInspection(
            entry=CTCacheInfo(
                domain=expected_domain,
                provider_used=entry.provider_used,
                subdomain_count=len(entry.subdomains),
                cached_at=entry.cached_at,
                age_days=int(age_seconds / 86400),
                file_size_bytes=file_stat.st_size,
                age_seconds=age_seconds,
            )
        )
    except FileNotFoundError:
        return CacheInspection()
    except CachePolicyMismatch:
        return CacheInspection(other_policy=True)
    except (OSError, OverflowError, TypeError, ValueError, json.JSONDecodeError, RecursionError):
        logger.debug("CT cache inspection failed for %s", domain, exc_info=True)
        return CacheInspection(failed=True)


def ct_cache_show(domain: str) -> CTCacheInfo | None:
    """Return metadata about a valid cached CT entry, or None otherwise."""
    return _ct_cache_inspect(domain).entry


def _ct_cache_list_detailed(*, limit: int | None = None) -> CacheListing[CTCacheInfo]:
    """List CT metadata with optional bounded payload inspection."""
    entries: list[CTCacheInfo] = []
    try:
        d = resolve_cache_directory("ct-cache")
        if d is None:
            logger.debug("CT cache listing rejected its configured directory")
            return CacheListing(failed=1)
        if not d.exists():
            return CacheListing()
        if not d.is_dir():
            logger.debug("CT cache listing path is not a directory")
            return CacheListing(failed=1)
        selection = select_cache_file_stems(d, limit=limit)
        failed = 0
        other_policy = 0
        for stem in selection.stems:
            inspection = _ct_cache_inspect(stem)
            if inspection.entry is not None:
                entries.append(inspection.entry)
            elif inspection.failed:
                failed += 1
            elif inspection.other_policy:
                other_policy += 1
        return CacheListing(
            entries=tuple(entries),
            failed=failed,
            inspected=len(selection.stems),
            total=selection.total,
            temporary_files=selection.temporary_files,
            other_policy=other_policy,
        )
    except OSError:
        logger.debug("CT cache list failed", exc_info=True)
        return CacheListing(failed=1)


def ct_cache_list() -> list[CTCacheInfo]:
    """List all valid cached CT entries with metadata."""
    return list(_ct_cache_list_detailed().entries)


# ── Serialization ─────────────────────────────────────────────────────


def _entry_to_dict(
    domain: str,
    subdomains: list[str],
    cert_summary: CertSummary | None,
    provider_used: str,
    infrastructure_clusters: InfrastructureClusterReport | None,
) -> dict[str, Any]:
    from recon_tool.network_policy import current_policy

    d: dict[str, Any] = {
        "_cache_version": _CT_CACHE_VERSION,
        "_resolution_policy_id": current_policy().identity,
        "cached_at": datetime.now(UTC).isoformat(),
        "domain": domain,
        "provider_used": provider_used,
        "subdomains": subdomains,
    }
    d["cert_summary"] = cert_summary_to_cache_dict(cert_summary)
    d["infrastructure_clusters"] = infrastructure_clusters_to_cache_dict(infrastructure_clusters)
    return d


def _entry_from_dict(data: dict[str, Any], age_seconds: float, expected_domain: str) -> CTCacheEntry:
    if data.get("_cache_version") != _CT_CACHE_VERSION or data.get("domain") != expected_domain:
        raise ValueError("CT cache payload domain or version does not match its cache key")
    require_cache_policy(data)
    provider_used = data.get("provider_used", "unknown")
    cached_at = data.get("cached_at", "unknown")
    if not isinstance(provider_used, str) or not isinstance(cached_at, str):
        raise ValueError("CT cache provider_used and cached_at must be strings")
    return CTCacheEntry(
        subdomains=cache_string_tuple(data.get("subdomains", []), "subdomains"),
        cert_summary=normalize_cert_summary(cert_summary_from_cache_dict(data)),
        provider_used=provider_used,
        cached_at=cached_at,
        age_days=int(age_seconds / 86400),
        infrastructure_clusters=infrastructure_clusters_from_cache_dict(data),
    )
