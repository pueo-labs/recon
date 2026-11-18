# Mutation testing promoted to a gate (2026-06)

The roadmap assurance track calls for "mutation testing promoted to a
gate with a score floor." The hand-rolled pilot
(`tests/test_mutation_resistance.py`, v1.9.9) and the deferral memo
(`validation/v1.9.10-mutation-status.md`) planned a cosmic-ray sweep as
CI work; this memo records the standing gate, including the false
start, because the correction is the most instructive part.

Gate: `.github/workflows/mutation.yml`. Config: `mutation.toml`. Floor:
`scripts/mutation_floor.py`. Tool: cosmic-ray (the `mutation`
dependency group).

## The v2.1.16 baseline was an artifact, and what caught it

The first sweep (run on the maintainer's Windows machine) reported
1,642 of 1,642 mutants killed. That number was wrong, and the v2.1.16
release notes repeated it. What actually happened: cosmic-ray's worker
spawns the test command with no shell, and the command began with a
bare `python`. On Windows, a bare program name resolves through the
CreateProcess search order, whose first stop is the directory of the
*base interpreter image*, not the virtual environment, so every mutant
was "tested" by an interpreter whose environment cannot even import the
test suite's conftest (`No module named hypothesis`). Every mutant
"died" of an instant collection error, never of a test verdict: a false
100% kill score.

It was caught by the gate's own design. The CI workflow includes a
baseline step (the kill-set must pass on unmutated code before any
mutant is scored) that the by-hand local run had skipped; on the Linux
runner, where `PATH` resolution under `uv run` is correct, the same
sweep produced 486 survivors out of 1,642, and the disagreement forced
the diagnosis. A second local sweep in a CI-equivalent clone (locked
venv, baseline verified first) reproduced the CI number, 486 of 1,642,
identically. The falsifiability lesson generalizes: an autonomous loop
is only as good as the checks inside it, and "the test command itself
is broken" is the failure mode the baseline step exists to catch.

Two mechanical fixes prevent recurrence:

- The test command starts with the `pytest` console script, never bare
  `python`. The console script lives in the venv's scripts directory,
  which is the first place both platforms' resolution looks for the
  spawning process's siblings, so the workers test the interpreter that
  has the project and its test dependencies.
- `cosmic-ray baseline` is mandatory before any scored sweep, in CI and
  in the local recipe below.

## Scope: the inference core first

The mutated surface is `recon_tool/bayesian.py`: factor construction,
variable elimination, the evidence-responsive uncertainty band, and the
`n_eff` display-mass machinery.
(The YAML network loaders and the result dataclasses were later split into
`bayesian_loader.py` and `bayesian_models.py` as part of the god-file
decomposition. They sit outside this mutation surface by design: the loaders
are config/parsing covered by `test_bayesian_loader_edges` /
`test_bayesian_topology` / `test_bayesian_validation_rounds`, and the
dataclasses are pure frozen data whose mutants are equivalent-by-construction,
the category the floor already discounts. The inference functions themselves
were moved byte-identically, so the kill *strength* on the inference core is
unchanged; the post-decomposition sweep (round 4 below) re-established the
absolute counts.) Chosen first because it is the highest
trust-per-effort surface: the numbers it emits are the product recon
asks operators to rely on, it is already the most-verified module in
the tree (differential verification v2.1.7, drift gate v2.1.14,
interval coverage v2.1.15), and mutation testing answers the question
those harnesses do not: would the suite notice if this code were subtly
wrong?

## What the real survivors taught, and the response

The 486 genuine survivors clustered in code the original four-file
kill-set exercises only indirectly, which is to say: the mutation gate
found real test gaps on its first honest run.

| Cluster | Survivors | Response |
|---|---|---|
| `credible_interval` / `beta_ppf` / `_erfinv` (the interval arithmetic) | 83 | `tests/test_bayesian_unit_math.py`: hand-computed interval values, exact Beta anchors, and boundary fallback coverage |
| `_declarative_evidence_count` (CAL14 n_eff) | 53 | hand-computed counting cases (fired, informative absence, uninformative absence, group handling) |
| `_rank_evidence` / `_contributing_evidence` | ~45 | hand-computed LLRs, influence shares, tie-breaks, group reduction |
| parsers / loaders (`_parse_*`, `load_network`, `load_priors_override`) | ~95 | `tests/test_bayesian_validation_rounds.py` + `tests/test_bayesian_topology.py` added to the kill-set; loader edge cases in the unit file |
| TenantInfo adapters (`infer_from_tenant_info`, `signals_from_tenant_info`, `_conflict_provenance`) | ~35 | adapter unit tests (signal derivation, conflict provenance, interval dampening) |
| deal-contract predicates | ~30 | direct predicate tests (a weakened contract is invisible on correct code) |
| annotation-union operators (`X \| None` under `from __future__ import annotations`) | ~170 | inert under postponed annotations; the current gate uses line-scoped mutation pragmas so runtime unions remain tested |
| output rounding (`round(x, 4)`) | few | granularity assertions in the unit file (4-decimal exactly: a 3- or 5-decimal emission fails) |

The remaining long tail is re-measured by the corrected sweep; any
survivor that stays is either killed with a test or accepted in the
table below with a reason.

## Results (corrected baseline through 2026-07)

Authoritative run: the CI `mutation-gate` workflow on ubuntu (locked
venv, baseline-verified, operators filter applied), cross-checked by an
identical local sweep in a CI-equivalent clone. The honest corrected
trajectory, against the false v2.1.16 "1,642 of 1,642":

| Round | Tested | Killed | Survived | Survival | What changed |
|---|---|---|---|---|---|
| 1 (corrected) | 1,465 | 1,252 | 213 | 14.5% | interpreter fixed, then-global BitOr filter, unit-math anchors |
| 2 | 1,465 | 1,312 | 153 | 10.4% | loader-edge + n_eff tests added |
| 3 (pre-split) | 1,431 | 1,308 | 123 | 8.6% | Is/IsNot filtered, bound + penalty + absence kills |
| 4 (post-decomposition) | 1,083 | 981 | 102 | 9.4% | bayesian.py split; v2.2 output-field + counterfactual kills |
| 5 (collection-aware contracts) | 662 | 603 | 59 | 8.9% | exact boundaries, neutral fallbacks, opportunity masking, adapter extraction |
| 6 (narrowed runtime scope) | 717 | 655 | 62 | 8.6% | line-scoped annotation filter; 55 runtime union mutants restored |

(Round 3 run: 1,642 mutants generated, 210 filtered under the then-configured exclusions,
1 incompetent within tolerance, so 1,431 tested.)

Round 4 re-established the baseline after the god-file decomposition moved the
YAML loaders and result dataclasses out of `bayesian.py` (1,212 generated, 129
filtered, 0 incompetent, 1,083 tested). The split removed ~360 readily-killed
loader / dataclass mutants from the surface, so the accepted residual,
which lives in the inference core that stayed, became a larger *fraction* of the
smaller denominator even though the suite's kill strength on that core is
unchanged. The 2026-06 scheduled sweep first surfaced this at 12.5% (135 of
1,083): the v2.2 evidence-semantics surface (per-node entropy reduction, the
exact leave-one-unit-out counterfactuals) had shipped output fields whose
rounding and arithmetic the kill-set pinned only in aggregate. The aggregate
`TestOutputRounding` form (`all(v == round(v, 4))` plus `any(round(v, 3) != v)`)
cannot catch a *single* field rounding coarser, because the other fields keep
the `any()` satisfied. Per-field exact-literal anchors in
`tests/test_bayesian_unit_math.py` (`TestOutputRounding`,
`TestUnitCounterfactuals`, and the `_rank_evidence` order anchor) close that gap:
they killed 33 survivors (`posterior` / `interval` / `entropy_reduction(_nats)` /
`posterior_without` / `delta` rounding in both directions, the counterfactual
`delta = posterior - posterior_without` subtraction, and the descending-absolute
sort-key sign), taking the surface to 9.4%.

Round 5 is the authoritative Cycle 60 run at commit `0c473d7`:
[GitHub Actions run 29154457989](https://github.com/pueo-labs/recon/actions/runs/29154457989).
The semantic-integrity refactor produced 801 jobs; the configured operator
filter skipped 139 and left 662 tested mutants. The first sweep at `8cb0347`
killed 578 and left 84 survivors, a 12.69 percent survival rate that correctly
failed the unchanged 12 percent ceiling. A replay of every survivor identified
exact probability-boundary, neutral-fallback, collection-opportunity, adapter,
and likelihood-ratio contracts. The strengthened kill set killed 25 additional
mutants, yielding 603 killed, 59 survived, zero incompetent, zero pending, and
8.91 percent survival. Independent review removed two proposed entropy tests
outside the helper's documented probability domain; invalid inputs were not
used to improve the score.

Round 6 is the authoritative narrowed-filter run at commit `aac9245`:
[GitHub Actions run 29160654831](https://github.com/pueo-labs/recon/actions/runs/29160654831).
It narrows the filter rather than changing the score floor. Six postponed
annotation unions are marked line by line and account for 66 inert mutants;
the explicit identity-comparison policy accounts for the other 18 skipped
jobs. All 55 runtime BitOr mutants now execute. UTF-8 preflight killed 52
and left three behaviorally unchanged under reviewed current invariants: two
parent-assignment unions add a node name that validation keeps distinct from
its parents, and one counterfactual union adds a unit selected only after the
masked set has excluded it. The authoritative 801-job result is 84 skipped, 717
tested, 655 killed, 62 survived, zero incompetent, zero pending, and 8.65
percent survival, exactly matching the preflight.

The first two rounds killed 60+ genuine survivors that were real test
gaps the gate exposed (loaders, n_eff arithmetic, interval math,
TenantInfo adapters, contract predicates). The third round filters the
identity-comparison mutants by policy and kills the
last cheap genuine survivors (out-of-range bound checks, the conflict
penalty constant asserted as a literal, the `absence_informative` flip).

**The accepted residual (8.6% pre-split, 9.4% post-decomposition, 8.9% in
Round 5, and 8.65% in Round 6) is dominated by mutants
classified as equivalent or behaviorally
irrelevant under the documented valid-input and configuration contracts.** The
session DB is uploaded as a CI artifact on every run, so this is checkable.

- *Identity for value equality* (`==` to `is`): excluded by explicit policy.
  Testing object identity for value semantics is a Python anti-pattern; this
  exclusion is not presented as a proof for arbitrary string objects.
- *Ordering for equality* (`==` to `<=` / `>=` / `<` / `>` on a string or
  enum): configuration-relative. The shipped model and reviewed fixtures do
  not exercise a lexicographic neighbor that changes the branch, but arbitrary
  valid node names could. These remain tested and accepted, not filtered.
- *Arithmetic by 1.0* (`*` to `/` / `**` / `//` on the loaded
  `evidence_n_eff_contrib`, which is `1.0` in the shipped
  `bayesian_network.yaml`): `x * 1.0 == x / 1.0 == x ** 1.0`, so the
  operator is irrelevant. Mathematically equivalent.
- *Frozen-dataclass flags* (`frozen=True` to `False`): no code path mutates
  these instances, so the flag is behaviourally invisible; killing it would
  mean asserting that assignment raises, a language-feature test.
- *Always-true contract decorators* (`@deal.post(...)` removed): the
  postconditions hold on every valid input and are disabled under `-O`, so
  removing an assertion that never fires changes nothing observable.
- *Order-invariant loop and traversal mutants* (`queue.pop(0)` to
  `pop(-1)`, some `continue` to `break`): the topological sort accepts any
  valid order and checks only the visited count, so the traversal order
  does not change the result.
- *Rounding under the shipped calibration*: the defaults produce `n_eff`
  in multiples of 0.5. A supported custom calibration can yield additional
  decimal places. The unit suite covers the two-decimal output for that case.
- *Union to symmetric difference on fresh elements*: configuration-relative.
  Node names are distinct from their validated parents, and counterfactual
  units are enumerated only after already-masked units are excluded. Under
  those invariants, the three surviving runtime-union mutants produce the same
  sets. Runtime unions remain tested so an invariant change is visible.

## November 18 evidence-reporting review

The [November 17 main run](https://github.com/pueo-labs/recon/actions/runs/44238891321)
left 69 of 749 tested mutants alive. A targeted replay of nine survivors
found observable differences in evidence counts, provenance labels, binding
selection, or rounding with a custom calibration.

The mixed-declaration fixture supplies both names on one observation channel.
It checks which binding fired, which absence affected the posterior, and
whether each counterfactual identifies a group or a single signal. A neutral
absence contributes zero evidence units. Swapping the input channel changes
the expected posterior from 6/7 to 2/11 under the fixture's equal prior odds.
All nine replayed variants failed an assertion; the original passed.

## The floor

`scripts/mutation_floor.py mutation.sqlite --fail-over 12`: survival over
**tested** mutants (killed + survived) must stay at or under 12% (kill
score at or above 88%). The floor sits above the documented
accepted residual (8.9% in Round 5 and 8.65% in Round 6)
with margin, so it ratchets the current
kill strength and fails when real coverage regresses (untested new code
spikes survival well past the residue), without forcing tests against invalid
inputs or inert configuration-relative behavior. This is the mutation-testing
posture: kill the genuine survivors, classify and accept the equivalents,
set a defensible floor, never chase 100%. The 5% figure the v2.1.16 notes
implied was never real; it was the wrong-interpreter artifact described
above.

The script replaces `cr-rate`, whose accounting divides kills by every
recorded result and therefore counts filter-skipped jobs as if they had
survived; the script also fails outright on incompetent results (a broken
worker means the score measures nothing) and on pending jobs (a partial
sweep is not a score).

## When it runs

- Blocking on any push or PR that touches the mutated surface, the
  kill-set files, the config, the floor script, or the workflow.
- Weekly on a schedule, so toolchain drift still surfaces.
- On demand via `workflow_dispatch`.

Not per-push: a full sweep costs about an hour of runner time, and a
docs or catalog change cannot change the mutation score of an untouched
module.

## Running it locally (Windows notes earned the hard way)

```powershell
# A non-OneDrive clone with the locked venv; uv sync --locked works there.
git clone . $env:TEMP\recon-mutation; cd $env:TEMP\recon-mutation
$env:UV_PYTHON = "3.11"; $env:UV_LINK_MODE = "copy"
$env:UV_LOCKED = "1"
$env:PYTHONUTF8 = "1"              # cosmic-ray decodes worker output as UTF-8;
                                   # Windows pytest otherwise may emit cp1252
                                   # and misrecord a killed mutant as incompetent
uv sync --locked --group mutation
uv run --group mutation cosmic-ray baseline mutation.toml   # mandatory
uv run --group mutation cosmic-ray init mutation.toml mutation.sqlite
uv run --group mutation cr-filter-operators mutation.sqlite mutation.toml
uv run --group mutation cr-filter-pragma mutation.sqlite
uv run --group mutation cosmic-ray exec mutation.toml mutation.sqlite
uv run python scripts/mutation_floor.py mutation.sqlite --fail-over 12
```

cosmic-ray mutates the working copy of `recon_tool/bayesian.py` in
place during exec and restores it afterward; do not edit the tree, run
other test commands, or run `uv` commands in that clone while it
executes (a concurrent `uv run` resync produced the one batch of
genuinely incompetent results we observed). Check `git status` if a run
is interrupted.
