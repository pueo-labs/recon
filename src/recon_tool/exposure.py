"""Pure defensive exposure assessment over resolved TenantInfo data.

Generated prose must stay neutral and hedged. The terminology guard is a
copy-style lint for recon-authored text, not an input blocklist.
"""

from __future__ import annotations

import logging

from recon_tool import exposure_gaps as gap_detection
from recon_tool import exposure_observability as observability
from recon_tool.constants import (
    SVC_BIMI,
    SVC_DKIM,
    SVC_DKIM_EXCHANGE,
    SVC_DKIM_GOOGLE,
    SVC_SPF_STRICT,
)
from recon_tool.email_applicability import MailApplicability, mail_applicability
from recon_tool.email_security import observed_email_control_services
from recon_tool.exposure_comparison import build_metrics
from recon_tool.exposure_copy import EXPOSURE_DISCOURAGED_COPY_TERMS
from recon_tool.exposure_copy import build_evidence_refs as _build_evidence_refs
from recon_tool.exposure_copy import check_neutral_copy as _check_neutral_copy
from recon_tool.exposure_copy import evidence_slugs as _evidence_slugs
from recon_tool.exposure_hardening import compute_hardening_status as _compute_hardening_status
from recon_tool.exposure_models import (
    ConsistencyObservation,
    EmailPosture,
    EvidenceReference,
    ExposureAssessment,
    GapReport,
    HardeningGap,
    IdentityPosture,
    InfrastructureFootprint,
    PostureComparison,
    PostureDifference,
    RelativeAssessment,
)
from recon_tool.exposure_models import (
    HardeningControl as HardeningControl,
)
from recon_tool.exposure_models import (
    HardeningStatus as HardeningStatus,
)
from recon_tool.exposure_scoring import compute_exposure_index
from recon_tool.models import TenantInfo

logger = logging.getLogger(__name__)

# Backward-compatible alias for callers that imported the old internal name.
_EMAIL_GATEWAY_SLUGS = gap_detection.EMAIL_GATEWAY_SLUGS

# ── Neutral-language copy terms ─────────────────────────────────────────

# Backward-compatible alias for older tests or callers that imported the old internal name.
EXPOSURE_BANNED_TERMS = EXPOSURE_DISCOURAGED_COPY_TERMS


# ── Slug classification maps ───────────────────────────────────────────

_CLOUD_PROVIDER_SLUGS: dict[str, str] = {
    "aws-route53": "AWS",
    "aws-cloudfront": "AWS",
    "aws-elb": "AWS",
    "aws-s3": "AWS",
    "azure-dns": "Azure",
    "azure-cdn": "Azure",
    "azure-appservice": "Azure",
    "azure-fd": "Azure",
    "gcp-dns": "GCP",
    "gcp-app": "GCP",
}

_CDN_WAF_SLUGS: dict[str, str] = {
    "cloudflare": "Cloudflare",
    "akamai": "Akamai",
    "fastly": "Fastly",
    "imperva": "Imperva",
}

_DNS_PROVIDER_SLUGS: dict[str, str] = {
    "aws-route53": "AWS Route 53",
    "azure-dns": "Azure DNS",
    "gcp-dns": "Google Cloud DNS",
    "cloudflare": "Cloudflare",
}

_CA_SLUGS: dict[str, str] = {
    "letsencrypt": "Let's Encrypt",
    "digicert": "DigiCert",
    "sectigo": "Sectigo",
    "aws-acm": "Amazon",
    "google-trust": "Google Trust",
    "globalsign": "GlobalSign",
}


# ── Helper functions ───────────────────────────────────────────────────


def _compute_email_security_score(info: TenantInfo) -> int:
    """Email-security score (0-5); see ``constants.email_security_score`` for the definition."""
    return observability.ObservableEmailState.from_info(info).security_score


def _compute_email_posture(info: TenantInfo) -> EmailPosture:
    """Derive email security posture from TenantInfo."""
    observed = observability.ObservableEmailState.from_info(info)
    services_set = observed_email_control_services(info.evidence)
    slugs_set = set(info.slugs)
    dmarc_policy = observed.dmarc_policy
    mta_sts_mode = observed.mta_sts_mode

    dkim_configured = observed.dkim_available and (
        SVC_DKIM in services_set or SVC_DKIM_EXCHANGE in services_set or SVC_DKIM_GOOGLE in services_set
    )
    spf_strict = observed.spf_available and SVC_SPF_STRICT in services_set
    bimi_configured = observed.bimi_available and SVC_BIMI in services_set

    # ``email_gateway`` is set only from the MX topology path. A generic
    # vendor-verification slug is an indicator, not routing evidence.
    mx_gateway_slugs = _evidence_slugs(info, frozenset({"MX"})) & set(_EMAIL_GATEWAY_SLUGS)
    gateway = info.email_gateway if observed.gateway_available and mx_gateway_slugs else None

    # Collect relevant slugs for evidence
    relevant_slugs: set[str] = set()
    if dmarc_policy is not None:
        relevant_slugs.add("dmarc")
    if dkim_configured:
        relevant_slugs.update(_evidence_slugs(info, frozenset({"DKIM"})))
    if spf_strict:
        relevant_slugs.add("spf-strict")
    if bimi_configured:
        relevant_slugs.add("bimi")
    if mta_sts_mode is not None:
        relevant_slugs.add("mta-sts")
        if mta_sts_mode == "enforce":
            relevant_slugs.add("mta-sts-enforce")
    if gateway:
        relevant_slugs.update(mx_gateway_slugs)
    # Also include any TLS-RPT evidence
    if "tls-rpt" in slugs_set:
        relevant_slugs.add("tls-rpt")

    evidence = _build_evidence_refs(info, relevant_slugs)

    return EmailPosture(
        dmarc_policy=dmarc_policy,
        dkim_configured=dkim_configured,
        spf_strict=spf_strict,
        mta_sts_mode=mta_sts_mode,
        email_gateway=gateway,
        bimi_configured=bimi_configured,
        email_security_score=_compute_email_security_score(info),
        evidence=evidence,
    )


def _compute_identity_posture(info: TenantInfo) -> IdentityPosture:
    """Derive identity posture from TenantInfo."""
    # A vendor TXT token does not establish the operating IdP. The only
    # currently retained named route is Google's explicit federation response.
    idp = info.google_idp_name

    relevant_slugs: set[str] = set()
    if idp:
        relevant_slugs.add("google-workspace")
    if info.auth_type == "Federated":
        relevant_slugs.add("microsoft365")
    if info.google_auth_type is not None:
        relevant_slugs.add("google-workspace")

    evidence = _build_evidence_refs(info, relevant_slugs)

    return IdentityPosture(
        auth_type=info.auth_type,
        identity_provider=idp,
        google_auth_type=info.google_auth_type,
        google_idp_name=info.google_idp_name,
        evidence=evidence,
    )


def _compute_infrastructure_footprint(info: TenantInfo) -> InfrastructureFootprint:
    """Derive infrastructure footprint from TenantInfo."""
    cname_slugs = _evidence_slugs(info, frozenset({"CNAME"}))
    ns_slugs = _evidence_slugs(info, frozenset({"NS"}))
    caa_slugs = _evidence_slugs(info, frozenset({"CAA"}))

    # Cloud providers (deduplicated by provider name)
    cloud_names: set[str] = set()
    for slug, name in _CLOUD_PROVIDER_SLUGS.items():
        if slug in cname_slugs:
            cloud_names.add(name)
    cloud_providers = tuple(sorted(cloud_names))

    # DNS provider
    dns_provider: str | None = None
    for slug, name in _DNS_PROVIDER_SLUGS.items():
        if slug in ns_slugs:
            dns_provider = name
            break

    # CDN/WAF
    cdn_names: list[str] = []
    for slug, name in _CDN_WAF_SLUGS.items():
        if slug in cname_slugs:
            cdn_names.append(name)
    cdn_waf = tuple(sorted(cdn_names))

    # Certificate authorities
    ca_names: list[str] = []
    for slug, name in _CA_SLUGS.items():
        if slug in caa_slugs:
            ca_names.append(name)
    certificate_authorities = tuple(sorted(ca_names))

    # Evidence from all infrastructure slugs
    relevant_slugs = (
        (cname_slugs & (set(_CLOUD_PROVIDER_SLUGS) | set(_CDN_WAF_SLUGS)))
        | (ns_slugs & set(_DNS_PROVIDER_SLUGS))
        | (caa_slugs & set(_CA_SLUGS))
    )
    evidence = _build_evidence_refs(info, relevant_slugs)

    return InfrastructureFootprint(
        cloud_providers=cloud_providers,
        dns_provider=dns_provider,
        cdn_waf=cdn_waf,
        certificate_authorities=certificate_authorities,
        evidence=evidence,
    )


def _compute_consistency_observations(info: TenantInfo) -> tuple[ConsistencyObservation, ...]:
    """Derive configuration consistency observations from TenantInfo."""
    observations: list[ConsistencyObservation] = []

    # Only MX records establish simultaneous delivery paths. Account or
    # verification indicators alone do not establish active mail service.
    mx_slugs = _evidence_slugs(info, frozenset({"MX"}))
    has_exchange = "microsoft365" in mx_slugs
    has_google = "google-workspace" in mx_slugs
    if has_exchange and has_google:
        obs = _check_neutral_copy("MX records reference both Microsoft 365 and Google Workspace delivery paths")
        evidence = _build_evidence_refs(info, {"microsoft365", "google-workspace"} & mx_slugs)
        observations.append(ConsistencyObservation(observation=obs, category="dual_provider", evidence=evidence))

    return tuple(observations)


# ── Public API: assess_exposure_from_info ──────────────────────────────

_ASSESSMENT_DISCLAIMER = (
    "This assessment identifies the publicly observable security configuration "
    "of the domain. It is intended for defensive review, vendor due diligence, "
    "and security architecture planning."
)


def assess_exposure_from_info(
    info: TenantInfo,
    *,
    hypothetical_components: frozenset[str] = frozenset(),
    applicability: MailApplicability | None = None,
) -> ExposureAssessment:
    """Assess a domain's publicly observable security posture.

    Pure function: TenantInfo in, ExposureAssessment out. No I/O.
    """
    from recon_tool.collection_view import collection_claim_info

    applicability = mail_applicability(info) if applicability is None else applicability
    source_info = info
    info = collection_claim_info(source_info)
    email = _compute_email_posture(info)
    identity = _compute_identity_posture(info)
    infra = _compute_infrastructure_footprint(info)
    consistency = _compute_consistency_observations(info)
    hardening = _compute_hardening_status(info, applicability=applicability)
    index = compute_exposure_index(
        source_info, hypothetical_components=hypothetical_components, applicability=applicability
    )

    # Subsections overlap: DMARC is cited by the email posture and again by its
    # hardening control, CAA by infrastructure and its control. Concatenating made
    # one record look like several, so dict.fromkeys drops repeats in first order.
    collected: list[EvidenceReference] = [*email.evidence, *identity.evidence, *infra.evidence]
    for obs in consistency:
        collected.extend(obs.evidence)
    for ctrl in hardening.controls:
        collected.extend(ctrl.evidence)
    all_evidence = list(dict.fromkeys(collected))

    return ExposureAssessment(
        domain=info.queried_domain,
        email_posture=email,
        identity_posture=identity,
        infrastructure_footprint=infra,
        consistency_observations=consistency,
        hardening_status=hardening,
        posture_score=index.score_floor,
        posture_score_label=_check_neutral_copy("exact-evidence floor in recon's public-control model"),
        disclaimer=_check_neutral_copy(_ASSESSMENT_DISCLAIMER),
        evidence=tuple(all_evidence),
        index_components=index.components,
        unconfirmable_absent_points=index.unconfirmable_absent_points,
        unavailable_controls=index.unavailable_controls,
    )


# ── Gap detection helpers ──────────────────────────────────────────────


def find_gaps_from_info(info: TenantInfo, *, applicability: MailApplicability | None = None) -> GapReport:
    """Identify hardening opportunities in a domain's public configuration.

    Each detector gates its own named observation scopes against raw retained
    evidence. A composite reporting projection would incorrectly erase the
    successful DNS half of a conditionally attempted MTA-STS HTTP request.
    Pure function: TenantInfo in, GapReport out. No I/O.
    """
    applicability = mail_applicability(info) if applicability is None else applicability
    gaps: list[HardeningGap] = []
    gaps.extend(gap_detection.detect_missing_controls(info, applicability=applicability))
    gaps.extend(gap_detection.detect_weak_configs(info, applicability=applicability))
    gaps.extend(gap_detection.detect_inconsistencies(info))
    gap_detection.validate_gap_lineage(gaps, info.degraded_sources)

    observed = observability.ObservableEmailState.from_info(info)
    return GapReport(
        domain=info.queried_domain,
        gaps=tuple(gaps),
        disclaimer=_check_neutral_copy(gap_detection.GAPS_DISCLAIMER),
        unavailable_controls=tuple(
            name for name in observed.unavailable_control_names() if not applicability.evidence_for(name)
        ),
        degraded_sources=tuple(sorted(set(info.degraded_sources))),
    )


# ── Public API: compare_postures_from_infos ────────────────────────────

_COMPARISON_DISCLAIMER = (
    "This comparison is based on publicly observable configuration data. "
    "Differences in posture may reflect different organizational priorities, "
    "not necessarily security deficiencies."
)


def _build_differences(info_a: TenantInfo, info_b: TenantInfo) -> tuple[PostureDifference, ...]:
    """Build control/service differences between two domains."""
    # Compare key security controls
    controls_a = _compute_hardening_status(info_a)
    controls_b = _compute_hardening_status(info_b)

    diffs: list[PostureDifference] = []

    for ctrl_a, ctrl_b in zip(controls_a.controls, controls_b.controls, strict=True):
        if "source unavailable" in {ctrl_a.detail, ctrl_b.detail} or any(
            control.detail.startswith("not applicable:") for control in (ctrl_a, ctrl_b)
        ):
            continue
        if ctrl_a.present != ctrl_b.present:
            first, second = info_a.queried_domain, info_b.queried_domain
            active, inactive = (first, second) if ctrl_a.present else (second, first)
            inactive_control = ctrl_b if ctrl_a.present else ctrl_a
            if ctrl_a.name == "DKIM":
                desc = (
                    f"DKIM observed at a probed selector for {active}; no DKIM record was observed "
                    f"at recon's bounded common-selector set for {inactive}"
                )
            elif ctrl_a.name in {"DMARC", "MTA-STS"}:
                active_control = ctrl_a if ctrl_a.present else ctrl_b
                desc = f"{ctrl_a.name} in {active}: {active_control.detail}; in {inactive}: {inactive_control.detail}"
            else:
                desc = f"{ctrl_a.name} present in {active} but absent in {inactive}"
            diffs.append(
                PostureDifference(
                    description=desc,
                    domain_a_has=ctrl_a.present,
                    domain_b_has=ctrl_b.present,
                )
            )

    return tuple(diffs)


def _build_relative_assessment(info_a: TenantInfo, info_b: TenantInfo) -> tuple[RelativeAssessment, ...]:
    """Build relative posture assessment across dimensions."""
    assessments: list[RelativeAssessment] = []

    # Email security
    observed_a = observability.ObservableEmailState.from_info(info_a)
    observed_b = observability.ObservableEmailState.from_info(info_b)
    if not observed_a.score_collection_available or not observed_b.score_collection_available:
        unavailable_domains = ", ".join(
            info.queried_domain
            for info, observed in ((info_a, observed_a), (info_b, observed_b))
            if not observed.score_collection_available
        )
        summary = (
            "Email-security control observations are not comparable because collection was unavailable for "
            f"{unavailable_domains}"
        )
    else:
        score_a = observed_a.security_score
        score_b = observed_b.security_score
        if score_a > score_b:
            summary = f"{info_a.queried_domain} has more email-security controls observed than {info_b.queried_domain}"
        elif score_b > score_a:
            summary = f"{info_b.queried_domain} has more email-security controls observed than {info_a.queried_domain}"
        else:
            summary = (
                f"{info_a.queried_domain} and {info_b.queried_domain} have a comparable set of email-security controls"
            )
    assessments.append(RelativeAssessment(dimension="email_security", summary=summary))

    # Identity federation. ``None`` is unobserved, never a negative result.
    identity_states: dict[str | None, str] = {
        None: "the identity federation state is unknown",
        "Federated": "federated identity was observed",
        "Managed": "a managed identity response was observed",
    }
    state_a = identity_states.get(info_a.auth_type, "the identity federation state is unknown")
    state_b = identity_states.get(info_b.auth_type, "the identity federation state is unknown")
    if state_a == state_b:
        summary = f"For both domains, {state_a}"
    else:
        summary = f"For {info_a.queried_domain}, {state_a}; for {info_b.queried_domain}, {state_b}"
    assessments.append(RelativeAssessment(dimension="identity_federation", summary=summary))

    # Generic slugs are public fingerprint indicators, not proof of active use.
    indicators_a = len(info_a.slugs)
    indicators_b = len(info_b.slugs)
    if info_a.degraded_sources or info_b.degraded_sources:
        incomplete_domains = ", ".join(info.queried_domain for info in (info_a, info_b) if info.degraded_sources)
        summary = (
            "Public fingerprint counts are not compared because collection opportunity was incomplete for "
            f"{incomplete_domains}"
        )
    elif indicators_a > indicators_b:
        summary = (
            f"{info_a.queried_domain} has more public fingerprint indicators "
            f"({indicators_a} vs {indicators_b} observed)"
        )
    elif indicators_b > indicators_a:
        summary = (
            f"{info_b.queried_domain} has more public fingerprint indicators "
            f"({indicators_b} vs {indicators_a} observed)"
        )
    else:
        summary = f"Both domains have the same public fingerprint count ({indicators_a} observed)"
    assessments.append(RelativeAssessment(dimension="public_fingerprints", summary=summary))

    return tuple(assessments)


def compare_postures_from_infos(info_a: TenantInfo, info_b: TenantInfo) -> PostureComparison:
    """Compare the security postures of two domains side by side.

    Pure function: two TenantInfo in, PostureComparison out. No I/O.
    """
    from recon_tool.collection_view import collection_claim_info

    info_a = collection_claim_info(info_a)
    info_b = collection_claim_info(info_b)
    index_a = compute_exposure_index(info_a)
    index_b = compute_exposure_index(info_b)
    return PostureComparison(
        domain_a=info_a.queried_domain,
        domain_b=info_b.queried_domain,
        metrics=build_metrics(info_a, info_b, index_a, index_b),
        differences=_build_differences(info_a, info_b),
        relative_assessment=_build_relative_assessment(info_a, info_b),
        domain_a_index_components=index_a.components,
        domain_b_index_components=index_b.components,
        domain_a_unavailable_controls=index_a.unavailable_controls,
        domain_b_unavailable_controls=index_b.unavailable_controls,
        disclaimer=_check_neutral_copy(_COMPARISON_DISCLAIMER),
    )
