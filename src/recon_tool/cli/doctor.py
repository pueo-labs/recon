# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportUnknownArgumentType=none
"""Doctor command implementation: environment/identity/CT/MCP/catalog checks.

Extracted from cli.py (docs/roadmap.md god-file track). Plain command-logic
helpers; the Typer app and the thin @app.command wrappers stay in cli.py, which
imports this module and references the orchestrators through a small assignment
facade. Imports the shared cli helpers / formatter; never imports cli.py.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal, TypeAlias

import typer

from recon_tool.cli.config_directory import config_directory_check
from recon_tool.cli.doctor_report import (
    CERTSPOTTER_CHECK_NAME,
    CT_CHECK_NAME,
    NEXT_MCP_REINSTALL,
    NEXT_RERUN,
    DoctorCheck,
    DoctorStatus,
    emit_doctor_json,
    render_summary,
    summarize_checks,
)
from recon_tool.cli.shared import fmt_exc as _fmt_exc
from recon_tool.cli.shared import render_diagnostic_status_row
from recon_tool.cli.shared import render_status_row as _render_status_row
from recon_tool.cli.shared import safe_diagnostic_markup as _safe_markup
from recon_tool.exit_codes import (
    EXIT_ERROR,
    EXIT_VALIDATION,
)
from recon_tool.formatter import get_console, get_err_console
from recon_tool.formatter.theme import ERROR, SUCCESS, WARNING

McpCheck: TypeAlias = DoctorCheck

_NEXT_IDENTITY = f"check network or proxy access to Microsoft identity endpoints, {NEXT_RERUN}"
_NEXT_DNS = f"check the system resolver and network, {NEXT_RERUN}"
_NEXT_REINSTALL = f"reinstall recon-tool in this environment, {NEXT_RERUN}"
_LIMITATIONS_RESOLVER_ANCHOR = "docs/limitations.md#resolvers-that-answer-names-that-should-not-exist"
RESOLVER_ANSWERS_NONEXISTENT = (
    "Resolver answers names that should not exist; related-domain results will be unreliable. "
    f"See {_LIMITATIONS_RESOLVER_ANCHOR}"
)
# RFC 6761 reserves `.invalid`: no name under it can exist, so any answer for
# one comes from the resolver itself rather than from the DNS.
RESOLVER_PROBE_PREFIX = "recon-doctor-nonexistent-"
_NEXT_RESOLVER = f"use a resolver that returns NXDOMAIN for nonexistent names, {NEXT_RERUN}"


TemplateCreateStatus: TypeAlias = Literal["created", "exists", "non_file"]

_LAUNCHER_VERSION_RE = re.compile(r"^recon\s+v?(?P<version>\d+\.\d+\.\d+)$", re.IGNORECASE)
_LAUNCHER_VERSION_TIMEOUT_SECONDS = 5.0


def _classify_template_collision(target: Path) -> TemplateCreateStatus | None:
    """Classify a publish collision without letting a probe mask the original error."""
    try:
        if not target.exists():
            return None
        return "exists" if target.is_file() else "non_file"
    except OSError:
        return None


def _create_template_atomically(target: Path, content: str) -> TemplateCreateStatus:
    """Publish a complete template without replacing any existing path.

    A same-directory hard link is the portable no-replace publication step.
    Filesystems without hard-link support fail safely instead of weakening the
    scaffold's no-overwrite guarantee.
    """
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=f".{target.name}.",
            suffix=".tmp",
            dir=target.parent,
            delete=False,
        ) as stream:
            temp_path = Path(stream.name)
            stream.write(content)

        try:
            os.link(temp_path, target)
        except OSError:
            collision = _classify_template_collision(target)
            if collision is not None:
                return collision
            raise
        return "created"
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


_SIGNALS_TEMPLATE = """\
# Custom signals are merged with built-in signals at load time.
# Each entry defines a derived intelligence signal.
#
# Fields:
#   name:           Signal display name
#   category:       Signal category: security, identity, infrastructure, saas
#   confidence:     Signal confidence: high, medium, low
#   description:    Human-readable description (use hedged language for inferences)
#   requires:       List of fingerprint slugs required (all must match)
#   min_matches:    (optional) Minimum number of required slugs that must match
#   metadata:       (optional) Additional conditions on metadata fields
#     - field:      Metadata field: dmarc_policy, auth_type, email_security_score
#       operator:   Comparison: eq, neq, gte, lte
#       value:      Value to compare against
#
# Example:
# signals:
#   - name: "Custom Security Signal"
#     category: "security"
#     confidence: "medium"
#     description: "Custom security tooling indicators"
#     requires:
#       - "delta-sso"
#     min_matches: 1

signals: []
"""


_FINGERPRINTS_TEMPLATE = """\
# Custom fingerprints are merged with built-in fingerprints at load time.
# Each entry adds a new SaaS/service detection rule.
#
# Fields:
#   name:           Human-readable service name (shown in output)
#   slug:           Unique identifier (lowercase, hyphens)
#   type:           Detection type: txt, spf, mx, ns, cname, cname_target, subdomain_txt, caa, srv, dmarc_rua
#   pattern:        Regex pattern to match against DNS record value
#   category:       Service category: email, security, identity, saas, infrastructure
#   provider_group: (optional) Group for display: microsoft365, google-workspace
#   display_group:  (optional) Override display grouping
#
# Example:
# fingerprints:
#   - name: "Synthetic Delta SSO"
#     slug: "delta-sso"
#     type: "txt"
#     pattern: "delta-domain-verification="
#     category: "identity"

fingerprints: []
"""


def _mcp_tool_registry_check(server_mcp: Any, required_tools: frozenset[str]) -> McpCheck:
    """Return the static canonical-tool registry check."""
    try:
        tools = asyncio.run(server_mcp.list_tools())
        tool_names = {str(getattr(tool, "name", "")) for tool in tools}
        missing_tools = sorted(required_tools - tool_names)
        if missing_tools:
            return DoctorCheck(
                "Tools enumerated",
                "fail",
                f"{len(tools)} registered; missing canonical: {', '.join(missing_tools)}",
                NEXT_MCP_REINSTALL,
            )
        return DoctorCheck(
            "Tools enumerated",
            "ok",
            f"{len(tools)} registered; {len(required_tools)} canonical tools present",
        )
    except Exception as exc:
        return DoctorCheck("Tools enumerated", "fail", f"{exc}", NEXT_MCP_REINSTALL)


def _mcp_resource_registry_check(server_mcp: Any, required_resources: tuple[str, ...]) -> McpCheck:
    """Return the static canonical-resource registry check."""
    try:
        resources = asyncio.run(server_mcp.list_resources())
        resource_uris = {str(getattr(resource, "uri", "")) for resource in resources}
        missing_resources = [uri for uri in required_resources if uri not in resource_uris]
        if missing_resources:
            return DoctorCheck(
                "Resources enumerated",
                "fail",
                f"{len(resources)} registered; missing canonical: {', '.join(missing_resources)}",
                NEXT_MCP_REINSTALL,
            )
        return DoctorCheck(
            "Resources enumerated",
            "ok",
            f"{len(resources)} registered; {len(required_resources)} canonical resources present",
        )
    except Exception as exc:
        return DoctorCheck("Resources enumerated", "fail", f"{exc}", NEXT_MCP_REINSTALL)


def _render_mcp_reference_config() -> None:
    """Render the generic config and safe-installer guidance."""
    from recon_tool.mcp_client.install import build_recon_block, warn_if_fallback

    console = get_err_console()
    recon_block = build_recon_block()
    console.print()
    console.print(
        f"  [{WARNING}]Security note:[/{WARNING}] `recon mcp` runs with the privileges of\n"
        "  the calling user. Start with manual approvals and only expand\n"
        "  `autoApprove` if you fully understand the risk."
    )
    console.print()
    console.print("  [bold]Reference config for clients that use `mcpServers`[/bold]")
    console.print()
    console.print("  [dim]# Claude Desktop: ~/Library/Application Support/Claude/claude_desktop_config.json[/dim]")
    console.print("  [dim]# Cursor: ~/.cursor/mcp.json or <project>/.cursor/mcp.json[/dim]")
    console.print("  [dim]# Windsurf: ~/.codeium/windsurf/mcp_config.json[/dim]")
    console.print("  [dim]# Kiro: ~/.kiro/settings/mcp.json or <project>/.kiro/settings/mcp.json[/dim]")
    console.print(
        "  [dim]# VS Code uses a different top-level `servers` key; run `recon mcp install --client=vscode`.[/dim]"
    )
    console.print(
        "  [dim]# Prefer `recon mcp install --client=<name>` so existing client configuration is merged safely.[/dim]"
    )
    console.print()
    # The reference config is the command's only stdout payload, so
    # `recon doctor --mcp > config.json` captures valid JSON.
    typer.echo(json.dumps({"mcpServers": {"recon": recon_block}}, indent=2))
    console.print()

    if warn_if_fallback() is not None:
        console.print(
            f"  [{WARNING}]Tip:[/{WARNING}] GUI clients (Claude Desktop, Windsurf) often don't\n"
            "  inherit your shell PATH. The config above uses recon's safe\n"
            "  sys.path-stripping Python fallback. For a shorter config, add\n"
            "  `recon` to PATH and rerun `recon doctor --mcp`."
        )
        console.print()


def doctor_mcp() -> None:
    """Validate the static MCP registry and emit copy-pasteable client config."""
    import shutil
    import sys

    # Check rows are diagnostics: keep them on stderr so a redirect or pipe
    # receives only the machine-readable JSON stanza emitted on stdout.
    console = get_err_console()
    console.print()

    checks: list[McpCheck] = []

    # 1. MCP package importable
    import importlib

    try:
        importlib.import_module("mcp")
        from recon_tool.mcp_client.sdk_compat import SDK_FAMILY, SDK_VERSION

        checks.append(DoctorCheck("MCP package", "ok", f"mcp {SDK_VERSION} ({SDK_FAMILY}) installed"))
    except ImportError as exc:
        checks.append(DoctorCheck("MCP package", "fail", f"not installed: {exc}", NEXT_MCP_REINSTALL))
        _render_mcp_checks(checks, summary=True)
        raise typer.Exit(code=EXIT_ERROR) from exc

    # 2. Server module imports cleanly
    try:
        from recon_tool.server import mcp as server_mcp

        checks.append(DoctorCheck("Server module", "ok", "loaded"))
    except Exception as exc:
        checks.append(DoctorCheck("Server module", "fail", f"import failed: {exc}", NEXT_MCP_REINSTALL))
        _render_mcp_checks(checks, summary=True)
        raise typer.Exit(code=EXIT_ERROR) from exc

    # 3. MCP server has instructions
    instructions = getattr(server_mcp, "instructions", None)
    if isinstance(instructions, str) and instructions.strip():
        checks.append(DoctorCheck("Server Instructions", "ok", f"{len(instructions)} chars"))
    else:
        checks.append(
            DoctorCheck("Server Instructions", "fail", "missing; agents may misuse tools", NEXT_MCP_REINSTALL)
        )

    # 4. Enumerate tools through the public SDK surface and require the
    # canonical workflow anchors. Extra registered tools remain compatible.
    from recon_tool.mcp_client.dns_readiness import DNS_CHECK_NAME, collection_policy_readiness
    from recon_tool.mcp_client.doctor import REQUIRED_RESOURCES, REQUIRED_TOOLS
    from recon_tool.server.app import MCP_COLLECTION_POLICY

    readiness = collection_policy_readiness(MCP_COLLECTION_POLICY)
    checks.append(DoctorCheck(DNS_CHECK_NAME, readiness.status, readiness.detail, readiness.next))

    checks.append(_mcp_tool_registry_check(server_mcp, REQUIRED_TOOLS))

    # 5. Enumerate local resources independently so a tool-list failure does
    # not hide a second registration problem.
    checks.append(_mcp_resource_registry_check(server_mcp, REQUIRED_RESOURCES))

    # 6. recon executable on PATH (important for short GUI-client configs).
    # A missing launcher is informational: the generated config still works
    # through the interpreter fallback.
    config_directory = config_directory_check()
    if config_directory is not None:
        checks.append(config_directory)

    recon_path = shutil.which("recon")
    if recon_path:
        checks.append(DoctorCheck("recon on PATH", "ok", recon_path))
    else:
        checks.append(
            DoctorCheck("recon on PATH", "info", f"not found; generated config will use {sys.executable} fallback")
        )

    _render_mcp_checks(checks, summary=True)

    # Keep the reference config in sync with the safe installer.
    _render_mcp_reference_config()

    if any(check.status == "fail" for check in checks):
        raise typer.Exit(code=EXIT_ERROR)


def _render_mcp_checks(checks: Sequence[DoctorCheck], *, summary: bool = False) -> None:
    """Render MCP check rows, then optionally the closing summary, on stderr."""
    console = get_err_console()
    for check in checks:
        _render_status_row(console, check.status, check.name, check.detail)
        if check.next:
            render_diagnostic_status_row(console, mark="", style="dim", name="Next", detail=check.next)
    if summary:
        console.print()
        render_summary(console, summarize_checks(checks, mode="mcp"))


def validate_doctor_mode(
    *,
    fix: bool,
    mcp: bool,
    client: str | None,
    config_path: str | None,
    json_output: bool = False,
) -> None:
    """Reject incompatible local modes before any filesystem or network work."""
    if int(fix) + int(mcp) + int(client is not None) > 1:
        get_console().print(f"[{ERROR}]Choose exactly one of --fix, --mcp, or --client.[/{ERROR}]")
        raise typer.Exit(code=EXIT_VALIDATION)
    if config_path is not None and client is None:
        get_console().print(f"[{ERROR}]--config-path requires --client.[/{ERROR}]")
        raise typer.Exit(code=EXIT_VALIDATION)
    if json_output and (fix or mcp):
        # --mcp already writes its mcpServers reference config to stdout, and
        # --fix writes files rather than reporting checks.
        get_err_console().print(
            f"[{ERROR}]--json works with recon doctor and --client, not with --fix or --mcp.[/{ERROR}]"
        )
        raise typer.Exit(code=EXIT_VALIDATION)


def _client_check(check: Any, client: str) -> DoctorCheck:
    """Lift a client-doctor row into the shared doctor check shape."""
    status: DoctorStatus = check.status
    next_step = f"recon mcp install --client={client}" if status == "fail" else None
    return DoctorCheck(str(check.name), status, str(check.detail), next_step)


def doctor_client(client: str, config_path: str | None = None, *, json_output: bool = False) -> None:
    """Read a client's MCP config and report whether recon is registered.

    Complements `--mcp` (which validates the server) by answering the
    other half of "did the install work": does the client's own config
    file carry the recon server entry that client would load.
    """
    from recon_tool.mcp_client.client_doctor import check_client
    from recon_tool.mcp_client.install import SUPPORTED_CLIENTS, InstallError, expand_config_path

    console = get_err_console() if json_output else get_console()
    if not json_output:
        console.print()

    if client not in SUPPORTED_CLIENTS:
        console.print(
            f"  [{ERROR}]unknown client '{_safe_markup(client)}'[/{ERROR}]\n  Supported: {', '.join(SUPPORTED_CLIENTS)}"
        )
        raise typer.Exit(EXIT_VALIDATION)

    try:
        override = expand_config_path(config_path) if config_path is not None else None
        report = check_client(client, config_path_override=override)  # pyright: ignore[reportArgumentType]
    except (InstallError, ValueError, OSError) as exc:
        console.print(f"  [{ERROR}]client config check refused:[/{ERROR}] {_safe_markup(exc)}")
        raise typer.Exit(EXIT_VALIDATION) from exc

    checks = [_client_check(check, client) for check in report.checks]
    summary = summarize_checks(checks, mode="client", client=client)
    if json_output:
        emit_doctor_json(checks, summary, mode="client", client=client, notes=report.notes)
        if summary.exit_code:
            raise typer.Exit(summary.exit_code)
        return

    console.print(f"  [bold]MCP client config check: {_safe_markup(client)}[/bold]")
    console.print()
    for check in checks:
        _render_status_row(console, check.status, check.name, check.detail)

    if report.notes:
        console.print()
        for note in report.notes:
            console.print(f"  [dim]note:[/dim] {_safe_markup(note)}")

    console.print()
    render_summary(console, summary)
    if summary.status == "fail":
        console.print(
            "  See the inspected paths above; add --config-path to check an explicit profile.",
            soft_wrap=True,
        )
    console.print()
    if summary.exit_code:
        raise typer.Exit(summary.exit_code)


def doctor_fix() -> bool:
    """Scaffold template config files and report whether every write succeeded."""

    from recon_tool.paths import config_dir as _config_dir

    console = get_console()
    config_dir = _config_dir()

    try:
        config_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        console.print(
            f"[{ERROR}]Cannot create config directory {_safe_markup(config_dir)}: {_safe_markup(exc)}[/{ERROR}]"
        )
        return False

    templates = [
        ("fingerprints.yaml", _FINGERPRINTS_TEMPLATE),
        ("signals.yaml", _SIGNALS_TEMPLATE),
    ]

    failures = 0
    for filename, content in templates:
        target = config_dir / filename
        try:
            status = _create_template_atomically(target, content)
            if status == "created":
                console.print(f"  [{SUCCESS}]created:[/{SUCCESS}] {_safe_markup(target)}")
            elif status == "exists":
                console.print(f"  already exists: {_safe_markup(target)}")
            else:
                failures += 1
                console.print(f"  [{ERROR}]cannot use {_safe_markup(target)}: path is not a regular file[/{ERROR}]")
        except OSError as exc:
            failures += 1
            console.print(f"  [{ERROR}]failed to create {_safe_markup(target)}: {_safe_markup(exc)}[/{ERROR}]")

    if failures:
        noun = "template" if failures == 1 else "templates"
        console.print(f"  [{ERROR}]{failures} {noun} could not be created.[/{ERROR}]")
        return False
    return True


def _doctor_print_header(console: Any) -> None:
    """Print version, schema, interpreter, package, and install identity.

    The substring "v2.0 stable schema" (vs "pre-v2.0 schema") reports the
    schema-lock generation. Fusion execution policy is independent of schema
    stability and is documented by the CLI flags and ADR-0013.
    """
    import recon_tool
    from recon_tool import __version__, updater

    console.print()
    schema_label = "v2.0 stable schema" if __version__.startswith("2.") else "pre-v2.0 schema"
    console.print(f"  recon [bold]v{__version__}[/bold] [dim]({schema_label})[/dim]")
    python_executable = _safe_markup(Path(sys.executable).resolve())
    package_file = getattr(recon_tool, "__file__", None)
    package_location = Path(package_file).resolve().parent if package_file else "unknown"
    method = updater.detect_install_method()
    method_detail = f"{method} (best effort)" if method == updater.PIP else method
    # Preserve copyable paths in captured output even at narrow terminal widths.
    console.print(f"  Python [bold]{sys.version.split()[0]}[/bold] at {python_executable}", soft_wrap=True)
    if not (3, 11) <= sys.version_info[:2] <= (3, 15) or sys.version_info.releaselevel != "final":
        console.print(f"  [{WARNING}]Python is outside the tested stable range (3.11 through 3.15).[/{WARNING}]")
    console.print(f"  Package {_safe_markup(package_location)}", soft_wrap=True)
    console.print(f"  Install method {_safe_markup(method_detail)}")
    console.print()


def _same_path(left: Path, right: Path) -> bool:
    """Compare resolved paths with Windows case folding."""
    return os.path.normcase(str(left)) == os.path.normcase(str(right))


def _is_relative_lexical(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _is_relative_launcher_path(path: Path) -> bool:
    s = str(path)
    if not s or s == ".":
        return True
    if s.startswith((".", "..")):
        return True
    return not (path.is_absolute() or s.startswith(("/", "\\")))


def _target_in_ancestors(target: Path, current_directory: Path) -> bool:
    try:
        resolved_t = target.resolve()
    except OSError:
        return True
    home = Path.home().resolve()
    for ancestor in (current_directory, *current_directory.parents):
        if ancestor == ancestor.parent or home.is_relative_to(ancestor):
            break
        if resolved_t.is_relative_to(ancestor) or _is_relative_lexical(target, ancestor):
            return True
    return False


def _launcher_is_in_current_workspace(launcher: Path, lexical: Path | None = None) -> bool:
    """Refuse to execute a launcher planted in the current workspace tree."""
    try:
        current_directory = Path.cwd().resolve()
        targets = [launcher]
        if lexical is not None:
            targets.append(lexical)
            if _is_relative_launcher_path(lexical):
                return True

        for candidate in (current_directory, *current_directory.parents):
            if (candidate / ".git").exists():
                return any(t.resolve().is_relative_to(candidate) or _is_relative_lexical(t, candidate) for t in targets)

        return any(_target_in_ancestors(t, current_directory) for t in targets)
    except OSError:
        return True


def _launcher_version(launcher: Path) -> tuple[str | None, str | None]:
    """Read a PATH launcher's version without involving a command shell."""
    if os.name == "nt" and launcher.suffix.casefold() in {".bat", ".cmd"}:
        return None, "batch launchers are not executed by doctor"
    try:
        completed = subprocess.run(  # noqa: S603 - absolute PATH result, fixed argument, no shell.
            [str(launcher), "--version"],
            capture_output=True,
            check=False,
            shell=False,
            timeout=_LAUNCHER_VERSION_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, _fmt_exc(exc)

    # Capture bytes so a stale or hostile launcher cannot crash doctor merely
    # by emitting output that is invalid under the host's default codec.
    # Replacement decoding is sufficient here because only an exact ASCII
    # version line is accepted below; undecodable bytes can never strengthen a
    # match. Keep supporting text-valued CompletedProcess fixtures/embedders.
    def _decode(value: bytes | str | None) -> str:
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")
        return value or ""

    output = "\n".join((_decode(completed.stdout), _decode(completed.stderr)))[:2048]
    if completed.returncode != 0:
        return None, f"version check exited {completed.returncode}"
    for line in output.splitlines():
        match = _LAUNCHER_VERSION_RE.fullmatch(line.strip())
        if match is not None:
            return match.group("version"), None
    return None, "version output was not recognized"


def _doctor_path_launcher_check() -> DoctorCheck:
    """Compare the first PATH launcher with the package running doctor."""
    from recon_tool import updater

    found = shutil.which("recon")
    if found is None:
        return DoctorCheck(
            "PATH recon launcher",
            "ok",
            f"not found; this environment can use `{sys.executable} -m recon_tool`",
        )
    lexical = Path(found)
    try:
        launcher = lexical.resolve()
        executable_dir = Path(sys.executable).resolve().parent
    except OSError as exc:
        return DoctorCheck("PATH recon launcher", "warn", f"could not resolve {found}: {_fmt_exc(exc)}")

    expected_launchers = (executable_dir / "recon", executable_dir / "recon.exe")
    if any(_same_path(launcher, candidate) for candidate in expected_launchers):
        launcher_version = updater.current_version()
        error = None
    elif _is_relative_launcher_path(lexical) or _launcher_is_in_current_workspace(launcher, lexical=lexical):
        launcher_version = None
        error = "launcher is inside the current workspace and was not executed"
    else:
        launcher_version, error = _launcher_version(lexical)

    current = updater.current_version()
    if launcher_version is None:
        return DoctorCheck(
            "PATH recon launcher",
            "warn",
            f"{lexical} could not be verified ({error}); run `{lexical} --version`, then activate the intended "
            "environment or reinstall recon-tool for that launcher",
        )
    if updater.compare_versions(launcher_version, current) != 0:
        return DoctorCheck(
            "PATH recon launcher",
            "warn",
            f"{lexical} reports {launcher_version}, but this process is {current}; activate the intended environment "
            "or reinstall recon-tool for that launcher, then rerun `recon doctor`",
        )
    return DoctorCheck("PATH recon launcher", "ok", f"{lexical} reports {launcher_version}")


def _http_check(name: str, status_code: int) -> DoctorCheck:
    """Map an identity-endpoint HTTP status to a doctor row."""
    if status_code == 200:
        return DoctorCheck(name, "ok", f"HTTP {status_code}")
    return DoctorCheck(name, "fail", f"HTTP {status_code}", _NEXT_IDENTITY)


async def _doctor_identity_checks() -> list[DoctorCheck]:
    """Probe the Microsoft identity-discovery endpoints (OIDC, GetUserRealm, Autodiscover)."""
    import httpx

    checks: list[DoctorCheck] = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get("https://login.microsoftonline.com/common/.well-known/openid-configuration")
            checks.append(_http_check("OIDC discovery", resp.status_code))
        except (httpx.RequestError, OSError) as exc:
            checks.append(DoctorCheck("OIDC discovery", "fail", _fmt_exc(exc), _NEXT_IDENTITY))

        # Synthetic non-existent address avoids probing a real account.
        try:
            resp = await client.get(
                "https://login.microsoftonline.com/GetUserRealm.srf",
                params={"login": "recon-connectivity-check@example.com", "json": "1"},
            )
            checks.append(_http_check("GetUserRealm", resp.status_code))
        except (httpx.RequestError, OSError) as exc:
            checks.append(DoctorCheck("GetUserRealm", "fail", _fmt_exc(exc), _NEXT_IDENTITY))

        try:
            resp = await client.post(
                "https://autodiscover-s.outlook.com/autodiscover/autodiscover.svc",
                content="<test/>",
                headers={"Content-Type": "text/xml"},
            )
            checks.append(DoctorCheck("Autodiscover", "ok", f"HTTP {resp.status_code} (reachable)"))
        except (httpx.RequestError, OSError) as exc:
            checks.append(DoctorCheck("Autodiscover", "fail", _fmt_exc(exc), _NEXT_IDENTITY))
    return checks


def _dns_failure_detail(exc: BaseException, qname: str, rdtype: str) -> str:
    """Describe a dnspython failure in plain language instead of its raw message."""
    import dns.exception
    import dns.resolver

    if isinstance(exc, dns.resolver.NXDOMAIN):
        return f"the resolver says {qname} does not exist"
    if isinstance(exc, dns.resolver.NoAnswer):
        return f"the resolver returned no {rdtype} records for {qname}"
    if isinstance(exc, dns.resolver.NoNameservers):
        return "no configured resolver could answer; every server failed or refused the query"
    if isinstance(exc, dns.exception.Timeout):
        return "the resolver did not answer in time"
    return f"could not reach the resolver ({_fmt_exc(exc)})"


def _doctor_dns_check() -> DoctorCheck:
    """Resolve a known-good TXT record to confirm DNS works."""
    import dns.exception
    import dns.resolver

    try:
        answers = dns.resolver.resolve("example.com", "TXT")
        return DoctorCheck("DNS resolution", "ok", f"{len(list(answers))} TXT records")  # pyright: ignore[reportArgumentType]
    except (dns.exception.DNSException, OSError) as exc:
        detail = _dns_failure_detail(exc, "example.com", "TXT")
        if isinstance(exc, (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer)):
            # example.com publishes TXT records, so either answer is wrong.
            detail = f"{detail}, although it publishes them; the resolver may be filtering or rewriting answers"
        return DoctorCheck("DNS resolution", "fail", detail, _NEXT_DNS)


def _doctor_resolver_probe() -> DoctorCheck:
    """Ask the system resolver for a name that cannot exist.

    Lookups use this same default resolver. A captive, filtering, or
    NXDOMAIN-rewriting resolver answers names that do not exist, which makes
    related-domain probing report artifact hosts as real. The doctor's
    example.com TXT check cannot reveal that: it asks for a name that does
    exist. So doctor makes one extra query, here only and never at lookup time,
    for a random label under ``.invalid``. RFC 6761 reserves that TLD so no
    name under it exists anywhere; any answer other than NXDOMAIN came from the
    resolver itself. The random label defeats caching. A subdomain of
    example.com is not a safe probe because that zone may synthesize answers.
    """
    import secrets

    import dns.exception
    import dns.resolver

    name = "Nonexistent-name probe"
    qname = f"{RESOLVER_PROBE_PREFIX}{secrets.token_hex(6)}.invalid"
    try:
        dns.resolver.resolve(qname, "A")
    except dns.resolver.NXDOMAIN:
        return DoctorCheck(name, "ok", "reserved test name returned NXDOMAIN")
    except dns.resolver.NoAnswer:
        # NOERROR with no records still claims the name exists.
        return DoctorCheck(name, "warn", RESOLVER_ANSWERS_NONEXISTENT, _NEXT_RESOLVER)
    except (dns.exception.DNSException, OSError) as exc:
        detail = _dns_failure_detail(exc, qname, "A")
        return DoctorCheck(name, "info", f"could not run the probe: {detail}")
    return DoctorCheck(name, "warn", RESOLVER_ANSWERS_NONEXISTENT, _NEXT_RESOLVER)


def _doctor_ct_status(name: str, status_code: int) -> DoctorCheck:
    """Map one certificate-transparency probe to a doctor row."""
    if status_code == 200:
        return DoctorCheck(name, "ok", "HTTP 200")
    return DoctorCheck(name, "warn", f"HTTP {status_code} (optional enrichment degraded)")


async def _doctor_ct_checks() -> list[DoctorCheck]:
    """Probe crt.sh, then CertSpotter, once each for the reserved example.com name."""
    import httpx

    from recon_tool.sources.cert_providers import CertSpotterProvider

    async with httpx.AsyncClient(timeout=8.0) as client:
        try:
            resp = await client.get("https://crt.sh/?q=%.example.com&output=json")
            crtsh = _doctor_ct_status(CT_CHECK_NAME, resp.status_code)
        except (httpx.RequestError, OSError) as exc:
            crtsh = DoctorCheck(CT_CHECK_NAME, "warn", f"{_fmt_exc(exc)} (optional enrichment degraded)")
        try:
            resp = await CertSpotterProvider().connectivity_probe(client, "example.com")
            certspotter = _doctor_ct_status(CERTSPOTTER_CHECK_NAME, resp.status_code)
        except (httpx.RequestError, OSError) as exc:
            certspotter = DoctorCheck(CERTSPOTTER_CHECK_NAME, "warn", f"{_fmt_exc(exc)} (optional enrichment degraded)")
    return [crtsh, certspotter]


def _doctor_mcp_check() -> DoctorCheck:
    """Confirm the MCP server module imports cleanly."""
    try:
        from recon_tool.server import mcp  # noqa: F401  # pyright: ignore[reportUnusedImport]

        return DoctorCheck("MCP server module", "ok", "loaded")
    except Exception as exc:
        return DoctorCheck("MCP server module", "fail", _fmt_exc(exc), _NEXT_REINSTALL)


def _doctor_fingerprint_db_check() -> DoctorCheck:
    """Confirm the built-in fingerprint database loads."""
    try:
        from recon_tool.fingerprints import load_fingerprints

        fps = load_fingerprints()
        if fps:
            return DoctorCheck("Fingerprint database", "ok", f"{len(fps)} fingerprints loaded")
        return DoctorCheck(
            "Fingerprint database", "fail", "no fingerprints loaded; detection will not work", _NEXT_REINSTALL
        )
    except Exception as exc:
        return DoctorCheck("Fingerprint database", "fail", _fmt_exc(exc), _NEXT_REINSTALL)


def _doctor_custom_path(filename: str) -> Path:
    """Resolve a custom config file path in the config dir (env / legacy / XDG)."""
    from recon_tool.paths import config_dir

    return config_dir() / filename


def _custom_file_next(path: Path) -> str:
    return f"fix or move aside {path}, {NEXT_RERUN}"


def _doctor_custom_fingerprints_check() -> DoctorCheck:
    """Report on the optional user fingerprints.yaml overlay."""
    custom_path = _doctor_custom_path("fingerprints.yaml")
    if not custom_path.exists():
        return DoctorCheck("Custom fingerprints", "ok", f"none ({custom_path} not found)")
    try:
        import yaml

        data = yaml.safe_load(custom_path.read_text(encoding="utf-8"))
        count = 0
        if isinstance(data, dict) and "fingerprints" in data:
            count = len(data["fingerprints"])
        elif isinstance(data, list):
            count = len(data)
        return DoctorCheck("Custom fingerprints", "ok", f"{count} entries in {custom_path}")
    except Exception as exc:
        return DoctorCheck("Custom fingerprints", "fail", _fmt_exc(exc), _custom_file_next(custom_path))


def _doctor_signal_db_check() -> DoctorCheck:
    """Confirm the built-in signal database loads.

    Reports the loaded total and the reportable subset separately. ``recon
    signals list`` renders only signals carrying a public observation label,
    so the two surfaces legitimately differ; naming the split here keeps an
    operator verifying their install from reading the gap as a lost catalog.
    """
    try:
        from recon_tool.signals import load_signals, reportable_signals

        sigs = load_signals()
        if sigs:
            listed = len(reportable_signals())
            detail = f"{len(sigs)} signals loaded ({listed} reportable via `recon signals list`)"
            return DoctorCheck("Signal database", "ok", detail)
        return DoctorCheck(
            "Signal database", "fail", "no signals loaded; signal intelligence will not work", _NEXT_REINSTALL
        )
    except Exception as exc:
        return DoctorCheck("Signal database", "fail", _fmt_exc(exc), _NEXT_REINSTALL)


def _doctor_schema_fields_check() -> DoctorCheck:
    """Verify the locked-schema top-level fields are still emitted by ``format_tenant_json``.

    The v2.0 quality bar: synthesise a minimal TenantInfo, render it
    through the JSON formatter, and confirm every required top-level field from
    ``recon_tool.schema_contract.REQUIRED_TOP_LEVEL_FIELDS`` appears. Drift
    between that tuple and ``docs/recon-schema.json#/required`` is caught at PR
    time by ``tests/test_json_schema_file.py``.
    """
    try:
        import json as _json

        from recon_tool.formatter import format_tenant_json
        from recon_tool.models import ConfidenceLevel, TenantInfo
        from recon_tool.schema_contract import REQUIRED_TOP_LEVEL_FIELDS

        sample = TenantInfo(
            tenant_id="recon-doctor-sample",
            display_name="recon doctor synthetic",
            default_domain="example.invalid",
            queried_domain="example.invalid",
            confidence=ConfidenceLevel.LOW,
        )
        payload = _json.loads(format_tenant_json(sample))
        missing = sorted(set(REQUIRED_TOP_LEVEL_FIELDS) - set(payload.keys()))
        if missing:
            return DoctorCheck(
                "Schema fields",
                "fail",
                f"{len(missing)} locked field(s) missing from emitter output: {missing}",
                _NEXT_REINSTALL,
            )
        return DoctorCheck("Schema fields", "ok", f"{len(REQUIRED_TOP_LEVEL_FIELDS)} locked top-level fields present")
    except Exception as exc:
        return DoctorCheck("Schema fields", "fail", _fmt_exc(exc), _NEXT_REINSTALL)


def _doctor_custom_signals_check() -> DoctorCheck:
    """Report on the optional user signals.yaml overlay."""
    custom_signals_path = _doctor_custom_path("signals.yaml")
    if not custom_signals_path.exists():
        return DoctorCheck("Custom signals", "ok", f"none ({custom_signals_path} not found)")
    try:
        import yaml as _yaml

        data = _yaml.safe_load(custom_signals_path.read_text(encoding="utf-8"))
        count = 0
        if isinstance(data, dict) and "signals" in data:
            count = len(data["signals"])
        return DoctorCheck("Custom signals", "ok", f"{count} entries in {custom_signals_path}")
    except Exception as exc:
        return DoctorCheck("Custom signals", "fail", _fmt_exc(exc), _custom_file_next(custom_signals_path))


def _doctor_render(console: Any, checks: Sequence[DoctorCheck]) -> bool:
    """Print each check row and the closing summary line.

    Returns True when any check failed, so the caller can set a non-zero
    process exit code for scriptable health gating.
    """
    for check in checks:
        _render_status_row(console, check.status, check.name, check.detail)
    summary = summarize_checks(checks, mode="doctor")
    console.print()
    render_summary(console, summary)
    console.print()
    return summary.status == "fail"


def _doctor_release_check() -> DoctorCheck:
    """Report the installable release without changing the environment."""
    from recon_tool import updater

    current = updater.current_version()
    latest = updater.fetch_latest_version(timeout=3.0)
    if latest is None:
        return DoctorCheck("Release status", "warn", "could not check PyPI; retry with `recon update --check`")
    comparison = updater.compare_versions(current, latest)
    if comparison < 0:
        return DoctorCheck(
            "Release status",
            "warn",
            f"{current} installed; {latest} available on PyPI; run `recon update`",
            "recon update",
        )
    if comparison > 0:
        return DoctorCheck("Release status", "ok", f"{current} is newer than PyPI ({latest}); no downgrade offered")
    return DoctorCheck("Release status", "ok", f"{current} is up to date on PyPI")


async def doctor(*, json_output: bool = False) -> None:
    """Run diagnostic checks.

    The check order is load-bearing: ``tests/test_doctor.py`` drives the
    httpx mock with a positional side-effect list, so identity probes must
    run before the certificate-transparency probes (crt.sh, then CertSpotter).

    Exit code is 0 when every check passes or only optional checks (including
    release status) report warnings, and 1 when any core check fails, so a CI or
    monitoring job can gate on ``recon doctor`` instead of always reading
    success. ``json_output`` renders the same check list as one JSON document
    on stdout, with the same exit code and no human header.
    """
    console = get_console()
    if not json_output:
        _doctor_print_header(console)

    checks = await collect_doctor_checks()
    if json_output:
        summary = summarize_checks(checks, mode="doctor")
        emit_doctor_json(checks, summary, mode="doctor")
        if summary.exit_code:
            raise typer.Exit(code=summary.exit_code)
        return

    if _doctor_render(console, checks):
        raise typer.Exit(code=EXIT_ERROR)


async def collect_doctor_checks() -> list[DoctorCheck]:
    """Run every default-mode check and return the rows, in display order."""
    checks: list[DoctorCheck] = []
    checks.append(_doctor_path_launcher_check())
    checks.append(await asyncio.to_thread(_doctor_release_check))
    checks.extend(await _doctor_identity_checks())
    checks.append(_doctor_dns_check())
    checks.append(_doctor_resolver_probe())
    checks.extend(await _doctor_ct_checks())
    checks.append(_doctor_mcp_check())
    checks.append(_doctor_fingerprint_db_check())
    config_directory = config_directory_check()
    if config_directory is not None:
        checks.append(config_directory)
    checks.append(_doctor_custom_fingerprints_check())
    checks.append(_doctor_signal_db_check())
    checks.append(_doctor_schema_fields_check())
    checks.append(_doctor_custom_signals_check())
    return checks
