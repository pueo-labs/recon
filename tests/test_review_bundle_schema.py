# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportUnknownArgumentType=none, reportUnknownMemberType=none, reportUnknownVariableType=none
"""Generated ReviewBundle v1 schema contract tests."""

from __future__ import annotations

import copy
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from recon_tool.models import ConfidenceLevel, EvidenceRecord, SourceResult, TenantInfo
from recon_tool.review_bundle import (
    ReviewCollectionContext,
    build_review_bundle,
    build_review_error_bundle,
    validate_review_bundle,
)
from recon_tool.review_bundle_schema import (
    REVIEW_BUNDLE_TOP_LEVEL_FIELDS,
    build_review_bundle_schema,
    packaged_review_bundle_schema,
    packaged_review_bundle_schema_text,
)
from scripts import generate_review_bundle_schema

_ROOT = Path(__file__).resolve().parents[1]
_DOCS_SCHEMA = _ROOT / "docs" / "review-bundle-schema.json"
_PACKAGED_SCHEMA = _ROOT / "src" / "recon_tool" / "data" / "review-bundle-schema.json"
_START = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)
_END = _START + timedelta(seconds=2)


@pytest.fixture(scope="module")
def schema() -> dict[str, Any]:
    value = json.loads(_DOCS_SCHEMA.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    Draft202012Validator.check_schema(value)
    return value


@pytest.fixture(scope="module")
def success_bundle() -> dict[str, Any]:
    evidence = EvidenceRecord("DMARC", "v=DMARC1; p=none", "DMARC", "dmarc")
    info = TenantInfo(
        tenant_id=None,
        display_name="Example Industries Ltd",
        default_domain="example.com",
        queried_domain="example.com",
        confidence=ConfidenceLevel.MEDIUM,
        sources=("dns_records",),
        services=("DMARC",),
        slugs=("dmarc",),
        dmarc_policy="none",
        evidence=(evidence,),
        resolved_at=_END.isoformat(),
        ct_attempt_outcome="skipped",
    )
    result = SourceResult(
        source_name="dns_records",
        dmarc_policy="none",
        evidence=(evidence,),
        raw_dns_records=(("DMARC", evidence.raw_value),),
        ct_attempt_outcome="skipped",
    )
    return build_review_bundle(
        info,
        (result,),
        "Example.COM",
        _context(),
        generated_at=_END + timedelta(seconds=1),
    )


def _context() -> ReviewCollectionContext:
    return ReviewCollectionContext(
        started_at=_START,
        ended_at=_END,
        ct_enabled=False,
        timeout_seconds=30.0,
    )


def _validator(schema: dict[str, Any]) -> Draft202012Validator:
    return Draft202012Validator(schema, format_checker=FormatChecker())


def _assert_invalid(schema: dict[str, Any], value: dict[str, Any]) -> None:
    assert list(_validator(schema).iter_errors(value))


def _walk_refs(value: Any) -> list[str]:
    if isinstance(value, dict):
        refs = [item for key, item in value.items() if key == "$ref" and isinstance(item, str)]
        return refs + [ref for item in value.values() for ref in _walk_refs(item)]
    if isinstance(value, list):
        return [ref for item in value for ref in _walk_refs(item)]
    return []


def test_schema_validates_live_success_and_error_outputs(
    schema: dict[str, Any],
    success_bundle: dict[str, Any],
) -> None:
    failure = build_review_error_bundle(
        "bad coordinate",
        _context(),
        "timeout",
        failed_source_roles=("dns_records",),
        generated_at=_END + timedelta(seconds=1),
    )

    _validator(schema).validate(success_bundle)
    _validator(schema).validate(failure)


def test_schema_distinguishes_success_and_error_stages(
    schema: dict[str, Any],
    success_bundle: dict[str, Any],
) -> None:
    broken_success = copy.deepcopy(success_bundle)
    broken_success["workflow"]["status"] = "failed"
    _assert_invalid(schema, broken_success)

    failure = build_review_error_bundle(
        "bad coordinate",
        _context(),
        "validation",
        generated_at=_END + timedelta(seconds=1),
    )
    failure["result"]["explained_baseline"] = success_bundle["result"]["explained_baseline"]
    _assert_invalid(schema, failure)


@pytest.mark.parametrize(
    ("path", "field", "value"),
    [
        ((), "unexpected", True),
        (("generator",), "unexpected", True),
        (("scope",), "unexpected", True),
        (("collection",), "unexpected", True),
        (("collection", "options"), "unexpected", True),
        (("source_opportunities", 0), "unexpected", True),
        (("source_opportunities", 0, "observation_window"), "unexpected", True),
        (("workflow",), "unexpected", True),
        (("result",), "unexpected", True),
        (("result", "explained_baseline"), "unexpected", True),
        (("result", "evidence_ledger", 0), "unexpected", True),
        (("result", "review_candidates"), "unexpected", True),
        (("result", "review_candidates", "candidates", 0), "unexpected", True),
    ],
)
def test_review_bundle_owned_objects_are_closed(
    schema: dict[str, Any],
    success_bundle: dict[str, Any],
    path: tuple[str | int, ...],
    field: str,
    value: object,
) -> None:
    changed = copy.deepcopy(success_bundle)
    target: Any = changed
    for segment in path:
        target = target[segment]
    target[field] = value
    _assert_invalid(schema, changed)


@pytest.mark.parametrize(
    ("path", "bad_value"),
    [
        (("generated_at",), "not-a-timestamp"),
        (("content_digest",), "sha256:not-a-digest"),
        (("source_opportunities", 0, "state"), "unknown"),
        (("source_opportunities", 0, "instance_count"), 0),
        (("result", "evidence_ledger", 0, "evidence_id"), "broken"),
        (("result", "review_candidates", "candidates", 0, "candidate_id"), "broken"),
        (("result", "review_candidates", "candidates", 0, "evidence_ids"), ["broken"]),
    ],
)
def test_structural_integrity_fields_are_constrained(
    schema: dict[str, Any],
    success_bundle: dict[str, Any],
    path: tuple[str | int, ...],
    bad_value: object,
) -> None:
    changed = copy.deepcopy(success_bundle)
    target: Any = changed
    for segment in path[:-1]:
        target = target[segment]
    target[path[-1]] = bad_value
    _assert_invalid(schema, changed)


def test_schema_is_self_contained_and_embeds_current_lookup_schema(schema: dict[str, Any]) -> None:
    lookup = json.loads((_ROOT / "docs" / "recon-schema.json").read_text(encoding="utf-8"))
    rebuilt = build_review_bundle_schema(lookup)

    assert rebuilt == schema
    assert all(ref.startswith("#/") for ref in _walk_refs(schema))
    assert schema["$defs"]["LookupResult"]["title"] == lookup["title"]
    assert "$schema" not in schema["$defs"]["LookupResult"]
    assert "$id" not in schema["$defs"]["LookupResult"]
    assert "#/$defs/LookupResult/$defs/" in json.dumps(schema["$defs"]["LookupResult"])

    changed = copy.deepcopy(lookup)
    changed["title"] = "lookup schema drift sentinel"
    assert build_review_bundle_schema(changed)["$defs"]["LookupResult"]["title"] == changed["title"]


def test_generated_copies_and_packaged_loaders_are_exact(schema: dict[str, Any]) -> None:
    docs_text = _DOCS_SCHEMA.read_text(encoding="utf-8")
    packaged_text = _PACKAGED_SCHEMA.read_text(encoding="utf-8")

    assert docs_text == packaged_text
    assert packaged_review_bundle_schema_text() == docs_text
    assert packaged_review_bundle_schema() == schema
    assert tuple(schema["required"]) == REVIEW_BUNDLE_TOP_LEVEL_FIELDS
    assert generate_review_bundle_schema.main(["--check"]) == 0


def test_generator_check_detects_drift(tmp_path: Path) -> None:
    docs_copy = tmp_path / "review-bundle-schema.json"
    package_copy = tmp_path / "packaged-review-bundle-schema.json"
    current = _DOCS_SCHEMA.read_text(encoding="utf-8")
    docs_copy.write_text(current, encoding="utf-8")
    package_copy.write_text("{}\n", encoding="utf-8")

    assert (
        generate_review_bundle_schema.main(
            [
                "--check",
                "--docs-schema",
                str(docs_copy),
                "--packaged-schema",
                str(package_copy),
            ]
        )
        == 1
    )


def test_oversized_integer_timeout_is_a_validation_error(success_bundle: dict[str, Any]) -> None:
    bundle = copy.deepcopy(success_bundle)
    bundle["collection"]["options"]["timeout_seconds"] = 10**400
    with pytest.raises(ValueError, match="timeout_seconds"):
        validate_review_bundle(bundle)
