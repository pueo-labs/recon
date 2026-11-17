"""Shared collection-status meaning for human lookup renderers.

The panel and Markdown surfaces keep their own layout and wording, but they
must agree on what a degraded marker means. This projection separates core
source failures from certificate-transparency fallback and cache states without
creating a new public output contract.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

from recon_tool.confidence import is_confidence_contributor
from recon_tool.models import ConfidenceLevel, SourceResult, TenantInfo
from recon_tool.source_status import CT_PROVIDER_MARKERS, PUBLIC_ENDPOINT_PRIVATE_ADDRESS

_CT_SOURCES = CT_PROVIDER_MARKERS
# Whole-source markers for each default lookup source. The opt-in Google CSE
# probe is excluded because it is not attempted by default.
_WHOLE_SOURCE_MARKERS: tuple[frozenset[str], ...] = (
    frozenset({"dns_records", "dns"}),
    frozenset({"source:oidc_discovery", "oidc_discovery"}),
    frozenset({"source:user_realm", "user_realm"}),
    frozenset({"source:google_identity", "google_identity"}),
)
CTCollectionState = Literal["none", "fallback_recovered", "cache_recovered", "unavailable"]
SourceDisplayState = Literal["match", "no_match", "unavailable"]

# Legacy collectors retain expected negative responses in the error field.
# Explicit unavailability takes precedence over these compatibility markers.
_SOFT_MISS_MARKERS = (
    "No Google Workspace",
    "No federated IdP redirect",
    "Not a Google Workspace",
    "No M365 tenant",
    "Not a registered M365",
    "HTTP 400 from OIDC discovery",
    "No information could be resolved",
    "no data returned",
)


def source_display_state(result: SourceResult) -> SourceDisplayState:
    """Use one match, clean non-match, or unavailable state in source views."""
    if result.source_unavailable:
        return "unavailable"
    if is_confidence_contributor(result):
        return "match"
    if not result.error or any(marker in result.error for marker in _SOFT_MISS_MARKERS):
        return "no_match"
    return "unavailable"


# One wording for every human surface (panel, --plain, --md, MCP text). It
# reports the resolver's response class for the queried name, nothing more:
# NXDOMAIN is a clean observed-empty answer, not authenticated denial.
NAME_NXDOMAIN_STATEMENT = "No DNS name: the resolver returned NXDOMAIN for this domain."


def name_nxdomain_statement(info: TenantInfo) -> str | None:
    """Return the shared nonexistence statement only for an observed NXDOMAIN."""
    return NAME_NXDOMAIN_STATEMENT if info.dns_name_status == "nxdomain" else None


def low_confidence_guidance(info: TenantInfo, *, detailed: bool) -> str | None:
    """Point a sparse CLI briefing at diagnostics, unless already requested."""
    if info.confidence != ConfidenceLevel.LOW or detailed:
        return None
    return "Use --explain to inspect evidence or --verbose to review source status."


@dataclass(frozen=True)
class CollectionStatusProjection:
    """Renderer-neutral interpretation of lookup collection degradation."""

    unavailable_sources: tuple[str, ...]
    ct_sources: tuple[str, ...]
    ct_state: CTCollectionState
    ct_cache_age_days: int | None
    ct_subdomain_count: int
    # True only when every default lookup source (DNS, OIDC discovery,
    # GetUserRealm, Google identity routing) is marked unavailable and nothing
    # was observed or recovered, so the note can say "All N" instead of "N".
    all_sources_unavailable: bool = False

    resolver_note: str | None = None

    @property
    def is_warning(self) -> bool:
        """Return whether the projected state includes incomplete collection."""
        return bool(self.resolver_note or self.unavailable_sources) or self.ct_state == "unavailable"


def project_collection_status(info: TenantInfo) -> CollectionStatusProjection:
    """Classify degraded markers without assigning renderer-specific prose."""
    unavailable_sources = tuple(
        source
        for source in info.degraded_sources
        if source not in _CT_SOURCES and source != PUBLIC_ENDPOINT_PRIVATE_ADDRESS
    )
    ct_sources = tuple(source for source in info.degraded_sources if source in _CT_SOURCES)

    ct_state: CTCollectionState = "none"
    if ct_sources:
        if info.ct_provider_used is None:
            ct_state = "unavailable"
        elif info.ct_cache_age_days is not None and info.ct_subdomain_count > 0:
            ct_state = "cache_recovered"
        elif info.ct_subdomain_count > 0 or (info.cert_summary is not None and info.cert_summary.cert_count > 0):
            ct_state = "fallback_recovered"
        else:
            ct_state = "unavailable"

    degraded = frozenset(info.degraded_sources)
    all_sources_unavailable = (
        all(not degraded.isdisjoint(markers) for markers in _WHOLE_SOURCE_MARKERS)
        and info.tenant_id is None
        and not info.services
        and ct_state in {"none", "unavailable"}
    )

    return CollectionStatusProjection(
        unavailable_sources=unavailable_sources,
        ct_sources=ct_sources,
        ct_state=ct_state,
        ct_cache_age_days=info.ct_cache_age_days,
        ct_subdomain_count=info.ct_subdomain_count,
        all_sources_unavailable=all_sources_unavailable,
        resolver_note=(
            "The resolver returned a private or reserved address for a public service. "
            "Related domains may be artifacts. Run recon doctor"
            if PUBLIC_ENDPOINT_PRIVATE_ADDRESS in degraded
            else None
        ),
    )


def unavailable_sources_phrase(
    status: CollectionStatusProjection,
    *,
    verb: str = "",
    escape: Callable[[str], str] | None = None,
) -> str | None:
    """Name unavailable sources with an honest quantifier, or None when none are.

    ``verb`` lets a renderer keep its own grammar ("were" in Markdown prose),
    and ``escape`` applies a renderer's escaping to each source marker only.
    """
    if not status.unavailable_sources:
        return None
    listed = ", ".join(escape(source) if escape else source for source in status.unavailable_sources)
    count = len(status.unavailable_sources)
    if count == 1:
        infix = " was" if verb == "were" else (f" {verb}" if verb else "")
        return f"1 source{infix} unavailable ({listed})"
    infix = f" {verb}" if verb else ""
    quantifier = "All " if status.all_sources_unavailable else ""
    return f"{quantifier}{count} sources{infix} unavailable ({listed})"


def collection_note_parts(status: CollectionStatusProjection) -> tuple[str, ...]:
    """Compact material caveats shared by the panel and its linear view."""
    parts: list[str] = []
    sources_phrase = unavailable_sources_phrase(status)
    if sources_phrase is not None:
        parts.append(sources_phrase)
    if status.ct_state == "unavailable":
        parts.append(f"All CT providers unavailable ({', '.join(status.ct_sources)})")
    elif status.ct_state == "cache_recovered":
        age = status.ct_cache_age_days
        age_str = "today" if age == 0 else f"{age} day{'s' if age != 1 else ''} old"
        parts.append(f"CT: from local cache, {age_str} ({status.ct_subdomain_count} subdomains)")
    if status.resolver_note:
        parts.append(status.resolver_note)
    return tuple(parts)


def cache_age_label(age_seconds: float) -> str:
    """Return a compact, readable cache age without false precision."""
    if age_seconds < 60:
        return "under 1 minute"
    if age_seconds < 3600:
        minutes = int(age_seconds // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    if age_seconds < 86400:
        hours = int(age_seconds // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''}"
    days = int(age_seconds // 86400)
    return f"{days} day{'s' if days != 1 else ''}"


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


def cache_reuse_note(info: TenantInfo, *, now: datetime | None = None) -> str | None:
    """Name a reused result-cache collection, or return ``None`` for a fresh one.

    ``cached_at`` is stamped only by the result-cache read path, so its presence
    is the reuse fact. The age comes from ``resolved_at``, the original
    collection time, with ``cached_at`` as the fallback. Collection notes on a
    reused result describe that earlier collection, which this line makes
    explicit. Neither timestamp enters the stable lookup JSON.
    """
    if info.cached_at is None:
        return None
    collected = _parse_timestamp(info.resolved_at) or _parse_timestamp(info.cached_at)
    if collected is None:
        when = "an earlier collection"
    else:
        reference = now if now is not None else datetime.now(UTC)
        when = f"{cache_age_label(max(0.0, (reference - collected).total_seconds()))} ago"
    return f"Cached result from {when}. Use --no-cache to collect again."
