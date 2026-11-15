"""Collection-aware hardening display status and retained declaration proofs."""

from __future__ import annotations

from dataclasses import replace

from recon_tool import exposure_gaps as gap_detection
from recon_tool import exposure_observability as observability
from recon_tool.constants import SVC_BIMI, SVC_DKIM, SVC_DKIM_EXCHANGE, SVC_DKIM_GOOGLE
from recon_tool.email_applicability import MailApplicability, mail_applicability
from recon_tool.email_security import observed_email_control_services
from recon_tool.exposure_copy import build_evidence_refs as _build_evidence_refs
from recon_tool.exposure_copy import evidence_refs
from recon_tool.exposure_copy import evidence_slugs as _evidence_slugs
from recon_tool.exposure_models import HardeningControl, HardeningStatus
from recon_tool.models import TenantInfo


def _dmarc_hardening_control(info: TenantInfo, *, dmarc_available: bool, slugs: set[str]) -> HardeningControl:
    """Credit DMARC only when the effective policy enforces.

    A published ``p=none`` record, and a stricter ``p=`` whose ``pct`` or
    ``t=y`` testing mode leaves the effective level at none, is monitoring.
    Quarantine and reject after that step still count. The published policy
    stays visible in the detail either way.
    """
    effective = gap_detection.effective_email_dmarc_policy(info)
    published = info.dmarc_policy
    if not dmarc_available:
        detail = "source unavailable"
    elif published is None:
        detail = "not configured"
    elif published == "none":
        detail = "policy set to none (monitoring only, not enforcing)"
    elif effective is not None and effective != published:
        detail = f"{published} (effective {effective})"
    else:
        detail = published
    observed = dmarc_available and published is not None
    present = dmarc_available and effective in {"quarantine", "reject"}
    return HardeningControl(
        name="DMARC",
        present=present,
        detail=detail,
        evidence=_build_evidence_refs(info, {"dmarc"} & slugs) if observed else (),
    )


def compute_hardening_status(info: TenantInfo, *, applicability: MailApplicability | None = None) -> HardeningStatus:
    """Derive hardening control status from TenantInfo."""
    observed = observability.ObservableEmailState.from_info(info)
    services_set = observed_email_control_services(info.evidence)
    slugs_set = set(info.slugs)
    controls: list[HardeningControl] = [
        _dmarc_hardening_control(info, dmarc_available=observed.dmarc_available, slugs=slugs_set)
    ]

    # DKIM
    dkim_available = observed.dkim_available
    dkim_present = dkim_available and bool(services_set & {SVC_DKIM, SVC_DKIM_EXCHANGE, SVC_DKIM_GOOGLE})
    controls.append(
        HardeningControl(
            name="DKIM",
            present=dkim_present,
            detail=("configured" if dkim_present else "not observed at recon's bounded common-selector set")
            if dkim_available
            else "source unavailable",
            evidence=(_build_evidence_refs(info, _evidence_slugs(info, frozenset({"DKIM"}))) if dkim_present else ()),
        )
    )

    # MTA-STS. RFC 8461 defines mode "none" as "policy not in effect": the
    # record was observed, but it may not be credited as a present control.
    mta_available = observed.mta_sts_available
    mta_declared_off = mta_available and info.mta_sts_mode == "none"
    mta_present = mta_available and info.mta_sts_mode is not None and not mta_declared_off
    if not mta_available:
        mta_detail = "source unavailable"
    elif mta_declared_off:
        mta_detail = "policy published with mode none (not in effect)"
    else:
        mta_detail = info.mta_sts_mode or "not configured"
    controls.append(
        HardeningControl(
            name="MTA-STS",
            present=mta_present,
            detail=mta_detail,
            evidence=_build_evidence_refs(info, {"mta-sts", "mta-sts-enforce"} & slugs_set)
            if mta_present or mta_declared_off
            else (),
        )
    )

    # BIMI
    bimi_available = observed.bimi_available
    bimi_present = bimi_available and SVC_BIMI in services_set
    controls.append(
        HardeningControl(
            name="BIMI",
            present=bimi_present,
            detail=("configured" if bimi_present else "not configured") if bimi_available else "source unavailable",
            evidence=_build_evidence_refs(info, {"bimi"} & slugs_set) if bimi_present else (),
        )
    )

    # TLS-RPT
    tls_rpt_available = observed.tls_rpt_available
    tls_rpt_present = tls_rpt_available and "tls-rpt" in slugs_set
    controls.append(
        HardeningControl(
            name="TLS-RPT",
            present=tls_rpt_present,
            detail=("configured" if tls_rpt_present else "not configured")
            if tls_rpt_available
            else "source unavailable",
            evidence=_build_evidence_refs(info, {"tls-rpt"}) if tls_rpt_present else (),
        )
    )

    # CAA records
    caa_available = observed.caa_available
    caa_evidence_slugs = _evidence_slugs(info, frozenset({"CAA"}))
    caa_present = caa_available and bool(caa_evidence_slugs)
    controls.append(
        HardeningControl(
            name="CAA",
            present=caa_present,
            detail=("configured" if caa_present else "not configured") if caa_available else "source unavailable",
            evidence=_build_evidence_refs(info, caa_evidence_slugs) if caa_present else (),
        )
    )

    applicability = mail_applicability(info) if applicability is None else applicability
    projected: list[HardeningControl] = []
    for control in controls:
        projected_control = control
        proof = applicability.evidence_for(control.name)
        if proof:
            basis = (
                "Null MX, SPF deny-all and enforcing DMARC declared"
                if control.name in {"DKIM", "BIMI"}
                else "sole Null MX declared"
            )
            projected_control = replace(
                control,
                detail=f"not applicable: {basis}",
                evidence=tuple(dict.fromkeys((*control.evidence, *evidence_refs(proof)))),
            )
        projected.append(projected_control)
    return HardeningStatus(controls=tuple(projected))
