"""Evidence-scoped normalization for the panel's compact Email service row."""

from __future__ import annotations

from recon_tool.collection_view import collection_observable_evidence
from recon_tool.constants import SVC_DKIM, SVC_DKIM_EXCHANGE, SVC_DKIM_GOOGLE
from recon_tool.email_security import observed_email_control_services
from recon_tool.formatter.classify import evidence_role_service_label
from recon_tool.merger_tables import GATEWAY_SLUG_NAMES, GATEWAY_SLUGS
from recon_tool.models import EvidenceRecord, TenantInfo

_EMAIL_NOISE = frozenset(
    {
        "DKIM",
        "DKIM (Exchange Online)",
        "DMARC",
        "MTA-STS",
        "BIMI",
        "TLS-RPT",
        "Exchange Autodiscover",
        "Microsoft 365",
        "Google Workspace",
        "Exchange-style endpoint indicator",
        "Custom or unclassified MX",
        "Null MX (domain does not accept email)",
    }
)
_FALLBACK_PROVIDERS = ("Microsoft 365", "Google Workspace", "Zoho Mail", "ProtonMail", "AWS SES")


def _append_unique(summary: list[str], value: str | None) -> None:
    """Append a nonempty value once while preserving discovery order."""
    if value and value not in summary:
        summary.append(value)


def _email_summary_providers(
    info: TenantInfo,
    service_set: set[str],
    evidence: tuple[EvidenceRecord, ...],
    summary: list[str],
) -> None:
    """Order observed delivery paths before hedged downstream indicators."""
    ordered_services = sorted(service_set)

    def _add_list(value: str | None, *, hedge: bool = False) -> None:
        for raw_part in (value or "").split(" + "):
            part = raw_part.strip()
            if not part:
                continue
            label = next((item for item in ordered_services if item == part or item.startswith(f"{part} (")), part)
            if hedge and label == part and part not in service_set:
                label = f"{part} (possible downstream indicator)"
            elif label == part:
                supporting = tuple(
                    record
                    for record in evidence
                    if record.rule_name.casefold() == part.casefold() or GATEWAY_SLUG_NAMES.get(record.slug) == part
                )
                label = evidence_role_service_label(part, supporting)
            _append_unique(summary, label)

    if info.primary_email_provider:
        _add_list(info.primary_email_provider)
        _add_list(info.email_gateway)
    else:
        _add_list(info.email_gateway)
        _add_list(info.likely_primary_email_provider, hedge=True)
    if summary:
        return
    for provider in _FALLBACK_PROVIDERS:
        label = next(
            (item for item in ordered_services if item == provider or item.startswith(f"{provider} (")),
            None,
        )
        _append_unique(summary, label)


def _email_summary_controls(
    info: TenantInfo,
    service_set: set[str],
    email_services: list[str],
    evidence: tuple[EvidenceRecord, ...],
    summary: list[str],
) -> None:
    """Append compact observations for the primary email controls."""
    if info.dmarc_policy:
        _append_unique(summary, f"DMARC {info.dmarc_policy}")
    elif "DMARC" in service_set:
        _append_unique(summary, "DMARC")

    observed = observed_email_control_services(evidence)
    qualified = [label for label in (SVC_DKIM_EXCHANGE, SVC_DKIM_GOOGLE) if label in observed]
    if qualified:
        summary.extend(qualified)
    elif SVC_DKIM in observed or SVC_DKIM in service_set:
        _append_unique(summary, SVC_DKIM)

    if any(service.startswith("SPF: strict") for service in email_services):
        _append_unique(summary, "SPF strict")
    elif any(service.startswith("SPF: softfail") for service in email_services):
        _append_unique(summary, "SPF softfail")
    elif "SPF record observed" in service_set:
        # A live +all / ?all / no-all policy is not a scored control, but
        # hiding it made the compact row look like SPF was never collected.
        _append_unique(summary, "SPF observed")

    if info.mta_sts_mode and info.mta_sts_mode != "none":
        _append_unique(summary, f"MTA-STS {info.mta_sts_mode}")
    elif "MTA-STS" in service_set and info.mta_sts_mode != "none":
        # RFC 8461 mode "none" means the policy is not in effect. The TXT
        # still adds the MTA-STS service label; do not list it as a live
        # control next to DMARC / SPF when the fetched policy is off.
        _append_unique(summary, "MTA-STS")

    if "BIMI" in service_set:
        _append_unique(summary, "BIMI")


def _compact_email_summary(
    info: TenantInfo,
    email_services: list[str],
    evidence: tuple[EvidenceRecord, ...],
) -> list[str]:
    """Build the evidence-scoped Email core retained by every panel mode."""
    service_set = set(email_services)
    summary: list[str] = []
    _email_summary_providers(info, service_set, evidence, summary)
    _email_summary_controls(info, service_set, email_services, evidence, summary)
    return summary


def normalize_email_services(categorized: dict[str, list[str]], info: TenantInfo) -> None:
    """Lead with compact Email facts, then append remaining indicators."""
    original_email = list(categorized["Email"])
    evidence = collection_observable_evidence(info)
    gateway_names = {
        record.rule_name for record in evidence if record.source_type.upper() == "MX" and record.slug in GATEWAY_SLUGS
    }
    noise = _EMAIL_NOISE | gateway_names
    remaining = [
        service
        for service in original_email
        if not any(service == item or service.startswith(f"{item} (") for item in noise)
        and not service.startswith("SPF")
    ]
    email_summary = _compact_email_summary(info, original_email, evidence)
    for service in remaining:
        _append_unique(email_summary, service)
    if email_summary:
        categorized["Email"] = email_summary
    else:
        del categorized["Email"]
