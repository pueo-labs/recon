# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportPrivateUsage=none, reportUnknownArgumentType=none, reportUnknownMemberType=none
# pyright: reportUnknownVariableType=none
"""Property-based tests for recon_tool/exposure.py core functions.

Uses Hypothesis to generate random TenantInfo instances and verify
correctness properties across all valid inputs.
"""

from __future__ import annotations

import ast
import io
import re
from dataclasses import fields, is_dataclass, replace
from pathlib import Path
from typing import Unpack

import hypothesis.strategies as st
import pytest
from hypothesis import HealthCheck, given, settings
from rich.console import Console

from recon_tool.constants import (
    SVC_BIMI,
    SVC_DKIM,
    SVC_DKIM_EXCHANGE,
    SVC_DKIM_GOOGLE,
    SVC_DMARC,
    SVC_MTA_STS,
    SVC_SPF_SOFTFAIL,
    SVC_SPF_STRICT,
    effective_dmarc_policy,
)
from recon_tool.exposure import (
    EXPOSURE_DISCOURAGED_COPY_TERMS,
    ExposureAssessment,
    _compute_email_security_score,
    assess_exposure_from_info,
    compare_postures_from_infos,
    find_gaps_from_info,
)
from recon_tool.formatter.exposure import render_exposure_panel, render_gaps_panel
from recon_tool.models import ConfidenceLevel, EvidenceRecord, TenantInfo
from tests.tenant_fixtures import TenantInfoArguments, TenantInfoOverrides

# ── Custom Hypothesis strategy for TenantInfo ──────────────────────────

_KNOWN_SLUGS = (
    "microsoft365",
    "google-workspace",
    "proofpoint",
    "mimecast",
    "okta",
    "duo",
    "descope",
    "cloudflare",
    "aws-route53",
    "azure-dns",
    "akamai",
    "letsencrypt",
    "digicert",
    "crowdstrike",
    "zscaler",
    "dmarc",
    "bimi",
    "mta-sts",
    "mta-sts-enforce",
    "tls-rpt",
    "spf-strict",
    "spf-softfail",
    "dkim",
    "dkim-exchange",
    "canva",
    "dropbox",
    "zoom",
    "sentinelone",
    "netskope",
    "aws-cloudfront",
    "gcp-dns",
    "fastly",
    "sectigo",
    "aws-acm",
)

_KNOWN_SERVICES = (
    "Exchange Online",
    "Microsoft 365",
    SVC_DKIM,
    SVC_DKIM_EXCHANGE,
    SVC_SPF_STRICT,
    SVC_SPF_SOFTFAIL,
    SVC_DMARC,
    SVC_BIMI,
    SVC_MTA_STS,
    "Google Workspace: Gmail",
    "Proofpoint",
    "Cloudflare CDN",
)

_DMARC_POLICIES = st.sampled_from([None, "none", "quarantine", "reject"])
_AUTH_TYPES = st.sampled_from([None, "Federated", "Managed"])
_MTA_STS_MODES = st.sampled_from([None, "enforce", "testing", "none"])
_CONFIDENCE_LEVELS = st.sampled_from(list(ConfidenceLevel))


def _evidence_for_slug(slug: str) -> st.SearchStrategy[EvidenceRecord]:
    """Generate an EvidenceRecord for a given slug.

    ``raw_value`` mimics realistic DNS record content (alphanumerics plus
    the small punctuation set actually seen in TXT / MX / CNAME / NS / CAA
    values: ``. - _ = ; : / @``). The strategy also filters out any draw
    that contains a term from ``EXPOSURE_DISCOURAGED_COPY_TERMS``: the
    Property-8 neutral-copy test walks every string field of the
    ExposureAssessment, including echoed evidence values, and a randomly
    drawn natural-English token (``"should"``, ``"risk"`` ...) would
    spuriously fail a test that exists to validate *recon-authored*
    prose, not echoed inputs. Real DNS records do not contain those
    plain-English tokens, so the filter narrows the strategy toward
    realistic inputs rather than restricting genuine coverage.
    """
    raw_value_strategy = st.text(
        min_size=1,
        max_size=50,
        alphabet=st.characters(
            whitelist_categories=("L", "N"),
            whitelist_characters=".-_=;:/@",
        ),
    ).filter(lambda v: not any(term in v.lower() for term in EXPOSURE_DISCOURAGED_COPY_TERMS))
    return st.builds(
        EvidenceRecord,
        source_type=st.sampled_from(["TXT", "MX", "CNAME", "NS", "CAA"]),
        raw_value=raw_value_strategy,
        rule_name=st.just(f"rule-{slug}"),
        slug=st.just(slug),
    )


@st.composite
def tenant_info_strategy(draw: st.DrawFn) -> TenantInfo:
    """Generate a random but valid TenantInfo instance."""
    slugs = draw(st.lists(st.sampled_from(_KNOWN_SLUGS), min_size=0, max_size=10, unique=True))
    services = draw(st.lists(st.sampled_from(_KNOWN_SERVICES), min_size=0, max_size=8, unique=True))
    dmarc_policy = draw(_DMARC_POLICIES)
    auth_type = draw(_AUTH_TYPES)
    mta_sts_mode = draw(_MTA_STS_MODES)
    google_auth_type = draw(st.sampled_from([None, "Federated", "Managed"]))
    google_idp_name = draw(st.sampled_from([None, "Okta", "Ping Identity"]))

    # Generate evidence records for a subset of slugs (only if slugs non-empty)
    evidence: list[EvidenceRecord] = []
    if slugs:
        evidence_slugs = draw(st.lists(st.sampled_from(slugs), max_size=5))
        for s in evidence_slugs:
            evidence.append(draw(_evidence_for_slug(s)))

    return TenantInfo(
        tenant_id=draw(st.sampled_from([None, "tid-12345"])),
        display_name="Test Corp",
        default_domain="test.onmicrosoft.com",
        queried_domain="test.invalid",
        confidence=draw(_CONFIDENCE_LEVELS),
        sources=("test_source",),
        services=tuple(services),
        slugs=tuple(slugs),
        dmarc_policy=dmarc_policy,
        auth_type=auth_type,
        mta_sts_mode=mta_sts_mode,
        google_auth_type=google_auth_type,
        google_idp_name=google_idp_name,
        evidence=tuple(evidence),
    )


# Common settings for all property tests
_PBT_SETTINGS = settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.too_slow],
)


# ── Property 1: Structural completeness ────────────────────────────────
# Feature: defensive-security-tools, Property 1: Structural completeness


class TestProperty1StructuralCompleteness:
    """**Validates: Requirements 1.1, 1.7**"""

    @given(info=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_assess_exposure_returns_all_sections(self, info: TenantInfo) -> None:
        """For any valid TenantInfo, assess_exposure_from_info returns an
        ExposureAssessment with all required sections and score in [0, 100]."""
        result = assess_exposure_from_info(info)

        assert isinstance(result, ExposureAssessment)
        assert result.email_posture is not None
        assert result.identity_posture is not None
        assert result.infrastructure_footprint is not None
        assert result.consistency_observations is not None
        assert result.hardening_status is not None
        assert isinstance(result.posture_score, int)
        assert 0 <= result.posture_score <= 100
        assert result.domain == info.queried_domain


# ── Property 2: Subsection faithfulness ────────────────────────────────
# Feature: defensive-security-tools, Property 2: Subsection faithfulness


class TestProperty2SubsectionFaithfulness:
    """**Validates: Requirements 1.2, 1.3, 1.4, 1.5, 1.6**"""

    @given(info=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_email_posture_reflects_input(self, info: TenantInfo) -> None:
        """Email posture fields reflect typed control evidence, not labels."""
        from recon_tool.email_security import observed_email_control_services

        result = assess_exposure_from_info(info)
        ep = result.email_posture

        assert ep.dmarc_policy == info.dmarc_policy
        assert ep.mta_sts_mode == info.mta_sts_mode

        control_services = observed_email_control_services(info.evidence)
        expected_dkim = bool(control_services & {SVC_DKIM, SVC_DKIM_EXCHANGE, SVC_DKIM_GOOGLE})
        assert ep.dkim_configured == expected_dkim

        expected_spf = SVC_SPF_STRICT in control_services
        assert ep.spf_strict == expected_spf

    @given(info=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_identity_posture_reflects_input(self, info: TenantInfo) -> None:
        """Identity posture fields faithfully reflect TenantInfo input."""
        result = assess_exposure_from_info(info)
        ip = result.identity_posture

        assert ip.auth_type == info.auth_type
        assert ip.google_auth_type == info.google_auth_type

    @given(info=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_infrastructure_cloud_providers_subset_of_slugs(self, info: TenantInfo) -> None:
        """Infrastructure cloud providers are derived from slug classifications."""
        from recon_tool.exposure import _CLOUD_PROVIDER_SLUGS

        result = assess_exposure_from_info(info)
        infra = result.infrastructure_footprint

        # A cloud-footprint role requires CNAME evidence; a generic slug or an
        # NS-only DNS-provider observation is not enough.
        cname_slugs = {ev.slug for ev in info.evidence if ev.source_type.upper() == "CNAME"}
        expected_providers = {_CLOUD_PROVIDER_SLUGS[s] for s in cname_slugs if s in _CLOUD_PROVIDER_SLUGS}
        assert set(infra.cloud_providers) == expected_providers


# ── Property 3: Score bounds ───────────────────────────────────────────
# Feature: defensive-security-tools, Property 3: Score bounds


class TestProperty3ScoreBounds:
    """**Validates: Requirements 1.7**"""

    @given(info=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_posture_score_in_range(self, info: TenantInfo) -> None:
        """Posture score is always in [0, 100]."""
        result = assess_exposure_from_info(info)
        assert 0 <= result.posture_score <= 100


# ── Property 4: Disclaimers ───────────────────────────────────────────
# Feature: defensive-security-tools, Property 4: Disclaimers


class TestProperty4Disclaimers:
    """**Validates: Requirements 1.8, 2.8, 3.5**"""

    @given(info=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_exposure_assessment_has_disclaimer(self, info: TenantInfo) -> None:
        """ExposureAssessment includes a non-empty disclaimer."""
        result = assess_exposure_from_info(info)
        assert result.disclaimer
        assert "defensive review" in result.disclaimer.lower() or "publicly observable" in result.disclaimer.lower()

    @given(info=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_gap_report_has_disclaimer(self, info: TenantInfo) -> None:
        """GapReport includes a non-empty disclaimer."""
        result = find_gaps_from_info(info)
        assert result.disclaimer
        assert "configuration gaps" in result.disclaimer.lower() or "best practices" in result.disclaimer.lower()

    @given(info_a=tenant_info_strategy(), info_b=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_comparison_has_disclaimer(self, info_a: TenantInfo, info_b: TenantInfo) -> None:
        """PostureComparison includes a non-empty disclaimer."""
        result = compare_postures_from_infos(info_a, info_b)
        assert result.disclaimer
        assert "publicly observable" in result.disclaimer.lower() or "comparison" in result.disclaimer.lower()


# ── Property 5: Evidence references ───────────────────────────────────
# Feature: defensive-security-tools, Property 5: Evidence references


class TestProperty5EvidenceReferences:
    """**Validates: Requirements 1.9, 2.7**"""

    @given(info=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_exposure_evidence_refs_link_to_input(self, info: TenantInfo) -> None:
        """All EvidenceReference slugs in ExposureAssessment appear in input evidence."""
        result = assess_exposure_from_info(info)
        input_slugs = {ev.slug for ev in info.evidence}

        for ref in result.evidence:
            assert ref.slug in input_slugs, f"Fabricated evidence slug: {ref.slug}"

    @given(info=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_gap_evidence_refs_link_to_input(self, info: TenantInfo) -> None:
        """All EvidenceReference slugs in GapReport appear in input evidence."""
        result = find_gaps_from_info(info)
        input_slugs = {ev.slug for ev in info.evidence}

        for gap in result.gaps:
            for ref in gap.evidence:
                assert ref.slug in input_slugs, f"Fabricated evidence slug: {ref.slug}"


# ── Property 6: Gap detection correctness ─────────────────────────────
# Feature: defensive-security-tools, Property 6: Gap detection correctness


class TestProperty6GapDetectionCorrectness:
    """**Validates: Requirements 2.2, 2.3, 2.4, 2.5**"""

    @given(info=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_missing_dmarc_produces_gap(self, info: TenantInfo) -> None:
        """A bounded absence or evidence-backed monitoring policy produces a gap."""
        result = find_gaps_from_info(info)
        gap_observations = " ".join(g.observation.lower() for g in result.gaps)
        has_dmarc_evidence = any(
            record.slug == "dmarc" and record.source_type.upper() == "DMARC" for record in info.evidence
        )

        if info.dmarc_policy is None:
            assert "dmarc" in gap_observations, "Missing DMARC should produce a gap"
        elif info.dmarc_policy == "none" and has_dmarc_evidence:
            assert "dmarc" in gap_observations, "DMARC 'none' should produce a gap"

    @given(info=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_missing_dkim_produces_gap(self, info: TenantInfo) -> None:
        """If no typed DKIM response is retained, a bounded DKIM gap is present."""
        has_dkim = any(record.source_type.upper() == "DKIM" for record in info.evidence)
        result = find_gaps_from_info(info)
        gap_observations = " ".join(g.observation.lower() for g in result.gaps)

        if not has_dkim:
            assert "dkim" in gap_observations, "Missing DKIM should produce a gap"

    @given(info=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_missing_mta_sts_produces_gap(self, info: TenantInfo) -> None:
        """If mta_sts_mode is None, an MTA-STS gap is present."""
        result = find_gaps_from_info(info)
        gap_observations = " ".join(g.observation.lower() for g in result.gaps)

        if info.mta_sts_mode is None:
            assert "mta-sts" in gap_observations, "Missing MTA-STS should produce a gap"

    @given(info=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_spf_softfail_produces_gap(self, info: TenantInfo) -> None:
        """Typed SPF softfail evidence without strict evidence produces a gap."""
        spf_slugs = {record.slug for record in info.evidence if record.source_type.upper() == "SPF"}
        has_softfail = "spf-softfail" in spf_slugs
        has_strict = "spf-strict" in spf_slugs
        result = find_gaps_from_info(info)
        gap_observations = " ".join(g.observation.lower() for g in result.gaps)

        if has_softfail and not has_strict:
            assert "spf" in gap_observations, "SPF softfail without strict should produce a gap"

    @given(info=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_gateway_without_dmarc_reject_produces_gap(self, info: TenantInfo) -> None:
        """An MX-backed gateway without DMARC reject produces a consistency gap."""
        from recon_tool.exposure import _EMAIL_GATEWAY_SLUGS

        mx_slugs = {ev.slug for ev in info.evidence if ev.source_type.upper() == "MX"}
        gateway_present = any(
            slug in _EMAIL_GATEWAY_SLUGS and _EMAIL_GATEWAY_SLUGS[slug] == info.email_gateway for slug in mx_slugs
        )
        dmarc_evidence_present = any(
            record.slug == "dmarc" and record.source_type.upper() == "DMARC" for record in info.evidence
        )
        dmarc_basis_available = info.dmarc_policy is None or dmarc_evidence_present
        result = find_gaps_from_info(info)
        gap_observations = " ".join(g.observation.lower() for g in result.gaps)

        if (
            gateway_present
            and dmarc_basis_available
            and effective_dmarc_policy(info.dmarc_policy, info.dmarc_pct, info.dmarc_testing) != "reject"
        ):
            assert "gateway" in gap_observations, "Gateway without DMARC reject should produce a gap"

    def test_dmarc_testing_quarantine_is_reported_as_non_enforcing(self) -> None:
        info = TenantInfo(
            tenant_id=None,
            display_name="Test Corp",
            default_domain="test.invalid",
            queried_domain="test.invalid",
            confidence=ConfidenceLevel.HIGH,
            sources=("test_source",),
            services=(SVC_DMARC,),
            slugs=("dmarc",),
            dmarc_policy="quarantine",
            dmarc_testing=True,
            evidence=(EvidenceRecord("DMARC", "v=DMARC1; p=quarantine; t=y", SVC_DMARC, "dmarc"),),
        )

        assessment = assess_exposure_from_info(info)
        gaps = find_gaps_from_info(info)

        assert assessment.posture_score == 0
        dmarc = next(control for control in assessment.hardening_status.controls if control.name == "DMARC")
        assert dmarc.present is False
        assert dmarc.detail == "quarantine (effective none)"
        assert any("not effectively enforcing" in gap.observation for gap in gaps.gaps)

    def test_gateway_with_dmarc_testing_reject_still_has_consistency_gap(self) -> None:
        info = TenantInfo(
            tenant_id=None,
            display_name="Test Corp",
            default_domain="test.invalid",
            queried_domain="test.invalid",
            confidence=ConfidenceLevel.HIGH,
            sources=("test_source",),
            services=(SVC_DMARC,),
            slugs=("dmarc", "proofpoint"),
            dmarc_policy="reject",
            dmarc_testing=True,
            email_gateway="Proofpoint",
            evidence=(
                EvidenceRecord("MX", "10 mx.example.net", "Proofpoint", "proofpoint"),
                EvidenceRecord("DMARC", "v=DMARC1; p=reject; t=y", SVC_DMARC, "dmarc"),
            ),
        )

        gaps = find_gaps_from_info(info)

        assert any("gateway" in gap.observation.lower() for gap in gaps.gaps)
        assert any("Effective DMARC policy is quarantine" in gap.observation for gap in gaps.gaps)


# ── Property 7: Gap structure validity ────────────────────────────────
# Feature: defensive-security-tools, Property 7: Gap structure validity


class TestProperty7GapStructureValidity:
    """**Validates: Requirements 2.1, 2.6**"""

    @given(info=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_all_gaps_have_valid_structure(self, info: TenantInfo) -> None:
        """Every HardeningGap has valid category, severity, and non-empty fields."""
        result = find_gaps_from_info(info)
        valid_categories = {"email", "identity", "infrastructure", "consistency"}
        valid_severities = {"high", "medium", "low"}

        for gap in result.gaps:
            assert gap.category in valid_categories, f"Invalid category: {gap.category}"
            assert gap.severity in valid_severities, f"Invalid severity: {gap.severity}"
            assert gap.observation, "Observation must be non-empty"
            assert gap.recommendation, "Recommendation must be non-empty"


# ── Property 8: Neutral generated copy ────────────────────────────────
# Feature: defensive-security-tools, Property 8: Neutral generated copy


def _collect_string_fields(obj: object) -> list[str]:
    """Recursively collect all string fields from a dataclass."""
    strings: list[str] = []
    if isinstance(obj, str):
        strings.append(obj)
    elif isinstance(obj, tuple | list):
        for item in obj:
            strings.extend(_collect_string_fields(item))
    elif is_dataclass(obj) and not isinstance(obj, type):
        for field in fields(obj):
            strings.extend(_collect_string_fields(getattr(obj, field.name)))
    return strings


class TestProperty8NeutralGeneratedCopy:
    """**Validates: Requirements 7.1, 7.2, 7.5, 2.12, 3.9**"""

    @given(info=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_no_discouraged_terms_in_exposure_assessment_copy(self, info: TenantInfo) -> None:
        """Generated ExposureAssessment copy stays neutral for normal inputs."""
        result = assess_exposure_from_info(info)
        all_strings = _collect_string_fields(result)
        for s in all_strings:
            lower = s.lower()
            for term in EXPOSURE_DISCOURAGED_COPY_TERMS:
                assert term not in lower, f"Discouraged copy term '{term}' found in: {s!r}"

    @given(info=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_no_discouraged_terms_in_gap_report_copy(self, info: TenantInfo) -> None:
        """Generated GapReport copy stays neutral for normal inputs."""
        result = find_gaps_from_info(info)
        all_strings = _collect_string_fields(result)
        for s in all_strings:
            lower = s.lower()
            for term in EXPOSURE_DISCOURAGED_COPY_TERMS:
                assert term not in lower, f"Discouraged copy term '{term}' found in: {s!r}"

    @given(info_a=tenant_info_strategy(), info_b=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_no_discouraged_terms_in_comparison_copy(self, info_a: TenantInfo, info_b: TenantInfo) -> None:
        """Generated PostureComparison copy stays neutral for normal inputs."""
        result = compare_postures_from_infos(info_a, info_b)
        all_strings = _collect_string_fields(result)
        for s in all_strings:
            lower = s.lower()
            for term in EXPOSURE_DISCOURAGED_COPY_TERMS:
                assert term not in lower, f"Discouraged copy term '{term}' found in: {s!r}"


# ── Property 9: "Consider" language ──────────────────────────────────
# Feature: defensive-security-tools, Property 9: Consider language


class TestProperty9ConsiderLanguage:
    """**Validates: Requirements 7.3**"""

    @given(info=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_all_recommendations_start_with_consider(self, info: TenantInfo) -> None:
        """Every HardeningGap.recommendation starts with 'Consider'."""
        result = find_gaps_from_info(info)
        for gap in result.gaps:
            assert gap.recommendation.startswith("Consider"), (
                f"Recommendation does not start with 'Consider': {gap.recommendation!r}"
            )


# ── Property 10: Comparison metrics match inputs ─────────────────────
# Feature: defensive-security-tools, Property 10: Comparison metrics


class TestProperty10ComparisonMetrics:
    """**Validates: Requirements 3.2**"""

    @given(info_a=tenant_info_strategy(), info_b=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_comparison_metrics_match_inputs(self, info_a: TenantInfo, info_b: TenantInfo) -> None:
        """Comparison metrics accurately reflect both inputs."""
        result = compare_postures_from_infos(info_a, info_b)
        metrics = {m.metric_name: m for m in result.metrics}

        # Email security score
        score_a = _compute_email_security_score(info_a)
        score_b = _compute_email_security_score(info_b)
        assert metrics["email_security_score"].domain_a_value == str(score_a)
        assert metrics["email_security_score"].domain_b_value == str(score_b)

        # DMARC policy
        assert metrics["dmarc_policy"].domain_a_value == (info_a.dmarc_policy or "")
        assert metrics["dmarc_policy"].domain_b_value == (info_b.dmarc_policy or "")

        # Service count
        assert metrics["service_count"].domain_a_value == str(len(info_a.services))
        assert metrics["service_count"].domain_b_value == str(len(info_b.services))


# ── Property 11: Comparison differences ──────────────────────────────
# Feature: defensive-security-tools, Property 11: Comparison differences


class TestProperty11ComparisonDifferences:
    """**Validates: Requirements 3.3**"""

    @given(info_a=tenant_info_strategy(), info_b=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_differences_are_correct_set_operations(self, info_a: TenantInfo, info_b: TenantInfo) -> None:
        """Differences correctly represent the symmetric difference of controls."""
        result = compare_postures_from_infos(info_a, info_b)

        for diff in result.differences:
            # If domain_a_has is True and domain_b_has is False, the control
            # is present in a but absent in b (and vice versa)
            assert diff.domain_a_has != diff.domain_b_has, f"Difference should be asymmetric: {diff.description}"


# ── Property 12: Relative assessment consistency ─────────────────────
# Feature: defensive-security-tools, Property 12: Relative assessment consistency


class TestProperty12RelativeAssessmentConsistency:
    """**Validates: Requirements 3.4**"""

    @given(info_a=tenant_info_strategy(), info_b=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_email_security_assessment_consistent(self, info_a: TenantInfo, info_b: TenantInfo) -> None:
        """If domain_a has higher email score, assessment indicates domain_a is stronger."""
        result = compare_postures_from_infos(info_a, info_b)
        score_a = _compute_email_security_score(info_a)
        score_b = _compute_email_security_score(info_b)

        email_assessment = next(
            (a for a in result.relative_assessment if a.dimension == "email_security"),
            None,
        )
        assert email_assessment is not None

        # v1.0.2 retired ``stronger``/``comparable`` verdict words and the
        # ``score {n}/5 vs {n}/5`` form in favor of describing how the
        # observed-control sets differ. Both apex domains now appear in
        # every assessment summary, and the count direction is conveyed
        # via ``more … than`` / ``a comparable set``.
        summary_lower = email_assessment.summary.lower()
        if score_a > score_b:
            assert info_a.queried_domain in email_assessment.summary
            assert "more" in summary_lower
        elif score_b > score_a:
            assert info_b.queried_domain in email_assessment.summary
            assert "more" in summary_lower
        else:
            assert "comparable" in summary_lower

    @pytest.mark.parametrize(
        ("auth_a", "auth_b", "expected"),
        [
            (None, None, "For both domains, the identity federation state is unknown"),
            (
                "Federated",
                None,
                "For example.com, federated identity was observed; "
                "for other.example, the identity federation state is unknown",
            ),
            (
                "Managed",
                "Federated",
                "For example.com, a managed identity response was observed; "
                "for other.example, federated identity was observed",
            ),
        ],
    )
    def test_identity_federation_preserves_unknown_state(
        self,
        auth_a: str | None,
        auth_b: str | None,
        expected: str,
    ) -> None:
        """Unknown identity discovery is not converted into a negative claim."""
        info_a = TenantInfo(
            tenant_id=None,
            display_name="example.com",
            default_domain="example.com",
            queried_domain="example.com",
            auth_type=auth_a,
        )
        info_b = TenantInfo(
            tenant_id=None,
            display_name="other.example",
            default_domain="other.example",
            queried_domain="other.example",
            auth_type=auth_b,
        )

        result = compare_postures_from_infos(info_a, info_b)

        assessment = next(item for item in result.relative_assessment if item.dimension == "identity_federation")
        assert assessment.summary == expected
        assert "does not" not in assessment.summary


# ── Task 6.1: Import safety test ─────────────────────────────────────


class TestImportSafety:
    """**Validates: Requirements 8.1, 8.2, 8.3**"""

    def test_exposure_module_has_no_network_imports(self) -> None:
        """Verify exposure.py doesn't import network-facing modules."""
        source = Path("src/recon_tool/exposure.py").read_text()
        tree = ast.parse(source)

        # Collect all import names
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)

        disallowed_network_imports = {"httpx", "dns", "dns.resolver", "recon_tool.sources"}
        violations = imports & disallowed_network_imports
        assert not violations, f"Network-facing imports found in exposure.py: {violations}"


# ── Task 6.2: Neutral-copy integration test ──────────────────────────


class TestNeutralCopyIntegration:
    """**Validates: Requirements 7.1, 7.2, 7.4, 7.5**"""

    def _make_info(self, **overrides: Unpack[TenantInfoOverrides]) -> TenantInfo:
        """Create a TenantInfo with sensible defaults, allowing overrides."""
        defaults: TenantInfoArguments = {
            "tenant_id": "tid-test",
            "display_name": "Test Corp",
            "default_domain": "test.onmicrosoft.com",
            "queried_domain": "test.invalid",
            "confidence": ConfidenceLevel.HIGH,
            "sources": ("test_source",),
            "services": (),
            "slugs": (),
            "dmarc_policy": None,
            "auth_type": None,
            "mta_sts_mode": None,
        }
        defaults.update(overrides)
        return TenantInfo(**defaults)

    def _scan_for_discouraged_copy_terms(self, strings: list[str]) -> list[tuple[str, str]]:
        """Return list of (discouraged_term, containing_string) violations."""
        violations = []
        for s in strings:
            lower = s.lower()
            for term in EXPOSURE_DISCOURAGED_COPY_TERMS:
                if term in lower:
                    violations.append((term, s))
        return violations

    def test_no_discouraged_terms_in_exposure_output_variants(self) -> None:
        """Generate multiple TenantInfo variants and scan generated exposure copy."""
        infos = [
            self._make_info(),  # empty
            self._make_info(
                services=(SVC_DKIM, SVC_SPF_STRICT, SVC_DMARC, SVC_BIMI, SVC_MTA_STS),
                slugs=("microsoft365", "dmarc", "dkim", "proofpoint", "okta", "crowdstrike", "zscaler"),
                dmarc_policy="reject",
                auth_type="Federated",
                mta_sts_mode="enforce",
            ),
            self._make_info(
                slugs=("canva", "dropbox", "zoom"),
                dmarc_policy="none",
            ),
            self._make_info(
                services=(SVC_SPF_SOFTFAIL,),
                slugs=("proofpoint",),
                dmarc_policy="quarantine",
                mta_sts_mode="testing",
            ),
        ]

        for info in infos:
            result = assess_exposure_from_info(info)
            all_strings = _collect_string_fields(result)
            violations = self._scan_for_discouraged_copy_terms(all_strings)
            assert not violations, f"Discouraged copy terms in exposure output: {violations}"

    def test_no_discouraged_terms_in_gaps_output_variants(self) -> None:
        """Generate multiple TenantInfo variants and scan generated gaps copy."""
        infos = [
            self._make_info(),
            self._make_info(
                services=(SVC_SPF_SOFTFAIL,),
                slugs=("proofpoint", "mimecast"),
                dmarc_policy="quarantine",
                mta_sts_mode="testing",
            ),
            self._make_info(
                slugs=("canva", "dropbox"),
            ),
        ]

        for info in infos:
            result = find_gaps_from_info(info)
            all_strings = _collect_string_fields(result)
            violations = self._scan_for_discouraged_copy_terms(all_strings)
            assert not violations, f"Discouraged copy terms in gaps output: {violations}"

    def test_no_discouraged_terms_in_comparison_output(self) -> None:
        """Run compare_postures and scan generated comparison copy."""
        info_a = self._make_info(
            queried_domain="a.invalid",
            dmarc_policy="reject",
            auth_type="Federated",
            slugs=("okta", "crowdstrike", "zscaler"),
        )
        info_b = self._make_info(
            queried_domain="b.invalid",
            dmarc_policy="none",
        )
        result = compare_postures_from_infos(info_a, info_b)
        all_strings = _collect_string_fields(result)
        violations = self._scan_for_discouraged_copy_terms(all_strings)
        assert not violations, f"Discouraged copy terms in comparison output: {violations}"

    def test_comparison_allows_discouraged_term_inside_input_domain(self) -> None:
        """Style guidance must not block legitimate reserved/example domains."""
        info_a = self._make_info(
            queried_domain="retargeting.example.com",
            dmarc_policy="reject",
            services=(SVC_DKIM, SVC_SPF_STRICT, SVC_DMARC),
        )
        info_b = self._make_info(queried_domain="baseline.example.com")

        result = compare_postures_from_infos(info_a, info_b)

        assert result.domain_a == "retargeting.example.com"
        assert any("retargeting.example.com" in item.summary for item in result.relative_assessment)

    def test_no_discouraged_terms_in_tool_docstrings(self) -> None:
        """Verify neutral language in the MCP tool docstrings.

        Uses word-boundary matching to avoid false positives like
        'hardening' matching 'harden' — 'hardening' is the approved
        replacement vocabulary per the design doc.
        """
        pytest.importorskip("mcp")
        from recon_tool.server import assess_exposure as ae
        from recon_tool.server import compare_postures as cp
        from recon_tool.server import find_hardening_gaps as fhg

        for func in (ae, fhg, cp):
            doc = func.__doc__ or ""
            lower = doc.lower()
            for term in EXPOSURE_DISCOURAGED_COPY_TERMS:
                # Use word boundary to avoid false positives (e.g. "hardening" vs "harden")
                pattern = rf"\b{re.escape(term)}\b"
                assert not re.search(pattern, lower), f"Discouraged copy term '{term}' in docstring of {func.__name__}"


# ── Observability legibility: the score is a lower bound ───────────────
# The posture score counts only observed-present controls, so a low score can
# mean "hardened but quiet". These tests pin the lower-bound accounting and the
# gap confirmability flag that make that legible to a consuming agent.


class TestScoreObservability:
    @staticmethod
    def _info(
        *,
        services: tuple[str, ...] = (),
        slugs: tuple[str, ...] = (),
        evidence: tuple[EvidenceRecord, ...] = (),
    ) -> TenantInfo:
        return TenantInfo(
            tenant_id=None,
            display_name="Test Corp",
            default_domain="test.onmicrosoft.com",
            queried_domain="test.invalid",
            confidence=ConfidenceLevel.LOW,
            sources=("test_source",),
            services=services,
            slugs=slugs,
            evidence=evidence,
        )

    def test_bare_domain_unresolved_capacity_is_thirty(self) -> None:
        # DKIM (+15), identity federation (+10), and an MX-backed gateway (+5)
        # remain unresolved. Generic vendor indicators receive no control credit.
        result = assess_exposure_from_info(self._info())
        assert result.unconfirmable_absent_points == 30

    def test_observed_dkim_drops_the_floor_by_fifteen(self) -> None:
        from recon_tool.constants import SVC_DKIM

        result = assess_exposure_from_info(
            self._info(
                services=(SVC_DKIM,),
                evidence=(EvidenceRecord("DKIM", "selector response", SVC_DKIM, "dkim"),),
            )
        )
        assert result.unconfirmable_absent_points == 15

    def test_two_vendor_indicators_do_not_change_the_control_floor(self) -> None:
        result = assess_exposure_from_info(self._info(slugs=("crowdstrike", "okta")))
        assert result.unconfirmable_absent_points == 30

    def test_generic_identity_vendor_slug_does_not_name_the_operating_idp(self) -> None:
        result = assess_exposure_from_info(self._info(slugs=("descope",)))
        assert result.identity_posture.identity_provider is None

    def test_txt_vendor_indicators_receive_no_role_or_control_credit(self) -> None:
        slugs = ("okta", "crowdstrike", "proofpoint", "microsoft365", "google-workspace")
        info = replace(
            self._info(slugs=slugs),
            services=("Okta", "CrowdStrike", "Proofpoint", "Microsoft 365", "Google Workspace"),
            evidence=tuple(EvidenceRecord("TXT", f"token={slug}", slug, slug) for slug in slugs),
        )

        assessment = assess_exposure_from_info(info)
        gaps = find_gaps_from_info(info)

        assert assessment.identity_posture.identity_provider is None
        assert assessment.email_posture.email_gateway is None
        assert assessment.consistency_observations == ()
        assert assessment.posture_score == 0
        assert not any("gateway" in gap.observation.lower() for gap in gaps.gaps)

    def test_explicit_google_federation_response_can_name_the_idp(self) -> None:
        info = replace(
            self._info(slugs=("google-workspace",)),
            google_auth_type="Federated",
            google_idp_name="Okta",
            evidence=(EvidenceRecord("HTTP", "redirect=okta", "Google federation", "google-workspace"),),
        )

        assessment = assess_exposure_from_info(info)

        assert assessment.identity_posture.identity_provider == "Okta"

    @pytest.mark.parametrize(
        ("slug", "provider"),
        [("cloudflare", "Cloudflare"), ("aws-route53", "AWS Route 53")],
    )
    def test_ns_role_does_not_expand_into_cloud_or_cdn_role(self, slug: str, provider: str) -> None:
        info = replace(
            self._info(slugs=(slug,)),
            evidence=(EvidenceRecord("NS", f"ns.{slug}.example", provider, slug),),
        )

        infra = assess_exposure_from_info(info).infrastructure_footprint

        assert infra.dns_provider == provider
        assert infra.cloud_providers == ()
        assert infra.cdn_waf == ()

    def test_txt_ca_vendor_indicator_is_not_a_caa_record(self) -> None:
        info = replace(
            self._info(slugs=("globalsign",)),
            evidence=(EvidenceRecord("TXT", "_globalsign-domain-verification=opaque", "GlobalSign", "globalsign"),),
        )

        assessment = assess_exposure_from_info(info)
        gaps = find_gaps_from_info(info)
        caa = next(control for control in assessment.hardening_status.controls if control.name == "CAA")

        assert assessment.infrastructure_footprint.certificate_authorities == ()
        assert not caa.present
        assert any("caa" in gap.observation.lower() for gap in gaps.gaps)

    def test_unmodeled_caa_issuer_still_establishes_record_presence(self) -> None:
        info = replace(
            self._info(),
            evidence=(EvidenceRecord("CAA", '0 issue "new-ca.example"', "CAA record", "caa"),),
        )

        assessment = assess_exposure_from_info(info)
        gaps = find_gaps_from_info(info)
        caa = next(control for control in assessment.hardening_status.controls if control.name == "CAA")

        assert caa.present
        assert assessment.infrastructure_footprint.certificate_authorities == ()
        assert not any("caa" in gap.observation.lower() for gap in gaps.gaps)

    def test_amazon_caa_authorization_is_not_named_as_an_acm_workload(self) -> None:
        info = replace(
            self._info(slugs=("aws-acm",)),
            evidence=(EvidenceRecord("CAA", '0 issue "amazon.com"', "CAA: AWS Certificate Manager", "aws-acm"),),
        )

        authorities = assess_exposure_from_info(info).infrastructure_footprint.certificate_authorities

        assert authorities == ("Amazon",)

    def test_google_dkim_is_consistent_across_assessment_and_degradation(self) -> None:
        observed = replace(
            self._info(services=(SVC_DKIM_GOOGLE,), slugs=("google-workspace",)),
            evidence=(EvidenceRecord("DKIM", "v=DKIM1; p=opaque", SVC_DKIM_GOOGLE, "google-workspace"),),
        )

        available = assess_exposure_from_info(observed)
        unavailable = assess_exposure_from_info(replace(observed, degraded_sources=("dns:dkim",)))

        assert available.email_posture.dkim_configured
        assert next(control for control in available.hardening_status.controls if control.name == "DKIM").present
        assert not unavailable.email_posture.dkim_configured
        assert next(control for control in unavailable.hardening_status.controls if control.name == "DKIM").detail == (
            "source unavailable"
        )

    def test_floor_never_pushes_ceiling_past_100(self) -> None:
        result = assess_exposure_from_info(self._info())
        ceiling = min(100, result.posture_score + result.unconfirmable_absent_points)
        assert result.posture_score <= ceiling <= 100

    def test_dkim_gap_is_not_absence_confirmable(self) -> None:
        # DKIM uses operator-chosen selectors, so its absence is not confirmable
        # from the common-selector probe; the gap must flag that.
        report = find_gaps_from_info(self._info())
        dkim_gaps = [g for g in report.gaps if "dkim" in g.observation.lower()]
        assert dkim_gaps
        assert all(not g.absence_confirmable for g in dkim_gaps)

    def test_missing_dmarc_gap_is_absence_confirmable(self) -> None:
        # A missing DMARC record is a genuine public-records fact.
        report = find_gaps_from_info(self._info())
        dmarc_gaps = [g for g in report.gaps if "dmarc" in g.observation.lower()]
        assert dmarc_gaps
        assert all(g.absence_confirmable for g in dmarc_gaps)

    @staticmethod
    def _complete_info(degraded_sources: tuple[str, ...]) -> TenantInfo:
        return TenantInfo(
            tenant_id="tid-test",
            display_name="Test Corp",
            default_domain="test.onmicrosoft.com",
            queried_domain="test.invalid",
            confidence=ConfidenceLevel.HIGH,
            sources=("dns_records",),
            services=(SVC_DMARC, SVC_DKIM, SVC_SPF_STRICT, SVC_MTA_STS, SVC_BIMI),
            slugs=(
                "dmarc",
                "mta-sts",
                "mta-sts-enforce",
                "proofpoint",
                "crowdstrike",
                "okta",
                "tls-rpt",
                "letsencrypt",
            ),
            dmarc_policy="reject",
            auth_type="Federated",
            mta_sts_mode="enforce",
            email_gateway="Proofpoint",
            evidence=(
                EvidenceRecord("DMARC", "v=DMARC1; p=reject", SVC_DMARC, "dmarc"),
                EvidenceRecord("DKIM", "v=DKIM1; p=opaque", SVC_DKIM, "dkim"),
                EvidenceRecord("SPF", "v=spf1 -all", SVC_SPF_STRICT, "spf-strict"),
                EvidenceRecord("MTA_STS", "v=STSv1; id=1", SVC_MTA_STS, "mta-sts"),
                EvidenceRecord("MTA_STS_POLICY", "mode: enforce", SVC_MTA_STS, "mta-sts-enforce"),
                EvidenceRecord("BIMI", "v=BIMI1; l=https://example/logo.svg", SVC_BIMI, "bimi"),
                EvidenceRecord("TXT", "v=TLSRPTv1; rua=mailto:tls@example.com", "TLS-RPT", "tls-rpt"),
                EvidenceRecord("CAA", '0 issue "letsencrypt.org"', "CAA record", "caa"),
                EvidenceRecord("CAA", '0 issue "letsencrypt.org"', "Let's Encrypt", "letsencrypt"),
                EvidenceRecord("MX", "10 mx.example.net", "Proofpoint", "proofpoint"),
                EvidenceRecord("HTTP", "NameSpaceType=Federated", "GetUserRealm", "microsoft365"),
            ),
            degraded_sources=degraded_sources,
        )

    @pytest.mark.parametrize(
        ("marker", "expected_score", "expected_ceiling_points", "unavailable_controls"),
        [
            ("dns:dmarc", 70, 20, {"DMARC"}),
            ("dns:mta_sts", 75, 15, {"MTA-STS"}),
            ("http:mta_sts_policy", 75, 15, {"MTA-STS"}),
            ("dns:apex_txt", 80, 10, set()),
            ("dns:mx", 85, 5, set()),
            ("detector:dkim", 75, 15, {"DKIM"}),
            ("detector:caa", 85, 5, {"CAA"}),
            ("detector:email_security", 45, 45, {"DMARC", "MTA-STS", "BIMI", "TLS-RPT"}),
            ("dns", 10, 80, {"DMARC", "DKIM", "MTA-STS", "BIMI", "TLS-RPT", "CAA"}),
            ("dns_records", 10, 80, {"DMARC", "DKIM", "MTA-STS", "BIMI", "TLS-RPT", "CAA"}),
        ],
    )
    def test_degraded_declarative_channels_are_unobserved(
        self,
        marker: str,
        expected_score: int,
        expected_ceiling_points: int,
        unavailable_controls: set[str],
    ) -> None:
        info = self._complete_info((marker,))
        assessment = assess_exposure_from_info(info)
        report = find_gaps_from_info(info)
        controls = {control.name: control for control in assessment.hardening_status.controls}

        assert assessment.posture_score == expected_score
        assert assessment.unconfirmable_absent_points == expected_ceiling_points
        expected_unavailable = set(unavailable_controls)
        if marker == "dns:apex_txt":
            expected_unavailable.add("SPF")
        if marker == "dns:mx":
            expected_unavailable.add("Email gateway")
        if marker in {"dns", "dns_records"}:
            expected_unavailable.update({"SPF", "Email gateway"})
        assert set(assessment.unavailable_controls) == expected_unavailable
        assert set(report.unavailable_controls) == expected_unavailable
        assert report.degraded_sources == (marker,)
        assert all(controls[name].detail == "source unavailable" for name in unavailable_controls)
        if "DMARC" in unavailable_controls:
            assert assessment.email_posture.dmarc_policy is None
            assert not any("dmarc" in gap.observation.lower() for gap in report.gaps)
        if "MTA-STS" in unavailable_controls:
            assert assessment.email_posture.mta_sts_mode is None
            assert not any("mta-sts" in gap.observation.lower() for gap in report.gaps)
        if marker == "dns:apex_txt":
            assert assessment.email_posture.spf_strict is False
        if marker == "dns:mx":
            assert assessment.email_posture.email_gateway is None
        if marker in {"dns", "dns_records"}:
            assert assessment.email_posture.dkim_configured is False
            assert assessment.email_posture.bimi_configured is False
            assert not any("tls-rpt" in gap.observation.lower() for gap in report.gaps)
            assert not any("caa" in gap.observation.lower() for gap in report.gaps)

        output = io.StringIO()
        Console(file=output, width=100, force_terminal=False).print(render_exposure_panel(assessment))
        assert output.getvalue().count("source unavailable") >= len(unavailable_controls)

        gap_output = io.StringIO()
        Console(file=gap_output, width=100, force_terminal=False).print(render_gaps_panel(report))
        assert "Collection unavailable for:" in gap_output.getvalue()

    def test_comparison_does_not_treat_unavailable_control_as_absent(self) -> None:
        observed = self._complete_info(())
        degraded = replace(
            observed,
            queried_domain="degraded.example",
            degraded_sources=("dns:dmarc",),
        )

        comparison = compare_postures_from_infos(degraded, observed)
        metrics = {metric.metric_name: metric for metric in comparison.metrics}

        assert metrics["dmarc_policy"].domain_a_value == "source unavailable"
        assert not any(diff.description.startswith("DMARC present") for diff in comparison.differences)

    def test_unobserved_dkim_is_bounded_to_common_selectors(self) -> None:
        assessment = assess_exposure_from_info(self._info())
        dkim = next(control for control in assessment.hardening_status.controls if control.name == "DKIM")

        assert dkim.detail == "not observed at recon's bounded common-selector set"
        assert "not configured" not in dkim.detail

    def test_dkim_difference_does_not_claim_absence(self) -> None:
        observed = replace(
            self._info(services=(SVC_DKIM,)),
            queried_domain="observed.example",
            evidence=(EvidenceRecord("DKIM", "v=DKIM1; p=opaque", SVC_DKIM, "dkim"),),
        )
        unobserved = replace(self._info(), queried_domain="unobserved.example")

        comparison = compare_postures_from_infos(observed, unobserved)
        dkim = next(difference for difference in comparison.differences if difference.description.startswith("DKIM"))

        assert "bounded common-selector set" in dkim.description
        assert "absent" not in dkim.description

    def test_comparison_marks_incomplete_opportunity_instead_of_ranking_zero(self) -> None:
        observed = self._complete_info(())
        degraded = replace(
            self._complete_info(("dns:dkim",)),
            queried_domain="degraded.example",
            services=(),
            slugs=(),
            evidence=(),
        )

        comparison = compare_postures_from_infos(degraded, observed)
        metrics = {metric.metric_name: metric for metric in comparison.metrics}
        assessments = {item.dimension: item.summary for item in comparison.relative_assessment}

        assert metrics["email_security_score"].domain_a_value == "source unavailable"
        assert metrics["service_count"].domain_a_value == "0 observed (partial collection)"
        assert "not comparable" in assessments["email_security"]
        assert "not compared" in assessments["public_fingerprints"]


class TestExposureEvidenceIsDeduplicated:
    """One observed record must appear once in the assessment evidence.

    The subsections overlap by construction: DMARC is cited by the email
    posture and again by its hardening control, and a CAA record by both the
    infrastructure view and its control. Concatenating them made a single
    record look like several, so anything counting corroborating records for a
    claim saw about twice the support that exists.
    """

    def test_overlapping_sections_do_not_repeat_a_record(self) -> None:
        from recon_tool.exposure import assess_exposure_from_info
        from recon_tool.models import ConfidenceLevel, EvidenceRecord, TenantInfo

        evidence = (
            EvidenceRecord(source_type="TXT", raw_value="v=DMARC1; p=reject", rule_name="dmarc", slug="dmarc"),
            EvidenceRecord(source_type="TXT", raw_value="v=spf1 -all", rule_name="spf", slug="spf"),
            EvidenceRecord(source_type="CNAME", raw_value="sel._domainkey", rule_name="dkim", slug="dkim"),
            EvidenceRecord(source_type="TXT", raw_value="v=BIMI1", rule_name="bimi", slug="bimi"),
            EvidenceRecord(source_type="CAA", raw_value="0 issue letsencrypt.org", rule_name="caa", slug="letsencrypt"),
        )
        info = TenantInfo(
            tenant_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            display_name="Synthetic Alpha",
            default_domain="alpha.onmicrosoft.com",
            queried_domain="alpha.invalid",
            confidence=ConfidenceLevel.HIGH,
            services=("DMARC", "DKIM", "SPF"),
            slugs=("dmarc", "dkim", "spf", "bimi", "letsencrypt"),
            evidence=evidence,
            dmarc_policy="reject",
            mta_sts_mode="enforce",
        )

        references = list(assess_exposure_from_info(info).evidence)

        assert len(references) == len(set(references))


class TestScoreCeilingSurvivesIdentityDegradation:
    """The ceiling must stay an upper bound when any channel degrades.

    A degraded identity channel masks ``auth_type`` to None, so a federated
    namespace loses those points from its score. Every DNS channel contributes
    a matching term to the unconfirmable total; identity was omitted, so the
    reported ceiling fell below the undegraded ceiling and stopped bounding the
    true posture from above.
    """

    @staticmethod
    def _info(degraded: tuple[str, ...]):
        from recon_tool.models import ConfidenceLevel, EvidenceRecord, TenantInfo

        evidence = (
            EvidenceRecord(source_type="DMARC", raw_value="v=DMARC1; p=reject", rule_name="DMARC", slug="dmarc"),
            EvidenceRecord(source_type="CAA", raw_value="0 issue letsencrypt.org", rule_name="caa", slug="letsencrypt"),
            EvidenceRecord(
                source_type="HTTP",
                raw_value="NameSpaceType=Federated",
                rule_name="GetUserRealm",
                slug="microsoft365",
            ),
        )

        return TenantInfo(
            tenant_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            display_name="Synthetic Alpha",
            default_domain="alpha.onmicrosoft.com",
            queried_domain="alpha.invalid",
            confidence=ConfidenceLevel.HIGH,
            services=("DMARC",),
            slugs=("dmarc", "letsencrypt"),
            evidence=evidence,
            dmarc_policy="reject",
            auth_type="Federated",
            degraded_sources=degraded,
        )

    def _ceiling(self, degraded: tuple[str, ...]) -> int:
        from recon_tool.exposure import assess_exposure_from_info

        assessment = assess_exposure_from_info(self._info(degraded))
        return min(100, assessment.posture_score + assessment.unconfirmable_absent_points)

    def test_identity_degradation_does_not_lower_the_ceiling(self) -> None:
        baseline = self._ceiling(())

        assert self._ceiling(("identity:user_realm",)) == baseline

    def test_a_dns_channel_still_behaves_the_same_way(self) -> None:
        baseline = self._ceiling(())

        assert self._ceiling(("dns:caa",)) == baseline

    def test_identity_degradation_lowers_the_score_it_compensates(self) -> None:
        from recon_tool.exposure import assess_exposure_from_info

        undegraded = assess_exposure_from_info(self._info(()))
        degraded = assess_exposure_from_info(self._info(("identity:user_realm",)))

        assert degraded.posture_score < undegraded.posture_score
        assert degraded.unconfirmable_absent_points > undegraded.unconfirmable_absent_points

    @given(info=tenant_info_strategy())
    @_PBT_SETTINGS
    def test_component_ledger_is_complete_and_self_consistent(self, info: TenantInfo) -> None:
        assessment = assess_exposure_from_info(info)
        components = assessment.index_components

        assert len(components) == 9
        assert len({component.component_id for component in components}) == 9
        assert sum(component.maximum_points for component in components) == 90
        assert assessment.posture_score == sum(component.awarded_points for component in components)
        assert assessment.unconfirmable_absent_points == sum(component.unconfirmable_points for component in components)
        assert all(component.evidence for component in components if component.awarded_points)
        assert all(not component.evidence for component in components if component.state == "unavailable")


class TestMtaStsModeNoneIsNotInEffect:
    """RFC 8461 defines mode "none" as "policy not in effect".

    Regression coverage: a fetched none-mode policy was credited as a present
    MTA-STS control with no gap raised, so a domain that explicitly disabled
    MTA-STS looked better than one that never deployed it.
    """

    @staticmethod
    def _info() -> TenantInfo:
        return TenantInfo(
            tenant_id=None,
            display_name="Test Corp",
            default_domain="test.onmicrosoft.com",
            queried_domain="test.invalid",
            confidence=ConfidenceLevel.HIGH,
            sources=("test_source",),
            services=(SVC_MTA_STS,),
            slugs=("mta-sts",),
            mta_sts_mode="none",
            evidence=(
                EvidenceRecord("MTA_STS", "v=STSv1; id=1", SVC_MTA_STS, "mta-sts"),
                EvidenceRecord("MTA_STS_POLICY", "mode: none", SVC_MTA_STS, "mta-sts"),
            ),
        )

    def test_control_is_not_present_and_detail_stays_precise(self) -> None:
        assessment = assess_exposure_from_info(self._info())
        control = next(c for c in assessment.hardening_status.controls if c.name == "MTA-STS")

        assert control.present is False
        # The record was observed, so the detail must say so rather than erase it.
        assert control.detail == "policy published with mode none (not in effect)"
        assert control.evidence
        assert assessment.email_posture.mta_sts_mode == "none"
        assert assessment.email_posture.email_security_score == 0

    def test_mode_none_raises_a_gap_distinct_from_absence(self) -> None:
        report = find_gaps_from_info(self._info())
        observations = [gap.observation for gap in report.gaps]

        assert any("mode none" in observation for observation in observations)
        assert not any("No MTA-STS policy detected" in observation for observation in observations)


class TestDmarcNoneIsNotAHardeningControl:
    """DMARC p=none is monitoring. It is not a present hardening control.

    The same rule applies when pct or t=y testing leaves the effective
    policy at none. A reject record compared with a none record is one
    DMARC difference.
    """

    @staticmethod
    def _info(
        *,
        queried_domain: str = "test.invalid",
        dmarc_policy: str = "none",
        dmarc_pct: int | None = None,
        evidence: tuple[EvidenceRecord, ...] | None = None,
    ) -> TenantInfo:
        if evidence is None:
            evidence = (EvidenceRecord("DMARC", "v=DMARC1; p=none", SVC_DMARC, "dmarc"),)
        return TenantInfo(
            tenant_id=None,
            display_name="Test Corp",
            default_domain="test.onmicrosoft.com",
            queried_domain=queried_domain,
            confidence=ConfidenceLevel.HIGH,
            sources=("test_source",),
            services=(SVC_DMARC,),
            slugs=("dmarc",),
            dmarc_policy=dmarc_policy,
            dmarc_pct=dmarc_pct,
            evidence=evidence,
        )

    def test_policy_none_is_visible_and_not_present(self) -> None:
        assessment = assess_exposure_from_info(self._info())
        control = next(item for item in assessment.hardening_status.controls if item.name == "DMARC")

        assert control.present is False
        assert control.detail == "policy set to none (monitoring only, not enforcing)"
        assert control.evidence
        assert assessment.email_posture.dmarc_policy == "none"

        output = io.StringIO()
        Console(file=output, width=120, force_terminal=False).print(render_exposure_panel(assessment))
        rendered = output.getvalue()
        assert "- DMARC: policy set to none (monitoring only, not enforcing)" in rendered

    def test_partial_quarantine_is_not_present(self) -> None:
        assessment = assess_exposure_from_info(
            self._info(
                dmarc_policy="quarantine",
                dmarc_pct=50,
                evidence=(EvidenceRecord("DMARC", "v=DMARC1; p=quarantine; pct=50", SVC_DMARC, "dmarc"),),
            )
        )
        control = next(item for item in assessment.hardening_status.controls if item.name == "DMARC")

        assert control.present is False
        assert control.detail == "quarantine (effective none)"
        assert control.evidence

    def test_reject_versus_none_is_one_dmarc_difference(self) -> None:
        reject = self._info(
            queried_domain="reject.invalid",
            dmarc_policy="reject",
            evidence=(EvidenceRecord("DMARC", "v=DMARC1; p=reject", SVC_DMARC, "dmarc"),),
        )
        monitoring = self._info(queried_domain="none.invalid")

        comparison = compare_postures_from_infos(reject, monitoring)
        dmarc = [item for item in comparison.differences if item.description.startswith("DMARC")]

        assert len(dmarc) == 1
        assert dmarc[0].domain_a_has is True
        assert dmarc[0].domain_b_has is False
