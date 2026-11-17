# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportPrivateUsage=none
"""Round-trip tests for the disk cache's TenantInfo serialization.

Covers every field that lives on TenantInfo, including the
topology fields (primary_email_provider, email_gateway, dmarc_pct,
likely_primary_email_provider) and the CT provider attribution and
name-provenance fields. Raises coverage on
cache.py from 60% toward 90%.

All fixtures use fabricated data only — no real company names.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

import pytest

from recon_tool.cache import (
    _CACHE_VERSION,
    DEFAULT_TTL,
    _safe_cache_path,
    cache_clear,
    cache_clear_all,
    cache_dir,
    cache_get,
    cache_put,
    tenant_info_from_dict,
    tenant_info_to_dict,
)
from recon_tool.cache_paths import bind_cache_directory
from recon_tool.models import (
    BIMIIdentity,
    CertSummary,
    ConfidenceLevel,
    DnsCatalogSummary,
    EvidenceRecord,
    MergeConflicts,
    TenantInfo,
    UnclassifiedDnsObservation,
)
from tests.cache_path_helpers import self_referencing_directory


def _complete_info() -> TenantInfo:
    """Build a TenantInfo with every field populated."""
    return TenantInfo(
        tenant_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        display_name="Synthetic Alpha Ltd",
        default_domain="alpha.onmicrosoft.com",
        queried_domain="alpha.invalid",
        confidence=ConfidenceLevel.HIGH,
        region="NA",
        sources=("oidc_discovery", "user_realm", "dns_records", "google_identity"),
        services=("Microsoft 365", "Google Workspace", "Cloudflare"),
        slugs=("microsoft365", "google-workspace", "cloudflare"),
        auth_type="Federated",
        dmarc_policy="reject",
        domain_count=2,
        tenant_domains=("alpha.invalid", "alpha.onmicrosoft.com"),
        related_domains=("api.alpha.invalid", "dev.alpha.invalid"),
        insights=("Federated auth", "Dual provider"),
        degraded_sources=("crt.sh",),
        cert_summary=CertSummary(
            cert_count=42,
            issuer_diversity=3,
            issuance_velocity=5,
            newest_cert_age_days=2,
            oldest_cert_age_days=365,
            top_issuers=("DigiCert", "Let's Encrypt", "Sectigo"),
        ),
        evidence=(
            EvidenceRecord(
                source_type="TXT",
                raw_value="MS=ms12345",
                rule_name="Microsoft 365",
                slug="microsoft365",
            ),
            EvidenceRecord(
                source_type="MX",
                raw_value="10 aspmx.l.google.com",
                rule_name="Google Workspace",
                slug="google-workspace",
            ),
        ),
        evidence_confidence=ConfidenceLevel.HIGH,
        inference_confidence=ConfidenceLevel.MEDIUM,
        detection_scores=(("microsoft365", "high"), ("cloudflare", "medium")),
        bimi_identity=BIMIIdentity(
            organization="Synthetic Alpha Ltd",
            country="US",
            state="WA",
            locality="Redmond",
        ),
        site_verification_tokens=("google-verify-token-xyz",),
        mta_sts_mode="enforce",
        google_auth_type="Managed",
        google_idp_name="Google",
        primary_email_provider="Microsoft 365",
        email_gateway="Proofpoint",
        dmarc_pct=100,
        likely_primary_email_provider=None,
        ct_provider_used="certspotter",
        ct_subdomain_count=87,
        ct_related_domains=("api.alpha.invalid", "dev.alpha.invalid"),
        merge_conflicts=MergeConflicts(
            tenant_id=(),
            display_name=(),
        ),
    )


def _posterior_payload() -> dict[str, object]:
    """Return one complete cached posterior observation for corruption tests."""
    return {
        "name": "m365_tenant",
        "posterior": 0.5,
        "interval_low": 0.4,
        "interval_high": 0.6,
        "n_eff": 1.0,
        "sparse": False,
    }


class TestRoundTripAllFields:
    """Every field survives a round-trip through tenant_info_to_dict and
    tenant_info_from_dict without loss."""

    def test_basic_fields(self) -> None:
        info = _complete_info()
        d = tenant_info_to_dict(info)
        restored = tenant_info_from_dict(d)
        assert restored.tenant_id == info.tenant_id
        assert restored.display_name == info.display_name
        assert restored.default_domain == info.default_domain
        assert restored.queried_domain == info.queried_domain
        assert restored.region == info.region
        assert restored.auth_type == info.auth_type
        assert restored.dmarc_policy == info.dmarc_policy
        assert restored.domain_count == info.domain_count

    def test_confidence_roundtrip(self) -> None:
        info = _complete_info()
        d = tenant_info_to_dict(info)
        restored = tenant_info_from_dict(d)
        assert restored.confidence == ConfidenceLevel.HIGH
        assert restored.evidence_confidence == ConfidenceLevel.HIGH
        assert restored.inference_confidence == ConfidenceLevel.MEDIUM

    def test_tuple_fields_roundtrip(self) -> None:
        info = _complete_info()
        restored = tenant_info_from_dict(tenant_info_to_dict(info))
        assert restored.sources == info.sources
        assert restored.services == info.services
        assert restored.slugs == info.slugs
        assert restored.tenant_domains == info.tenant_domains
        assert restored.related_domains == info.related_domains
        assert restored.ct_related_domains == info.ct_related_domains
        assert restored.insights == info.insights
        assert restored.degraded_sources == info.degraded_sources
        assert restored.site_verification_tokens == info.site_verification_tokens

    def test_cert_summary_roundtrip(self) -> None:
        info = _complete_info()
        restored = tenant_info_from_dict(tenant_info_to_dict(info))
        assert restored.cert_summary is not None
        assert restored.cert_summary.cert_count == 42
        assert restored.cert_summary.issuer_diversity == 3
        assert restored.cert_summary.issuance_velocity == 5
        assert restored.cert_summary.top_issuers == ("DigiCert", "Let's Encrypt", "Sectigo")

    def test_ct_attempt_outcome_roundtrips(self) -> None:
        from dataclasses import replace

        info = replace(_complete_info(), ct_attempt_outcome="live_success")
        restored = tenant_info_from_dict(tenant_info_to_dict(info))
        assert restored.ct_attempt_outcome == "live_success"

    def test_unvalidated_legacy_bimi_identity_is_not_cached(self) -> None:
        info = _complete_info()
        restored = tenant_info_from_dict(tenant_info_to_dict(info))
        assert restored.bimi_identity is None

    def test_evidence_records_roundtrip(self) -> None:
        info = _complete_info()
        restored = tenant_info_from_dict(tenant_info_to_dict(info))
        assert len(restored.evidence) == 2
        first = restored.evidence[0]
        assert first.source_type == "TXT"
        assert first.slug == "microsoft365"
        assert first.raw_value == "MS=ms12345"
        assert first.rule_name == "Microsoft 365"

    def test_detection_scores_roundtrip(self) -> None:
        info = _complete_info()
        restored = tenant_info_from_dict(tenant_info_to_dict(info))
        # Order may not be preserved (dict → tuple), so compare as sets
        assert set(restored.detection_scores) == set(info.detection_scores)

    def test_v091_topology_fields_roundtrip(self) -> None:
        """Topology fields must persist through the cache."""
        info = _complete_info()
        restored = tenant_info_from_dict(tenant_info_to_dict(info))
        assert restored.primary_email_provider == "Microsoft 365"
        assert restored.email_gateway == "Proofpoint"
        assert restored.dmarc_pct == 100
        assert restored.likely_primary_email_provider is None

    def test_v092_ct_provenance_roundtrip(self) -> None:
        """CT provider attribution must persist through the cache."""
        info = _complete_info()
        restored = tenant_info_from_dict(tenant_info_to_dict(info))
        assert restored.ct_provider_used == "certspotter"
        assert restored.ct_subdomain_count == 87

    def test_google_workspace_fields_roundtrip(self) -> None:
        info = _complete_info()
        restored = tenant_info_from_dict(tenant_info_to_dict(info))
        assert restored.google_auth_type == "Managed"
        assert restored.google_idp_name == "Google"
        assert restored.mta_sts_mode == "enforce"

    def test_empty_display_name_roundtrip(self) -> None:
        from dataclasses import replace

        info = replace(_complete_info(), display_name="")
        restored = tenant_info_from_dict(tenant_info_to_dict(info))
        assert restored.display_name == ""

    def test_likely_primary_roundtrip_when_set(self) -> None:
        """Symmetric check: when likely_primary is populated and primary
        is None (gateway-fronted domain), round-trip preserves both."""
        from dataclasses import replace

        base = _complete_info()
        info = replace(
            base,
            primary_email_provider=None,
            likely_primary_email_provider="Google Workspace",
            email_gateway="Proofpoint",
        )
        restored = tenant_info_from_dict(tenant_info_to_dict(info))
        assert restored.primary_email_provider is None
        assert restored.likely_primary_email_provider == "Google Workspace"
        assert restored.email_gateway == "Proofpoint"

    def test_shared_verification_tokens_are_not_cached(self) -> None:
        from dataclasses import replace

        info = replace(
            _complete_info(),
            shared_verification_tokens=(("MS=ms12345", "gamma.invalid"),),
        )

        data = tenant_info_to_dict(info)
        assert "shared_verification_tokens" not in data

        restored = tenant_info_from_dict(data)
        assert restored.shared_verification_tokens == ()


class TestCacheDiskOperations:
    """Exercise the cache_put / cache_get disk I/O paths in isolated temp dirs."""

    @pytest.fixture(autouse=True)
    def _isolated_cache(self, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
        with tempfile.TemporaryDirectory() as tmp:
            monkeypatch.setenv("RECON_CONFIG_DIR", tmp)
            yield

    def test_put_then_get_roundtrip(self) -> None:
        info = _complete_info()
        cache_put("alpha.invalid", info)
        restored = cache_get("alpha.invalid")
        assert restored is not None
        assert restored.tenant_id == info.tenant_id
        assert restored.display_name == info.display_name

    def test_get_rejects_entry_bound_to_another_domain(self) -> None:
        cache_dir().mkdir(parents=True, exist_ok=True)
        payload = tenant_info_to_dict(_complete_info())
        (cache_dir() / "beta.invalid.json").write_text(json.dumps(payload), encoding="utf-8")

        assert cache_get("beta.invalid") is None

    def test_put_rejects_entry_bound_to_another_domain(self) -> None:
        cache_put("beta.invalid", _complete_info())

        assert not (cache_dir() / "beta.invalid.json").exists()

    def test_put_normalizes_url_input_to_literal_cache_key(self) -> None:
        from dataclasses import replace

        info = replace(_complete_info(), queried_domain="www.alpha.invalid")

        cache_put("https://www.alpha.invalid/path?utm=1", info)

        assert (cache_dir() / "www.alpha.invalid.json").exists()
        assert cache_get("alpha.invalid") is None
        assert cache_get("https://www.alpha.invalid/path") is not None

    def test_exact_subhost_does_not_reuse_apex_cache_entry(self) -> None:
        cache_put("alpha.invalid", _complete_info())

        assert cache_get("mail.alpha.invalid") is None

    def test_exact_subhost_has_an_independent_cache_key(self) -> None:
        from dataclasses import replace

        exact_info = replace(_complete_info(), queried_domain="mail.alpha.invalid")
        cache_put("mail.alpha.invalid", exact_info)

        assert cache_get("mail.alpha.invalid") is not None
        assert cache_get("alpha.invalid") is None

    def test_future_mtime_is_rejected(self) -> None:
        cache_put("alpha.invalid", _complete_info())
        path = cache_dir() / "alpha.invalid.json"
        future = time.time() + 365 * 86400
        os.utime(path, (future, future))

        assert cache_get("alpha.invalid") is None

    def test_write_binds_one_resolved_cache_directory(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        first = tmp_path / "first"
        second = tmp_path / "second"
        directories = iter((first, second))
        monkeypatch.setattr("recon_tool.paths.cache_root", lambda: next(directories))

        cache_put("alpha.invalid", _complete_info())

        assert (first / "cache" / "alpha.invalid.json").exists()
        assert not (second / "cache" / "alpha.invalid.json").exists()

    def test_get_missing_returns_none(self) -> None:
        assert cache_get("does-not-exist.invalid") is None

    def test_get_rejects_traversal_domain(self) -> None:
        assert cache_get("..\\secrets") is None

    def test_get_corrupt_json_returns_none(self) -> None:
        cache_dir().mkdir(parents=True, exist_ok=True)
        (cache_dir() / "bad.invalid.json").write_text("not valid json{{{", encoding="utf-8")
        assert cache_get("bad.invalid") is None

    def test_get_non_object_json_returns_none(self) -> None:
        cache_dir().mkdir(parents=True, exist_ok=True)
        (cache_dir() / "bad.invalid.json").write_text("[]", encoding="utf-8")
        assert cache_get("bad.invalid") is None

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("services", "Mail"),
            ("domain_count", 1e999),
            # Negative and out-of-range integers: the float case above is
            # rejected on type alone, so nothing else exercised the range
            # clauses that keep a poisoned count out of a rendered record.
            ("domain_count", -1),
            ("domain_count", 2**40),
            ("spf_include_count", -5),
            ("ct_subdomain_count", 2**63),
            ("auth_type", 123),
            ("confidence", "garbage"),
            ("evidence_confidence", "garbage"),
            ("inference_confidence", "garbage"),
            ("dmarc_testing", "false"),
            ("slug_confidences", {"poison": float("inf")}),
            ("slug_confidences", {"poison": 1.01}),
            ("dmarc_pct", 101),
            ("posterior_observations", "corrupt"),
            ("posterior_observations", [None]),
        ],
    )
    def test_get_valid_object_with_invalid_field_shape_returns_none(self, field: str, value: object) -> None:
        cache_dir().mkdir(parents=True, exist_ok=True)
        payload = tenant_info_to_dict(_complete_info())
        payload[field] = value
        # Key the file to the payload's own queried_domain. Keying it to an
        # unrelated name made cache_get reject on the domain binding, which is
        # already covered by test_get_rejects_entry_bound_to_another_domain,
        # before it ever reached the poisoned field, so every row of this table
        # passed without exercising the value guard it names.
        (cache_dir() / "alpha.invalid.json").write_text(json.dumps(payload), encoding="utf-8")
        assert cache_get("alpha.invalid") is None

    def test_unpoisoned_control_payload_is_still_admitted(self) -> None:
        """Keeps the poisoned-field table above from silently going vacuous again.

        Every row of that table asserts a rejection, so any change that makes
        the fixture unreadable for an unrelated reason turns the whole table
        green while testing nothing. This control fails in that case.
        """
        cache_dir().mkdir(parents=True, exist_ok=True)
        payload = tenant_info_to_dict(_complete_info())
        (cache_dir() / "alpha.invalid.json").write_text(json.dumps(payload), encoding="utf-8")

        assert cache_get("alpha.invalid") is not None

    def test_get_rejects_non_boolean_legacy_degradation_flag(self) -> None:
        cache_dir().mkdir(parents=True, exist_ok=True)
        payload = tenant_info_to_dict(_complete_info())
        payload.pop("degraded_sources")
        payload["crtsh_degraded"] = "false"
        (cache_dir() / "bad.invalid.json").write_text(json.dumps(payload), encoding="utf-8")
        assert cache_get("bad.invalid") is None

    def test_get_rejects_non_boolean_posterior_sparse_flag(self) -> None:
        cache_dir().mkdir(parents=True, exist_ok=True)
        payload = tenant_info_to_dict(_complete_info())
        payload["posterior_observations"] = [
            {
                "name": "m365_tenant",
                "posterior": 0.5,
                "interval_low": 0.4,
                "interval_high": 0.6,
                "sparse": 1,
            }
        ]
        (cache_dir() / "bad.invalid.json").write_text(json.dumps(payload), encoding="utf-8")
        assert cache_get("bad.invalid") is None

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("conflict_provenance", "corrupt"),
            ("conflict_provenance", [None]),
            ("conflict_provenance", [{"field": 7, "sources": ["dns"], "magnitude": 0.1}]),
            ("conflict_provenance", [{"field": "provider", "sources": [7], "magnitude": 0.1}]),
            ("evidence_ranked", [{"kind": 7, "name": "dns", "llr": 1.0}]),
            ("evidence_ranked", [{"kind": "dns", "name": "MX", "llr": None}]),
            (
                "unit_counterfactuals",
                [{"unit": 7, "kind": "MX", "observed": "mail", "posterior_without": 0.4, "delta": 0.1}],
            ),
            (
                "unit_counterfactuals",
                [{"unit": "mx", "kind": "MX", "observed": "mail", "posterior_without": 0.4}],
            ),
        ],
    )
    def test_get_rejects_malformed_nested_posterior_diagnostics(self, field: str, value: object) -> None:
        cache_dir().mkdir(parents=True, exist_ok=True)
        payload = tenant_info_to_dict(_complete_info())
        observation = _posterior_payload()
        observation[field] = value
        payload["posterior_observations"] = [observation]
        (cache_dir() / "bad.invalid.json").write_text(json.dumps(payload), encoding="utf-8")

        assert cache_get("bad.invalid") is None

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("posterior", 1.01),
            ("posterior", None),
            ("interval_low", -0.01),
            ("interval_low", None),
            ("interval_high", 1.01),
            ("interval_high", None),
            ("n_eff", -1.0),
        ],
    )
    def test_get_rejects_out_of_range_posterior_values(self, field: str, value: object) -> None:
        cache_dir().mkdir(parents=True, exist_ok=True)
        payload = tenant_info_to_dict(_complete_info())
        observation = _posterior_payload()
        observation[field] = value
        payload["posterior_observations"] = [observation]
        (cache_dir() / "bad.invalid.json").write_text(json.dumps(payload), encoding="utf-8")

        assert cache_get("bad.invalid") is None

    @pytest.mark.parametrize(
        ("interval_low", "posterior", "interval_high"),
        [(0.6, 0.5, 0.8), (0.2, 0.9, 0.8), (0.8, 0.5, 0.2)],
    )
    def test_get_rejects_impossible_posterior_intervals(
        self, interval_low: float, posterior: float, interval_high: float
    ) -> None:
        cache_dir().mkdir(parents=True, exist_ok=True)
        payload = tenant_info_to_dict(_complete_info())
        observation = _posterior_payload()
        observation.update({"interval_low": interval_low, "posterior": posterior, "interval_high": interval_high})
        payload["posterior_observations"] = [observation]
        (cache_dir() / "bad.invalid.json").write_text(json.dumps(payload), encoding="utf-8")

        assert cache_get("bad.invalid") is None

    def test_get_old_cache_version_returns_none(self) -> None:
        cache_dir().mkdir(parents=True, exist_ok=True)
        data = tenant_info_to_dict(_complete_info())
        data["_cache_version"] = _CACHE_VERSION - 1
        (cache_dir() / "alpha.invalid.json").write_text(json.dumps(data), encoding="utf-8")
        assert cache_get("alpha.invalid") is None

    def test_get_stale_returns_none(self) -> None:
        """Files older than TTL are evicted lazily by cache_get."""
        info = _complete_info()
        cache_put("alpha.invalid", info)
        # Age the file past the TTL
        path = cache_dir() / "alpha.invalid.json"
        old = time.time() - (DEFAULT_TTL + 10)
        os.utime(path, (old, old))
        assert cache_get("alpha.invalid", ttl=DEFAULT_TTL) is None

    def test_get_fresh_survives_zero_ttl_query_with_larger_ttl(self) -> None:
        """A fresh file is returned as long as the caller's TTL covers it."""
        info = _complete_info()
        cache_put("alpha.invalid", info)
        # Fresh file, caller uses default TTL → hit
        assert cache_get("alpha.invalid") is not None

    def test_put_creates_cache_directory_if_missing(self) -> None:
        """cache_put should create the cache directory on first write."""
        # Remove the cache dir if it already exists from an earlier call
        import shutil

        if cache_dir().exists():
            shutil.rmtree(cache_dir())
        assert not cache_dir().exists()
        cache_put("alpha.invalid", _complete_info())
        assert cache_dir().exists()
        assert (cache_dir() / "alpha.invalid.json").exists()

    def test_put_rejects_traversal_domain(self) -> None:
        cache_put("..\\escape", _complete_info())
        if cache_dir().exists():
            assert list(cache_dir().glob("*.json")) == []

    def test_clear_deletes_valid_cache_entry(self) -> None:
        cache_put("alpha.invalid", _complete_info())

        assert cache_clear("alpha.invalid") is True
        assert not (cache_dir() / "alpha.invalid.json").exists()

    def test_clear_rejects_traversal_and_preserves_sibling_json(self) -> None:
        outside = cache_dir().parent / "outside.json"
        outside.write_text('{"keep": true}', encoding="utf-8")

        assert cache_clear("../outside") is False
        assert outside.exists()
        assert outside.read_text(encoding="utf-8") == '{"keep": true}'

    def test_clear_rejects_sibling_prefix_traversal(self) -> None:
        sibling_dir = cache_dir().parent / "cache-evil"
        sibling_dir.mkdir(parents=True)
        outside = sibling_dir / "settings.json"
        outside.write_text('{"keep": true}', encoding="utf-8")

        assert cache_clear("../cache-evil/settings") is False
        assert outside.exists()

    def test_clear_all_deletes_only_top_level_json_cache_entries(self) -> None:
        cache_put("alpha.invalid", _complete_info())
        d = cache_dir()
        nested = d / "nested"
        nested.mkdir()
        keep_nested = nested / "nested.invalid.json"
        keep_nested.write_text('{"keep": true}', encoding="utf-8")
        keep_text = d / "notes.txt"
        keep_text.write_text("keep", encoding="utf-8")

        assert cache_clear_all() == 1
        assert not (d / "alpha.invalid.json").exists()
        assert keep_nested.exists()
        assert keep_text.exists()

    def test_redirected_cache_directory_cannot_escape_configured_root(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        configured_root = tmp_path / "configured"
        external = tmp_path / "external"
        configured_root.mkdir()
        external.mkdir()
        redirected = configured_root / "cache"
        if os.name == "nt":
            command_processor = os.environ.get("COMSPEC", r"C:\Windows\System32\cmd.exe")
            subprocess.run(  # noqa: S603 - controlled test-only paths create a local junction
                [command_processor, "/d", "/c", "mklink", "/J", str(redirected), str(external)],
                check=True,
                capture_output=True,
                text=True,
            )
        else:
            redirected.symlink_to(external, target_is_directory=True)

        monkeypatch.setenv("RECON_CONFIG_DIR", str(configured_root))
        sentinel = external / "alpha.invalid.json"
        original = b'{"outside": true}'
        sentinel.write_bytes(original)

        assert _safe_cache_path("alpha.invalid") is None
        assert cache_get("alpha.invalid") is None
        cache_put("alpha.invalid", _complete_info())
        assert sentinel.read_bytes() == original
        assert cache_clear("alpha.invalid") is False
        assert cache_clear_all() == 0
        assert sentinel.read_bytes() == original

    def test_self_referencing_cache_directory_degrades_without_raising(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        configured_root = tmp_path / "configured-loop"
        configured_root.mkdir()
        redirected = configured_root / "cache"
        monkeypatch.setenv("RECON_CONFIG_DIR", str(configured_root))

        with self_referencing_directory(redirected):
            assert _safe_cache_path("alpha.invalid") is None
            assert cache_get("alpha.invalid") is None
            cache_put("alpha.invalid", _complete_info())
            assert cache_clear("alpha.invalid") is False
            assert cache_clear_all() == 0


class TestCacheDirRespectsEnvVar:
    def test_env_var_overrides_default(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("RECON_CONFIG_DIR", str(tmp_path))
        assert cache_dir() == tmp_path / "cache"

    def test_default_legacy_when_recon_dir_present(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        # Back-compat: an existing ~/.recon keeps being used.
        monkeypatch.delenv("RECON_CONFIG_DIR", raising=False)
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        (tmp_path / ".recon").mkdir()
        assert cache_dir() == tmp_path / ".recon" / "cache"

    def test_default_xdg_when_no_legacy_dir(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        # Fresh install (no ~/.recon): XDG cache home.
        monkeypatch.delenv("RECON_CONFIG_DIR", raising=False)
        monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        assert cache_dir() == tmp_path / ".cache" / "recon" / "cache"


class TestDictShape:
    """The serialized dict shape matches what callers expect."""

    def test_dict_has_cache_metadata(self) -> None:
        d = tenant_info_to_dict(_complete_info())
        assert "_cache_version" in d
        assert "_cached_at" in d
        # _cached_at is an ISO 8601 string with timezone info
        parsed = datetime.fromisoformat(d["_cached_at"])
        assert parsed.tzinfo is not None

    def test_dict_is_json_serializable(self) -> None:
        d = tenant_info_to_dict(_complete_info())
        # Should serialize cleanly — no sets, datetimes, etc.
        serialized = json.dumps(d)
        parsed = json.loads(serialized)
        assert parsed["tenant_id"] == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

    def test_from_dict_handles_missing_new_fields(self) -> None:
        """A dict from an older cache version (no v0.9.2 fields) still
        restores into a valid TenantInfo — the new fields default to None
        / 0 instead of raising KeyError."""
        d = tenant_info_to_dict(_complete_info())
        # Strip out the v0.9.2 fields to simulate an older cache entry
        d.pop("ct_provider_used", None)
        d.pop("ct_subdomain_count", None)
        d.pop("ct_related_domains", None)
        restored = tenant_info_from_dict(d)
        assert restored.ct_provider_used is None
        assert restored.ct_subdomain_count == 0
        assert restored.ct_related_domains == ()

    def test_from_dict_preserves_tuple_input_compatibility(self) -> None:
        data = tenant_info_to_dict(_complete_info())
        data["sources"] = tuple(data["sources"])
        assert tenant_info_from_dict(data).sources == _complete_info().sources

    def test_from_dict_handles_missing_v091_fields(self) -> None:
        """Even older cache dicts (pre-v0.9.1) without topology fields
        should still deserialize — the fields default to None."""
        d = tenant_info_to_dict(_complete_info())
        d.pop("primary_email_provider", None)
        d.pop("email_gateway", None)
        d.pop("dmarc_pct", None)
        d.pop("likely_primary_email_provider", None)
        restored = tenant_info_from_dict(d)
        assert restored.primary_email_provider is None
        assert restored.email_gateway is None
        assert restored.dmarc_pct is None
        assert restored.likely_primary_email_provider is None


# Needed for os.utime in test_get_stale_returns_none
import time

# ── chain_motifs + v1.7 cert_summary fields round-trip ────────


class TestChainMotifsRoundTrip:
    """Regression test: pre-fix, the cache silently dropped
    ``chain_motifs`` and the v1.7 ``cert_summary`` extensions
    (``wildcard_sibling_clusters``, ``deployment_bursts``). A cached
    lookup served zero motifs even when the original resolve produced
    matches, which is what masked the v1.8 motif library's coverage
    gap during the deep-dive validation.
    """

    def test_chain_motifs_round_trip(self) -> None:
        from dataclasses import replace

        from recon_tool.cache import tenant_info_from_dict, tenant_info_to_dict
        from recon_tool.models import ChainMotifObservation

        info = replace(
            _complete_info(),
            chain_motifs=(
                ChainMotifObservation(
                    motif_name="tm_to_azurefd",
                    display_name="Azure Traffic Manager → Azure Front Door",
                    confidence="medium",
                    subdomain="api.example.com",
                    chain=("foo.trafficmanager.net", "bar.azurefd.net"),
                ),
            ),
        )
        restored = tenant_info_from_dict(tenant_info_to_dict(info))
        assert len(restored.chain_motifs) == 1
        assert restored.chain_motifs[0].motif_name == "tm_to_azurefd"
        assert restored.chain_motifs[0].chain == (
            "foo.trafficmanager.net",
            "bar.azurefd.net",
        )

    def test_v17_cert_summary_extensions_round_trip(self) -> None:
        from dataclasses import replace

        from recon_tool.cache import tenant_info_from_dict, tenant_info_to_dict
        from recon_tool.models import CertBurst, CertSummary

        info = replace(
            _complete_info(),
            cert_summary=CertSummary(
                cert_count=10,
                issuer_diversity=2,
                issuance_velocity=5,
                newest_cert_age_days=1,
                oldest_cert_age_days=200,
                top_issuers=("DigiCert",),
                wildcard_sibling_clusters=(("a.example.com", "b.example.com"),),
                deployment_bursts=(
                    CertBurst(
                        window_start="2025-04-01T00:00:00Z",
                        window_end="2025-04-01T00:00:30Z",
                        span_seconds=30,
                        names=("c.example.com", "d.example.com", "e.example.com"),
                    ),
                ),
            ),
        )
        restored = tenant_info_from_dict(tenant_info_to_dict(info))
        assert restored.cert_summary is not None
        assert restored.cert_summary.wildcard_sibling_clusters == (("a.example.com", "b.example.com"),)
        assert len(restored.cert_summary.deployment_bursts) == 1
        burst = restored.cert_summary.deployment_bursts[0]
        assert burst.span_seconds == 30
        assert "c.example.com" in burst.names


def test_catalog_discovery_payload_survives_the_cache_round_trip() -> None:
    """`--include-unclassified` must not report an empty catalog on a cache hit.

    Only `unclassified_cname_chains` was persisted, so after any prior lookup of
    the domain the discovery path served zero summaries and no unclassified
    observations for the whole TTL, which reads as "nothing unclassified"
    rather than "not measured".
    """
    info = TenantInfo(
        tenant_id=None,
        display_name="example.invalid",
        default_domain="example.invalid",
        queried_domain="example.invalid",
        confidence=ConfidenceLevel.LOW,
        dns_catalog_summaries=(
            DnsCatalogSummary(
                record_type="txt",
                opportunity_count=9,
                observed_count=7,
                classified_count=2,
                truncated=True,
            ),
        ),
        unclassified_dns_observations=(
            UnclassifiedDnsObservation(record_type="txt", owner="example.invalid", value="vendor-verify=abc"),
        ),
    )

    restored = tenant_info_from_dict(tenant_info_to_dict(info))

    assert restored.dns_catalog_summaries == info.dns_catalog_summaries
    assert restored.unclassified_dns_observations == info.unclassified_dns_observations


def test_bound_cache_enumerates_only_the_open_directory(tmp_path: Path) -> None:
    layer = tmp_path / "cache"
    layer.mkdir()
    (layer / "original.test.json").touch()
    with bind_cache_directory(layer, enumerate_names=True, mutate=True) as bound:
        if os.name == "nt":
            with pytest.raises(PermissionError):
                layer.rename(tmp_path / "previous")
        else:
            layer.rename(tmp_path / "previous")
            layer.mkdir()
            (layer / "new.test.json").touch()
        assert [name for name in bound.names() if name.endswith(".json")] == ["original.test.json"]
        bound.unlink("original.test.json")
    if os.name != "nt":
        assert (layer / "new.test.json").is_file()
