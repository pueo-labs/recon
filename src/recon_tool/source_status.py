"""Central interpretation of collector degradation markers.

The strings in ``TenantInfo.degraded_sources`` describe unavailable
observation channels. They are collection provenance, not negative domain
evidence. This module keeps whole-source, granular resolver, HTTP, and detector
markers consistent across inference and reporting consumers.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal, TypeAlias

ObservationChannel: TypeAlias = Literal[
    "dmarc",
    "dkim",
    "mta_sts",
    "bimi",
    "tls_rpt",
    "apex_txt",
    "mx",
    "caa",
    "ns",
    "cname",
    "a",
    "subdomain_txt",
    "dmarc_rua",
    "srv",
]

PUBLIC_ENDPOINT_PRIVATE_ADDRESS = "resolver:public_endpoint_private_address"

_WHOLE_DNS_MARKERS = frozenset({"dns", "dns_records"})
_CHANNEL_MARKERS: dict[ObservationChannel, frozenset[str]] = {
    "dmarc": frozenset({"dns:dmarc", "detector:email_security"}),
    "dkim": frozenset({"dns:dkim", "detector:dkim"}),
    "mta_sts": frozenset({"dns:mta_sts", "http:mta_sts_policy", "detector:email_security"}),
    "bimi": frozenset({"dns:bimi", "detector:email_security"}),
    "tls_rpt": frozenset({"dns:tls_rpt", "detector:email_security"}),
    "apex_txt": frozenset({"dns:apex_txt", "detector:txt"}),
    "mx": frozenset({"dns:mx", "detector:mx"}),
    "caa": frozenset({"dns:caa", "detector:caa"}),
    "ns": frozenset({"dns:ns", "detector:ns"}),
    "cname": frozenset(
        {
            "dns:cname",
            "detector:cname",
            "detector:cname_infra",
            "detector:m365_cnames",
            "detector:gws_cnames",
            "detector:domain_connect",
            "detector:common_subdomains",
            "detector:idp_hub",
            "detector:exchange_endpoints",
        }
    ),
    "a": frozenset(
        {
            "dns:a",
            "detector:a",
            "detector:hosting_a_record",
            "detector:idp_hub",
            "detector:exchange_endpoints",
        }
    ),
    "subdomain_txt": frozenset({"dns:subdomain_txt", "detector:subdomain_txt"}),
    "dmarc_rua": frozenset({"dns:dmarc_rua", "detector:dmarc_rua"}),
    "srv": frozenset({"dns:srv", "detector:srv", "detector:m365_cnames"}),
}


@dataclass(frozen=True, slots=True)
class SourceStatus:
    """Normalized availability for public observation channels."""

    degraded_sources: frozenset[str]

    @classmethod
    def from_degraded_sources(cls, degraded_sources: Iterable[object] | None) -> SourceStatus:
        """Normalize markers while tolerating external or legacy input."""
        if degraded_sources is None:
            return cls(frozenset())
        if isinstance(degraded_sources, str):
            return cls(frozenset({degraded_sources}))
        return cls(frozenset(source for source in degraded_sources if isinstance(source, str)))

    @property
    def whole_dns_unavailable(self) -> bool:
        """Whether the DNS source as a whole failed."""
        return not self.degraded_sources.isdisjoint(_WHOLE_DNS_MARKERS)

    def channel_available(self, channel: ObservationChannel) -> bool:
        """Return false when either the whole source or this channel failed."""
        return not self.whole_dns_unavailable and self.degraded_sources.isdisjoint(_CHANNEL_MARKERS[channel])

    def channel_unavailable(self, channel: ObservationChannel) -> bool:
        """Return true when the requested channel could not be observed."""
        return not self.channel_available(channel)

    @property
    def unavailable_channels(self) -> frozenset[ObservationChannel]:
        """Return every known channel made unavailable by the markers."""
        return frozenset(channel for channel in _CHANNEL_MARKERS if self.channel_unavailable(channel))


CT_PROVIDER_MARKERS = frozenset({"crt.sh", "certspotter"})
"""Markers for certificate-transparency providers, which have their own fallback chain."""


def collection_incomplete(degraded_sources: Iterable[object] | None, *, ct_provider_used: str | None) -> bool:
    """Return whether degraded markers record a collection failure.

    Every non-CT marker records an unavailable collector or channel. A CT
    provider marker is routine when another provider, a partial page, or the
    separate CT cache still supplied the CT channel (``ct_provider_used`` is
    set); it records a failure only when no CT path recovered. Sparse and
    observed-empty results carry no marker, so this rule never rejects them.
    """
    markers = SourceStatus.from_degraded_sources(degraded_sources).degraded_sources
    if any(marker not in CT_PROVIDER_MARKERS for marker in markers):
        return True
    return bool(markers) and ct_provider_used is None
