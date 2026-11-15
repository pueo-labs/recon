# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportPrivateUsage=none
"""Targeted coverage tests for formatter rendering paths.

Exercises panel render branches that weren't hit by the existing test
files: empty services, no cert_summary, degraded sources with and
without CT provider attribution, render_source_status_panel,
detect_provider edge cases, etc. No real company names.
"""

from __future__ import annotations

import csv
import io
import re

import pytest
from rich.console import Console

from recon_tool.formatter import (
    detect_provider,
    format_batch_csv,
    format_tenant_csv_row,
    get_console,
    render_source_status_panel,
    render_sources_detail,
    render_tenant_panel,
    render_verbose_sources,
    set_console,
)
from recon_tool.formatter.classify import categorize_services, provider_line
from recon_tool.models import (
    CertSummary,
    ConfidenceLevel,
    EvidenceRecord,
    SourceResult,
    SurfaceAttribution,
    TenantInfo,
)

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip(s: str) -> str:
    return _ANSI_RE.sub("", s)


@pytest.fixture(autouse=True)
def _restore_console():
    """Each test in this file replaces the global console via set_console;
    restore the original on teardown so other test modules (CliRunner-based
    tests, etc.) get a clean console fixture instead of the StringIO buffer
    orphaned at the end of this file's last test."""
    original = get_console()
    yield
    set_console(original)


def _make_console() -> tuple[Console, io.StringIO]:
    buf = io.StringIO()
    c = Console(file=buf, force_terminal=True, width=200, no_color=True, highlight=False)
    set_console(c)
    return c, buf


def _minimal_info(**overrides: object) -> TenantInfo:
    defaults: dict[str, object] = {
        "tenant_id": None,
        "display_name": "Synthetic Alpha",
        "default_domain": "alpha.invalid",
        "queried_domain": "alpha.invalid",
        "confidence": ConfidenceLevel.MEDIUM,
        "region": "NA",
        "sources": ("dns_records",),
        "services": (),
        "slugs": (),
        "auth_type": None,
        "dmarc_policy": None,
        "domain_count": 1,
    }
    defaults.update(overrides)
    return TenantInfo(**defaults)  # type: ignore[arg-type]


class TestEvidenceSemanticServiceClassification:
    @pytest.mark.parametrize(
        ("parent_slug", "parent_service", "unsupported_child"),
        [
            ("microsoft365", "Microsoft 365", "Microsoft Copilot (likely)"),
            ("google-workspace", "Google Workspace", "Google Gemini (likely)"),
        ],
    )
    def test_parent_platform_does_not_infer_child_product(
        self,
        parent_slug: str,
        parent_service: str,
        unsupported_child: str,
    ) -> None:
        categorized = categorize_services(
            _minimal_info(
                services=(parent_service,),
                slugs=(parent_slug,),
                evidence=(EvidenceRecord("MX", f"mx.{parent_slug}.example", parent_service, parent_slug),),
            )
        )

        assert f"{parent_service} (MX delivery path)" in categorized["Email"]
        assert unsupported_child not in {service for services in categorized.values() for service in services}

    def test_direct_ai_fingerprint_remains_visible(self) -> None:
        categorized = categorize_services(
            _minimal_info(
                services=("Microsoft 365", "OpenAI Enterprise"),
                slugs=("microsoft365", "openai"),
                evidence=(
                    EvidenceRecord("TXT", "MS=opaque", "Microsoft 365", "microsoft365"),
                    EvidenceRecord("TXT", "openai-domain-verification=opaque", "OpenAI Enterprise", "openai"),
                ),
            )
        )

        assert categorized["AI"] == ["OpenAI Enterprise (public TXT account indicator)"]


class TestEvidenceRoleAwareServiceClassification:
    def test_public_categorizer_masks_an_unavailable_collection_channel(self) -> None:
        info = _minimal_info(
            services=("Proofpoint",),
            slugs=("proofpoint",),
            evidence=(EvidenceRecord("MX", "10 mx.proofpoint.example", "Proofpoint", "proofpoint"),),
            degraded_sources=("dns:mx",),
        )

        assert categorize_services(info) == {}

    def test_legacy_topology_fields_without_lineage_do_not_create_mx_roles(self) -> None:
        info = _minimal_info(
            services=("Microsoft 365", "Proofpoint"),
            slugs=("microsoft365", "proofpoint"),
            primary_email_provider="Microsoft 365",
            email_gateway="Proofpoint",
            evidence=(),
        )

        assert provider_line(info) == "Microsoft 365 (role unavailable)"

    def test_null_mx_renders_as_no_mail_observation_not_delivery(self) -> None:
        info = _minimal_info(
            services=("Null MX (domain does not accept email)",),
            slugs=("null-mx",),
            evidence=(
                EvidenceRecord(
                    "MX",
                    "0 .",
                    "Null MX (domain does not accept email)",
                    "null-mx",
                ),
            ),
        )

        assert provider_line(info) == "Null MX (domain does not accept email)"
        assert categorize_services(info) == {"Email": ["Null MX (domain does not accept email)"]}

    def test_google_domains_nameserver_stays_a_dns_role(self) -> None:
        info = _minimal_info(
            services=("Google Domains DNS",),
            slugs=("google-domains-dns",),
            evidence=(
                EvidenceRecord(
                    "NS",
                    "ns-cloud-a1.googledomains.com",
                    "Google Domains DNS",
                    "google-domains-dns",
                ),
            ),
        )

        assert categorize_services(info) == {"Cloud": ["Google Domains DNS (DNS)"]}
        assert "Google Workspace" not in provider_line(info)

    @pytest.mark.parametrize(
        ("slug", "service", "category", "expected"),
        [
            ("proofpoint", "Proofpoint", "Email", "Proofpoint (public TXT account indicator)"),
            ("okta", "Okta", "Identity", "Okta (public TXT account indicator)"),
            (
                "crowdstrike",
                "CrowdStrike Falcon",
                "Security",
                "CrowdStrike Falcon (public TXT account indicator)",
            ),
            ("zscaler", "Zscaler", "Security", "Zscaler (public TXT account indicator)"),
            ("openai", "OpenAI Enterprise", "AI", "OpenAI Enterprise (public TXT account indicator)"),
            ("slack", "Slack", "Collaboration", "Slack (public TXT account indicator)"),
            ("github", "GitHub", "Collaboration", "GitHub (public TXT account indicator)"),
            ("jamf", "Jamf", "Security", "Jamf (public TXT account indicator)"),
            (
                "gitlab",
                "GitLab",
                "Collaboration",
                "GitLab (public TXT account indicator)",
            ),
        ],
    )
    def test_txt_only_vendor_receipt_is_not_rendered_as_an_active_role(
        self,
        slug: str,
        service: str,
        category: str,
        expected: str,
    ) -> None:
        info = _minimal_info(
            services=(service,),
            slugs=(slug,),
            evidence=(
                EvidenceRecord(
                    "SUBDOMAIN_TXT" if slug == "gitlab" else "TXT",
                    f"{slug}=opaque",
                    service,
                    slug,
                ),
            ),
        )

        categorized = categorize_services(info)

        assert categorized[category] == [expected]
        assert sum(item.startswith(service) for items in categorized.values() for item in items) == 1

    @pytest.mark.parametrize(
        ("slug", "service", "expected"),
        [
            ("cloudflare", "Cloudflare", "Cloudflare (DNS)"),
            ("aws-route53", "AWS Route 53", "AWS Route 53 (DNS)"),
        ],
    )
    def test_ns_only_evidence_renders_only_the_dns_role(
        self,
        slug: str,
        service: str,
        expected: str,
    ) -> None:
        info = _minimal_info(
            services=(service,),
            slugs=(slug,),
            evidence=(EvidenceRecord("NS", f"ns.{slug}.example", service, slug),),
        )

        categorized = categorize_services(info)

        assert categorized["Cloud"] == [expected]
        assert "CDN" not in categorized["Cloud"][0]

    def test_cloudflare_cname_can_render_an_edge_role(self) -> None:
        info = _minimal_info(
            services=("Cloudflare",),
            slugs=("cloudflare",),
            evidence=(EvidenceRecord("CNAME", "www.alpha.invalid -> edge.cloudflare.net", "Cloudflare", "cloudflare"),),
        )

        assert categorize_services(info)["Cloud"] == ["Cloudflare (CDN/edge)"]

    def test_cloudflare_txt_only_is_an_account_indicator_not_a_cdn(self) -> None:
        info = _minimal_info(
            services=("Cloudflare",),
            slugs=("cloudflare",),
            evidence=(EvidenceRecord("TXT", "cloudflare-verify=opaque", "Cloudflare", "cloudflare"),),
        )

        assert categorize_services(info)["Cloud"] == ["Cloudflare (public TXT account indicator)"]

    def test_evidence_linked_crowdstrike_alias_is_not_filed_twice(self) -> None:
        info = _minimal_info(
            services=("CrowdStrike",),
            slugs=("crowdstrike",),
            evidence=(
                EvidenceRecord(
                    "TXT",
                    "crowdstrike-falcon-site-verification=opaque",
                    "CrowdStrike",
                    "crowdstrike",
                ),
            ),
        )

        categorized = categorize_services(info)

        assert categorized == {"Security": ["CrowdStrike Falcon (public TXT account indicator)"]}

    def test_amazon_caa_authorization_is_not_rendered_as_a_cloud_workload(self) -> None:
        info = _minimal_info(
            services=("CAA: AWS Certificate Manager",),
            slugs=("aws-acm",),
            evidence=(EvidenceRecord("CAA", '0 issue "amazon.com"', "CAA: AWS Certificate Manager", "aws-acm"),),
        )

        categorized = categorize_services(info)

        assert categorized == {"Security": ["CAA: Amazon authorized"]}

    def test_legacy_amazon_caa_slug_marks_authorization_role_unavailable(self) -> None:
        info = _minimal_info(
            services=("CAA: AWS Certificate Manager",),
            slugs=("aws-acm",),
        )

        assert categorize_services(info) == {"Security": ["CAA: AWS Certificate Manager (role unavailable)"]}

    @pytest.mark.parametrize(
        ("slug", "service", "category"),
        [
            ("cloudflare", "Cloudflare", "Cloud"),
            ("aws-route53", "AWS Route 53", "Cloud"),
            ("slack", "Slack", "Collaboration"),
        ],
    )
    def test_legacy_slug_without_evidence_does_not_invent_a_role(
        self,
        slug: str,
        service: str,
        category: str,
    ) -> None:
        info = _minimal_info(services=(service,), slugs=(slug,))

        assert categorize_services(info)[category] == [f"{service} (role unavailable)"]


class TestCsvFormulaNeutralization:
    @pytest.mark.parametrize(
        "value",
        [
            '=HYPERLINK("https://example.invalid")',
            "+SUM(1,1)",
            "-SUM(1,1)",
            "@SUM(1,1)",
            "\t=SUM(1,1)",
            "\r=SUM(1,1)",
            "\n=SUM(1,1)",
            " =SUM(1,1)",
            " \t=SUM(1,1)",
        ],
    )
    def test_tenant_csv_row_neutralizes_formula_prefixes(self, value: str) -> None:
        row = format_tenant_csv_row(_minimal_info(display_name=value))
        rendered = row["display_name"]

        # Two guarantees: the cell is quoted so a spreadsheet treats it as
        # literal text, and control characters are removed first so the file is
        # also safe to `cat`. Stripping removes any leading tab, CR, or LF that
        # the raw value carried, so compare against the stripped original.
        from recon_tool.validator import strip_control_chars

        assert rendered.startswith("'")
        assert not any(char in rendered for char in "\t\r\n")
        assert rendered[1:] == strip_control_chars(value)

    def test_tenant_csv_row_leaves_safe_text_unchanged(self) -> None:
        row = format_tenant_csv_row(_minimal_info(display_name="Synthetic Alpha Ltd"))

        assert row["display_name"] == "Synthetic Alpha Ltd"

    def test_batch_csv_sanitizes_success_and_error_rows(self) -> None:
        info = _minimal_info(
            queried_domain="=tenant.example",
            display_name='=HYPERLINK("https://example.invalid")',
            tenant_id="+tenant-id",
            auth_type="@Managed",
            dmarc_policy="-reject",
            mta_sts_mode=" enforce",
            google_auth_type="\tmanaged",
        )

        text = format_batch_csv(
            [
                ("ignored.example", info, None),
                ("=error.example", None, "lookup failed"),
            ]
        )
        rows = list(csv.DictReader(io.StringIO(text)))

        assert rows[0]["domain"] == "'=tenant.example"
        assert rows[0]["display_name"].startswith("'=HYPERLINK")
        assert rows[0]["tenant_id"] == "'+tenant-id"
        assert rows[0]["auth_type"] == "'@Managed"
        assert rows[0]["dmarc_policy"] == "'-reject"
        assert rows[0]["mta_sts_mode"] == " enforce"
        # The leading tab is stripped as a control character, so the value is
        # no longer formula-shaped and needs no quote.
        assert rows[0]["google_auth_type"] == "managed"
        assert rows[1]["domain"] == "'=error.example"
        assert rows[0]["error"] == ""
        assert rows[1]["error"] == "lookup failed"


class TestDetectProviderEdgeCases:
    def test_topology_all_none_slugs_empty_returns_hedged_unknown(self) -> None:
        result = detect_provider(
            services=(),
            slugs=(),
            primary_email_provider=None,
            email_gateway=None,
            likely_primary_email_provider=None,
        )
        assert "Unknown" in result

    def test_gateway_only_no_primary_no_likely(self) -> None:
        result = detect_provider(
            services=(),
            slugs=(),
            primary_email_provider=None,
            email_gateway="Proofpoint",
            likely_primary_email_provider=None,
        )
        assert result == "Proofpoint gateway (MX delivery path; downstream unobserved)"

    def test_likely_only_no_primary_no_gateway(self) -> None:
        """A non-MX candidate remains a possible downstream indicator."""
        result = detect_provider(
            services=(),
            slugs=(),
            primary_email_provider=None,
            email_gateway=None,
            likely_primary_email_provider="Google Workspace",
        )
        assert result == "Google Workspace (possible downstream indicator)"

    def test_untyped_slug_does_not_gain_a_secondary_role_when_mx_path_is_set(self) -> None:
        result = detect_provider(
            services=(),
            slugs=("microsoft365", "google-workspace"),
            primary_email_provider="Microsoft 365",
            email_gateway=None,
        )
        assert result == "Microsoft 365 (MX delivery path)"

    def test_gateway_does_not_promote_untyped_account_slug(self) -> None:
        result = detect_provider(
            services=(),
            slugs=("microsoft365",),
            primary_email_provider=None,
            email_gateway="Proofpoint",
        )
        assert result == "Proofpoint gateway (MX delivery path; downstream unobserved)"

    def test_zoho_slug_fallback(self) -> None:
        # Default has_mx_records=True — assumes custom MX unless the
        # caller explicitly passes has_mx_records=False. See
        # TestBackwardCompatDetectProvider for the full rationale.
        result = detect_provider(services=(), slugs=("zoho",))
        assert result == "Zoho Mail (account indicator) + Custom or unclassified MX (MX delivery path)"

    def test_protonmail_slug_fallback(self) -> None:
        result = detect_provider(services=(), slugs=("protonmail",))
        assert result == "ProtonMail (account indicator) + Custom or unclassified MX (MX delivery path)"

    def test_aws_ses_only_slug(self) -> None:
        result = detect_provider(services=(), slugs=("aws-ses",))
        assert result == "AWS SES (account indicator) + Custom or unclassified MX (MX delivery path)"


class TestRenderTenantPanelEdgeCases:
    """Exercise render_tenant_panel branches that basic tests miss."""

    def test_empty_services_no_insights(self) -> None:
        _, buf = _make_console()
        info = _minimal_info()
        from recon_tool.formatter import get_console

        get_console().print(render_tenant_panel(info))
        out = _strip(buf.getvalue())
        assert "Synthetic Alpha" in out

    def test_with_cert_summary(self) -> None:
        _, buf = _make_console()
        info = _minimal_info(
            services=("DMARC", "BIMI"),
            cert_summary=CertSummary(
                cert_count=20,
                issuer_diversity=2,
                issuance_velocity=3,
                newest_cert_age_days=5,
                oldest_cert_age_days=100,
                top_issuers=("DigiCert", "Let's Encrypt"),
            ),
        )
        from recon_tool.formatter import get_console

        # Certs section is shown only under --verbose to keep
        # the default view tight. Pass verbose=True to exercise it.
        get_console().print(render_tenant_panel(info, verbose=True))
        out = _strip(buf.getvalue())
        assert "Certs" in out
        assert "20 total" in out
        assert "DigiCert" in out

    def test_degraded_sources_without_ct_provider(self) -> None:
        _, buf = _make_console()
        info = _minimal_info(
            services=("DMARC",),
            degraded_sources=("crt.sh", "certspotter"),
        )
        from recon_tool.formatter import get_console

        get_console().print(render_tenant_panel(info))
        out = _strip(buf.getvalue())
        # Format: "Note" header + "N sources unavailable (...)"
        assert "Note" in out
        assert "crt.sh" in out
        assert "unavailable" in out

    def test_ct_provider_without_degraded_suppresses_note(self) -> None:
        """When CT succeeded cleanly (no degraded sources),
        the panel does NOT show a Note line. The CT provenance is still
        available via --json and --verbose for users who need it; the
        panel stays uncluttered on the happy path."""
        _, buf = _make_console()
        info = _minimal_info(
            services=("DMARC",),
            ct_provider_used="crt.sh",
            ct_subdomain_count=42,
        )
        from recon_tool.formatter import get_console

        get_console().print(render_tenant_panel(info))
        out = _strip(buf.getvalue())
        assert "Note:" not in out

    def test_degraded_plus_ct_provider_fallback(self) -> None:
        """Routine CT fallback notes are suppressed in panel output.
        CT provenance is still available in --json."""
        _, buf = _make_console()
        info = _minimal_info(
            services=("DMARC",),
            degraded_sources=("crt.sh",),
            ct_provider_used="certspotter",
            ct_subdomain_count=87,
        )
        from recon_tool.formatter import get_console

        get_console().print(render_tenant_panel(info))
        out = _strip(buf.getvalue())
        # Routine CT fallback is suppressed — infrastructure noise
        assert "Note" not in out

    def test_related_domains_truncation(self) -> None:
        """More than 8 related domains shows a compact
        '(N total, M more, use --full to see all)' footer."""
        _, buf = _make_console()
        info = _minimal_info(
            services=("DMARC",),
            related_domains=tuple(f"sub{i}.alpha.invalid" for i in range(25)),
        )
        from recon_tool.formatter import get_console

        get_console().print(render_tenant_panel(info))
        out = _strip(buf.getvalue())
        assert "sub0.alpha.invalid" in out
        assert "25 total" in out
        assert "more" in out
        assert "--full" in out

    def test_related_domains_full_list_when_show_domains(self) -> None:
        """show_domains=True renders the complete related list."""
        _, buf = _make_console()
        info = _minimal_info(
            services=("DMARC",),
            related_domains=tuple(f"sub{i}.alpha.invalid" for i in range(15)),
        )
        from recon_tool.formatter import get_console

        get_console().print(render_tenant_panel(info, show_domains=True))
        out = _strip(buf.getvalue())
        assert "sub14.alpha.invalid" in out
        assert "and " not in out or "more" not in out.split("sub14.alpha.invalid")[1]

    def test_subdomain_summary_uses_aligned_lines_before_overflow(self) -> None:
        """Long provider names should not hide every other provider behind
        a single opaque overflow count in the default panel."""
        _, buf = _make_console()
        attributions = (
            *(
                SurfaceAttribution(
                    subdomain=f"azure{i}.alpha.invalid",
                    primary_slug="azure-app-service",
                    primary_name="Azure App Service",
                    primary_tier="infrastructure",
                )
                for i in range(33)
            ),
            *(
                SurfaceAttribution(
                    subdomain=f"proxy{i}.alpha.invalid",
                    primary_slug="microsoft-entra-application-proxy",
                    primary_name="Microsoft Entra Application Proxy",
                    primary_tier="application",
                )
                for i in range(12)
            ),
            *(
                SurfaceAttribution(
                    subdomain=f"front{i}.alpha.invalid",
                    primary_slug="azure-front-door",
                    primary_name="Azure Front Door",
                    primary_tier="infrastructure",
                )
                for i in range(9)
            ),
            SurfaceAttribution(
                subdomain="shop.alpha.invalid",
                primary_slug="shopify",
                primary_name="Shopify",
                primary_tier="application",
            ),
        )
        info = _minimal_info(
            services=("DMARC",),
            surface_attributions=attributions,
        )

        get_console().print(render_tenant_panel(info))
        out = _strip(buf.getvalue())

        assert "Subdomain      Azure App Service (33)" in out
        assert "Microsoft Entra Application Proxy (12)" in out
        assert "Azure Front Door (9)" in out
        assert "Shopify (1)" in out

    def test_m365_panel_with_tenant_id(self) -> None:
        _, buf = _make_console()
        info = _minimal_info(
            tenant_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            display_name="Synthetic Alpha Ltd",
            services=("Microsoft 365",),
            slugs=("microsoft365",),
            auth_type="Federated",
        )
        from recon_tool.formatter import get_console

        get_console().print(render_tenant_panel(info))
        out = _strip(buf.getvalue())
        # Format: the label is "Tenant" (no " ID:" suffix) and
        # the tenant UUID appears on the same line.
        assert "Tenant" in out
        assert "a1b2c3d4" in out

    def test_default_panel_keeps_compact_email_summary(self) -> None:
        """When Email dedupe would remove every email entry, keep a compact
        summary so the Services block does not look sparse."""
        _, buf = _make_console()
        info = _minimal_info(
            services=(
                "Apple Business",
                "DKIM",
                "DKIM (Exchange Online)",
                "DMARC",
                "Exchange Autodiscover",
                "Microsoft 365",
                "Mimecast",
                "SPF complexity: 4 includes",
                "SPF: softfail (~all)",
            ),
            slugs=("apple", "microsoft365", "mimecast"),
            dmarc_policy="quarantine",
            primary_email_provider="Microsoft 365",
            email_gateway="Mimecast",
            evidence=(
                EvidenceRecord("MX", "alpha-com.mail.protection.outlook.com", "Microsoft 365", "microsoft365"),
                EvidenceRecord("MX", "us-smtp-inbound.mimecast.com", "Mimecast", "mimecast"),
            ),
        )
        from recon_tool.formatter import get_console

        get_console().print(render_tenant_panel(info))
        out = _strip(buf.getvalue())
        assert "Email" in out
        assert "Microsoft 365" in out
        assert "Mimecast" in out
        assert "DMARC quarantine" in out
        assert "DKIM" in out
        assert "SPF softfail" in out
        assert "SPF complexity" not in out

    def test_mta_sts_none_is_not_listed_as_a_live_control(self) -> None:
        from recon_tool.formatter.email_summary import normalize_email_services

        info = _minimal_info(
            services=("Microsoft 365", "DMARC", "MTA-STS", "SPF: strict (-all)"),
            slugs=("microsoft365", "dmarc", "mta-sts", "spf-strict"),
            dmarc_policy="reject",
            mta_sts_mode="none",
            primary_email_provider="Microsoft 365",
            evidence=(
                EvidenceRecord("MX", "alpha-com.mail.protection.outlook.com", "Microsoft 365", "microsoft365"),
                EvidenceRecord("DMARC", "v=DMARC1; p=reject", "DMARC", "dmarc"),
                EvidenceRecord("MTA_STS", "v=STSv1", "MTA-STS", "mta-sts"),
                EvidenceRecord("MTA_STS_POLICY", "mode: none", "MTA-STS", "mta-sts"),
                EvidenceRecord("SPF", "v=spf1 -all", "SPF: strict (-all)", "spf-strict"),
            ),
        )
        categorized = {"Email": ["Microsoft 365", "DMARC", "MTA-STS", "SPF: strict (-all)"]}
        normalize_email_services(categorized, info)
        assert categorized["Email"] == ["Microsoft 365 (MX delivery path)", "DMARC reject", "SPF strict"]

    def test_permissive_spf_is_listed_as_observed(self) -> None:
        from recon_tool.formatter.email_summary import normalize_email_services

        info = _minimal_info(
            services=("Microsoft 365", "SPF record observed"),
            slugs=("microsoft365", "spf"),
            primary_email_provider="Microsoft 365",
            evidence=(
                EvidenceRecord("MX", "alpha-com.mail.protection.outlook.com", "Microsoft 365", "microsoft365"),
                EvidenceRecord("SPF", "v=spf1 +all", "SPF record observed", "spf"),
            ),
        )
        categorized = {"Email": ["Microsoft 365", "SPF record observed"]}
        normalize_email_services(categorized, info)
        assert categorized["Email"] == ["Microsoft 365 (MX delivery path)", "SPF observed"]

    def test_explain_flag_renders_classification(self) -> None:
        _, buf = _make_console()
        info = _minimal_info(
            services=("Microsoft 365", "Google Workspace"),
            slugs=("microsoft365", "google-workspace"),
            primary_email_provider="Microsoft 365",
            email_gateway="Proofpoint",
            evidence=(
                EvidenceRecord("MX", "mx.microsoft.example", "Microsoft 365", "microsoft365"),
                EvidenceRecord("MX", "mx.proofpoint.example", "Proofpoint", "proofpoint"),
            ),
        )
        from recon_tool.formatter import get_console

        assert provider_line(info) == ("Microsoft 365 (MX delivery path) + Proofpoint gateway (MX delivery path)")
        get_console().print(render_tenant_panel(info, explain=True))
        out = _strip(buf.getvalue())
        # Format: the Provider line carries the primary/gateway
        # classification inline. No separate "[Primary (MX): …]"
        # classification block.
        assert "Microsoft 365 (MX delivery path)" in out
        assert "Proofpoint gateway" in out


class TestRenderSourceStatusPanel:
    """render_source_status_panel for --explain output."""

    def test_empty_results_returns_none(self) -> None:
        assert render_source_status_panel([]) is None

    def test_mixed_success_and_failure(self) -> None:
        _, buf = _make_console()
        results = [
            SourceResult(
                source_name="oidc_discovery",
                tenant_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                region="NA",
            ),
            SourceResult(source_name="google_workspace", error="No Google Workspace configuration found"),
            SourceResult(source_name="dns_records", m365_detected=True, dmarc_policy="reject"),
        ]
        panel = render_source_status_panel(results)
        assert panel is not None
        from recon_tool.formatter import get_console

        get_console().print(panel)
        out = _strip(buf.getvalue())
        assert "oidc_discovery" in out
        assert "google_workspace" in out
        assert "No Google Workspace" in out
        assert "dns_records" in out
        assert "DMARC: reject" in out

    def test_all_failure(self) -> None:
        results = [
            SourceResult(source_name="oidc_discovery", error="HTTP 429"),
            SourceResult(source_name="dns_records", error="DNS error"),
        ]
        panel = render_source_status_panel(results)
        assert panel is not None


class TestRenderVerboseSources:
    def test_verbose_renders_success_and_failure(self) -> None:
        _, buf = _make_console()
        results = [
            SourceResult(
                source_name="oidc_discovery",
                tenant_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                region="NA",
            ),
            SourceResult(
                source_name="google_identity",
                error="No Google Workspace configuration found",
            ),
            SourceResult(source_name="user_realm", error="HTTP 403"),
        ]
        render_verbose_sources(results)
        out = _strip(buf.getvalue())
        assert "oidc_discovery" in out
        assert "tenant ID found" in out
        assert "no match google_identity" in out
        assert "No Google Workspace configuration found" in out
        assert "user_realm" in out
        assert "HTTP 403" in out

    def test_error_with_data_is_failed_in_every_source_view(self) -> None:
        result = SourceResult(
            source_name="user_realm",
            detected_services=("Microsoft 365",),
            error="upstream failed",
            source_unavailable=True,
        )

        _, buf = _make_console()
        render_verbose_sources([result])
        verbose = _strip(buf.getvalue())
        assert "unavailable user_realm" in verbose
        assert "upstream failed" in verbose
        assert "data returned" not in verbose

        _, buf = _make_console()
        panel = render_source_status_panel([result])
        assert panel is not None
        get_console().print(panel)
        status = _strip(buf.getvalue())
        assert "upstream failed" in status
        assert "data returned" not in status

        _, buf = _make_console()
        get_console().print(render_sources_detail([result]))
        detail = _strip(buf.getvalue())
        assert "unavailable" in detail
        assert "upstream failed" in detail

    def test_verbose_counts_match_the_health_line_for_nxdomain(self) -> None:
        """A negative realm answer is no match, and CT stays its own unit."""
        from recon_tool.formatter.source_ladder import LadderState

        results = [
            SourceResult(
                source_name="dns_records",
                degraded_sources=("crt.sh", "certspotter"),
            ),
            SourceResult(source_name="oidc_discovery"),
            SourceResult(
                source_name="user_realm",
                error="Could not resolve display name or default domain",
            ),
            SourceResult(source_name="google_identity"),
            SourceResult(
                source_name="google_workspace",
                error="No Google Workspace configuration found",
            ),
        ]
        _, buf = _make_console()
        render_verbose_sources(results)
        verbose = _strip(buf.getvalue())
        state = LadderState.planned(skip_ct=False, active_probes=False)
        state.finalize(results)
        health = state.health_line()
        assert health is not None
        expected = [(outcome.state, unit) for unit in state.units if (outcome := state.outcome(unit)) is not None]
        assert _verbose_rows(verbose) == expected
        assert "no match user_realm" in verbose
        assert "unavailable user_realm" not in verbose
        assert "unavailable ct" in verbose
        assert "google_workspace" not in verbose
        assert "mta_sts" in verbose

    def test_related_host_does_not_add_a_verbose_row(self) -> None:
        from recon_tool.formatter.source_ladder import LadderState

        results = [
            SourceResult(source_name="dns_records"),
            SourceResult(source_name="oidc_discovery"),
            SourceResult(source_name="user_realm"),
            SourceResult(source_name="google_identity"),
            SourceResult(source_name="dns_records", error="related-host residue"),
        ]
        _, buf = _make_console()
        render_verbose_sources(results)
        verbose = _strip(buf.getvalue())
        state = LadderState.planned(skip_ct=False, active_probes=False)
        state.finalize(results)
        rows = _verbose_rows(verbose)
        assert [unit for _state, unit in rows].count("dns_records") == 1
        assert len(rows) == sum(1 for unit in state.units if state.outcome(unit) is not None)
        assert "related-host residue" not in verbose

    def test_active_probe_adds_the_google_workspace_unit(self) -> None:
        results = [
            SourceResult(source_name="dns_records"),
            SourceResult(source_name="oidc_discovery"),
            SourceResult(source_name="user_realm"),
            SourceResult(source_name="google_identity"),
            SourceResult(source_name="google_workspace", error="No Google Workspace configuration found"),
        ]
        _, buf = _make_console()
        render_verbose_sources(results, active_probes=True)
        verbose = _strip(buf.getvalue())
        assert "no match google_workspace" in verbose
        assert "No Google Workspace configuration found" in verbose


def _verbose_rows(output: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for line in output.splitlines():
        if ":" not in line:
            continue
        head = line.split(":", 1)[0]
        padded = f" {head} "
        if " no match " in padded:
            state = "no_match"
        elif " unavailable " in padded:
            state = "unavailable"
        elif " match " in padded:
            state = "match"
        else:
            continue
        rows.append((state, head.strip().split()[-1]))
    return rows


class TestCsvStripsTerminalControlCharacters:
    """CSV must sanitize like every other text sink.

    ``display_name`` comes from the GetUserRealm ``FederationBrandName``
    response and is attacker-controllable for any looked-up domain. The panel,
    markdown, and plain-text sinks all strip control characters; CSV
    historically neutralized only spreadsheet formula prefixes, so a raw ESC,
    OSC, or BEL survived into the file and acted on the terminal as soon as the
    operator ran ``cat`` on it.
    """

    _HOSTILE = "Synthetic\x1b]0;pwned\x07\x1b[2J ‮dtL"

    def test_display_name_column_is_stripped(self) -> None:
        from recon_tool.formatter.serialize import format_tenant_csv_row
        from recon_tool.models import ConfidenceLevel, TenantInfo

        info = TenantInfo(
            tenant_id="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            display_name=self._HOSTILE,
            default_domain="synthetic.onmicrosoft.com",
            queried_domain="example.com",
            confidence=ConfidenceLevel.LOW,
        )
        rendered = "".join(format_tenant_csv_row(info).values())
        for forbidden in ("\x1b", "\x07", "‮"):
            assert forbidden not in rendered

    def test_batch_error_column_is_stripped(self) -> None:
        from recon_tool.formatter.serialize import format_batch_csv

        hostile_domain = "\x1b]0;PWNED\x07x"
        out = format_batch_csv([(hostile_domain, None, f"Invalid domain format: {hostile_domain}")])
        for forbidden in ("\x1b", "\x07"):
            assert forbidden not in out

    def test_formula_prefix_neutralization_still_applies(self) -> None:
        from recon_tool.formatter.serialize import _csv_safe

        assert _csv_safe('=HYPERLINK("http://evil.invalid")').startswith("'")
        assert _csv_safe("ordinary value") == "ordinary value"
