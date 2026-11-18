# OpenSSF Posture

This note records the current OpenSSF path for recon. It is intentionally
separate from the public Scorecard badge: Scorecard is an automated signal,
while the Best Practices Badge is an account-backed project questionnaire.

## Current Snapshot

The November 17, 2026 recheck of the v2.27.3 release commit returned
an overall score of 8.3 from Scorecard v5.6.0. The
[manual Scorecard run](https://github.com/pueo-labs/recon/actions/runs/44202514366)
completed successfully and refreshed the
[public result](https://api.securityscorecards.dev/projects/github.com/pueo-labs/recon).

The public API is authoritative for the exact commit behind the badge. Docs-only
commits can move `main` after a snapshot is written, so this file records the
reviewed posture and the live API URL rather than treating a commit hash as a
durable status promise. Remote release readiness queries that API for `HEAD`,
requires an overall score of at least `8.0`, keeps the non-SAST required
code-owned controls at `10`, and requires the documented SAST floor of `10`.

Every required check except SAST scored 10. SAST and CI-Tests both returned
`-1` because GitHub denied the scanner access to third-party check data.
SAST therefore fails remote release readiness even though the repository's
CodeQL and CI runs passed. Pull requests targeting `main` and pushes to
`main` run CodeQL, with weekly and manual default-branch analysis available.

The remaining low or unknown checks are process-bound:

| Check | Current reason | Real next step |
|---|---|---|
| `Branch-Protection` | `main` requires PRs, strict CI, CodeQL and gitleaks, linear history, no deletion or force pushes, and no bypass actors. Independent approvals, last-push approval and required CODEOWNERS review are absent because there is one maintainer. | Stale approvals are dismissed and review threads must resolve. Release readiness enforces these controls. Add independent approval requirements when a second qualified reviewer is available. |
| `Code-Review` | No human-approved changesets appear in Scorecard's sampled window; automated review comments are not approvals. | Use normal reviewed PRs for non-urgent work when there is another qualified reviewer. Do not manufacture review history. |
| `CII-Best-Practices` | The real badge project is now linked from README. Its status is separate from this dated Scorecard snapshot. | Keep questionnaire answers consistent with the repository; check the current Scorecard API before claiming its sampled result changed. |
| `Contributors` | Scorecard sees no contributor diversity across organizations. | Accept this for a single-maintainer project. Do not add artificial contributors. |

## Best Practices Badge Readiness

The detailed worksheet lives in
[openssf-badge-readiness.md](openssf-badge-readiness.md). The OpenSSF Best
Practices Badge criteria are organized around basics, change control,
reporting, quality, security, and analysis. recon already has local evidence
for many passing-level questions. The repository
[.project.d/bestpractices.json](../.project.d/bestpractices.json) supplies all 67 criterion proposals
to the badge service, with dated maintainer knowledge attestations and unknown
answers for unverified response history. A source and primary-documentation review leaves
9 unknown answers; the other proposals comprise 55 `Met` and 3 `N/A` answers.
Private HTTPS vulnerability reporting is enabled and linked from `SECURITY.md`.
The import file does not create a badge project or claim a
passing result:

| Area | Local evidence |
|---|---|
| Basics | README, Apache-2.0 license, PyPI package metadata, documented install and update path, public issue tracker, and stable project URLs. |
| Change control | Git history, SemVer policy, changelog, release process, tagged releases, signed provenance assets, and short-lived branch guidance. |
| Reporting | `SECURITY.md`, private vulnerability-reporting email, response timeline, issue templates, and no-real-company-data contribution policy. |
| Quality | `scripts/check.py` as the canonical local gate, branch coverage gate, mutation gate, property tests, fuzzing, golden renders, pyright strict mode, and generated-artifact drift guards. |
| Security | CodeQL, ruff security rules, `pip-audit`, secret scanning, push protection, least-privilege workflow tokens, pinned workflow actions, SBOM, same-job deterministic-build checks, Trusted Publishing, PyPI attestations, and GitHub build provenance. |
| Analysis | Strict type checking, static analysis, workflow-pin checks, validation hygiene, text hygiene, schema drift checks, and release readiness checks. |

The live first-party JSON and SVG for
[project 15800](https://www.bestpractices.dev/projects/15800) reported
Passing at 100 percent on 2026-10-23 and identified this recon repository.
README now embeds its official dynamic badge. This is an account-backed
self-assessment, not an independent security audit or a security guarantee.
The worksheet above remains local evidence and historical proposal state;
the badge service owns the current answers and status. Future status can change.
Any later badge must point to its actual reviewed project and must not be added as a placeholder.

## CODEOWNERS Decision

`.github/CODEOWNERS` routes all repository paths to `@blisspixel` so external
pull requests have clear ownership. This does not by itself create a
Scorecard-reviewed workflow. It is preparation for a future branch ruleset that
requires CODEOWNERS review when a second qualified maintainer is available.
Maintainer changes already use checked pull requests; the author cannot supply
an independent approval of their own change. Outside contributors and
prospective reviewers are welcome through [CONTRIBUTING.md](../CONTRIBUTING.md).

## Research Sources

- OpenSSF Scorecard check definitions:
  `https://github.com/ossf/scorecard/blob/main/docs/checks.md`
- OpenSSF Best Practices Badge passing criteria:
  `https://www.bestpractices.dev/en/criteria/0`
- GitHub CODEOWNERS review routing:
  `https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners`
