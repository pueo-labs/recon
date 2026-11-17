# recon

<!-- mcp-name: io.github.pueo-labs/recon -->

[![CI](https://github.com/pueo-labs/recon/actions/workflows/ci.yml/badge.svg)](https://github.com/pueo-labs/recon/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/recon-tool.svg?cacheSeconds=300)](https://pypi.org/project/recon-tool/)
[![Python](https://img.shields.io/pypi/pyversions/recon-tool.svg?cacheSeconds=300)](https://pypi.org/project/recon-tool/)
[![License](https://img.shields.io/pypi/l/recon-tool.svg?cacheSeconds=300)](https://github.com/pueo-labs/recon/blob/main/LICENSE)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/pueo-labs/recon/badge)](https://scorecard.dev/viewer/?uri=github.com/pueo-labs/recon)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/15800/badge)](https://www.bestpractices.dev/projects/15800)

Point recon at a domain to see its **public technology and identity
footprint**: email providers and controls, identity indicators, SaaS services,
and cloud infrastructure. No credentials, API keys, or active scanning.
Use the CLI for a quick lookup, versioned JSON for automation, or the local
MCP server from an agent.

recon reports evidence-backed observations, not a complete inventory or a
security verdict. A domain does not establish an organization's boundaries.

## See the Output

![Synthetic recon output in a modern Linux terminal](https://raw.githubusercontent.com/pueo-labs/recon/main/docs/assets/terminal-demo.svg)

**Synthetic illustration, generated, not captured.** The real formatter renders
a deterministic, no-network fixture for Example Industries Ltd. No real
organization is depicted, and no live lookup of reserved `example.com`
reproduces this fixture.

<!-- terminal-demo-transcript:start -->
<details>
<summary>Accessible text transcript</summary>

```text
demo@recon:~$ recon example.com    # synthetic fixture, not a captured run
6 sources: 5 matched, 1 no match
Example Industries Ltd (unverified)
example.com
Reserved name: results are public residue, not an organization.
──────────────────────────────────────────────────────────────────────────────
  Provider      Microsoft 365 + Proofpoint gateway
  Tenant        a1b2c3d4-e5f6-7890-abcd-ef1234567890 • NA
  Tenant domain example-industries.onmicrosoft.example.com
  Auth          Federated
  Confidence    ●●● High (3 sources)


Services
  Email            Microsoft 365, Proofpoint, DMARC reject, DKIM,
                   SPF strict, MTA-STS enforce
  Identity         Okta
  Cloud            Cloudflare (CDN/edge), AWS Route 53 (DNS)
  Security         Wiz Security
  Data & Analytics Snowflake, Datadog
  Collaboration    Slack, Atlassian (Jira/Confluence), GitHub, Zoom
                   Evidence roles: --explain


High-signal related domains
  login.example.com, support.example.com, status.example.com

Insights
  Federated identity observed; identity-vendor indicators: Okta
  Email security: observed controls: DMARC reject, DKIM, SPF strict, MTA-STS

```

</details>
<!-- terminal-demo-transcript:end -->

## Quick Start

**macOS / Linux:**

```bash
curl -fsSL https://raw.githubusercontent.com/pueo-labs/recon/main/scripts/install.sh | bash
```

**Windows (PowerShell):**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/pueo-labs/recon/main/scripts/install.ps1 | iex"
```

The installer sets up recon for your user account, including Python when needed.
Open a new terminal afterward. Python 3.15 is the default development and release
runtime; 3.11 through 3.15 remain supported. Already have a supported Python? Use
`pip install recon-tool` in a virtual environment, or `uv tool install --python 3.15 recon-tool` /
`pipx install --python python3.15 recon-tool` on managed distributions like Arch Linux and Omarchy.
For review-before-run instructions, other package managers, updates, and recovery,
see the [installation guide](https://github.com/pueo-labs/recon/blob/main/docs/getting-started.md#install-or-update).

```bash
recon --version      # offline install check
recon doctor         # online connectivity and installation diagnostics
```

Lookups make DNS queries visible to recursive and authoritative infrastructure.
MTA-STS is the only default target-owned HTTP request; Google CSE and BIMI
certificate probes require explicit `--direct-probes`. There is no port
scanning or application crawling. Replace the placeholder to start:

```bash
recon "<domain-you-want-to-review>"
```

If the panel warns that related domains may be artifacts, run `recon doctor`
to check whether your resolver answers names that should not exist.

Ordinary lookups may reuse the 24-hour result cache and say so when they do; a
result whose collection had unavailable sources is never reused. Use
`--no-cache` to bypass the cache for both reading and writing;
certificate-transparency enrichment has a separate cache. See
[first lookup and cache behavior](https://github.com/pueo-labs/recon/blob/main/docs/getting-started.md#first-lookup).

## Common Commands

The bare command stays compact. Request evidence or structured output when needed:

```bash
recon example.com                      # compact panel
recon example.com --explain             # evidence and source status
recon example.com --json                # structured record
recon example.com --plain               # linear text for screen readers and grep
recon review example.com               # fresh, evidence-linked review bundle
recon batch domains.txt --json          # look up a supplied domain list
recon delta example.com                # compare with a cached baseline
recon update                           # update through the original package manager
```

These examples use reserved domains; real lookups will not reproduce the
synthetic illustration above. For multi-domain reviews, recon describes
observed similarities and differences without inferring ownership or a
corporate relationship. See the
[evidence-first review workflow](https://github.com/pueo-labs/recon/blob/main/docs/defender-workflow.md)
and [batch guide](https://github.com/pueo-labs/recon/blob/main/docs/getting-started.md#batch-and-delta).

## Use with an Agent

The PyPI package installs the CLI and MCP runtime. Connect the local server to
Claude Desktop, Claude Code, Cursor, VS Code, Windsurf, or Kiro:

```bash
recon mcp install --client=claude-desktop
recon mcp doctor
```

Restart the client and begin with manual tool approvals. Ask for one domain's
email and identity indicators, or a service comparison across supplied domains.
Missing evidence means "not observed", not "not used"; collection failures
remain explicit. Local execution is the default, and the project does not
operate a hosted service.

See [MCP setup and supported clients](https://github.com/pueo-labs/recon/blob/main/docs/mcp.md)
and [skills, plugins, and their validation status](https://github.com/pueo-labs/recon/blob/main/agents/README.md).

### Omarchy Desktop Shell Integration

recon includes a thin, keyboard-first desktop shell plugin for [Omarchy](https://omarchy.org)
located in [`integrations/omarchy/`](https://github.com/pueo-labs/recon/blob/main/integrations/omarchy/):

- **Keyboard-driven workflow**: focus domain input automatically, press `Enter` to run
  bounded inspection, and press `Ctrl+D` to toggle baseline delta comparison.
- **Direct process invocation**: passes structured arguments directly (`["recon", domain, "--json"]`)
  without shell interpolation.
- **Safe clipboard handling**: pasting text never triggers an automatic network request.
- **Zero background daemons**: runs unprivileged inside Omarchy's Quickshell environment.

See [`integrations/omarchy/README.md`](https://github.com/pueo-labs/recon/blob/main/integrations/omarchy/README.md) for installation and shortcuts.

## Documentation

| Need | Guide |
|---|---|
| Install, update, uninstall, or troubleshoot | [Getting started](https://github.com/pueo-labs/recon/blob/main/docs/getting-started.md) |
| Find a command or flag | [CLI reference](https://github.com/pueo-labs/recon/blob/main/docs/cli-surface.md) |
| Build automation or hand off evidence | [JSON schema](https://github.com/pueo-labs/recon/blob/main/docs/schema.md), [review bundles](https://github.com/pueo-labs/recon/blob/main/docs/review-bundles.md) |
| Understand results and their limits | [How it works](https://github.com/pueo-labs/recon/blob/main/docs/how-it-works.md), [limitations](https://github.com/pueo-labs/recon/blob/main/docs/limitations.md), [reporting observations](https://github.com/pueo-labs/recon/blob/main/docs/reporting-observations.md) |
| Linux and Omarchy environment setup | [Linux / Omarchy guide](https://github.com/pueo-labs/recon/blob/main/docs/omarchy-and-linux.md) |
| Check plans and shipped changes | [Roadmap](https://github.com/pueo-labs/recon/blob/main/ROADMAP.md), [changelog](https://github.com/pueo-labs/recon/blob/main/CHANGELOG.md) |
| Find architecture, security, research, or release procedures | [Full documentation index](https://github.com/pueo-labs/recon/blob/main/docs/README.md) |

## Contributing and Support

Catalog corrections and documented vendor patterns are especially useful.
Start with [CONTRIBUTING.md](https://github.com/pueo-labs/recon/blob/main/CONTRIBUTING.md)
for setup, verification, and contribution requirements; coding agents should
also read [AGENTS.md](https://github.com/pueo-labs/recon/blob/main/AGENTS.md).
For repeatable catalog work, start with the harness-neutral
[maintenance skill and offline example](https://github.com/pueo-labs/recon/blob/main/agents/maintainer/skills/recon-catalog-maintenance/SKILL.md).

Use [issues](https://github.com/pueo-labs/recon/issues) for bugs and feature
requests. Keep public examples reserved and synthetic; never post evaluated
company domains, tenant IDs, or per-domain results. See the
[private reporting paths](https://github.com/pueo-labs/recon/blob/main/docs/data-handling-policy.md#private-non-security-reports)
and [security policy](https://github.com/pueo-labs/recon/blob/main/SECURITY.md).
Intended for [defensive use](https://github.com/pueo-labs/recon/blob/main/docs/legal.md).

## License

[Apache 2.0](https://github.com/pueo-labs/recon/blob/main/LICENSE).
