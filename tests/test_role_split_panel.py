"""ADR-0015: role-split vendor claims in the default view.

A domain can publish a mail vendor and an identity vendor that are not the same
company. Before this, the panel named the mail vendor in a singular, unroled
``Provider`` row, filed the identity vendor under ``Email`` with no mail role
(so ADR-0012 dropped it from the default view), and let ``Model support``
corroborate one of two equally supported tenant-class claims. A reader who
stopped at the panel briefed the wrong primary vendor.

These tests pin the split *and* pin that ordinary single-vendor records are
untouched, because the cost of the fix is one extra row and it must be paid
only where the ambiguity exists.
"""

from __future__ import annotations

import io
from dataclasses import replace
from io import StringIO

from rich.console import Console

from recon_tool.bayesian import load_network
from recon_tool.formatter import render_tenant_panel
from recon_tool.formatter.classify import categorize_services
from recon_tool.formatter.roles import identity_role_vendors, model_support_claims, role_split_vendors
from recon_tool.models import ConfidenceLevel, EvidenceRecord, PosteriorObservation, TenantInfo

# Real production shapes: the identity collectors emit source_type "HTTP" and
# carry the endpoint in rule_name. Getting this wrong is why the first draft of
# these fixtures silently exercised nothing.
_OIDC = EvidenceRecord("HTTP", "tenant_id=c7c08208-4f4d-45f1-83cd-5e2f491ab786", "OIDC Discovery", "microsoft365")
_REALM = EvidenceRecord("HTTP", "NameSpaceType=Federated", "GetUserRealm", "microsoft365")
_GOOGLE_MX = EvidenceRecord("MX", "10 aspmx.l.google.example", "Google Workspace", "google-workspace")
_GOOGLE_DKIM = EvidenceRecord("DKIM", "google._domainkey.beta.invalid", "DKIM (Google Workspace)", "dkim")


def _posterior(name: str, posterior: float, low: float) -> PosteriorObservation:
    node = next(node for node in load_network().nodes if node.name == name)
    binding = node.evidence[0]
    return PosteriorObservation(
        name=name,
        description=node.description,
        posterior=posterior,
        interval_low=low,
        interval_high=0.99,
        evidence_used=(f"{binding.kind}:{binding.name}",),
        n_eff=4.0,
        sparse=False,
    )


def _info(*, evidence: tuple[EvidenceRecord, ...], slugs: tuple[str, ...], services: tuple[str, ...]) -> TenantInfo:
    return TenantInfo(
        tenant_id="c7c08208-4f4d-45f1-83cd-5e2f491ab786",
        display_name="",
        default_domain="beta.invalid",
        queried_domain="beta.invalid",
        region="NA",
        confidence=ConfidenceLevel.HIGH,
        sources=("oidc", "userrealm", "dns"),
        services=services,
        slugs=slugs,
        auth_type="Federated",
        evidence=evidence,
        evidence_confidence=ConfidenceLevel.HIGH,
        inference_confidence=ConfidenceLevel.HIGH,
    )


def split_info() -> TenantInfo:
    """Google-class mail, Microsoft-class identity: the reported case."""
    return _info(
        evidence=(_GOOGLE_MX, _GOOGLE_DKIM, _OIDC, _REALM),
        slugs=("google-workspace", "microsoft365", "dkim"),
        services=("Google Workspace", "Microsoft 365", "DKIM (Google Workspace)"),
    )


def single_vendor_info() -> TenantInfo:
    """One vendor doing mail and identity: must render exactly as before."""
    return _info(
        evidence=(
            EvidenceRecord("MX", "10 beta-invalid.mail.protection.outlook.example", "Microsoft 365", "microsoft365"),
            _OIDC,
            _REALM,
        ),
        slugs=("microsoft365",),
        services=("Microsoft 365",),
    )


def _panel_text(info: TenantInfo) -> str:
    console = Console(file=io.StringIO(), width=78, no_color=True, legacy_windows=False)
    console.print(render_tenant_panel(info))
    assert isinstance(console.file, StringIO)
    return console.file.getvalue()


def test_identity_vendors_come_from_endpoint_provenance_not_slug_category() -> None:
    # microsoft365 is catalogued under Email; only its evidence provenance says
    # identity. A category-driven rule would return nothing here.
    assert identity_role_vendors(split_info()) == ("Microsoft 365",)


def test_role_split_names_both_vendors_with_their_roles() -> None:
    out = _panel_text(split_info())

    assert "Mail" in out
    assert "Identity" in out
    assert "Google Workspace" in out
    assert "Microsoft 365" in out
    # The defect was a singular unroled headline; it must be gone.
    assert "Provider" not in out


def test_single_vendor_panel_keeps_the_provider_row() -> None:
    out = _panel_text(single_vendor_info())

    assert "Provider" in out
    assert "  Mail " not in out
    assert role_split_vendors(single_vendor_info()) is None


def test_no_identity_evidence_keeps_absence_absent() -> None:
    mail_only = _info(
        evidence=(_GOOGLE_MX,),
        slugs=("google-workspace",),
        services=("Google Workspace",),
    )

    assert identity_role_vendors(mail_only) == ()
    assert role_split_vendors(mail_only) is None
    assert "Identity" not in _panel_text(mail_only)


def test_identity_vendor_is_filed_under_identity_not_email() -> None:
    categorized = categorize_services(split_info())

    assert any("Microsoft 365" in service for service in categorized.get("Identity", []))
    assert not any("Microsoft 365" in service for service in categorized.get("Email", []))


def test_model_support_names_every_tenant_class_claim_at_the_same_fill() -> None:
    claims = [_posterior("google_workspace_tenant", 0.90, 0.82), _posterior("m365_tenant", 0.95, 0.89)]

    named, fill = model_support_claims(claims)

    assert fill == 3
    assert {claim.name for claim in named} == {"google_workspace_tenant", "m365_tenant"}


def test_model_support_still_reports_the_weakest_single_claim() -> None:
    # Conservatism preserved: a lone weak node still drives the row, and a
    # non-tenant node is not swept in beside a tenant claim.
    claims = [_posterior("m365_tenant", 0.95, 0.89), _posterior("email_gateway_present", 0.58, 0.42)]

    named, fill = model_support_claims(claims)

    assert fill == 2
    assert [claim.name for claim in named] == ["email_gateway_present"]


def test_model_support_vendor_is_visible_on_secondary_mail_selector() -> None:
    google = EvidenceRecord("DKIM", "v=DKIM1; p=example", "DKIM (Google Workspace)", "google-workspace")
    mx = EvidenceRecord("MX", "10 mx.beta.invalid", "Custom or unclassified MX", "self-hosted-email")
    info = replace(
        split_info(),
        evidence=(_OIDC, _REALM, google, mx),
        primary_email_provider="Custom or unclassified MX",
        posterior_observations=(
            _posterior("google_workspace_tenant", 0.90, 0.82),
            _posterior("m365_tenant", 0.95, 0.89),
        ),
    )
    panel = _panel_text(info)
    facts, services = panel.split("Services", maxsplit=1)
    assert "Google Workspace tenant" in " ".join(facts.split())
    assert "DKIM (Google Workspace)" in " ".join(services.split())
