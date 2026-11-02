# Roadmap

The canonical product plan is [docs/roadmap.md](docs/roadmap.md). Shipped work
belongs in [CHANGELOG.md](CHANGELOG.md), and detailed historical planning belongs
in [docs/roadmap-history.md](docs/roadmap-history.md). This file is the short
operator and contributor view: current state, next work, boundaries, and gates.

## Status

recon **v2.27.0** is the current production baseline. The CLI, versioned JSON,
local stdio MCP server, bounded public-metadata collectors, fail-closed claim
audit, MCP dual-SDK matrix, and verified release path are complete. Local
execution is the default, and the project does not operate a hosted service.
Optional cloud materials remain a draft and are not a validated production
deployment.

The resolver and detection engine are feature-complete. The stable lookup,
briefing, full connection map, batch, capsule, and NamespaceReviewBundle
surfaces share one evidence and claim discipline. New product work must solve a
named operator handoff that the existing surfaces cannot solve. The shipped
v2.19 assurance batch includes compatible fixes, documented catalog indicators,
operator-display corrections and a PR-first release workflow. It adds no
collector and does not expand the inference model.

The evidence-semantic audit is complete: 29 families are complete. 0 material
runtime families carry incomplete lineage. Fail-closed inventory spans 91 score
or quantitative fields. Production MCP stays on `mcp>=2.0.0,<3`, with exact
1.28.1 rollback, 2.0.0 production-floor, and 2.3.0 locked-baseline rows blocking
in CI.

Release verification binds each published artifact to its exact tag, workflow,
signer, and commit digest and requires SBOM provenance. One
digest-bound v2.6.3 historical exception preserves that release's
distribution-only bundle while
still requiring SBOM structure validation. Later releases fail if provenance is
absent.

## Resume here

State at 2026-11-02: v2.27.0 is the published build. Tag `v2.27.0` is
`9c213f79`. PyPI, the GitHub Release, and the MCP Registry entry
`io.github.blisspixel/recon` report that version. No issues are open. The
packaging batch and tracker #324 are closed. Shipped behavior is in the
changelog. A documentation commit after the tag does not move the tag or
the package. The 2026-11-02 toolchain refresh updates Hatchling to 1.33.0,
the development lock, and the pinned setup-uv, setup-python, and
codeql-action releases. It does not cut a release. Dependabot proposed
those updates. The maintainer re-lands them, because a bot author fails
the commit-metadata hygiene gate and those pull requests cannot merge.

The 2026-10-29 repository transfer prepares `pueo-labs/recon` and the
`io.github.pueo-labs/recon` registry identity without a version bump or release.
The existing v2.27.0 package and old registry entry are unchanged. Complete the
[external transfer checklist](docs/release-process.md#repository-transfer-checklist)
before a separately authorized release and registry migration.

What is next, and why:

1. The monthly fingerprint-freshness loop. The resolver and detection engine
   are feature-complete, so the durable work is a fresh look at public
   patterns, not another product surface. Each round makes a new temporary
   list of questions. That list is unique to the round, it is not a reused
   roster of organizations, and it is not committed. Research public vendor
   documents and standards for a new or changed pattern on the records recon
   already reads. The maintainer skills `recon-catalog-maintenance`,
   `recon-corpus-plan`, `recon-catalog-round`, and
   `recon-fingerprint-triage` are the procedure. Refine a skill when a round
   shows that the instructions are wrong or incomplete. Promote a rule only
   with a current public or disclosure-safe basis, a real `verified` date,
   synthetic positive and lookalike fixtures, and provenance tests. GitHub
   receives that pattern. It does not receive a statement that a named
   organization uses a service, and it does not receive an apex, a tenant
   identifier, an opaque token, or a per-domain row. Those stay in the
   gitignored private roots when an operator supplies them. The 2026-10-28
   pass dated the Anthropic and Mistral apex TXT rules from current vendor
   pages and left six other AI rules undated, because those cited
   pages do not print the exact grammar. A later pass the same day checked
   eight undated CRM and marketing rules and left them undated for the same
   reason. The older Dynamics authenticate-domains article now redirects, and
   a search-index copy of it is not a current basis. A later pass the same
   day dated the Emma account-validation TXT and the Eloqua tracking-domain
   CNAME from pages that print the grammar, and left six other CRM rules
   undated. The 2026-10-29 pass dated the Klaviyo branded-sending TXT, the
   Kartra custom-domain CNAME, and the Iterable tracking-domain CNAME from
   pages that print the grammar, and left five other marketing rules
   undated. The cited Intercom article now serves a different article, so
   that URL is not a current basis for either Intercom rule. The 2026-10-30
   pass dated the Account Engagement tracker-domain CNAME and the Salesforce
   `_spf.salesforce.com` include from pages that print the grammar, and left
   six other rules undated. The 2026-11-02 pass dated the Yandex Webmaster
   rights-verification TXT from the page that prints the grammar, and left
   seven other rules undated. That work does not cut a release.
   The next round uses a new question list and the rules that are still due.
   The closed 5,199-row drift round remains a measurement contract. It does
   not promote rules. Start at [catalog maintenance](docs/catalog-maintenance.md).

2. Two upstream dependency blockers, and only when upstream ships the fix.
   PyYAML 6.0.3 has no cp315 wheel, so Python 3.15 builds it from source.
   Stable pip still vendors an urllib3 without the proxy TLS and chunk-size
   fixes, so the mitigation recorded on closed issue 187 stays. Do not add a
   local pin or drop the audit to make the refresh look finished. See
   [the October review](docs/maintenance-review-2026-10-08.md).

3. Black-box defects before any new surface. None are open. A new collector,
   score, inference path, or set-level review bundle needs a named operator
   handoff that the existing surfaces cannot solve. Output truthfulness
   outranks another feature release.

Not next, and why:

- Another package release. v2.27.0 is the current build. This note does not
  change behavior, so it does not cut a version.
- A new DNS record-type collector. IANA's parameter table, last updated
  2026-10-16, added temporary `DELEG` and `DELEGPARAM` registrations.
  `HTTPS`, `SVCB`, `DSYNC`, `RESINFO`, `HHIT`, and `BRID` were already
  assigned. `RESINFO` describes the recursive resolver, not the queried
  name. `DELEG` is a parent-zone delegation draft. `HHIT` and `BRID` are
  remote-identification records. `HTTPS` and `SVCB` are service-binding
  records, often published by a CDN that NS or CNAME rules already name.
  Querying a new type is a new collector. The 2026-10 documentation pass
  did not find a miss the current records cannot answer.
- Antigravity CLI (`agy`). `--client=gemini` writes the Gemini CLI file
  `~/.gemini/settings.json`. `agy` is a separate client and reads global
  `~/.gemini/config/mcp_config.json` and workspace `.agents/mcp_config.json`.
  There is no open issue for that client, and adding it would not correct the
  installer that shipped.
- Agent Plugins promotion, a project-operated service, and an overall
  security rating. The gates are in
  [What Is Deliberately Not Next](#what-is-deliberately-not-next).

When picking work back up, sync `main` and run
`uv run python scripts/check.py` before starting anything else. The Unreleased
catalog note from the 2026-10-28 freshness pass does not by itself cut a
release. If Unreleased has other user-visible behavior changes, batch them
through the [release process](docs/release-process.md). Otherwise continue the
freshness loop on rules that are still due, or wait for the upstream blockers
above.

## Current release and next steps

v2.17.12 shipped the stable engine's bounded audience-composition tranche for
admins, defenders, consultants, and analysts. It did not expand collection,
infer ownership, or add a security rating.

v2.18.0 shipped **NamespaceReviewBundle v1**. It is a caller-owned,
deterministic evidence handoff for one namespace. Its baseline bypasses the
lookup-result cache, keeps direct probes off, records CT as an explicit choice,
retains evidence and candidate identifiers, distinguishes completed and failed
workflows, and renders one role-neutral human report. Its digest detects content
modification but is not a signature or proof of collector identity. A future
operator-supplied set extension remains deferred until real use demonstrates a
handoff the single-namespace contract cannot solve.

v2.18.1 fixed the first stability-soak defect: degraded CNAME classification no
longer erases names supplied by successful certificate transparency. v2.18.2
updated dependency tooling and workflow pins without changing product behavior.
v2.18.3 tightened diagnostic and renderer truthfulness. v2.18.4 withdrew the
interactive fusion-transition notice; the implicit default remains enabled and
silent.

v2.19 shipped the duplicate-evidence correction, documented catalog additions,
and PR-first release workflow. Installation and update maintenance focuses on the first
five minutes: one-command Windows and macOS/Linux installers, working upgrades
from version-pinned installs, release status in `recon doctor`, and clear pip
instructions. Normal lookup output stays quiet. Acceptance requires fresh
install and upgrade tests, PATH and failure handling, and release parity.

v2.20 shipped reliable installation and update recovery and replaced the
Omarchy bar widget with an on-demand native panel; v2.20.1 kept home-managed uv
and pipx updates available from any working directory.

v2.21 closed the October black-box issue sweep without adding a collector,
score or inference path. Collection truth: total collection failure exits 4,
an apex NXDOMAIN is stated rather than narrated as a quiet domain, a collection
with unavailable sources is never reused from the result cache, and the
generated MCP launcher starts from the home directory or a filesystem root
while still refusing a working-directory shadow package. Toolchain: Python 3.15
is the default, CI tests 3.11 through 3.15 plus a free-threaded probe, and
actions and Node are current. Interface: one theme role table on the 16 ANSI
colors with an ASCII fallback, a source ladder on stderr, narrow-terminal
layout that never breaks identifiers, the same qualifiers on every surface, one
doctor vocabulary with JSON output, and theme-following Omarchy status colors.

The [Linux interface qualification](docs/interface-qualification-2026-10-20.md)
exercises the source ladder and native panel on a running desktop. It identifies
and corrects idle ladder redraws, palette singleton shadowing, and input
selection that did not follow the accent; publication is tracked in the changelog.
Typecheck and release jobs run Node 26 with `check-latest`, so they pick up
each new 26.x release, including the 2026-10-21 security release (26.12.1) and
the LTS line from 2026-10-28, without a pin change. Python 3.15.1 remains the
pinned local and container interpreter. Python 3.15.2, released 2026-10-25,
is the current GA security release and is not yet that pin. 3.11 through
3.15 remain the tested compatibility range. Drop PyYAML source builds once a
cp315 wheel ships.

v2.22 isolated lower-trust MCP collection from split-horizon DNS and finished
the build-toolchain CA remediation. v2.23 published the harness-neutral catalog
maintenance entry point, bounded maintenance and batch correlation inputs,
replaced suite-wide typing relaxations with exact scopes, and repaired
Bayesian assurance scenarios without changing model parameters. v2.24 closed
the next black-box issue batch (issues 284 through 291): Null MX applicability,
wide boxed reports, MCP DNS capability and chain-depth bounds, evidence
canonicalization, literal `www` hosts, cache policy labels, offline exit codes,
and shared CNAME matching between fresh and cached detection. v2.25 made MCP DNS
collection work without setup by defaulting to encrypted Cloudflare
DNS-over-HTTPS, with saved settings and `RECON_DNS_VIEW=none` as overrides.

`main` is the single integration and release branch. Short-lived implementation
and release-preparation branches merge through required checks and are deleted
after merge. GitHub Release and PyPI must agree before publication is complete. The final
release job verifies human maintainer ownership and original sealed evidence;
GitHub promotion remains an explicit human handoff.

The [executable acceptance loop](docs/roadmap.md#autonomous-improvement-acceptance)
continues to require positive/negative fixtures, provenance, and the full gate.
Distinct-source dependency correction remains a separate question to
characterize before changing model weights.

The ordered work is:

1. Fix compatibility, rendering, diagnostic, or provenance defects found by
   black-box use.
2. Keep the monthly fingerprint-freshness loop current. The closed 5,199-row
   drift round remains a measurement contract, not a source of automatic
   catalog promotion.
3. Run renderer parity review on every release that changes human output.
4. Keep the 29-family claim audit, all three MCP SDK pins, full test gate, release
   provenance, and channel parity blocking.
5. Use concrete bug reports and reproducible operator examples to justify any
   new composition surface.
6. Provide thin, independently removable desktop integrations (such as the
   keyboard-first Omarchy Quickshell plugin in `integrations/omarchy/`) that reuse
   existing structured CLI JSON outputs and domain-validation logic without
   shell interpolation or background daemons. The Omarchy panel defaults to no
   bar slot, with native settings and explicit lookup, baseline, copy and terminal
   actions. Optional automatic watching remains separate follow-up scope.

The v2.19 maintenance releases shipped updater recovery, module isolation,
regex admission, vendor-neutral agent-discovery declarations, supplied-domain
service workflows, and SPF, DKIM, BIMI and TLS-RPT admission corrections.
The default panel remains compact. Cryptographic verification and full SPF
evaluation remain outside the product. Protocol currency does not imply that
every agent harness or portable plugin client has been exercised.

The [October maintenance review](docs/maintenance-review-2026-10-08.md) records
the 2026-10-08 dependency refresh and its synchronized build constraints, plus
SPF record selection, TXT byte fidelity and bounded local MCP inputs. Those
changes shipped through the checked PR and release workflow; see the changelog.
The upstream pip vendored-transport refresh still awaits a stable upstream
release; the audit mitigation stays in force.

For correlation, prioritize the accuracy of the public observation and the
honesty of its explanation: documented vendor patterns, synthetic positive and
lookalike cases, duplicate-evidence checks, and sparse or failed collection.
Keep numerical diagnostics visibly model-relative. Independent calibration is
unestablished; no replacement population study, company interviews, or private
inventory collection is planned or required for maintenance. The cancelled
M365 frame remains closed. The
[canonical assurance priorities](docs/roadmap.md#current-assurance-priorities)
define this practical loop. General robustness envelopes remain conditional
research rather than a promised product feature.

The September assurance pass makes that order concrete: preserve collection
caveats across output formats, correct unsupported catalog claims before
growing coverage, make profile-specific installation diagnostics reproducible,
and exercise the installed wheel outside its source checkout. The
[claim-review ledger](validation/2026-09-05-catalog-claim-review.md) records
retirements and a separate unpromoted research queue. Passing these gates is
bounded implementation evidence, not enterprise certification, calibrated
accuracy, or proof that any named organization should adopt recon.

The portable Agent Plugins candidate remains an offline maintainer track. Its
schema validation and frozen client preflight are useful readiness evidence,
not a compatibility claim or conformance claim. Resume the paired client frame
only under the frozen rules in
[the agent-portability declaration](docs/agent-portability-evaluation-declaration.md).

## Version path (order of operations)

There are no calendar estimates. Patch releases remain available for security,
silent-failure, and contract-preserving fixes.

| Version | State | Boundary |
|---|---|---|
| v2.10 through v2.14 | Shipped | Evidence audit, MCP v2 adoption, the structural fusion decision, caller-held capsules, and catalog-quality measurement |
| v2.15 | Shipped | Default-view claim clarity, accessible `--plain`, and pre-collection validation |
| v2.16 | Shipped | One shared briefing across panel, plain, Markdown, and MCP text, plus renderer parity gates |
| v2.17 | Shipped | Additive downstream connection map while preserving briefing cuts |
| v2.18 | Shipped | NamespaceReviewBundle v1 plus contract-preserving fixes and maintenance |
| v2.19 | Shipped | Catalog and operator assurance, reproducible builds, and reviewed release preparation |
| v2.20 | Shipped | Installation and update recovery, accessible prose, and the native Omarchy panel |
| v2.21 | Shipped; maintenance continues | Collection truth, the Python 3.15 toolchain, and the interface rules from the October issue sweep |
| v3.0, conditional | Not scheduled | Exists only if a genuine claim or observation contract change cannot remain additive; otherwise v2 remains current |

The fusion omitted-choice change is claim-neutral compatibility debt. The
implicit v2 default stays enabled and silent. `--fusion` and `--no-fusion` pin
behavior if an operator wants a fixed choice. A default change may ride a
genuine major boundary if one is required, but it does not justify a major
release by itself.

## Standing loops

| Loop | Cadence | Pass condition |
|---|---|---|
| Fingerprint freshness | Monthly and on a known vendor change or missed detection | Promoted rules have current public or disclosure-safe support, fictional positives, lookalike negatives, scoped wording, and provenance tests |
| Catalog drift | Quarterly or by declared window | Frozen thresholds hold; comparisons across unequal catalog digests are withheld; no promotion comes from the drift frame |
| Black-box renderer review | Per human-surface release | Compact surfaces keep their intended cuts and agree on claim meaning |
| Claim audit | Every material claim change | All discovered claim families remain fail closed with exact or explicitly bounded lineage |
| MCP compatibility | CI and SDK events | Exact 1.28.1, 2.0.0, and 2.3.0 rows remain green |
| Dependency and supply chain | Weekly, on advisory, and per release | CI, CodeQL, Scorecard, secrets scan, dependency audit, SBOM, provenance, and artifact parity remain green |
| Release readiness | Every release | Main, tag, GitHub Release, and PyPI identify one commit and one artifact set |

Catalog detail lives in [docs/catalog-strategy.md](docs/catalog-strategy.md).
The executable [maintenance workflow](docs/catalog-maintenance.md) starts with
a harness-neutral skill and fictional offline example, then separates private
corpus planning, bounded collection, rule triage and monthly reference receipts.
New rounds must bind their
actual exclusions and preserve untouched holdouts; a classified-surface uplift
is not independent precision or permission for automatic promotion.
Quality and publication evidence lives in
[docs/strategic-gap-audit.md](docs/strategic-gap-audit.md). External submission
work must rerun the
[submission freeze checklist](docs/submission-freeze-checklist.md). The
[2026-06-30 local proof](validation/2026-06-30-submission-freeze-local-proof.md)
is the most recent historical public proof memo, not a freeze of the current
package.

## Active tracks

1. **Evidence-semantic integrity:** maintenance at the highest trust rank. Any
   new or stronger claim surface reopens the fail-closed audit.
2. **MCP compatibility:** keep both supported SDK generations and complete
   local resource/tool diagnostics green.
3. **Product quality:** stability soak, operator feedback, renderer parity, and
   reproducible black-box tests. Preserve complete accessibility guidance and
   incomplete-comparison diagnostics across human surfaces. Do not substitute
   feature count for quality.
4. **Catalog quality:** continue bounded freshness and drift work. Do not stamp
   unverifiable dates or promote from evaluation holdouts.
5. **Vendor-role visibility:** the human renderer decision is complete. Any
   change to stable `slugs` remains at the claim-envelope boundary.
6. **Optional operator-hosted access:** lower-priority draft work only. Local CLI
   and stdio MCP remain complete; the project does not operate a service.

## What Is Deliberately Not Next

| Work | Gate that could unblock it |
|---|---|
| New collectors, scores, or inference machinery | Demonstrated operator miss plus the existing evidence and stability gates |
| Set-level NamespaceReviewBundle | Stable single-namespace use plus a named consumer; membership remains caller-supplied |
| Broad catalog growth | Independently reviewed vendor evidence and the precision budget |
| Portable Agent Plugins promotion | Reproducible install, discovery, launch, update, and failure evidence from every frozen representative client |
| OKF knowledge export | Named consumer, v0.2 mapping, lifecycle model, and privacy review |
| More cloud provider infrastructure | Named operator and provider-specific validation |
| Project-operated public multi-tenant service | Separate product, governance, and funding decision |
| Native acceleration | Product-shaped profiling and the ADR-0010 evidence gates |
| Overall security or maturity rating | Out of scope; recon reports bounded public observations |

## Invariants

**Collection boundary:** public metadata only. DNS queries may be observed by
recursive and authoritative infrastructure. MTA-STS is the sole default
target-owned HTTP request. Google CSE and BIMI certificate probes are explicit
opt-in direct probes. No credentials, scanning, exploit checks, or generic
target application crawling.

**Claim discipline:** a domain is a query coordinate, not an organization
identifier. Sparse stays sparse. Source failure is unavailable, never negative.
Parent-platform presence is not child-product use. The public-evidence index is
not an overall security rating.

**Data handling:** no committed real-target corpus. Examples use synthetic or
reserved namespaces. Public validation artifacts are aggregate-only or carry a
disclosure-safe basis.

**Surface stability:** CLI, JSON, MCP, cache, and import changes follow
[docs/stability.md](docs/stability.md). Briefing and full-map surfaces keep their
separate jobs. Portable formats remain additive projections and never silently
replace stable JSON or MCP contracts.

## Where to read more

| Question | Document |
|---|---|
| Canonical plan and detailed gates | [docs/roadmap.md](docs/roadmap.md) |
| Historical planning | [docs/roadmap-history.md](docs/roadmap-history.md) |
| Shipped changes | [CHANGELOG.md](CHANGELOG.md) |
| Evidence and quality proof | [docs/strategic-gap-audit.md](docs/strategic-gap-audit.md) |
| Claim audit | [docs/default-claim-audit.md](docs/default-claim-audit.md) |
| Catalog maintenance | [docs/catalog-strategy.md](docs/catalog-strategy.md) |
| Release process | [docs/release-process.md](docs/release-process.md) |
| Publication freeze | [docs/submission-freeze-checklist.md](docs/submission-freeze-checklist.md) |
