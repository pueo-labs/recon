# Artifact Review Guide

Status: reviewer-facing guide for external write-up readiness. This file defines
what an outside reviewer can run, what result each command validates, and which
paper claims remain maintainer-reproducible only.

## Scope

The review artifact is the repository at a specific commit plus the released
Python package built from that source. It includes:

- the CLI, importable package, and local stdio MCP server;
- the stable JSON schema in [recon-schema.json](recon-schema.json);
- public proof and synthetic validation harnesses under `validation/`;
- aggregate-only validation memos under `validation/*.md`;
- the aggregate-safe paper figure package in [paper-figures.md](paper-figures.md)
  and `assets/paper/*.svg`;
- the public label snapshot and public-list sampling decision in
  [public-label-snapshot-decision.md](public-label-snapshot-decision.md);
- citation metadata in [../CITATION.cff](../CITATION.cff);
- supply-chain and release-integrity notes in [supply-chain.md](supply-chain.md);
- final submission-freeze commands and stop rules in
  [submission-freeze-checklist.md](submission-freeze-checklist.md);
- archive policy boundaries in [archive-readiness.md](archive-readiness.md);
- outside public-artifact replication instructions in
  [replication-runbook.md](replication-runbook.md).

The artifact does not include private corpora, per-domain outputs, real target
lists, paid feeds, credentials, hosted services, DOI claims, or archive metadata
that has not been created yet.

## Reviewer Commands

Run from the repository root after installing the development environment:

| Goal | Command | Expected result |
|---|---|---|
| Install dependencies | `uv sync --locked` | Development environment resolves from `uv.lock`. A metadata change the lock does not contain fails and leaves `uv.lock` unchanged. |
| Quick public proof smoke | `uv run python -m validation.reproduce_paper_numbers --profile smoke --stamp artifact-review-smoke` | Writes a manifest and summary under `validation/local/paper-numbers/artifact-review-smoke/`; reports no private corpora and no default network requirement. |
| Full public proof bundle | `uv run python -m validation.reproduce_paper_numbers --profile paper --stamp artifact-review-paper` | Runs suppression monotonicity, planted-evidence movement, differential verification, interval coverage, likelihood sensitivity, and layer ablation. |
| Paper figure drift check | `uv run python scripts/generate_paper_figures.py --check` | Verifies the committed SVG figures match the deterministic aggregate-safe generator. |
| Canonical local gate | `uv run python scripts/check.py` | Ruff, Pyright, coverage-gated tests, generated-artifact checks, validation and text hygiene, tracked Markdown links and heading anchors, interface and paper checks, and ratchets pass. |
| Release readiness | `uv run python scripts/release_readiness.py` | Version, citation metadata, lockfile, roadmap, supply-chain recipe freshness, private-data hygiene, and commit hygiene pass for the local checkout. |
| Published release verification | `uv run python scripts/release_readiness.py --remote` | After `main` and the current version are published, the remote and local current version tag plus `HEAD` identify one commit, required GitHub Actions checks pass, public Scorecard API state matches `HEAD`, PyPI wheel and sdist, GitHub Release wheel, sdist, SBOM, and attestation export match the current version, and PyPI provenance verifies for both distributions. GitHub provenance covers the wheel and sdist for the exact v2.6.3 historical exception, and also covers the completed SBOM for later releases produced by the current workflow. |

If a Windows terminal closes stdout during the long coverage run, redirect the
wrapper output to `logs/check-full.log`. `logs/` is ignored:

```powershell
uv run python scripts/check.py > logs\check-full.log 2>&1
```

That changes only terminal handling. It does not skip any gate.
The wrapper emits ANSI styling only to a capable terminal, so the redirected
log is plain text and remains searchable without escape-sequence cleanup.

## What The Public Bundle Validates

The most recent completed historical maintainer proof check is recorded in
[../validation/2026-06-30-submission-freeze-local-proof.md](../validation/2026-06-30-submission-freeze-local-proof.md).
The most recent completed historical public claim-audit refresh is
[../validation/2026-06-29-scorecard-gate-claim-audit.md](../validation/2026-06-29-scorecard-gate-claim-audit.md).
The current paper and artifact package is unfrozen after subsequent product,
documentation, and release changes. These dated records apply only to the
commits and package state they name; rerun the submission gate before external
submission. The claim-audit memo records the last completed paper-package
claim-audit refresh.
It supersedes the June 29 metric-lineage refresh, the June 28 final claim audit,
and the earlier adversarial-perturbation proof memo only as the latest
claim-audit gate; those earlier memos remain focused historical records for their
respective checks.

| Claim family | Public command or gate | Reviewer interpretation |
|---|---|---|
| Inference arithmetic | `validation.differential_verification` through the reproduction bundle | Variable elimination matches an independent full-joint reference over the bounded none/one/all cross-product sweep and exhaustive local subsets for three factor-heavy nodes under two background contexts. It does not enumerate the global evidence power set. |
| Evidence-removal and planting boundary | `validation.adversarial_properties` through the reproduction bundle | Under fixed local positive-factor assumptions, deletion does not raise local presence odds in the tested contexts. In synthetic model contexts, planted evidence can raise posteriors across decision boundaries. Neither result is a real-world error-rate claim. |
| Band perturbation containment | `validation.interval_coverage --json` through the reproduction bundle | The 80 percent uncertainty band contains selected CAL8 perturbed-model conditionals in the finite experiment. This is not a credible interval, confidence interval, identification region, or general misspecification bound. |
| Likelihood sensitivity | `validation.likelihood_sensitivity` through the reproduction bundle | The harness reports model-relative changes under the configured +/-20 percent binding-likelihood perturbation. It does not perturb grouped-absence parameters, encode a pass threshold, or establish real-world calibration. |
| Layer comparison | `validation.layer_ablation` through the reproduction bundle | Mixed Bayesian baseline results and the tailored assortative graph result reproduce without target data. They do not establish real product value. |
| Public-list sampling boundary | [public-label-snapshot-decision.md](public-label-snapshot-decision.md) plus `scripts/check_paper_claims.py` | Public-list numbers are robustness checks rather than population rates or benchmark prevalence. |
| Paper figures | `scripts/generate_paper_figures.py --check` | SVG figures are deterministic renderings of committed topology and aggregate memos, not hand-edited screenshots. |
| Runtime and docs integrity | `scripts/check.py` | Generated schema, fingerprint catalog, surface inventory, CLI surface docs, text hygiene, validation hygiene, tracked Markdown links and local heading anchors, interface layout, paper artifacts, and tests agree with source. CI and release invocations provide a full revision range to text hygiene. |
| Published artifact integrity | `scripts/release_readiness.py --remote` | The public package, public Scorecard API state, PyPI provenance, GitHub Release, and GitHub build provenance are aligned with the current version after publication. This validates release state, not empirical paper results. |

## What Is Not Publicly Reproducible

Some paper rows use real-domain corpora that cannot be committed under the
data-handling policy:

- DMARC full-posterior consistency and held-out residual aggregates in
  [../validation/2026-06-28-full-corpus-calibration-refresh.md](../validation/2026-06-28-full-corpus-calibration-refresh.md).
- M365 DNS-only provider corroboration aggregates in the same memo. The
  [M365 tenancy decision](m365-tenancy-decision.md) explains why this remains
  corroboration rather than independent calibration.
- Aggregate-only certificate-transparency validation closure in
  [../validation/2026-06-26-c3-ct-partial.md](../validation/2026-06-26-c3-ct-partial.md).

These are maintainer-reproducible aggregate results. Reviewers can inspect the
memo, disclosure controls, and harness code, but they cannot regenerate the
private rows from the public repository. The [paper claim map](paper-claim-map.md)
records this distinction claim by claim.

Public-list cross-checks are public and re-queryable, but the project does not
publish a frozen real-apex label snapshot for this submission. Treat those
numbers as robustness checks rather than population rates.

## Disclosure Controls

Reviewers should expect committed artifacts to contain:

- counts, rates, intervals, quantiles, and aggregate deltas;
- explicit synthetic examples under reserved namespaces;
- vendor names when they are detection classes.

Reviewers should not find:

- real apex lists;
- organization names as targets;
- tenant IDs;
- per-domain findings;
- raw private corpus rows;
- unsuppressed small strata.

The mechanical backstops are `scripts/check_validation_hygiene.py`,
`tests/test_validation_hygiene.py`, and release readiness. Semantic review still
owns prose that a regex cannot classify.

## Review Outcome Language

Use these labels when writing the artifact appendix:

- Available: repository, release assets, license, docs, and citation metadata are
  present.
- Functional: the public proof bundle and canonical local gate run successfully.
- Reusable: the README, docs index, schema, operational contract, and data policy
  are sufficient to rerun the public artifact and understand limits.
- Results validated: only the public proof and synthetic rows qualify for an
  outside reviewer. Private-corpus rows are aggregate evidence, not externally
  reproduced results.

Archive status is separate from those review labels. The current repository is
archive-ready in the sense described by [archive-readiness.md](archive-readiness.md),
but it does not claim a DOI or add `.zenodo.json` until a real archive path is
chosen.

Outside replication status is also separate. Use
[replication-runbook.md](replication-runbook.md) to request a clean-machine
public command rerun with the handoff packet, and record only aggregate outcome
notes unless a separate data-handling review approves a stronger release model.

Before any external submission package, use
[submission-freeze-checklist.md](submission-freeze-checklist.md) to rerun the
claim audit, public proof bundle, figure drift check, local gate, and release
readiness without adding placeholder archive, badge, or replication claims.
