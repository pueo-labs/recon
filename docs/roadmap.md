# Roadmap

This file is the canonical product plan and scope boundary. Shipped work belongs
in [CHANGELOG.md](../CHANGELOG.md). Historical planning lives in
[roadmap-history.md](roadmap-history.md). Release mechanics live in
[release-process.md](release-process.md). Research and publication work is
tracked separately from product work.

> **Status:** v2.27.0 is current. The CLI, versioned JSON, local stdio MCP,
> bounded collectors, evidence and renderer contracts, MCP compatibility matrix,
> and verified release path are established. The resolver and detection engine
> are feature-complete. Recent shipped work belongs in the
> [changelog](../CHANGELOG.md), with earlier plans in
> [roadmap-history.md](roadmap-history.md).
>
> **Current priority: contract-preserving maintenance.** Installation and update
> polish, agent-discovery declarations, supplied-domain service workflows, and
> SPF, DKIM, BIMI and TLS-RPT admission corrections shipped in v2.19 maintenance
> releases. v2.21 closed the October black-box issue sweep: collection truth for
> total failure, NXDOMAIN and degraded cache reuse, the MCP launcher working
> directory guard, the Python 3.15 toolchain, and the interface rules (theme
> roles, ASCII fallback, source ladder, narrow layout, caveat parity, doctor
> JSON). Keep those behaviors under regression tests rather than treating
> completed work as a future tranche. Routine catalog maintenance uses public
> specifications and synthetic evidence; company interviews and private
> inventory confirmation are not release gates.
> The [Linux interface qualification](interface-qualification-2026-10-20.md)
> covers real-terminal motion and live desktop palettes. Preserve its regressions
> for idle redraws, QML singleton resolution and accent-colored input selection.
> Typecheck and release jobs run Node 26 with `check-latest`, tracking each new
> 26.x release, including security releases and the LTS line from 2026-10-28.
> Python 3.15.1 remains the pinned local and container interpreter. Python
> 3.15.2, released 2026-10-25, is the current GA security release and is not
> yet that pin. Older maintained versions are compatibility targets, not the
> development or release default.
> The [October review](maintenance-review-2026-10-08.md) records the dependency
> refresh, synchronized build graph, current bug fixes and local security
> boundaries. The changelog records its release batch. The pip vendored-transport issue
> requires an upstream stable fix; package audit workarounds remain in force.
>
> `main` is the single integration and release branch. Checked implementation
> and release-preparation branches are temporary. Publication is complete only
> when the exact main commit, tag, GitHub Release, and PyPI artifacts agree.
>
> New product surfaces need a demonstrated operator handoff. A v3.0 remains
> conditional on a genuine claim or observation contract break. Optional cloud
> hosting and agent portability remain separate maintainer tracks, without a
> hosted-service or cross-client compatibility claim. The
> [short roadmap](../ROADMAP.md#version-path-order-of-operations) records version
> boundaries and the standing loops below preserve the stable baseline.
>
> **Code-graph orientation:** refresh the ignored
> `.agent/codegraph/manifest.json` after each tracked milestone and read it for
> the exact build commit, trust level, checks, and counts. A current high-trust
> graph with passing integrity checks is required before broad changes. The
> graph is an implementation aid, not a substitute for source and test
> verification.

## Standing loops

With the resolver and detection engine feature-complete, the roadmap is mostly
a set of loops that never finish because the world they observe keeps changing,
plus bounded composition work justified by concrete operator handoffs. The
recent releases (v2.15, v2.16) were output of the playtest loop; the next durable
stream is output of the freshness loop. Agent portability is
a separate maintainer track: its preflight passes, while paired collection is
deferred behind enforceable account hard stops and a reproducible driver for
all three required desktop clients. It does not queue product work. Each loop
names its trigger, cadence, artifact, and stop or pass condition. A loop is
healthy when it runs on its cadence and produces its artifact, not when it
"completes."

| Loop | Trigger | Cadence | Artifact | Stop / pass |
|---|---|---|---|---|
| Fingerprint freshness (the catalog loop) | Monthly, plus a missed-detection report or a known vendor change | Monthly | New/updated YAML fingerprints, regenerated JSON catalog, `verified` dates, aggregate memo | Never complete; a promotion pass stops when a survivor lacks an independent public or disclosure-safe basis, fails its lookalike negative, or would breach the precision budget |
| Catalog drift round | A frozen prior sample re-observed against the current catalog | Quarterly, or per declared window | Aggregate-only drift memo | No frozen-threshold breach; classification withheld across unequal catalog digests; no promotion from a drift frame |
| Black-box playtest / renderer parity | A release that touches a human surface; an external test round | Per release | Round memo, `surface-parity.md` movement, ADRs | The `surface-parity` gate stays green; a presentation-only round means the loop is working |
| Adversarial corpus round | A named defect vector or a new mitigation to gate | On event, then standing | Frozen `.invalid` fixtures, `results.json`, dated memo | The gated vector stays at its committed result (Pattern I at zero of seven); corroborators still support |
| Dependency and supply-chain audit | A PR or push, an advisory, a Dependabot bump | Weekly, plus on event | Green CodeQL, Scorecard, secrets scan, dependency audit; re-authored bot bumps | Floors green; the SAST ratchet advances only on Scorecard evidence, never by backfill |
| Upstream provider-endpoint drift | The passive integration cron | Weekly | A live passive smoke of the identity and CT endpoints | Endpoints still behave; a break is an upstream change to characterize |
| Inference CPT drift gate | An edit to `bayesian_network.yaml` | Per commit | The committed inference baseline plus an explicit `--update` acknowledgement in the diff | No node moves beyond its band without an acknowledged baseline update |
| MCP dual-SDK matrix | An SDK release or a spec change | On event, plus per CI | A dated compatibility matrix, all three pins green | The v1.28.1 rollback, v2.0.0 production floor, and v2.3.0 locked baseline rows stay green |
| Mutation gate | A push or PR to a gated module, plus a weekly sweep | Per change, plus weekly | The mutation score over tested mutants | Genuine survivors killed with per-field pins; the floor is a fraction over tested mutants and is not bumped to pass |
| Doc-versus-runtime consistency | Each release | Per release | Reconciled roadmap, schema, stability, and CHANGELOG; the parity matrix | The drift gates stay green; no document claims behavior the code lacks |
| Release readiness and provenance | Each release | Per release | Local and remote readiness, SBOM, provenance, channel parity | The tag, PyPI artifact, and GitHub Release identify one commit; the SBOM and attestations are present |

### Current assurance priorities

The September 2026 step-back review prioritizes operator trust over feature
count. Its bounded corrections preserve unavailable-source and sparse-result
caveats in linear output, honor explicit explanation requests, avoid stability
claims after graph-construction clipping, verify explicit installation paths,
and test the built wheel outside the checkout. The
[catalog claim review](../validation/2026-09-05-catalog-claim-review.md)
narrows or retires unsupported rules and keeps new coverage proposals separate.
These corrections and the subsequent reproducibility and design-language pass
shipped in v2.19.0. The minor version accounts for
the additive diagnostic flag and documented CNAME support, not a new collection
surface or a new inference model.

The correlation review reinforces a practical standard: best-effort
interpretation of what the public channel exposes. The next work is:

- Verify fingerprint meaning against current vendor documentation and test
  synthetic positives, deceptive lookalikes, and optional or stale declarations.
- Exercise repeated records, shared derivations, conflicting evidence, sparse
  results, and failed collectors with offline fixtures. A repeated view adds no
  independent corroboration; a failed source supplies no negative fact.
- Check panel, plain, Markdown, and MCP wording against those fixtures. Keep
  evidence strength, model-relative posteriors, and heuristic bands distinct
  from validated probabilities, preserving stable JSON fields.
- Fix concrete mismatches found in reproducible reports, and retain unknown or
  unresolved states when the public evidence cannot decide the claim.
- Provide thin, independently removable desktop integrations (such as the
  keyboard-first Omarchy Quickshell plugin in `integrations/omarchy/`), reusing
  existing structured CLI JSON outputs and domain-validation logic without
  shell interpolation or background daemons.

Independent calibration remains unestablished. No company interviews, private
inventory collection, or replacement population study is planned or required
to maintain and release recon. The cancelled M365 frame remains closed. The
[product-quality study requirements](#3-establish-a-reproducible-product-quality-baseline)
are conditional standards for any future empirical accuracy claim, not the next
maintenance task. General robustness envelopes remain research, not a promised
feature. Best effort does not relax provenance, correctness, or wording gates.

Further research remains conditional:

- Before retuning inference, characterize repeated records and shared
  derivations as dependency units. Compare duplicate views, distinct source
  units, and failed collection before changing weights. Per-slug fusion now
  counts each exact source-type/value pair once regardless of matching rule
  names. Dependence among distinct pairs remains unresolved; the score is a
  heuristic, not a calibrated probability.
- Before extending the public observation envelope, identify a consumer that
  needs per-record collection windows, vantage, or graph-completeness metadata.
  Internal timestamps and seed stability cannot supply those guarantees.
- Before claiming client portability, complete the frozen representative-client
  evaluation. Manifest validation and local stdio tests do not substitute for it.
- Before broadening fingerprints, test exact owner/value grammar, deceptive
  lookalikes, overlap, collection opportunity, and retirement semantics. A
  missing public signal can remain the correct answer.

### Autonomous improvement acceptance

The improvement goal is more correctly scoped observations from the existing
public channels, with repeatable evidence for each change. Authorized local
implementation can proceed through automated checks without a human approval
step, company interviews, or private inventory. Independent vendor support is
an evidence requirement; it does not require a human reviewer. Publication
continues to follow the operator's explicit instructions.

Each bounded pass follows the [maintainer loop](maintainer-loop-runbook.md):

1. Select a documented missed pattern or reproduce a violated invariant.
2. Pin the positive and withheld outcomes before changing behavior. For math,
   include duplication, rule aliases, input ordering, and failed-source cases.
   For catalog rules, include exact owners, lookalikes, wildcard responses,
   empty observations, and retained rule provenance.
3. Implement the smallest correction, regenerate affected artifacts, and run
   the focused regressions followed by `uv run python scripts/check.py`.
4. Record the observed improvement and remaining limits, then take the next
   supported candidate. Insufficient documentary support leaves that candidate
   unresolved; it does not block unrelated supported work.

The [first pass](../validation/2026-09-13-evidence-and-catalog-loop.md) makes
per-slug evidence strength invariant to repeated records and rule aliases and
adds Shopify's documented root-domain verification owner.
These are executable correctness and documented-pattern improvements, without
retuning priors or claiming measured real-world precision. Next, apply the same
negative fixtures to additional vendor families and characterize cross-channel
shared derivations before considering broader dependency math.

### The fingerprint-freshness loop, in detail

The repository [maintainer workflow](catalog-maintenance.md) supplies separate
corpus-planning and catalog-round skills alongside fingerprint triage. Planning
is offline; new collection is explicit and bounded. Development exclusions,
source availability, exact rule provenance, and an untouched holdout remain
review gates. Fixed-observation coverage uplift is a diagnostic, not precision
or a complete service-selection counterfactual. These maintenance instructions
do not open a new feature tranche or expand the frozen portable plugin frame.

The harness-neutral maintenance entry point includes a runnable fictional
offline round and private due/review receipts. Frozen collection budgets,
durable starts and consumed-holdout accounting preserve partial and unavailable
work. Monthly reference review is distinct from the weekly endpoint smoke;
neither a scheduled wake nor an empty candidate queue proves catalog freshness
or authorizes collection. See the changelog for release status.

This is the loop that runs forever, because vendors add, rename, and retire the
public patterns recon detects. It runs in two directions each month, and both
carry a public reference or a disclosure-safe basis by construction, so a
promoted rule never rests on a private observation.

- **Corpus-mining direction:** an opt-in private corpus is scanned, unclassified
  DNS observations are diagnosed for gaps, the gaps are measured against the
  frozen classified-surface baseline, and surviving candidates are triaged. This
  finds patterns recon sees but cannot yet name.
- **Vendor-documentation direction:** a vendor's own published verification and
  routing records seed a candidate that carries its reference by construction.
  This finds patterns before a real target exhibits them.

Each pass answers three questions: what is new (a pattern no rule matches), what
changed (a rule whose vendor endpoint or selector moved, caught by drift and a
dead-reference check), and what retired (a rule whose basis no longer resolves,
caught by the freshness audit). A pass can also change family wording without
adding a rule: the first 2026-08-18 vendor-doc check found two already-matched
mail-routing hosts whose primary-family prose still treated a legacy or older
default as current. Disclosure safety rests on the permanently
gitignored private workspaces, the validation-hygiene gate, aggregate-only
memos, and the mandatory public-reference-or-disclosure-safe-basis rule on every
promoted fingerprint. Evaluated apexes, organization names, tenant identifiers,
and per-domain rows never leave the private workspace.

## What Is Next, and Why

Rank and urgency are different axes. Priority 1 remains the standing highest
trust priority because output truthfulness outranks features; its current
29-family audit is complete at the 2026-09-13 checkpoint. Priority 2 adopted
MCP v2 on 2026-07-31 and retains rollback, production-floor, and locked-baseline
pins as blocking checks. Priority 3's
v2.11 decision and v2.12 compatibility transition are complete, and v2.13's
capsule and OKF-deferral release is shipped. v2.14 is also shipped with the
closed rank, regional, vendor-seed, and prior-sample drift decisions plus full
publication proof, v2.15 shipped the default-view claim-clarity and
accessibility decisions, and **v2.16.0 shipped renderer parity** (one shared
briefing across the panel, `--plain`, `--md`, and the MCP text surface, MCP JSON
fusion, and the gated surface-parity matrix).

v2.17.12 shipped the stable engine's bounded composition pass for its primary
audiences. Admins now have installation identity diagnostics when multiple
launchers exist. Defenders have one evidence-first briefing that keeps
collection validity and unresolved states beside review candidates. Consultants
and analysts can carry the existing ecosystem and cohort views in one
backward-compatible JSON bundle for an operator-supplied set. None of these
changes expands collection, infers ownership, or creates a security rating.

The v2.18.0 contract boundary is **NamespaceReviewBundle v1**. This separate
caller-owned artifact composes exactly one baseline that bypasses the
lookup-result cache for one namespace with its evidence-linked review candidates
and one deterministic, role-neutral human rendering. Direct probes remain off,
CT is an explicit recorded choice, and every retained evidence item and
candidate has a stable content identifier. Workflow status distinguishes
`completed` from `failed`; collection validity distinguishes
`complete_for_recorded_opportunities`, `partial`, `unavailable`, and
`not_observed`. Temporal facts are retained without assigning one universal
freshness verdict. The digest detects content modification but is not a
signature or collector identity.

The artifact ships through `recon review <domain>` and the MCP
`build_review_bundle` tool. Both surfaces preserve the same contract, while the
stable lookup, batch, and capsule contracts remain unchanged. A future
operator-supplied set variant is deferred until this first contract is stable.
It must not infer portfolio membership, rank security, schedule collection, or
upload retained evidence. The fingerprint-freshness loop remains the durable
detection stream and continues alongside this product polish.

The stability soak that began with v2.18.0 continues after v2.19.6. Fix
compatibility, rendering, or provenance defects found through real operator use;
collect role-specific feedback before considering a set-level extension; keep
set membership caller-supplied; continue the monthly fingerprint-freshness and
per-release black-box renderer loops; and keep the 29-family claim audit, all three
MCP SDK pins, the full test gate, and release provenance blocking. Further
feature work requires a named operator handoff that the stable surfaces
cannot solve.

v2.18.1 addresses the first stability-soak defect: a degraded CNAME
classification pass no longer erases names contributed by a separately
successful CT path. Exact CT name provenance is internal and cache-persistent;
the stable lookup schema, briefing versus full-map split, and fail-closed
CNAME-dependent classifications remain unchanged.

Agent portability is a separate maintainer track, not a version-path
milestone: its representative task, client, measure, privacy, and stop-rule
contract is frozen, its protected-main prerequisite and the candidate's
network-free schema, layout, launch, skill, and version validation are complete,
and a 2026-08-20 preflight passes with every frozen client and the matching
runtime. The v1.0.0 specification is Published and its canonical schemas remain
byte-identical to the pinned copies. The paired evaluation is still unmeasured,
so the project makes no client compatibility or conformance claim. GPT-5.6
Luna and a $5 total external-charge ceiling are declared. Resume the current
native path against the complete-surface candidate in the frozen VS Code,
Cursor, and Kiro frame only when the account hard stops and reproducible client
driver are verifiable, without changing stable CLI, JSON, or MCP contracts.
New claim-surface drift reopens
priority 1. Version milestones through v3.0:
[ROADMAP.md](../ROADMAP.md#version-path-order-of-operations).

| Track | Why it sits here | State today | What closes it |
|---|---|---|---|
| [1. Evidence-semantic integrity](#1-restore-evidence-semantic-integrity) | Truthfulness outranks features, and this defect class required a complete sweep rather than one-case fixes. | Complete through the 2026-08-30 ReviewBundle review. The fail-closed default-claim audit owns all discovered primary surfaces through 29 families. 29 are complete; 0 material runtime families carry incomplete lineage. Static agent and MCP contracts now pin process scope, collection boundaries, output forms, cache behavior, and abstention semantics. Runtime explanations, insights, panels, service labels, posture observations, hardening prompts, cohort summaries, ReviewBundles, and every exposure-index component carry their reviewed evidence or static contract basis. | Keep the fail-closed audit green; any uncovered or semantically stronger surface reopens this track. |
| [2. MCP protocol characterization](#2-keep-final-mcp-v2-compatibility-green-after-adoption) | The 2026-07-28 specification is a breaking release and the SDK moves regardless of recon, so compatibility must stay explicit. | Production adopted `mcp>=2.0.0,<3` on 2026-07-31. Exact `1.28.1`, `2.0.0`, and `2.3.0` rows remain blocking. | Keep deterministic ordering, conforming schemas, live stdio behavior, and all three exact pins green. |
| [3. Product-quality baseline](#3-establish-a-reproducible-product-quality-baseline) | Depends on a stable claim taxonomy from priority 1. Measuring still-incomplete claim families would measure a definition that is changing. | v2.11 stopped a structurally non-identifying design before target contact. v2.12 classifies fusion as an advanced diagnostic and starts the explicit-flag transition while preserving the stable v2 default. | Keep the identifiability gate and ADR-0013 transition contract blocking. Any future fusion study needs a new identifiable candidate and preregistration. |
| [4. Catalog quality loop](#turn-catalog-quality-into-the-detection-improvement-loop) | The shipped claim, compatibility, quality-decision, and capsule contracts make independent catalog measurement interpretable. | Shipped in v2.14. Convenience, unseen-vertical, rank, regional, vendor-seed, and prior-sample drift rounds are complete with aggregate results and explicit dispositions. Drift records no threshold breach, no unavailable or unmeasured row, one disclosed measurement-surface change, and no catalog promotion. | Keep the frozen round contracts and regression gates reproducible; backfill review dates only in independently reviewed families. |
| [4. Optional cloud access and scale-out](#4-optional-operator-hosted-access-and-scale-out) | Useful accessibility and scale polish for some operators, but lower priority than the core evidence, compatibility, and catalog-quality tracks. | Draft stateless remote adapter, container, and Cloud Run Terraform pass local artifact checks but are not yet provider-validated. Local remains the default. | One operator proof plus bounded load, cost, rotation, retention, and rollback evidence. Each additional provider needs named demand and its own validation context. |

Everything blocked behind these, and the gate that unblocks each, is in
[ROADMAP.md](../ROADMAP.md#what-is-deliberately-not-next). The phased execution
sequence is the
[Quality Proof execution plan](strategic-gap-audit.md#quality-proof-execution-plan).

## Product Goal

recon composes typed public DNS, certificate-transparency, and unauthenticated
identity evidence around a domain query coordinate while preserving scope,
time, dependence, collection opportunity, and ambiguity. A domain is not an
organization identifier. The result is a conservative, provenance-bearing view
of its public technology and identity namespace, and its best answer is
sometimes "unresolved." It must not turn parent-platform presence, sparse
metadata, a model score, or missing public evidence into a claim about product
use, security maturity, ownership, or exploitability.

The primary workflows are:

1. Single-domain public-evidence summary.
2. Explanation and provenance for every material claim.
3. Operator-supplied comparison, batch, or related-domain analysis.

Advanced graph, posterior, hypothesis, simulation, catalog-mutation, and
fingerprint-discovery surfaces remain available for specialist workflows. They
must earn their complexity through measured value and must not obscure the
three primary workflows.

## Current Product-Surface Debt

This ledger keeps polish work inside the shipped product boundary. It names
current debt without turning every refinement into feature work.

| Debt class | Current state | Next boundary |
|---|---|---|
| Feature work | Governed by the dependency order below, not by the polish loop; the optional operator-hosted surface now has a named architecture and security gate | Do not add commands, schemas, provider claims, or inference modes without their existing evidence gate |
| UX flow | Root help, no-argument onboarding, installation identity diagnostics, malformed-input recovery, all-source failure recovery, low-confidence next steps, evidence-first defender briefing, combined portfolio JSON, batch outcome guidance, cross-platform release verification, target-free catalog discovery, explicit bounded-versus-complete cache inspection, and NamespaceReviewBundle v1 through CLI and MCP are implemented | Keep both review surfaces contract-identical; defer saved set manifests, divergence records, and any set renderer until the single-namespace contract is stable and keep membership caller-supplied |
| Visual polish | Lookup and batch help use task panels; linear help and adaptive welcome rows keep commands complete; fingerprint previews, ranked signal results, and narrow cache rows keep hierarchy and field association without changing structured order | Preserve complete option visibility and exact technical-token copyability before changing presentation metadata |
| Observability | MCP rejection logs and unexpected batch details stay bounded; live MCP diagnostics retain completed rows and name the failed protocol phase; cache overview names exact inspected, uninspected, failed, and temporary-artifact state; corpus tests separate collection errors from negative observations; captured gate logs are plain; remote readiness and release recovery name exact evidence and preconditions | Define a versioned doctor or cache record only after a machine consumer and compatibility envelope are named |
| Reliability | Static and live MCP diagnostics require canonical tools and resources, with live JSON resource reads; typed batch errors, bounded workers, bounded corpus and default cache inspection, residue-aware cache clearing, closed-pipe handling, explicit degradation, exact exit codes, complete catalog inspection, sealed artifact reconstruction and parity, command-status-aware release recovery, fail-closed bounded dependency-audit retry, and all-nonzero SBOM audit gating are implemented | Do not change the current batch or corpus-test exit contract without a compatibility decision covering mixed and all-error streams |
| Security | Unresolved HTTP destinations fail closed; rejected values and unexpected details stay out of default output; persisted inputs, corpus files, local catalog text, and default cache payload work are bounded; empty catalog filters cannot bypass compact defaults; release verification binds artifacts and recovery commands to exact status, workflow, tag, signer, and commit evidence; the installed dependency auditor resolves under Python isolated mode; pull requests and pushes to `main` run CodeQL while weekly and manual main scans remain | Ratchet the remote SAST requirement from its evidence-backed transition floor of 7 to 10 only after the public Scorecard window reports successful supported SAST checks for every sampled merged pull request; do not backfill history for the metric |
| Accessibility | `--plain` is shipped; help uses complete linear output when needed; welcome alignment is content-aware at ordinary widths; catalog and cache rows preserve labels when narrow; color is never the only status channel | Keep both paths complete; do not replace the parser or hide specialist controls |
| Documentation accuracy | README, MCP quick starts, stability, operational, security, generated CLI, release, catalog, cache, corpus, agent, schema, example, snapshot, and test surfaces use reserved target identities or disclosure-safe aggregates; the release gate rejects the retired target vocabulary | Keep eventual machine diagnostics separate from human output until versioned contracts are justified; retain manual review for previously unseen organization-shaped prose and preserve provider definitions |
| Interchange portability | Native client layouts remain the supported install paths. A deterministic complete-surface candidate passes offline validation against byte-pinned Agent Plugins v1.0.0 schemas that still match the Published canonical bytes. The frozen three-client/runtime preflight passes, GPT-5.6 Luna and a $5 ceiling are declared, but representative-client compatibility is unmeasured. Versioned JSON remains the structured runtime contract. v2.13 shipped a separate caller-owned capsule schema; ADR-0014 defers OKF v0.2 because no named consumer justifies its trust and lifecycle mapping. | Resume the complete frozen native-versus-portable VS Code, Cursor, and Kiro frame only when account hard stops and a reproducible three-desktop-client driver are verifiable. Keep the capsule and JSON contracts stable and native paths supported. Reopen an additive OKF projection only for a named consumer with a privacy review; never replace JSON or turn offline validation into a conformance claim. |

## Priority Order

### 1. Restore evidence-semantic integrity

Status: complete on 2026-08-01; fail-closed drift monitoring remains active.
The live MCP instruction, score-description, parent-platform child-product,
and cross-renderer provider summary corrections began shipping in v2.4.0.

Why first: output truthfulness is more valuable than another feature. The
roadmap review found a sparse-output fixture that inferred Copilot use from a
parent tenant even though the evidence could not establish child-product
licensing, enablement, deployment, or use. That inference and the earlier MCP
target-interaction and score overstatements are now corrected with regression
tests. Provider topology now also uses one evidence-aware summary across panel,
JSON, CSV, MCP, and chain output. Source-derived Markdown service labels now
cross an escaped output boundary, and service sections use exact,
mutually exclusive provider grouping instead of broad substring matches. The
inference-confidence path now groups error-free source types and sources by
canonical claim, so failed or unrelated provider evidence cannot corroborate
a different claim. Duplicate result objects from one source count once, and
explanations name the exact winning claim and qualifying evidence.
The fail-closed [default-claim audit](default-claim-audit.md) now inventories
every discovered primary surface and binds compact JSON and MCP ownership to
exact digests. All 29 families are complete. Generated insights capture the emitting rule and exact
retained-evidence or bounded-observation association before rendering, preserve
that state through collection projection and result-cache version 4, and feed
it into explanation construction without text classification. Structured
observation scopes, related-namespace signal isolation, and strict cache
lineage validation enforce that contract across degraded and enriched results.
Explanation terminals now carry explicit exact, exact-rule-only, reconstructed,
or unsupported lineage status. The additive exact-lineage diagnostics list
every terminal without a retained evidence-to-rule association while the
schema-version-1 reachability fields keep their stable meaning. Default panel
assembly now uses the queried namespace coordinate, shares canonical projected
field semantics, and excludes unavailable channel evidence from derived
summaries. Service labels now retain evidence-established roles, and posture
observations retain their exact rule, branch-local evidence, and typed metadata
dependencies through CLI, MCP, profile, and explanation paths. Profile-relative
expectations are withheld under degraded collection and remain lenses rather
than scores. Hardening prompts now distinguish observed weak configuration,
bounded non-observation, unresolved hideable state, and observed configuration
inconsistency while retaining exact generator, evidence, predicate, and scope
lineage. The exposure index now exposes its complete weighted component ledger,
including exact rule, state, predicate, scope, awarded and unresolved points,
and retained evidence. Comparison output carries a ledger for each namespace,
and hardening simulation labels changed components as hypothetical. All
material runtime families now have exact lineage. Static MCP and generated-guidance
semantics now have dedicated process-scope, network-boundary, output-form,
cache-behavior, and abstention guards. Current sovereignty
handling preserves absent metadata as unknown; that invariant should remain
explicit and tested.

Work:

- Audit every default panel insight, service label, live MCP instruction and
  tool description, generated agent guidance item, recommendation, and score
  label against its direct provenance path.
- Treat the queried apex as a namespace coordinate, never an organization
  identity. Audit shared-token, tenant, display-name, issuer, vendor, CT, and
  related-domain language so exact observed overlap is not promoted into
  ownership, shared control, account identity, or current-use claims.
- Define one machine-readable internal claim contract before creating another
  inference layer. It must declare the narrow claim and scope, positive
  alternatives, genuine authoritative negatives, source-success preconditions,
  dependency groups, freshness, renderer obligations, generation-time rule
  lineage, and regression fixtures. Heuristic reconstruction from rendered
  insight or posture text cannot satisfy exact provenance.
  - Completed in v2.5.0 for
    `dns.dmarc.valid_policy_is_reject.v1`; see
    [claim-contracts.md](claim-contracts.md). Exact evaluator lineage reaches a
    collector-retained raw record. The bounded built-in insight generators now
    retain exact rule and evidence-or-observation-scope associations. Posture,
    hardening, exposure-index, and time observations now retain their reviewed
    exact generation path or explicit bounded scope. No tenant field or
    public dossier was added. The separate
    cohort-summary contract adds 2.2 as an explicit option while 2.1 remains the
    default.
- Model construction, collection, claim state, and time as orthogonal axes.
  Design an internal observation-opportunity ledger with `not attempted`,
  `observed value`, `observed empty`, `unavailable`, `not enabled`, and `not
  applicable`; keep the stable `EvidenceRecord` and `degraded_sources` shapes as
  compatibility projections until an additive contract earns promotion.
- Prototype an internal claim dossier for that one family: four-state result,
  minimal supporting and authoritative-negative certificate antichains,
  incomplete provenance, unavailable channels, observation window, conflicts,
  and permitted resolving evidence. Use bounded frozen-set antichains, not a
  new dependency or an unreviewed broad ontology.
  - Completed for the first DMARC contract with bounded exact antichains,
    fail-closed limits, explicit provenance limitations, and replay after
    canonical ledger union.
- Encode the four states as a two-coordinate knowledge lattice. Merge canonical
  provenance ledgers by associative, commutative, idempotent unit union, then
  recompute rule closure and certificate antichains. The state projection must
  be monotone for reviewed monotone rules but is not generally a homomorphism:
  premises split across views may create a new derivation. Expiry or retraction
  must replay the remaining ledger instead of trying to invert a merge.
- Keep the shipped regression guard that rejects child-product use or
  deployment claims inferred only from a parent platform.
- Preserve missing cloud metadata as unknown.
- In human-facing output, describe `email_security_score` as a count of
  observable public email controls and the 0-100 value as a model-bound
  public-evidence index. Preserve stable JSON fields until a versioned contract
  change is justified.
- Separate observed configuration, defined public absence, and unresolved
  non-observable state in recommendations.
- State the default target-visible MTA-STS policy fetch and opt-in CSE and BIMI
  requests anywhere the product summarizes its collection boundary.
- Design, but do not expose prematurely, a defaulted provenance envelope that
  can carry record owner, source family, observation time, scope, and freshness
  semantics. Any stable schema addition follows
  [ADR-0003](adr/0003-v2-schema-lock.md).

Acceptance evidence:

- Every material default claim has a direct evidence-to-claim path.
- Every material cross-domain statement names the exact typed overlap and keeps
  alternative explanations open; shared administrative tokens, tenant IDs,
  broad providers, and public issuers do not become ownership verdicts.
- The first claim contract has positive, explicit-disconfirming, conflict,
  unavailable, empty, invalid, stale, time-unknown, and duplicate-derivation
  fixtures in `tests/test_claim_contract.py`. Its result is invariant to
  duplicate renderings of one evidence unit. Empty DNS results remain
  unresolved until authority or authenticated-denial provenance is retained.
- Property tests establish canonical-ledger union laws, duplicate invariance,
  monotone state projection, and a cross-view conjunction whose support appears
  only after merged-ledger closure. Adding evidence cannot erase an already
  established sign under the reviewed monotone rule system.
- Explanation output reports provenance completeness and disconnected terminal
  claims instead of asserting a complete path when none exists.
- Sparse golden outputs contain no product-use inference derived solely from a
  parent platform.
- Missing sovereignty metadata never produces a commercial-cloud conclusion.
- No default output presents a public-evidence index as overall security
  maturity.
- Existing v2 JSON compatibility remains green unless an explicitly versioned,
  additive schema change is approved.
- Relevant golden, cache, schema, explanation, panel, and MCP tests pass.

Stop rule: do not add new inference or scoring semantics while a known default
claim lacks adequate evidence.

### 2. Keep final MCP v2 compatibility green after adoption

Status: production adoption complete on 2026-07-31. The 2026-10-20 currency
check refreshes the lock and current-SDK row to 2.3.0; exact v1.28.1 rollback,
v2.0.0 production-floor, and v2.3.0 locked-baseline rows remain blocking.
See the [dated compatibility results](mcp-2026-07-28-readiness.md#dated-compatibility-results)
for the upstream behavior review and local probe evidence.

The matrix pin lives in `.github/workflows/ci.yml` and the probe is
`scripts/check_mcp_compatibility.py`. It exercises both stable SDK generations
without changing `pyproject.toml`, `uv.lock`, or the active environment.

Why second: the final MCP 2026-07-28 specification and stable Python SDK are
external compatibility boundaries. Production now runs on the stable v2 SDK;
the v1.28.1 row continuously verifies the rollback path.

Completed checkpoints:

- Exact-pin `mcp==2.0.0` in an isolated compatibility environment without
  widening the production dependency.
- Exercise server import, stdio startup, `recon mcp doctor`, discovery, tool
  calls, resource reads, structured output, errors, and deterministic listing
  under stable v1.28.1 and stable v2.0.0.
- Record a migration result for `FastMCP`, protocol types, `ToolError`,
  annotations, discovery, wire aliases, and synchronous resource handlers.
- Review shared catalog and cache behavior under the v2 worker-thread model.
- Reject the unproven `mcp>=1.0` floor and raise it to the fully characterized
  stable v1.28.1 release.

The same compatibility boundary passes 23 tools, six resources, zero
resource templates, one prompt, 44 schema documents, representative structured
success and error results, concurrent catalog reloads, real stdio calls, and
the live doctor on all three supported exact pins. Stable v2 additionally proves
`server/discover`, worker-thread synchronous handlers, and conservative
complete-result metadata on every cacheable method. Production uses
`mcp>=2.0.0,<3`, adopted after the remote adapter and compatibility boundary
passed the same gate.

Acceptance evidence:

- A dated compatibility matrix covers both SDK generations.
- Tool and resource order is deterministic.
- Declared output schemas and structured results conform under both tested
  generations.
- Every complete `server/discover`, `tools/list`, supported resource-list, and
  resource-read result carries valid `ttlMs` and `cacheScope` hints as required
  by the final caching specification.
- The local stdio workflow remains intact.
- Production stays on v2 while the exact v1.28.1 rollback row remains green.
- The optional remote HTTP need now has a separate architecture and security
  review. It does not imply OAuth, Roots, Sampling, Apps, Tasks, protocol
  logging, or production SDK v2 adoption.

Detailed work and rollback criteria live in
[mcp-2026-07-28-readiness.md](mcp-2026-07-28-readiness.md) and
[ADR-0009](adr/0009-mcp-2026-readiness.md).

### 3. Establish a reproducible product-quality baseline

Status: structural stop recorded before target collection. The network-free,
corpus-free half of the Phase 1 baseline is frozen in
[2026-08-05-quality-baseline-scorecard.md](../validation/2026-08-05-quality-baseline-scorecard.md);
the aggregate-only stable-v1 network characterization is complete in the
[2026-08-12 live-characterization memo](../validation/2026-08-12-stable-v1-live-characterization.md).
The population, two-stage sampling mechanism, eligibility window, cluster rule,
public HMAC contexts, private-key commitment, and private-frame commitment are frozen in the
[v2.11 frame declaration](quality-evaluation-frame-declaration.md), but the
window is cancelled and the frame remains unused. The 2026-08-13
[arm-identifiability audit](../validation/2026-08-13-quality-arm-identifiability.md)
stopped the design with zero target requests.
Depends on the claim taxonomy from priority 1.

The phase order, promotion evidence, and stop rules are summarized in the
[Quality Proof execution plan](strategic-gap-audit.md#quality-proof-execution-plan).

Every choice that had to precede results is frozen in
[quality-baseline-preregistration.md](quality-baseline-preregistration.md),
dated 2026-08-05. It selects `m365_tenant` under
`runtime.identity-and-tenant.v1` as the primary family by elimination from the
[external evidence ledger](statistical-assurance.md#external-evidence-ledger),
pins the intended arms to code paths, fixes the safety margin at 0.02, and
records a power analysis. Its dated amendment now records that the arms do not
form four distinct binary decisions under shipped behavior. A1 equals A0, A2
equals A3, and A3 never supports when A0 abstains. Consequently the positive
benefit gate cannot pass for any sample size. The evaluation frame excludes the
existing calibration corpus whole and remains unused.

The audit produced a result, not only an absence. Across the enumerated DNS
evidence-role states, the candidate's supported set is a subset of the
baseline's: A3 never supports where A0 abstains, and A0 supports where A3
abstains. Under the shipped emission threshold, the Bayesian fusion layer cannot
add a supported M365 tenancy claim the deterministic layer does not already
make. That is exhaustive over the enumerated space rather than sampled, so it is
a stronger and more general finding than the cancelled 340-domain collection
could have produced. It is scoped to one claim family, one DNS-only channel, one
node with one binding, and the shipped 0.5 model-support threshold, and it is
not a population claim. The evaluation design that follows is preserved as the
frozen record of what was committed; it is a post-mortem, not a plan.

Why third: the project has extensive implementation and assurance checks, but
it does not yet measure whether probabilistic fusion, CT enrichment, a large
fingerprint catalog, or a broad MCP surface materially improves a predeclared
operator outcome over deterministic evidence plus explicit abstention.

Work:

- Create an aggregate-safe scorecard using synthetic fixtures plus
  maintainer-local, disclosure-controlled real-domain evaluation.
- Measure claim-family precision where independent labels exist, unsupported
  claim rate, abstention and unresolved rate, explanation completeness,
  classified versus unclassified observable surface, degraded-source rate,
  p50/p95 cold and warm latency, peak allocation, CT marginal signal gain, and
  MCP discovery and result payload bytes.
- Require an executable structural-identifiability and dominance preflight
  before any future live ablation. The frozen M365 design failed this check:
  its arms collapse and its candidate cannot beat its baseline. Treat that stop
  as useful evidence, not as a reason to invent a threshold or collect anyway.
- Require each future source, inference, catalog, or graph change to name the
  metric it should improve and the regression budget it must preserve.
- Keep the completed stable-v1 resolver, allocation, CT-value, and independent
  Draft 2020-12 schema characterizations as blocking baseline inputs. The live
  convenience sample completed 50 of 50 no-CT contract rows and 47 of 50 CT
  rows, with three bounded timeouts and no product-contract failure. It is
  performance and degradation evidence, not outcome or population evidence.
  Apply stable-v2 deltas from the completed MCP matrix separately.

Primary evaluation design:

- Operator decision: for one material claim in a single-domain summary, should
  the operator accept it as supported by the public channel or see it remain
  unresolved?
- Unit: predeclare one primary claim family, the current Bayesian candidate, and
  the deterministic comparator. Each unique domain contributes one frozen
  `(domain, claim_family, observation_time)` row and one independent reference
  label, and every arm receives the same raw snapshot. Admit at most one domain
  from each known administrative, ownership, or tenant cluster in the primary
  analysis. This keeps the domain row identical to the Bernoulli unit used by
  the paired decision rule. Unknown cross-domain dependence remains a
  limitation. A clustered multi-domain analysis is secondary until it defines
  a cluster-level estimand, outcome, and decision rule. Domain groups are kept
  intact across parameter-development, calibration, and evaluation splits. Any
  corpus that informed a prior or likelihood is a development corpus and cannot
  supply primary rows. Repeated observations, other claim families, and other
  arm contrasts are sensitivity analyses only and cannot change the primary
  decision.
- Sampling model: before collection, name the target population, eligibility
  window, positive- and negative-stratum sampling frames, and sampling
  mechanism. Population-coverage interpretation for the paired
  Clopper-Pearson bounds and prospective power analysis requires independent
  exchangeable Bernoulli units within each stratum after known-cluster
  exclusion, or a probability sampling design with matching design-based
  inference. For a fixed or purposively selected corpus, `(b-c)/n` is only the
  exact empirical corpus effect. Any binomial interval is then model-based on
  an unverified exchangeability assumption and cannot support population
  promotion.
- Labels: an independent provider-owned endpoint, standards-defined public
  record, or other predeclared authoritative source that is not an input to the
  compared predictor. A family without an independent reference reports only
  coverage, provenance, and disagreement diagnostics, never precision.
- Primary benefit estimand: **reference-positive support rate**, the number of
  independently labeled positive units emitted as supported divided by all
  independently labeled positive units. Candidate-minus-baseline is positive
  when the candidate supports more true claims.
- Primary safety estimand: **reference-negative unsupported-emission rate**, the
  number of independently labeled negative domains emitted as supported divided
  by all reference-negative domains. Candidate-minus-baseline is positive when
  the candidate causes more unsupported emissions. The negative-stratum
  denominator prevents the safety metric from changing with an intentionally
  stratified label mix. Also report selective risk, unsupported emissions
  divided by all supported emissions, but do not use that unstable ratio as the
  primary gate when an arm emits nothing.
- Secondary evaluation: report abstention, overall emission rate,
  distinct-score or tie-preserving reliability, provenance completeness,
  latency, and allocation. Report Brier and log score only for an arm whose
  total frozen forecast is explicitly interpreted as
  `P(reference-positive | frozen inputs)` on every eligible two-class row, with
  a predeclared abstention convention. An arbitrary evidence-strength score
  qualifies only after its mapping is fitted on disjoint development data and
  frozen. Otherwise exclude the arm from proper-score comparison or label any
  plug-in loss descriptive, not proper-score evidence. Any interval must name
  its resampling unit and assumptions. Do not call a model calibrated from an
  overlapping, one-sided, or parameter-development reference.
- Prevalence-sensitive secondary metrics: when label strata have different
  sampling rates, pooled abstention, unresolved, overall emission,
  proper-score risk, reliability, and selective risk require known inclusion
  probabilities and frozen design or post-stratification weights for the target
  population. Without them, report stratum-specific or fixed-sample descriptive
  values and make no population rate or calibration claim.
- Minimum evidence for a decision: the
  [preregistration](quality-baseline-preregistration.md) supersedes this
  roadmap's earlier nominal floor of 100 units with 30 and 30. Under the exact
  paired rule and the frozen safety margin, the power analysis requires at least
  155 reference-positive and 183 reference-negative units (roughly 340 after
  cluster exclusion and ineligible-row removal); at n=30 the tightest achievable
  safety statement is a margin near 0.12, which is why 30 was never a power
  claim. Report every arm's emission and discordance counts. Selective risk for
  an arm with fewer than 30 supported-emission unique domains is descriptive
  only. A corpus that misses either primary label stratum is ineligible for the
  decision gate.
- Boundary-valid paired rule: within each label stratum, count candidate-only
  supported decisions `b`, baseline-only supported decisions `c`, and unique
  domains `n`. Construct a conservative one-sided 95 percent bound on
  `(b - c) / n` by subtracting Bonferroni-adjusted one-sided
  Clopper-Pearson bounds for the two discordance proportions. Use a lower bound
  for benefit in the positive stratum and an upper bound for safety in the
  negative stratum. This remains uncertain when both arms make zero unsupported
  emissions; unlike a percentile bootstrap, it cannot collapse to a false
  `[0, 0]` safety conclusion at the boundary.
- Promotion rule: before reading outputs, choose and justify a small positive
  absolute safety noninferiority margin, freeze the tail probability and
  implementation, and require both co-primary conditions: the benefit lower
  bound is above zero, and the safety upper bound is below that margin. Also
  require the empirical zero-regression safeguard `b_negative == 0`: the
  candidate may not introduce an unsupported emission on any negative domain
  that the baseline left unresolved. A zero margin would be strict safety
  superiority, not noninferiority, and is prohibited under the boundary case.
  Because both co-primary conditions must pass, this is an intersection-union
  decision; additional arm or family claims need a predeclared multiplicity
  procedure.
- Reporting: publish raw paired counts and candidate-minus-baseline effect
  bounds. Under simple exchangeable sampling within label strata, a paired
  domain bootstrap may be reported only as a secondary sensitivity analysis:
  resample the positive and negative strata separately, apply the same sampled
  units to every arm, and preserve both denominators. Under a complex
  probability design, any resampling interval must reproduce the frozen
  strata, primary sampling units, and inclusion weights or use a valid survey
  bootstrap. Otherwise label it a fixed-sample sensitivity with no
  design-based coverage interpretation. Repeated observations belong only in a
  separate longitudinal sensitivity analysis clustered by domain. Neither
  analysis can rescue an inconclusive primary result. An inconclusive or
  negative result moves fusion to an explicitly advanced diagnostic.

Acceptance evidence:

- A dated baseline, reproduction command, environment description, and
  aggregate result memo exist.
- No real apex, organization name, tenant ID, or per-domain row is committed.
- The ablation decision rule is written before the run.
- The result determines whether advanced fusion remains in the primary path or
  becomes an explicitly advanced diagnostic.
- Coverage remains above the enforced 90.2 percent branch-aware project gate and
  the 80 percent user bar, with no regression from the current baseline, and
  the canonical local gate passes.

Stop rule: do not expand graph or probabilistic machinery without measured
benefit to a named user outcome.

### 4. Optional operator-hosted access and scale-out

Status: draft and not yet provider-validated, lower priority than the three
core tracks above. It is intended to be
directionally useful, not a validated production deployment.

Why last: an authenticated remote endpoint can make recon accessible to
operators who want to use it from several AI products, shared automation, or a
cloud environment. That is useful depth and scale polish for some users. It is
not required to use recon, does not replace the local CLI or stdio MCP server,
and does not create a project-operated hosted service.
The project does not operate a hosted endpoint.

Principles:

- Keep one model-neutral remote MCP boundary. OpenAI, Anthropic, Microsoft
  Foundry, and other compatible clients consume that endpoint; they do not need
  separate recon implementations.
- Keep deployment operator-owned and opt-in. Local CLI and stdio MCP remain the
  complete default and require no cloud account.
- Use a stateless Streamable HTTP process in a non-root OCI container, with
  bounded requests, explicit authentication, host and origin controls, no
  stateful catalog-mutation tools, and provider-managed secret storage.
- Treat a cloud provider as a hosting and identity choice, not as the AI model
  choice. A caller can host on one provider and use an AI client from another.
- Label every reference at the evidence level it has. Passing local syntax,
  build, and protocol checks is not provider validation. A provider logo or
  speculative Terraform module is not implementation evidence.

Initial work:

- Maintain the optional remote adapter and portable container as draft
  artifacts without adding a new default CLI path or dependency group.
- Maintain one draft Google Cloud Run Terraform reference because Cloud Run
  documents remote MCP hosting, supports scale to zero, and accepts the
  portable container contract.
- Keep AWS AgentCore, Azure Container Apps, Cloudflare, Kubernetes, and
  per-user OAuth as researched plans until each has named demand and the
  provider-specific validation context needed to make its security and IaC
  claims true.

Acceptance evidence:

- One external operator validates the reference through a real remote MCP
  client and records the exact image digest, region, identity mode, and rollback
  path.
- Bounded load testing records concurrency, latency, timeout, scale-to-zero,
  provider quota, and cost behavior without committing queried-domain data.
- Credential rotation, secret versioning, log redaction and retention, image
  rollback, and deletion are exercised.
- CI keeps the container build, health boundary, unauthenticated rejection, and
  Terraform formatting and validation green.
- Adding another cloud implementation requires a named operator, provider
  identity and region context, and the same evidence at that platform's
  boundary.

The full architecture, July 2026 research, provider matrix, threat model,
sequencing, and runbook gates live in
[optional-cloud-deployment-plan.md](optional-cloud-deployment-plan.md).

Stop rule: do not turn this into a project-operated SaaS, claim model-vendor
hosting where the vendor is only an MCP client, or add provider IaC that has not
been validated against a real provider context.

## Next

These tracks follow the completed evidence, compatibility, quality-decision,
and capsule milestones in dependency order. The stable-v1 async and schema
characterizations remain completed supporting evidence; stable-v2 deltas are
available from the completed priority 2 matrix.

The immediate product execution slice is the fingerprint-freshness loop.
v2.27.0 published progress notifications, capability honesty, display titles,
the Claude Code marketplace, Codex and Gemini CLI install targets, and MCP
Registry metadata. That release did not change this slice. A round makes a
new temporary question list, keeps that list private, and publishes only a
disclosure-safe pattern with synthetic fixtures. It does not publish a claim
that a named organization uses a service. The 2026-10-28 pass dated two AI
verification rules whose current vendor pages state the token grammar and
left six undated because the cited pages do not. A later pass the same day
checked eight undated CRM and marketing rules and left them undated for the
same reason. The older Dynamics authenticate-domains article now redirects,
and a search-index copy of it is not a current basis. A later pass the same
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
seven other rules undated. That work does not cut a release. The 2026-10 documentation
pass read the IANA DNS parameter update and left collection on the existing
record types. Agent portability remains a separate maintainer track and does
not appear here as a product milestone:

1. Preserve the shipped v2.14 rank, regional,
   [vendor-seed](../validation/2026-08-14-catalog-vendor-seed-round.md), and
   [prior-sample drift](../validation/2026-08-14-catalog-drift-round.md)
   decisions, including every promoted, rejected, deferred, unavailable,
   unmeasured, measurement-surface, and non-comparable disposition.
2. Require every promoted rule to carry a current provider reference or
   disclosure-safe basis, a `verified` date, a fictional positive fixture, a
   lookalike negative, scoped wording, and exact provenance tests.
3. Backfill `verified` dates only in independently reviewed families after
   confirming the vendor's current public page. The 2026-08-19 MX pass dated
   Google Workspace (`smtp.google.com` current default, `aspmx.*` documented
   pre-2023) and Microsoft 365 (`mail.protection.outlook.com` still named,
   `mx.microsoft` for DNSSEC/DANE and some new accepted domains) from the
   current vendor pages. That was family wording and dated coverage, not a
   missing-pattern promotion. The later 2026-08-19 Okta pass dated the
   custom-domain family (`_oktaverification`, `okta.com`, `oktapreview.com`,
   `customdomains.okta.com`, `okta-dnssec.com`, `okta-gov.com`) from current
   developer and allowlist pages; `okta-domain-verification` stays undated
   because the current guide does not name it. The 2026-08-20 Mimecast pass
   dated inbound MX and `_netblocks` SPF from current support articles. A later
   2026-08-20 pass dated current TrendAI regional MX and SPF values, Barracuda
   inbound MX, and Cisco Cloud Gateway `iphmx.com`. It corrected the Cisco
   current-versus-earlier direction and left `ess.cisco.com` undated. The same
   pass completed the 22-region AWS SES receiving table and dated current AWS
   SES, Google Workspace, and Microsoft 365 SPF values. It also dated current
   Akamai `akamaiedge.net`, `akamaized.net`, `edgekey.net`, and `edgesuite.net`
   CNAME rules without stamping the separately unsupported Akamai patterns.
   The bounded HubSpot review then dated its current `hubspotemail.net` SPF and
   two `hubspot.net` CNAME rules while leaving seven unsupported patterns
   undated.
   The bounded Marketo review then dated `mktomail.com`, both `mktoweb.com`
   CNAME paths, and the exact documented tracking-link host form. It replaced
   the broad `mkto-` fragment with a validated regex and left five unsupported
   patterns undated.
   The bounded Salesforce Marketing Cloud review then dated eight CNAME and
   discovered-target rules for documented application, CloudPages/content,
   web-view, tenant-specific API, and Subscription Center roles. It left the
   unsupported `exacttarget.com` SPF and `SFMC-` TXT observations undated.
   The AWS load-balancer correction then consolidated seven partial regional
   `aws-nlb` rules into one partition-aware ELBv2 regex, retained the stable
   slug, and made the ALB/NLB ambiguity explicit.
   The AWS API Gateway correction then consolidated five partial regional rules
   into one partition-aware regex while excluding edge-optimized CloudFront and
   private VPC endpoint forms. The Microsoft residual pass separated Azure
   Communication Services Email's `ms-domain-verification=` token from
   Microsoft 365's `MS=ms########`, narrowed commercial Autodiscover and GCC
   High MX, and dated the supported government SPF, government application
   domain, and SharePoint roles.
   Proofpoint gateway MX/SPF stays undated: public product pages do not name
   those hosts, and the Essentials connection-details article is login-walled.
   Detail:
   [catalog-strategy.md](catalog-strategy.md#3-freshness).
4. v2.17.5 published this batch after a reviewed pull request and all protected-
   main checks, with PyPI and GitHub artifacts, SBOM provenance, and exact
   channel-parity proof. The follow-up Microsoft review closes the named
   residual queue. Current endpoint guidance supports bounded
   `tm-3.office.com`, `svc.cloud.microsoft`, and `svc.sovcloud.cn` route
   observations; current Exchange guidance supports narrowing the broad
   `eo.outlook.com` rule to the documented legacy `mail.eo.outlook.com` MX
   family. `msv1.invalid` remains undated and no longer claims a
   migration state because no current first-party page documents that role.
   Keep Proofpoint blocked for the same evidence reason. Detail:
   [2026-08-20 Microsoft residual review](../validation/2026-08-20-microsoft-residual-review.md).
   The 2026-08-21 Statuspage review then replaces a dead shared reference and
   dates the exact current custom-email TXT, SPF include, and custom-domain
   CNAME-target family. Four unsupported variants remain undated with narrower
   claims. Detail:
   [2026-08-21 Statuspage fingerprint review](../validation/2026-08-21-statuspage-fingerprint-review.md).
   The follow-up 2026-08-21 Zendesk review corrects the TXT observation from
   an unsupported apex `zendeskverification=` value to the documented
   `zendeskverification.<domain>` owner, dates the exact
   `mail.zendesk.com` SPF include and both `zendesk.com` CNAME roles, and
   leaves two unsupported broad forms undated with narrower claims. Detail:
   [2026-08-21 Zendesk fingerprint review](../validation/2026-08-21-zendesk-fingerprint-review.md).
   The next 2026-08-21 Tencent EdgeOne review adds the missing, documented
   `eo.dnse0.com` shard and dates exact current shard 0, 2, 3, and 5 examples.
   Shards 1 and 4 remain undated because no reviewed current first-party page
   names those exact forms. All six descriptions are narrowed to a routing
   relationship rather than traffic, feature, or configuration-state claims.
   Detail:
   [2026-08-21 Tencent EdgeOne fingerprint review](../validation/2026-08-21-tencent-edgeone-fingerprint-review.md).
   The 2026-08-30 Cloudflare review is complete at 1,112 catalog detections,
   157 dated, and zero stale dated rules. Detail:
   [2026-08-30 Cloudflare fingerprint review](../validation/2026-08-30-cloudflare-fingerprint-review.md).
5. Keep the completed stable-v1 characterization, structural-identifiability
   memo, v2.12 transition, and v2.13 capsule contracts blocking while this work
   proceeds. No catalog result reopens the voided fusion design or upgrades an
   observation into a population claim.
6. Preserve the frozen representative task, client, success, error, latency,
   discovery-byte, context-cost, portability, privacy, and stop-rule
   [contract](agent-portability-evaluation-declaration.md). GPT-5.6 Luna is the
   declared common model and $5 is the hard total external-charge ceiling.
   Collection remains deferred because account-side hard stops and a
   reproducible driver for all three required desktop clients were not
   verifiable. Resume the complete 30-session frame only when both gates are
   enforceable; do not shrink or substitute it. This measurement does not queue
   product work and does not change stable CLI, JSON, MCP wire, or OKF
   projection decisions. Detail:
   [2026-08-20 portability cost gate](../validation/2026-08-20-agent-portability-cost-gate.md).

### Apply the v2.11 result through v2.12 and v3

The fusion decision is not deferred to the final phase of the broader quality
plan. The v2.11 preflight established before collection that the frozen
promotion condition is structurally unreachable. v2.12 aligns product
positioning, documentation, and tests with non-promotion: fusion is an advanced
diagnostic. The runtime default cannot flip in a minor release because the
stability policy classifies that as breaking. ADR-0013 therefore preserves
implicit v2 behavior. A later amendment withdraws the interactive transition
notice: the default-off flip is not scheduled, so default runs stay silent.
Stable JSON fields, explicit CLI flags, and MCP tools remain unchanged.

The default-off switch is **not itself a scheduled milestone** (ADR-0013
amendment, 2026-08-18). The flip is claim-neutral: the identifiability finding,
re-confirmed by the 2026-08-17 adversarial corpus, means fusion adds no supported
claim the deterministic layer does not already make, so flipping it changes only
which of three diagnostic fields populate, not any emitted claim, and no shipped
consumer reads those fields from a default no-flag run. It is therefore deferred,
optional compatibility debt that rides a genuine contract-maturity major (the
claim/observation envelope) if one ships, and otherwise stays deferred behind the
stable flags. v2.16 also made MCP `lookup_tenant` JSON compute fusion
unconditionally, so a future flip is no longer CLI-only and must reconcile the
CLI-versus-MCP parity contract; see the ADR-0013 amendment.

### Separate observation change from interpretation change

The legacy delta path compares rendered snapshot outputs. v2.13 adds a separate
caller-owned capsule path without changing that stable shape. A catalog, model,
software version, normalizer, evaluation time, collection option, resolver
vantage, cache state, or source failure can change those outputs without a
public target-state change. Immediate degradation-aware suppression keeps
unavailable previous channels from becoming confirmed additions, unavailable
current channels from becoming confirmed removals, and dependent scalar
comparisons from proceeding without both observation opportunities. Exact
temporal semantics require replayable local observation capsules.

The shipped v2.13 release defines a caller-held capsule containing retained
raw DNS observations, normalized facts and snapshots, per-source opportunity
states, observation windows, a
frozen evaluation `as_of`, cache and vantage metadata, collection options,
software and normalizer versions, catalog and model digests, and a content
digest. Compare public observations by applying one frozen normalizer to both
raw capsules. Classify comparison results as observation, collection-regime,
time-evaluation, or interpretation deltas. Store stable signal identifiers
instead of reconstructing them from human-facing insight prose.

Shipped acceptance evidence:

- current v2 delta fields remain compatible and incomplete comparisons name the
  degraded sources and withheld changes;
- replaying the same capsule under the same version is deterministic apart from
  excluded render timestamps;
- replaying one capsule under a different explicit `as_of` produces only a
  time-evaluation delta and resulting freshness-state changes;
- replaying the same facts under different catalog or model versions creates
  interpretation deltas only;
- unavailable previous sources cannot create fact additions, unavailable
  current sources cannot create fact removals, and dependent scalar changes
  require both endpoint opportunities;
- every confirmed fact delta names comparable source roles and observation
  windows;
- storage remains local and caller-owned; monitoring and longitudinal retention
  require a separate privacy and architecture review;
- a decision memo either defers Open Knowledge Format v0.2 for lack of a named
  consumer or defines an additive projection whose `sources`, `generated`,
  `verified`, lifecycle, and freshness fields never upgrade the underlying
  claim. The structured capsule and recon JSON remain authoritative.

ADR-0014 takes the first disposition. The separate Draft 2020-12 capsule
schema, CLI guide, deterministic and adversarial tests, and local-only
retention boundary shipped after the full canonical, protected-main,
publication, provenance, and channel-parity gates passed.

### Prototype provenance-constrained claim robustness after the baseline

The advanced correlation thesis is not a narrower heuristic interval around one
committed posterior. It begins with separate Boolean must/may envelopes for
positive public support and authoritative public disconfirmation over explicit
evidence-removal, evidence-planting, dependence, and parameter assumptions. A
robust score envelope is secondary. Neither is a probability bound or
identification region. The formal proposal and promotion requirements are in
[correlation.md](correlation.md).

Start only after the priority 3 decision rule and evidence-unit taxonomy are
frozen. Classify units as provider-attested, functionally routing,
standards-declarative, administrative, historical structural, or derived. Make
manipulation costs claim-specific and expose them as assumptions. Scalar
budgets require a predeclared strictly positive additive cost for every
admissible nonidentity manipulation; identity has cost zero, and forbidden
actions are excluded or assigned infinite cost. Prefer Pareto or lexicographic
budgets over unlike action classes instead of summed ranks. Under either vector
budget, every nonidentity action has a componentwise nonnegative, nonzero cost
vector, and only identity has the zero vector. The first prototype remains an
advanced diagnostic and must not change the stable schema.

Acceptance evidence:

- Exhaustive enumeration and the optimized solver agree on bounded fixtures.
- Boolean positive and authoritative-negative must/may results are primary; a
  graded score never overrides a supported, disconfirmed, conflicted, or
  unresolved Boolean state.
- In the separately labeled forward-planting sensitivity, administrative-only
  additions cause zero transitions from initially unresolved or not-supported
  cases to supported at the predeclared support threshold.
- Every lower and upper bound names an attaining witness for the finite
  prototype, or an epsilon-optimal witness with a declared tolerance, plus the
  dependency unit, provenance path, threat model, and budget.
- Budget monotonicity, zero-budget collapse, dependency-unit invariance, and
  inverse compatibility-certificate replay pass as property tests. Separately
  named forward flip certificates also replay exactly.
- Bounded fixtures enumerate the complete primary inverse Boolean
  decision-flip antichain for the selected four-state decision. Secondary score
  lowering or raising antichains are named separately and never substitute for
  the Boolean family. Any forward deletion or addition sensitivity is also
  separately named and tested. A production cap carries an explicit
  `enumeration_complete=false` diagnostic rather than implying completeness.
- Where independent verification can exclude an observed-unit planting action,
  the prototype may report a minimum-cost conditional inspection set that
  intersects every selected adverse Boolean witness's verifiable observed-unit
  set. It must state that witness blocking depends on the favorable
  "confirmed genuine" outcomes and expose the verification-cost model as an
  assumption. If any witness has no such unit, the result reports that
  existing-fact verification cannot block all admitted adverse witnesses.
- Collector failure remains unobserved rather than becoming evidence of
  absence.
- The prototype beats deterministic evidence plus abstention on a predeclared
  operator outcome or is retired without reinterpretation.
- Probability or partial-identification language remains prohibited until a
  coherent normalized joint law over claims, full latent target state, and
  observation-process state, plus a possibly claim-dependent observation
  kernel, is specified and independently reviewed.

### Qualify or demote CT graph correlation before adding graph machinery

The current graph is a clique projection of certificate SAN sets. Its Louvain
edge weight is shared-certificate count; modularity is not a calibrated quality
score, and seed-sweep ARI does not measure sensitivity to missing or noisy CT
entries. Compare the current projection with fixed-total certificate weighting,
a certificate-host bipartite representation, or a native hypergraph view before
considering CPM, Leiden, or a stochastic block model.

Acceptance evidence:

- provenance, typed namespace topology, and inferred co-occurrence graphs remain
  separate objects;
- every cross-domain edge names its direction, roles, provenance, observation
  window, interaction class, and specificity class;
- Synthetic fixtures include heavy-tailed SAN counts, multi-tenant hub
  certificates, missing entries, and bridge noise.
- Operator-supplied grouping evaluations report pairwise false co-membership,
  precision, recall, ARI or variation of information, coverage, and abstention.
- Optimizer, data, and model stability are measured separately.
- A degree-aware null comparison is included.
- Hub-dominated, truncated, or data-unstable graphs abstain rather than emit
  relationship-looking connected components.
- cohort-local ubiquity filters use all eligible observation opportunities and
  disclose their denominator; capped output carries `enumeration_complete` and
  omitted edge or member counts before absence is interpretable;
- The simplest representation meeting predeclared quality and runtime budgets
  wins. No new dependency is added without a measured residual gap.

### Dimension public email posture without breaking compatibility

The current five-point value mixes sender-authentication declarations,
transport policy, branding, and observation presence. A proposed reporting
dimension would add DMARC aggregate reporting and TLSRPT, but reporting is not
part of the current score. Current standards give all of these different
semantics. Write an ADR for a dimensioned model:

- sender authentication declaration: DMARC, SPF, and observed DKIM;
- transport policy: validated MTA-STS mode and, only if feasible,
  DNSSEC-validated DANE;
- reporting: DMARC aggregate reporting and TLSRPT;
- brand presentation: BIMI;
- observation confidence and degraded-source state.

Audit RFC 9989 completion, including bounded DNS Tree Walk behavior and the
current meanings of `np`, `psd`, `t`, and historic `pct`. Treat an MTA-STS TXT
record as different from a valid enforcing HTTPS policy. Treat TLSRPT as
reporting, not enforcement. Give DANE credit only when the MX and TLSA data are
DNSSEC-secure. Keep the existing stable field as a compatibility view until a
versioned migration is approved.

### Evaluate modern standards-defined passive DNS surfaces

RFC 9460 SVCB and HTTPS records expose typed alternative endpoints and
connection parameters without opening a target connection. RFC 9848, published
in 2026, standardizes ECH configuration bootstrapping through those records.
SMTP DANE in RFC 7672 exposes authenticated transport policy only when the MX
and TLSA chain is DNSSEC-secure. These are plausible additions to recon's public
namespace model, not automatic fingerprint or security-score inputs.

Evaluate them after the product baseline and claim contract identify a named
operator outcome. Keep the first pass observational: priority, target name,
parameter keys, and DNSSEC state. Do not decode ECH configuration into product
identity, infer live protocol use, or make a connection attempt. DANE must
distinguish secure, insecure, bogus, and indeterminate DNSSEC results; raw TLSA
presence alone receives no transport-assurance claim.

Acceptance evidence:

- standards parsers have bounded positive, malformed, unknown-key, alias-loop,
  and hostile-size fixtures;
- every observation has owner, subject, source, time, and interaction semantics;
- no target connection or hidden direct probe is introduced;
- incremental classified-surface or operator value beats a DNS-type-presence
  baseline on a predeclared aggregate metric;
- unsupported product, protocol-use, and security-maturity conclusions remain
  impossible by construction;
- any stable output follows the additive schema gate and preserves older
  consumers.

### Add measured async and schema-interoperability characterization

Run representative synthetic single, batch, graph, and MCP workflows with
asyncio debug mode, an explicit slow-callback threshold, wall-time measurement,
and peak-allocation tracking. Classify each resolver path as async I/O, bounded
CPU, bounded local I/O, or justified offload. Move only measured blocking I/O
to `asyncio.to_thread` or a bounded executor, and do not thread non-thread-safe
DNS detector state.

Validate canonical MCP schemas with an independent JSON Schema 2020-12
validator. Do not rely on `format` as portable semantic validation, do not
resolve external schema references from the network, and keep schema depth,
size, and validation time bounded.

### Gate native acceleration on product-shaped evidence

Keep the default runtime and distribution pure Python under
[ADR-0010](adr/0010-evidence-gated-native-acceleration.md). Use the completed
stable-v1 stage characterization above, then measure Python-side improvements
to catalog loading, regex dispatch, repeated inference calculations, and any
other observed local hotspot. Do not infer end-to-end value from a kernel or
microbenchmark.

The first Python optimization pass is complete in v2.5.1. A bounded compiled
regex cache reduced the checked 1,000-value by 298-rule stage from 348 ms to
115 ms while preserving exact matches and catalog lifecycle behavior. One
batch-local Bayesian configuration snapshot reduced the checked 25-record
fusion stage from 864 ms to 355 ms without a process-global cache. CT stability
reuses its primary partition instead of recomputing one of the same eight
seeds. Hermetic retry and resolution tests plus file-grouped test workers cut
the measured full-suite wall time from 330.53 seconds serial without coverage
to 88.83 seconds with branch coverage. These are dated local diagnostics, not
product SLOs; [performance.md](performance.md) records the fixtures and limits.

The next optimization order is evidence-gated. The first item is complete in
v2.5.2:

1. Completed: split YAML remains canonical, one deterministic JSON runtime
   catalog is packaged, byte drift and exact ordered semantic equality are
   gated, and the 15-repetition Python 3.14.4 characterization measured a
   12.59-times median cold-load gain with 72.0 percent less traced peak
   allocation.
2. Characterize a batch-scoped SSRF-safe HTTP pool. Preserve request-specific
   timeouts, retries, cancellation, rebinding checks, CT policy, and degraded
   results before considering promotion.
3. Partially completed July 14, 2026: retained-output batch scheduling now uses
   a fixed input-ordered worker pool. At seven-way concurrency and the
   10,000-domain cap, a local one-off synthetic characterization created seven
   outer batch worker tasks instead of 10,000 eager outer tasks and reduced
   traced scheduling peak from 11,638,234 to
   480,232 bytes. The current batch path also bounds indexed ecosystem overlap
   and peer-list materialization, with known omission and unknown unfinished
   enumeration diagnostics. Keep the sparse, dense and permutation fixtures
   blocking before increasing concurrency. Summary-mode discarded rendering
   remains separate profiling work.

An optional Rust extension may enter an isolated prototype only when a stable,
deterministic, coarse-grained stage remains above 250 ms p95 on a representative
warm fixture or at least 20 percent of warm end-to-end p95 after a Python
optimization pass. These are conservative provisional governance floors, not
product SLOs; a clean-machine, stage-specific follow-up to the stable-v1
baseline must replace them with operation-specific budgets before a prototype.
They exclude microhotspots, require Amdahl-relevant
pressure, and demand enough improvement to repay native release maintenance.
Promotion requires at least a 3 times stage-p95 improvement
and also a 20 percent warm end-to-end p95 improvement, 25 percent sustained
batch-throughput improvement, or 30 percent peak-allocation improvement. It
also requires exact Python-reference parity, compiler-free installation on
every advertised platform, native quality gates, a multi-ecosystem SBOM,
reproducibility, provenance, and a visible Python fallback.

Do not add Go without an independently valuable hosted or worker boundary. Do
not add Mojo without a measured tensor, GPU, or accelerator kernel and a stable
cross-platform release contract. Neither exists in the current product.

### Turn catalog quality into the detection-improvement loop

Status: **shipped in v2.14; maintenance gate**. Future rounds still
freeze each contract before collection. The immutable contract names the question, independent input
stratum or frozen prior sample for drift, eligibility window, deduplication and
known-cluster unit, observation opportunities, CT and direct-probe settings,
catalog and code digests, aggregate outputs, promotion and regression budgets,
and disclosure review. A result may not retroactively change those choices.

The catalog currently holds 873 entries across 698 unique slugs, with 1,123
detections. The frozen classified-surface baseline that the promotion gate
measures against is 855 entries and 1,062 detections, recorded in
[the 2026-07-17 aggregate memo](../validation/2026-07-17-typed-catalog-baseline.md);
that number is a fixed reference point and does not move when the catalog does.
Establish stale-rule and independent-stratum baselines before adding broad new
families. Every promoted rule needs a current
public reference or disclosure-safe aggregate basis, a `verified` date,
positive and lookalike-negative fixtures, sparse-result wording, and provenance
tests. Prioritize regional and record-type gaps by aggregate frequency. Do not
add higher-order motifs until direct fingerprint quality is measured.

Use deduplicated, private rounds with distinct rank, regional, vertical,
vendor-seed, or drift questions. Before calling a round complete, account for
every bounded catalog record path as measured, unavailable, or not yet
instrumented. The opt-in maintenance envelope and private reducer now cover
CNAME chains, apex CNAME, non-SPF TXT, SPF targets, MX, NS, CAA, DMARC RUA,
bounded owner-qualified TXT, and bounded SRV observations. An empty queue is
not evidence of completeness. The unseen vertical holdout is complete without
post-holdout tuning. The independent rank round is complete. The regional
baseline and clean protected-main replay each completed all 1,000 rows, and the
aggregate-only
[result](../validation/2026-08-13-catalog-regional-round.md) records an accepted
fixed-observation decision for six documented provider families. The
[vendor-seed protocol](catalog-vendor-seed-round-declaration.md), bounded source
freezer, immutable receipt binding, fail-closed preparer, and evaluator are
implemented. Its provider source plan, receipt-bound dossier,
17,952-namespace exclusion union, and 33-row HubSpot frame produced the closed
aggregate-only [result](../validation/2026-08-14-catalog-vendor-seed-round.md):
29 corroborated, 4 observed-silent, no unavailable, unmeasured, or error
outcome, and no rule promotion. The 5,199-row prior-sample
[drift result](../validation/2026-08-14-catalog-drift-round.md) is also closed
with complete measurement, no threshold breach, one explicitly disclosed
catalog-driven measurement-surface change, and no rule promotion.
Evaluated apexes, organization names,
tenant identifiers, target-owned record values, and per-domain rows remain off
GitHub. Generic provider patterns, provider-owned references, reserved synthetic
fixtures, and disclosure-safe aggregates are the validation review surface.

For the regional round, freeze the exact raw IANA root-zone and UN M49 English
table responses before sampling. The derived mapping admits only exact ASCII
two-letter IANA country-code TLD and UN ISO-alpha2 matches in the five canonical
M49 regions; regionless M49 rows are counted and excluded. Publish only source,
mapping, frame, and implementation commitments before target contact. The
result remains a ccTLD-namespace comparison, not registrant geolocation or a
regional prevalence estimate.

The shipped v2.14 evidence order was rank bands, regional, vendor-seed, then drift. The
rank round is closed with a membership-bound four-band aggregate, four bounded
promoted families, explicit dispositions, and a fixed-observation
zero-regression decision in the aggregate-only
[rank-round result](../validation/2026-08-13-catalog-rank-round.md). The regional
baseline, fixed-observation disposition, and clean protected-main replay are
complete in the
[regional result](../validation/2026-08-13-catalog-regional-round.md). The
vendor-seed label, denominator, exclusions, disclosure boundary, bounded source
acquisition, immutable receipt binding, and fail-closed tooling are fixed in
the [public declaration](catalog-vendor-seed-round-declaration.md). Its exact
33-row [result](../validation/2026-08-14-catalog-vendor-seed-round.md) is closed
with no catalog promotion. A
provider relationship does not label publication of a particular DNS record,
so the reported measure is provider-level relationship corroboration, not
recall or a false-negative rate. The frozen-sample drift declaration and
protected-main result now bind and close the July baseline's 5,199 measured
rows, prior result, observation-only comparison fields, catalog and execution
digests, disclosure rule, measurement-surface disposition, and zero-promotion
decision. The convenience baseline and unseen vertical holdout remain
supporting evidence, not substitutes for those independent rounds. v2.14 was
complete only when every
frozen round has an aggregate result and every candidate has an explicit
promoted, rejected, deferred, unavailable, or unmeasured disposition. Those
evidence gates and the coherent v2.14.0 publication gate are complete.

Do not keep vendor-name-only proposals. A catalog candidate enters the backlog
only with an exact record type and pattern, a source or disclosure-safe
aggregate basis, an identifier, and an explicit pending, rejected, promoted, or
deferred disposition.

See [catalog-strategy.md](catalog-strategy.md).

### Simplify operator and agent discovery using measurements

Status: **maintainer track, not a version-path milestone; contract frozen,
portable candidate offline-validated, and three-client/runtime preflight
passed; model and cost envelope declared; paired collection deferred by the
frozen stop rule**.
(v2.16.0 shipped renderer parity, not this work.)

The network-free
[preregistration](agent-portability-evaluation-declaration.md) freezes three
listed clients, five representative tasks, native and portable package
variants, success and unsupported-claim measures, discovery and result bytes,
client-context treatment, launch and recovery behavior, privacy rules, and
stop rules. It pins the exact Agent Plugins and Agent Skills source revisions
and canonical schema digests. Its protected-main prerequisite passed. The
generated `agents/agent-plugin/` candidate preserves all 23 tools and both
skills, omits client-only and experimental frontmatter, and passes a
network-free canonical gate over the byte-pinned schemas, exact package layout,
launch shape, file bounds, path containment, version parity, and qualified claim
wording. Agent Plugins v1.0.0 is now Published; the canonical schema bytes still
match the pinned copies. This does not establish client compatibility or
conformance.

The first maintainer-local preflight remains historical stop evidence: Cursor
was unavailable and the selected recon 2.6.3 did not match candidate 2.14.0. A
second network-free preflight on 2026-08-20 passed with recon 2.17.4 and exact
versions observed for VS Code, Cursor, and Kiro. A later rerun passed with the
exact v2.17.5 candidate and the same client versions. Every preflight started
zero sessions. Passing preflight is environment readiness only and establishes
no client behavior.

GPT-5.6 Luna is the declared common model and $5 is the hard total
external-charge ceiling, split into planned $1.50, $1.50, and $2.00 client
sublimits. The collection stop rule applies because signed-in account hard
stops and a reproducible driver for all three required desktop clients could
not be verified from this environment. Published model rates do not establish
an enforceable cross-account ceiling. Zero model sessions started and external
spend is $0. The complete 30-session frame may resume only when both gates are
demonstrably enforceable; no sampling, client substitution, or compatibility
claim is allowed. Detail:
[2026-08-20 portability cost gate](../validation/2026-08-20-agent-portability-cost-gate.md).

Separate primary workflows from specialist workflows in documentation now.
Treat portable packaging as a separate axis from tool-list context cost. The
existing `agents/claude-code/` bundle uses Claude Code's native
`.claude-plugin/plugin.json` and `.mcp.json` layout; it is not a portable Agent
Plugins package.

The implemented candidate has root `plugin.json` and `mcp.json` documents
carrying the matching canonical schemas, immediate skill children under
`skills/`, and an explicit stdio transport. Generation from canonical skill sources and
independent offline validation are blocking in local and hosted CI. After a
passing three-client and runtime preflight, exercise install, discovery,
launch, failure reporting, and update behavior in the three frozen listed
clients. Preserve the native installers and Claude Code
bundle unless that portable path proves equivalent. Published v1.0.0 does not
by itself establish client behavior. Do not make an unqualified compatibility
or conformance claim, and do not let later specification work change the stable
CLI, JSON, or MCP contracts.

The dated CLI measurement is complete. Against the published v2.5.5 baseline,
native task panels reduce `lookup --help` from 154 to 109 lines at 80 columns
and from 261 to 180 lines at 60 columns. Every canonical option remains visible
at 80 columns, and the collection boundary moves from near the end into the
first half. The grouping changes presentation metadata only; all 28 options,
aliases, defaults, validation rules, and runtime paths remain unchanged.

Do not introduce a core-versus-advanced CLI mode. Grouping solves ordinary
widths without hiding specialist controls. The shipped fallback now selects
linear help below 70 columns, passes the actual terminal width through to the
formatter, preserves long option tokens and concise root summaries at 40, 60,
and 69 columns, and removes presentation markup from command prose. The
no-argument path uses indented command and description pairs at narrow widths.
This closes the measured accessibility debt without replacing the parser.

The dated pre-ReviewBundle MCP measurement is also complete. A real local stdio session on the
production SDK yields 81,562 compact serialized result-body bytes across
initialization, tools, resources, resource templates, and prompts. Counts
exclude JSON-RPC envelopes and transport framing. That frozen 22-tool listing
contributes 70,538 bytes, including 41,997 bytes of distinct output schemas. A
hypothetical seven-tool primary listing is 69.2 percent smaller, above the
predeclared 30 percent threshold, but that result-body reduction is not yet
evidence of model-context reduction in a representative client. The base MCP
protocol supports list pagination but no interoperable client-selected tool
filter.

Keep the complete stable tool surface as the default. Do not introduce a custom
core profile until a representative client proves material context benefit and
the design preserves direct specialist access. Use existing bounded catalog
parameters before reading the full catalog resource. Generated discovery
artifacts remain non-contractual under
[ADR-0007](adr/0007-surface-inventory-discovery-context.md) until a concrete
external consumer needs a stable subset.

### Reduce remaining interface hotspots after semantics stabilize

The 2026-07-14 measured audit found compatibility and facade navigation debt,
not general micro-file sprawl. Twenty-four 18-line compatibility shims account
for 18.0 percent of runtime Python files but 1.0 percent of runtime Python
lines. The 102 ordinary implementations have a 286-line median, only four are
at or below 50 lines, and 38 exceed 400 lines. The source tree is one package
level deep and has no import cycle. Do not perform a bulk merge, package move,
or minimum-file-size cleanup. Follow the boundary rules and staged ownership,
test, compatibility, runtime-package, and hotspot plan in
[structural-maintainability.md](structural-maintainability.md).

The high-trust graph identifies two high interface decomposition candidates:

- `src/recon_tool/formatter/panel.py`: high blast radius, broad outgoing
  dependency surface, and a special file-size ratchet;
- `src/recon_tool/server/introspection.py`: high blast radius, broad
  dependency and incoming-reference surface, plus framework registration
  behavior.

Read the current ignored code-graph manifest, impact records, and hotspots for
exact counts rather than copying volatile graph metrics into this roadmap.
The current critical MCP orchestration files are `server/app.py` and
`server/__init__.py`; treat those as high-risk shared boundaries even though
they are not the decomposition targets named above.

Keep each public module as a compatibility orchestrator and extract only
cohesive, stateless sections. Preserve byte-equivalent panel output, MCP
registration order, generated inventory, public imports, and schema behavior.
Do not split decorated MCP tools one by one. `merger.py` follows only after the
lower-risk interface splits. Before source movement, publish a durable
source-to-focused-test ownership map and redistribute the five measured
catch-all test suites into existing behavior owners.

## Shipped Foundation

The following are maintenance concerns, not active feature projects:

- Package-local CLI, formatter, MCP server, and MCP client boundaries, guarded
  by [ADR-0008](adr/0008-interface-package-locality.md) and interface-layout
  checks.
- Typed `LookupOptions` at the CLI boundary.
- Raw-preserving compact caps for the named high-volume MCP graph and
  correlation tools.
- Bounded config, cache, delta, CT, regex, and formatting-control readers.
- Scheduled provider-drift checks, generated schema and surface-inventory
  checks, release readiness, Trusted Publishing, provenance, external SBOM,
  and reproducible-build verification.
- RFC 9989 parser and scoring work already recorded in the changelog. The
  remaining work is a completion audit against the final standard, not a claim
  that the protocol is entirely implemented.

Detailed shipped records are in [CHANGELOG.md](../CHANGELOG.md),
[roadmap-history.md](roadmap-history.md), and the ADR index.

## Publication and Process Track

The external write-up, claim freeze, OpenSSF Best Practices questionnaire,
outside replication, and archive or DOI decision are legitimate maintainer
projects. They do not outrank product truthfulness, compatibility, measured
utility, catalog quality, or operator usability.

The write-up remains governed by
[external-writeup-plan.md](external-writeup-plan.md),
[paper-claim-map.md](paper-claim-map.md), and
[submission-freeze-checklist.md](submission-freeze-checklist.md). Public-list numbers remain robustness checks rather than population rates. M365 tenancy
evidence remains corroboration rather than independent calibration. The latest
local proof record is
[2026-06-30-submission-freeze-local-proof.md](../validation/2026-06-30-submission-freeze-local-proof.md).

The current review and external-event boundaries are in
[strategic-gap-audit.md](strategic-gap-audit.md),
[artifact-review.md](artifact-review.md),
[public-label-snapshot-decision.md](public-label-snapshot-decision.md),
[m365-tenancy-decision.md](m365-tenancy-decision.md),
[replication-runbook.md](replication-runbook.md), and
[archive-readiness.md](archive-readiness.md).

## Success Metrics

The product-quality baseline that was to set dated values for these was stopped
before target collection (the arms collapse, so its promotion gate is
structurally unreachable; see track 3). These therefore remain the metrics a
future measured study would report, not a scheduled deliverable, and green
process gates are necessary but are not proof of product utility. The roadmap
tracks at least:

- unsupported default claim rate;
- abstention and unresolved rate by claim family;
- independently corroborated precision where a suitable reference exists;
- explanation and provenance completeness;
- claim-contract coverage, minimal-certificate replay, and abstention-reason
  completeness for material default claims;
- observation-versus-interpretation delta replay stability;
- typed graph enumeration completeness and eligible-denominator disclosure;
- classified share of the observable record surface and stale-rule count;
- cold and warm p50/p95 latency, peak allocation, timeout, and degraded-source
  rate;
- marginal CT signal gain relative to latency cost;
- MCP discovery bytes and representative workflow context cost;
- portable Agent Plugins offline schema and package validation, followed by
  client-specific discovery, launch, install, update, and failure evidence;
- deterministic CLI, JSON, and MCP behavior;
- the enforced 90.2 percent branch-aware project gate, above the 80 percent user
  bar, with no coverage regression;
- green local and remote CI, reproducible artifacts, and release provenance.

## Invariants

These are the properties every track above must preserve. They change only
through an ADR, never as a side effect of feature work, and most of the
acceptance evidence in this document exists to keep them true. Each group names
the mechanism that enforces it, so a reviewer can check rather than trust.

**Collection boundary.** Enforced by
[ADR-0001](adr/0001-passive-zero-credential.md),
[ADR-0011](adr/0011-public-metadata-collection-boundary.md), and the transport
and resolver tests.

- Public metadata only: DNS, certificate transparency, unauthenticated identity
  discovery, and the documented standards-compliant MTA-STS policy fetch.
- Google CSE and BIMI certificate fetches remain explicit opt-in direct probes
  and never run in a default lookup.
- No credentials, API keys, paid feeds, port scanning, exploit checks, or
  target application crawling.

**Claim discipline.** Enforced by claim contracts, golden output fixtures, and
the regression guards named under priority 1.

- A domain is a query coordinate. It is not an organization, owner, account
  operator, corporate group, or deployed product.
- Observations are hedged and provenance-bearing. Sparse or degraded evidence
  lowers confidence and may require abstention; an unresolved answer is a
  correct answer.
- A source failure is an unavailable channel, never a negative observation, and
  never evidence of absence.
- Parent-platform presence never becomes a child-product licensing, enablement,
  deployment, or use claim. Missing metadata, including sovereignty metadata,
  stays unknown rather than defaulting.
- Exact observed overlap in shared administrative tokens, tenant identifiers,
  issuers, or certificate names does not become an ownership or control verdict.
- A public-evidence index is never presented as overall security maturity.

**Data handling.** Enforced by
[data-handling-policy.md](data-handling-policy.md) and the validation-hygiene
gate in `scripts/check_validation_hygiene.py`, which runs locally and in the
release path.

- No runtime aggregate database. No real-target corpus or per-domain rows are
  committed or published; maintainer-local validation data stays in the
  permanently ignored workspaces defined by the data-handling policy.
- All current evaluated-target examples use explicit synthetic identities under
  reserved namespaces; public validation artifacts are otherwise
  aggregate-only.

**Surface stability and bounds.** Enforced by
[stability.md](stability.md), [ADR-0003](adr/0003-v2-schema-lock.md), and the
generated-artifact drift gates.

- Stable CLI, JSON, MCP, cache, and import surfaces change only through their
  documented compatibility discipline.
- Bounded network, parser, cache, schema, and output behavior.
- A clean root, canonical docs in `docs/`, source in `src/`, logs in ignored
  `logs/`, and agent work only in ignored `.agent/`.

## Intentionally Not Doing

- Active scanning, port enumeration, vulnerability or exploit testing.
- Credentialed tenant or SaaS enumeration.
- A project-operated public endpoint, SaaS, or multi-tenant service. The
  optional references are operator-owned deployments only.
- Per-user OAuth or additional provider implementations without the named
  consumer, threat model, identity context, and validation gates in the
  optional cloud plan.
- Company ownership, firmographics, news, financial, or hiring inference.
- Security verdicts, certifications, confirmed-vulnerability claims, or claims
  about controls that are not publicly observable.
- Speculative dependencies, abstraction layers, scoring dimensions, or
  fingerprint grammars without measured pressure.
- Publication process as a substitute for product-quality evidence.

## Current External Basis

Checked through 2026-08-30 UTC against primary sources and recent research:

- [Agent Plugins v1.0.0 Published specification](https://agent-plugins.org/specification)
- [Agent Plugins compatible clients](https://agent-plugins.org/compatible-clients)
- [Agent Skills specification](https://agentskills.io/specification)
- [Open Knowledge Format v0.2 specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
- [Google Cloud OKF v0.2 trust-signals announcement](https://cloud.google.com/blog/products/data-analytics/okf-v0-2-adds-trust-signals/)
- [Google Cloud OKF announcement, which describes the superseded v0.1 form](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing/)
- [IANA Root Zone Database](https://www.iana.org/domains/root/db)
- [UN M49 standard country or area and geographic-region codes](https://unstats.un.org/unsd/methodology/m49/overview/)
- [MCP 2026-07-28 release candidate](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)
- [MCP current documentation](https://modelcontextprotocol.io/docs/getting-started/intro)
- [MCP Python SDK release history](https://pypi.org/project/mcp/)
- [Google Workspace current MX setup (`smtp.google.com`, legacy `aspmx.*` still supported)](https://knowledge.workspace.google.com/admin/domains/set-up-mx-records-for-google-workspace)
- [Microsoft 365 external DNS records (current Learn page still names `mail.protection.outlook.com`)](https://learn.microsoft.com/en-us/microsoft-365/enterprise/external-domain-name-system-records)
- [TrendAI Email Security domain configuration](https://docs.trendmicro.com/en-us/documentation/article/trend-micro-email-security-online-help-configuring-a-domain)
- [TrendAI Email Security SPF records](https://docs.trendmicro.com/en-us/documentation/article/trend-micro-email-security-online-help-adding-spf-records)
- [Barracuda Email Gateway Defense MX configuration](https://documentation.campus.barracuda.com/wiki/spaces/EGD/pages/2850986)
- [Cisco Secure Email Cloud Gateway hostnames](https://docs.ces.cisco.com/docs/hostnames)
- [Amazon SES endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/ses.html)
- [Amazon SES custom MAIL FROM domain](https://docs.aws.amazon.com/ses/latest/dg/mail-from.html)
- [Google Workspace SPF setup](https://support.google.com/a/answer/33786)
- [Akamai Property Manager hostname mapping](https://techdocs.akamai.com/property-mgr/reference/modify-property-hostnames)
- [Cloudflare DNS nameserver formats](https://developers.cloudflare.com/dns/nameservers/)
- [Cloudflare partial-zone verification and CNAME targets](https://developers.cloudflare.com/dns/zone-setups/partial-setup/setup/)
- [Cloudflare Pages custom-domain targets](https://developers.cloudflare.com/pages/configuration/custom-domains/)
- [Cloudflare China Network DNS targets](https://developers.cloudflare.com/china-network/concepts/china-dns/)
- [HubSpot email authentication](https://knowledge.hubspot.com/marketing-email/manage-email-authentication-in-hubspot)
- [HubSpot Domains API guide](https://developers.hubspot.com/docs/api-reference/legacy/cms/domains/guide)
- [Adobe Marketo Engage setup steps](https://experienceleague.adobe.com/en/docs/marketo/using/getting-started/initial-setup/setup-steps)
- [Adobe Marketo Engage protocol configuration](https://experienceleague.adobe.com/en/docs/marketo/using/getting-started/initial-setup/configure-protocols-for-marketo)
- [Salesforce Marketing Cloud Engagement allowlist endpoints](https://help.salesforce.com/s/articleView?id=mktg.mc_es_ip_addresses_for_inclusion.htm&language=en_US&type=5)
- [Salesforce Marketing Cloud stack locations](https://help.salesforce.com/s/articleView?id=000383566&language=en_US&type=1)
- [Salesforce Marketing Cloud tenant-specific endpoints](https://developer.salesforce.com/docs/marketing/marketing-cloud/guide/your-subdomain-tenant-specific-endpoints.html)
- [Salesforce Marketing Cloud CloudPages endpoint transition](https://help.salesforce.com/s/articleView?id=000389721&language=en_US&type=1)
- [AWS Network Load Balancer DNS names](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/network-load-balancers.html)
- [AWS Application Load Balancer DNS names](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/application-load-balancers.html)
- [AWS Elastic Load Balancing regional endpoints](https://docs.aws.amazon.com/general/latest/gr/elb.html)
- [AWS China Application Load Balancer DNS names](https://docs.amazonaws.cn/en_us/elasticloadbalancing/latest/application/application-load-balancers.html)
- [RFC 9989: DMARC](https://www.rfc-editor.org/info/rfc9989/)
- [RFC 3986: URI generic syntax](https://www.rfc-editor.org/info/rfc3986/)
- [RFC 2308: DNS negative caching](https://www.rfc-editor.org/rfc/rfc2308)
- [RFC 4035: authenticated DNSSEC denial](https://www.rfc-editor.org/rfc/rfc4035#section-5.4)
- [RFC 9824: compact DNSSEC denial](https://www.rfc-editor.org/rfc/rfc9824)
- [Provenance semirings](https://web.cs.ucdavis.edu/~green/papers/pods07.pdf)
- [RFC 8461: MTA-STS](https://www.rfc-editor.org/info/rfc8461/)
- [RFC 8460: TLSRPT](https://www.rfc-editor.org/info/rfc8460/)
- [RFC 7672: SMTP security via DANE](https://www.rfc-editor.org/info/rfc7672/)
- [Python asyncio development guidance](https://docs.python.org/3.14/library/asyncio-dev.html)
- [Python free-threading guidance](https://docs.python.org/3/howto/free-threading-python.html)
- [PyO3 free-threading guidance](https://pyo3.rs/main/free-threading)
- [PyO3 ABI feature guidance](https://pyo3.rs/main/features)
- [Maturin distribution guidance](https://www.maturin.rs/distribution.html)
- [Mojo versioning and stability FAQ](https://docs.modular.com/mojo/faq)
- [JSON Schema 2020-12 validation](https://json-schema.org/draft/2020-12/json-schema-validation)
- [Manski on partial identification with missing data](https://doi.org/10.1016/j.ijar.2004.10.006)
- [Zhang and Peixoto on statistically significant community structure](https://arxiv.org/abs/2006.14493)
- [Conformal Risk Control, revision 2025-06-13](https://arxiv.org/abs/2208.02814)
- [DORA State of AI-assisted Software Development 2025](https://dora.dev/research/2025/dora-report/)
- [Google small change guidance](https://google.github.io/eng-practices/review/developer/small-cls.html)
- [Google code review guidance](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
- [ISO/IEC 25010:2023 product quality model](https://www.iso.org/standard/78176.html)
- [ISSRE 2025 study of human and AI-generated code](https://arxiv.org/abs/2508.21634)
- [Post-hoc software models for AI-driven engineering, revised 2025-11-11](https://arxiv.org/abs/2511.02475)

When an external standard changes, update the dated readiness or design plan
before changing production behavior.
