# recon Agent Plugins candidate

Schema-pinned portable packaging candidate for recon-tool 2.27.1. It
contains the complete MCP surface and the two existing recon skills in the
fixed [Agent Plugins v1.0.0](https://agent-plugins.org/specification)
locations.

This directory has passed offline validation against the vendored canonical
Agent Plugins v1.0.0 schemas. Version 1.0.0 is Published.
Offline validation is not an unqualified compatibility or conformance claim;
promotion remains blocked on the frozen Visual Studio Code, Cursor, and Kiro
[representative-client evaluation](https://github.com/pueo-labs/recon/blob/v2.27.1/docs/agent-portability-evaluation-declaration.md).

Prerequisites:

- Python 3.11 or newer;
- `recon-tool` installed so the client can resolve the `recon` executable;
- client-controlled approval for any networked lookup.

## Load the directory

Obtain this directory from a recon source checkout; it is not installed by
the PyPI wheel or shipped as a separate release asset. Choose the directory
containing `plugin.json` in a client that supports Agent Plugins v1.0.0.
You may copy the complete directory elsewhere before loading it. Do not
choose the repository root, `skills/`, or a client-native scaffold.

Clients discover the two immediate `skills/*/SKILL.md` files and the root
`mcp.json`. Both Agent Skills and MCP stdio support are needed for the full
experience. A skills-only client can use the CLI fallback if it exposes a
shell. Installation UI and approvals remain client-specific.

The client must find the installed `recon` executable through its executable
search path. GUI applications may not inherit a terminal's PATH. Configure
the client's launch environment or use the documented native MCP installer
as a separate fallback; do not put an absolute path or shell command into
this portable `command` field. The launch is `recon` with the separate
argument `mcp`, from the plugin root. No source checkout is needed to launch.

## State and skill prerequisites

`mcp.json` sets `RECON_CONFIG_DIR` to `${PLUGIN_DATA}/recon`. The client
supplies and expands `PLUGIN_DATA`; recon's configuration, caches, and
limiter state stay there across plugin updates. The package directory need
not be writable. Cursor and VS Code, checked 2026-10-25, leave
`${PLUGIN_DATA}` unexpanded. recon then ignores that value, warns once,
and uses the ordinary config location instead of creating a literal
`${PLUGIN_DATA}` directory in the working directory. This is separate
from ordinary CLI/native-client config: existing custom fingerprints and
profiles are not automatically imported.

Already-connected MCP tools do not require a shell or a CLI version probe.
Tool prefixes and skill invocation UI are client-defined. The triage skill
can review supplied observations and the installed catalog, but editing
built-in fingerprints and running repository tests requires a separate,
explicitly selected recon source checkout. Versioned documentation links
are references, not bundled scripts or permission to clone a repository.

## Verify locally

First check the client's discovered skills and server status. MCP discovery,
catalog resources, and `get_fingerprints` are local checks; no target lookup
is needed to verify loading. `recon mcp doctor` checks the local runtime's
handshake, but does not establish that a particular client loaded this
package successfully. No paid or live-model client validation is implied.

Validate from a recon source checkout:

```bash
uv run python scripts/generate_agent_plugin.py --check
uv run python scripts/check_agent_plugin.py
```

Agent Plugins controls packaging only. It does not change MCP wire behavior,
permissions, stable recon JSON, observation capsules, or the separately
deferred Open Knowledge Format v0.2 projection. Native client scaffolds under
`agents/` remain supported and unchanged during evaluation.
