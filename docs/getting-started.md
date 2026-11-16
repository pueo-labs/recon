# Getting Started

This guide covers install, update, uninstall, and the first commands to run.
The short product overview is in [README.md](../README.md).

## Requirements

- Windows, macOS, or Linux. The one-command installer below sets up `uv` and
  Python when needed; a fresh install does not require administrator access.
- For a manual Python install: Python 3.11 through 3.15. The latest Python 3.15 patch is recommended; every
  version in that tested range retains the same supported behavior and output
  contracts. Later Python versions are not yet part of the compatibility claim.
- The recon runtime needs no API keys, credentials, paid accounts, or external
  services owned by recon. Optional GitHub Release verification uses an
  authenticated GitHub CLI session or `GH_TOKEN` with public read access.

## Install or Update

**macOS or Linux:**

```bash
curl -fsSL https://raw.githubusercontent.com/pueo-labs/recon/main/scripts/install.sh | bash
```

**Windows (PowerShell):**

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://raw.githubusercontent.com/pueo-labs/recon/main/scripts/install.ps1 | iex"
```

The helper installs the exact recon version recorded in the script. It preserves
the sole `uv` or `pipx` owner of an existing install and refuses ambiguous or
unmanaged ownership with recovery guidance. On a fresh machine it downloads
the pinned official `uv` installer, then lets `uv` install Python 3.15 and recon
in an isolated tool environment. It updates PATH and verifies `recon --version`
before reporting success. For pipx it selects an available stable Python from
3.15 through 3.11 and prints its version and executable. An existing pipx
installation keeps its own supported Python; an unsupported or unreadable
environment stops with `pipx reinstall` guidance.

You can rerun the current installer to install its release or use `recon update`
to get the latest published version. GitHub Release and PyPI carry the same
release artifacts; the package manager downloads the package from PyPI.

To inspect a fixed script first, download a
[release tag](https://github.com/pueo-labs/recon/releases/latest), review its
helper, then run `bash scripts/install.sh` or
`powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1` locally.

If you already have Python 3.11 through 3.15, install directly:

```bash
pip install recon-tool
# Or use an isolated tool environment:
uv tool install --python 3.15 recon-tool
pipx install --python python3.15 recon-tool
```

For pipx, name an installed stable Python 3.11 through 3.15; on Windows with
the Python launcher, use `--python 3.15`. Passing `--python` together with
`pipx install --force` does not change an existing environment's interpreter.
Use `pipx reinstall recon-tool --python <supported-python>` to change it, then
rerun the helper to install its exact release.

If `pip` reports an externally managed environment, use the platform installer
or the [virtual environment instructions](#install-in-a-virtual-environment).

Open a new terminal after install, then run an offline verification of the
installed command:

```bash
recon --version
```

To check the latest release and online connectivity to recon's public data sources, run:

```bash
recon doctor
```

The release check queries PyPI with a short timeout. It reports an available
update, an up-to-date install, or a local version newer than the published
release. A failed release check is a warning; it never installs anything and
does not fail otherwise healthy diagnostics. Ordinary lookups and `--version`
do not check for updates.

## Verify a Published Release

Security-sensitive consumers can verify the exact GitHub Release asset set,
completed SBOM, tag-bound bundle, PyPI attestations, cross-channel SHA-256
parity, and both wheel entry points before optionally installing the verified
local wheel. Releases produced by the current workflow include the SBOM in the
signed subject set; the exact v2.6.3 historical exception covers its wheel and
sdist while still requiring SBOM structure validation. The complete
macOS/Linux and Windows PowerShell paths are in the
[consumer verification quick path](supply-chain.md#consumer-verification-quick-path).

## Update

```bash
recon update
recon update --check
```

`recon update` detects whether the package was installed with `uv`, `pipx`,
`pip`, or an editable checkout and runs the matching upgrade command when it can.
`recon update --check` reports separately when the installed version matches
PyPI, is behind PyPI, or is newer than the latest published release. It never
offers to replace a newer local or source build with an older PyPI release.

User-level uv and pipx launchers work from home and unrelated directories,
including symlink shims. The updater still requires a matching installation
receipt and local manager destination; project-local or relative manager
launchers require manual maintenance.

`recon update` downloads a pip release before it replaces a pip install, so a
download failure leaves the current files in place. On macOS and Linux it then
runs the package manager in the foreground. On Windows the running launcher
locks `recon.exe`, so the command copies an isolated worker outside the
package, prints a log path, and exits. The worker waits until that launcher
and any other `recon.exe` have exited, retries a transient file lock, and
checks that `recon-tool` imports before it reports success.

Wait for `Update completed` in the terminal or the Windows log, then run
`recon --version`. If `recon` cannot start, run the recovery command at the
end of that output. After a pip download, that command reuses the downloaded
files when the staging directory is still present, and otherwise installs the
same release from PyPI with the original interpreter, for example
`python -m pip install -U recon-tool`. A `site-packages` directory whose name
starts with `~econ-tool` is an unfinished pip uninstall and can be removed
after `recon --version` works.

Windows pip installs older than 2.19.5 keep the package manager inside the
locked launcher. Upgrade those copies with `python -m pip install -U recon-tool`.
Direct package-manager commands below also run outside the recon launcher.

`recon doctor` reports the running version, Python executable, package location,
and detected installation method. It advises when Python is outside the tested
stable range without treating that advisory as a failed connectivity check.
It also warns when the first `recon` launcher
on PATH reports a different version, which commonly means a stale global install
is taking precedence over the intended environment. Its release-status check
reports whether this version is current on PyPI and suggests `recon update`
when a newer release is available. A version-check outage is a warning and
never triggers an installation.

Direct package-manager commands also work:

```bash
uv tool install --upgrade recon-tool
pipx upgrade recon-tool
pip install -U recon-tool
```

## Uninstall

Use the tool that installed recon:

```bash
uv tool uninstall recon-tool
pipx uninstall recon-tool
pip uninstall recon-tool
```

## Install with pipx

`pipx` is a good default for command-line tools because it creates an isolated
environment and puts the script on PATH.

```bash
pipx install recon-tool
recon --version
```

## Install in a Virtual Environment

```bash
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

or:

```bash
source .venv/bin/activate
```

Then install and verify:

```bash
pip install -U recon-tool
recon --version
```

## Install from a Git Checkout

```bash
git clone https://github.com/pueo-labs/recon.git
cd recon
pip install -e .
```

For development work in this repository, prefer:

```bash
uv sync
uv run python scripts/check.py
```

After an editable or environment install, either the `recon` console script or
the package module entry works:

```bash
recon --version
python -m recon_tool --version
```

## First Lookup

Lookups make DNS queries which recursive and authoritative DNS infrastructure
may observe. The only default request to a target-owned HTTP endpoint is the
standards-defined MTA-STS policy fetch at
`https://mta-sts.<domain>/.well-known/mta-sts.txt`. Google CSE and BIMI direct
probes run only when `--direct-probes` is explicitly enabled.

```bash
recon example.com
```

recon ships no offline demo mode: this is a real lookup command, but an ordinary
lookup may reuse a recent result from the default 24-hour cache. Pass
`--no-cache` to bypass the lookup-result cache for both reading and writing;
CT enrichment can still reuse its separate cache. A reused result says so in
one muted line, such as `Cached result from 3 hours ago. Use
--no-cache to collect again.`, on the panel, `--plain`, and `--md` output; the
lookup JSON contract is unchanged. Reserved names such as `example.com` return a
real panel of stray public residue from unrelated test configurations,
including a meaningless display name, at High confidence. It shows you the
shape of the output, not a result about any organization, and the result says
so: every human surface prints `Reserved name: results are public residue, not
an organization.` under the title, and `--json` adds `"reserved_name": true`.
The display name itself is provider-reported, so the panel, `--plain`, `--md`
and MCP text mark it `(unverified)` and `--json` carries
`"display_name_verified": false`. Point recon at a domain you want to review to
see a real footprint.

Cache reuse follows three rules:

- **Incomplete collections are not reused.** When a lookup records a collector
  failure (an unavailable identity endpoint, a DNS channel that timed out, or
  every CT provider failing with no CT cache fallback), recon still answers
  with the partial result, but the next ordinary lookup collects again instead
  of serving it. A routine CT fallback, where crt.sh failed but CertSpotter or
  the CT cache supplied the data, is not a collector failure. Sparse results
  with no failure, including low confidence and an empty service list, are
  reused normally.
- **`--no-cache` bypasses both the read and the write.** It always collects,
  and it neither reads nor replaces the stored entry. An ordinary lookup
  replaces the entry when it is expired or not reusable.
- **`recon cache show <domain>` reports the same decision a lookup makes:**
  `reusable`, `expired; next lookup refreshes`, or `not reusable; previous
  collection had unavailable sources`. It shows metadata only, never the
  cached payload. `recon cache clear <domain>` removes the entry if you want to
  discard it outright.

`--no-ct` and `--direct-probes` lookups never read or write the shared result
cache, because their scope differs from a default lookup.

### What you see while recon collects

On an interactive terminal, a lookup that collects (not a cache hit) draws a
short ladder on stderr, one row per source family: DNS records, Microsoft
tenant discovery, Microsoft user realm, Google identity, MTA-STS policy and
certificate transparency. Each row spins while it runs and settles to
a check mark and `matched`, a dash mark and `no match`, or a cross and
`unavailable (reason)` (`ok`, `-` and `x` in ASCII mode). When collection ends the ladder collapses into one source-health
line above the panel:

```text
6 sources: 3 matched, 2 no match, 1 unavailable (CT: crt.sh, certspotter rate limited)
```

The ladder never animates under `--no-color`, `NO_COLOR`, `TERM=dumb`, `CI`,
`--debug`, or when stderr is not a terminal; set `RECON_NO_ANIMATION=1` to
turn it off anywhere else. In each of those cases the source-health line alone
is printed. `--json`, `--md` and `--explain-dag` print neither, and stdout is
never touched: `recon example.com 2>/dev/null` gives the same output with or
without the ladder.

Warnings from collectors are gathered during collection and summarized once
on stderr after the ladder, for example
`2 hosts could not be resolved (login.microsoftonline.com, autodiscover.example.com). Run recon doctor.`
A name that does not resolve is worded `could not resolve`; a host recon
refuses because it resolves to a private address is worded
`skipped: resolves to a private address`. `--debug` keeps the detailed log
lines instead of the summary.

Use explicit synthetic identities under reserved namespaces in examples and
docs. Public validation work with real apexes stays in gitignored local
workspaces.

The panel's two dot rows answer different questions, so they can disagree
without either being wrong. `Confidence` is a deterministic merged tier over
source count, same-claim corroboration, and source degradation; a degraded
source lowers it. It is not a raw source count and not a probability.
`Model support` is threshold-relative: where a claim's hand-set uncertainty band
sits against the model's decision threshold. A single-source record can carry a
full model display, and the panel says so on the row when the two sit two steps
apart. Definitions: [glossary.md](glossary.md); detail:
[how-it-works.md](how-it-works.md).

`--confidence-mode strict` (or `--strict`) drops hedging qualifiers like
`observed` and `indicators` from insight lines, but only on a dense-evidence
record: High confidence with at least three sources. A thin-evidence record
keeps its hedges under `strict` by design, because dropping the hedge on sparse
evidence would overclaim. So the same insight can read one way on a dense record
and another on a thin one, and identically when neither is dense.

## Encrypted DNS

By default the `recon` command uses your system resolver, so results match
what your machine sees and nothing changes on networks that block encrypted
DNS. To send CLI lookups over encrypted DNS instead, opt in once in your shell
profile:

```bash
export RECON_DNS_VIEW=caller-safe
```

The CLI then uses the same encrypted view as the MCP server: saved
`RECON_DNS_SERVERS` and `RECON_DNS_TLS_NAME` settings if present, otherwise
Cloudflare or Google when your system already uses one of them, otherwise
Cloudflare DNS-over-HTTPS (`cloudflare-dns.com`). Your local, office or VPN
resolver is not consulted, so split-horizon private answers stay out of the
results, and the chosen resolver operator sees the names you look up. See
[DNS view isolation](mcp.md#dns-view-isolation) for the Google and Quad9
settings and the DNS-over-TLS option.

Only the exact value `caller-safe` opts the CLI in; any other value, or none,
keeps the system resolver. With the opt-in set, invalid `RECON_DNS_*` settings
make lookups exit with code 2 before any collection instead of silently using
the system resolver. A failure never falls back to the system resolver. If the
network blocks encrypted DNS, every source fails and recon says so; save a
resolver the network permits, or unset `RECON_DNS_VIEW`. Structured output
records the view in `resolution_vantage` (`caller-safe` or `operator`). A result
cached under one view is never reused under the other. The result cache holds
one entry per domain; collecting under a different view replaces that entry,
so switching back collects again.

## Input Normalization

Pass a public-suffix domain (for example `example.com`). A bare hostname without
a dot is rejected with `Invalid domain format` rather than treated as an unknown
CLI command.

recon accepts common paste shapes:

```bash
recon https://www.example.com/path
recon example.com.
recon mail.example.com
```

By default, recon reduces a URL or sub-host to the registrable apex where tenant,
MX, SPF, DMARC, and CT evidence usually live. Pass `--exact` only when you want
DNS facts for the literal host:

```bash
recon mail.example.com --exact
recon www.example.com --exact
```

## Output Modes

```bash
recon example.com
recon example.com --full
recon example.com --explain
recon example.com --plain
recon example.com --json
recon example.com --md
```

Services are already present in the compact default panel, grouped by lane
(Email, Identity, Cloud, Security, AI, Data & Analytics, Collaboration,
Business Apps). `--md` uses those same lanes. The default `--md` report is still
a briefing: it caps insights and related domains and omits unattributed
matches. `--json` and `--md --full` are the downstream connection map: every
lane including empty ones, every vendor row with its evidence role, catalog
summaries, and related hosts classified by first label (`auth.`, `shop.`,
`workday.`). `--verbose` keeps the panel summary and adds certificate and
evidence detail plus one stderr row per source-health unit when that
collection just ran. Those rows use the source-health line's collection
units and states, and both classify the resolver results. A result
reused from cache keeps the expanded panel and does not invent those
unit states. `--full` adds the verbose
detail, all known domains, and posture observations. `--services` remains
accepted for compatibility; new workflows do not need it.

Use `--explain` when a claim matters. It shows the evidence chain behind the
result. Built-in generated insights retain their exact emitting rule and
evidence-or-observation-scope association. Signal-adjacent, conflict, lexical,
confidence, and legacy posture associations can still be reconstructed. Flat
explanations label that distinction. In explained JSON,
`exact_provenance_complete` and `lineage_disconnected_terminals` answer the
exact-lineage question; schema-version-1 `provenance_complete` retains its
broader graph-reachability meaning.

Use `--plain` for screen readers, grep, and other linear-text workflows. It
renders the default panel's rows as indented `key: value` lines with no color
or box-drawing: the same claims the panel shows, in the same order, under the
stable schema names, and with the same cuts. Grep for `provider:` and
`tenant_id:`, not `Provider`.

Insight sentences, uncertainty hedges, next steps and omission notes remain
complete in both plain modes. All values have terminal and bidirectional
formatting controls removed. Other display values keep the shared 200-character
bound; a shortened value ends with ` [truncated; see --json]`. Use `--json` for
the structured record rather than parsing a shortened display value.

A record whose mail vendor and identity vendor differ leads with `mail:` and
`identity:` (the role split from
[ADR-0015](adr/0015-role-split-vendor-claims-in-the-default-view.md)) and still
emits `provider:` after them, carrying its usual MX-delivery-path summary, so
one grep works on every record. On a split it prints that role, `provider:
Google Workspace (MX delivery path)`, because the vendor word is one `mail:`
just said and the role is the reason it came back. Long lists are cut the way
the panel cuts them: `related_domains:` carries the high-signal selection and
`related_domains_note:` states how many more exist, and `insights:` is capped
with an `insights_note:` beside it. Each note names `--plain --full` and counts
against it, so what you heard plus what the note states is what that command
prints. The panel's own footer points at the panel's `--full`, which stays
curated, so the same record can carry two different remainders: each is exact
about the output it names.

Add `--full` for the complete structured record, including Bayesian internals
such as `posterior_observations` and `interval_low`:

```bash
recon example.com --plain          # the panel, linearised
recon example.com --plain --full   # every field the record carries
```

Before 2.15, plain `--plain` always emitted the full record. If you parse it
for a field outside the panel, add `--full`;
[ADR-0016](adr/0016-plain-emits-the-panel-record.md) records the change, and
`--json` remains the surface recommended for automation. Either mode tracks the
panel's default/detailed split ([ADR-0012](adr/0012-default-view-evidence-role-visibility.md)),
so evidence-role qualifiers are compacted unless you add `--explain`.
This is the linear view for a standard single-domain lookup. Chain, compare,
exposure, and gaps reports use their own formats; batch and delta have
mode-specific output.

Color follows one order, highest first: `--color` or `--no-color`, then a
non-empty `NO_COLOR`, then `TERM=dumb`, then `FORCE_COLOR` (any value except
empty or `0`), then terminal detection. `--no-color` removes every escape
sequence, bold included, on stdout and stderr.

`--ascii` replaces the Unicode glyphs with ASCII: `[##-]` for confidence dots,
`ok`, `-` and `x` for source marks, `H`, `M` and `L` for salience, and `-` for
the divider. It turns on automatically under `TERM=dumb` and on a terminal whose
encoding cannot show the glyphs, so `TERM=dumb recon example.com` prints pure
ASCII.

`--color`, `--no-color` and `--ascii` are global options, but they work in
either position: `recon example.com --no-color` and `recon --no-color
example.com` are the same, as is any subcommand form such as `recon review
example.com --no-color`. When both color flags appear, the last one given wins. The other global
options must come first: use `recon --debug example.com`, and run
`recon --version` on its own. A misplaced one is rejected with exit code 2 and
a message that shows the working form.

An option's value remains data even when it spells a global flag. For example,
`--compare --ascii` selects the snapshot file named `--ascii`; it does not turn
on ASCII output.

## Exit Codes

Every command follows one exit-code contract, so a script can branch on the
outcome without parsing output. The same table is in
[schema.md](schema.md) for machine consumers.

| Code | Meaning |
|---|---|
| 0 | Success: the command completed and produced output |
| 1 | General handled error, for example a missing optional dependency or a failed `doctor` check |
| 2 | Validation: bad input rejected before any work, for example a malformed domain or mutually exclusive flags |
| 3 | No data: the target resolved but nothing was available to report |
| 4 | Internal: a caught network or pipeline failure, or the last-resort crash handler |

## Inspect Local Cache State

`cache show` reads metadata only. The default overview enumerates cache
filenames for exact totals but opens at most the lexicographically first 100
result files and 100 CT files. Use `--all` only when a complete inspection is
worth the additional local work:

```bash
recon cache show
recon cache show --all
```

recon resolves its config, cache, and state directories in one order:
an absolute `RECON_CONFIG_DIR` with no unexpanded `${...}` placeholder, else an
existing legacy `~/.recon/`, else the XDG base
directories (`$XDG_CONFIG_HOME/recon`, `$XDG_CACHE_HOME/recon`,
`$XDG_STATE_HOME/recon`). On Windows with none of those set, that resolves to
`%USERPROFILE%\.config\recon`, `%USERPROFILE%\.cache\recon`, and
`%USERPROFILE%\.local\state\recon`. `recon doctor` prints the resolved paths.

An interrupted atomic write can leave a cache-writer-shaped temporary file.
The overview counts that residue without reading or printing its payload,
exits 4, and points to the confirmed `recon cache clear --all` workflow. That
clear-all operation removes both completed entries and recognized temporary
write artifacts, while unrelated `*.tmp` files are left alone.

## Explore the Local Catalogs

The list, search, and show commands below are local and do not query a domain or
another network source:

```bash
recon fingerprints list
recon fingerprints search email
recon fingerprints show <slug>
recon signals list
recon signals search email
recon signals show "<signal name>"
```

Fingerprint slugs are named public-record indicators. A slug may have more than
one catalog record, so `fingerprints show` renders every matching record and
its detection rules, relationship hints, tiers, and verification dates. Signals
are derived reportable-observation definitions built from candidate fingerprint
slugs and metadata conditions. Human fingerprint search is a ten-slug preview;
add `--json` to retrieve every matching catalog record. Category filters use
word-prefix matching for one token and literal phrase matching for multiword
queries in both the CLI and MCP server. Human catalog detail output strips
terminal controls from locally extended text and visibly marks values truncated
after 1,024 characters.

`recon fingerprints test` is different: it resolves every domain in the chosen
local corpus through the ordinary live lookup pipeline. DNS infrastructure may
observe those queries, MTA-STS remains the one default target-owned HTTP
request, and the usual public CT and identity-source boundaries apply. The
entire UTF-8 input is validated before the first lookup: at most 1 MiB total,
1 KiB per logical line, and 500 non-comment domain rows. Valid URL and sub-host
forms normalize to their apex and duplicate normalized domains resolve once.
Any malformed row rejects the file before collection begins. Human output
counts matches, clean non-matches, and lookup errors separately. JSON rows
retain `matched` and `detail` and add `status` with `matched`, `not_matched`, or
`error`, so failed collection is not negative evidence.
Valid corpus invocations retain exit 0 even when one or every lookup reports an
error. Automation must inspect each JSON row's `status` instead of treating the
process exit status as collection success.

At terminal widths below 70 columns, command help automatically switches to a
complete linear layout so long option names remain visible. Ranked signal
search results keep relevance order and carry an explicit category and
confidence instead of implying category grouping.

If a lookup times out or every online source fails, run `recon doctor` to
check source connectivity, then retry the lookup. Each row reads `ok`, `warn`,
`fail`, or `info`, and a failure summary ends with the next step to take.
`recon doctor --json` returns the same rows for scripts, with the same exit
code. If doctor prints `Resolver answers names that should not exist`, the
system resolver is synthesizing answers, and related-domain results from that
network are unreliable; see
[limitations](limitations.md#resolvers-that-answer-names-that-should-not-exist).

## Namespace Review Bundles

NamespaceReviewBundle v1 is the separate, caller-owned contract for a
deterministic evidence handoff about one namespace. It composes exactly one
fresh baseline that bypasses the lookup-result cache with evidence-linked
review candidates and one role-neutral human rendering. Direct probes are fixed
off; CT is the only optional collection lane. CT may use its documented cache,
and the artifact records that outcome separately. Temporal facts do not become
a universal fresh or stale verdict.

```bash
recon review example.com
recon review example.com --json
recon review example.com --output example-review.json
recon review example.com --no-ct
```

The default view is deterministic Markdown. `--json` emits the validated v1
artifact, while `--output` writes that JSON artifact locally and refuses to
replace an existing file unless `--force` is supplied. Through MCP, call
`build_review_bundle(domain, no_ct=false, timeout_seconds=120)` for the same
structured artifact. The `domain_report` prompt uses that tool once and asks the
client to render the standing section order without adding other analysis
tools. Full contract, failure, privacy, and rendering semantics are in
[review-bundles.md](review-bundles.md).

## Batch and Delta

```bash
recon batch domains.txt --json
recon batch domains.txt --json --include-ecosystem --summary --summary-schema 2.2
recon batch domains.txt --ndjson
cat domains.txt | recon batch - --json
recon delta example.com
```

The longer batch command emits one portfolio evidence bundle for the exact
operator-supplied set. It preserves ordered success and error records, adds
observable ecosystem hyperedges, and attaches the aggregate-only cohort summary
under `cohort_summary`. Shared infrastructure and configuration are public
observations, not proof of ownership, control, a corporate relationship, or
relative security. Plain batch JSON and the streaming NDJSON path keep their
existing shapes.

Batch files contain one domain per line. Blank lines and lines beginning with
`#` are ignored. Valid URL, sub-host, and apex spellings that normalize to the
same registrable apex are resolved once, with the first occurrence preserved.
Malformed values deduplicate only when their trimmed, lowercased spellings
match, so distinct malformed inputs retain separate diagnostics. The reader
accepts at most 10,000 non-comment records before deduplication, 1 KiB of UTF-8
per logical line, and 10 MiB of UTF-8 in total. The full behavior is documented
in [operational-contract.md](operational-contract.md).

## Observation Capsules

Capture one caller-owned artifact, replay it without network access, or compare
two artifacts while keeping observation, collection, time, and interpretation
changes separate:

```bash
recon capsule capture example.com --output example-before.json
recon capsule replay example-before.json
recon capsule compare example-before.json example-after.json --json
```

Capture uses the ordinary public collection boundary. Capsule files may retain
public verification tokens, tenant identifiers, and related domains, so protect
them and review them before sharing. recon does not upload, schedule, or retain
them. Full semantics and the separate JSON Schema are in
[observation-capsules.md](observation-capsules.md).

## MCP Setup

```bash
recon mcp install --client=claude-desktop
recon doctor --mcp
recon mcp doctor
recon doctor --client=claude-desktop
```

Run the checks in that order. They validate the static server registry, the
live local stdio tools and JSON resources, and the saved configuration for the
same client. The live doctor does not inspect client configuration. Use
[mcp.md](mcp.md) for client-specific config, tool lists, approval guidance, and
troubleshooting.

## Shell Completion

```bash
recon --install-completion
recon --show-completion
```

Restart the shell after installing completion.

## Installer and PATH Troubleshooting

If installation appears to wait, check its ownership progress message. Another
uv tool operation can hold the tool-directory lock. The helper waits up to
15 seconds per ownership probe and retries a recognized lock timeout once.
If it still cannot inspect ownership, wait for that operation to finish and
rerun the helper. It does not switch managers while ownership is unknown.

If the version after a manual install is unexpected, first list the launchers:

```bash
type -a recon
```

In PowerShell, use `Get-Command recon -All`. Check the first entry against the
intended manager's executable directory (`uv tool dir --bin` or
`pipx environment --value PIPX_BIN_DIR`). Run `recon doctor` from the intended
environment to compare that PATH launcher, including a symlink shim, with the
running package. Activate the intended environment or remove the obsolete copy
with its owning manager, then restart the shell.
The [launcher and installer contract](launcher-installation.md) describes the
ownership and workspace safeguards.

## Windows PATH Notes

If `recon` is not found after `pip install`, the script likely went into your
user Scripts directory, which may not be on PATH. Prefer the installer, `uv`, or
`pipx`. If you must use bare `pip`, add the matching user Scripts directory to
PATH and restart the terminal. As a temporary fallback while PATH is fixed:

```bash
python -m recon_tool --version
```

If that version differs from `recon --version`, run `recon doctor` from the
intended environment. Its `PATH recon launcher` row identifies the launcher
taking precedence so you can activate the intended environment or reinstall
that launcher with its package manager.

## Next Reads

- [how-it-works.md](how-it-works.md)
- [limitations.md](limitations.md)
- [schema.md](schema.md)
- [automation-examples.md](automation-examples.md)
- [mcp.md](mcp.md)
