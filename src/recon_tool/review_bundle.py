# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportUnknownArgumentType=none, reportUnknownMemberType=none, reportUnknownVariableType=none
"""Deterministic, caller-owned single-namespace review artifacts.
ReviewBundle is separate from the stable lookup and observation-capsule
contracts. It composes one fresh lookup, its exact collection opportunities,
an explained lookup baseline, and evidence-linked review candidates without
performing I/O or another network request during construction.
"""

from __future__ import annotations

import contextlib
import dataclasses
import json
import math
import os
import tempfile
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from recon_tool import __version__
from recon_tool.capsule import (
    canonical_json_bytes,
    content_digest,
    current_interpretation_context,
    parse_utc_time,
    project_source_observations,
    utc_text,
    validate_collection_vantage,
)
from recon_tool.collection_view import (
    collection_observable_evidence,
    collection_observable_info,
    collection_observable_results,
)
from recon_tool.exposure import find_gaps_from_info
from recon_tool.exposure_models import HardeningGap
from recon_tool.formatter import format_tenant_dict
from recon_tool.json_limits import is_positive_timeout, load_bounded_json_file
from recon_tool.models import EvidenceRecord, SourceResult, TenantInfo
from recon_tool.validator import strip_control_chars, validate_domain

REVIEW_BUNDLE_SCHEMA_VERSION = "1.0"
REVIEW_CANDIDATES_SCHEMA_VERSION = "1.0"
EXPLAINED_BASELINE_SCHEMA_VERSION = "1.0"
MAX_REVIEW_BUNDLE_BYTES = 10 * 1024 * 1024

REVIEW_SCOPE_STATEMENT = (
    "This caller-owned artifact reviews public metadata for one caller-supplied namespace. "
    "It does not establish ownership, an organizational relationship, overall security, "
    "a vulnerability, or control completeness."
)
REVIEW_LIMITATIONS = (
    "Collection uses the documented public-metadata boundary and no credentials or active scanning.",
    "Direct probes are disabled; MTA-STS remains the only default target-owned HTTP request.",
    "Unavailable or hideable observations do not establish absence.",
    "Review candidates are evidence-linked prompts, not security findings, rankings, or verdicts.",
    "The artifact is local and caller-owned; recon does not upload, retain, or schedule it.",
)

_TOP_LEVEL_FIELDS = {
    "record_type",
    "schema_version",
    "generated_at",
    "generator",
    "interpretation_context",
    "scope",
    "collection",
    "source_opportunities",
    "workflow",
    "result",
    "scope_statement",
    "limitations",
    "content_digest",
}
_SUCCESS_FIELDS = {
    "record_type",
    "queried_domain",
    "explained_baseline",
    "evidence_ledger",
    "review_candidates",
}
_ERROR_FIELDS = {"record_type", "error_kind", "failed_source_roles"}
_EVIDENCE_FIELDS = {"source_type", "raw_value", "rule_name", "slug"}
_EVIDENCE_LEDGER_FIELDS = {"evidence_id", *_EVIDENCE_FIELDS}
_EXPLANATION_FIELDS = {
    "item_name",
    "item_type",
    "matched_evidence",
    "evidence_ids",
    "fired_rules",
    "confidence_derivation",
    "weakening_conditions",
    "curated_explanation",
    "lineage_status",
    "lineage_rule_ids",
}
_CANDIDATE_FIELDS = {
    "candidate_id",
    "category",
    "severity",
    "observation",
    "recommendation",
    "generator_rule_id",
    "observation_state",
    "observation_scope",
    "metadata_dependencies",
    "absence_confirmable",
    "evidence",
    "evidence_ids",
}
_ERROR_KINDS = frozenset({"validation", "lookup", "timeout"})
_OPPORTUNITY_STATES = frozenset({"observed_value", "observed_empty", "partial", "unavailable"})
_WORKFLOW_STATUSES = frozenset({"completed", "failed"})
_COLLECTION_VALIDITY_STATES = frozenset(
    {"complete_for_recorded_opportunities", "partial", "unavailable", "not_observed"}
)

__all__ = [
    "EXPLAINED_BASELINE_SCHEMA_VERSION",
    "MAX_REVIEW_BUNDLE_BYTES",
    "REVIEW_BUNDLE_SCHEMA_VERSION",
    "REVIEW_CANDIDATES_SCHEMA_VERSION",
    "REVIEW_LIMITATIONS",
    "REVIEW_SCOPE_STATEMENT",
    "ReviewCollectionContext",
    "build_review_bundle",
    "build_review_error_bundle",
    "load_review_bundle",
    "validate_review_bundle",
    "write_review_bundle",
]


@dataclasses.dataclass(frozen=True, slots=True)
class ReviewCollectionContext:
    """Caller attestation and observation window for one fresh review.

    Supported adapters set fixed provenance fields from the collection path
    they control. Other callers must attest to the same facts.
    """

    started_at: datetime
    ended_at: datetime
    ct_enabled: bool
    timeout_seconds: float
    vantage: str = "caller-local"
    result_cache: Literal["bypassed"] = "bypassed"
    direct_probes: Literal[False] = False


@dataclasses.dataclass(frozen=True, slots=True)
class _BundleAssembly:
    input_coordinate: str
    queried_domain: str | None
    collection: ReviewCollectionContext
    generated_at: datetime | None
    source_opportunities: list[dict[str, Any]]


def _safe_coordinate(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("input_coordinate must be a string")
    safe = strip_control_chars(value, max_len=512).strip()
    if not safe or safe != value or len(value) > 512:
        raise ValueError("input_coordinate must be 1 to 512 printable characters")
    return safe


def _collection_times(collection: ReviewCollectionContext) -> tuple[str, str]:
    started = utc_text(collection.started_at)
    ended = utc_text(collection.ended_at)
    if collection.ended_at < collection.started_at:
        raise ValueError("review collection end must not precede its start")
    if not is_positive_timeout(collection.timeout_seconds):
        raise ValueError("review timeout must be finite and positive")
    validate_collection_vantage(collection.vantage, label="review")
    if collection.result_cache != "bypassed":
        raise ValueError("review collection must attest that the lookup-result cache was bypassed")
    if collection.direct_probes is not False:
        raise ValueError("review collection must attest that direct probes were disabled")
    return started, ended


def _generated_text(generated_at: datetime | None, ended_at: datetime) -> str:
    generated = generated_at or datetime.now(UTC)
    generated_text = utc_text(generated)
    if generated.astimezone(UTC) < ended_at.astimezone(UTC):
        raise ValueError("generated_at must not precede collection.ended_at")
    return generated_text


def _evidence_body(item: object) -> dict[str, str]:
    body: dict[str, str] = {}
    for field in ("source_type", "raw_value", "rule_name", "slug"):
        value = getattr(item, field, None)
        if not isinstance(value, str):
            raise ValueError(f"evidence {field} must be a string")
        body[field] = value
    return body


def _evidence_id(domain: str, body: Mapping[str, str]) -> str:
    return content_digest({"record_type": "review_evidence", "queried_domain": domain, **body})


def _evidence_ledger(domain: str, items: Iterable[object]) -> tuple[list[dict[str, str]], dict[tuple[str, ...], str]]:
    ledger_by_id: dict[str, dict[str, str]] = {}
    ids_by_value: dict[tuple[str, ...], str] = {}
    for item in items:
        body = _evidence_body(item)
        evidence_id = _evidence_id(domain, body)
        ledger_by_id[evidence_id] = {"evidence_id": evidence_id, **body}
        ids_by_value[tuple(body[field] for field in ("source_type", "raw_value", "rule_name", "slug"))] = evidence_id
    return [ledger_by_id[key] for key in sorted(ledger_by_id)], ids_by_value


def _lookup_evidence_id(item: object, ids_by_value: Mapping[tuple[str, ...], str]) -> str:
    body = _evidence_body(item)
    key = tuple(body[field] for field in ("source_type", "raw_value", "rule_name", "slug"))
    try:
        return ids_by_value[key]
    except KeyError as exc:
        raise ValueError("review evidence is absent from the evidence ledger") from exc


def _explanation_records(
    info: TenantInfo,
    results: list[SourceResult],
) -> tuple[list[Any], tuple[EvidenceRecord, ...]]:
    from recon_tool.absence import evaluate_absence_signals, evaluate_positive_absence
    from recon_tool.email_security import signal_context_from_tenant_info, signal_context_metadata
    from recon_tool.explanation import explain_confidence, explain_insights, explain_signals
    from recon_tool.insight_explanation import InsightExplanationContext
    from recon_tool.signals import evaluate_signals, load_signals

    projected = collection_observable_info(info)
    observable_evidence = collection_observable_evidence(projected)
    context = signal_context_from_tenant_info(projected)
    signal_matches = evaluate_signals(context)
    signals = load_signals()
    all_signal_matches = [
        *signal_matches,
        *evaluate_absence_signals(signal_matches, signals, context.detected_slugs),
        *evaluate_positive_absence(signal_matches, signals, context.detected_slugs),
    ]
    signal_records = explain_signals(
        all_signal_matches,
        signals,
        context.detected_slugs,
        signal_context_metadata(context),
        observable_evidence,
        projected.detection_scores,
    )
    insight_records = explain_insights(
        list(projected.insights),
        frozenset(projected.slugs),
        frozenset(projected.services),
        observable_evidence,
        InsightExplanationContext(projected.detection_scores, projected.insight_claims),
    )
    confidence_record = explain_confidence(
        collection_observable_results(results),
        projected.evidence_confidence,
        projected.inference_confidence,
        projected.confidence,
        identity_conflict=bool(projected.merge_conflicts and projected.merge_conflicts.tenant_id),
    )
    return [*signal_records, *insight_records, confidence_record], observable_evidence


def _explained_baseline(
    info: TenantInfo,
    results: list[SourceResult],
    ids_by_value: Mapping[tuple[str, ...], str],
) -> dict[str, Any]:
    from recon_tool.explanation import build_explanation_dag, serialize_explanation
    from recon_tool.fusion_apply import apply_fusion

    baseline_info = apply_fusion(collection_observable_info(info))
    records, observable_evidence = _explanation_records(baseline_info, results)
    explanations: list[dict[str, Any]] = []
    for record in records:
        item = serialize_explanation(record)
        item["evidence_ids"] = sorted(
            {_lookup_evidence_id(evidence, ids_by_value) for evidence in record.matched_evidence}
        )
        explanations.append(item)
    explanations.sort(
        key=lambda item: (
            str(item["item_type"]),
            str(item["item_name"]),
            canonical_json_bytes(item),
        )
    )
    return {
        "record_type": "explained_lookup_baseline",
        "schema_version": EXPLAINED_BASELINE_SCHEMA_VERSION,
        "lookup": format_tenant_dict(baseline_info),
        "explanations": explanations,
        "explanation_dag": build_explanation_dag(records, observable_evidence),
    }


def _candidate_body(
    gap: HardeningGap,
    ids_by_value: Mapping[tuple[str, ...], str],
) -> dict[str, Any]:
    evidence = sorted(
        (_evidence_body(item) for item in gap.evidence),
        key=lambda item: tuple(item[field] for field in ("source_type", "raw_value", "rule_name", "slug")),
    )
    evidence_ids = sorted(
        {
            ids_by_value[tuple(item[field] for field in ("source_type", "raw_value", "rule_name", "slug"))]
            for item in evidence
        }
    )
    dependencies = [
        {
            "field": item.field,
            "operator": item.operator,
            "expected_value": item.expected_value,
            "observed_value": item.observed_value,
        }
        for item in gap.metadata_dependencies
    ]
    dependencies.sort(key=canonical_json_bytes)
    return {
        "category": gap.category,
        "severity": gap.severity,
        "observation": gap.observation,
        "recommendation": gap.recommendation,
        "generator_rule_id": gap.generator_rule_id,
        "observation_state": gap.observation_state,
        "observation_scope": sorted(set(gap.observation_scope)),
        "metadata_dependencies": dependencies,
        "absence_confirmable": gap.absence_confirmable,
        "evidence": evidence,
        "evidence_ids": evidence_ids,
    }


def _review_candidates(info: TenantInfo) -> tuple[dict[str, Any], tuple[HardeningGap, ...]]:
    report = find_gaps_from_info(info)
    return (
        {
            "record_type": "review_candidates",
            "schema_version": REVIEW_CANDIDATES_SCHEMA_VERSION,
            "domain": report.domain,
            "disclaimer": report.disclaimer,
            "unavailable_controls": sorted(set(report.unavailable_controls)),
            "degraded_sources": sorted(set(report.degraded_sources)),
            "candidates": [],
        },
        tuple(report.gaps),
    )


def _collection_payload(
    collection: ReviewCollectionContext,
    *,
    ct_provider_used: str | None,
    ct_cache_age_days: int | None,
    ct_attempt_outcome: str | None,
) -> dict[str, Any]:
    started, ended = _collection_times(collection)
    return {
        "started_at": started,
        "ended_at": ended,
        "as_of": ended,
        "options": {
            "ct_enabled": collection.ct_enabled,
            "direct_probes": collection.direct_probes,
            "timeout_seconds": collection.timeout_seconds,
        },
        "vantage": collection.vantage,
        "cache": {
            "result_cache": collection.result_cache,
            "ct_provider_used": ct_provider_used,
            "ct_cache_age_days": ct_cache_age_days,
            "ct_attempt_outcome": ct_attempt_outcome,
        },
    }


def _collection_validity(opportunities: list[dict[str, Any]]) -> str:
    if not opportunities:
        return "not_observed"
    states = {row["state"] for row in opportunities}
    if states <= {"observed_value", "observed_empty"}:
        return "complete_for_recorded_opportunities"
    if states == {"unavailable"}:
        return "unavailable"
    return "partial"


def _base_bundle(
    assembly: _BundleAssembly,
    result: dict[str, Any],
) -> dict[str, Any]:
    _started, ended = _collection_times(assembly.collection)
    generated_text = _generated_text(assembly.generated_at, parse_utc_time(ended, "collection.ended_at"))
    status = "completed" if result["record_type"] == "review_success" else "failed"
    bundle: dict[str, Any] = {
        "record_type": "review_bundle",
        "schema_version": REVIEW_BUNDLE_SCHEMA_VERSION,
        "generated_at": generated_text,
        "generator": {"name": "recon-tool", "version": __version__},
        "interpretation_context": current_interpretation_context(),
        "scope": {
            "kind": "single_namespace",
            "selection_basis": "caller_supplied",
            "input_coordinate": _safe_coordinate(assembly.input_coordinate),
            "queried_domain": assembly.queried_domain,
        },
        "collection": _collection_payload(
            assembly.collection,
            ct_provider_used=(result.get("_ct_provider_used") if status == "completed" else None),
            ct_cache_age_days=(result.get("_ct_cache_age_days") if status == "completed" else None),
            ct_attempt_outcome=(result.get("_ct_attempt_outcome") if status == "completed" else None),
        ),
        "source_opportunities": assembly.source_opportunities,
        "workflow": {
            "status": status,
            "collection_validity": _collection_validity(assembly.source_opportunities),
            "freshness_assessment": "not_assigned",
        },
        "result": {key: value for key, value in result.items() if not key.startswith("_ct_")},
        "scope_statement": REVIEW_SCOPE_STATEMENT,
        "limitations": list(REVIEW_LIMITATIONS),
    }
    bundle["content_digest"] = content_digest(bundle)
    validate_review_bundle(bundle)
    return bundle


def build_review_bundle(
    info: TenantInfo,
    results: Iterable[SourceResult],
    input_coordinate: str,
    collection: ReviewCollectionContext,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Build one deterministic ReviewBundle from caller-attested fresh inputs."""
    if info.cached_at is not None:
        raise ValueError("review bundles require a fresh TenantInfo with cached_at unset")
    domain = validate_domain(info.queried_domain, apex=False)
    if domain != info.queried_domain:
        raise ValueError("review domain must already be normalized")
    result_list = sorted(results, key=lambda item: (item.source_name, canonical_json_bytes(dataclasses.asdict(item))))
    started, ended = _collection_times(collection)
    opportunities, _observations = project_source_observations(
        result_list,
        started_at=started,
        ended_at=ended,
    )
    candidate_report, gaps = _review_candidates(info)
    ledger_inputs: list[object] = [*collection_observable_evidence(info)]
    ledger_inputs.extend(evidence for gap in gaps for evidence in gap.evidence)
    ledger, ids_by_value = _evidence_ledger(domain, ledger_inputs)
    candidates: list[dict[str, Any]] = []
    for gap in gaps:
        body = _candidate_body(gap, ids_by_value)
        candidate_id = content_digest({"record_type": "review_candidate", "queried_domain": domain, **body})
        candidates.append({"candidate_id": candidate_id, **body})
    candidates.sort(key=lambda item: (str(item["generator_rule_id"]), str(item["candidate_id"])))
    candidate_report["candidates"] = candidates
    success = {
        "record_type": "review_success",
        "queried_domain": domain,
        "explained_baseline": _explained_baseline(info, result_list, ids_by_value),
        "evidence_ledger": ledger,
        "review_candidates": candidate_report,
        "_ct_provider_used": info.ct_provider_used,
        "_ct_cache_age_days": info.ct_cache_age_days,
        "_ct_attempt_outcome": info.ct_attempt_outcome,
    }
    return _base_bundle(
        _BundleAssembly(input_coordinate, domain, collection, generated_at, opportunities),
        result=success,
    )


def build_review_error_bundle(
    input_coordinate: str,
    collection: ReviewCollectionContext,
    error_kind: Literal["validation", "lookup", "timeout"],
    failed_source_roles: Iterable[str] = (),
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Build a typed ReviewBundle failure without lookup facts or candidates."""
    if error_kind not in _ERROR_KINDS:
        raise ValueError(f"unsupported review error kind: {error_kind!r}")
    roles = sorted({_safe_role(role) for role in failed_source_roles})
    started, ended = _collection_times(collection)
    failed_results = [
        SourceResult(source_name=role, error="collection failed", source_unavailable=True) for role in roles
    ]
    opportunities, _observations = project_source_observations(
        failed_results,
        started_at=started,
        ended_at=ended,
    )
    return _base_bundle(
        _BundleAssembly(input_coordinate, None, collection, generated_at, opportunities),
        result={
            "record_type": "review_error",
            "error_kind": error_kind,
            "failed_source_roles": roles,
        },
    )


def _safe_role(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("failed source role must be a string")
    safe = strip_control_chars(value, max_len=128).strip()
    if not safe or safe != value:
        raise ValueError("failed source role must be 1 to 128 printable characters")
    return safe


def _require_mapping(value: object, field: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be a JSON object")
    return value


def _require_list(value: object, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a JSON array")
    return value


def _require_keys(value: Mapping[str, Any], field: str, expected: set[str]) -> None:
    if set(value) != expected:
        raise ValueError(f"{field} has unknown or missing fields")


def _require_string(value: object, field: str, maximum: int = 1024) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise ValueError(f"{field} must be a non-empty string of at most {maximum} characters")
    if strip_control_chars(value, max_len=maximum) != value:
        raise ValueError(f"{field} must not contain control characters")
    return value


def _require_text(value: object, field: str, maximum: int = 1024) -> str:
    if not isinstance(value, str) or len(value) > maximum:
        raise ValueError(f"{field} must be a string of at most {maximum} characters")
    if strip_control_chars(value, max_len=maximum) != value:
        raise ValueError(f"{field} must not contain control characters")
    return value


def _require_digest(value: object, field: str) -> str:
    digest = _require_string(value, field, 71)
    if len(digest) != 71 or not digest.startswith("sha256:"):
        raise ValueError(f"{field} must be a lowercase SHA-256 digest")
    suffix = digest.removeprefix("sha256:")
    if any(character not in "0123456789abcdef" for character in suffix):
        raise ValueError(f"{field} must be a lowercase SHA-256 digest")
    return digest


def _validate_finite_json(value: object, field: str = "review bundle") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{field} must not contain non-finite numbers")
    if isinstance(value, list):
        for item in value:
            _validate_finite_json(item, field)
    elif isinstance(value, dict):
        for item in value.values():
            _validate_finite_json(item, field)


def _validate_context(bundle: Mapping[str, Any]) -> None:
    generator = _require_mapping(bundle.get("generator"), "generator")
    _require_keys(generator, "generator", {"name", "version"})
    if generator.get("name") != "recon-tool":
        raise ValueError("generator.name must be 'recon-tool'")
    _require_string(generator.get("version"), "generator.version", 64)
    context = _require_mapping(bundle.get("interpretation_context"), "interpretation_context")
    _require_keys(
        context,
        "interpretation_context",
        {"recon_version", "normalizer_version", "catalog_digest", "model_digest"},
    )
    _require_string(context.get("recon_version"), "interpretation_context.recon_version", 64)
    _require_string(context.get("normalizer_version"), "interpretation_context.normalizer_version", 32)
    _require_digest(context.get("catalog_digest"), "interpretation_context.catalog_digest")
    _require_digest(context.get("model_digest"), "interpretation_context.model_digest")


def _validate_scope(bundle: Mapping[str, Any], success: bool) -> str | None:
    scope = _require_mapping(bundle.get("scope"), "scope")
    _require_keys(scope, "scope", {"kind", "selection_basis", "input_coordinate", "queried_domain"})
    if scope.get("kind") != "single_namespace" or scope.get("selection_basis") != "caller_supplied":
        raise ValueError("scope must describe one caller-supplied namespace")
    _safe_coordinate(_require_string(scope.get("input_coordinate"), "scope.input_coordinate", 512))
    domain = scope.get("queried_domain")
    if success:
        if not isinstance(domain, str) or validate_domain(domain, apex=False) != domain:
            raise ValueError("scope.queried_domain must be a normalized domain on success")
        return domain
    if domain is not None:
        raise ValueError("scope.queried_domain must be null on error")
    return None


def _validate_collection(bundle: Mapping[str, Any]) -> tuple[datetime, datetime]:
    collection = _require_mapping(bundle.get("collection"), "collection")
    _require_keys(collection, "collection", {"started_at", "ended_at", "as_of", "options", "vantage", "cache"})
    started = parse_utc_time(collection.get("started_at"), "collection.started_at")
    ended = parse_utc_time(collection.get("ended_at"), "collection.ended_at")
    as_of = parse_utc_time(collection.get("as_of"), "collection.as_of")
    if ended < started or as_of != ended:
        raise ValueError("collection must have a non-reversed window and as_of equal to ended_at")
    _require_string(collection.get("vantage"), "collection.vantage", 128)
    options = _require_mapping(collection.get("options"), "collection.options")
    _require_keys(options, "collection.options", {"ct_enabled", "direct_probes", "timeout_seconds"})
    if type(options.get("ct_enabled")) is not bool or options.get("direct_probes") is not False:
        raise ValueError("collection options require boolean ct_enabled and direct_probes fixed false")
    timeout = options.get("timeout_seconds")
    if not is_positive_timeout(timeout):
        raise ValueError("collection.options.timeout_seconds must be finite and positive")
    cache = _require_mapping(collection.get("cache"), "collection.cache")
    _require_keys(
        cache,
        "collection.cache",
        {"result_cache", "ct_provider_used", "ct_cache_age_days", "ct_attempt_outcome"},
    )
    if cache.get("result_cache") != "bypassed":
        raise ValueError("collection.cache.result_cache must be 'bypassed'")
    for field in ("ct_provider_used", "ct_attempt_outcome"):
        value = cache.get(field)
        if value is not None and not isinstance(value, str):
            raise ValueError(f"collection.cache.{field} must be a string or null")
    age = cache.get("ct_cache_age_days")
    if age is not None and (type(age) is not int or age < 0):
        raise ValueError("collection.cache.ct_cache_age_days must be a non-negative integer or null")
    return started, ended


def _validate_opportunities(bundle: Mapping[str, Any], started: datetime, ended: datetime) -> list[dict[str, Any]]:
    rows = _require_list(bundle.get("source_opportunities"), "source_opportunities")
    roles: list[str] = []
    for index, raw in enumerate(rows):
        row = _require_mapping(raw, f"source_opportunities[{index}]")
        _require_keys(
            row,
            f"source_opportunities[{index}]",
            {"source_role", "state", "instance_count", "degraded_markers", "observation_window"},
        )
        roles.append(
            _safe_role(_require_string(row.get("source_role"), f"source_opportunities[{index}].source_role", 128))
        )
        if row.get("state") not in _OPPORTUNITY_STATES:
            raise ValueError(f"source_opportunities[{index}].state is invalid")
        count = row.get("instance_count")
        if type(count) is not int or count < 1:
            raise ValueError(f"source_opportunities[{index}].instance_count must be positive")
        markers = _require_list(row.get("degraded_markers"), f"source_opportunities[{index}].degraded_markers")
        if not all(isinstance(item, str) and item for item in markers) or markers != sorted(set(markers)):
            raise ValueError(f"source_opportunities[{index}].degraded_markers must be uniquely sorted strings")
        window = _require_mapping(row.get("observation_window"), f"source_opportunities[{index}].observation_window")
        _require_keys(window, f"source_opportunities[{index}].observation_window", {"started_at", "ended_at"})
        if (
            parse_utc_time(window.get("started_at"), "observation_window.started_at") != started
            or parse_utc_time(window.get("ended_at"), "observation_window.ended_at") != ended
        ):
            raise ValueError("source opportunity windows must match the collection window")
    if roles != sorted(set(roles)):
        raise ValueError("source opportunities must be uniquely sorted by source role")
    return [dict(row) for row in rows]


def _validate_evidence_body(value: object, field: str) -> dict[str, str]:
    row = _require_mapping(value, field)
    _require_keys(row, field, _EVIDENCE_FIELDS)
    return {key: _require_string(row.get(key), f"{field}.{key}", 8192) for key in _EVIDENCE_FIELDS}


def _evidence_key(body: Mapping[str, str]) -> tuple[str, ...]:
    return tuple(body[key] for key in ("source_type", "raw_value", "rule_name", "slug"))


def _validate_baseline(result: Mapping[str, Any], domain: str) -> Mapping[str, Any]:
    baseline = _require_mapping(result.get("explained_baseline"), "result.explained_baseline")
    _require_keys(
        baseline,
        "result.explained_baseline",
        {"record_type", "schema_version", "lookup", "explanations", "explanation_dag"},
    )
    if baseline.get("record_type") != "explained_lookup_baseline":
        raise ValueError("explained baseline record_type is invalid")
    if baseline.get("schema_version") != EXPLAINED_BASELINE_SCHEMA_VERSION:
        raise ValueError("explained baseline schema version is unsupported")
    lookup = _require_mapping(baseline.get("lookup"), "result.explained_baseline.lookup")
    if lookup.get("record_type") != "lookup" or lookup.get("schema_version") != "2.0":
        raise ValueError("explained baseline must contain a stable v2 lookup")
    if lookup.get("queried_domain") != domain:
        raise ValueError("explained baseline lookup domain must match scope domain")
    dag = _require_mapping(baseline.get("explanation_dag"), "result.explained_baseline.explanation_dag")
    if dag.get("schema_version") != 1:
        raise ValueError("explanation DAG schema version is unsupported")
    return baseline


def _validate_ledger(result: Mapping[str, Any], domain: str) -> dict[str, dict[str, str]]:
    ledger_rows = _require_list(result.get("evidence_ledger"), "result.evidence_ledger")
    ledger: dict[str, dict[str, str]] = {}
    for index, raw in enumerate(ledger_rows):
        row = _require_mapping(raw, f"result.evidence_ledger[{index}]")
        _require_keys(row, f"result.evidence_ledger[{index}]", _EVIDENCE_LEDGER_FIELDS)
        evidence_id = _require_digest(row.get("evidence_id"), f"result.evidence_ledger[{index}].evidence_id")
        body = {
            key: _require_string(row.get(key), f"result.evidence_ledger[{index}].{key}", 8192)
            for key in _EVIDENCE_FIELDS
        }
        if evidence_id != _evidence_id(domain, body):
            raise ValueError("evidence ledger ID does not match its content")
        ledger[evidence_id] = body
    if list(ledger) != sorted(ledger) or len(ledger) != len(ledger_rows):
        raise ValueError("evidence ledger must be uniquely sorted by evidence_id")
    return ledger


def _validate_explanations(baseline: Mapping[str, Any], ledger: Mapping[str, Mapping[str, str]]) -> None:
    explanations = _require_list(baseline.get("explanations"), "result.explained_baseline.explanations")
    explanation_order: list[tuple[str, str, bytes]] = []
    for index, raw in enumerate(explanations):
        item = _require_mapping(raw, f"result.explained_baseline.explanations[{index}]")
        _require_keys(item, f"result.explained_baseline.explanations[{index}]", _EXPLANATION_FIELDS)
        for field in ("item_name", "item_type", "confidence_derivation", "lineage_status"):
            _require_string(item.get(field), f"explanation.{field}", 16384)
        _require_text(item.get("curated_explanation"), "explanation.curated_explanation", 16384)
        evidence_ids = _require_list(item.get("evidence_ids"), "explanation.evidence_ids")
        if evidence_ids != sorted(set(evidence_ids)) or any(value not in ledger for value in evidence_ids):
            raise ValueError("explanation evidence_ids must be uniquely sorted ledger references")
        matched = _require_list(item.get("matched_evidence"), "explanation.matched_evidence")
        matched_bodies = [_validate_evidence_body(value, "explanation.matched_evidence") for value in matched]
        if {_evidence_key(body) for body in matched_bodies} != {_evidence_key(ledger[value]) for value in evidence_ids}:
            raise ValueError("explanation evidence_ids do not match matched_evidence")
        for list_field in ("fired_rules", "weakening_conditions", "lineage_rule_ids"):
            values = _require_list(item.get(list_field), f"explanation.{list_field}")
            if not all(isinstance(value, str) for value in values):
                raise ValueError(f"explanation.{list_field} must contain strings")
        explanation_order.append((str(item["item_type"]), str(item["item_name"]), canonical_json_bytes(item)))
    if explanation_order != sorted(explanation_order):
        raise ValueError("explanations must be deterministically sorted")


def _validate_candidate(
    candidate: Mapping[str, Any],
    *,
    index: int,
    domain: str,
    ledger: Mapping[str, Mapping[str, str]],
) -> tuple[str, str]:
    _require_keys(candidate, f"candidate[{index}]", _CANDIDATE_FIELDS)
    candidate_id = _require_digest(candidate.get("candidate_id"), f"candidate[{index}].candidate_id")
    for field in (
        "category",
        "severity",
        "observation",
        "recommendation",
        "generator_rule_id",
        "observation_state",
    ):
        _require_string(candidate.get(field), f"candidate[{index}].{field}", 8192)
    if type(candidate.get("absence_confirmable")) is not bool:
        raise ValueError("candidate.absence_confirmable must be a boolean")
    for field in ("observation_scope", "evidence_ids"):
        values = _require_list(candidate.get(field), f"candidate[{index}].{field}")
        if not all(isinstance(value, str) and value for value in values) or values != sorted(set(values)):
            raise ValueError(f"candidate.{field} must be uniquely sorted strings")
    evidence_ids = candidate["evidence_ids"]
    if any(value not in ledger for value in evidence_ids):
        raise ValueError("candidate evidence_ids must reference the evidence ledger")
    evidence = _require_list(candidate.get("evidence"), f"candidate[{index}].evidence")
    evidence_bodies = [_validate_evidence_body(value, f"candidate[{index}].evidence") for value in evidence]
    if {_evidence_key(body) for body in evidence_bodies} != {_evidence_key(ledger[value]) for value in evidence_ids}:
        raise ValueError("candidate evidence_ids do not match candidate evidence")
    dependencies = _require_list(
        candidate.get("metadata_dependencies"),
        f"candidate[{index}].metadata_dependencies",
    )
    for dependency in dependencies:
        row = _require_mapping(dependency, "candidate metadata dependency")
        _require_keys(
            row,
            "candidate metadata dependency",
            {"field", "operator", "expected_value", "observed_value"},
        )
        _require_string(row.get("field"), "candidate metadata dependency.field", 128)
        _require_string(row.get("operator"), "candidate metadata dependency.operator", 32)
    if dependencies != sorted(dependencies, key=canonical_json_bytes):
        raise ValueError("candidate metadata dependencies must be deterministically sorted")
    body = {key: value for key, value in candidate.items() if key != "candidate_id"}
    expected_id = content_digest({"record_type": "review_candidate", "queried_domain": domain, **body})
    if candidate_id != expected_id:
        raise ValueError("candidate_id does not match candidate content")
    return str(candidate["generator_rule_id"]), candidate_id


def _validate_candidates_report(
    result: Mapping[str, Any],
    domain: str,
    ledger: Mapping[str, Mapping[str, str]],
) -> None:
    report = _require_mapping(result.get("review_candidates"), "result.review_candidates")
    _require_keys(
        report,
        "result.review_candidates",
        {
            "record_type",
            "schema_version",
            "domain",
            "disclaimer",
            "unavailable_controls",
            "degraded_sources",
            "candidates",
        },
    )
    if (
        report.get("record_type") != "review_candidates"
        or report.get("schema_version") != REVIEW_CANDIDATES_SCHEMA_VERSION
    ):
        raise ValueError("review candidate contract is unsupported")
    if report.get("domain") != domain:
        raise ValueError("review candidate domain must match scope domain")
    _require_string(report.get("disclaimer"), "result.review_candidates.disclaimer", 4096)
    for field in ("unavailable_controls", "degraded_sources"):
        values = _require_list(report.get(field), f"result.review_candidates.{field}")
        if not all(isinstance(value, str) and value for value in values) or values != sorted(set(values)):
            raise ValueError(f"review_candidates.{field} must be uniquely sorted strings")
    candidates = _require_list(report.get("candidates"), "result.review_candidates.candidates")
    order = []
    for index, raw in enumerate(candidates):
        candidate = _require_mapping(raw, f"candidate[{index}]")
        order.append(_validate_candidate(candidate, index=index, domain=domain, ledger=ledger))
    if order != sorted(order) or len(order) != len(set(order)):
        raise ValueError("review candidates must be uniquely and deterministically sorted")


def _validate_success(result: Mapping[str, Any], domain: str) -> None:
    _require_keys(result, "result", _SUCCESS_FIELDS)
    if result.get("queried_domain") != domain:
        raise ValueError("result domain must match scope domain")
    baseline = _validate_baseline(result, domain)
    ledger = _validate_ledger(result, domain)
    _validate_explanations(baseline, ledger)
    _validate_candidates_report(result, domain, ledger)


def _validate_error(result: Mapping[str, Any]) -> None:
    _require_keys(result, "result", _ERROR_FIELDS)
    if result.get("error_kind") not in _ERROR_KINDS:
        raise ValueError("review error kind is unsupported")
    roles = _require_list(result.get("failed_source_roles"), "result.failed_source_roles")
    if roles != sorted(set(roles)):
        raise ValueError("failed source roles must be uniquely sorted")
    for role in roles:
        _safe_role(role)


def _validate_workflow(
    bundle: Mapping[str, Any],
    *,
    success: bool,
    opportunities: list[dict[str, Any]],
) -> None:
    workflow = _require_mapping(bundle.get("workflow"), "workflow")
    _require_keys(workflow, "workflow", {"status", "collection_validity", "freshness_assessment"})
    if workflow.get("status") not in _WORKFLOW_STATUSES:
        raise ValueError("workflow.status is unsupported")
    if workflow.get("collection_validity") not in _COLLECTION_VALIDITY_STATES:
        raise ValueError("workflow.collection_validity is unsupported")
    if workflow.get("freshness_assessment") != "not_assigned":
        raise ValueError("workflow.freshness_assessment must be 'not_assigned'")
    expected_status = "completed" if success else "failed"
    if workflow.get("status") != expected_status:
        raise ValueError("workflow status does not match result")
    if workflow.get("collection_validity") != _collection_validity(opportunities):
        raise ValueError("workflow collection validity does not match source opportunities")


def _validate_error_consistency(
    bundle: Mapping[str, Any],
    result: Mapping[str, Any],
    opportunities: list[dict[str, Any]],
) -> None:
    _validate_error(result)
    roles = result["failed_source_roles"]
    if [row["source_role"] for row in opportunities] != roles or any(
        row["state"] != "unavailable" for row in opportunities
    ):
        raise ValueError("error source opportunities must exactly match failed source roles")
    cache = _require_mapping(bundle["collection"], "collection")["cache"]
    if any(cache[field] is not None for field in ("ct_provider_used", "ct_cache_age_days", "ct_attempt_outcome")):
        raise ValueError("error bundles must not claim CT result facts")


def validate_review_bundle(bundle: Mapping[str, Any]) -> None:
    """Fail closed on unknown owned fields, invalid references, or drift."""
    from recon_tool.review_bundle_schema import validate_review_bundle_document

    try:
        _validate_finite_json(bundle)
    except RecursionError as exc:
        raise ValueError("review bundle nesting exceeds the supported limit") from exc
    if set(bundle) != _TOP_LEVEL_FIELDS:
        raise ValueError("review bundle has unknown or missing top-level fields")
    if bundle.get("record_type") != "review_bundle":
        raise ValueError("review bundle record_type must be 'review_bundle'")
    if bundle.get("schema_version") != REVIEW_BUNDLE_SCHEMA_VERSION:
        raise ValueError(f"unsupported review bundle schema version: {bundle.get('schema_version')!r}")
    generated = parse_utc_time(bundle.get("generated_at"), "generated_at")
    _validate_context(bundle)
    result = _require_mapping(bundle.get("result"), "result")
    success = result.get("record_type") == "review_success"
    if not success and result.get("record_type") != "review_error":
        raise ValueError("result record_type must be review_success or review_error")
    domain = _validate_scope(bundle, success)
    started, ended = _validate_collection(bundle)
    if generated < ended:
        raise ValueError("generated_at must not precede collection.ended_at")
    opportunities = _validate_opportunities(bundle, started, ended)
    _validate_workflow(bundle, success=success, opportunities=opportunities)
    if success:
        if domain is None:
            raise ValueError("success bundle must carry a normalized scope domain")
        _validate_success(result, domain)
    else:
        _validate_error_consistency(bundle, result, opportunities)
    if bundle.get("scope_statement") != REVIEW_SCOPE_STATEMENT:
        raise ValueError("review scope statement is not the fixed v1 text")
    if bundle.get("limitations") != list(REVIEW_LIMITATIONS):
        raise ValueError("review limitations are not the fixed v1 list")
    validate_review_bundle_document(bundle)
    recorded_digest = _require_digest(bundle.get("content_digest"), "content_digest")
    without_digest = {key: value for key, value in bundle.items() if key != "content_digest"}
    if recorded_digest != content_digest(without_digest):
        raise ValueError("content_digest does not match review bundle content")


def load_review_bundle(path: Path) -> dict[str, Any]:
    """Load one bounded regular-file ReviewBundle and verify its integrity."""
    try:
        raw, _stat, _age = load_bounded_json_file(path, maximum_bytes=MAX_REVIEW_BUNDLE_BYTES)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise ValueError(f"Could not load review bundle {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError(f"Could not load review bundle {path}: root must be a JSON object")
    bundle = dict(raw)
    try:
        validate_review_bundle(bundle)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid review bundle {path}: {exc}") from exc
    return bundle


def write_review_bundle(path: Path, bundle: Mapping[str, Any], *, overwrite: bool = False) -> None:
    """Atomically write one validated ReviewBundle without accidental overwrite."""
    validate_review_bundle(bundle)
    parent = path.parent
    if not parent.is_dir():
        raise ValueError(f"Review bundle output directory does not exist: {parent}")
    if path.exists() and not overwrite:
        raise FileExistsError(f"Review bundle output already exists: {path}")
    payload = json.dumps(bundle, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if len(payload.encode("utf-8")) > MAX_REVIEW_BUNDLE_BYTES:
        raise ValueError("Review bundle exceeds the maximum artifact size")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f"{path.name}.", suffix=".tmp", dir=str(parent))
    reserved = False
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if not overwrite:
            reservation = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(reservation)
            reserved = True
        os.replace(temporary_name, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(temporary_name)
        if reserved:
            with contextlib.suppress(OSError):
                path.unlink()
        raise
