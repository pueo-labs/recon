"""MCP Registry server.json generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from scripts.generate_mcp_registry import (
    DECLARED_ARGV,
    DESCRIPTION,
    MCP_NAME_LINE,
    SCHEMA_URL,
    agreement_problems,
    check,
    registry_document,
    schema_problems,
    write,
)

ROOT = Path(__file__).resolve().parents[1]


def test_description_fits_the_registry_limit() -> None:
    assert 1 <= len(DESCRIPTION) <= 100


def test_fresh_registry_file_agrees_with_the_project_version(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "recon-tool"\nversion = "2.2.8"\n',
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(MCP_NAME_LINE + "\n", encoding="utf-8")
    write(tmp_path)

    assert agreement_problems(tmp_path) == []
    assert DECLARED_ARGV == ("uvx", "--from", "recon-tool", "recon", "mcp")
    assert registry_document("2.2.8")["$schema"] == SCHEMA_URL


def test_registry_identity_uses_the_organization_without_renaming_the_package() -> None:
    document = registry_document("2.27.0")
    assert document["name"] == "io.github.pueo-labs/recon"
    assert document["repository"] == {
        "url": "https://github.com/pueo-labs/recon",
        "source": "github",
        "id": "1207478328",
    }
    assert document["websiteUrl"] == "https://github.com/pueo-labs/recon"
    assert MCP_NAME_LINE == "<!-- mcp-name: io.github.pueo-labs/recon -->"
    packages = cast(list[dict[str, object]], document["packages"])
    assert packages[0]["identifier"] == "recon-tool"
    assert packages[0]["version"] == "2.27.0"


def test_generated_document_matches_the_vendored_schema() -> None:
    assert schema_problems(registry_document("2.26.1")) == []


def test_schema_rejects_a_description_over_100_characters() -> None:
    document = registry_document("2.26.1")
    document["description"] = "x" * 101
    assert schema_problems(document)


def test_committed_registry_matches_the_generator() -> None:
    assert check(ROOT) == []


def test_readme_publishes_the_mcp_name_on_its_own_line() -> None:
    assert MCP_NAME_LINE in (ROOT / "README.md").read_text(encoding="utf-8").splitlines()


def test_registry_file_stays_lf_on_checkout() -> None:
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8").splitlines()
    assert "server.json text eol=lf" in attributes


def test_version_drift_fails_agreement(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "recon-tool"\nversion = "2.2.8"\n', encoding="utf-8")
    readme = tmp_path / "README.md"
    readme.write_text(MCP_NAME_LINE + "\n", encoding="utf-8")
    write(tmp_path)
    payload = json.loads((tmp_path / "server.json").read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    document = cast(dict[str, object], payload)
    document["version"] = "2.2.7"
    (tmp_path / "server.json").write_text(json.dumps(document) + "\n", encoding="utf-8")

    problems = agreement_problems(tmp_path)

    assert any("2.2.7" in problem and "2.2.8" in problem for problem in problems)


def test_launch_drift_fails_agreement(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "recon-tool"\nversion = "2.2.8"\n',
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(MCP_NAME_LINE + "\n", encoding="utf-8")
    write(tmp_path)
    payload = json.loads((tmp_path / "server.json").read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    document = cast(dict[str, object], payload)
    packages = document["packages"]
    assert isinstance(packages, list)
    package = cast(dict[str, object], cast(list[object], packages)[0])
    package["packageArguments"] = [{"type": "positional", "value": "serve"}]
    (tmp_path / "server.json").write_text(json.dumps(document) + "\n", encoding="utf-8")

    problems = agreement_problems(tmp_path)

    assert any("declared launch" in problem for problem in problems)


def test_missing_readme_marker_fails_agreement(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "recon-tool"\nversion = "2.2.8"\n',
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("# recon\n", encoding="utf-8")
    write(tmp_path)

    problems = agreement_problems(tmp_path)

    assert any("mcp-name" in problem for problem in problems)


def test_registry_gate_is_wired_into_local_and_ci_gates() -> None:
    check_source = (ROOT / "scripts" / "check.py").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    release = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

    assert '(_CORE, "mcp-registry", [_PY, "scripts/generate_mcp_registry.py", "--check"]),' in check_source
    assert "run: uv run python scripts/generate_mcp_registry.py --check" in workflow
    assert "publish-mcp-registry:" in release
    assert "MCP_PUBLISHER_VERSION: v1.8.9" in release
    assert "releases/latest" not in release
    assert "./mcp-publisher login github-oidc" in release
    assert 'test "$GITHUB_REPOSITORY" = "pueo-labs/recon"' in release
    assert '"io.github.${GITHUB_REPOSITORY_OWNER}/recon"' in release
    registry_job = release.split("publish-mcp-registry:", 1)[1].split("github-release:", 1)[0]
    assert "needs: [verify-pypi-parity]" in registry_job
    assert "id-token: write" in registry_job
    assert registry_job.index("Validate repository and registry namespace") < registry_job.index(
        "./mcp-publisher login github-oidc"
    )
    assert "uv sync" not in release.split("publish-mcp-registry:", 1)[1].split("github-release:", 1)[0]
    assert "download-artifact" not in release.split("publish-mcp-registry:", 1)[1].split("github-release:", 1)[0]
