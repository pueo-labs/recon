# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportUnknownArgumentType=none, reportUnknownMemberType=none, reportUnknownVariableType=none
"""Certificate transparency intelligence providers.

Abstracts CT querying behind a CertIntelProvider protocol with shared
filtering helpers. Providers: CrtshProvider (primary), CertSpotterProvider (fallback).

All HTTP goes through the SSRF-safe client from recon_tool/http.py.
Zero credentials, zero API keys.
"""

from __future__ import annotations

import logging
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol, runtime_checkable

import httpx

from recon_tool.http import http_client
from recon_tool.infra_graph import build_infrastructure_clusters
from recon_tool.models import CertBurst, CertSummary, InfrastructureClusterReport
from recon_tool.rate_limit import (
    AdaptiveRateLimiter,
    RateLimited,
    ct_rate_limiter_certspotter,
    ct_rate_limiter_crtsh,
)
from recon_tool.sources.cert_issuer import issuer_display_name
from recon_tool.validator import is_safe_dns_name

# CT SAN values are attacker-controlled: anyone can log a certificate for
# a domain they own, with arbitrary SAN strings, to a public CT log, and
# crt.sh / CertSpotter return them verbatim. A SAN carrying raw control
# bytes (ESC, NUL, an interior newline) would otherwise flow into
# related_domains and the wildcard / burst surfaces, then render to the
# operator's terminal (rich does not strip ESC) or into MCP / markdown
# output. A real DNS name uses only the letter-digit-hyphen alphabet plus
# dot, underscore (DKIM / SRV selectors), and a leading wildcard label;
# reject anything else rather than try to sanitize a malformed name.
# Canonical implementation lives in recon_tool.validator; aliased here for
# the cert-ingestion call sites and the round-2 regression tests.
_is_safe_san_name = is_safe_dns_name


# ── Caps for derived cert intelligence ───────────────────────────────────
# Wildcard SAN sibling clusters: each cert that contains ≥1 wildcard SAN
# can produce one cluster of its non-wildcard SANs. We bound both how
# many clusters surface and how big each cluster can be — a single cert
# with hundreds of SANs would otherwise dominate the field.
_MAX_WILDCARD_CLUSTERS = 10
_MAX_NAMES_PER_CLUSTER = 20

# Temporal CT burst detection: certificates whose not_before timestamps
# fall within ``_BURST_WINDOW_SECONDS`` of each other are treated as a
# co-issuance cohort. The minimum cohort size keeps single renewals out
# of the burst output. ``_MAX_BURSTS`` and ``_MAX_NAMES_PER_BURST`` cap
# the surface so a long history with constant renewals does not flood
# the JSON.
_BURST_WINDOW_SECONDS = 60
_MIN_BURST_NAMES = 3
_MAX_BURSTS = 8
_MAX_NAMES_PER_BURST = 25


def _parse_iso_datetime(value: str) -> datetime:
    """Parse an ISO-8601 timestamp tolerating a trailing ``Z``.

    Python 3.10's ``datetime.fromisoformat`` rejects the ``Z`` UTC
    suffix that CertSpotter and many CT log emitters use; only 3.11+
    accepts it natively. We normalise here so both providers behave
    the same on every supported Python. Raises ValueError on
    unparseable input — callers handle that.
    """
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    return datetime.fromisoformat(normalized)


logger = logging.getLogger("recon")

__all__ = [
    "CertIntelProvider",
    "CertSpotterProvider",
    "CrtshProvider",
    "build_cert_summary",
    "filter_subdomains",
]

# ── Shared constants ────────────────────────────────────────────────────

# Patterns to filter out from CT results — wildcards, common noise,
# and subdomains that rarely have interesting TXT/MX records.
SKIP_PREFIXES = (
    "*.",
    "cpanel.",
    "cpcalendars.",
    "cpcontacts.",
    "webdisk.",
    "webmail.",
    "mail.",
    "ftp.",
    "localhost.",
    "www.",
)

# Maximum number of unique subdomains to extract from CT results.
MAX_SUBDOMAINS = 100

# Bound local processing of CT provider responses. The HTTP client still
# receives a provider response as a whole, but parsing every certificate
# entry and every name from a very large crt.sh JSON payload can create
# avoidable CPU/memory spikes before the public ``MAX_SUBDOMAINS`` cap is
# applied. These limits keep extraction proportional to the output cap.
_MAX_CRTSH_ENTRIES = MAX_SUBDOMAINS * 20
_MAX_CRTSH_RAW_NAMES = MAX_SUBDOMAINS * 10
_MAX_CRTSH_CERT_SUMMARY_ENTRIES = MAX_SUBDOMAINS * 10

# Hostnames cap out at 253 chars. A pathological crt.sh ``name_value``
# field could in principle list millions of newline-delimited names,
# and parsing the whole field before any later cap is what made
# CrtshProvider memory-unbounded under hostile/malformed CT responses.
# Cap the per-cert SAN parse to a generous-but-bounded number; sane
# certs are well below this (web PKI BR limits push real certs to a
# few thousand SANs at the outside).
_MAX_SANS_PER_CERT = 2000

# High-signal subdomain prefixes that commonly CNAME to SaaS providers.
HIGH_SIGNAL_PREFIXES = (
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
    "support",
    "help",
    "status",
    "track",
    "click",
    "image",
    "view",
    "email",
    "em.",
    "cdn",
    "assets",
    "static",
    "media",
    "blog",
    "docs",
    "kb",
    "stage",
    "staging",
    "dev",
    "sandbox",
    "preview",
    "uat",
    # Keep prioritization in parity with the dns.py probe
    # wordlist. CT SAN sets that include these prefixes should sort to
    # the top of the returned subdomain list so the operator sees the
    # data, AI, ops, and security tiers when CT happens to surface them.
    "data",
    "analytics",
    "ml",
    "ai",
    "internal",
    "ops",
    "tools",
    "security",
)

# Timeout for CT HTTP calls. Separate from DNS query timeout because
# CT services can be slow under load. Kept tight so a slow provider
# fails fast and the fallback chain proceeds.
_CT_TIMEOUT = 6.0


# Process-wide cap on concurrent CT calls. Both crt.sh and
# CertSpotter free-tier rate-limit aggressively (CertSpotter ~50
# req/min per IP), and batch concurrency multiplied unbounded CT
# pressure. The 5241-domain 2026-05-27 corpus run saw 99.9% of records
# with crt.sh degraded because four-way batch concurrency burst far
# past the per-IP budget. Capping CT calls process-wide keeps the
# enumerator under free-tier limits regardless of how many domains
# the caller is resolving in parallel.
#
# Created lazily on first use because the running asyncio loop must
# exist at construction time. ``_get_ct_semaphore`` returns a per-
# loop singleton so tests that create their own loop see a fresh
# semaphore rather than a stale one bound to the prior loop.
import asyncio  # noqa: E402  (placed here so the rationale stays adjacent)
import weakref  # noqa: E402

_CT_GLOBAL_CONCURRENCY = 2
# Keyed by the loop object through a weak map so a closed loop's entry drops on
# GC. A plain id(loop) key could be reused by a freshly-created loop and hand
# back a stale semaphore (permits already consumed by the dead loop).
_ct_semaphore_by_loop: weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, asyncio.Semaphore] = (
    weakref.WeakKeyDictionary()
)


def _get_ct_semaphore() -> asyncio.Semaphore:
    """Return the asyncio semaphore that gates CT provider calls.

    Bound to the running event loop. Tests that swap loops get a
    fresh semaphore rather than one tied to the previous loop's
    state.
    """
    loop = asyncio.get_running_loop()
    sem = _ct_semaphore_by_loop.get(loop)
    if sem is None:
        sem = asyncio.Semaphore(_CT_GLOBAL_CONCURRENCY)
        _ct_semaphore_by_loop[loop] = sem
    return sem


def _parse_retry_after(resp: httpx.Response) -> float | None:
    """Parse the ``Retry-After`` header into seconds, or return None.

    RFC 7231 allows either a delta-seconds integer or an HTTP-date;
    we accept only the numeric form because the HTTP-date branch
    requires careful clock handling and providers we care about
    (crt.sh, CertSpotter) emit the numeric form when they emit at all.
    Negative or unparseable values become None.
    """
    raw = resp.headers.get("retry-after")
    if not raw:
        return None
    try:
        seconds = float(raw.strip())
    except (TypeError, ValueError):
        return None
    if seconds < 0:
        return None
    return seconds


# ── Protocol ────────────────────────────────────────────────────────────


class CertProviderPartialRateLimit(Exception):
    """Partial CT page data collected before a provider rate limit.

    Carries usable subdomain and summary data so the orchestrator can retain
    the partial observation while still marking the provider degraded.
    """

    def __init__(
        self,
        subdomains: list[str],
        cert_summary: CertSummary | None,
        infrastructure_clusters: InfrastructureClusterReport | None,
        provider_name: str,
    ) -> None:
        self.subdomains = subdomains
        self.cert_summary = cert_summary
        self.infrastructure_clusters = infrastructure_clusters
        self.provider_name = provider_name
        super().__init__(f"{provider_name} rate-limited after partial CT pages")


@runtime_checkable
class CertIntelProvider(Protocol):
    """Protocol for certificate transparency intelligence providers."""

    @property
    def name(self) -> str:
        """Unique identifier for this provider (e.g. 'crt.sh', 'certspotter')."""
        ...

    async def query(
        self,
        domain: str,
    ) -> tuple[list[str], CertSummary | None, InfrastructureClusterReport | None]:
        """Query CT data for a domain.

        Returns:
            Tuple of ``(discovered_subdomains, cert_summary,
            infrastructure_clusters)``. ``cert_summary`` is None when no
            cert metadata could be parsed; ``infrastructure_clusters``
            is None on the same condition (the report is built from the
            same entries).

        Raises:
            Exception on failure (timeout, HTTP error, etc.) so the
            fallback chain can proceed to the next provider.
            CertProviderPartialRateLimit when a rate limit truncates paging
            after at least one successful page; callers must retain the
            payload and mark the provider degraded.
        """
        ...


# ── Shared filtering helpers ────────────────────────────────────────────


def filter_subdomains(
    raw_names: list[str],
    domain: str,
    skip_prefixes: tuple[str, ...] = SKIP_PREFIXES,
    max_count: int = MAX_SUBDOMAINS,
) -> list[str]:
    """Filter and prioritize subdomain names from CT results.

    Applies: wildcard removal, noise-prefix skip, subdomain-of-domain
    validation, priority sort (high-signal first, shallow first), max cap.

    Args:
        raw_names: Raw subdomain strings (may include wildcards, noise, etc.)
        domain: The queried domain (e.g. "example.com")
        skip_prefixes: Prefixes to filter out
        max_count: Maximum number of subdomains to return

    Returns:
        Filtered, prioritized list of subdomain strings.
    """
    domain_lower = domain.lower()
    seen: set[str] = set()

    # Hard ceiling on accumulation to bound worst-case memory and sort
    # cost. A domain with an enormous CT history (tens of thousands of
    # distinct subdomains) would otherwise force the whole set into
    # memory and sort it — when recon is exposed via MCP to an untrusted
    # caller, that's an easy CPU-spike vector. Capping at ``max_count *
    # 10`` keeps enough headroom to still prioritize high-signal
    # subdomains correctly while bounding the work.
    hard_cap = max_count * 10

    for raw_name in raw_names:
        name = raw_name.lower().strip()
        if not name or name == domain_lower:
            continue
        # Drop SAN values that are not clean DNS names. Anything carrying
        # control bytes or other non-DNS characters is not a real related
        # domain and would be an ANSI-escape / newline injection vector in
        # the rendered panel and MCP output.
        if not _is_safe_san_name(name):
            continue
        if any(name.startswith(prefix) for prefix in skip_prefixes):
            continue
        if not name.endswith(f".{domain_lower}"):
            continue
        seen.add(name)
        if len(seen) >= hard_cap:
            break

    if not seen:
        return []

    def _sort_key(name: str) -> tuple[int, int, str]:
        """Sort: high-signal prefixes first, then by depth (shallow first), then alpha."""
        prefix = name.split(f".{domain_lower}")[0]
        is_high = 0 if any(prefix == p or prefix.startswith((p + ".", p + "-")) for p in HIGH_SIGNAL_PREFIXES) else 1
        depth = prefix.count(".")
        return (is_high, depth, name)

    return sorted(seen, key=_sort_key)[:max_count]


def _extract_wildcard_sibling_clusters(
    entries: Sequence[Mapping[str, str | int | list[str] | None]],
) -> tuple[tuple[str, ...], ...]:
    """Walk cert entries, harvesting non-wildcard SANs from any cert that
    also covered a wildcard SAN.

    Each cert that contains ``*.something`` produces one cluster: the
    sorted, deduplicated, non-wildcard SAN set from that same cert.
    Wildcards in the cluster itself are dropped (the wildcard fact is
    already implicit in the cluster's existence).

    Bounded by ``_MAX_WILDCARD_CLUSTERS`` and ``_MAX_NAMES_PER_CLUSTER``
    to keep one massive cert from dominating the field. Identical
    clusters across renewals are deduplicated.
    """
    seen_clusters: set[tuple[str, ...]] = set()
    out: list[tuple[str, ...]] = []
    for entry in entries:
        names = entry.get("dns_names")
        if not isinstance(names, list) or not names:
            continue
        # Need at least one wildcard SAN for this cert to be a "wildcard
        # cert" for our purposes.
        has_wildcard = any(n.startswith("*.") for n in names)
        if not has_wildcard:
            continue
        siblings: set[str] = set()
        for n in names:
            normalized = n.strip().lower()
            if not normalized or normalized.startswith("*."):
                continue
            siblings.add(normalized)
        if not siblings:
            continue
        cluster = tuple(sorted(siblings)[:_MAX_NAMES_PER_CLUSTER])
        if cluster in seen_clusters:
            continue
        seen_clusters.add(cluster)
        out.append(cluster)
        if len(out) >= _MAX_WILDCARD_CLUSTERS:
            break
    return tuple(out)


def _detect_deployment_bursts(
    entries: Sequence[Mapping[str, str | int | list[str] | None]],
) -> tuple[CertBurst, ...]:
    """Cluster cert entries by ``not_before`` proximity.

    Sort entries by parseable ``not_before``; each contiguous group whose
    span fits inside ``_BURST_WINDOW_SECONDS`` becomes a candidate burst.
    A burst is emitted only when the cohort has at least
    ``_MIN_BURST_NAMES`` distinct non-wildcard SANs across the group.

    Output is intentionally relative — span_seconds + name list — and
    never claims ownership. Co-issuance is observable; "same owner" is
    not.
    """
    parsed: list[tuple[datetime, list[str]]] = []
    for entry in entries:
        not_before_raw = entry.get("not_before")
        if not isinstance(not_before_raw, str):
            continue
        try:
            dt = _parse_iso_datetime(not_before_raw)
        except (ValueError, TypeError):
            continue
        dt = dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt
        names = entry.get("dns_names")
        names_list: list[str] = []
        if isinstance(names, list):
            for n in names:
                nm = n.strip().lower()
                if nm and not nm.startswith("*."):
                    names_list.append(nm)
        parsed.append((dt, names_list))

    if not parsed:
        return ()
    parsed.sort(key=lambda t: t[0])

    bursts: list[CertBurst] = []
    i = 0
    while i < len(parsed):
        window_start = parsed[i][0]
        cluster: list[tuple[datetime, list[str]]] = [parsed[i]]
        j = i + 1
        while j < len(parsed):
            if (parsed[j][0] - window_start).total_seconds() <= _BURST_WINDOW_SECONDS:
                cluster.append(parsed[j])
                j += 1
            else:
                break
        # Collect distinct non-wildcard SANs across the cohort.
        names_set: set[str] = set()
        for _, ns in cluster:
            names_set.update(ns)
        if len(names_set) >= _MIN_BURST_NAMES:
            window_end = cluster[-1][0]
            span = max(int((window_end - window_start).total_seconds()), 0)
            sorted_names = tuple(sorted(names_set)[:_MAX_NAMES_PER_BURST])
            bursts.append(
                CertBurst(
                    window_start=window_start.isoformat(),
                    window_end=window_end.isoformat(),
                    span_seconds=span,
                    names=sorted_names,
                )
            )
            if len(bursts) >= _MAX_BURSTS:
                break
        i = j if j > i else i + 1
    return tuple(bursts)


def build_cert_summary(
    entries: Sequence[Mapping[str, str | int | list[str] | None]],
    now: datetime,
) -> CertSummary | None:
    """Build a CertSummary from certificate metadata entries.

    Each entry should have keys: issuer_id (or issuer_ca_id), issuer_name,
    not_before, not_after. Entries missing required fields are skipped.
    When an entry also carries a ``dns_names`` list (CertSpotter, or
    crt.sh after the SAN-attached payload change), wildcard sibling
    clustering and temporal burst detection both run.

    Args:
        entries: List of cert metadata dicts.
        now: Current UTC datetime for age calculations.

    Returns:
        CertSummary if any valid entries found, None otherwise.
    """
    issuer_ids: set[str] = set()
    issuer_name_counter: Counter[str] = Counter()
    not_before_dates: list[datetime] = []
    cert_meta_count = 0

    for entry in entries:
        issuer_id = entry.get("issuer_id") or entry.get("issuer_ca_id")
        issuer_name = entry.get("issuer_name")
        not_before_raw = entry.get("not_before")
        not_after_raw = entry.get("not_after")

        if issuer_id is None or issuer_name is None or not_before_raw is None or not_after_raw is None:
            continue
        if not isinstance(not_before_raw, str) or not isinstance(not_after_raw, str):
            continue

        try:
            not_before_dt = _parse_iso_datetime(not_before_raw)
            # Validate not_after is also parseable
            _parse_iso_datetime(not_after_raw)
        except (ValueError, TypeError):
            continue

        cert_meta_count += 1
        issuer_ids.add(str(issuer_id))
        # Issuer names are free text from the CT log (attacker-influenceable
        # for a self-logged cert) and render to the terminal under --verbose
        # and into markdown. Unlike SAN names they are not DNS names, so we
        # cannot charset-reject; strip control bytes and bound length.
        issuer_name_counter[issuer_display_name(str(issuer_name))] += 1
        not_before_dates.append(not_before_dt)

    if cert_meta_count == 0 or not not_before_dates:
        return None

    # Make all dates offset-aware for comparison with `now`
    aware_dates = []
    for dt in not_before_dates:
        aware_dt = dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt
        aware_dates.append(aware_dt)

    newest_dt = max(aware_dates)
    oldest_dt = min(aware_dates)
    ninety_days_ago = now - timedelta(days=90)

    wildcard_clusters = _extract_wildcard_sibling_clusters(entries)
    bursts = _detect_deployment_bursts(entries)

    return CertSummary(
        cert_count=cert_meta_count,
        issuer_diversity=len(issuer_ids),
        issuance_velocity=sum(1 for dt in aware_dates if dt >= ninety_days_ago),
        newest_cert_age_days=max((now - newest_dt).days, 0),
        oldest_cert_age_days=max((now - oldest_dt).days, 0),
        top_issuers=tuple(
            name
            for name, _ in sorted(
                issuer_name_counter.items(),
                key=lambda item: (-item[1], item[0]),
            )[:3]
        ),
        wildcard_sibling_clusters=wildcard_clusters,
        deployment_bursts=bursts,
    )


# ── CT payload parsers (pure, no I/O) ───────────────────────────────────


def _extract_crtsh_entries(
    data: list[Any],
) -> tuple[list[str], list[dict[str, str | int | list[str] | None]]]:
    """Pull bounded raw-name and per-cert lists from a crt.sh JSON payload.

    Pure parsing, no I/O. Caps the entries scanned, the SANs per cert, the
    cert-summary entries, and the raw-name list so a large or hostile CT
    history cannot exhaust memory.
    """
    raw_names: list[str] = []
    cert_entries: list[dict[str, str | int | list[str] | None]] = []
    for entry in data[:_MAX_CRTSH_ENTRIES]:
        if not isinstance(entry, dict):
            continue

        name_value = entry.get("name_value", "")
        cert_sans: list[str] = []
        if isinstance(name_value, str):
            # Bound the field before splitting: a single newline-free SAN line could
            # otherwise be the entire (body-capped) response, and _is_safe_san_name
            # scans every character. 256 chars per SAN slot is generous.
            name_value = name_value[: _MAX_SANS_PER_CERT * 256]
            for raw_name in name_value.split("\n", _MAX_SANS_PER_CERT):
                if len(cert_sans) >= _MAX_SANS_PER_CERT:
                    break
                n = raw_name.strip()
                if n and _is_safe_san_name(n):
                    cert_sans.append(n)

        if len(cert_entries) < _MAX_CRTSH_CERT_SUMMARY_ENTRIES:
            cert_entries.append(
                {
                    "issuer_ca_id": entry.get("issuer_ca_id"),
                    "issuer_id": entry.get("issuer_ca_id"),
                    "issuer_name": entry.get("issuer_name"),
                    "not_before": entry.get("not_before"),
                    "not_after": entry.get("not_after"),
                    "dns_names": cert_sans,
                }
            )

        if len(raw_names) >= _MAX_CRTSH_RAW_NAMES:
            continue
        for n in cert_sans:
            raw_names.append(n)
            if len(raw_names) >= _MAX_CRTSH_RAW_NAMES:
                break
    return raw_names, cert_entries


def _parse_certspotter_issuance(
    issuance: Any,
) -> tuple[list[str], dict[str, str | int | list[str] | None] | None, str | None]:
    """Parse one CertSpotter issuance into (safe SAN names, cert entry, id).

    Pure parsing, no I/O. Returns empty / None on a non-mapping issuance so
    the caller can skip it.
    """
    if not isinstance(issuance, dict):
        return [], None, None

    issuance_id = issuance.get("id")
    last_id = str(issuance_id) if isinstance(issuance_id, str | int) else None

    dns_names = issuance.get("dns_names", [])
    cert_sans: list[str] = []
    if isinstance(dns_names, list):
        for name in dns_names:
            if len(cert_sans) >= _MAX_SANS_PER_CERT:
                break
            if isinstance(name, str):
                stripped = name.strip()
                if stripped and _is_safe_san_name(stripped):
                    cert_sans.append(stripped)

    issuer = issuance.get("issuer")
    issuer_name = None
    if isinstance(issuer, dict):
        candidate = issuer.get("friendly_name") or issuer.get("name")
        if isinstance(candidate, str):
            issuer_name = candidate

    cert_entry: dict[str, str | int | list[str] | None] = {
        "issuer_id": issuer_name,
        "issuer_name": issuer_name,
        "not_before": issuance.get("not_before"),
        "not_after": issuance.get("not_after"),
        "dns_names": cert_sans,
    }
    return cert_sans, cert_entry, last_id


# ── CrtshProvider ───────────────────────────────────────────────────────


class CrtshProvider:
    """CertIntelProvider backed by crt.sh certificate transparency logs."""

    @property
    def name(self) -> str:
        return "crt.sh"

    async def query(
        self,
        domain: str,
    ) -> tuple[list[str], CertSummary | None, InfrastructureClusterReport | None]:
        """Query crt.sh for subdomain discovery and cert metadata.

        Raises on any failure so the fallback chain can proceed.
        Gated by the global CT semaphore so corpus-scale batch
        concurrency does not blow past per-IP rate limits.
        """
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        # Adaptive rate limiter. The limiter handles its own breaker
        # and AIMD pacing; on success we mark the call as a probe that
        # passed, on 429 we feed Retry-After back so the limiter slows
        # down. Local-side RateLimited (breaker open, or wait exceeds
        # max_wait_s) raises so the orchestrator falls through to
        # CertSpotter or cache without blocking the run.
        limiter = ct_rate_limiter_crtsh()
        try:
            await limiter.acquire()
        except RateLimited as exc:
            msg = f"crt.sh rate-limited locally for {domain}: {exc}"
            raise httpx.HTTPError(msg) from exc
        async with _get_ct_semaphore(), http_client(timeout=_CT_TIMEOUT, retry_transient=False) as client:
            try:
                resp = await client.get(url)
            except httpx.HTTPError:
                limiter.on_other_failure()
                raise
            if resp.status_code == 429:
                # Server-side rate limit. Feed Retry-After (if any) to
                # the limiter so the next call honors it as a floor.
                # Brief on-call sleep (bounded) for the worst-offender
                # case where Retry-After is small enough to ride out.
                retry_after = _parse_retry_after(resp)
                limiter.on_rate_limited(retry_after_s=retry_after)
                if retry_after is not None and retry_after <= 30.0:
                    await asyncio.sleep(retry_after)
                msg = f"crt.sh rate-limited (HTTP 429) for {domain}"
                raise httpx.HTTPStatusError(msg, request=resp.request, response=resp)
            if resp.status_code != 200:
                limiter.on_other_failure()
                msg = f"crt.sh returned HTTP {resp.status_code} for {domain}"
                raise httpx.HTTPStatusError(msg, request=resp.request, response=resp)
            try:
                data = resp.json()
            except (ValueError, RecursionError) as exc:
                # RecursionError (deeply-nested JSON) is a RuntimeError, not a
                # ValueError, so it bypassed this guard and skipped the limiter
                # update; catch it so the provider degrades like any bad payload.
                limiter.on_other_failure()
                msg = f"crt.sh returned invalid JSON for {domain}"
                raise httpx.HTTPError(msg) from exc
            limiter.on_success()

        if not isinstance(data, list):
            return [], None, None

        # Parse the (bounded) payload into raw names + per-cert entries. Done
        # in _extract_crtsh_entries so the query method stays a thin
        # fetch-then-parse driver.
        raw_names, cert_entries = _extract_crtsh_entries(data)
        subdomains = filter_subdomains(raw_names, domain)

        now = datetime.now(UTC)
        cert_summary = build_cert_summary(cert_entries, now)
        cluster_report = build_infrastructure_clusters(list(cert_entries)) if cert_entries else None

        return subdomains, cert_summary, cluster_report


# ── CertSpotterProvider ─────────────────────────────────────────────────


class CertSpotterProvider:
    """CertIntelProvider backed by the CertSpotter free API.

    Zero API keys, zero credentials. Uses the public unauthenticated endpoint.

    Pagination: CertSpotter returns issuances in pages. Without
    pagination a single request returns ~100 entries for small domains but
    silently truncates on large targets — producing the enrichment
    asymmetry observed on bank-scale domains (one run returned 5 related
    subdomains, another returned 100+). This provider now follows the
    ``after=`` cursor up to ``_MAX_PAGES`` pages, stopping early when
    enough subdomains have been collected or when the API returns an
    empty page.

    Rate limits: CertSpotter's free tier has weekly IP quotas. When the
    API returns a 429 or an empty first page, we stop and return what
    we have. The caller sees a smaller but non-zero result rather than
    a failure.
    """

    _BASE_URL = "https://api.certspotter.com/v1/issuances"
    # Maximum number of pages to fetch. At 8s timeout per page + ~2s of retry
    # backoff, each page can cost up to ~10s, and we hit this cost 5× in
    # parallel under batch concurrency. Dropped from 4 to 2 after validation
    # on a 100-domain corpus showed 10-14% of big-enterprise lookups hitting
    # the 120s aggregate ceiling, usually during CertSpotter pagination.
    # Two pages still cover ~500 certs, which is enough for the subdomain-
    # discovery use case on all but the very largest cert portfolios.
    _MAX_PAGES = 2

    @property
    def name(self) -> str:
        return "certspotter"

    async def _fetch_page(
        self,
        client: httpx.AsyncClient,
        domain: str,
        after_cursor: str | None,
    ) -> httpx.Response:
        """Fetch a single CertSpotter page. No retry decorator — when CertSpotter
        is consistently slow, three 8s ReadTimeouts per page accumulated >25s of
        pure delay and blew the aggregate resolve budget on big enterprises
        (observed during 150-domain validation: 12% timeout rate). Failing
        fast on the first timeout is better than waiting 25s to discover the
        provider is unhealthy — the caller still gets whatever pages
        succeeded. Returns the raw httpx Response so the caller can inspect
        status_code (429 vs 200 vs other)."""
        params: dict[str, str | list[str]] = {
            "domain": domain,
            "include_subdomains": "true",
            "expand": ["dns_names", "issuer"],
        }
        if after_cursor is not None:
            params["after"] = after_cursor
        return await client.get(self._BASE_URL, params=params)

    async def connectivity_probe(self, client: httpx.AsyncClient, domain: str) -> httpx.Response:
        """One unauthenticated first-page request, the same shape lookups use."""
        return await self._fetch_page(client, domain, None)

    async def _fetch_page_with_feedback(
        self,
        client: httpx.AsyncClient,
        domain: str,
        after_cursor: str | None,
        limiter: AdaptiveRateLimiter,
    ) -> httpx.Response:
        """Fetch one page and report terminal transport failure once."""
        try:
            return await self._fetch_page(client, domain, after_cursor)
        except httpx.HTTPError:
            limiter.on_other_failure()
            raise

    @staticmethod
    def _accumulate_issuances(
        data: list[Any],
        all_raw_names: list[str],
        all_cert_entries: list[dict[str, str | int | list[str] | None]],
    ) -> str | None:
        """Accumulate one page's issuances into the running lists, and return the
        last issuance id (the pagination cursor) or None.

        Entry count and aggregate retained SAN count are bounded independently.
        A response can otherwise multiply the per-certificate SAN cap across
        every admitted issuance before the later unique-name check runs.
        """
        last_id: str | None = None
        for issuance in data:
            if len(all_cert_entries) >= _MAX_CRTSH_CERT_SUMMARY_ENTRIES:
                break
            names, cert_entry, issuance_id = _parse_certspotter_issuance(issuance)
            if cert_entry is None:
                continue
            remaining_names = max(_MAX_CRTSH_RAW_NAMES - len(all_raw_names), 0)
            retained_names = names[:remaining_names]
            all_raw_names.extend(retained_names)
            cert_entry["dns_names"] = retained_names
            all_cert_entries.append(cert_entry)
            if issuance_id is not None:
                last_id = issuance_id
        return last_id

    async def query(
        self,
        domain: str,
    ) -> tuple[list[str], CertSummary | None, InfrastructureClusterReport | None]:
        """Query CertSpotter for subdomain discovery and cert metadata.

        Iterates through up to ``_MAX_PAGES`` paginated responses using
        CertSpotter's ``after=<issuance_id>`` cursor. Each page's results
        are accumulated into a single raw-names list before filtering.
        Stops early when a page is empty, when a 429 is returned, or when
        the filtered subdomain count already exceeds ``MAX_SUBDOMAINS``.

        Each page uses one bounded request. Transport, parse, and non-429 HTTP
        failures are reported to the adaptive limiter and raised so the
        provider fallback chain can proceed without multiplying quota pressure.

        Raises on failures (for example HTTP 5xx or a 4xx other than 429) so
        the fallback chain can proceed.
        A 429 response is NOT raised — the provider returns the data
        collected so far (which may be partial) and the caller can decide
        whether that's enough.
        """
        all_raw_names: list[str] = []
        all_cert_entries: list[dict[str, str | int | list[str] | None]] = []
        after_cursor: str | None = None
        # Mark when a 429 truncated this call so the caller
        # can distinguish rate-limit-driven empty results from genuine
        # empty-cert-history responses. The caller (dns.py) uses this
        # signal to mark certspotter as degraded rather than silently
        # treating it as a soft success.
        rate_limited = False

        # Adaptive rate limiter + breaker. Free-tier subdomain queries
        # are 10/day, so the breaker is the real protection: once the
        # daily quota hits, the provider 429s, the limiter slows down
        # and eventually trips the breaker for a cooldown. Subsequent
        # acquires fail fast (RateLimited) and the orchestrator falls
        # through to cache.
        limiter = ct_rate_limiter_certspotter()
        try:
            await limiter.acquire()
        except RateLimited as exc:
            msg = f"CertSpotter rate-limited locally for {domain}: {exc}"
            raise httpx.HTTPError(msg) from exc

        async with _get_ct_semaphore(), http_client(timeout=_CT_TIMEOUT, retry_transient=False) as client:
            for _ in range(self._MAX_PAGES):
                resp = await self._fetch_page_with_feedback(client, domain, after_cursor, limiter)
                if resp.status_code == 429:
                    # Rate-limited. Feed Retry-After (if any) to the
                    # adaptive limiter so its next acquire honors the
                    # server's stated wait. Brief on-call sleep
                    # (bounded) for the cheap-to-ride-out case. Stop
                    # paging and return what we have; the caller sees
                    # partial data when at least one page succeeded.
                    retry_after = _parse_retry_after(resp)
                    limiter.on_rate_limited(retry_after_s=retry_after)
                    if retry_after is not None and retry_after <= 30.0:
                        await asyncio.sleep(retry_after)
                    rate_limited = True
                    break
                if resp.status_code != 200:
                    limiter.on_other_failure()
                    msg = f"CertSpotter returned HTTP {resp.status_code} for {domain}"
                    raise httpx.HTTPStatusError(msg, request=resp.request, response=resp)
                try:
                    data = resp.json()
                except (ValueError, RecursionError) as exc:
                    # RecursionError (deeply-nested JSON) is a RuntimeError, not a
                    # ValueError; catch it so a hostile payload degrades cleanly.
                    limiter.on_other_failure()
                    msg = f"CertSpotter returned invalid JSON for {domain}"
                    raise httpx.HTTPError(msg) from exc
                # Got a parseable 200; mark the limiter healthy so AIMD
                # speeds the next call slightly.
                limiter.on_success()
                if not isinstance(data, list) or not data:
                    # Empty page. We've reached the end of the issuance
                    # list (genuine empty success, not rate-limited).
                    break

                # Accumulate this page's issuances (entry-count capped) via the
                # helper so this method stays a thin pagination driver.
                last_id = self._accumulate_issuances(data, all_raw_names, all_cert_entries)

                # If we already have enough unique candidate names to
                # fill MAX_SUBDOMAINS after filtering, or have hit the entry
                # cap, stop early. No point paying for more pages.
                if (
                    len(set(all_raw_names)) >= MAX_SUBDOMAINS * 2
                    or len(all_raw_names) >= _MAX_CRTSH_RAW_NAMES
                    or len(all_cert_entries) >= _MAX_CRTSH_CERT_SUMMARY_ENTRIES
                ):
                    break

                # Advance the cursor. If the response didn't include
                # ids we can't paginate any further.
                if last_id is None:
                    break
                after_cursor = last_id

        if not all_raw_names and not all_cert_entries:
            # Rate-limit-driven empty result raises so the
            # orchestrator marks the provider as degraded. Without
            # this, dns.py treats the empty tuple as a soft success
            # (continue, do not record degradation), and the panel
            # claims "no certspotter data" rather than "certspotter
            # was rate-limited."
            if rate_limited:
                msg = f"CertSpotter rate-limited (HTTP 429) for {domain}"
                raise httpx.HTTPError(msg)
            return [], None, None

        subdomains = filter_subdomains(all_raw_names, domain)
        now = datetime.now(UTC)
        cert_summary = build_cert_summary(all_cert_entries, now)
        cluster_report = build_infrastructure_clusters(list(all_cert_entries)) if all_cert_entries else None
        if rate_limited:
            # Partial pages under 429 must not look like a complete CT view.
            raise CertProviderPartialRateLimit(
                subdomains,
                cert_summary,
                cluster_report,
                self.name,
            )
        return subdomains, cert_summary, cluster_report
