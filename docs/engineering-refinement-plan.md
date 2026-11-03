# Engineering Refinement Plan

Status: active implementation plan; v2.16 shipped, the engine is
feature-complete, and the standing work is the fingerprint-freshness loop. The
v2.15 representative-client preflight remains parked on client availability.
Review date: 2026-08-18

This plan translates the canonical [roadmap](roadmap.md) into bounded
engineering tracks. It does not authorize unrelated runtime expansion. Every
track preserves the public-metadata-only boundary in
[ADR-0011](adr/0011-public-metadata-collection-boundary.md), adversarial missing-data
discipline in [ADR-0002](adr/0002-mnar-adversarial-absence.md), and stable v2
contract discipline in [ADR-0003](adr/0003-v2-schema-lock.md).

Default collection performs no active scanning or port probing. Authoritative
DNS may observe recursive-resolver traffic, MTA-STS is the only default
target-owned HTTP/application request, and the documented Google CSE and BIMI
certificate requests are explicit opt-in direct probes.

## Baseline

- Release metadata is synchronized on v2.27.1. Publication status requires
  separate remote verification of the exact tag, GitHub Release, PyPI files,
  attestations, SBOM, CI, and channel hashes; a version bump is not evidence.
- Local release readiness must pass before tagging; remote release readiness
  must pass for the same commit after publication.
- Meaningful branch-aware coverage is above 90.2 percent, which is now the
  blocking baseline ratchet and remains above the 80 percent user bar.
- The ignored local code graph must be refreshed after each tracked milestone.
  Read `.agent/codegraph/manifest.json` for its exact build commit, trust level,
  checks, and counts rather than copying volatile metrics into this plan.
- Interface locality, typed lookup options, named high-volume MCP caps,
  generated schema and surface guards, provider-drift checks, and release
  provenance are shipped.

Graph trust is high, not absolute. Runtime registration, dynamic dispatch,
reflection, monkeypatching, and framework behavior must still be verified with
source and tests before a wide change.

## Decision Filter

Accept work when it does at least one of these:

- Corrects a claim that is stronger than its public evidence.
- Proves compatibility with an imminent external standard or dependency.
- Establishes a reproducible user-value or reliability measure.
- Reduces cognitive load or blast radius in a measured hotspot.
- Improves catalog quality, provenance, degradation behavior, or deterministic
  output without weakening sparse-result honesty.

Defer work that mainly adds abstraction, dependencies, protocol surface,
inference layers, or catalog entries without a named consumer, measured gap,
or failing guard.

## Track 1: Evidence-Semantic Integrity

Status: complete maintenance gate; live MCP boundary, score wording, and parent-platform
child-product inference corrected in v2.4.0; provider summaries now share
one evidence-aware derivation across output surfaces; Markdown service labels
now cross one escaped output boundary and use mutually exclusive provider
groups; confidence scoring now has a dedicated module with distinct-source,
canonical-claim aggregation and winning-claim provenance; the first bounded
internal claim contract is implemented for exact apex DMARC `p=reject`
Dependencies: none
Risk: high product-trust risk, high compatibility sensitivity

Default panel and MCP text assembly now preserve the queried namespace as the
subject coordinate and derive panel-only workload summaries only from
collection-observable evidence. Service labels, posture observations,
hardening guidance, and every weighted exposure-index component now retain
exact generation-time basis. Comparisons carry both namespace ledgers, and
simulations distinguish hypothetical from live component values. All 28
default-claim families, including the aggregate cohort-summary contract, are
complete. The static agent and MCP reviews now pin
process scope, collection boundaries, output forms, and abstention semantics.

### Scope

1. Inventory material claims emitted by the default panel and primary MCP
   workflows.
2. Classify each claim as directly observed, derived from a documented rule,
   defined public absence, or unresolved.
3. Keep the completed parent-platform child-product regression guard green.
   The live MCP collection-boundary instructions and model-bound score wording
   were the first completed corrections. Preserve and test the existing
   behavior that keeps absent sovereignty metadata unknown.
4. Preserve current stable JSON names while correcting presentation and
   inference semantics.
5. Build one narrow machine-enforced internal claim contract and
   observation-opportunity ledger before benchmark enrollment or a scored
   robustness solver. Include positive and authoritative-negative alternatives,
   unavailable and observed-empty opportunities, dependency units, four-state
   output, time semantics, and renderer obligations.
   Completed after v2.4.0 as `dns.dmarc.valid_policy_is_reject.v1`; empty and
   invalid DNS observations remain unresolved because the current adapter does
   not retain authority or authenticated-denial provenance. Opt-in in-core
   schema 2.2 consumes transient claim-state and effective-policy projections;
   schema 2.1 remains the default and tenant JSON remains unchanged.
6. Draft a provenance-envelope ADR before changing `EvidenceRecord` or public
   schemas. The ADR must define source family, record owner, observation time,
   scope, and freshness semantics, plus migration and cache behavior.

### Graph and test guidance

- `models.py` is deceptively central, with a large high-confidence import and
  cross-file call surface in the current graph.
- `merger.py` has high blast radius and contract risk.
- Consult `impact.jsonl`, `edges.jsonl`, `refs.jsonl`, and `checks.json` before
  touching either file, and take exact counts from the current ignored graph
  rather than this tracked plan.
- Likely tests include panel golden and disclosure tests, cache round trips,
  schema contracts, explanation DAGs, staleness timestamps, MCP structured
  output, server instructions, generated agent guidance, and merger tests.

### Acceptance

- Every default material claim has a direct provenance path.
- Sparse output contains no inferred child-product use from parent-platform
  presence.
- Unknown sovereignty metadata remains unknown.
- Public-evidence values are not described as overall security scores.
- The first claim contract passes positive, explicit-disconfirming, conflict,
  unavailable, empty, invalid, stale, time-unknown, duplicate-derivation,
  cross-view conjunction, exhaustive-oracle, and fail-closed bound fixtures;
  its certificate antichains map every derivation to canonical dependency
  units.
- Stable JSON remains compatible unless an additive change completes the full
  schema-lock process.
- Full local CI passes with no coverage regression.

### Stop rule

Do not combine this work with a broad model, schema, or interface refactor.
Correct the smallest evidence-to-claim path first.

## Track 2: MCP 2026-07-28 Compatibility Matrix

Status: adopted 2026-07-31; stable v1.28.1 remains the tested rollback pin
Dependencies: none; this stream can proceed independently of Track 1
Risk: dependency and protocol compatibility

The exact stable v1.28.1 and stable v2.0.0 environments pass the full isolated
matrix. Production uses `mcp>=2.0.0,<3`; both exact pins remain blocking so the
rollback line is continuously verified.

### Scope

- Test server import, stdio startup, doctor, discovery, representative tool
  calls, resource reads, error behavior, structured content, schemas, and
  deterministic order on stable v1.28.1 and stable v2.0.0.
- Record an explicit migration decision for `FastMCP`, protocol type imports,
  `ToolError`, annotations, snake-case SDK attributes, `discover()`, and
  `model_dump(by_alias=True)` where required on the wire.
- Review synchronous resource handlers and shared catalog or cache state under
  v2 worker-thread execution.
- Give every complete `server/discover`, `tools/list`, supported resource-list,
  and resource-read response valid `ttlMs` and `cacheScope` hints. Record a
  disposition for every other cacheable operation exposed by the server.
- Keep the corrected `mcp>=1.28.1` floor enforced in the compatibility job.
- Keep stdio as the supported surface. Do not add remote transport or unused
  extensions.

### Acceptance

- A dated matrix records pass, fail, migration action, and rollback pin.
- The current production path stays green throughout the spike.
- Tool and resource inventories remain deterministic.
- Declared output schemas conform to JSON Schema 2020-12 and returned
  structured content conforms to those schemas.
- Required caching hints are present and valid on every complete cacheable
  result recon exposes under the draft 2026 protocol.
- Full gates pass before any dependency-range change.

Detailed phases are in
[mcp-2026-07-28-readiness.md](mcp-2026-07-28-readiness.md).

## Track 3: Product-Quality Baseline and Ablation

Status: v2.11 structural stop and v2.12 compatibility transition complete
Dependencies: Track 1's first machine-enforced claim contract and
observation-opportunity ledger
Risk: measurement-design and disclosure risk

### Scope

Build one reproducible, aggregate-safe scorecard with synthetic fixtures and
maintainer-local real-domain evaluation. Record only disclosure-reviewed
aggregates.

Metrics:

- independently corroborated precision by claim family where a suitable label
  exists;
- unsupported claim, false-confidence, abstention, and unresolved rates;
- explanation and provenance completeness;
- classified share of observable record values and stale-rule count;
- degraded-source and partial-result rates;
- p50/p95 cold and warm latency and peak allocation;
- marginal CT signal gain and latency cost;
- MCP discovery bytes and representative workflow result bytes.

The resolver latency, allocation, CT-value, and current-schema measurements are
produced by Track 5's stable-v1 characterization and consumed by this scorecard;
they are not measured twice.

Run a predeclared ablation with four distinct arms: deterministic evidence plus
explicit abstention, per-slug evidence strength, the strongest reviewed evidence
unit, and the current Bayesian network. Freeze the decision rule before the run.
Do not tune it after seeing the result.

Primary design:

- Operator decision: accept one material single-domain claim as supported by
  the public channel, or leave it unresolved.
- Unit: one frozen row per domain for one predeclared claim family. Admit at
  most one domain from each known administrative, ownership, or tenant cluster
  in the primary analysis. This makes the domain row the Bernoulli unit used by
  the paired decision rule. Treat any clustered multi-domain analysis as
  secondary until it defines a cluster-level estimand, outcome, and decision
  rule. Keep groups intact across parameter development and evaluation.
- Sampling model: name the target population, eligibility window,
  stratum-specific sampling frames, and sampling mechanism before collection.
  Population interpretation of binomial bounds and power requires independent
  exchangeable units within strata after known-cluster exclusion, or a
  probability design with matching design-based inference. A fixed or
  purposively selected corpus yields only an empirical corpus effect; its
  binomial bounds are model-based and cannot support population promotion.
- Independent labels: provider-owned endpoints, standards-defined records, or
  other predeclared authoritative sources not consumed by the compared
  predictor. Unlabeled families report coverage and corroboration diagnostics,
  not precision.
- Minimum: 100 independently labeled primary sampling units, including at least
  30 reference-positive and 30 reference-negative units. Run a power analysis
  under the exact paired rule and plausible discordances before collection.
  Supported-emission count governs whether selective risk is estimable, not
  primary-gate eligibility.
- Evaluation: reference-positive support rate and reference-negative
  unsupported-emission rate are co-primary. Report abstention, tie-preserving
  reliability, selective risk versus coverage, provenance completeness,
  latency, and allocation as secondary measures. Report Brier and log score
  only for an arm whose total frozen forecast is explicitly interpreted as
  `P(reference-positive | frozen inputs)` on every eligible two-class row and
  has a predeclared abstention convention. An evidence-strength score qualifies
  only after its mapping is fitted on disjoint development data and frozen.
  Otherwise omit proper-score comparison or label a plug-in loss descriptive.
- Weighting: if label strata are sampled at different rates, pooled abstention,
  unresolved, overall emission, proper scores, reliability, and selective risk
  require known inclusion probabilities and frozen design or
  post-stratification weights for the target population. Otherwise report
  stratum-specific or fixed-sample descriptive values without a population
  rate or calibration claim.
- Go or no-go: within each label stratum, use conservative one-sided 95 percent
  bounds on candidate-only minus baseline-only support from
  Bonferroni-adjusted Clopper-Pearson discordance bounds. Fusion remains primary
  only when the positive-stratum benefit lower bound exceeds zero, the
  negative-stratum safety upper bound is below a predeclared positive absolute
  noninferiority margin, and the candidate introduces no unsupported emission
  on a negative unit left unresolved by the baseline. Inconclusive or negative
  results move fusion to an advanced diagnostic. Bootstrap intervals remain
  secondary and cannot rescue the gate.

### Acceptance

- A dated method, environment, reproduction command, result memo, and
  regression-budget proposal exist.
- Per-unit rows may exist only in the permanently ignored
  `validation/runs-private/` or `validation/local/` workspaces. They are never
  committed or published. Each run uses the ignored manual `RETENTION.md`
  control defined in `maintainer-validation.md` and removes superseded rows
  when they no longer support a reviewed aggregate memo or named longitudinal
  comparison.
- A negative or mixed result is recorded without relabeling it as success.
- Each proposed inference, source, graph, or catalog change names a target
  metric before implementation.

Dependency-ordered work around this decision:

- Before benchmark enrollment or any scored solver, build one internal
  machine-enforced claim contract and observation-opportunity ledger. Require
  separate positive and authoritative-negative certificate antichains,
  explicit opportunity atoms, dependency groups, four-state output,
  duplicate-derivation invariance, and incomplete-provenance diagnostics.
- After the first contract is stable, define a caller-held observation capsule
  and separate observation, collection-regime, time-evaluation, and
  interpretation deltas before statistical temporal modeling.
- Prototype provenance-constrained Boolean must/may robustness in
  [correlation.md](correlation.md) behind an advanced-only surface. Prefer
  Pareto or lexicographic budgets across unlike manipulation classes. Keep any
  robust score envelope secondary. Require finite-prototype witnesses or
  declared epsilon-optimal witnesses, minimal inverse and forward certificates,
  and exact agreement on bounded fixtures. Promote it only if it beats
  deterministic abstention on a predeclared operator outcome.
- Qualify the CT graph by comparing its clique projection with fixed-total
  certificate weighting and bipartite or hypergraph representations. Separate
  seed, data, and model stability; include a degree-aware null and heavy-tailed
  multi-tenant fixtures. Do not add a graph dependency before a simpler method
  leaves a measured residual gap.

## Track 4: Dimensioned Email Observations

Status: deferred pending measured evidence after the active catalog phase
Dependencies: Tracks 1 and 3
Risk: stable-contract and user-interpretation risk

Write an ADR before implementation. Separate:

- sender-authentication declarations;
- transport policy;
- reporting configuration;
- brand presentation;
- observation confidence and degraded-source state.

Complete an RFC 9989 behavior audit. Distinguish MTA-STS record presence from a
valid `enforce` policy, TLSRPT reporting from transport enforcement, and BIMI
from authentication. Evaluate DANE only as a bounded feasibility design; any
credit requires DNSSEC-validated MX and TLSA data. Preserve the existing
five-point field as a compatibility view until a versioned migration is
approved.

### Acceptance

- An accepted ADR defines the dimensions, compatibility view, evidence
  requirements, and migration boundary.
- An RFC 9989 matrix covers record discovery, supported tags, historic `pct`,
  malformed records, and bounded-query behavior.
- MTA-STS, TLSRPT, BIMI, and any DANE proposal receive only their
  standards-supported semantics.
- The DANE feasibility step records an explicit implement or defer decision;
  no credit is possible without DNSSEC-validated MX and TLSA data.
- Existing stable JSON remains unchanged unless the schema-lock process closes.

## Track 5: Measured Async and Schema Interoperability

Status: stable-v1 characterization and stable-v2 compatibility deltas complete;
clean-machine stage budgets remain future evidence
Dependencies: none for resolver and current-schema baselines; stable-v2 deltas
are available from the completed Track 2 matrix
Risk: concurrency and brittle-benchmark risk

### Scope

- Run representative synthetic single, batch, graph, and MCP calls with
  asyncio debug mode and an explicit slow-callback threshold.
- Record wall time, peak allocations, and blocked-loop observations. Treat
  profiler output as characterization, not a brittle CI timing assertion.
- Record cold CLI startup and separate catalog loading, fingerprint matching,
  inference, graph construction, serialization, and rendering before proposing
  a language boundary.
- Classify each resolver-reachable call as async I/O, bounded CPU, bounded
  local I/O, or justified offload.
- Move only measured blocking I/O to `asyncio.to_thread` or a bounded executor.
- Apply Python algorithm, caching, and allocation improvements before any
  optional native prototype. Use the promotion gates in ADR-0010.
- Validate canonical schemas with an independent Draft 2020-12 validator.
- Reject external network resolution for schema references, reliance on
  `format` as semantic validation, and unbounded schema depth or validation
  time.

### July 12, 2026 checkpoint

- Kept the runtime and universal wheel pure Python with support for Python 3.11
  through 3.14. Python 3.14 is preferred for development and measurement, not
  required for correct behavior.
- Replaced repeated module-level catalog regex dispatch with a strictly bounded
  compiled-pattern cache and exact invalidation on catalog generation changes.
- Replaced repeated built-in YAML parsing with one deterministic generated JSON
  runtime artifact. Split YAML remains canonical source and sdist content;
  exact drift, ordered semantic parity, and a 12.59-times Python 3.14.4 median
  cold-load gain are checked evidence.
- Loaded Bayesian model and prior configuration once per fusion-enabled batch,
  with a coherent batch-local snapshot and no cross-invocation global cache.
- Removed one duplicate Louvain partition while retaining the exact primary
  partition, eight-seed stability statistic, and deterministic output.
- Removed live resolution and real retry delays from unit tests while asserting
  exact retry schedules and no-I/O invalid-input behavior.
- Validated four-worker file-grouped full-suite execution with combined branch
  coverage. The complete OS and Python compatibility matrix remains intact.
- Deferred connection-pool reuse and bounded cross-domain correlation until
  their named product-shaped measurements exist.

### July 14, 2026 bounded scheduling checkpoint

- Replaced retained-output `gather` fan-out with a fixed outer worker pool that
  creates at most the requested concurrency in batch worker tasks and restores
  input order. Each admitted lookup retains its own bounded internal tasks.
- Preserved the separate NDJSON completion-order scheduler, all public output
  shapes, per-domain progress outcomes, error, enrichment, and cancellation
  behavior. Later inputs are admitted as workers become available, so progress
  timing can differ from the eager fan-out implementation.
- At seven-way concurrency and 10,000 synthetic inputs, task creation fell from
  10,000 to seven and traced scheduling peak fell from 11,638,234 to 480,232
  bytes. These are local allocation diagnostics, not throughput or latency SLOs.
- Kept summary-mode shaping and dense cross-domain correlation as the next
  bounded batch work rather than combining unrelated changes into this pass.

### Acceptance

- A dated performance artifact records the environment and stage measurements.
- Cancellation, aggregate timeout, and partial-result behavior remain intact.
- Non-thread-safe DNS detector state is never moved across threads.
- Compact MCP modes retain deterministic caps, omitted counts, and raw parity.
- Every changed path has a regression test or a documented no-change result.
- Stable-v1 resolver and schema measurements remain separately reproducible
  from v2-specific compatibility deltas.

## Track 6: Catalog Quality and Lifecycle

Status: shipped in v2.14; maintenance gate. Rank, regional,
vendor-seed, and prior-sample drift rounds are closed with aggregate results
and explicit dispositions
Dependencies: Track 3 measurement definitions
Risk: false-positive and regional-selection bias

- Measure classified surface by record type and stratum before broad catalog
  expansion.
- Ratchet current public references and `verified` dates. New undated rules are
  not accepted.
- Preserve the closed vendor-seed source, exclusion, frame, catalog, execution,
  and aggregate result commitments. Do not treat silence as a false negative or
  tune the evaluated catalog from holdout outcomes. Preserve the completed
  5,199-row drift result, including its catalog-driven measurement-surface
  disposition, zero threshold breach, and zero-promotion decision.
- Prioritize regional and non-CNAME gaps by aggregate frequency only within the
  declared observation opportunities and recurrence thresholds.
- Resolve each current candidate as promoted, rejected, or explicitly
  deferred.
- Require positive, lookalike-negative, sparse, and provenance tests for every
  promoted rule.
- Keep the expression-grammar proposal conditional on demonstrated multi-field
  rule pressure or a measured matcher bottleneck.

See [catalog-strategy.md](catalog-strategy.md).

### Acceptance

- A dated baseline names the exact catalog revision, corpus strata, record-type
  classified surface, unresolved share, stale-rule count, and corroboration
  diagnostics.
- Precision is claimed only for independently labeled units, with the Track 3
  minimum and uncertainty rule; low corroboration alone is not called a false
  positive.
- Every promoted rule has a reference or disclosure-safe basis, `verified`
  date, positive, lookalike-negative, sparse, and provenance tests.
- Classified surface improves without a statistically supported precision
  regression, and each candidate has an exact pattern plus a disposition.

## Track 7: Operator and Agent Surface Simplification

Status: maintainer track; contract frozen, portable candidate offline-validated,
three-client/runtime preflight passed, paired collection not started, profile
deferred
Dependencies: Track 3 context-cost baseline
Risk: compatibility and discoverability risk

The frozen
[representative-client evaluation contract](agent-portability-evaluation-declaration.md)
names three clients, five tasks, native and portable package variants, success
and unsupported-claim measures, discovery and result bytes, client-context
treatment, install and update behavior, launch and recovery behavior, privacy
rules, and promotion, deferral, and stop rules. It pins the exact Agent Plugins
and Agent Skills source revisions and canonical schema digests. That contract
passed protected main before candidate implementation. The generated
complete-surface candidate now passes network-free schema, package, launch,
skill, version, and containment checks. That result is not a compatibility
claim. Do not collect results or change the stable tool surface outside the
frozen client frame.

The first maintainer-local preflight started no sessions and made no network
requests. It stopped because Cursor was unavailable and the selected
client-launch recon was 2.6.3 rather than the 2.14.0 candidate. Preserve that
result as environment-readiness evidence only. Do not drop Cursor, substitute a
client, or treat the observed VS Code and Kiro versions as compatibility proof.
A second network-free preflight on 2026-08-20 passed with recon 2.17.4 and all
three clients ready, again with zero sessions and zero network requests. That
clears the environment gate but proves no client behavior. Declare the selected
models and hard cost ceiling before collection.

Document the three primary workflows separately from specialist graph,
posterior, hypothesis, simulation, catalog-mutation, and discovery workflows.
The 2026-07-13 CLI baseline measured 154 lines at 80 columns and 261 lines at
60 columns. Native task panels reduce those surfaces to 109 and 180 lines,
respectively, while retaining every option and moving collection disclosure
into the first half. At 80 columns every canonical option remains untruncated.
At 56 columns, two long names can still truncate, so complete narrow-terminal
support remains a separate plain-linear-help design problem.

The 2026-07-13 production-SDK stdio baseline measures 81,562 compact serialized
result-body bytes across initialization and the four discovery listings. The
22-tool list accounts for 70,538 bytes; output schemas account for 41,997 of
those bytes. Counts exclude JSON-RPC envelopes and transport framing.
A hypothetical seven-tool primary subset reduces the tool listing by 69.2
percent, but actual model-context treatment is client-dependent and the base
protocol has no client-selectable tool filter. Keep the complete stable surface
as the default and defer a profile until at least one representative client
proves an end-to-end context benefit without losing specialist access.

Do not rename or remove stable tools as a documentation cleanup, and do not
add a CLI profile because grouping already solved the measured CLI hierarchy
problem without hiding controls. Prefer bounded existing catalog calls before
reading whole catalog resources.

### Acceptance

- Primary workflows fit on one reader screen and do not require graph,
  posterior, or catalog internals.
- The dated CLI baseline records width, line count, token visibility, and the
  remaining narrow-terminal truncation. The MCP baseline records initialization,
  listing composition, optional resource size, and representative result bytes.
- No discovery profile is implemented unless its threshold is predeclared. If
  implemented, the core profile reduces discovery bytes by at least 30 percent
  on the recorded catalog, retains the complete default surface and stable tool
  names, and demonstrates a material context reduction in a representative client.

## Track 8: Interface Hotspot Decomposition

Status: later, after semantic and MCP changes stabilize
Dependencies: Tracks 1 and 2
Risk: critical blast radius

The high-trust graph identifies `formatter/panel.py` and
`server/introspection.py` as the next interface hotspots. Keep their public
modules as compatibility orchestrators and extract cohesive, stateless
sections. Require byte-equivalent panel golden output, unchanged MCP
registration order, unchanged generated inventories, no import cycle, and
tighter file-size ratchets. Consider `merger.py` only after the interface splits.

The 2026-07-14 structural audit rejects a bulk decomposition or consolidation.
Of 133 runtime Python modules, 24 are 18-line compatibility shims. After shims
and package entry files are excluded, the 102 ordinary implementations have a
286-line median, only four are at or below 50 lines, and 38 exceed 400 lines.
The source tree is wide but only one package level deep. The real navigation
debt is compatibility and facade indirection plus broad catch-all test suites,
not general micro-file sprawl. Fifteen runtime modules are between 800 and 999
lines, one is above the cap, and 67 production `PLR09xx` findings remain under
ratchet, so large-module pressure also remains real. The complete measured
plan is in
[structural-maintainability.md](structural-maintainability.md).

Execute this track in four bounded phases:

1. Publish a source-to-focused-test ownership map and separate direct import
   owners from heuristic test candidates in local graph output.
2. Redistribute five catch-all test suites into existing behavior owners one
   suite at a time without reducing collected tests or coverage.
3. Audit compatibility exports and runtime modules with no production importer.
   Keep v2 import shims until a breaking release and require an explicit
   supported contract for dormant runtime code.
4. Extract at most one cohesive auxiliary-rendering owner from
   `formatter/panel.py`, then assess a response-contract and pure-conversion
   extraction from `server/introspection.py`. Do not split decorated tools one
   by one or move broad stable facades only to reduce line counts.

### Acceptance

- Panel golden output is byte-equivalent and MCP registration order and
  generated inventories are unchanged.
- No import cycle or public-import change is introduced.
- At least one special file-size allowance is removed or lowered by at least 20
  percent without moving complexity into another oversized module.
- No compatibility shim points to another shim, no new shim is added, and no
  ordinary implementation below 100 lines is introduced without a named
  contract or safety boundary.
- The five catch-all test filenames are removed through behavior-owner moves;
  collected tests and the dated 90.52 percent branch-coverage result do not
  regress.
- Focused likely-test sets from `impact.jsonl` plus the full local gate pass.

## Completed or Maintenance-Only Work

- Package-local interface boundaries and typed lookup options.
- Compact output caps for every currently named high-volume MCP target.
- The July 10 hostile-input bounds for MCP config, delta JSON, CT retention,
  regex admission, and formatting controls. Add new fixtures only for a
  concrete uncovered parser or collector boundary.
- Current release publication, attestations, SBOM, same-job deterministic-build
  evidence, provider drift, and generated-artifact checks.
- Publication, OpenSSF process, independent replication, and archive planning.
  Maintain these separately; they are not product-runtime dependencies.

## Global Non-Goals

- No remote MCP server, OAuth, Apps, Tasks, Roots, Sampling, or protocol logging
  without a named consumer and new architecture review.
- No active scanning, port probing, credentialed access, paid feeds, or broader
  target-side HTTP behavior beyond the default MTA-STS request and explicit
  opt-in Google CSE / BIMI certificate probes.
- No blanket executor around resolver or detector logic.
- No stable JSON, CLI, MCP, cache, or import change outside its compatibility
  process.
- No new inference, motif, scoring dimension, or abstraction without measured
  evidence and a declared success metric.

## Execution Order

1. Keep the completed evidence-semantic audit and stable MCP v1/v2 matrix as
   blocking maintenance gates.
2. Preserve the completed stable-v1 characterization, v2.11 structural stop,
   v2.12 compatibility transition, and shipped v2.13 observation capsules.
3. Preserve the shipped v2.14 rank, regional, vendor-seed, and prior-sample
   drift decisions, including their non-promotion, non-comparability, and
   measurement-surface dispositions.
4. Keep the v2.14 release proof reproducible. Keep all public evidence
   aggregate-only and do not present repeated-frame evidence as independent
   coverage.
5. Backfill review dates only in families examined through those rounds, and
   raise the freshness ratchet only when measured coverage supports it.
6. Preserve the frozen v2.15 representative-client evaluation contract and the
   offline-validated complete-surface Agent Plugins candidate. Run the paired
   client frame and simplify operator or agent discovery only if its frozen
   outcome gates justify that decision. Keep the native client paths until
   representative-client evidence supports portability.
7. Reopen additive OKF v0.2 projection work only for a named consumer with a
   privacy and semantic mapping review; versioned JSON remains authoritative.
8. Treat dimensioned email observations, CT-enabled catalog discovery,
   robustness prototypes, and new graph machinery as separately gated feature
   tracks after the active v2.15 evaluation decision.
9. Decompose critical interface hotspots without changing behavior when the
   active semantic and catalog work no longer shares their blast radius.

Each step closes only with its named acceptance evidence, full local CI, the 90.2
percent branch-aware project gate, no regression from the current coverage
baseline, and no known unaddressed issue in scope.
