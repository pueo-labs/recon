# Stability Policy

As of v1.0, recon commits to the public surfaces listed below. **Stable**
surfaces will not break between patch or minor releases; breaking them
requires a major version bump and a deprecation window. v2.0 promotes
the Bayesian fusion surfaces (`--fusion`, `--explain-dag`,
`posterior_observations`, `slug_confidences`, MCP `get_posteriors` and
`explain_dag`) from their pre-v2.0 experimental status into the stable
set. The disposition table that anchors the promotion lives in
[`roadmap-history.md`](roadmap-history.md#v200--maturity).

For the JSON output contract in full field-by-field detail, see
[`schema.md`](schema.md). For the release process, see
[`release-process.md`](release-process.md).

---

## Stable surfaces

### CLI commands

| Command | Stability | Notes |
|---|---|---|
| `recon <domain>` / `recon lookup <domain>` | Stable | Default panel layout (section order, field names). |
| `recon batch <file>` | Stable | One domain per line (comments with `#`), `--json` / `--md` / `--csv`. |
| `recon doctor` | Stable | Check labels and exit codes. `--fix`, `--mcp`, and `--client` sub-flags. Rows use one status vocabulary: `ok`, `warn`, `fail`, `info`. `--json` (default mode and `--client`, additive) emits the doctor report object in [`schema.md`](schema.md#doctor-report-recon-doctor---json) with the human view's exit code. |
| `recon mcp` | Stable | stdio transport only. |
| `recon delta <domain>` | Stable | Auto-cache diff (v0.10.2). Diff panel + `--json`. |
| `recon cache show [domain]` | Stable | Payload-free result and CT cache metadata; overview mode opens the first 100 completed JSON files per layer and reports exact totals, while `--all` explicitly inspects every completed JSON file. `--exact` selects literal-host keys. Missing, expired, inspection-failure, and temporary-residue states remain distinct. |
| `recon cache clear [domain \| --all]` | Stable | Clears both CT subdomain cache and TenantInfo result cache (v1.0.2+); confirmed clear-all also removes interrupted-write artifacts. `--exact` selects a literal-host key. |
| `recon fingerprints list` | Stable | v1.1+. Per-category summary by default; `--category`, `--type`, `--all`, `--json`. Explicit empty filters are validation errors. |
| `recon fingerprints search <query>` | Stable | v1.1+. Search slug / name / category / detection pattern. |
| `recon fingerprints show <slug>` | Stable | v1.1+. Full entry definition, including synthetic-slug provenance. |
| `recon fingerprints check [path]` | Stable | v1.1+. Runtime schema, duplicate-slug, and specificity (v1.2+) checks. |
| `recon fingerprints new <slug>` | Stable | v1.2+. Scaffolding wizard: slug / schema / specificity gates then emits YAML. |
| `recon fingerprints test <slug>` | Stable | v1.2+. Validates, apex-normalizes, and deduplicates a bounded local UTF-8 corpus before live lookup, or uses the fictional format example. JSON rows retain `matched` and `detail` and add the tri-state `status`; human output separates lookup errors from clean misses. A valid invocation retains exit 0 even when lookups fail, so automation must inspect `status`. |
| `recon signals list` / `search` / `show` | Stable | v1.1+. Ranked search rows carry explicit category and confidence fields; explicit empty category filters are validation errors. |
| `recon review <domain>` | Stable (v2.18+) | One fresh, cache-bypassed NamespaceReviewBundle. Direct probes remain off; `--no-ct` is the only collection-lane switch. `--output` writes the separate caller-owned JSON contract and requires `--force` to replace a file. |
| `recon capsule capture <domain>` | Stable (v2.13+) | Writes the separate caller-owned capsule contract. Existing files require explicit `--force`; collection follows the ordinary public-source boundary. |
| `recon capsule replay <file>` | Stable (v2.13+) | Verifies and replays locally with no network requests. `--as-of` changes only the evaluation context. |
| `recon capsule compare <before> <after>` | Stable (v2.13+) | Classifies observation, collection-regime, time-evaluation, and interpretation change; `--json` follows the capsule schema. |

### CLI flags (on `recon <domain>`)

| Flag | Stability | Notes |
|---|---|---|
| `--json` | Stable | JSON output contract in [`schema.md`](schema.md). |
| `--md` | Stable; **default selection changed in 2.16** | Markdown H2 section structure is stable; prose is not. As of 2.16 the report is the default briefing (ADR-0017): it leads with the vendor roles, cuts insights and related domains with an `--md --full` note, honors `--confidence-mode`, and titles the report on the queried domain (the display name is carried below, labelled unverified). `--md --full` restores every entry. |
| `--full` / `-f` | Stable | Expanded evidence + all domains + posture; retains the default Services summary. With `--plain` or `--md`, selects the complete structured record / uncut report. |
| `--plain` | Stable; **default output changed in 2.15** | Renders the default panel's rows as linear `key: value` text, including the panel's own list cuts: `related_domains:` and `insights:` carry the panel's selection with a sibling `related_domains_note:` / `insights_note:` naming the remainder. Through 2.14.x it always emitted the complete structured record; that output is unchanged and now behind `--plain --full`. Key names are the stable schema names either way, so an existing `grep tenant_id:` still matches, and `provider:` is emitted on every record including a role split. Each note's remainder counts against `--plain --full`, the output the note itself names, so shown plus withheld equals that list; the panel's own footer counts against the panel's `--full`, which drops restatement lines the record keeps, so the two remainders can differ for one record. Migration: add `--full` if you parse a field outside the panel or need an uncut list. [ADR-0016](adr/0016-plain-emits-the-panel-record.md). |
| `--verbose` / `-v` | Stable | Expanded evidence, confidence and detection detail, plus one stderr row per source-health unit when that collection just ran. The rows use the same collection units and the same matched, no match, and unavailable states as the source-health line. Both classify the resolver results. A result reused from cache keeps the expanded panel and does not invent those unit states. |
| `--explain` | Stable | Panel, source status, and flat evidence explanations; `--json --explain` additionally emits the structured, lineage-qualified `explanation_dag`. |
| `--services` / `-s` | Stable | Retained for compatibility; Services are shown by default. |
| `--domains` / `-d` | Stable | Shows all tenant and related domains in the panel. On `--plain` and `--md`, which render the briefing, use `--full` for the complete list rather than `--domains`. |
| `--sources` | Stable | Per-source resolution status table. |
| `--posture` / `-p`, `--exposure`, `--gaps` | Stable | Posture observation modes. |
| `--profile NAME` | Stable | Built-in profiles: fintech, healthcare, saas-b2b, high-value-target, public-sector, higher-ed. Custom profiles additive. |
| `--confidence-mode {hedged,strict}`, `--strict` | Stable | v0.11. Default `hedged`; `--strict` is a shortcut for `--confidence-mode strict`. `strict` drops hedging qualifiers (`observed`, `likely`, `indicators`) only on a dense-evidence record (High confidence with at least three sources); a thin-evidence record keeps its hedges under `strict` by design, so the same insight can read differently across two records and identically when neither is dense. |
| `--compare <file>` | Stable | Diff against previous JSON export. |
| `--chain`, `--depth <1-3>` | Stable | Recursive related-domain resolution. |
| `--no-cache`, `--cache-ttl <sec>` | Stable | Lookup-result cache control. `--no-cache` bypasses both the read and the write. A result whose collection recorded a collector failure is never reused. The independent CT cache still applies. |
| `--timeout <sec>` / `-t` | Stable | Per-domain pipeline timeout (default 120s). Chains have a total budget of depth times timeout; each lookup is capped by the remaining budget. |
| `--fusion` / `--no-fusion` | Stable (v2.0+) | Advanced Bayesian diagnostic control. v2 preserves the historical implicit enabled default. Pass `--no-fusion` for deterministic output or `--fusion` to pin the diagnostic on. A v2.12 interactive transition notice was withdrawn: the omitted-choice flip is deferred optional debt, not a scheduled default change. |
| `--explain-dag` | Stable (v2.0+) | v1.9.0. Render Bayesian evidence DAG. |

### CLI flags (on `recon batch <file>`)

| Flag | Stability | Notes |
|---|---|---|
| `--summary` | Stable (v2.1+) | Aggregate-only cohort output. Contract 2.1 remains the default. |
| `--summary-schema {2.1,2.2}` | Stable | Exact cohort-contract selector. Version 2.2 is an additive opt-in with corrected missingness and raw-evidence-bound DMARC rates. The nondefault 2.2 value requires `--summary`. |

The cohort schema identifiers are exact contract selectors, not package SemVer
ranges. Changing the default away from 2.1 or removing either accepted value is
a breaking stable-surface change and requires a deprecation window plus a
package-major release.

### CLI exit codes

| Code | Meaning | Stability |
|---|---|---|
| 0 | Success | Stable |
| 1 | General error (fallback) | Stable |
| 2 | Input validation error (bad domain format, missing file) | Stable |
| 3 | No data found | Stable |
| 4 | Internal / network error | Stable |

For single-domain commands, code 3 is reserved for a completed collection with
`error_type="no_data"`. Aggregate timeout and all-source pipeline failure use
code 4. Human diagnostics use stderr and never prefix successful JSON,
Markdown, or plain stdout. Verbose source rows distinguish `match`, `no match`,
and `error` without relying on color alone.

### MCP tools

All 23 MCP tools are **stable**: names, existing parameter names, existing
parameter types, and existing return fields will not be removed or change type
or meaning between patch or minor releases. New optional parameters and new
additive return fields may be added. The Bayesian-fusion tools
(`get_posteriors`, `explain_dag`) ship pre-v2.0 under experimental
labels and graduate to stable in v2.0 per the disposition table in
[`roadmap-history.md`](roadmap-history.md#v200--maturity).

| Tool | Parameters |
|---|---|
| `lookup_tenant` | `domain`, `format` ("text"\|"json"\|"markdown", default "text"), `explain` (bool, default false) |
| `build_review_bundle` | `domain`, `no_ct` (bool, default false), `timeout_seconds` (float, default 120.0) |
| `analyze_posture` | `domain`, `explain` (bool, default false), `profile` (str, optional) |
| `chain_lookup` | `domain`, `depth` (1-3, default 1), `result_limit` (int, default 0) |
| `discover_fingerprint_candidates` | `domain`, `skip_ct` (bool, default False), `keep_intra_org` (bool, default False), `min_count` (int, default 1) |
| `reload_data` | (none) |
| `assess_exposure` | `domain` |
| `find_hardening_gaps` | `domain` |
| `compare_postures` | `domain_a`, `domain_b` |
| `get_fingerprints` | `category` (str, optional), `limit` (int, optional), `offset` (int, default 0; used with `limit`) |
| `get_signals` | `category` (optional), `layer` (1-4, optional) |
| `explain_signal` | `signal_name`, `domain` (optional) |
| `test_hypothesis` | `domain`, `hypothesis` |
| `simulate_hardening` | `domain`, `fixes` (list[str]) |
| `inject_ephemeral_fingerprint` | `name`, `slug`, `category`, `confidence`, `detections` (list[dict]) |
| `list_ephemeral_fingerprints` | (none) |
| `clear_ephemeral_fingerprints` | (none) |
| `reevaluate_domain` | `domain` |
| `cluster_verification_tokens` | `domains` (list[str]), `peer_limit_per_domain` (int, default 0) |
| `get_infrastructure_clusters` | `domain`, `member_limit_per_cluster` (int, default 0) |
| `export_graph` | `domain`, `node_limit` (int, default 0), `edge_limit` (int, default 0) |
| `get_posteriors` | `domain` |
| `explain_dag` | `domain`, `output_format` ("text"\|"dot", default "text") |

All MCP tools are stability-covered, but not all are read-only.

**Stateful tools:**

- `reload_data` re-reads local catalogs and clears the lookup cache.
- `inject_ephemeral_fingerprint` adds a process-scoped ephemeral fingerprint.
- `clear_ephemeral_fingerprints` removes process-scoped ephemeral fingerprints.
- `reevaluate_domain` replaces one cached merged result after applying the
  current process catalog. It does not make a network request.

All other tools are read-only. Read-only domain tools can still make passive
outbound requests on a cache miss. The FastMCP Server Instructions document
those boundaries for agents each session.

### JSON output fields

The full top-level JSON contract is in [`schema.md`](schema.md) and the
machine-readable schema is [`recon-schema.json`](recon-schema.json). Summary of
stability tags:

- **64 top-level properties, 48 required on single-domain success output**,
  covering identity, provider, sources, services, domains, email security, CT
  metadata, sovereignty, and nested `cert_summary` / `bimi_identity` objects.
- **Bayesian fusion fields** (`slug_confidences`,
  `posterior_observations`): pre-v2.0 experimental, stable v2.0+ per
  the schema-lock disposition table in
  [`roadmap-history.md`](roadmap-history.md#v200--maturity).
- **Schema-hardening fields**, all stable (v2.0+):
  - `fusion_enabled` (bool): true when the Bayesian fusion layer ran.
  - `record_type` (output-mode discriminator): `"lookup"` on a
    single-domain success object.
  - `schema_version` (string): `"2.0"`.
  - `error_kind` (enum: `validation`, `lookup`, `timeout`): on the batch
    error record.

- **`dns_name_status`** (conditional, additive): present only as `"nxdomain"`
  when the resolver returned NXDOMAIN for the queried name; absent otherwise.
  See [`schema.md`](schema.md).
- **`display_name_verified`** (additive, optional): always `false`; recon
  never verifies the provider-reported display name.
- **`reserved_name`** (conditional, additive): present only as `true` when
  the queried name is a reserved special-use name. See [`schema.md`](schema.md).

The v2.0 schema-hardening pass also reshaped two surfaces before the lock:
`slug_confidences` is now an object map, and `wildcard_sibling_clusters`
entries are now `{names: [...]}` objects.

Any `--json` consumer that reads only stable fields will work across
patch and minor releases without modification.

Observation capsules use the separate
[`observation-capsule-schema.json`](observation-capsule-schema.json) contract.
Capsule schema version `1.0`, replay records, and classified delta records are
stable as of v2.13. Additive optional fields may land in a later minor release.
Removing or renaming existing fields, changing their types or meanings, or
changing capsule digest canonicalization requires a new capsule schema version
and a compatibility path. This guarantee does not make a digest a signature or
the internal normalized snapshot part of the stable lookup JSON.

The `recon doctor --json` report is a separate additive surface, documented in
[`schema.md`](schema.md#doctor-report-recon-doctor---json). Its
`schema_version` integer, the four status words, the summary counts, and
`summary.exit_code` are stable. Row names, detail, and next-step text are
diagnostics and may be reworded. Adding a check row or an optional field is
additive.

NamespaceReviewBundle artifacts use the separate
[`review-bundle-schema.json`](review-bundle-schema.json) contract. Its
`schema_version` is independent of the stable lookup and capsule schemas.
ReviewBundle-owned objects are closed; additive owned fields require a new
ReviewBundle schema version. The embedded lookup retains the stable v2
contract and its additive policy.

### Config / data files

`~/.recon/` below is shorthand for recon's **resolved** config, cache, and
state directories, not a literal path. Resolution order: `RECON_CONFIG_DIR`
when it is an absolute path and contains no unexpanded `${...}` placeholder,
else an existing legacy `~/.recon/`, else the XDG bases
(`$XDG_CONFIG_HOME/recon`, `$XDG_CACHE_HOME/recon`, `$XDG_STATE_HOME/recon`;
defaults `~/.config/recon`, `~/.cache/recon`, `~/.local/state/recon`). A fresh
install gets the XDG paths; the legacy branch exists so an existing `~/.recon/`
is never stranded. `recon doctor` prints the resolved paths, and the rule is
implemented in [`paths.py`](../src/recon_tool/paths.py). The stability
guarantee is on each file's schema, not on the directory it resolves to.

| Surface | Stable guarantee |
|---|---|
| `data/fingerprints/*.yaml` schema | Stable. Fields: name, slug, category, confidence, detections, match_mode, weight, m365, provider_group, display_group. v1.1 split the monolith into per-category files; file boundaries are a repo-organization detail, not part of the schema contract. |
| `~/.recon/fingerprints.yaml` schema | Same. Custom entries are **additive only**; they cannot override built-ins. A `~/.recon/fingerprints/` directory is also accepted (v1.1+). |
| `data/signals.yaml` schema | Stable. Fields: name, category, confidence, description, requires, metadata, contradicts, requires_signals, expected_counterparts, positive_when_absent. |
| `~/.recon/signals.yaml` schema | Same. Additive only. |
| `data/motifs.yaml` and custom `motifs.yaml` marker schema | `match_mode: dns_suffix` validates hostname grammar and matches DNS-label suffixes. Built-ins select this mode. `substring` and omitted mode preserve legacy custom fragments; unknown modes or invalid suffixes reject the motif. Matching is ordered and custom motifs remain additive only. |
| `data/profiles/*.yaml` schema | Stable. Fields: name, description, category_boost, signal_boost, focus_categories, exclude_signals, prepend_note, expected_categories, expected_motifs. |
| `~/.recon/profiles/*.yaml` schema | Same. Additive only. |
| `~/.recon/cache/*.json` (TenantInfo cache) | Stable. Within the current cache version, entries lacking later additive fields remain readable and current writes include current fields. An explicit cache-version mismatch, wrong-shaped, corrupt, oversized, or numerically invalid file degrades to a clean miss. |
| `~/.recon/ct-cache/*.json` (per-domain CT cache) | Stable. Older entries without certificate-summary or infrastructure-cluster extensions remain readable; current writes preserve those extensions. Wrong-shaped, corrupt, oversized, or numerically invalid files degrade to a clean miss. |
| `RECON_CONFIG_DIR` environment variable | Stable for an absolute path. A relative value or an unexpanded `${...}` placeholder is ignored, with one stderr warning, and resolution continues with the legacy directory or XDG. `recon doctor` and `recon doctor --mcp` add a warn row naming the placeholder token. |
| `RECON_DNS_VIEW`, `RECON_DNS_SERVERS`, `RECON_DNS_TLS_NAME`, `RECON_DNS_TRANSPORT` environment variables | Stable. MCP: unset or `caller-safe` binds the encrypted caller-safe view (saved servers, else a recognized host public service, else Cloudflare DNS-over-HTTPS); `none` disables DNS-dependent tools; `operator` uses host DNS for operator-authorized callers. CLI: only `RECON_DNS_VIEW=caller-safe` opts in to the same view; unset, empty, or `operator` keeps host DNS. Other values refuse collection with exit code 2. Invalid settings refuse collection (CLI exit code 2) and never fall back to host DNS. See [mcp.md](mcp.md#dns-view-isolation). |
| `RECON_NO_ANIMATION` environment variable | Stable. Any non-empty value other than `0`, `false` or `no` turns off the animated source ladder; the static source-health line on stderr remains. Presentation only: it never changes stdout, JSON, or exit codes. |
| `RECON_MCP_LOG_REQUESTS` environment variable | Stable. MCP: unset or unrecognized values suppress routine request-level logging (runtime level WARNING). Set to `1`, `true`, `yes`, or `on` for verbose request logging including full URLs. Warning and exception diagnostics may contain domain inputs. |
| `recon_tool/data/observation-capsule-schema.json` | Byte-identical packaged copy of the documented capsule schema. Stable by its own `capsule_schema_version`, separate from lookup schema version `2.0`. |

---

## Surfaces promoted from experimental to stable in v2.0

The following surfaces shipped pre-v2.0 under an experimental label
and graduate to stable in v2.0 per the schema-lock disposition table
in [`roadmap-history.md`](roadmap-history.md#v200--maturity). Each one's pre-v2.0
shape is preserved unchanged; only the EXPERIMENTAL qualifier in
docstrings and schema descriptions is removed.

| Surface | Introduced | Stable as of |
|---|---|---|
| `--fusion` CLI flag | v0.11 | v2.0 |
| `--explain-dag` CLI flag | v1.9.0 | v2.0 |
| `slug_confidences` field | v0.11 | v2.0 |
| `posterior_observations` field | v1.9.0 | v2.0 |
| MCP `get_posteriors` tool | v1.9.0 | v2.0 |
| MCP `explain_dag` tool | v1.9.0 | v2.0 |
| `chain_motifs` field | v1.7.0 | v2.0 |
| `wildcard_sibling_clusters` field (in `cert_summary`) | v1.7.0 | v2.0 |
| `deployment_bursts` field (in `cert_summary`) | v1.7.0 | v2.0 |
| `infrastructure_clusters` field | v1.8.0 | v2.0 |
| `ecosystem_hyperedges` field (batch wrapper) | v1.8.0 | v2.0 |
| `evidence_conflicts` field | v1.7.0 | v2.0 |

---

## What "stable" means

A stable surface will not break between patch releases (`x.y.z` → `x.y.z+1`)
or between minor releases (`x.y` → `x.y+1`). Breaking changes to stable
surfaces require a major version bump (`x.y` → `(x+1).0`) and a minimum
one-release deprecation window with a warning emitted before removal.

**Additions are not breaking changes.** New optional CLI flags, new
optional JSON fields, new MCP tools, new fingerprints or signals can all
land in minor releases without breaking existing consumers.

**Default value changes to existing fields** ARE breaking changes if a
consumer was relying on the default.

That rule also applies to stable CLI defaults. ADR-0013 therefore preserves the
v2 implicit fusion behavior. A v2.12 interactive transition notice was later
withdrawn; the omitted-choice flip remains deferred optional compatibility
debt rather than a scheduled v3 requirement. The explicit `--fusion` and
`--no-fusion` behaviors do not change.

---

## What is NOT in the stability contract

- **Which rows the human views select**: the default panel, `--plain`, `--md`,
  and the MCP text surface render a curated briefing, and what that briefing
  includes or withholds (the role rows, the high-signal related-domain
  selection, the insight cap, the withheld-count notes) may change in a minor
  release. The flags, their exit codes, and the stable schema key names those
  surfaces print do not change without this contract's process. `--json` is the
  surface automation should parse, and `--plain --full` / `--md --full` restore
  the complete record. ADR-0016 changed the `--plain` default selection in 2.15
  and ADR-0017 changed the `--md` and MCP text selection in 2.16 under this
  rule; 2.15 is the named precedent, reasoned rather than a claim that the
  surface was uncovered. See
  [ADR-0017](adr/0017-one-briefing-in-every-shape.md).
- **Rich panel visual formatting**: colors, whitespace, row ordering
  within Services categories, box-drawing details. The section structure
  is stable; pixel-level rendering is not.
- **Evidence-role wording on the human views**: the default panel, `--plain`,
  and `--md` compact the record-role qualifier out of service and provider
  labels and omit matches with no established role; `--explain`, `--verbose`,
  and `--full` keep them. One exception: `--plain`'s `provider:` key on a
  role-split record keeps its role, because there it repeats the vendor `mail:`
  has already named and the role is what makes the repetition a second fact.
  The JSON `provider` field and the MCP payloads are
  unaffected and stay the machine contract. See
  [ADR-0012](adr/0012-default-view-evidence-role-visibility.md).
- **Insight wording**: individual insight text may be refined. The
  insight *types* and their *trigger conditions* are stable (see
  `signals.yaml`); the exact phrasing is not.
- **Which specific fingerprints fire for a given domain**: the `slugs`
  field is stable as a mechanism; its contents depend on the fingerprint
  database version and may change as new fingerprints are added or
  existing ones are refined.
- **Debug / verbose internals**: `--explain` output is stable at the
  section level; per-line detail may evolve.
- **Cache file internal layouts beyond the documented TenantInfo/CT
  shapes**: future fields may be added; consumers should ignore unknown
  fields (forward-compatible reads).

---

## Python support policy

The stable Python surface is the range advertised in `pyproject.toml` and
tested in CI.

- **Currently tested:** Python 3.11, 3.12, 3.13, 3.14, and 3.15.
- **Adding a Python version:** update CI, classifiers, and this section in the
  same change.
- **Dropping a Python version:** treat as a compatibility change, document it
  in `CHANGELOG.md`, and warn one minor release ahead when practical.

---

## SemVer commitment

From 1.0 onward, recon follows [Semantic Versioning](https://semver.org)
strictly:

- **MAJOR** (1.x → 2.0): breaking change to any stable surface.
- **MINOR** (1.x → 1.(x+1)): backward-compatible additions. Breaking
  changes to *experimental* surfaces are allowed.
- **PATCH** (1.x.y → 1.x.(y+1)): bug fixes only. No new features, no
  schema changes.

Pre-1.0 releases (0.9.x through 0.11.x) did not honor this contract
strictly; some minor releases included breaking changes within a minor.
From 1.0 onward the contract is enforced.
