# Statistical assurance

Semantic baseline established for recon v2.4.0. Reviewed against v2.27.1 on
2026-11-03.

This document records what recon's numerical outputs establish and where their
support stops. Faithful computation, model-relative uncertainty, external
corroboration, and independent validation are different claims. A green test in
one category cannot be promoted into another.

The formal model and research direction are in
[correlation.md](correlation.md). The mechanism-to-test map is in
[assurance-case.md](assurance-case.md). Validation artifacts are indexed in
[validation/README.md](../validation/README.md).

## Four evidence levels on two axes

The levels are not a single scale of truth. Levels 1 and 2 concern provenance
and implementation soundness. Levels 3 and 4 concern comparison with external
evidence.

### Level 1: observed

A bounded collector returned a re-queryable public fact, such as a DNS record,
certificate SAN, or identity endpoint response. This licenses:

> The public channel returned this value at this time.

It does not establish current product use, ownership, control effectiveness, or
private state. Public records can be stale, ambiguous, or intentionally planted.

### Level 2: internally sound and model-relative

A deterministic rule or committed model computed its documented output
faithfully. Examples include exact variable elimination, dependency-group
selection, counterfactual masking, graph seed stability, and ordered bounded
uncertainty bands.

This licenses:

> Given these inputs and committed assumptions, the implementation produced the
> documented result.

It does not establish that a prior, CPT, likelihood, dependency assumption,
graph projection, or heuristic score tracks reality. Synthetic worlds sampled
from the same model are level 2 evidence.

### Level 3: external corroboration with a stated dependency

The output agrees with a real external channel, but the comparison is
overlapping, one-sided, selection-biased, or otherwise not an independent
two-class test of the claim. This can be useful corroboration when the dependency
is named.

Examples include comparing a policy posterior dominated by DMARC with the DMARC
record, or comparing DNS-driven M365 evidence with provider identity endpoints
that are related to the same tenancy state.

This licenses only the exact corroboration statement. It does not license a
general calibration claim.

### Level 4: independent predictive validation

A two-class external reference evaluates the named claim family on a predeclared
population with parameter development disjoint from evaluation and predictor
inputs disjoint from the label. Appropriate evidence includes proper scores,
tie-preserving reliability diagnostics with domain-cluster uncertainty,
selective risk versus coverage, and supported versus unsupported claim rates.

This is the level required before calling a score empirically calibrated for a
population. No current recon claim family has a clean level 4 result that
supports general calibration language.

## Current numeric semantics

### Per-slug `slug_confidences`

The per-slug value is a Beta-shaped additive evidence-strength score. It uses
hand-set source priors and positive weights, with no fitted negative likelihood.
Each exact `(slug, source_type, raw_value)` contributes once, including when
different rule names match it. Repeated copies cannot raise the score. Distinct
values still add weight without a general dependency correction; their
independence is not established. This is level 2, not an externally calibrated
posterior probability. Retained provenance occurrences are not removed.

### Bayesian-network posterior

`posterior_observations[*].posterior` is an exact marginal for the committed
nine-node Bayesian network. Exact arithmetic is level 2. The value is
model-relative because the priors, CPTs, likelihoods, dependence groups, and
missingness rules are manually encoded, and several parameters were informed
by a June 2026 development corpus. They were not fitted by a runtime training
algorithm, but "not machine learned" does not mean independently validated.

### Evidence-responsive uncertainty band

`interval_low` and `interval_high` come from a post-inference Beta-shaped
display with mean equal to the network posterior and concentration equal to
`n_eff`: `alpha = posterior * n_eff` and
`beta = (1 - posterior) * n_eff`. The concentration is hand constructed, not an
observed sample size. It increases with counted evidence units and decreases
with a global conflict penalty, subject to a floor of four.

When `alpha >= 1` and `beta >= 1`, the implementation uses central 80 percent
Beta quantiles if they contain the reported mean. That exact branch includes
uniform and boundary-mode cases, so it is not strictly an interior-unimodality
test. Other shapes, or quantiles that miss the mean, use a clamped mean-centered
normal approximation. Exact zero and one inputs produce degenerate endpoint
bands. The result is therefore a mixed display rule, not a single
posterior-quantile construction.

The band is level 2. It is not:

- a Bayesian credible interval over uncertain CPTs or likelihoods;
- a frequentist confidence interval;
- an identification region under unknown MNAR;
- guaranteed to widen whenever evidence is removed or narrow whenever evidence
  is added.

The current perturbation harness shows selected model-internal containment under
its elicitation scenarios. That is a useful regression property, not empirical
coverage.

### `sparse`

`sparse=true` means the effective display mass is at its configured floor after
counted fired or declarative-absence units and global conflict penalties. This
can mean no units were counted, or that conflict penalties offset their display
mass. It is not synonymous with no observed evidence, a passive-observation
ceiling, or an absence finding. It does not quantify a calibrated uncertainty
level and does not guarantee that the posterior is near 0.5.

### Signed marginal entropy change

`entropy_reduction_nats` is

$$
H(P_m(X))-H(P_m(X\mid e)).
$$

It can be negative. It is a signed marginal entropy change, not realized
pointwise information gain. Summing it across dependent nodes can double count
belief changes.

### Graph values

When `algorithm == "louvain"`, `modularity` is the objective value for the
observed clique projection, not confidence or statistical significance.
Connected-component and skipped paths use `0.0` as a sentinel.
`partition_stability` is mean pairwise adjusted Rand index across seeds on one
fixed graph. It does not measure stability to missing CT entries, hub
certificates, or graph weighting choices.

Construction caps, including per-certificate SAN clipping, select the
connected-components fallback without a seed-stability value. The public report
does not expose a completeness flag or omitted counts. Graph counts describe
the constructed graph, and separate presentation caps can omit members,
clusters, or exported edges. Neither algorithm selection nor seed stability
establishes complete collection or presentation.

## External evidence ledger

| Claim or output | Highest level | Evidence | Limit |
|---|---:|---|---|
| Raw DNS, CT, and identity responses | 1 | Re-queryable public response with source status and time | Can be stale, partial, or ambiguous |
| Fingerprint slugs and signals | 2 | Deterministic rules and fixtures | Catalog precision is not established for every rule |
| Per-slug evidence strength | 2 | Deterministic additive score | No fitted two-class likelihood or independent calibration |
| `m365_tenant` posterior | 3 | DNS-driven score compared with provider endpoint attestation: historical fixed-bin ECE 0.0471, historical legacy index-sliced equal-mass ECE 0.0440, agreement 0.889, n=3,296 in the 2026-06-28 development aggregate; see the [M365 tenancy decision](m365-tenancy-decision.md) | In-sample corroboration between related channels, not clean independent calibration |
| `google_workspace_tenant` posterior | 3 | One-sided provider routing attestation, n=11 positives and recall 0.3636 | No authoritative negative class, so calibration is not identified |
| `email_security_policy_enforcing` posterior | 3 | Full score compared with DMARC: historical fixed-bin ECE 0.0761, historical legacy index-sliced equal-mass ECE 0.0651, n=2,906 DMARC publishers across 22 development strata | DMARC is the dominant input; the input-disjoint residual reuses parameter-development data and performs poorly, with historical fixed-bin ECE 0.3747 and historical legacy equal-mass ECE 0.3263 |
| Hideable IdP, gateway, CDN, and hosting posteriors | 2 | Exact model computation and selected synthetic properties | No training-disjoint and predictor-input-disjoint two-class reference |
| `email_security_modern_provider` | 2 | Pure propagation from parent nodes | Not an independent measurement |
| Uncertainty band | 2 | Deterministic mean/concentration Beta display with a boundary fallback, plus finite model-internal scenario checks | No coherent parameter posterior, identification region, or empirical coverage claim |
| CT graph partition | 2 | Deterministic fixed-seed partition plus seed sweep | Clique-projection bias and data stability remain unmeasured |
| Cohort summaries | 1 plus 2 | Caller-supplied set, explicit denominators, model-relative reductions | No population inference or ownership claim |

The M365 and policy figures are development-corpus aggregate diagnostics, not
universal performance rates. The policy rows are publisher-conditional, and
several parameters were informed by the same corpus. No current tie-preserving
numeric estimate is available. Historical equal-mass bins
split tied scores by index; historical row-bootstrap and Wilson intervals assume
iid rows and carry no coverage interpretation. The held-out residual prevents a
clean calibration claim but is not itself a level-4 training-disjoint result.

## Validation that remains necessary

The four-arm M365 study was cancelled before target collection on 2026-08-13.
The [arm-identifiability audit](../validation/2026-08-13-quality-arm-identifiability.md)
found A1 equal to A0 and A2 equal to A3 across the frozen 64 DNS evidence-role
states, with no case where A3 supported and A0 abstained. Its benefit gate
could not pass at any sample size. The following arms are a post-mortem of that
design, not an active collection plan:

1. deterministic evidence plus explicit abstention;
2. per-slug evidence strength;
3. strongest reviewed evidence unit;
4. current Bayesian network.

Any future study needs a distinct candidate with at least two non-collapsed
evidence units, a binary operator action tied to shipped behavior, an executable
structural-identifiability and dominance preflight, disjoint labels, and a new
preregistration. The cancelled frame remains unused and cannot complete the
voided design. The implicit v2 fusion default remains enabled and silent for
compatibility; the non-promotion disposition classifies it as an advanced
diagnostic, not a default-off runtime change. See
[ADR-0013](adr/0013-fusion-non-promotion-and-v3-transition.md) and its amendments.

The following measurement requirements remain necessary for any new study,
but are not sufficient to authorize collection:

Predeclare one primary family, candidate, and comparator. Use one frozen
`(domain, claim_family, observation_time)` row per unique domain, admit at most
one domain per known administrative, ownership, or tenant cluster in the
primary analysis, keep domain groups intact across parameter development and
evaluation, and require predictor-input-disjoint labels. A clustered
multi-domain analysis remains secondary until it defines a cluster-level
estimand, outcome, and decision rule. Report the precisely defined
reference-positive support rate and reference-negative unsupported-emission
rate, abstention, selective risk versus coverage, tie-preserving reliability,
provenance completeness, latency, and allocation. Report Brier and log score
only for an arm that supplies one frozen probability forecast for every
eligible row; arbitrary evidence-strength scores require a development-disjoint
fitted probability mapping first. The primary paired bounds must remain valid
at zero discordance. Bootstrap intervals are secondary, must preserve the
predeclared label strata and paired structure, and cannot repair unknown
cross-domain dependence. Every interval must name its assumptions.

The historical minimum sample sizes and go or no-go rule remain in
[roadmap.md](roadmap.md). A new study must freeze its own justified sample plan,
decision rule, and compatible product disposition before evaluation. No
secondary metric can override a failed primary decision after results are
visible or revive the cancelled design.

The proposed claim-robustness envelope adds a separate test: evidence removal
and planting under explicit provenance classes, dependency units, costs, and
budgets. Its first bounds are pointwise, model-and-threat-relative robust scores,
not probability bounds. Identification of `P(C | O=o)` additionally requires a
coherent normalized joint law over the claim, full latent target state, and
observation-process state, plus a possibly claim-dependent observation kernel
and an explicit ambiguity class. Support compatibility alone supplies no
observation likelihoods. See
[correlation.md](correlation.md#5-claim-robustness-envelopes).

## Wording rules

- Say "observed" for a public fact.
- Say "deterministically derived" for a rule output.
- Say "evidence strength" for `slug_confidences`.
- Say "model-relative posterior" for the Bayesian-network mean.
- Say "evidence-responsive uncertainty band" for `interval_low` and
  `interval_high`.
- Say "external corroboration" for an overlapping or related reference.
- Say "empirically calibrated" only after a predeclared, training-disjoint and
  predictor-input-disjoint level 4 evaluation supports it for the named
  population.
- Say "unresolved" when the public channel and admitted assumptions do not
  identify the claim.

These terms are compatibility-neutral. Stable field names remain unchanged.
