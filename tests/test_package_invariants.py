# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportUnknownArgumentType=none, reportUnknownMemberType=none, reportUnknownVariableType=none
"""Package artifact invariants for recon's intentionally small box.

These tests build a local wheel and inspect the archive directly. They pin the
traceability-matrix invariant that the package ships only the intended data
catalogs, and that runtime dependencies stay lean and free of ML, GeoIP, ASN, or
paid-vendor SDK surfaces.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tarfile
import zipfile
from email.parser import Parser
from pathlib import Path
from uuid import uuid4

from scripts import check_validation_hygiene

_REPO_ROOT = Path(__file__).resolve().parents[1]
_BUILD_CONSTRAINTS = _REPO_ROOT / "build-constraints.txt"

_PRIVATE_SDIST_PREFIXES = (
    ".agent/",
    "validation/agentic_ux/local/",
    "validation/agentic_ux/runs/",
    "validation/corpus-private/",
    "validation/live_runs/",
    "validation/local/",
    "validation/runs-private/",
)

_EXPECTED_DATA_FILES = {
    "recon_tool/data/bayesian_network.yaml",
    "recon_tool/data/fingerprints.generated.json",
    "recon_tool/data/motifs.yaml",
    "recon_tool/data/observation-capsule-schema.json",
    "recon_tool/data/posture.yaml",
    "recon_tool/data/profiles/fintech.yaml",
    "recon_tool/data/profiles/healthcare.yaml",
    "recon_tool/data/profiles/high-value-target.yaml",
    "recon_tool/data/profiles/higher-ed.yaml",
    "recon_tool/data/profiles/public-sector.yaml",
    "recon_tool/data/profiles/saas-b2b.yaml",
    "recon_tool/data/recon-schema.json",
    "recon_tool/data/review-bundle-schema.json",
    "recon_tool/data/signals.yaml",
    "recon_tool/data/surface-inventory.json",
}

_CANONICAL_FINGERPRINT_SOURCES = {
    "ai.yaml",
    "crm-marketing.yaml",
    "data-analytics.yaml",
    "discovered-signals.yaml",
    "email.yaml",
    "infrastructure.yaml",
    "productivity.yaml",
    "security.yaml",
    "surface.yaml",
    "verifications.yaml",
    "verticals.yaml",
}

_EXPECTED_RUNTIME_DEPENDENCIES = {
    "certifi",  # Patched CA bundle for the default HTTPX trust store.
    "deal",
    "defusedxml",
    "dnspython",
    "httpcore",  # Existing HTTPX transport dependency, now a direct guarded-backend API contract.
    "httpcore2",  # Security floor for the MCP HTTPX v2 transport.
    "httpx",
    "httpx2",  # Security floor for the MCP HTTPX v2 client.
    "anyio",  # Patched floor for the transitive async runtime.
    "jsonschema",
    "mcp",
    "networkx",
    "opentelemetry-api",  # Patched parser for trace context supplied to MCP.
    "publicsuffixlist",
    "pyjwt",  # Patched floor for the existing MCP JWT dependency.
    "python-multipart",
    "pyyaml",
    "rich",
    "typer",
}

_FORBIDDEN_DATA_SUFFIXES = {
    ".bin",
    ".csv",
    ".db",
    ".feather",
    ".geojson",
    ".joblib",
    ".mmdb",
    ".npy",
    ".npz",
    ".onnx",
    ".parquet",
    ".pickle",
    ".pkl",
    ".pt",
    ".pth",
    ".sqlite",
    ".sqlite3",
}

_FORBIDDEN_RUNTIME_DEPENDENCIES = {
    "azure-identity",
    "azure-mgmt-resource",
    "boto3",
    "botocore",
    "geoip2",
    "google-cloud",
    "google-cloud-compute",
    "maxminddb",
    "numpy",
    "pandas",
    "pyarrow",
    "pyasn",
    "pymc",
    "scikit-learn",
    "scipy",
    "sklearn",
    "stan",
    "tensorflow",
    "torch",
}


def _run_build(out_dir: Path, *build_args: str) -> None:
    uv_exe = shutil.which("uv")
    assert uv_exe is not None, "uv is required to build package artifacts"
    build_env = os.environ.copy()
    # Copy mode is deterministic across ordinary, cross-device, and
    # cloud-backed Windows cache locations. Artifact content is unchanged.
    build_env["UV_LINK_MODE"] = "copy"
    result = subprocess.run(  # noqa: S603 - fixed dev-tool argv, no shell.
        [
            uv_exe,
            "build",
            *build_args,
            "--out-dir",
            str(out_dir),
            "--build-constraints",
            str(_BUILD_CONSTRAINTS),
            "--require-hashes",
        ],
        cwd=_REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=build_env,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def _build_wheel(tmp_path: Path) -> Path:
    out_dir = tmp_path / "dist"
    sdist = _build_sdist(tmp_path)
    _run_build(out_dir, "--wheel", str(sdist))
    wheels = sorted(out_dir.glob("*.whl"))
    assert len(wheels) == 1
    return wheels[0]


def _build_sdist(tmp_path: Path) -> Path:
    out_dir = tmp_path / "dist"
    _run_build(out_dir, "--sdist")
    sdists = sorted(out_dir.glob("*.tar.gz"))
    assert len(sdists) == 1
    return sdists[0]


def _runtime_dependency_names(metadata_text: str) -> set[str]:
    metadata = Parser().parsestr(metadata_text)
    names: set[str] = set()
    for requirement in metadata.get_all("Requires-Dist") or []:
        match = re.match(r"\s*([A-Za-z0-9_.-]+)", requirement)
        assert match is not None, f"could not parse Requires-Dist: {requirement!r}"
        names.add(match.group(1).replace("_", "-").lower())
    return names


def test_wheel_ships_only_expected_catalog_data(tmp_path: Path) -> None:
    wheel = _build_wheel(tmp_path)
    assert wheel.name.endswith("-py3-none-any.whl")
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())

    data_files = {name for name in names if name.startswith("recon_tool/data/") and not name.endswith("/")}
    assert data_files == _EXPECTED_DATA_FILES

    forbidden_data = {name for name in data_files if Path(name).suffix.lower() in _FORBIDDEN_DATA_SUFFIXES}
    assert forbidden_data == set()

    unexpected_top_levels = {
        name.split("/", 1)[0]
        for name in names
        if "/" in name and not name.startswith("recon_tool/") and ".dist-info" not in name.split("/", 1)[0]
    }
    assert unexpected_top_levels == set()


def test_sdist_retains_public_sources_and_excludes_private_artifacts(tmp_path: Path) -> None:
    sentinel_dir = _REPO_ROOT / "validation" / "agentic_ux" / "local"
    sentinel_dir.mkdir(parents=True, exist_ok=True)
    sentinel = sentinel_dir / f"package-invariant-{uuid4().hex}.txt"
    sentinel.write_text("private package sentinel\n", encoding="utf-8")
    try:
        sdist = _build_sdist(tmp_path)
    finally:
        sentinel.unlink(missing_ok=True)

    with tarfile.open(sdist, "r:gz") as archive:
        members = [member for member in archive.getmembers() if member.isfile()]
        names = {Path(member.name).as_posix() for member in members}
        text_payloads = []
        for member in members:
            stream = archive.extractfile(member)
            if stream is None:
                continue
            try:
                text_payloads.append((member.name, stream.read().decode("utf-8")))
            except UnicodeDecodeError:
                continue

    relative_names = {name.split("/", 1)[1] for name in names if "/" in name}
    private_members = {
        name for name in relative_names if any(name.startswith(prefix) for prefix in _PRIVATE_SDIST_PREFIXES)
    }
    assert private_members == set()

    retired_identity_members = {
        name
        for name, text in text_payloads
        if check_validation_hygiene.RETIRED_TARGET_BRAND_RE.search(text)
        or check_validation_hygiene.RETIRED_PLACEHOLDER_RE.search(text)
    }
    assert retired_identity_members == set()

    fingerprint_sources = {
        Path(name).name for name in names if "/src/recon_tool/data/fingerprints/" in name and name.endswith(".yaml")
    }
    assert fingerprint_sources == _CANONICAL_FINGERPRINT_SOURCES
    assert any(name.endswith("/src/recon_tool/data/fingerprints.generated.json") for name in names)
    assert any(name.endswith("/build-constraints.txt") for name in names)
    assert {
        "validation/run_path_safety.py",
        "validation/evaluate_catalog_promotions.py",
        "validation/2026-06-25-squarespace-ext-sq.md",
        "validation/2026-06-25-ultradns-web-forwarding.md",
        "validation/2026-06-26-c3-ct-partial.md",
        "validation/2026-08-13-catalog-rank-round.md",
    } <= relative_names


def test_wheel_runtime_dependencies_stay_lean(tmp_path: Path) -> None:
    wheel = _build_wheel(tmp_path)
    with zipfile.ZipFile(wheel) as archive:
        metadata_name = next(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))
        metadata_text = archive.read(metadata_name).decode("utf-8")

    dependency_names = _runtime_dependency_names(metadata_text)
    assert dependency_names == _EXPECTED_RUNTIME_DEPENDENCIES
    assert dependency_names.isdisjoint(_FORBIDDEN_RUNTIME_DEPENDENCIES)
    # The patched floor must survive the sdist-to-wheel path. A lock update
    # alone would let pip retain an affected version in an existing install.
    assert "pyjwt>=2.14.0" in (Parser().parsestr(metadata_text).get_all("Requires-Dist") or [])
    assert "certifi>=2026.10.19" in (Parser().parsestr(metadata_text).get_all("Requires-Dist") or [])
    assert "opentelemetry-api>=1.45.2" in (Parser().parsestr(metadata_text).get_all("Requires-Dist") or [])
    assert "dnspython[doh]>=2.9.2" in (Parser().parsestr(metadata_text).get_all("Requires-Dist") or [])
