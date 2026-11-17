# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportMissingTypeArgument=none, reportPrivateUsage=none, reportUnknownArgumentType=none
# pyright: reportUnknownMemberType=none, reportUnknownParameterType=none, reportUnknownVariableType=none
"""Observation-capsule integrity, replay, and comparison tests."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

import recon_tool.capsule as capsule_module
from recon_tool.capsule import (
    CollectionContext,
    build_capsule,
    compare_capsules,
    load_capsule,
    parse_utc_time,
    project_source_observations,
    replay_capsule,
    validate_capsule,
    write_capsule,
)
from recon_tool.models import ConfidenceLevel, EvidenceRecord, SourceResult, TenantInfo

_START = datetime(2026, 8, 13, 12, 0, 0, tzinfo=UTC)
_END = _START + timedelta(seconds=3)


def _evidence(value: str = "v=DMARC1; p=reject") -> EvidenceRecord:
    return EvidenceRecord("TXT", value, "DMARC", "dmarc")


def _info(*, evidence: tuple[EvidenceRecord, ...] | None = None, domain: str = "example.com") -> TenantInfo:
    retained = evidence if evidence is not None else (_evidence(),)
    return TenantInfo(
        tenant_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        display_name="Example Industries Ltd",
        default_domain="example-industries.onmicrosoft.example.com",
        queried_domain=domain,
        confidence=ConfidenceLevel.HIGH,
        sources=("dns_records", "openid_configuration"),
        services=("DMARC", "Microsoft 365"),
        slugs=("dmarc", "microsoft365"),
        dmarc_policy="reject",
        evidence=retained,
        insights=("Multiple cloud-vendor catalog indicators co-observed; provider roles and diversity are unresolved",),
        resolved_at=_END.isoformat(),
        ct_attempt_outcome="skipped",
    )


def _dns_result(*, evidence: tuple[EvidenceRecord, ...] | None = None, unavailable: bool = False) -> SourceResult:
    retained = evidence if evidence is not None else (_evidence(),)
    return SourceResult(
        source_name="dns_records",
        dmarc_policy=None if unavailable else "reject",
        raw_dns_records=() if unavailable else tuple(("TXT", item.raw_value) for item in retained),
        evidence=() if unavailable else retained,
        ct_attempt_outcome=None if unavailable else "skipped",
        source_unavailable=unavailable,
        error="timeout" if unavailable else None,
    )


def _oidc_result() -> SourceResult:
    return SourceResult(
        source_name="openid_configuration",
        tenant_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        display_name="Example Industries Ltd",
        default_domain="example-industries.onmicrosoft.example.com",
        m365_detected=True,
    )


def _capsule(
    *,
    info: TenantInfo | None = None,
    results: tuple[SourceResult, ...] | None = None,
    vantage: str = "caller-local",
) -> dict:
    return build_capsule(
        info or _info(),
        results or (_dns_result(), _oidc_result()),
        CollectionContext(
            started_at=_START,
            ended_at=_END,
            ct_enabled=False,
            direct_probes=False,
            timeout_seconds=30.0,
            vantage=vantage,
        ),
    )


def test_capsule_is_deterministic_and_source_order_independent() -> None:
    first = _capsule()
    second = _capsule(results=(_oidc_result(), _dns_result()))
    assert first == second
    assert first["content_digest"].startswith("sha256:")
    assert first["interpretation"]["stable_signal_ids"] == ["Multi-Cloud"]


def test_capsule_retains_raw_observations_and_opportunity_windows() -> None:
    capsule = _capsule()
    retained = [fact for fact in capsule["observations"] if fact["kind"] == "retained_dns_record"]
    assert retained == [
        {
            "fact_id": retained[0]["fact_id"],
            "source_role": "dns_records",
            "kind": "retained_dns_record",
            "key": "TXT",
            "value": "v=DMARC1; p=reject",
        }
    ]
    dns = next(row for row in capsule["source_opportunities"] if row["source_role"] == "dns_records")
    assert dns["state"] == "observed_value"
    assert dns["observation_window"] == {
        "started_at": _START.isoformat(),
        "ended_at": _END.isoformat(),
    }


def test_unattempted_source_has_no_observation_opportunity() -> None:
    skipped = SourceResult(source_name="google_workspace", not_attempted=True)
    capsule = _capsule(results=(_dns_result(), skipped))
    assert [row["source_role"] for row in capsule["source_opportunities"]] == ["dns_records"]
    assert all(fact["source_role"] != "google_workspace" for fact in capsule["observations"])


@pytest.mark.parametrize(
    "attempted",
    [
        SourceResult(source_name="optional_source"),
        SourceResult(source_name="optional_source", default_domain="example.com"),
        SourceResult(source_name="optional_source", error="no match"),
        SourceResult(source_name="optional_source", error="timeout", source_unavailable=True),
        SourceResult(source_name="optional_source", degraded_sources=("optional:identity",)),
    ],
)
def test_unattempted_instances_do_not_change_attempted_opportunity(attempted: SourceResult) -> None:
    skipped = SourceResult(source_name=attempted.source_name, not_attempted=True)
    window = {"started_at": _START.isoformat(), "ended_at": _END.isoformat()}
    assert project_source_observations([attempted, skipped], **window) == project_source_observations(
        [attempted], **window
    )


def test_comparison_with_disabled_probe_withholds_observation_change() -> None:
    attempted = SourceResult(source_name="optional_source", default_domain="example.com")
    before = _capsule(results=(_dns_result(), attempted))
    after = _capsule(results=(_dns_result(), replace(attempted, not_attempted=True)))
    result = compare_capsules(before, after)
    assert result["observation"]["changed"] is False
    assert result["observation"]["suppressed_source_roles"] == ["optional_source"]
    assert result["collection_regime"]["changed"] is True


def test_capsule_rejects_opportunity_window_outside_collection() -> None:
    capsule = _capsule()
    capsule["source_opportunities"][0]["observation_window"]["ended_at"] = (_END + timedelta(seconds=1)).isoformat()
    capsule["content_digest"] = capsule_module._sha256(capsule_module._without_digest(capsule))
    with pytest.raises(ValueError, match="must match collection window"):
        validate_capsule(capsule)


def test_capsule_replay_is_offline_and_deterministic(monkeypatch: pytest.MonkeyPatch) -> None:
    capsule = _capsule()

    def forbidden_network(*_args: object, **_kwargs: object) -> None:
        pytest.fail("replay attempted a network call")

    monkeypatch.setattr("recon_tool.resolver.resolve_tenant", forbidden_network)
    first = replay_capsule(capsule)
    second = replay_capsule(capsule)
    assert first == second
    assert first["replayed_result_digest"] == capsule["interpretation"]["rendered_result_digest"]
    assert first["time_evaluation_changed"] is False
    assert first["result"]["queried_domain"] == "example.com"


def test_replay_with_explicit_as_of_changes_only_time_metadata() -> None:
    capsule = _capsule()
    baseline = replay_capsule(capsule)
    later = replay_capsule(capsule, as_of="2026-08-14T12:00:03Z")
    assert later["time_evaluation_changed"] is True
    assert later["result"] == baseline["result"]
    assert later["replayed_result_digest"] == baseline["replayed_result_digest"]


def test_compare_identical_capsules_has_no_changes() -> None:
    result = compare_capsules(_capsule(), _capsule())
    assert result["has_changes"] is False
    assert result["observation"] == {
        "changed": False,
        "added": [],
        "removed": [],
        "suppressed_source_roles": [],
    }


def test_compare_reports_observation_delta_with_role_and_windows() -> None:
    before = _capsule()
    added_evidence = (_evidence(), EvidenceRecord("TXT", "stripe-verification=abc", "Stripe", "stripe"))
    after = _capsule(
        info=_info(evidence=added_evidence),
        results=(_dns_result(evidence=added_evidence), _oidc_result()),
    )
    result = compare_capsules(before, after)
    added = result["observation"]["added"]
    assert result["observation"]["changed"] is True
    assert any(item["key"] == "TXT" and item["value"] == "stripe-verification=abc" for item in added)
    assert all(item["source_role"] == "dns_records" for item in added)
    assert all(item["observation_window"]["ended_at"] == _END.isoformat() for item in added)


def test_unavailable_current_source_withholds_removals() -> None:
    before = _capsule()
    after = _capsule(info=_info(evidence=()), results=(_dns_result(unavailable=True), _oidc_result()))
    result = compare_capsules(before, after)
    assert result["observation"]["added"] == []
    assert result["observation"]["removed"] == []
    assert result["observation"]["suppressed_source_roles"] == ["dns_records"]
    assert result["collection_regime"]["changed"] is True


def test_unavailable_previous_source_withholds_additions() -> None:
    before = _capsule(info=_info(evidence=()), results=(_dns_result(unavailable=True), _oidc_result()))
    after = _capsule()
    result = compare_capsules(before, after)
    assert result["observation"]["added"] == []
    assert result["observation"]["removed"] == []
    assert result["observation"]["suppressed_source_roles"] == ["dns_records"]


def test_compare_classifies_collection_vantage_change() -> None:
    result = compare_capsules(_capsule(vantage="resolver-a"), _capsule(vantage="resolver-b"))
    assert result["collection_regime"]["changed"] is True
    assert result["collection_regime"]["changes"] == [
        {"field": "vantage", "before": "resolver-a", "after": "resolver-b"}
    ]


def test_compare_classifies_time_evaluation_without_fact_change() -> None:
    capsule = _capsule()
    result = compare_capsules(capsule, capsule, after_as_of="2026-08-14T12:00:03+00:00")
    assert result["time_evaluation"]["changed"] is True
    assert result["time_evaluation"]["freshness_changes"] == []
    assert result["observation"]["changed"] is False
    assert result["interpretation"]["changed"] is False


def test_compare_classifies_interpretation_context_only(monkeypatch: pytest.MonkeyPatch) -> None:
    before = _capsule()
    changed_context = capsule_module.current_interpretation_context()
    changed_context["catalog_digest"] = f"sha256:{'1' * 64}"
    monkeypatch.setattr(capsule_module, "current_interpretation_context", lambda: changed_context)
    after = _capsule()
    result = compare_capsules(before, after)
    assert result["observation"]["changed"] is False
    assert result["interpretation"] == {
        "changed": True,
        "changes": [
            {
                "field": "catalog_digest",
                "before": before["interpretation_context"]["catalog_digest"],
                "after": changed_context["catalog_digest"],
            }
        ],
    }


def test_same_raw_dns_under_different_catalog_rule_is_interpretation_only() -> None:
    raw_value = "vendor-verification=abc"
    old_evidence = (EvidenceRecord("TXT", raw_value, "Old vendor rule", "old-vendor"),)
    new_evidence = (EvidenceRecord("TXT", raw_value, "New vendor rule", "new-vendor"),)
    before = _capsule(info=_info(evidence=old_evidence), results=(_dns_result(evidence=old_evidence), _oidc_result()))
    after = _capsule(info=_info(evidence=new_evidence), results=(_dns_result(evidence=new_evidence), _oidc_result()))
    result = compare_capsules(before, after)
    assert result["observation"]["changed"] is False
    assert result["interpretation"]["changed"] is True
    assert result["interpretation"]["changes"][0]["field"] == "rendered_result"


def test_compare_reports_stable_signal_identifier_change() -> None:
    before = _capsule()
    after = _capsule()
    after["interpretation"]["stable_signal_ids"] = ["Different Rule"]
    after["content_digest"] = capsule_module._sha256(capsule_module._without_digest(after))
    result = compare_capsules(before, after)
    assert result["observation"]["changed"] is False
    assert result["interpretation"]["changes"] == [
        {
            "field": "stable_signal_ids",
            "before": ["Multi-Cloud"],
            "after": ["Different Rule"],
        }
    ]


def test_compare_rejects_different_domains() -> None:
    with pytest.raises(ValueError, match="same queried_domain"):
        compare_capsules(_capsule(), _capsule(info=_info(domain="example.net")))


@pytest.mark.parametrize("as_of", ["not-a-time", "2026-08-14T12:00:03"])
def test_replay_rejects_invalid_or_naive_as_of(as_of: str) -> None:
    with pytest.raises(ValueError, match="as_of"):
        replay_capsule(_capsule(), as_of=as_of)


@pytest.mark.parametrize("as_of", ["0001-01-01T00:00:00+01:00", "9999-12-31T23:59:59-01:00"])
def test_timestamp_utc_overflow_is_a_validation_error(as_of: str) -> None:
    with pytest.raises(ValueError, match="as_of"):
        parse_utc_time(as_of, "as_of")


@pytest.mark.parametrize("as_of", ["0001-01-01T01:00:00+01:00", "9999-12-31T22:59:59-01:00"])
def test_timestamp_near_utc_boundary_remains_valid(as_of: str) -> None:
    assert parse_utc_time(as_of, "as_of").tzinfo is UTC


def test_validate_rejects_content_tampering() -> None:
    capsule = _capsule()
    capsule["collection"]["vantage"] = "tampered"
    with pytest.raises(ValueError, match="content_digest"):
        validate_capsule(capsule)


def test_validate_rejects_fact_tampering_before_outer_digest() -> None:
    capsule = _capsule()
    capsule["observations"][0]["value"] = "tampered"
    with pytest.raises(ValueError, match="fact_id"):
        validate_capsule(capsule)


def test_validate_rejects_unknown_fields_and_nonfinite_values() -> None:
    unknown = _capsule()
    unknown["unexpected"] = True
    with pytest.raises(ValueError, match="top-level"):
        validate_capsule(unknown)

    for invalid, message in ((float("nan"), "non-finite"), (10**400, "timeout_seconds")):
        nonfinite = _capsule()
        nonfinite["collection"]["options"]["timeout_seconds"] = invalid
        with pytest.raises(ValueError, match=message):
            validate_capsule(nonfinite)


def test_vantage_rejects_control_characters_and_truncation() -> None:
    with pytest.raises(ValueError, match="vantage"):
        _capsule(vantage="resolver\x1b[31m")
    with pytest.raises(ValueError, match="vantage"):
        _capsule(vantage="x" * 129)


def test_write_load_round_trip_and_no_clobber(tmp_path: Path) -> None:
    path = tmp_path / "capsule.json"
    capsule = _capsule()
    write_capsule(path, capsule)
    assert load_capsule(path) == capsule
    with pytest.raises(FileExistsError, match="already exists"):
        write_capsule(path, capsule)

    replacement = _capsule(vantage="replacement")
    write_capsule(path, replacement, overwrite=True)
    assert load_capsule(path) == replacement


def test_load_rejects_invalid_root_and_oversized_file(tmp_path: Path) -> None:
    array_path = tmp_path / "array.json"
    array_path.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="root must be a JSON object"):
        load_capsule(array_path)

    oversized = tmp_path / "large.json"
    oversized.write_bytes(b" " * (capsule_module.MAX_CAPSULE_BYTES + 1))
    with pytest.raises(ValueError, match="exceeds"):
        load_capsule(oversized)


def test_load_rejects_symlink(tmp_path: Path) -> None:
    target = tmp_path / "target.json"
    write_capsule(target, _capsule())
    link = tmp_path / "link.json"
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlink creation is unavailable")
    with pytest.raises(ValueError, match="symbolic link"):
        load_capsule(link)


def test_capsule_serialization_is_strict_json() -> None:
    encoded = json.dumps(_capsule(), allow_nan=False)
    assert "NaN" not in encoded


def test_context_tracks_ephemeral_fingerprints_and_preserves_recorded_capsule() -> None:
    from recon_tool.fingerprints import DetectionRule, Fingerprint, clear_ephemeral, get_ephemeral, inject_ephemeral

    previous_ephemeral = get_ephemeral()
    recorded = _capsule()
    before = replay_capsule(recorded)
    assert before["interpretation_context_match"] is True
    rule = Fingerprint(
        name="Synthetic capsule token",
        slug="synthetic-capsule-token",
        category="security",
        confidence="high",
        m365=False,
        detections=(DetectionRule(type="txt", pattern=r"^synthetic-capsule-token="),),
    )
    try:
        inject_ephemeral(rule)
        replay = replay_capsule(recorded)
        assert replay["interpretation_context_match"] is False
        assert replay["recorded_interpretation_context"] == recorded["interpretation_context"]
        assert replay["result"] == before["result"]
        assert (
            replay["current_interpretation_context"]["model_digest"]
            == before["current_interpretation_context"]["model_digest"]
        )
    finally:
        clear_ephemeral()
        for previous in previous_ephemeral:
            inject_ephemeral(previous)
    assert replay_capsule(recorded)["interpretation_context_match"] is True


@pytest.mark.parametrize("catalog", ["fingerprints", "signals", "motifs"])
def test_context_tracks_effective_loaded_custom_catalogs(monkeypatch: pytest.MonkeyPatch, catalog: str) -> None:
    from recon_tool import fingerprints, motifs, signals

    loaders = {
        "fingerprints": (fingerprints, "load_fingerprints", "name"),
        "signals": (signals, "load_signals", "description"),
        "motifs": (motifs, "load_motifs", "description"),
    }
    module, loader_name, field = loaders[catalog]
    loaded = getattr(module, loader_name)()
    before = capsule_module.current_interpretation_context()
    changed = (replace(loaded[0], **{field: "Synthetic changed catalog definition"}), *loaded[1:])
    monkeypatch.setattr(module, loader_name, lambda: changed)
    after = capsule_module.current_interpretation_context()
    assert before["catalog_digest"] != after["catalog_digest"]
    assert before["model_digest"] == after["model_digest"]
    assert after == capsule_module.current_interpretation_context()


def test_context_tracks_effective_prior_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    from recon_tool import bayesian_loader

    before = capsule_module.current_interpretation_context()
    root = next(node for node in bayesian_loader.load_network().nodes if not node.parents)
    override = 0.99 if root.prior != 0.99 else 0.01
    monkeypatch.setattr(bayesian_loader, "load_priors_override", lambda: {root.name: override})
    after = capsule_module.current_interpretation_context()
    assert before["model_digest"] != after["model_digest"]
    assert before["catalog_digest"] == after["catalog_digest"]


def test_historical_packaged_only_context_still_replays() -> None:
    recorded = _capsule()
    recorded["interpretation_context"]["catalog_digest"] = capsule_module._digest_files(capsule_module._CATALOG_FILES)
    recorded["interpretation_context"]["model_digest"] = capsule_module._digest_files(capsule_module._MODEL_FILES)
    recorded["content_digest"] = capsule_module.content_digest(capsule_module._without_digest(recorded))
    replay = replay_capsule(recorded)
    assert replay["interpretation_context_match"] is False
    assert replay["result"] == recorded["interpretation"]["rendered_result"]


@pytest.mark.parametrize("existing", [False, True])
def test_capsule_write_rejects_oversized_utf8_before_touching_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, existing: bool
) -> None:
    capsule = _capsule(info=replace(_info(), display_name="Synthetic caf\u00e9"))
    payload = json.dumps(capsule, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    assert len(payload.encode("utf-8")) > len(payload)
    monkeypatch.setattr(capsule_module, "MAX_CAPSULE_BYTES", len(payload))
    output = tmp_path / "capsule.json"
    if existing:
        output.write_text("caller-owned", encoding="utf-8")
    with pytest.raises(ValueError, match="maximum artifact size"):
        write_capsule(output, capsule, overwrite=existing)
    if existing:
        assert output.read_text(encoding="utf-8") == "caller-owned"
    else:
        assert not output.exists()
    assert sorted(path.name for path in tmp_path.iterdir()) == (["capsule.json"] if existing else [])


def test_capsule_write_at_exact_utf8_limit_round_trips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    capsule = _capsule()
    payload = json.dumps(capsule, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    monkeypatch.setattr(capsule_module, "MAX_CAPSULE_BYTES", len(payload.encode("utf-8")))
    output = tmp_path / "capsule.json"
    write_capsule(output, capsule)
    assert load_capsule(output) == capsule


def test_lexical_order_keeps_capsule_rendered_result_digest_stable() -> None:
    from recon_tool.merger import merge_results

    names = ("dev.example.com", "stage.example.com", "qa.example.com", "uat.example.com")
    first_result = replace(_dns_result(), related_domains=names)
    second_result = replace(_dns_result(), related_domains=tuple(reversed(names)))
    first_info = merge_results([first_result, _oidc_result()], "example.com")
    second_info = merge_results([second_result, _oidc_result()], "example.com")
    context = CollectionContext(
        started_at=_START,
        ended_at=_END,
        ct_enabled=False,
        direct_probes=False,
        timeout_seconds=30.0,
        vantage="caller-local",
    )
    first = build_capsule(first_info, (first_result, _oidc_result()), context)
    second = build_capsule(second_info, (second_result, _oidc_result()), context)
    assert first["interpretation"]["rendered_result_digest"] == second["interpretation"]["rendered_result_digest"]
    assert compare_capsules(first, second)["interpretation"]["changed"] is False
