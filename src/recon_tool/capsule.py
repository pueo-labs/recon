# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportUnknownArgumentType=none, reportUnknownVariableType=none
"""Caller-owned observation capsules and classified comparisons.

Capsules are separate from recon's stable lookup JSON. They retain the bounded
normalized material needed to audit a collection, verify artifact integrity,
and replay the recorded state without another network request. They are local
files owned by the caller; recon does not upload or retain them as a service.
"""

from __future__ import annotations

import contextlib
import dataclasses
import hashlib
import json
import math
import os
import re
import tempfile
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from recon_tool import __version__
from recon_tool.cache import tenant_info_from_dict, tenant_info_to_dict
from recon_tool.formatter import format_tenant_dict
from recon_tool.json_limits import is_positive_timeout, load_bounded_json_file
from recon_tool.models import SourceResult, TenantInfo
from recon_tool.signals import signal_rule_names_from_observation
from recon_tool.validator import strip_control_chars, validate_domain

CAPSULE_SCHEMA_VERSION = "1.0"
NORMALIZER_VERSION = "2"
MAX_CAPSULE_BYTES = 10 * 1024 * 1024

_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_DATA_DIR = Path(__file__).with_name("data")
_CATALOG_FILES = ("fingerprints.generated.json", "motifs.yaml", "signals.yaml")
_MODEL_FILES = ("bayesian_network.yaml",)
_SCALAR_FACT_FIELDS = (
    "tenant_id",
    "display_name",
    "default_domain",
    "region",
    "auth_type",
    "dmarc_policy",
    "google_auth_type",
    "google_idp_name",
    "mta_sts_mode",
    "dmarc_pct",
    "dmarc_np",
    "cloud_instance",
    "tenant_region_sub_scope",
    "msgraph_host",
)
_TOP_LEVEL_FIELDS = {
    "capsule_schema_version",
    "record_type",
    "queried_domain",
    "collection",
    "interpretation_context",
    "source_opportunities",
    "observations",
    "normalized_snapshot",
    "interpretation",
    "content_digest",
}

__all__ = [
    "CAPSULE_SCHEMA_VERSION",
    "MAX_CAPSULE_BYTES",
    "NORMALIZER_VERSION",
    "CollectionContext",
    "build_capsule",
    "canonical_json_bytes",
    "compare_capsules",
    "content_digest",
    "current_interpretation_context",
    "load_capsule",
    "parse_utc_time",
    "project_source_observations",
    "replay_capsule",
    "utc_text",
    "validate_capsule",
    "validate_collection_vantage",
    "write_capsule",
]


@dataclasses.dataclass(frozen=True, slots=True)
class CollectionContext:
    """Caller-controlled collection settings and observation window."""

    started_at: datetime
    ended_at: datetime
    ct_enabled: bool
    direct_probes: bool
    timeout_seconds: float
    vantage: str = "caller-local"


def canonical_json_bytes(value: object) -> bytes:
    """Return recon's deterministic UTF-8 JSON encoding for artifact digests."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def content_digest(value: object) -> str:
    """Return the lowercase SHA-256 digest of one canonical JSON value."""
    return f"sha256:{hashlib.sha256(canonical_json_bytes(value)).hexdigest()}"


# Backward-compatible private aliases for the capsule implementation and its
# established mutation tests. New caller-owned artifacts use the public names.
_canonical_bytes = canonical_json_bytes
_sha256 = content_digest


def _digest_files(names: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for name in sorted(names):
        content = (_DATA_DIR / name).read_bytes()
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return f"sha256:{digest.hexdigest()}"


def current_interpretation_context() -> dict[str, str]:
    """Identify packaged inputs and the effective operator-local interpretation.

    Hash loaded catalogs, including custom and ephemeral entries, rather than
    re-reading custom files that a long-running process has not reloaded.
    Existing capsules keep their recorded digests and remain valid; the
    packaged-only context used historically no longer claims an exact match.
    """
    from recon_tool.bayesian_loader import apply_priors_override, load_network, load_priors_override
    from recon_tool.fingerprints import load_fingerprints
    from recon_tool.motifs import load_motifs
    from recon_tool.signals import load_signals

    catalog = {
        "packaged_digest": _digest_files(_CATALOG_FILES),
        "fingerprints": [dataclasses.asdict(item) for item in load_fingerprints()],
        "signals": [dataclasses.asdict(item) for item in load_signals()],
        "motifs": [dataclasses.asdict(item) for item in load_motifs()],
    }
    model = {
        "packaged_digest": _digest_files(_MODEL_FILES),
        "network": dataclasses.asdict(apply_priors_override(load_network(), load_priors_override())),
    }
    return {
        "recon_version": __version__,
        "normalizer_version": NORMALIZER_VERSION,
        "catalog_digest": content_digest(catalog),
        "model_digest": content_digest(model),
    }


def utc_text(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("artifact timestamps must be timezone-aware")
    return value.astimezone(UTC).isoformat()


def parse_utc_time(value: object, field: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a non-empty ISO 8601 datetime")
    normalized = f"{value[:-1]}+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO 8601 datetime") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include a timezone")
    try:
        return parsed.astimezone(UTC)
    except OverflowError as exc:
        raise ValueError(f"{field} must be within the supported UTC datetime range") from exc


_utc_text = utc_text
_parse_time = parse_utc_time


def _json_value(value: object) -> Any:
    """Normalize tuples and dataclasses to their ordinary JSON value shape."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        value = dataclasses.asdict(value)
    return json.loads(_canonical_bytes(value))


def _fact(source_role: str, kind: str, key: str, value: object) -> dict[str, Any]:
    body = {
        "source_role": source_role,
        "kind": kind,
        "key": key,
        "value": _json_value(value),
    }
    return {"fact_id": _sha256(body), **body}


def _scalar_facts(result: SourceResult) -> list[dict[str, Any]]:
    """Return the optional scalar facts retained by one source."""
    role = result.source_name
    facts = [
        _fact(role, "normalized_scalar", field, value)
        for field in _SCALAR_FACT_FIELDS
        if (value := getattr(result, field)) is not None
    ]
    optional_values: tuple[tuple[bool, str, object], ...] = (
        (result.m365_detected, "m365_detected", True),
        (result.dmarc_policy is not None, "dmarc_testing", result.dmarc_testing),
        (
            bool(result.spf_include_count)
            or any(record_type.upper() == "SPF" for record_type, _ in result.raw_dns_records),
            "spf_include_count",
            result.spf_include_count,
        ),
        (result.ct_attempt_outcome is not None, "ct_subdomain_count", result.ct_subdomain_count),
        (result.ct_cache_age_days is not None, "ct_cache_age_days", result.ct_cache_age_days),
    )
    facts.extend(_fact(role, "normalized_scalar", key, value) for include, key, value in optional_values if include)
    return facts


def _result_facts(result: SourceResult) -> tuple[dict[str, Any], ...]:
    """Project one successful source result into stable normalized facts."""
    if result.error is not None or result.source_unavailable:
        return ()

    role = result.source_name
    facts = _scalar_facts(result)

    for value in sorted(set(result.tenant_domains)):
        facts.append(_fact(role, "normalized_set_member", "tenant_domain", value))
    for value in sorted(set(result.related_domains)):
        facts.append(_fact(role, "normalized_set_member", "related_domain", value))
    for value in sorted(set(result.site_verification_tokens)):
        facts.append(_fact(role, "normalized_set_member", "site_verification_token", value))
    for record_type, value in sorted(set(result.raw_dns_records)):
        facts.append(_fact(role, "retained_dns_record", record_type.upper(), value))
    if result.cert_summary is not None:
        facts.append(_fact(role, "normalized_object", "certificate_summary", result.cert_summary))
    if result.bimi_identity is not None:
        facts.append(_fact(role, "normalized_object", "bimi_identity", result.bimi_identity))
    return tuple(facts)


def _source_state(results: list[SourceResult], facts: tuple[dict[str, Any], ...]) -> str:
    if all(result.source_unavailable for result in results):
        return "unavailable"
    degraded = any(result.degraded_sources for result in results)
    if degraded or any(result.source_unavailable for result in results):
        return "partial"
    return "observed_value" if facts else "observed_empty"


def project_source_observations(
    results: Iterable[SourceResult],
    *,
    started_at: str,
    ended_at: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Retain only attempted collection instances as observation opportunities."""
    by_role: dict[str, list[SourceResult]] = {}
    for result in results:
        if result.not_attempted:
            continue
        by_role.setdefault(result.source_name, []).append(result)

    all_facts: dict[str, dict[str, Any]] = {}
    opportunities: list[dict[str, Any]] = []
    for role in sorted(by_role):
        role_results = by_role[role]
        role_facts_by_id: dict[str, dict[str, Any]] = {}
        for result in role_results:
            for fact in _result_facts(result):
                role_facts_by_id[fact["fact_id"]] = fact
        role_facts = tuple(role_facts_by_id[key] for key in sorted(role_facts_by_id))
        all_facts.update(role_facts_by_id)
        opportunities.append(
            {
                "source_role": role,
                "state": _source_state(role_results, role_facts),
                "instance_count": len(role_results),
                "degraded_markers": sorted({marker for result in role_results for marker in result.degraded_sources}),
                "observation_window": {
                    "started_at": started_at,
                    "ended_at": ended_at,
                },
            }
        )
    return opportunities, [all_facts[key] for key in sorted(all_facts)]


_source_observations = project_source_observations


def _stable_signal_ids(info: TenantInfo) -> list[str]:
    identifiers = {
        identifier for insight in info.insights for identifier in signal_rule_names_from_observation(insight)
    }
    return sorted(identifiers)


def _without_digest(capsule: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in capsule.items() if key != "content_digest"}


def validate_collection_vantage(vantage: str, *, label: str = "capsule") -> str:
    """Validate the same caller label before collection and artifact creation."""
    safe = strip_control_chars(vantage, max_len=128).strip()
    if not safe or safe != vantage:
        raise ValueError(f"{label} vantage must be 1 to 128 printable characters")
    return safe


def build_capsule(
    info: TenantInfo,
    results: Iterable[SourceResult],
    collection: CollectionContext,
) -> dict[str, Any]:
    """Build one deterministic, integrity-bound observation capsule."""
    started_text = _utc_text(collection.started_at)
    ended_text = _utc_text(collection.ended_at)
    if collection.ended_at < collection.started_at:
        raise ValueError("capsule collection end must not precede its start")
    if not is_positive_timeout(collection.timeout_seconds):
        raise ValueError("capsule timeout must be finite and positive")
    safe_vantage = validate_collection_vantage(collection.vantage)

    domain = validate_domain(info.queried_domain, apex=False)
    if domain != info.queried_domain:
        raise ValueError("capsule domain must already be normalized")
    opportunities, observations = _source_observations(
        results,
        started_at=started_text,
        ended_at=ended_text,
    )
    snapshot_info = dataclasses.replace(info, resolved_at=info.resolved_at or ended_text, cached_at=None)
    normalized_snapshot = tenant_info_to_dict(snapshot_info)
    normalized_snapshot.pop("_cached_at", None)
    rendered_result = format_tenant_dict(snapshot_info)
    interpretation = {
        "stable_signal_ids": _stable_signal_ids(snapshot_info),
        "rendered_result_digest": _sha256(rendered_result),
        "rendered_result": rendered_result,
    }
    capsule: dict[str, Any] = {
        "capsule_schema_version": CAPSULE_SCHEMA_VERSION,
        "record_type": "observation_capsule",
        "queried_domain": domain,
        "collection": {
            "started_at": started_text,
            "ended_at": ended_text,
            "as_of": ended_text,
            "options": {
                "ct_enabled": collection.ct_enabled,
                "direct_probes": collection.direct_probes,
                "timeout_seconds": collection.timeout_seconds,
            },
            "vantage": safe_vantage,
            "cache": {
                "result_cache": "bypassed",
                "ct_provider_used": info.ct_provider_used,
                "ct_cache_age_days": info.ct_cache_age_days,
                "ct_attempt_outcome": info.ct_attempt_outcome,
            },
        },
        "interpretation_context": current_interpretation_context(),
        "source_opportunities": opportunities,
        "observations": observations,
        "normalized_snapshot": normalized_snapshot,
        "interpretation": interpretation,
    }
    capsule["content_digest"] = _sha256(capsule)
    validate_capsule(capsule)
    return capsule


def _require_mapping(value: object, field: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be a JSON object")
    return value


def _require_keys(value: Mapping[str, Any], field: str, keys: set[str]) -> None:
    if set(value) != keys:
        raise ValueError(f"{field} has unknown or missing fields")


def _require_list(value: object, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a JSON array")
    return value


def _require_string(value: object, field: str, *, maximum: int = 512) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise ValueError(f"{field} must be a non-empty string of at most {maximum} characters")
    if strip_control_chars(value, max_len=maximum) != value:
        raise ValueError(f"{field} must not contain control characters")
    return value


def _validate_digest(value: object, field: str) -> str:
    digest = _require_string(value, field, maximum=71)
    if _DIGEST_RE.fullmatch(digest) is None:
        raise ValueError(f"{field} must be a lowercase SHA-256 digest")
    return digest


def _validate_finite_json(value: object, field: str = "capsule") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{field} must not contain non-finite numbers")
    if isinstance(value, list):
        for item in value:
            _validate_finite_json(item, field)
    elif isinstance(value, dict):
        for item in value.values():
            _validate_finite_json(item, field)


def _validate_collection(capsule: Mapping[str, Any]) -> None:
    collection = _require_mapping(capsule.get("collection"), "collection")
    _require_keys(collection, "collection", {"started_at", "ended_at", "as_of", "options", "vantage", "cache"})
    started = _parse_time(collection.get("started_at"), "collection.started_at")
    ended = _parse_time(collection.get("ended_at"), "collection.ended_at")
    as_of = _parse_time(collection.get("as_of"), "collection.as_of")
    if ended < started:
        raise ValueError("collection.ended_at must not precede collection.started_at")
    if as_of < started:
        raise ValueError("collection.as_of must not precede collection.started_at")
    _require_string(collection.get("vantage"), "collection.vantage", maximum=128)
    options = _require_mapping(collection.get("options"), "collection.options")
    _require_keys(options, "collection.options", {"ct_enabled", "direct_probes", "timeout_seconds"})
    for field in ("ct_enabled", "direct_probes"):
        if type(options.get(field)) is not bool:
            raise ValueError(f"collection.options.{field} must be a boolean")
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


def _validate_context(capsule: Mapping[str, Any]) -> None:
    context = _require_mapping(capsule.get("interpretation_context"), "interpretation_context")
    _require_keys(
        context,
        "interpretation_context",
        {"recon_version", "normalizer_version", "catalog_digest", "model_digest"},
    )
    _require_string(context.get("recon_version"), "interpretation_context.recon_version", maximum=64)
    _require_string(context.get("normalizer_version"), "interpretation_context.normalizer_version", maximum=32)
    _validate_digest(context.get("catalog_digest"), "interpretation_context.catalog_digest")
    _validate_digest(context.get("model_digest"), "interpretation_context.model_digest")


def _validate_opportunities(capsule: Mapping[str, Any]) -> None:
    rows = _require_list(capsule.get("source_opportunities"), "source_opportunities")
    collection = _require_mapping(capsule.get("collection"), "collection")
    collection_started = _parse_time(collection.get("started_at"), "collection.started_at")
    collection_ended = _parse_time(collection.get("ended_at"), "collection.ended_at")
    roles: list[str] = []
    for index, value in enumerate(rows):
        row = _require_mapping(value, f"source_opportunities[{index}]")
        _require_keys(
            row,
            f"source_opportunities[{index}]",
            {"source_role", "state", "instance_count", "degraded_markers", "observation_window"},
        )
        role = _require_string(row.get("source_role"), f"source_opportunities[{index}].source_role", maximum=128)
        roles.append(role)
        if row.get("state") not in {"observed_value", "observed_empty", "partial", "unavailable"}:
            raise ValueError(f"source_opportunities[{index}].state is invalid")
        count = row.get("instance_count")
        if type(count) is not int or count < 1:
            raise ValueError(f"source_opportunities[{index}].instance_count must be a positive integer")
        markers = _require_list(row.get("degraded_markers"), f"source_opportunities[{index}].degraded_markers")
        if not all(isinstance(marker, str) and marker for marker in markers):
            raise ValueError(f"source_opportunities[{index}].degraded_markers must contain strings")
        if markers != sorted(set(markers)):
            raise ValueError(f"source_opportunities[{index}].degraded_markers must be uniquely sorted")
        window = _require_mapping(row.get("observation_window"), f"source_opportunities[{index}].observation_window")
        _require_keys(
            window,
            f"source_opportunities[{index}].observation_window",
            {"started_at", "ended_at"},
        )
        started = _parse_time(
            window.get("started_at"),
            f"source_opportunities[{index}].observation_window.started_at",
        )
        ended = _parse_time(
            window.get("ended_at"),
            f"source_opportunities[{index}].observation_window.ended_at",
        )
        if ended < started:
            raise ValueError(f"source_opportunities[{index}] observation window is reversed")
        if (started, ended) != (collection_started, collection_ended):
            raise ValueError(f"source_opportunities[{index}] observation window must match collection window")
    if roles != sorted(set(roles)):
        raise ValueError("source_opportunities must be uniquely sorted by source_role")


def _validate_observations(capsule: Mapping[str, Any]) -> None:
    facts = _require_list(capsule.get("observations"), "observations")
    source_roles = {
        str(_require_mapping(row, "source opportunity")["source_role"])
        for row in _require_list(capsule.get("source_opportunities"), "source_opportunities")
    }
    identifiers: list[str] = []
    for index, value in enumerate(facts):
        fact = _require_mapping(value, f"observations[{index}]")
        if set(fact) != {"fact_id", "source_role", "kind", "key", "value"}:
            raise ValueError(f"observations[{index}] has unknown or missing fields")
        identifier = _validate_digest(fact.get("fact_id"), f"observations[{index}].fact_id")
        identifiers.append(identifier)
        body = {
            "source_role": _require_string(fact.get("source_role"), f"observations[{index}].source_role", maximum=128),
            "kind": _require_string(fact.get("kind"), f"observations[{index}].kind", maximum=128),
            "key": _require_string(fact.get("key"), f"observations[{index}].key", maximum=512),
            "value": fact.get("value"),
        }
        if body["source_role"] not in source_roles:
            raise ValueError(f"observations[{index}].source_role has no source opportunity")
        if identifier != _sha256(body):
            raise ValueError(f"observations[{index}].fact_id does not match its content")
    if identifiers != sorted(set(identifiers)):
        raise ValueError("observations must be uniquely sorted by fact_id")


def _validate_interpretation(capsule: Mapping[str, Any]) -> None:
    interpretation = _require_mapping(capsule.get("interpretation"), "interpretation")
    _require_keys(
        interpretation,
        "interpretation",
        {"stable_signal_ids", "rendered_result_digest", "rendered_result"},
    )
    identifiers = _require_list(interpretation.get("stable_signal_ids"), "interpretation.stable_signal_ids")
    if not all(isinstance(identifier, str) and identifier for identifier in identifiers):
        raise ValueError("interpretation.stable_signal_ids must contain non-empty strings")
    if identifiers != sorted(set(identifiers)):
        raise ValueError("interpretation.stable_signal_ids must be uniquely sorted")
    result = _require_mapping(interpretation.get("rendered_result"), "interpretation.rendered_result")
    recorded_digest = _validate_digest(
        interpretation.get("rendered_result_digest"),
        "interpretation.rendered_result_digest",
    )
    if recorded_digest != _sha256(result):
        raise ValueError("interpretation.rendered_result_digest does not match rendered_result")
    if result.get("record_type") != "lookup" or result.get("schema_version") != "2.0":
        raise ValueError("interpretation.rendered_result must be a stable v2 lookup record")
    if result.get("queried_domain") != capsule.get("queried_domain"):
        raise ValueError("interpretation.rendered_result domain does not match queried_domain")


def validate_capsule(capsule: Mapping[str, Any]) -> None:
    """Validate capsule structure, normalized snapshot, and both digests."""
    try:
        _validate_finite_json(capsule)
    except RecursionError as exc:
        raise ValueError("capsule nesting exceeds the supported limit") from exc
    if set(capsule) != _TOP_LEVEL_FIELDS:
        raise ValueError("capsule has unknown or missing top-level fields")
    if capsule.get("capsule_schema_version") != CAPSULE_SCHEMA_VERSION:
        raise ValueError(f"unsupported capsule schema version: {capsule.get('capsule_schema_version')!r}")
    if capsule.get("record_type") != "observation_capsule":
        raise ValueError("capsule record_type must be 'observation_capsule'")
    domain = _require_string(capsule.get("queried_domain"), "queried_domain", maximum=253)
    if validate_domain(domain, apex=False) != domain:
        raise ValueError("queried_domain must already be normalized")
    _validate_collection(capsule)
    _validate_context(capsule)
    _validate_opportunities(capsule)
    _validate_observations(capsule)
    snapshot = _require_mapping(capsule.get("normalized_snapshot"), "normalized_snapshot")
    if "_cached_at" in snapshot:
        raise ValueError("normalized_snapshot must not carry a cache-write timestamp")
    restored = tenant_info_from_dict(dict(snapshot))
    if restored.queried_domain != domain:
        raise ValueError("normalized_snapshot domain does not match queried_domain")
    _validate_interpretation(capsule)
    recorded_digest = _validate_digest(capsule.get("content_digest"), "content_digest")
    if recorded_digest != _sha256(_without_digest(capsule)):
        raise ValueError("content_digest does not match capsule content")


def load_capsule(path: Path) -> dict[str, Any]:
    """Load one bounded regular-file capsule and verify its integrity."""
    try:
        raw, _stat, _age = load_bounded_json_file(path, maximum_bytes=MAX_CAPSULE_BYTES)
    except (OSError, UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise ValueError(f"Could not load capsule {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError(f"Could not load capsule {path}: root must be a JSON object")
    capsule = dict(raw)
    try:
        validate_capsule(capsule)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid capsule {path}: {exc}") from exc
    return capsule


def write_capsule(path: Path, capsule: Mapping[str, Any], *, overwrite: bool = False) -> None:
    """Atomically write one validated capsule without accidental overwrite."""
    validate_capsule(capsule)
    parent = path.parent
    if not parent.is_dir():
        raise ValueError(f"Capsule output directory does not exist: {parent}")
    if path.exists() and not overwrite:
        raise FileExistsError(f"Capsule output already exists: {path}")
    payload = json.dumps(capsule, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if len(payload.encode("utf-8")) > MAX_CAPSULE_BYTES:
        raise ValueError("Capsule exceeds the maximum artifact size")
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


def replay_capsule(capsule: Mapping[str, Any], *, as_of: str | None = None) -> dict[str, Any]:
    """Replay a capsule locally through the current stable renderer."""
    validate_capsule(capsule)
    collection = _require_mapping(capsule["collection"], "collection")
    recorded_as_of = _require_string(collection["as_of"], "collection.as_of")
    evaluated = _utc_text(_parse_time(as_of or recorded_as_of, "as_of"))
    snapshot = _require_mapping(capsule["normalized_snapshot"], "normalized_snapshot")
    info = tenant_info_from_dict(dict(snapshot))
    rendered = format_tenant_dict(info)
    current_context = current_interpretation_context()
    recorded_context = dict(_require_mapping(capsule["interpretation_context"], "interpretation_context"))
    return {
        "capsule_schema_version": CAPSULE_SCHEMA_VERSION,
        "record_type": "observation_capsule_replay",
        "queried_domain": capsule["queried_domain"],
        "capsule_digest": capsule["content_digest"],
        "recorded_as_of": recorded_as_of,
        "evaluated_as_of": evaluated,
        "time_evaluation_changed": evaluated != _utc_text(_parse_time(recorded_as_of, "collection.as_of")),
        "interpretation_context_match": recorded_context == current_context,
        "recorded_interpretation_context": recorded_context,
        "current_interpretation_context": current_context,
        "replayed_result_digest": _sha256(rendered),
        "result": rendered,
    }


def _opportunities_by_role(capsule: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    rows = _require_list(capsule["source_opportunities"], "source_opportunities")
    return {
        str(_require_mapping(row, "source opportunity")["source_role"]): _require_mapping(row, "source opportunity")
        for row in rows
    }


def _facts_by_role(capsule: Mapping[str, Any]) -> dict[str, dict[str, Mapping[str, Any]]]:
    grouped: dict[str, dict[str, Mapping[str, Any]]] = {}
    for value in _require_list(capsule["observations"], "observations"):
        fact = _require_mapping(value, "observation")
        grouped.setdefault(str(fact["source_role"]), {})[str(fact["fact_id"])] = fact
    return grouped


def _delta_fact(fact: Mapping[str, Any], capsule: Mapping[str, Any]) -> dict[str, Any]:
    collection = _require_mapping(capsule["collection"], "collection")
    return {
        "fact_id": fact["fact_id"],
        "source_role": fact["source_role"],
        "kind": fact["kind"],
        "key": fact["key"],
        "value": fact["value"],
        "observation_window": {
            "started_at": collection["started_at"],
            "ended_at": collection["ended_at"],
        },
    }


def _collection_changes(before: Mapping[str, Any], after: Mapping[str, Any]) -> list[dict[str, Any]]:
    before_collection = _require_mapping(before["collection"], "collection")
    after_collection = _require_mapping(after["collection"], "collection")
    changes: list[dict[str, Any]] = []
    for field in ("options", "vantage", "cache"):
        if before_collection[field] != after_collection[field]:
            changes.append({"field": field, "before": before_collection[field], "after": after_collection[field]})
    before_roles = _opportunities_by_role(before)
    after_roles = _opportunities_by_role(after)
    for role in sorted(set(before_roles) | set(after_roles)):
        previous = before_roles.get(role)
        current = after_roles.get(role)
        previous_state = None if previous is None else previous["state"]
        current_state = None if current is None else current["state"]
        previous_markers = None if previous is None else previous["degraded_markers"]
        current_markers = None if current is None else current["degraded_markers"]
        if (previous_state, previous_markers) != (current_state, current_markers):
            changes.append(
                {
                    "field": f"source_opportunity:{role}",
                    "before": {"state": previous_state, "degraded_markers": previous_markers},
                    "after": {"state": current_state, "degraded_markers": current_markers},
                }
            )
    return changes


def _observation_changes(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    before_roles = _opportunities_by_role(before)
    after_roles = _opportunities_by_role(after)
    before_facts = _facts_by_role(before)
    after_facts = _facts_by_role(after)
    added: list[dict[str, Any]] = []
    removed: list[dict[str, Any]] = []
    suppressed: list[str] = []
    comparable_states = {"observed_value", "observed_empty"}
    for role in sorted(set(before_roles) | set(after_roles)):
        previous = before_roles.get(role)
        current = after_roles.get(role)
        if (
            previous is None
            or current is None
            or previous["state"] not in comparable_states
            or current["state"] not in comparable_states
        ):
            suppressed.append(role)
            continue
        previous_facts = before_facts.get(role, {})
        current_facts = after_facts.get(role, {})
        added.extend(_delta_fact(current_facts[key], after) for key in sorted(set(current_facts) - set(previous_facts)))
        removed.extend(
            _delta_fact(previous_facts[key], before) for key in sorted(set(previous_facts) - set(current_facts))
        )
    return added, removed, suppressed


def _interpretation_changes(before: Mapping[str, Any], after: Mapping[str, Any]) -> list[dict[str, Any]]:
    before_context = _require_mapping(before["interpretation_context"], "interpretation_context")
    after_context = _require_mapping(after["interpretation_context"], "interpretation_context")
    changes: list[dict[str, Any]] = []
    for field in ("recon_version", "normalizer_version", "catalog_digest", "model_digest"):
        if before_context[field] != after_context[field]:
            changes.append({"field": field, "before": before_context[field], "after": after_context[field]})
    before_interpretation = _require_mapping(before["interpretation"], "interpretation")
    after_interpretation = _require_mapping(after["interpretation"], "interpretation")
    if before_interpretation["stable_signal_ids"] != after_interpretation["stable_signal_ids"]:
        changes.append(
            {
                "field": "stable_signal_ids",
                "before": before_interpretation["stable_signal_ids"],
                "after": after_interpretation["stable_signal_ids"],
            }
        )
    before_facts = _require_list(before["observations"], "observations")
    after_facts = _require_list(after["observations"], "observations")
    if (
        before_facts == after_facts
        and before_interpretation["rendered_result_digest"] != after_interpretation["rendered_result_digest"]
    ):
        changes.append(
            {
                "field": "rendered_result",
                "before": before_interpretation["rendered_result_digest"],
                "after": after_interpretation["rendered_result_digest"],
            }
        )
    return changes


def compare_capsules(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    *,
    before_as_of: str | None = None,
    after_as_of: str | None = None,
) -> dict[str, Any]:
    """Classify observation, collection, time, and interpretation changes."""
    validate_capsule(before)
    validate_capsule(after)
    if before["queried_domain"] != after["queried_domain"]:
        raise ValueError("capsules must describe the same queried_domain")
    before_collection = _require_mapping(before["collection"], "collection")
    after_collection = _require_mapping(after["collection"], "collection")
    previous_time = _utc_text(_parse_time(before_as_of or before_collection["as_of"], "before_as_of"))
    current_time = _utc_text(_parse_time(after_as_of or after_collection["as_of"], "after_as_of"))
    added, removed, suppressed = _observation_changes(before, after)
    collection_changes = _collection_changes(before, after)
    interpretation_changes = _interpretation_changes(before, after)
    result = {
        "capsule_schema_version": CAPSULE_SCHEMA_VERSION,
        "record_type": "observation_capsule_delta",
        "queried_domain": before["queried_domain"],
        "before_capsule_digest": before["content_digest"],
        "after_capsule_digest": after["content_digest"],
        "observation": {
            "changed": bool(added or removed),
            "added": added,
            "removed": removed,
            "suppressed_source_roles": suppressed,
        },
        "collection_regime": {
            "changed": bool(collection_changes),
            "changes": collection_changes,
        },
        "time_evaluation": {
            "changed": previous_time != current_time,
            "before_as_of": previous_time,
            "after_as_of": current_time,
            "freshness_changes": [],
        },
        "interpretation": {
            "changed": bool(interpretation_changes),
            "changes": interpretation_changes,
        },
    }
    result["has_changes"] = bool(
        added or removed or collection_changes or previous_time != current_time or interpretation_changes
    )
    return result
