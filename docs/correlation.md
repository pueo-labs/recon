# Correlation model

Semantic baseline established for recon v2.4.0. Reviewed against v2.27.1 on
2026-11-03.

This document separates three things that must not be conflated:

1. facts and deterministic deductions that recon currently emits;
2. model-relative diagnostics that recon currently computes;
3. a research program that must pass predeclared product tests before it can
   change default behavior.

The conditional research thesis is **proof-carrying public observation with
provenance-constrained claim robustness**. The first candidate in section 5 is
a Boolean must/may claim envelope over compatible clean public states. The
robust score envelope is a secondary model diagnostic, not the foundation. A
later probabilistic model earns partial-identification language only after it
defines a coherent normalized joint law over the claim, full latent target
state, and observation-process state, plus an admitted observation kernel and
explicit ambiguity class. The useful question is not merely "what score does
one committed model assign?" It is:

> Which claims remain supported after realistic evidence hiding, evidence
> planting, dependence, and parameter uncertainty are made explicit?

That question fits recon's product boundary. It rewards provenance, supports
abstention, and turns adversarial ambiguity into an inspectable result. One
bounded claim contract and its minimal-certificate algebra are now implemented
internally for exact apex DMARC `p=reject`; see
[claim-contracts.md](claim-contracts.md). No public dossier, general registry,
robustness envelope, or graded bound is shipped. The first contract supplies an
implementation baseline; Boolean robustness would precede graded score bounds
in a future prototype. A new robustness surface would need demonstrated
operator value before promotion.

The product standard is best-effort interpretation of observable public
evidence, with explicit limits. No current claim family has independent
predictive validation supporting general calibration language; the
[statistical-assurance ledger](statistical-assurance.md#external-evidence-ledger)
states what each family can claim today. The first M365 study stopped before
collection because its candidate could not pass the declared benefit gate;
[section 8.3](#83-predeclared-product-ablation) records that bounded result.
It creates no obligation to launch a replacement study. Section 5 is conditional
research design, not a shipped robust-inference engine or a maintenance backlog.
Current work improves record interpretation, provenance, failure handling, and
renderer truth through documented public patterns and reproducible fixtures.

## 1. Scope and epistemic contract

"Correlation" is an umbrella term here for evidence linkage, dependence,
co-occurrence, and joint inference. It does not mean that recon estimates one
Pearson or Spearman correlation coefficient, and it never implies causation.

Given an apex domain, recon inspects a bounded, domain-centered public
namespace. The apex is a query scope, not proof of one organization or owner.
The current sources are:

- DNS records;
- certificate-transparency records;
- unauthenticated identity-discovery responses;
- the standards-compliant MTA-STS policy at `mta-sts.<domain>` by default.

DNS reads go through the configured recursive resolver, so authoritative DNS
infrastructure may observe resulting resolver traffic. The MTA-STS fetch is the
only default target-owned HTTP or application request and is visible to the
target's web infrastructure. Google CSE and BIMI certificate requests are
opt-in direct probes. recon does not scan ports, authenticate, crawl target
applications, test exploitability, or infer company ownership.

Let $O$ be the observations returned by this bounded collection channel. One
lookup is a non-atomic observation window: DNS, CT, identity metadata, and
MTA-STS can be read at different times, from different providers and vantage
points. The channel is incomplete and strategic:

- some facts must be published for a service to function;
- some declarations are optional;
- some identifiers are provider-attested;
- some operator-controlled tokens can be hidden, left stale, or planted;
- collectors can fail or return partial data.

Therefore $O$ does not identify the full private configuration $X$. A
correlation layer may organize or constrain claims about $X$, but it must not
manufacture observability.

### 1.1 Orthogonal output semantics

One label cannot encode how a result was constructed, whether collection
succeeded, what the claim state is, and when it applies. Every material output
should eventually carry four orthogonal axes:

| Axis | States | Meaning |
|---|---|---|
| Construction | observed, deterministic derivation, model diagnostic | Whether the value is a retained response, rule consequence, or model-relative number |
| Collection | observed value, observed empty, unavailable, not attempted, not applicable | Whether the relevant observation opportunity completed and what it returned |
| Claim | supported, disconfirmed within the public model, conflicted, unresolved | Whether reviewed public-evidence rules establish, oppose, disagree on, or cannot decide the claim |
| Time | current observation, historical observation, observation window | When the evidence was read and whether its constituent reads were simultaneous |

The construction axis does not contain `unresolved`: unresolved is a claim
state. The collection axis does not turn an unavailable source into an observed
empty result. A disconfirmed state is valid only for a claim whose reviewed
public model admits genuine negative evidence. For most private product-use or
ownership claims, non-detection remains unresolved.

Observed values and deterministic derivations are recon's product core.
Model-relative outputs are advanced diagnostics. A model score is not a fact,
security verdict, ownership claim, or calibrated probability unless an
independent evaluation establishes that interpretation for the named claim
family and population.

The shipped exposure index is one such deterministic, model-bound diagnostic.
Its stable compatibility scale is 0-100, while the current nine weighted
components assign at most 90 points. The reported floor sums only component
values that agree with exact retained evidence. Its ceiling adds modeled
capacity from unavailable, intrinsically narrow, inconsistent, or otherwise insufficient observation paths. Each
component retains the generation rule, basis state, typed predicates, bounded
scope, point weight, and record evidence. This ledger makes the arithmetic
replayable; it does not convert the result into an overall security measure.
Published no-mail declarations can make individual mail controls
inapplicable. An optional `applicability` proof block records that decision
separately from the existing control-observation state and evidence. Those
components retain their nominal weight and declaration proof, receive no
points or unresolved capacity, and are excluded from
`model_maximum_points`. The 0-100 compatibility scale is not renormalized.
The exact conditions and simulation behavior are documented in the
[MCP index contract](mcp.md#available-tools).

### 1.2 Provenance is part of the result

A claim without a direct evidence path is unsupported even when a heuristic or
model produces a high number. The minimum useful path is:

```text
raw public response
  -> normalized evidence record
  -> fingerprint or signal rule
  -> claim or model binding
  -> rendered observation
```

Source errors, stale cache state, derivation, and dependency grouping belong in
that path. Agreement among transformations of one raw record is not independent
corroboration.

### 1.3 What correlation should mean for recon

Correlation is not a flat count of matching fingerprints. It is the disciplined
composition of typed observations into the strongest public claim that survives
all reviewed alternatives. A useful result answers six questions:

1. What public facts were observed, by which source, owner, vantage, and time?
2. Which claim follows under deterministic rules, and which assumptions were
   required?
3. What minimal dependency-unit evidence sets support or oppose that claim?
4. Which compatible explanations remain?
5. What source failure, staleness, dependence, or manipulation could overturn
   the result?
6. What smallest independent verification or permitted observation would
   resolve the ambiguity?

This makes the product a passive public-namespace observatory, not a broader
scanner. Its differentiator is epistemic precision: a typed claim graph,
explicit unknowns, replayable explanations, and bounded correlation. A domain
can anchor the lookup without being treated as an organization, and two domains
can share an observed identifier without being declared commonly owned.

The central conservation rule is that derivation cannot create evidentiary
independence. Every derived claim inherits the raw origins, dependency groups,
observation opportunities, and time windows of its inputs. Duplicate renderings
of one observation remain one support unit.

## 2. Current correlation layers

Three layers share the same collected public observations. Only Layer 1 is
authoritative for "did we observe X?" Layer 2 describes retained CT
co-occurrence when available. Layer 3 is an advanced model-relative diagnostic.
On the CLI it runs by default; pin it with `--fusion` or skip it with
`--no-fusion`. MCP `lookup_tenant(format="json")` also populates fusion and has
no fusion toggle; `get_posteriors` and `explain_dag` expose dedicated diagnostic
views. Ordinary MCP text and Markdown do not render the posterior fields.

```mermaid
flowchart LR
  obs["Public observations: DNS, CT, identity, MTA-STS"]
  obs --> rules["Layer 1: deterministic rules<br/>slugs and signals"]
  rules --> panel["Default panel and JSON"]
  obs --> graphL["Layer 2: CT co-occurrence graph<br/>communities and motifs"]
  graphL --> panel
  rules -. "evidence chain" .-> bn["Layer 3: Bayesian network<br/>posteriors and bands"]
  bn -. "fusion path" .-> diagnostics["Detailed model diagnostics"]

  classDef det fill:#dbe5f7,stroke:#3c5a8c,stroke-width:1px,color:#101828
  classDef cooccurrence fill:#d7ecdf,stroke:#3f7d55,stroke-width:1px,color:#101828
  classDef bayes fill:#f8dedb,stroke:#a04a3f,stroke-width:1px,color:#101828
  class rules det
  class graphL cooccurrence
  class bn bayes
```

### 2.1 Deterministic evidence and rule correlation

The deterministic layer maps observed records to evidence records, fingerprint
slugs, signals, conflicts, motifs, and bounded summaries. Its guarantees are
software guarantees: deterministic ordering, bounded inputs, explicit source
status, and traceable rules. They are not population-level statistical
guarantees.

Important mechanisms include:

- wildcard SAN sibling summaries;
- certificate issuance bursts;
- CNAME and NS chain motifs;
- cross-source conflict records;
- batch-only ecosystem hyperedges;
- vertical-baseline diagnostics over caller-supplied cohorts.

These mechanisms describe public structure. They do not prove common ownership,
organizational control, live product use, or a causal explanation for change.

### 2.2 Per-slug evidence-strength heuristic

`fusion.py` computes `slug_confidences` from a Beta-shaped additive score. For a
slug, it chooses a source-type prior, adds positive weights once per exact
source-type/value pair, leaves the negative mass fixed, and reports the
resulting mean. Different rule names for the same pair add no weight; retained
provenance still includes every occurrence. Opaque raw values are not normalized.

For prior parameters $(\alpha_0,\beta_0)$ and observed positive weights $w_j$,

$$
s = \frac{\alpha_0 + \sum_j w_j}
 {\alpha_0 + \beta_0 + \sum_j w_j}.
$$

This is a monotone evidence-strength heuristic. It is not a fitted Bernoulli
posterior because there is no labeled likelihood model, no negative update, and
no general correction for dependence among distinct pairs. Exact deduplication
does not identify shared derivations across source types or values, and the
record has no separate owner or collection-window identifier. Human-facing
documentation should call it evidence strength. The stable field name remains
unchanged pending a versioned contract decision.

### 2.3 CT co-occurrence graph

The current graph layer constructs an undirected one-mode projection:

- nodes are non-wildcard SAN hostnames;
- every certificate's retained SAN set becomes a clique;
- an edge's Louvain weight is the number of retained certificate entries in
  which the two names co-occur;
- issuer samples are retained for display but do not affect the partition;
- Louvain uses a fixed seed;
- eight total seeds produce mean pairwise adjusted Rand index as an
  optimizer-stability diagnostic;
- bounded or failed cases fall back to connected components as documented by
  the schema.

For a partition $c$ with positive total edge weight ($2m>0$), weighted modularity is

$$
Q = \frac{1}{2m}\sum_{ij}
 \bigl(A_{ij} - \frac{k_i k_j}{2m}\bigr)
 \mathbf{1}\lbrack c_i=c_j\rbrack.
$$

Here $A_{ij}$ is the observed edge weight,
$k_i=\sum_j A_{ij}$, and $2m=\sum_i k_i$.

`Q` is an objective value relative to the modularity null model. It is not a
probability, calibrated partition-quality score, ownership confidence, or test
of statistical significance. Seed stability only shows whether the optimizer
repeats a partition on one fixed graph. It does not show stability to missing
CT entries, large multi-tenant certificates, or sampling noise.

Clipping a certificate to the 60-SAN construction limit sets the same internal
truncation flag as an entry or node stop and selects the existing
connected-components fallback. That path emits no seed-stability value. The
public report has no completeness flag or omitted-count ledger: `node_count`
and `edge_count` describe the constructed graph, while cluster members,
clusters, and exported edges have separate output caps. A Louvain result or
perfect seed stability therefore establishes neither complete collection nor
complete presentation of the graph.

The one-mode projection is the deeper limitation. A certificate containing
$k$ retained SANs creates $\binom{k}{2}$ pairwise edges. A single 60-SAN
certificate can therefore create 1,770 edges. This can turn certificate size
into apparent community evidence before Louvain sees the graph.

Graph output must be read as descriptive co-occurrence structure. It must not
be read as a discovered organization boundary.

### 2.4 Bayesian-network diagnostic

The current Bayesian layer contains nine binary claim nodes in a directed
acyclic graph. The CLI enables it by default; `--no-fusion` skips it and
`--fusion` pins it on. `get_posteriors` and `explain_dag` expose it explicitly
over MCP. Explicit flags and JSON field shapes stay stable. Any omitted-choice
change remains conditional on a genuine major contract boundary; otherwise the
v2 default stays enabled.
The layer is deterministic for fixed inputs, priors, and model data.

```mermaid
flowchart LR
  m365["m365_tenant<br/>prior 0.30"] --> fed["federated_identity"]
  gws["google_workspace_tenant<br/>prior 0.25"] --> fed
  fed --> okta["okta_idp"]
  m365 --> emp["email_security_modern_provider"]
  gws --> emp
  egw["email_gateway_present<br/>prior 0.18"] --> emp
  pol["email_security_policy_enforcing<br/>prior 0.62"]
  cdn["cdn_fronting<br/>prior 0.45"]
  aws["aws_hosting<br/>prior 0.40"]

  classDef root fill:#dbe5f7,stroke:#3c5a8c,stroke-width:1px,color:#101828
  classDef child fill:#f4f5f7,stroke:#6b7280,stroke-width:1px,color:#101828
  class m365,gws,egw,cdn,aws,pol root
  class fed,okta,emp child
```

Nine nodes total. Six roots carry priors only; three children use CPTs.
`email_security_modern_provider` has three parents because M365, Google
Workspace, and gateway presence contribute differently to the
provider-presence claim. `email_security_policy_enforcing` is a separate root
because policy enforcement is not the same claim as provider presence. Its
prior is the one corpus-grounded root value in the network: 0.62 reflects the
share of the 2026-06 development corpus publishing an enforcing DMARC policy
(CAL12), where the other roots stay hand-set.

Let $X_1,\ldots,X_n$ be claim nodes and let `pa(i)` be the parents of node
$i$. The committed model factorizes as

$$
P(X_1,\ldots,X_n)=\prod_i P(X_i\mid X_{\mathrm{pa}(i)}).
$$

Observed slug or signal bindings add virtual-evidence factors
$\phi_e(X_i)$. Exact variable elimination then computes

$$
P_m(X_i\mid e) =
\frac{\sum_{X\setminus X_i}\prod_j
 P_m(X_j\mid X_{\mathrm{pa}(j)})\prod_e\phi_e(X)}
 {\sum_X\prod_j
 P_m(X_j\mid X_{\mathrm{pa}(j)})\prod_e\phi_e(X)}.
$$

The subscript $m$ matters. The value is exact for the committed model, but the
priors, conditional-probability tables, evidence likelihoods, dependency groups,
and missingness rules are manually encoded. Several parameters were informed by
a June 2026 development corpus. Exact inference is not evidence that the model
tracks the world or generalizes beyond that corpus.

For example, the M365 root prior `0.30` and fired likelihoods `[0.95, 0.03]`
give `0.30 * 0.95 / (0.30 * 0.95 + 0.70 * 0.03) = 0.931372...` when that
binding is the only evidence. The emitted `0.9314` reflects four-decimal
rounding of those assumptions, not four-decimal empirical precision or a
validated 93% chance of current product use. Changing the display band's
`n_eff` does not test or integrate uncertainty in those parameters.

"Exact" describes variable elimination over the finite network, subject to
floating-point precision. The exported Python `load_network(path)` and `infer`
interfaces accept custom models whose individually valid likelihoods can have
numerically unsafe products. Evidence and factor products below the smallest
normal floating-point value raise `FloatingPointError`, including positive
subnormal products that can lose substantial relative precision before reaching
zero. Non-finite or nonpositive normalization also raises. These checks remain
active under `python -O`. Such a run emits no posterior; numerical failure cannot
be replaced by `0.5`. The engine remains a probability-space implementation,
not a general log-space solver for arbitrary extreme models.

## 3. Bayesian evidence semantics

### 3.1 Fired bindings

For a binding $e$ on claim node $X$, the model stores

$$
\phi_e(X=1)=P(e\mid X=1),\qquad
\phi_e(X=0)=P(e\mid X=0).
$$

The likelihood ratio is

$$
LR_e=\frac{P(e\mid X=1)}{P(e\mid X=0)}.
$$

Bindings in different declared units are multiplied as conditionally independent
given the claim. This is a modeling assumption, not an observed property.

### 3.2 Dependency groups

Bindings assigned to the same group are treated as redundant views of one
evidence unit. When several fire, the implementation keeps the member with the
largest absolute log likelihood ratio:

$$
e_g^*=\arg\max_{e\in g}|\log LR_e|.
$$

This prevents a known form of double counting and is operationally useful. It is
not a general conservative bound on the unknown joint likelihood. Without a
joint distribution, the true group likelihood ratio can lie above or below the
selected member. Ungrouped bindings can also share an unmodeled cause, collector,
or raw record.

The correct interpretation is: groups encode reviewed dependence assumptions;
they do not prove independence elsewhere.

### 3.3 Missingness

The implementation has two missingness policies.

For a hideable node, a non-fired binding contributes no factor:

$$
LR_{\neg e}=1.
$$

This is a conservative product rule: recon declines to treat missing optional
public evidence as evidence of absence. It is not derived from the statement
that missingness may be not at random. Unknown MNAR generally leaves the target
only partially identified unless the observation mechanism or a sensitivity set
is specified.

For a declarative node, a non-fired binding can contribute a complement
likelihood or a declared group-absence factor. This is appropriate only where
the collector observed the authoritative publication point successfully and the
declaration's absence has the documented meaning. Source failure is unobserved,
not absent.

### 3.4 Evidence removal

`masked_units` removes one dependency unit from every node it feeds. The
implementation uses this for leave-one-unit-out counterfactuals and held-out
reference checks.

For a local binary claim with fixed prior odds and only positive independent
likelihood ratios, deleting a fired unit cannot increase the local odds:

$$
O(X=1\mid E)=O(X=1)\prod_{e\in E}LR_e,
\quad LR_e\ge 1.
$$

This is a narrow monotonicity result. It does not prove that deletion moves the
full network toward 0.5, prevents confident false negatives, neutralizes parent
messages, or widens the reported uncertainty band. Those stronger properties
require additional assumptions and tests.

### 3.5 Model-relative posterior

The reported network mean is $P_m(X_i=1\mid e)$. It may be called a posterior
only with the model-relative qualifier. It must not be called calibrated for a
claim family unless parameter development is disjoint from evaluation and an
independent, predictor-input-disjoint label study supports that word for the
stated population and observation regime.

The current evidence shows:

- exact arithmetic and differential agreement for the committed model;
- deterministic behavior and positive factors;
- self-generated synthetic behavior under selected assumptions;
- DMARC-anchored agreement for the policy node, with poor calibration after
  holding out the DMARC-defining unit;
- M365 channel-split corroboration, not fully independent calibration;
- no two-class external calibration for the hideable infrastructure nodes.

## 4. Uncertainty and information diagnostics

### 4.1 Evidence-responsive uncertainty band

After exact network inference produces mean $p$, the implementation constructs
a separate Beta distribution with

$$
\alpha=p n_{\mathrm{eff}},\qquad
\beta=(1-p)n_{\mathrm{eff}},
$$

and reports its central 80 percent quantiles when both shape parameters are at
least one and those quantiles contain the reported mean. This is the exact
implementation branch, including uniform and boundary-mode cases; it should not
be read as a strict interior-unimodality test. Other cases, and any central
interval that misses the mean, use a clamped mean-centered fallback.
The effective mass is

$$
n_{\mathrm{eff}}=\max\bigl(n_{\min},\, n_{\min}+c_e N_e-c_c N_c\bigr),
$$

where $N_e$ is the effective-unit count after dependency grouping, structural
masking, and non-neutral declarative-absence selection; $N_c$ is the global
conflict count. The shipped defaults are $n_{\min}=4$, evidence contribution
$c_e=1$, and conflict penalty $c_c=1.5$.

This band is not derived from the Bayesian network's latent-state posterior,
CPT uncertainty, likelihood uncertainty, or a sampling design. It is a
model-relative evidence-strength display parameterized by and required to
contain $p$. The stable JSON fields are `interval_low` and `interval_high`;
documentation calls them an
**evidence-responsive uncertainty band**.

The same point posterior mean can therefore produce different band widths as
effective mass changes:

```mermaid
flowchart TB
  subgraph sparse["n_eff = 4 (display floor)"]
    sl["0.20"] --- sm["0.5"] --- sh["0.80"]
  end
  subgraph mid["n_eff = 8"]
    ml["0.28"] --- mm["0.5"] --- mh["0.72"]
  end
  subgraph dense["n_eff = 14 (more counted units)"]
    dl["0.33"] --- dm["0.5"] --- dh["0.67"]
  end
```

At $n_{\mathrm{eff}} = 4$ (the display floor) a mid-mean band is wide under
the display heuristic. At $n_{\mathrm{eff}} = 14$ the
same mid-mean is a tighter model-relative band. Neither width is a calibrated
coverage probability.

Four is a minimum display mass, not a passive-observation ceiling. More
counted units can increase the mass without bound under the current formula.
Conflict can lower display mass and widen the band above the floor; it never
changes the mean. Band width is not generally monotone in added evidence because
evidence can change both $p$ and $n_{\mathrm{eff}}$.

No ground-truth 80 percent coverage claim is made. A future interval with that
claim would require a coherent uncertainty model or a reference-label coverage
study under clearly stated exchangeability or shift assumptions.

### 4.2 Signed marginal entropy change

For each node the implementation reports

$$
\Delta H_i=H(P_m(X_i))-H(P_m(X_i\mid e)).
$$

This value can be negative for one observation. It is a signed marginal entropy
change, not realized pointwise information gain. The expectation of entropy
reduction under one coherent joint model is mutual information. A sum of
marginal entropy changes is not joint information gain and can double count
dependent claims.

For one realized observation, a nonnegative measure of belief change would be

$$
D_{\mathrm{KL}}\bigl(P_m(X_i\mid e)\Vert P_m(X_i)\bigr),
$$

but even that remains model-relative and does not measure product value.

### 4.3 Identifiability

No direct binding on a node does not imply posterior equals prior. Parent,
child, or shared evidence can move a node through the DAG. Conversely, a moved
posterior does not mean the private state was identified.

The relevant distinction is:

- **state uncertainty:** uncertainty about one target under a fixed model;
- **parameter uncertainty:** uncertainty about priors, CPTs, and likelihoods;
- **partial identification:** several admissible models or hidden observation
  mechanisms remain compatible with the public evidence.

The current network reports the first under one committed parameterization. It
does not integrate the second and does not compute the third.

### 4.4 CPT sensitivity

The network ships hand-encoded priors and CPT entries as data (section 2.4).
The fair question is how much any reported posterior depends on those exact
numbers. `tests/test_bayesian_sensitivity.py` answers it mechanically: it
perturbs every CPT entry and every root prior by $\pm 0.10$ across a fixed set
of canonical evidence scenarios, and records the largest posterior shift each
perturbation produces anywhere in the network.

The finite measurements are:

| Statistic | Historical v1.9.0 | Historical 2026-09-20 inputs | Role-observation fixtures (2026-10-23) |
|---|---|---|---|
| Median summary (new column: upper middle) | 0.019 | 0.020 | 0.0179 |
| 95th-percentile indexed shift | 0.109 | 0.100 | 0.1000 |
| Maximum observed | 0.139 | 0.134 | 0.1076 |

The new column covers 120 single-entry perturbation results: 20 root-prior/CPT
targets, two signed perturbations and three fixed synthetic scenarios, with
prior overrides explicitly disabled. The upper median uses sorted index
`N // 2`; the 95th-percentile value uses index `int(0.95 * N)`. The
[machine-readable receipt](../validation/role-observation-assurance-2026-10-23.json)
records the exact engine revision, model Git blob and SHA-256, inputs, fired
bindings, effective mass, sparse states and clipping rules. Reproduce with
`uv run pytest tests/test_bayesian_sensitivity.py -s`.

The dense M365/GWS cases now start from role-bearing `TenantInfo` fixtures
through the real adapter. Before numerical assertions, shared scenario
contracts require the named direct bindings, effective-unit counts, non-sparse
state and intended node movement. Removing identity observations fails that
precondition. Generic vendor slugs and verification TXT remain intentional
nonbinding controls. The empty scenario means no fired observations; it does
not restore unconditional priors for declarative nodes with informative
nonfires. Unbound auxiliary observations such as DKIM are not counted as
additional role evidence.

The historical 2026-09-20 inputs used retired generic M365/GWS vendor slugs;
they did not establish sensitivity of the dense role scenarios their names
suggested. Those numbers remain historical receipts, not current positive-role
assurance. The columns use different observation contracts and are not evidence
of improved population accuracy, calibration or general robustness. Likewise,
measurements from the v1.9.3 split do not become current merely because the
topology is unchanged: priors, likelihoods and actual fired inputs matter.
The retired `email_security_strong` combined three parents
with five evidence bindings; its replacements each carry one of those burdens
and not the other (section 4.9). The existing 0.30 maximum-shift and 0.10
upper-median regression ceilings remain unchanged. They apply to this declared
grid, not arbitrary CPT perturbations, unseen observations or interval coverage.

Grouping assurance uses a purpose-built model with three fired bindings:
grouped readings retain one effective unit and match the strongest single
reading, while the explicitly naive product retains three units. Conflict-band
cases start above the mass floor and require an actual mass decrease and wider
band at the same mean. Fixed-mean band checks and one selected positive-role
example replace a universal claim that arbitrary additional evidence narrows
intervals; section 4.1 explains why that claim is false.

These measurements bound the observed response to the tested one-at-a-time
perturbations on this scenario set. They do not establish typical behavior in a
target population or joint parameter correctness. Correlated misspecification
across several entries and whether the network's structure matches the world
remain section 8 questions.

### 4.5 Prior equality and the `sparse` flag

No local fired binding does not imply equality to the prior. Evidence at
children can update a root, and declarative absence can update a node without
any positive binding. A sufficient condition for prior equality is that every
observation factor in the node's connected model component is constant in its
state variables, including masked or omitted factors:

$$
P_m(X_i\mid e)=P_m(X_i)
\quad\text{if every observation factor in its component is state-independent.}
$$

The shipped network provides a concrete counterexample to a parent-only
interpretation. With only `federated_sso_hub` fired and no prior overrides,
`m365_tenant` has no local evidence and no parents, yet its posterior is
`0.5199`, above its `0.30` prior, because the observed child updates the root.
It remains `sparse=true`. With no fired bindings at all, the policy node is
`0.0554` under the successfully observed declarative-absence model, rather than
its `0.62` prior. Source masking changes that absence assumption.

`sparse` means only that effective display mass is at the configured floor.
Conflicts can return the mass to that floor even when evidence fired. It is
neither a prior-equality test nor a count of failed collectors. Read
`evidence_used`, `absence_informative`, `conflict_provenance`, and connected-node
evidence together. Neither a moved posterior nor an unchanged one identifies a
private configuration state.

The stable `evidence_ranked[*].influence_pct` field is the binding's share of
total absolute local fired log-likelihood ratio after dependency-group
reduction. It excludes informative absences and evidence at other nodes. A
100 percent share therefore does not mean the binding caused the entire
posterior change. `unit_counterfactuals` reports exact model replay with one
unit masked globally; those changes need not add to the total change. The LLR
calculation uses `log(likelihood_present) - log(likelihood_absent)` for both
group selection and ranking, preserving valid small likelihoods without
division overflow or an explanatory clamp.

An evidence unit is a committed model factor, not a raw-response identifier.
One response can produce several role observations at connected nodes; local
grouping does not establish their independence across those nodes. Removing
one unit can leave other consequences of that response active. Conversely,
masking every role associated with a response can also remove support from
other observations that satisfy the same Boolean role. The bounded offline
[shared-response characterization](shared-response-characterization.md)
records both differences, direct versus graph support, duplicate invariance
under the current adapter, and the limits of that result.

### 4.6 Relationship to the per-slug evidence-strength layer

recon carries two numeric layers that are easy to conflate because both emit a
number in $[0,1]$ per name. They answer different questions:

- **Per-slug evidence strength** (`slug_confidences`, section 2.2). A monotone
  summary over one slug's own evidence records. It addresses: given this
  evidence chain, how strongly did the deterministic pipeline attribute slug
  $s$? It is per-slug, closed-form, and encodes no relationship between slugs.
- **Network posterior** (`posterior_observations`, section 2.4). A
  multi-node update over the committed DAG. It addresses: given everything
  observed, how does the committed model score the high-level claim $X$, after
  parent propagation, dependency grouping, and conflict accounting?

Neither derives from the other and neither supersedes the other. The per-slug
value is confidence about an extraction; the network value is a model-relative
score for a claim that *uses* extractions as evidence. A high slug strength with
a near-prior posterior is coherent and common: the pipeline is confident about
what it saw, and the committed model treats what it saw as weakly diagnostic of
the broader claim. Both fields are independently stable in the schema, and a
consumer may read either or both.

### 4.7 Two claims the validation must not conflate

The checks in section 8 support two epistemologically separate propositions,
and most misreadings of this layer come from collapsing them:

1. **The engine is faithful to the committed model.** Exact-inference
   agreement with independent enumeration, the canonical-network reference
   test, the sensitivity bound in section 4.4, determinism, and per-node
   propagation stability all test this. Synthetic calibration is a separate
   behavioral diagnostic: even when latent states are sampled from the
   committed network, the current generator and shipped inference use different
   nonfire semantics (section 8.1). It cannot replace differential inference
   checks or validate the model's description of the world.
2. **The committed model is a useful description of the world.** Only
   corpus work speaks to this, and it speaks weakly. Agreement between a
   high posterior and a high-confidence deterministic classification is close
   to tautological where both read the same underlying records, which is the
   usual case. Section 8.2 records the ablation result that the current
   validation cannot decide the advanced layers' product disposition.

A related caveat applies to calibration metrics. For fixed observations and
labels, the conflict penalty in section 4.1 changes display mass and bands, but
never the posterior mean. It therefore cannot change Brier score, log score,
or expected calibration error computed from those means. A metric calculated
after filtering on `sparse` may change because the selected rows changed; that
is a selection effect and must be reported with its denominator. Proper scores
require a frozen probability interpretation and an evaluation design as stated
in section 8.3. An evidence-strength band does not acquire coverage guarantees
from a low point-forecast loss.

The same care applies to any reported calibration figure's regime. A figure
computed conditional on at least one binding firing describes that selected
regime, not all model-supported cases: propagation and informative absence may
also move a posterior. The unconditional figure includes all eligible rows.
Neither regime is calibrated or miscalibrated by construction. Any measured
gap can reflect missingness policy, corpus composition, or model mismatch;
quoting either figure requires its selection rule and denominator.

### 4.8 What the layer offers a defender

A defender who has hardened their public footprint wants a specific answer: if
someone ran this against us, what would the public channel actually support?

The layer reports a model-relative posterior, a display band, and the bindings
that contributed. Sparse results can reflect missing public records, failed
collection, model structure, or conflict penalties. They do not establish that
hardening succeeded. Additional public evidence can narrow a band without
implying a security weakness: standards-defined mail policies are intentionally
public. The actionable output is the bounded evidence claim and its source
status, not a ranking of how much a target reveals.

Two limits keep this honest. The output is model-relative, so it describes what
recon's committed model does with public evidence, not an attacker's ceiling
against a better model or a better channel. And a wide band is not a safety
certificate: section 4.11 documents a posture where the layer is confidently
wrong in the other direction.

### 4.9 Definitional discipline: the v1.9.3 split

The v1.9.0 corpus run surfaced exactly one weak node. `email_security_strong`
agreed with the deterministic pipeline on 52.6 percent of its high-confidence
posteriors while every other node sat near 100. The reflex reading is a
calibration problem: wrong numbers, tune the numbers. The v1.9.3 change came
from taking the alternative seriously, and it is the worked example this
project points at when a CPT change is proposed.

**The diagnosis.** The node's CPT was parameterized over modern-mail-provider
presence, with parents `m365_tenant`, `google_workspace_tenant`, and
`email_gateway_present`. Its evidence bindings were policy signals: DMARC
reject and quarantine, MTA-STS enforce, DKIM, strict SPF. Those are different
claims. An M365 tenant publishing `p=none` is a modern provider with weak
policy; a self-hosted domain behind a gateway publishing a strict reject is the
reverse. The node asserted "strong email security" using provider parents and
policy evidence, so it conflated the two, and no CPT entry can reconcile
definitions that disagree.

**The fix.** Replace the one node with two:

- `email_security_modern_provider` keeps the provider parents and drops the
  evidence bindings entirely. Its posterior is pure CPT propagation, because
  provider presence is already carried by the parent slugs.
- `email_security_policy_enforcing` becomes a root with no parents and carries
  the policy bindings. Enforcement is provider-independent: a Zoho, Fastmail,
  or self-hosted domain publishing reject with DKIM and a strict SPF fires it
  exactly as an M365 one does.

An operator who wants their conjunction needs the joint model probability or
an explicit deterministic claim rule. Multiplying two marginal posteriors is
valid only if their conditional independence under the observed evidence has
been established; separate field names do not establish it.

The same discipline applied to `federated_identity`, whose CPT parameterized
federation on `m365_tenant` alone. Federation exists without M365, so the
single-parent network systematically under-attributed it whenever the path ran
through anything else; v1.9.3 expanded the parents to include
`google_workspace_tenant`.

Two later corrections show the discipline is standing rather than historical.
v1.9.6 removed the `dkim_present` binding from the policy node: DKIM
publication is deliverability hygiene, and its likelihood ratio was
overstating what DKIM says about enforcement. The corpus-fitting reflex was to
lower the ratio until DKIM-only domains cleared 0.5, which would have improved
the agreement number while making the node a worse predictor of its own name.
CAL12 later moved the same node's prior from a hand-set 0.25 to 0.62 on
measured corpus base rates, making it the one corpus-grounded root in the
network.

**The principle.** A corpus run is a mirror that questions the topology, not a
fitter that minimizes a disagreement number. When a node disagrees with the
deterministic pipeline at high posterior, the first hypothesis is that the node
is conceptually wrong. CPT numbers are re-examined only after the topology is
clean.

### 4.10 Historical corpus sparsity

The v1.9.4 milestone used a selected 50-domain corpus with ten domains in each
of five supplied categories. The historical [run
memo](../validation/v1.9.4-calibration.md) records these percentages of domains
whose node display mass was at the floor:

| Node | Edge-proxied | Privacy | Financial | Defense | Government |
|---|---:|---:|---:|---:|---:|
| `aws_hosting` | 50% | 60% | 100% | 80% | 90% |
| `cdn_fronting` | 50% | 70% | 10% | 60% | 10% |
| `email_gateway_present` | 90% | 100% | 50% | 70% | 90% |
| `email_security_modern_provider` | 100% | 100% | 100% | 100% | 100% |
| `email_security_policy_enforcing` | 0% | 20% | 0% | 20% | 0% |
| `federated_identity` | 60% | 80% | 50% | 80% | 90% |
| `google_workspace_tenant` | 10% | 40% | 100% | 80% | 100% |
| `m365_tenant` | 60% | 50% | 20% | 50% | 20% |
| `okta_idp` | 90% | 90% | 90% | 100% | 100% |

Each ten percentage points represents one domain. These are fixed-corpus
descriptive rates, not population estimates or a classifier for organizational
posture. Small samples do not make intervals meaningless, but population
interpretation requires a justified sampling design. The historical model and
collection version also limit comparison with current output.

`sparse` does not mean absent, deliberately hidden, or insecure (section 4.5).
A zero policy-node sparse rate does not establish universal enforcing DMARC,
and a 100 percent Workspace sparse rate does not establish M365-only
deployment. The modern-provider node has no local bindings after the v1.9.3
split, so its display mass stays at the floor even when parent evidence moves
its posterior.

The historical survival ratio divides the high-model-support rate in the
corpus labeled hardened by that in the corpus labeled soft. The memo records
`email_gateway_present` 0.57, `cdn_fronting` 0.84,
`email_security_policy_enforcing` 0.98, `okta_idp` 1.21,
`federated_identity` 1.16, `aws_hosting` 1.09,
`google_workspace_tenant` 1.03, and `m365_tenant` 0.90. Values below or
above one describe lower or higher observed rates. The selected cohorts and
collection differences do not isolate a causal hardening effect; a small
denominator can make a ratio unstable.

These measurements do not validate deceptive-DNS robustness (section 4.11),
long-tail categories, or private cloud consumption that leaves no public
evidence.

### 4.11 Adversarial deception postures

Section 4.10 records sparsity on a selected historical corpus. This
subsection asks the harder question: how does the layer behave against a
posture that intends to mislead a passive observer? Pattern I (planted
administrative tokens) was measured end to end at the DNS-record layer on
2026-08-17
([adversarial corpus round](../validation/2026-08-17-adversarial-corpus-round.md)),
and its result is folded in below. The certificate-surface and rotation patterns
(F, G, H) remain qualitative: falsifying them needs a corpus that does not exist
at this layer, so what follows for them is a stated commitment about predicted
behavior, recorded so a future calibration run can confirm or refute it.

**Pattern F, wildcard-certificate rotation.** New certificates containing only
wildcard names contribute fewer explicit hostnames to CT enumeration. They do
not erase historical entries, establish one SAN per certificate, or imply
wildcard DNS resolution. The graph excludes wildcard names. If other records
stay fixed, apex mail and policy observations need not change. Sparse state,
posterior accuracy, and band width still depend on those other inputs and the
committed model; certificate shape alone guarantees none of them.

**Pattern G, short-TTL decoy CNAME chains.** The apex rotates CNAME targets
between observation windows so snapshots can disagree. A single lookup does
not retain those windows as a longitudinal conflict detector. The Bayesian
adapter currently projects conflicts on `display_name`, `auth_type`, `region`,
`tenant_id`, `dmarc_policy`, and `google_auth_type`; a changed CNAME target alone
does not populate that list. If retained source disagreement reaches one of
those fields, its penalty lowers display mass globally to the configured floor
(section 4.1). It does not change the posterior or guarantee a wide band near a
boundary mean. Rotation detection requires comparable snapshots and the
temporal contract in section 7.

**Pattern H, SAN-stuffing decoys.** The apex publishes certificates whose SAN
lists name unrelated services it does not run. The defense is upstream of this
layer: slug classification does not fire on a certificate SAN alone, requiring
a CNAME target, a verification record, or an MX, SPF, or NS pattern, so a SAN
claim without corroborating DNS never reaches the network as evidence. The
graph layer still ingests the stuffed edges, which is the section 2.3 caveat
about certificate size becoming apparent community structure.

**Pattern I, planted administrative tokens.** The apex publishes verification
records or SPF includes for vendors it does not use. Each is one static string,
free to publish, truthful as a DNS fact, and published by the operator itself,
so nothing about it is anomalous.

Measured end to end at the DNS-record layer on 2026-08-17
([adversarial corpus round](../validation/2026-08-17-adversarial-corpus-round.md)),
this is narrower than the earlier blanket "the one pattern the engine does not
handle." A partial record-role provenance gate already exists in
`bayesian_observations.signals_from_tenant_info`: the tenant, gateway, CDN, and
AWS observations fire only from evidence whose record type carries the claimed
role, so an administrative-only plant that produces the vendor slug does not move
the decision node. Over the seven gate-path administrative-token fixtures the
engine moved zero of seven nodes to supported. The status is therefore a
partly-closed vector with named residual gaps:

- **The gate blocks the plantable form on the gated nodes.** A planted
  verification TXT, an NS delegation, or a CAA record produces the vendor slug
  but not the role-typed evidence (a functional MX, DKIM, or role CNAME) the
  gated observations require, so that node's local binding stays inactive. The
  posterior can still move through evidence elsewhere in the network (section
  4.5). The slug enters inventory without supplying that local binding. Routing-shaped
  records in the positive fixtures still support the node under this model.
  An MX or CNAME reference to a vendor can itself be published without proving
  an active vendor account or successful traffic delivery. Record-role gating
  narrows the claim; it is not an unforgeability proof.
- **The declarative node moves on a declared policy, not on impersonation.** A
  published enforcing DMARC record adds its positive factor and removes the
  group-absence disconfirmer (section 3.3), so `email_security_policy_enforcing`
  goes supported, while a strict SPF record alone leaves it unresolved. But that
  is publishing your own declared policy, not impersonating a tenant; whether a
  published policy should count as support for "enforcing" is an open product
  question, not a false positive. Group reduction still keeps only the strongest
  fired binding per correlation group, so grouped derivatives of one planted
  record never stack.
- **The ungated routes are scalar, not record.** `federated_sso_hub` fires on
  `auth_type` and `okta_idp_observed` on `google_idp_name` with no record-role
  gate at all. Injecting those scalars moves federated_identity, m365_tenant,
  and okta_idp, and a lifted parent composes through the DAG to its children.
  But those scalars come from OIDC and UserRealm collection, not from DNS, so a
  pure-DNS adversary cannot set them; the record-role discipline the tenant
  nodes carry is simply missing on the IdP node, the clearest gap for the
  mitigation to close.

The mitigation is to generalize the existing gate: weight every binding by
detection provenance, and extend the record-role discipline to the scalar routes
and the IdP node. The functional corroborator the gate leans on is assumed
unforgeable, which is not itself proven: a CNAME to a real vendor edge, a nested
SPF include, or an NS delegation might pass a naive gate, so provenance weighting
is necessary here but not obviously sufficient. The catalogue files already
prescribe corroboration discipline; the inference layer honors it partially
today, and closing the rest is tracked engine work rather than a shipped
property. Section 5.6 states the acceptance property a fix must satisfy, and the
2026-08-17 corpus is its standing gate.

**What this subsection does not establish.** For the certificate-surface and
rotation patterns (F, G, H), these remain predictions from the design, not
measurements: falsifying them needs a controlled adversarial corpus at that
layer, synthetic where the posture must be exact, with predeclared supported
claims and permitted evidence. Silence at one node does not prevent support
propagating from another node. Pattern I is the measured exception: the 2026-08-17
corpus recorded above tested the record-plantable form end to end and the
record-role gate held (zero of seven administrative-only plants moved a gated
node to supported), and a record-layer disagreement fixture populated conflict
provenance. That does not establish temporal CNAME-rotation detection.
Section 5.6 states the acceptance property the
remaining commitment must satisfy.

## 5. Claim robustness envelopes

This section defines the candidate research direction. It is not a description
of current output.

### 5.1 Evidence units

Each claim-bearing unit should eventually carry:

$$
u=(x,s,n,r,v,[t_0,t_1],d,c,g,a,k),
$$

where:

- $x$: normalized value plus a raw-response reference or digest;
- $s$: subject the record describes, which may differ from the queried apex;
- $n$: namespace or record owner;
- $r$: source family and any provider attester;
- $v$: resolver, API, or collector vantage;
- $[t_0,t_1]$: observation window and freshness semantics;
- $d$: derivation path;
- $c$: claim family and scope;
- $g$: dependency group and causal origin;
- $a$: observation-opportunity state;
- $k$: manipulation class and assumed cost.

The observation-opportunity state should distinguish `not attempted`,
`observed value`, `observed empty`, `unavailable`, `not enabled`, and `not
applicable`. The current `degraded_sources` compatibility field cannot encode
that full state space. A future internal ledger should own these semantics and
derive the legacy field, not the reverse.

The manipulation class is an explicit model assumption. It is not learned from
the target. A useful initial taxonomy is:

| Class | Typical property | Examples |
|---|---|---|
| Provider-attested | Response is controlled by the provider | tenant namespace or identity metadata |
| Functionally routing | Change can disrupt live traffic or mail | MX, NS, service CNAME |
| Standards-declarative | Public policy has defined syntax and scope | DMARC, MTA-STS |
| Administrative | Cheap to add, remove, or leave stale | site-verification TXT token |
| Historical structural | Hard to erase retroactively but not proof of current use | CT SAN history |
| Derived | Adds no independence beyond its inputs | signal or rollup from one RRset |

Costs must be claim-specific. Changing MX may be costly for an email-routing
claim but irrelevant to a cloud-hosting claim. A scalar-budget prototype
requires a predeclared strictly positive **additive model cost** for every
admissible nonidentity manipulation; the identity has cost zero, and forbidden
actions are excluded or assigned infinite cost. These are sensitivity
parameters, not measured money or effort. Strict positivity makes budget zero
the exact-observation relation. If maintainers can defend only an ordinal
ordering, the model must use vector or lexicographic budgets and
inclusion-minimal flip sets instead of adding the ranks.

For a Pareto or lexicographic vector budget, every admissible nonidentity action
must likewise have a componentwise nonnegative, nonzero cost vector, and only
the identity may have the zero vector. Otherwise a zero-vector manipulation
would enter the zero budget and invalidate exact-observation collapse.

The preferred first threat budget is therefore a Pareto or lexicographic
vector, for example `(administrative planting, optional-declaration hiding,
routing changes, provider-attestation changes)`. It supports a defensible
statement such as "robust to any two administrative tokens, but not to one
provider-attestation change" without pretending unlike operations share an
objective exchange rate.

### 5.2 Observation compatibility, not forward perturbation alone

Partial identification is an inverse problem. Transforming the observed record
forward into more hypothetical records measures sensitivity, but it does not by
itself identify which latent states could have produced the record that recon
actually saw. The current network also does not define a normalized joint law
over evidence records: it combines latent-node CPTs with per-binding virtual
evidence factors and a max-LLR dependency-group heuristic. Those ingredients
define a scoring procedure, not a generative observation model.

The first prototype should be Boolean and threshold-free. Use separate reviewed
predicates $h^+_{m,C}(z)$ for positive public support and
$h^-_{m,C}(z)$ for authoritative public disconfirmation. For each
$\sigma\in\lbrace +,-\rbrace$, use the compatibility set defined below and report

$$
\underline h_b^\sigma(C,o)=
\min_{(m,z)\in\mathcal K_b^T(o)}h^\sigma_{m,C}(z),
\qquad
\overline h_b^\sigma(C,o)=
\max_{(m,z)\in\mathcal K_b^T(o)}h^\sigma_{m,C}(z).
$$

Each side has a must/may interval. A zero positive interval means only that no
compatible state supports the positive predicate; it is not a negative fact.
For one fixed $(m,z)$, positive support only is **supported**, authoritative
negative support only is **disconfirmed within the admitted public model**,
both are **conflicted**, and neither is **unresolved**. At every budget,
including zero when $\mathcal M$ admits multiple models, the robust summary
requires positive must-support with negative support impossible, negative
must-support with positive support impossible, or must on both sides for robust
conflict. Every other combination remains unresolved and all four interval
endpoints are shown. Budget zero collapses to the fixed-state mapping only under
the later singleton-model and exact-observation conditions. These evidence
states are deterministic and paraconsistent; they are not probabilities.

The score envelope is a secondary generalization for diagnostics that genuinely
need a graded support functional. Let $z$ be a claim-relevant **clean
public-evidence state**: the units that a
complete successful collection would expose under the admitted model. It is
still not the target's full private configuration. Each admitted model $m$
must define a nonempty feasible set $\mathcal Z_m$ and a deterministic support
functional

$$
s_m(C,z)\in[0,1].
$$

For the current engine, $s_m$ can be the replayed model-relative score under
one explicit parameter and grouping configuration. It must not be called a
probability merely because its range is $[0,1]$. For budget $b$, admitted
model $m$, and reviewed threat model $T$, define an observation relation
$o\in\mathcal H_{b,m}^T(z)$. Indexing the channel by $m$ makes the admitted
missingness and dependence assumptions operational rather than leaving them in
an unused model label. For every fixed $m$, budgets must be nested:
$\mathcal H_{b,m}^T(z)\subseteq\mathcal H_{b',m}^T(z)$ whenever
$b\le b'$. The relation may:

- hide units from $z$;
- plant units into $o$;
- retain or replace stale administrative units;
- represent a failed collector as unobserved, never as a clean negative;
- transform one dependency group as one causal unit;
- preserve units outside the declared threat model.

Let $\mathcal M$ be the admitted parameter, dependence, and missingness model
class. The observational compatibility set is

$$
\mathcal K_b^T(o)=
\lbrace (m,z):m\in\mathcal M,\ z\in\mathcal Z_m,\
o\in\mathcal H_{b,m}^T(z)\rbrace.
$$

The feasibility condition excludes model-impossible states. A reported envelope
requires $\mathcal K_b^T(o)\ne\varnothing$; an empty set means the admitted
model and threat assumptions are inconsistent with the observation. For claim
$C$, define the robust score envelope

$$
\underline s_b(C,o)=
\inf_{(m,z)\in\mathcal K_b^T(o)}s_m(C,z),
$$

$$
\overline s_b(C,o)=
\sup_{(m,z)\in\mathcal K_b^T(o)}s_m(C,z).
$$

These are pointwise model-and-threat-relative score bounds over an unknown
compatible clean state. They are not probability bounds or an identification
region. A probabilistic extension must replace this support-functional model
with a coherent observation model. Let $X$ be the full latent target state
needed by the claim, let $Z=g(X)$ be its clean public-evidence state, and let
$R$ contain observation-process state such as target intent, source
availability, and collector condition. Every admitted $m$ must define a
normalized joint law $P_m(C,X,R)$ and an observation kernel
$q_m(o\mid C,X,R)$. It then defines

$$
P_m(C=1\mid O=o)=
\frac{\int q_m(o\mid C=1,x,r)\,P_m(C=1,dx,dr)}
{\sum_{c\in\lbrace 0,1\rbrace}\int q_m(o\mid C=c,x,r)\,P_m(C=c,dx,dr)},
$$

when the denominator is positive. Omitting $C$ from the kernel asserts the
conditional independence $O\mathbin{\perp\perp}C\mid X,R$, which must be
defended rather than implied. If only marginal constraints are specified, the
compatible joint laws and observation kernels they admit are themselves the
model class. Probabilistic partial-identification bounds are the infimum and
supremum of this conditional over that explicit ambiguity class, not over an
unspecified extra mixture. An incomplete class can provide an unsupported
narrow range; a deliberately enlarged class may provide only an outer
sensitivity bound. If a prototype evaluates forward transformations $a(o)$
alone, it must call the result a **sensitivity envelope**, not an identification
region.

### 5.3 Decision semantics

The primary Boolean result uses no score threshold:

- robustly supported when $\underline h_b^+=1$ and
  $\overline h_b^-=0$;
- robustly disconfirmed within the public model when
  $\underline h_b^-=1$ and $\overline h_b^+=0$;
- robustly conflicted when $\underline h_b^+=\underline h_b^-=1$;
- unresolved otherwise, with all four must/may endpoints retained.

The secondary graded diagnostic uses a predeclared support threshold $\tau$:

$$
\text{supported if }\underline s_b\ge\tau,
$$

$$
\text{not supported across admitted states if }\overline s_b<\tau,
$$

$$
\text{unresolved otherwise}.
$$

The second label deliberately avoids "absent." A public channel can fail to
support presence without establishing real-world absence.
These threshold labels remain model diagnostics and never override any primary
Boolean claim state.

An operator-facing explanation should report:

- the orthogonal construction, collection, claim-state, and time semantics;
- the Boolean must/may result and, when enabled, lower and upper robust score;
- the threat model and budget;
- the clean-to-observed hiding and planting actions that attain each bound, or
  an epsilon-optimal witness and its declared tolerance;
- the provenance and assumed cost of those units;
- whether the decision changes.

The most valuable result may be a small certificate:

> The claim remains supported when any one administrative observation is treated
> as planted, but not when the provider-attested observation is treated as
> planted.

That is more actionable than a narrow heuristic band around 0.93.

#### 5.3.1 Deterministic provenance-certificate algebra

Before optimizing a score, recon can make its deterministic core
proof-carrying. Let $U(o)$ be canonical observed dependency units and let
$\mathrm{Atoms}(U)$ be the signed normalized and derived atoms exposed
by a unit set. Each observed atom $a$ retains an antichain
$\mathrm{Orig}_o(a)\subseteq 2^{U(o)}$ of minimal raw-origin unit
environments. Alternatives remain separate: if either $u_1$ or $u_2$
derives $a$, the environments are $\lbrace u_1\rbrace$ and $\lbrace u_2\rbrace$, not
$\lbrace u_1,u_2\rbrace$. Lift one atom proof $E$ to dependency units by distributive
choice:

$$
\Pi_o(E)=\min_{\subseteq}
\lbrace\bigcup_{a\in E}Q_a:
Q_a\in\mathrm{Orig}_o(a)\ \text{for every }a\in E\rbrace.
$$

Let $J$ be a reviewed monotone signed rule system. Write
$E\vdash_J^+ C$ and $E\vdash_J^- C$ for positive and authoritative-negative
derivability. The relation is paraconsistent by construction: deriving both
signs records conflict and does not entail an unrelated claim. Let
$\mathrm{valid}_J(E)$ mean that $E$ contains none of the explicit
minimal nogood environments declared by the contract. Let $\Omega_C$ be the
bounded universe of possible signed atoms under the claim contract, including
fixed and manipulable atoms. For a narrow public claim $C$, first define the
model-wide proof templates

$$
\widehat{\mathcal P}_C^T=\min_{\subseteq}
\lbrace E\subseteq\Omega_C:\mathrm{valid}_J(E),\ E\vdash_J^+ C\rbrace,
$$

$$
\widehat{\mathcal N}_C^T=\min_{\subseteq}
\lbrace E\subseteq\Omega_C:\mathrm{valid}_J(E),\ E\vdash_J^- C\rbrace.
$$

Atom-proof validity alone does not guarantee that its chosen raw origins can
coexist. Let $\mathrm{Base}(Q)$ contain only the signed base assertions supplied
by dependency units $Q$, and let $\mathrm{Cl}_J$ recompute deterministic signed
closure. Each origin environment for an atom must reproduce that atom from
its own base assertions. Define validity of a lifted unit environment by

$$
\mathrm{valid}^{\mathrm{unit}}_J(Q)=
\mathrm{valid}_J\bigl(\mathrm{Cl}_J(\mathrm{Base}(Q))\bigr).
$$

This checks the full closed raw-origin environment against every declared
nogood. For example, if $x\land y$ is a nogood, $x\vdash_J a$,
$y\vdash_J b$, and $a\land b\vdash_J^+C$, the atom proof
$\lbrace a,b\rbrace$ cannot bypass the nogood by hiding its origins $x,y$.
Apply this test separately to each candidate proof environment $Q$, never to
the entire observed ledger. Independently valid positive and negative proofs
remain available even when their combined ledger contains a nogood.

The active dependency-unit certificate antichains for the observed snapshot are

$$
\mathcal P_C(o)=\min_{\subseteq}
\lbrace Q:E\subseteq\mathrm{Atoms}(U(o)),\
 \mathrm{valid}_J(E),\ E\vdash_J^+ C,\ Q\in\Pi_o(E),\
 \mathrm{valid}^{\mathrm{unit}}_J(Q)\rbrace,
$$

$$
\mathcal N_C(o)=\min_{\subseteq}
\lbrace Q:E\subseteq\mathrm{Atoms}(U(o)),\
 \mathrm{valid}_J(E),\ E\vdash_J^- C,\ Q\in\Pi_o(E),\
 \mathrm{valid}^{\mathrm{unit}}_J(Q)\rbrace.
$$

An absent optional record never enters $\mathcal N_C$. A negative atom exists
only when the claim contract identifies an authoritative publication point, its
observation opportunity completed successfully, and the returned value has the
documented negative meaning.

The four snapshot states follow directly: neither family means unresolved,
positive only means supported, negative only means disconfirmed within the
public model, and both mean conflicted. No inconsistent input is allowed to
erase the other side.

The snapshot reducer has a useful algebra that should be explicit in the first
claim contract. Encode the state as

$$
q_C(o)=(p_C(o),n_C(o))\in\lbrace 0,1\rbrace^2,
$$

where each coordinate records whether its certificate family is nonempty.
Order these final states by information, componentwise. Componentwise join

$$
(p_1,n_1)\sqcup_k(p_2,n_2)=(p_1\lor p_2,n_1\lor n_2)
$$

combines already-derived signed assertions only when no rule can use premises
split across the two views. It is not the general evidence-view merge. A rule
such as $a\land b\vdash_J^+C$ can receive $a$ from one view and $b$ from
another even though both separate state projections are unresolved.

The general merge acts on canonical provenance ledgers. For ledgers $L_1$
and $L_2$, define

$$
L_1\sqcup_U L_2=\mathrm{dedup}(L_1\cup L_2),
$$

then recompute atoms, signed closure, certificate antichains, and $q_C$ from
the merged ledger. Canonical ledger union is associative, commutative, and
idempotent. For the reviewed monotone rule system, its projected claim state is
monotone in the information order: adding a view can establish either sign or
expose conflict, but cannot erase an established sign. The projection is not a
join homomorphism because cross-view derivations can create a sign absent from
both separate projections. Retraction or expiry is not an inverse union; it
requires replay from the remaining ledger. The information order must not be
misread as a truth, severity, or quality ranking. In particular, conflicted is
more informed than either one-sided state, not more true.

This has a compact provenance-semiring interpretation. Give each canonical raw
unit a symbol $x_u$; conjunction multiplies symbols, alternative derivations
add terms, and idempotence prevents a duplicate derived view from acquiring new
weight. The reduced expression

$$
\rho_C^+(o)=\bigoplus_{E\in\mathcal P_C(o)}
 \bigotimes_{u\in E}x_u
$$

has one minimal monomial per support certificate. It can be implemented with
bounded antichains of frozen sets, without a new runtime dependency. A minimum
forward deletion cut is then a transversal that intersects every active
positive certificate. The earlier Boolean coordinate satisfies $p_C(o)=1$
exactly when $\rho_C^+(o)\ne 0$; the coordinate and symbolic provenance
polynomial are different types.

A planting completion cannot be obtained from $\mathcal P_C(o)$, because its
members are already-observed dependency units. Let
$\mathcal A_{T,\mathrm{atom}}^+(o)\subseteq \Omega_C\setminus\mathrm{Atoms}(U(o))$
be the explicitly frozen set of
base atoms the threat model permits an operator to assert directly. Let
$\Lambda_T^+(o)$ be the finite family of admissible tagged dependency-unit
addition sets whose direct base-atom assertions lie in that set. One action may
assert several dependent base atoms. Let $\phi_A(U)$ be the dependency-unit
state after applying tagged actions $A$. For a
planting-only threat model, the valid completion-action antichain is

$$
\mathcal G_{C,+}^T(o)=\min_{\subseteq}
\lbrace A:E\in\widehat{\mathcal P}_C^T,\
 A\in\Lambda_T^+(o),\
 S_A=\mathrm{Cl}_J(\mathrm{Atoms}(\phi_A(U(o)))),\
 \mathrm{valid}_J(S_A),\ E\subseteq S_A\rbrace.
$$

This family deliberately excludes an addition that conflicts with an observed
mutually exclusive value. For a threat model that permits replacement, let
$A=(A^-,A^+)$ contain tagged dependency-unit removals and additions. The
general forward support-completion family minimizes $A$ subject to
$T$-admissibility,
$\mathrm{valid}_J(S_A)$ for
$S_A=\mathrm{Cl}_J(\mathrm{Atoms}(\phi_A(U(o))))$, and the
existence of some $E\in\widehat{\mathcal P}_C^T$ with $E\subseteq S_A$.
Every certificate,
completion, antichain minimum, and cost therefore maps atom derivations back to
dependency-unit actions first. Required removal or replacement actions remain
visible instead of being mislabeled as planting. These are exact deterministic
explanations, not likelihood or independence claims.

Every material claim contract should declare its subject, scope, time
semantics, positive alternatives, authoritative negatives, source-success
preconditions, dependency groups, freshness rules, renderer surfaces, and
regression fixtures. That registry is the deterministic foundation that the
score envelope and any later probabilistic model must consume.

The first bounded implementation now exists internally as
`dns.dmarc.valid_policy_is_reject.v1`; its exact contract, proof obligations,
limits, and primary standards are recorded in
[claim-contracts.md](claim-contracts.md). It uses fresh valid `p=reject` as
positive support and fresh valid `p=none` or `p=quarantine` as explicit
disconfirmation. Empty and invalid observations remain unresolved because the
current resolver does not retain DNS authority sections or DNSSEC denial
validation. That choice is stricter than reconstructing a negative certificate
from an empty list after collection.

The bounded antichain prototype is exact only for monotone derivations over
explicit atoms, including explicit authoritative-negative atoms maintained in a
separate family. Negation as failure, winner selection, nonmonotone thresholds,
thresholds over negative contributions, and stale-time invalidation require
explicit opportunity, value, validity, and nogood atoms or must remain outside
the first evaluator. The implemented evaluator further requires an acyclic Horn
program and computes deterministic topological closure. At-least-k rules over
monotone positive atoms remain within the algebra when encoded without cycles.
The shipped DMARC evaluator declares no nogood environments; the explicit
raw-origin validity filter above is part of the general research definition,
not a claim that the current evaluator implements arbitrary nogood contracts.

The same registry can define a narrow implication order over canonical claim
classes. Logical implication is first a preorder; mutually entailing claims
must be canonicalized or quotiented into one class. Define
$[C_1]\preceq[C_2]$ when $C_2$ entails $C_1$, so maximal entailed classes
are the strongest justified claims. "Administrative Microsoft token
published," "Exchange Online routing observed," and "Entra tenant namespace
returned" are distinct and often incomparable; none automatically entails
product deployment or use. A larger number must never move a claim upward in
this order.

### 5.4 Robustness radius and minimal compatibility certificates

For a scalar extended-real budget or another explicitly order-complete,
totally ordered nested budget domain, let
$D_b^{\mathrm{bool}}(C,o)$ be the robust Boolean state from section 5.3. For a
budget-zero state that is supported, disconfirmed, or conflicted, its decision
radius is

$$
r_T^{\mathrm{bool}}(C,o)=
\inf\lbrace b:D_b^{\mathrm{bool}}(C,o)\ne D_0^{\mathrm{bool}}(C,o)\rbrace.
$$

This definition covers robust support, disconfirmation, and conflict. For
example, support is lost when positive must-support fails or negative support
becomes possible; conflict is lost when either must bound fails. The radius is
undefined for an unresolved budget-zero state. Nested compatibility sets cannot
turn that initial ambiguity into a robust decision, so applying the formula to
it would yield an empty flip set and a misleading infinite radius. The infimum
is a least cost only when a flip witness attains it.

A componentwise Pareto budget is not totally ordered and must not be reduced to
one infimum. With $b\preceq b'$ meaning componentwise no greater, let
$F_T(C,o)=\lbrace b:D_b^{\mathrm{bool}}(C,o)\ne D_0^{\mathrm{bool}}(C,o)\rbrace$.
When the flip set has attainable minimal points,
report the Pareto-minimal flip frontier

$$
\mathcal R_T^{\mathrm{bool}}(C,o)=
\min_{\preceq}\lbrace b:D_b^{\mathrm{bool}}(C,o)
 \ne D_0^{\mathrm{bool}}(C,o)\rbrace.
$$

Incomparable points remain separate. A finite prototype has such a frontier
whenever its nonempty budget set is finite. For continuous budgets in a
finite-dimensional nonnegative orthant, also report the Pareto-minimal boundary
of $\overline{F_T(C,o)}$. Mark each boundary point as attained exactly when
it belongs to $F_T(C,o)$; attained and unattained portions can coexist.
For example, the upward-closed flip set
$\lbrace(x,y):x>0,\ y\ge1\rbrace\cup
\lbrace(x,y):x\ge1,\ y\ge0\rbrace$ has the sole attained minimal point
$(1,0)$, but its closure has minimal points $(0,1)$ and $(1,0)$.
Reporting only the attained point would omit the first flip branch. Attach
declared-tolerance epsilon-Pareto witnesses to each unattained boundary point;
do not call those points attained costs. Other continuous budget domains need
their topology and boundary-existence conditions declared separately. A
lexicographic budget can use the radius form only
after its priority order is declared and its domain is finite, discrete and
well-ordered, or otherwise shown order-complete. Totality alone is insufficient.

The graded score radius below is secondary and has the same order-completeness
requirement.

For a claim with $\underline s_0\ge\tau$, define the lower-support radius

$$
r_T^-(C,o)=\inf\lbrace b:\underline s_b(C,o)<\tau\rbrace.
$$

For a claim with $\overline s_0<\tau$, define the upper-support radius

$$
r_T^+(C,o)=\inf\lbrace b:\overline s_b(C,o)\ge\tau\rbrace.
$$

Use $\inf\varnothing=\infty$. The upper-support radius can be finite because
the inverse model admits clean supporting evidence hidden on the path from
$z$ to $o$; it is not a forward planting radius. In a general infinite model,
$\overline s_b=\tau$ can also hold without any compatible state attaining
$s_m(C,z)\ge\tau$. This is loss of the strictly-below-threshold envelope
decision, not an actual supporting-state witness. Report that boundary-only
case explicitly, with epsilon-optimal score witnesses labeled as remaining
below the threshold. At each budget, envelope crossing and existence of a
supporting-state witness agree when the supremum is attained, as in the finite
prototype. A lower-support inverse
witness can instead classify an observed supporting unit as planted, admit a
clean disconfirming unit hidden from observation, or combine allowed actions.
All witness directions are stated from clean state to observation.

For a finite cap $B$, let $\mathcal A_{T,B}(m,z,o)$ be the family of all
admissible sets of nonidentity clean-to-observed manipulation actions that
produce $o$ from $(m,z)$ within that cap. The identity realization contributes
the empty action set. Different action realizations of the same compatible
state remain separate; arbitrarily choosing one could omit a cheaper or
inclusion-minimal certificate. For a budget-zero Boolean decision $D$, define
an adverse-state predicate

$$
\mathrm{bad}_D(m,z)=
\begin{cases}
h^+_{m,C}(z)=0\ \text{or}\ h^-_{m,C}(z)=1,
 &D=\text{supported},\\
h^-_{m,C}(z)=0\ \text{or}\ h^+_{m,C}(z)=1,
 &D=\text{disconfirmed},\\
h^+_{m,C}(z)=0\ \text{or}\ h^-_{m,C}(z)=0,
 &D=\text{conflicted}.
\end{cases}
$$

The primary inverse Boolean flip-certificate antichain is

$$
\mathcal W_{B,D}^{\mathrm{bool}}=
\min_{\subseteq}
\lbrace A:(m,z)\in\mathcal K_B^T(o),\
 A\in\mathcal A_{T,B}(m,z,o),
 \mathrm{bad}_D(m,z)\rbrace.
$$

It is undefined for an unresolved initial state. The secondary graded
lowering and raising certificate families are

$$
\mathcal W_{B}^{\mathrm{score},-} = \min_{\subseteq}
\lbrace A:(m,z)\in\mathcal K_B^T(o),\
 A\in\mathcal A_{T,B}(m,z,o),\ s_m(C,z)<\tau\rbrace,
$$

$$
\mathcal W_{B}^{\mathrm{score},+} = \min_{\subseteq}
\lbrace A:(m,z)\in\mathcal K_B^T(o),\
 A\in\mathcal A_{T,B}(m,z,o),\ s_m(C,z)\ge\tau\rbrace.
$$

Report only the family relevant to the current decision and diagnostic. First
enumerate every inclusion-minimal member, then identify radius-attaining members
under a total order or Pareto-minimal cost vectors under a partial order.
The raising family contains only actual threshold-crossing witnesses and can
be empty at a boundary-only upper-envelope crossing. Such a crossing has no
raising certificate, even when its budget attains the diagnostic radius. If a
radius infimum is not attained, report epsilon-optimal budget witnesses without
calling them least-cost certificates; distinguish these from epsilon-optimal
score witnesses that do not cross the threshold. These antichains connect
recon's provenance graph to fault-tree-style explanations and distinguish
"one stale TXT token" from "a provider-attested response plus a live routing
change" without pretending the
assigned costs are objective facts. Radii or frontiers must not be compared
across claim families with different cost or threat models.

The prototype should enforce these exact invariants:

- nested budgets make each signed $\underline h_b^\sigma$ and
  $\underline s_b$ non-increasing, and each
  $\overline h_b^\sigma$ and $\overline s_b$ non-decreasing;
- at budget zero, an exact observation relation and singleton model collapse
  both bounds to the current model-relative support;
- duplicating a derived view inside one dependency unit changes neither bound;
- enlarging the compatibility or model class cannot narrow the envelope;
- every finite Boolean or graded compatibility certificate replays to its
  stated adverse predicate or score-threshold transition.

### 5.5 Tractability

At recon's current scale, the first implementation does not require a new
inference library.

For a finite evidence-unit set, finite parameter grid, strictly positive
additive costs for nonidentity manipulations, and small budgets,
enumerate compatible latent states or use branch and bound. Extrema are attained
in that finite prototype. In a continuous model, extrema are attained when the
actual nonempty compatibility set $\mathcal K_b^T(o)$ is compact and the
objective is continuous on it; otherwise report epsilon-optimal witnesses rather
than claiming a minimizer exists. As a separate forward-sensitivity
subproblem, a local log-odds model with additive unit values
$v_u=\log LR_u$ and costs $k_u$ has the worst-deletion problem

$$
\min_{d_u\in\lbrace 0,1\rbrace}
\bigl(\log O_0+\sum_u(1-d_u)v_u\bigr)
\quad\text{subject to}\quad
\sum_u k_u d_u\le b.
$$

This is a small 0-1 knapsack problem. The simple equal-cost case removes the
largest positive manipulable unit values first. That result is valid only for
the specified additive model. The full DAG can initially use exact repeated
inference over transformed evidence sets. Credal variable elimination is a
later option only if parameter sets demonstrate measured value and remain
tractable.

### 5.6 Addition matters as much as suppression

The shipped suppression property studies hiding positive evidence. recon's
highest-risk false-positive case is often the reverse: a cheap administrative
token can be planted or left stale. A robust design must test both directions.

Minimum acceptance properties for a prototype:

- in separately labeled forward planting sensitivity, administrative-only
  additions cannot create a supported deployment decision;
- provider-attested or functionally necessary evidence can preserve a useful
  lower bound;
- source failure never becomes evidence of absence;
- grouped derivatives never count as independent units;
- the explanation identifies the exact perturbation that changes the decision;
- negative results remain publishable and can terminate the approach.

The 2026-08-17 adversarial DNS-record corpus
([round memo](../validation/2026-08-17-adversarial-corpus-round.md),
`validation/adversarial_corpus/`) is the standing baseline for these properties.
It measures the record-plantable form of forward planting sensitivity against the
shipped engine (zero of seven administrative-only plants moved a gated node to
supported), retains model support on the positive routing-record fixtures, and
names the ungated scalar routes a complete gate must still close. A mitigation
must keep that corpus at its measured floor.

### 5.7 Inverse certificates and forward sensitivity are different objects

The primary $\mathcal W_{B,D}^{\mathrm{bool}}$ family and secondary
$\mathcal W_B^{\mathrm{score},-}$ or
$\mathcal W_B^{\mathrm{score},+}$ families solve named inverse compatibility
problems: which clean states and clean-to-observed actions could explain the
record recon saw and violate the selected decision condition? A separate
fixed-model forward analysis starts at $o$. Let $D_{m_0}(o)$ be the decision
under one frozen model, and let $d_A(o)$ and $p_A(o)$ apply tagged
dependency-unit deletion and addition actions in $A$. Freeze finite families
$\mathfrak D_T(o)$ and $\mathfrak P_T(o)$ of such action sets. A deletion
action may remove only a present hideable unit. An addition action creates an
admissible dependency unit and may directly assert only base atoms in the
frozen $\mathcal A_{T,\mathrm{atom}}^+(o)$ set from section 5.3.1. The rule
system then recomputes deterministic derived closure; those consequences need
not themselves be plantable and receive no independent planting action. An
action cannot relabel a nonmanipulable provider base atom as plantable. Let
$\mathrm{feasible}_{m_0}(o')$ reject transformed observations that
violate the claim contract's value, nogood, dependency, or source-opportunity
constraints. The inclusion-minimal forward flip families are

$$
\mathcal F_{\mathrm{del}}=
\min_{\subseteq}\lbrace A\in\mathfrak D_T(o):
\mathrm{feasible}_{m_0}(d_A(o)),\
D_{m_0}(d_A(o))\ne D_{m_0}(o)\rbrace,
$$

$$
\mathcal F_{\mathrm{add}}=
\min_{\subseteq}\lbrace A\in\mathfrak P_T(o):
\mathrm{feasible}_{m_0}(p_A(o)),\
D_{m_0}(p_A(o))\ne D_{m_0}(o)\rbrace.
$$

These families are antichains in the Boolean lattice. For a monotone Boolean
decision rule they resemble minimal cut and path sets from reliability theory,
but the current DAG is not assumed monotone, so every candidate must replay
against the actual scorer. A forward deletion can numerically resemble an
inverse planting witness, and a forward addition can resemble inverse hiding,
but the sets are interchangeable only after proving clean-state feasibility,
action-direction and cost symmetry, and scorer equivalence. The product must
never silently substitute one for the other.

For a currently supported Boolean claim, its inverse adverse-witness antichain
can create a conditional operator action. Let
$\mathcal A=\mathcal W_{B,\mathrm{supported}}^{\mathrm{bool}}$. For each
$A\in\mathcal A$, let $V_{\mathrm{confirm}}(A)$ be the observed units whose
plant action would be excluded by the specific verification outcome "confirmed
genuine." If any $V_{\mathrm{confirm}}(A)$ is empty,
verifying existing public facts cannot block every inverse lowering certificate,
and the result must say so. Otherwise assign each verifiable unit a predeclared
nonnegative verification cost $w_u$. A minimum-cost conditional inspection
set is the weighted hitting-set problem

$$
\min_H\sum_{u\in H}w_u
\quad\text{subject to}\quad
H\cap V_{\mathrm{confirm}}(A)\ne\varnothing
\qquad\text{for every }A\in\mathcal A.
$$

The result answers "which observed public facts should I verify independently
first, if confirmation excludes their planting explanations?" It is not a
guaranteed witness-blocking set before the outcomes are known and does not
pretend that evidence weights are calibrated probabilities.
Exact enumeration can use antichain pruning: once a certificate is found, no
strict superset can be inclusion-minimal. Because either inverse or forward
antichain can still be exponential, every output must declare whether enumeration
was complete; a capped list of examples is not a certificate of global
robustness.

### 5.8 Resolving evidence and the observation frontier

An unresolved result becomes useful when recon can say what would resolve it.
For a finite compatible-witness family $W$ that exhausts every admitted
witness relevant to the claim, action $q$, and possible outcome
$y\in\mathcal Y_q$, let $R_{q,y}\subseteq W$ be the witnesses ruled out by
that outcome. For a fixed nonadaptive batch plan $Q$ and one jointly feasible
outcome vector $y_Q$, the survivors are

$$
W_{Q,y_Q}=W\setminus\bigcup_{q\in Q}R_{q,y_q}.
$$

A plan identifies the signed state only when, for every feasible outcome
vector, the survivor set is nonempty and all survivors have one common pair
$(h^+,h^-)$. It resolves the claim only when that pair is supported
$(1,0)$, disconfirmed $(0,1)$, or conflicted $(1,1)$. A common
$(0,0)$ pair establishes that the admitted public model remains unresolved;
it is signed-state identification, not claim resolution. Minimum-cost
nonadaptive claim resolution minimizes the declared batch action cost under the
stronger condition. It is not a global adaptive optimum: an outcome-contingent
decision tree may choose later actions from earlier results and achieve a lower
worst-case cost. Any adaptive extension must define that policy tree, feasible
branches, stop rule, and worst-case cost explicitly. A resolution certificate
additionally requires
`enumeration_complete=true`. A capped or otherwise incomplete family may report
only an outcome-conditional result over the enumerated witnesses; omitted
witnesses could retain another claim state. Eliminating every witness is model
inconsistency, not resolution. The simple weighted hitting set in section 5.7
is a conditional special case for one target decision and verification outcome
that eliminates adverse witnesses while retaining at least one nonadverse
witness.

When no plan satisfies the outcome-robust condition, report that impossibility,
the residual states, and any outcome-conditional plans rather than forcing a
recommendation.

Without a defensible outcome distribution, recon must not call this expected
information gain or report expected bits. It can report deterministic quantities:
which witnesses an action can rule out, the worst-case residual claim state,
whether complete resolution is possible, and the minimal resolving-action
antichain.

Every action belongs to an explicit interaction profile:

- replay cached evidence under the same interpretation version;
- retry an unavailable public source after its freshness or backoff window;
- read an additional approved DNS record type;
- perform a clearly labeled target-visible or opt-in request;
- ask the operator to verify an observed fact independently.

The default lookup already exhausts its bounded source plan, so the honest next
step will often be "retry this unavailable source," "verify this provider-attested
identifier," or "the public channel cannot resolve this claim." This mechanism
must not become permission for unbounded probing.

## 6. Typed topology and graph correlation research

The graph layer should be improved only after its residual product value is
measured.

Three graph objects must remain separate:

1. a provenance graph showing how raw observations and assumptions produced a
   claim;
2. a typed public-namespace topology showing directed roles such as queried
   apex, record owner, routing target, provider attester, gateway, and
   historical certificate co-member;
3. an inferred co-occurrence or community graph used only as a model-relative
   exploratory diagnostic.

A shared tenant identifier, MX target, administrative token, CT certificate,
parent-vendor label, and public CA issuer are different relation types. They
must not collapse into one `relatedness` score. Exact provider-attested
identifiers can be strong administrative co-tenancy observations without
establishing ownership. Shared routing can show a common dependency without
showing common control. Administrative tokens can be copied or stale. Generic
vendors and public issuers are high-degree cohort coincidences.

Every relation should carry direction, source and target roles, provenance,
observation window, interaction class, and specificity class. Any cohort-local
ubiquity discount must use all eligible observation opportunities, not only
positive nonempty records, and must expose the denominator. Capped graph output
must expose completeness and omitted counts before absence can be interpreted.

### 6.1 Correct the data representation first

Certificates are naturally hyperedges or nodes in a bipartite graph. Before
changing the community algorithm, compare the current clique projection with:

1. a certificate-to-host bipartite graph;
2. a native hypergraph view;
3. a normalized projection in which each $k$-SAN certificate contributes a
   fixed total pair weight, for example

$$
w_{ij}^{(c)}=\frac{1}{\binom{k_c}{2}},\qquad k_c\ge 2.
$$

This prevents a large certificate from contributing quadratically more total
weight merely because it contains more names. The exact normalization is a
hypothesis to test, not a predetermined winner.

### 6.2 Separate three kinds of stability

- **optimizer stability:** repeated seeds on one graph;
- **data stability:** repeated CT snapshots or bootstrap samples;
- **model stability:** partitions under reasonable weighting and resolution
  choices.

Report pairwise co-assignment probabilities or consensus partitions only after
the bootstrap design is predeclared. A high modularity value or seed ARI cannot
substitute for data stability.

### 6.3 Require a null comparison

At minimum, compare observed partition structure with a degree-preserving null
that respects the chosen graph representation. If a stochastic block model is
considered later, use model selection and a degree-corrected or weighted form
appropriate to heavy-tailed infrastructure graphs. Do not add that complexity
unless it beats the corrected simple baseline on the named product metric.

### 6.4 Graph acceptance test

Use synthetic heavy-tailed and multi-tenant certificates plus
operator-supplied related-domain sets. Keep ownership assertions outside the
model. Predeclare:

- pairwise false co-membership rate;
- pairwise precision and recall where a supplied grouping exists;
- adjusted Rand index or variation of information;
- bootstrap co-assignment stability;
- coverage and abstention rate;
- latency and allocation budget.

Hub-dominated, truncated, or data-unstable graphs should abstain instead of
returning relationship-looking connected components. If graph coverage or
precision does not beat simple co-occurrence summaries, keep the stable field
for compatibility and move the feature out of primary presentation.

## 7. Temporal correlation

Public configuration change is often more identifiable than private stack
state. recon already has snapshot delta behavior. A later research path can
model sequences of directly observed facts:

$$
Y_t=(\text{MX RRset},\text{NS RRset},\text{DMARC RRset},
 \text{tenant response},\text{CT entries},\text{source status},\ldots)_t.
$$

Derived provider or product labels are interpretation outputs, not components of
the raw observation sequence.

Useful questions include:

- did a standards-defined public policy change?;
- did several distinct routing dependency units or record owners change in one
  window?;
- is a one-snapshot difference persistent or likely collection noise?;
- which source degradation explains an apparent disappearance?

Current `delta` is a diff of two rendered snapshot outputs, not proof that the
target state changed. A catalog, model, software version, collection option,
resolver vantage, cache age, or human-facing signal wording can change the
output while the public facts remain fixed. Source degradation can also turn a
previous value into an unresolved comparison rather than a removal.

A rigorous temporal layer therefore starts with a local observation capsule
containing raw response references or content, normalized observations,
per-source opportunity states, observation windows, a frozen evaluation
`as_of` time for freshness rules, cache and vantage metadata, collection
options, software and normalizer versions, catalog and model digests, and a
content digest. Replaying one capsule later must reuse its recorded `as_of`
unless the requested operation is explicitly a new time evaluation. Comparing
public observations requires applying one frozen normalizer version to both raw
capsules; a parser, normalizer, or freshness-rule change is an interpretation
delta. The comparison must distinguish:

- **observation delta:** public responses normalized under one frozen version
  changed under comparable collection, cache, and time-evaluation regimes;
- **collection-regime delta:** opportunity, source, vantage, option, cache
  provenance, or materially relevant cache age changed, unless a predeclared
  cache-comparability rule says otherwise;
- **time-evaluation delta:** the same capsule was evaluated with a different
  `as_of`, so a freshness classification changed without new public evidence;
- **interpretation delta:** the same facts produced different claims because
  recon's normalizer, freshness rules, claim rules, catalog, or model changed.

Signal deltas reconstructed from human-facing insight text remain best-effort
legacy diagnostics until snapshots store stable signal identifiers directly.
Deterministic persistence predicates and coordinated public-change bundles come
before a probabilistic change-point model.

Bayesian online change-point detection or a simpler sequential test can be
evaluated after repeat-snapshot data exist. No causal story should be inferred.
The default output is "a comparable public observation changed," not "a public
configuration changed," "a migration occurred," or "an incident occurred."
Configuration-change language requires a reviewed authoritative predicate and
persistence rule.

A stateless comparison of two caller-held observation capsules can follow the
claim ledger and may precede the scored robustness solver. It requires no new
retention service and directly repairs the semantics of the shipped delta path.
Longitudinal retention, persistence testing, monitoring, or change-point
inference remains later work because the current cache is not a measurement
system and a new retention contract requires a separate privacy and architecture
review.

## 8. Validation and falsification

### 8.1 What current tests establish

Current local checks establish implementation properties such as:

- variable-elimination agreement with independent enumeration of all 512
  latent states for each swept evidence configuration, anchored by
  [hand-computed cases](../tests/test_bayesian_differential.py); the sweep is
  not exhaustive over the global evidence power set;
- positive factors and ordered bounded bands;
- deterministic ordering;
- counterfactual masking behavior;
- selected suppression properties;
- seed-stability diagnostics;
- schema and renderer compatibility.

Synthetic worlds parameterized by the committed network are behavioral
diagnostics, not validation under one shared data-generating model. The current
generator conditions on every nonfire while shipped hideable-node inference
ignores nonfire, so their missingness semantics intentionally differ. They
cannot validate the network assumptions themselves.
The current planted graph experiment validates Louvain on an assortative graph
constructed to have the target structure. It does not validate real CT graph
semantics.

### 8.2 Existing evidence that must influence the roadmap

The current layer ablation already gives a cautionary result:

- the hard any-fired baseline wins pooled Brier score on most nodes in the
  self-generated experiment;
- strongest-only nearly matches the full network on several simple root nodes;
- the full network adds most value on propagation and policy nodes under its
  own assumptions;
- the graph benchmark is easy for Louvain because within-cluster density and
  bridge noise are planted explicitly.

This does not prove the advanced layers lack value. It proves the current
validation cannot decide their product disposition.

### 8.3 Predeclared product ablation

The four-arm M365 study was cancelled before target collection on 2026-08-13.
The [arm-identifiability audit](../validation/2026-08-13-quality-arm-identifiability.md)
exhaustively checked the 64 DNS evidence-role states in the frozen design:
A1 equaled A0, A2 equaled A3, and A3 never supported a case where A0 abstained.
Its positive-benefit gate could not pass at any sample size. This is a
structural result for that claim, channel, and decision rule, not a measured
population effect or a claim about every possible inference task.

The following arms and design requirements are retained as a post-mortem, not
an active collection plan:

1. deterministic evidence plus explicit abstention;
2. per-slug evidence strength;
3. strongest reviewed evidence unit;
4. current Bayesian network.

Any future candidate needs at least two non-collapsed evidence units, a binary
operator action tied to shipped behavior, an executable structural-identifiability
and dominance preflight, disjoint labels, and a new preregistration. The
cancelled frame must not be reused to complete this voided design. A future
robustness-envelope arm additionally needs a frozen threat model.

The implicit v2 fusion default remains enabled and silent for compatibility;
advanced-diagnostic positioning does not mean the default was switched off.
See [ADR-0013](adr/0013-fusion-non-promotion-and-v3-transition.md) and its
amendments. The requirements below govern the preserved design and inform,
but do not by themselves authorize, a new evaluation.

Predeclare one primary claim family, candidate, and comparator. Each unique
domain contributes one frozen `(domain, claim_family, observation_time)` row,
and every arm receives the same raw snapshot. The primary analysis admits
at most one domain from any known administrative, ownership, or tenant cluster,
so its Bernoulli unit and its paired discordance count are both the domain row.
Unknown cross-domain dependence remains a limitation. A clustered multi-domain
analysis is secondary until it predeclares a cluster-level estimand, outcome,
and decision rule. Domains remain grouped across parameter-development and
evaluation splits. Repeated times and additional families are sensitivity
analyses only. Before collection, name the target population, eligibility
window, positive- and negative-stratum sampling frames, and sampling mechanism.
Population-coverage interpretation for the paired Clopper-Pearson bounds and
prospective power calculation requires independent exchangeable Bernoulli units
within each stratum after the known-cluster exclusion, or a probability design
with matching design-based inference. On a fixed or purposively selected
corpus, `(b-c)/n` is only the exact empirical corpus effect; any binomial bound
is model-based on an unverified exchangeability assumption and cannot support a
population promotion claim. Use an independent provider-owned endpoint,
standards-defined record, or other predeclared authoritative reference that is
not an input to the predictor. A family without such a reference reports
coverage, disagreement, provenance, and robustness only, not precision or
calibration.

Report:

- reference-positive support rate;
- reference-negative unsupported-emission rate;
- abstention and unresolved rate;
- Brier and log score only for an arm that supplies a frozen forecast explicitly
  interpreted as `P(reference-positive | frozen inputs)` on every eligible
  two-class row, including a predeclared treatment of abstention; an arbitrary
  evidence-strength score qualifies only after a mapping is fitted on disjoint
  development data and frozen before evaluation. Otherwise exclude the arm
  from proper-score comparison or label any plug-in loss descriptive, not
  proper-score evidence;
- tie-preserving reliability with domain-cluster intervals;
- selective risk versus coverage;
- provenance completeness;
- cold and warm latency plus peak allocation.

If the positive and negative strata are sampled at different rates, pooled
abstention, unresolved, overall emission, proper-score risk, reliability, and
selective risk require known inclusion probabilities plus frozen design or
post-stratification weights for the named target population. Without those
weights, report stratum-specific values or fixed-sample descriptive losses and
make no target-population rate or calibration claim.

The historical sample minimums and paired decision rule remain in
[roadmap.md](roadmap.md). A new study must freeze its own justified sample plan,
decision rule, and compatible product disposition before reading results. The
cancelled study already received its non-promotion disposition; secondary
metrics cannot rescue its failed primary design after the fact.

### 8.4 Robustness benchmark

Keep three experiments separate:

1. **Inverse compatibility:** start from a feasible clean state, apply zero, one,
   and two typed clean-to-observed hiding or planting actions, duplicate one
   derived view, or fail one collector without changing the clean state. Given
   only the resulting observation, measure Boolean must/may status first and
   robust lower and upper scores second, plus compatibility-certificate
   completeness, witness replay, and explanation accuracy.
2. **Forward sensitivity:** start from a frozen observed record and separately
   delete hideable units or add administrative units. Measure forward decision
   transitions and forward-flip replay only; do not relabel these edits as
   inverse witnesses.
3. **CT graph stability:** insert large multi-tenant certificates and repeat graph
   evaluation across resampled entries. This is neither a claim-envelope nor a
   forward evidence-edit experiment.

Predeclare each experiment's allowed transformations, feasibility rules, costs,
threshold, and stop rule. Report them in separate result blocks.

## 9. Ranked research tasks

### 9.1 First: establish machine-enforced claim contracts

Status: first bounded internal contract complete after v2.4.0.

Value: foundational. Dependency: none. Residual risk: expanding the first leaf
contract into an ontology broader than the product needs.

The implemented first family is the exact claim that a fresh valid apex DMARC
record declares `p=reject`. Its bounded internal dossier separates construction,
collection, claim-state, and time axes; retains minimal positive and explicit-disconfirming certificate antichains; declares source role, 24-hour freshness,
and renderer obligations; and drives the opt-in schema 2.2 cohort-summary
denominator through two transient private projections. Schema 2.1 remains the
compatibility default. Time uses whole-resolution completion, not the exact DNS
query time, and that limitation remains explicit.

Acceptance:

- one claim contract has executable positive, explicit-disconfirming, conflict,
  unavailable, empty, invalid, stale, time-unknown, and duplicate-derivation
  fixtures;
- every emitted support certificate reaches canonical raw evidence; successful
  empty observations issue no sign until sufficient authority provenance is
  retained;
- the claim's four-state result is invariant to duplicate derived views;
- the internal dossier names incomplete provenance and observation windows;
- a bounded antichain implementation agrees with exhaustive enumeration;
- evaluation fails closed when an exact declared bound would be exceeded;
- no tenant JSON field, public dossier, or broad cross-claim ontology is
  introduced before the product benchmark demonstrates a consumer need. The
  cohort-summary contract is versioned separately, with 2.1 retained as the
  default and 2.2 available explicitly.

### 9.2 Second: establish the correlation value benchmark

Status: the four-arm M365 study was cancelled before target collection; section
8.3 records the structural stop. Its frozen design is a post-mortem. No
replacement population study is scheduled by this section.

Value: highest. Dependency: the first machine-enforced claim contract and its
observation-opportunity ledger. Risk: measurement design and label leakage.

Acceptance for any newly proposed study:

- candidate and comparator first pass an executable structural-identifiability
  and dominance preflight; their operator decisions and a new preregistration
  are frozen before evaluation;
- justified sample minimums and the paired decision rule are declared for the
  new study; each domain contributes one frozen primary row, and at most one
  domain is admitted from any known administrative, ownership, or tenant cluster;
- the target population, eligibility window, stratum-specific sampling frames,
  sampling mechanism, and exchangeability or design assumptions are frozen; a
  purposive corpus is reported as a fixed-corpus result and cannot pass a
  population promotion gate;
- predictor inputs and labels are disjoint by construction;
- aggregate results, environment, commands, and uncertainty are recorded;
- the result changes product disposition when the predeclared rule says it
  should;
- no real domain row or identifier is committed.

### 9.3 Third: separate observation and interpretation deltas

Value: high and immediately operator-visible. Dependency: observation ledger
and claim contracts. Risk: accidental stable-schema expansion.

v2.13 defines a local observation-capsule manifest and a pure comparison path. Keep
storage caller-owned. Classify fact, collection-regime, time-evaluation, and
interpretation changes separately, preserve unavailable comparisons as
unresolved, and store stable signal identifiers instead of reconstructing them
from prose.

Acceptance:

- replaying one capsule under the same version is byte-deterministic apart from
  explicitly excluded render timestamps;
- replaying one capsule under two catalog or model versions produces only
  interpretation deltas;
- replaying one capsule under a different explicit `as_of` produces only a
  time-evaluation delta and any resulting freshness-state changes;
- source failure cannot become a fact removal;
- every reported fact change identifies comparable source roles and observation
  windows;
- current v2 delta fields remain compatible, with incompleteness disclosed;
- no longitudinal retention or new target corpus is introduced.

### 9.4 Fourth: prototype provenance-constrained robustness envelopes

Value: potentially differentiating. Dependency: the claim contract and
evidence-unit taxonomy. Risk: subjective manipulation costs and false rigor.

Acceptance:

- the threat model, unit grouping, lexicographic or Pareto budget, and any
  secondary scalar cost scale or parameter ranges are explicit;
- Boolean must/may compatibility is the primary result; a score envelope is
  secondary and never overrides a supported, disconfirmed, conflicted, or
  unresolved primary Boolean claim state;
- exact exhaustive results on small fixtures agree with the optimized solver;
- among initially unresolved or not-supported cases, the separately labeled
  forward-planting sensitivity records zero administrative-only transitions to
  supported at the deployment threshold;
- every bound includes an attaining witness and evidence path for the finite
  prototype, or an epsilon-optimal witness with a declared tolerance;
- budget monotonicity, zero-budget collapse, dependency-unit invariance, and
  inverse compatibility-certificate replay pass as property tests; separately
  named forward flip certificates also replay exactly;
- the prototype beats deterministic abstention on a predeclared operator outcome
  or is retired;
- the first version is advanced-only and makes no stable schema change.

### 9.5 Fifth: qualify or demote CT graph correlation

Value: medium and uncertain. Dependency: the product baseline. Risk: projection
bias, low coverage, and accidental ownership implications.

Acceptance:

- clique, normalized, bipartite, or hypergraph representations are compared;
- optimizer, data, and model stability are measured separately;
- a degree-aware null and heavy-tailed multi-tenant fixtures are included;
- graph claims remain descriptive and never imply ownership;
- the simplest method meeting the predeclared threshold wins;
- no new graph dependency is added without a measured residual gap.

## 10. Reading current output

- Default facts and deterministic deductions are the primary product surface.
- `explanation_dag.provenance_complete` retains the schema-version-1 graph
  reachability contract, and `disconnected_terminals` names physical graph
  gaps. `exact_provenance_complete` applies the stronger generation-time
  evidence-to-rule requirement, while `lineage_disconnected_terminals` names
  every terminal that does not satisfy it.
- `slug_confidences` are evidence-strength scores, not validated probabilities.
- `posterior_observations[*].posterior` is exact for the committed Bayesian
  network and model-relative in the world.
- `interval_low` and `interval_high` form an evidence-responsive uncertainty
  band, not a demonstrated Bayesian credible interval or frequentist confidence
  interval.
- `entropy_reduction_nats` is a signed marginal entropy change.
- `infrastructure_clusters.modularity` is a Louvain objective value only when
  `algorithm == "louvain"`; connected-component and skipped paths use `0.0` as
  a sentinel. It is never confidence.
- `partition_stability` measures seed stability on one observed graph, not data
  stability.
- Sparse, degraded, or manipulable evidence may require an unresolved result.
- Cohort M365 and Google entries are model support coverage, not prevalence or
  lower bounds on private deployment.
- Legacy `recon delta` output remains a rendered-snapshot comparison with
  explicit incompleteness under degradation. The separate `recon capsule
  compare` path classifies observation, collection-regime, time-evaluation,
  and interpretation change without changing that stable v2 shape.
- No correlation output confirms product use, control effectiveness, ownership,
  exploitability, or overall security.

## 11. Primary literature and current guidance

Sources were rechecked 2026-07-10. Foundational sources remain relevant because
the mathematical identification problem has not changed.

- W3C, [PROV family overview](https://www.w3.org/TR/prov-overview/), 2013.
  Provenance needs explicit entities, activities, agents, derivation,
  reproducibility, and versioning. recon does not need RDF to adopt those
  semantics internally.
- Grädel and Tannen, [Provenance Analysis and Semiring Semantics for
  First-Order Logic](https://arxiv.org/abs/2412.07986), 2024-12-10. Positive and
  negative atomic provenance, alternative proof trees, and reverse provenance
  support the proposed certificate algebra without turning confidence into
  probability.
- de Kleer, [A General Labeling Algorithm for Assumption-Based Truth
  Maintenance](https://cdn.aaai.org/AAAI/1988/AAAI88-034.pdf), 1988. Sound,
  consistent, complete, inclusion-minimal assumption environments are the
  direct ancestor of the proposed support-certificate antichains.
- Manski, [Partial identification with missing data: concepts and
  findings](https://doi.org/10.1016/j.ijar.2004.10.006), 2005. Missing data
  without sufficiently strong assumptions generally identify a set, not one
  probability.
- Zhang and Peixoto, [Statistical inference of assortative community
  structures](https://arxiv.org/abs/2006.14493), 2020. Modularity maximization
  can overfit and does not by itself establish statistically significant
  communities.
- Peixoto, [Bayesian stochastic
  blockmodeling](https://arxiv.org/abs/1705.10225), 2017. Generative graph models,
  degree correction, posterior sampling, and model selection provide a more
  principled route when the data and product need justify the complexity.
- del Genio, [Hypermodularity and community detection in higher-order
  networks](https://arxiv.org/abs/2412.06935), 2024-12-09. Native higher-order
  graph objectives are an active research direction; their existence does not
  justify replacing a simpler typed or bipartite baseline without measured
  product value.
- Angelopoulos et al., [Conformal Risk
  Control](https://arxiv.org/abs/2208.02814), revision 2025-06-13. Finite-sample
  risk control requires a defined loss and assumptions; the work also makes
  distribution-shift and adversarial extensions explicit rather than silently
  transferring nominal coverage.
- Adams and MacKay, [Bayesian Online Changepoint
  Detection](https://arxiv.org/abs/0710.3742), 2007. Online run-length inference
  is a possible later method for repeated public-configuration observations,
  not a justification for causal migration stories.
- IETF, [RFC 9460: SVCB and HTTPS resource
  records](https://www.rfc-editor.org/info/rfc9460/), 2023, and [RFC 9848: ECH
  bootstrapping with DNS service
  bindings](https://www.rfc-editor.org/info/rfc9848/), 2026. These records are a
  current passive DNS surface for typed endpoint and connection-parameter
  observations. They do not establish live use without a connection test.
- IETF, [RFC 7672: SMTP DANE](https://www.rfc-editor.org/info/rfc7672/), 2015.
  TLSA policy has downgrade-resistant meaning only with DNSSEC validation, so a
  future DANE observation must distinguish secure, insecure, bogus, and
  indeterminate DNSSEC states.

These sources motivate methods and limitations. They do not validate recon's
manually encoded parameters or product claims.

## 12. Relationship to other documents

- [README.md](../README.md) defines the product and collection boundary.
- [roadmap.md](roadmap.md) owns priority, acceptance criteria, and stop rules.
- [statistical-assurance.md](statistical-assurance.md) records the evidence tier
  reached by each statistical claim.
- [limitations.md](limitations.md) records what the public channel cannot show.
- [schema.md](schema.md) defines stable output fields.
- [bayesian-cpt-discipline.md](bayesian-cpt-discipline.md) governs model changes.
- [ADR-0002](adr/0002-mnar-adversarial-absence.md) records the shipped
  non-firing-evidence policy; it must be read as a conservative implementation
  choice, not a derivation from MNAR.
- [validation/README.md](../validation/README.md) maps validation commands to the
  properties they test.

The roadmap is authoritative when research language and shipped behavior differ.
No research proposal in this document changes the stable product contract by
itself.
