# Public Replication Runbook

Status: instructions for an outside public-artifact replication pass. This file
does not claim that an outside replication pass has occurred, does not request
private data, and does not add runtime, dependency, schema, fingerprint, or
network behavior.

## Sources Checked

- ACM artifact review and badging:
  <https://www.acm.org/publications/policies/artifact-review-and-badging-current>
- Artifact review guide for this repository:
  [artifact-review.md](artifact-review.md)
- Most recent recorded public proof memo, historical and not a freeze of the
  current tree:
  [2026-06-30-submission-freeze-local-proof.md](../validation/2026-06-30-submission-freeze-local-proof.md)
- Most recent recorded final claim audit, historical and not a freeze of the
  current tree:
  [2026-06-29-scorecard-gate-claim-audit.md](../validation/2026-06-29-scorecard-gate-claim-audit.md)
- Archive readiness and DOI stop rules:
  [archive-readiness.md](archive-readiness.md)
- Security-aware artifact evaluation research:
  <https://arxiv.org/abs/2605.06508>

## Purpose

The replication pass asks an outside reviewer to rerun the public artifact on a
clean machine and report whether the public commands work as documented. It is
not a request to validate private-corpus rows or disclose real-domain data.
The current draft is unfrozen; a reviewer should use the exact commit or release
named in their outcome note rather than treating the June proof memos as current
evidence.

This strengthens the "functional" and public-result portions of the artifact
story while preserving the claim-map boundary:

- public synthetic and model-internal rows can be rerun;
- private-corpus rows remain aggregate evidence;
- the reviewer reports command outcomes and environment notes, not per-domain
  findings.

## Preconditions

Before sending this runbook to a reviewer:

1. `main` is clean and pushed.
2. GitHub CI, Secrets scan, and Scorecard pass on the target commit.
3. `uv run python scripts/check.py` passes locally.
4. When the target is the exact published current-version tag,
   `uv run python scripts/release_readiness.py --remote` passes on clean
   `main`. A later source-only target must not inherit that release-state claim.
5. The target commit has its own completed public proof memo, or the outcome
   note explicitly records that only the older historical memo exists. The
   current draft remains unfrozen until the full submission gate produces a new
   record.
6. The reviewer receives only a commit, release tag, or repository URL, not a
   private corpus or target list.

## Reviewer Handoff Packet

Send a short, bounded request. The packet should contain only these fields:

| Field | Content |
|---|---|
| Artifact pointer | Repository URL plus exact commit SHA or release tag. |
| Scope | Public-artifact functional replication only. No private corpus, target list, real-domain row, or credential is part of the request. |
| Commands | The six commands in [Reviewer Commands](#reviewer-commands), run from a fresh clone. |
| Environment note | OS family, shell family, Python version, and whether `uv sync --locked` resolved from `uv.lock`. |
| Outcome note | Pass or fail for each command, final local gate test count, skipped count, and coverage percentage. |
| Redaction check | Keep raw logs local until personal paths, credentials, terminal profiles, package-cache paths, and private target identifiers are reviewed out. |
| Return channel | Aggregate outcome note only. Raw logs, screenshots, and machine-local paths are not requested by default. |

Ask the reviewer to stop and report the first blocking environment error rather
than editing project files or relaxing gates. A clean failure report is useful
replication evidence; a locally patched run is a different experiment.

## Reviewer Commands

Run these from a fresh clone of the target commit:

| Goal | Command | Outcome to record |
|---|---|---|
| Environment resolve | `uv sync --locked` | Pass or fail, Python version, OS, and any resolver error. |
| Public proof smoke | `uv run python -m validation.reproduce_paper_numbers --profile smoke --stamp outside-replication-smoke` | Pass or fail; confirm the summary says no private corpora and no default network requirement. |
| Full public proof | `uv run python -m validation.reproduce_paper_numbers --profile paper --stamp outside-replication-paper` | Pass or fail; record the five public step statuses only. |
| Paper figure drift | `uv run python scripts/generate_paper_figures.py --check` | Pass or fail. |
| Canonical local gate | `uv run python scripts/check.py` | Pass or fail, final test count, skipped count, and coverage percentage. |
| Local release readiness | `uv run python scripts/release_readiness.py` | Pass or fail. |

The reviewer may also run `uv run python scripts/release_readiness.py --remote`
after the release is public. That checks publication state and provenance, not
empirical paper results.

## Safe Outcome Note

Record only aggregate outcome notes in a future public memo or appendix:

- reviewer role, not personal contact details unless they request attribution;
- operating system and Python version;
- commit or release tag reviewed;
- command pass/fail statuses;
- final local gate test count, skipped count, and coverage percentage;
- public proof step statuses;
- any non-secret installation or environment issue.

Do not record:

- real apex domains;
- organization names as targets;
- tenant IDs;
- per-domain outputs;
- raw private corpus rows;
- unsuppressed small strata;
- reviewer credentials, tokens, or local paths containing personal information.

## Outcome Record Discipline

A replication note is a narrow command-outcome record:

- Record failures as useful environment feedback, not as reviewer fault.
- Include the exact commit or release tag, OS family, Python version, command
  statuses, and public proof step statuses.
- Keep raw logs local unless they have been reviewed for personal paths,
  credentials, and private target identifiers.
- Do not include screenshots, machine-local absolute paths, terminal profiles,
  shell history, or package-cache paths in a public memo.
- Do not upgrade the wording from "public commands ran" to "results validated"
  unless the reviewer actually reran the row being described.
- Keep outside public-artifact replication separate from archive, DOI, badge,
  and private-corpus validation status.

## Interpretation

Use conservative language:

- "An outside reviewer reproduced the public proof commands" is acceptable only
  after that pass happens.
- "Private-corpus rows were independently reproduced" is not acceptable unless
  a separate data-handling and architecture review approves a disclosure-safe
  path.
- "Published release provenance verified" is release-state evidence, not
  empirical result validation.
- "Results validated" applies only to rows the reviewer actually reran from the
  public artifact.

## Stop Rules

- Do not send private corpora, target lists, tenant IDs, or per-domain JSON to a
  reviewer through this runbook.
- Do not ask a reviewer to query real organizations beyond the committed public
  proof commands.
- Do not publish a replication memo that contains personal contact data,
  machine-local secret paths, credentials, or private target identifiers.
- Do not change the runtime surface to make replication easier unless the
  roadmap separately approves that surface change.
