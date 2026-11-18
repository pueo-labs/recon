# Release Process

recon releases use a reviewed preparation commit, an exact-main tag, and a
GitHub Actions workflow that handles build and PyPI publication, followed by
a human-owned GitHub Release handoff. A successful tag
push means publication is pending, not that either registry is current.

## TL;DR

```bash
# 1. Merge the planned changes and dated CHANGELOG through a checked PR.
#    Wait for current-main CI. Start from clean main exactly at origin/main.
#    Generate the CLI surface line if commands or flags changed:
#    uv run python scripts/summarize_cli_surface_changes.py --old-ref vX.Y.Z

# 2. Run the local readiness preflight.
uv run python scripts/release_readiness.py

# 3. Create a release preparation branch at that exact main commit.
git switch -c release/vX.Y.Z
uv run python scripts/release.py --prepare-only

# 4. Push that branch, open a PR, and merge only after all checks pass.
#    Then follow "Tagging reviewed main" below. Never tag the preparation SHA.
#    Do not rerun release.py after the version preparation has merged.
```

## Release Decision and Cadence

Release quality includes the signal a version sends to users. The default is a
coherent release batch, not one package version per merged pull request. Group
compatible fixes, catalog updates, and documentation needed to explain them
under one short release narrative, then run the reviewed preparation path.

Cut an immediate patch release when a shipped correctness bug, security issue,
dependency failure, broken package, or release-artifact defect makes waiting
materially worse for users. A documentation-only change, planning change, issue
template change, repository metadata update, or internal proof refresh does not
by itself trigger a package release. Those changes can remain in `Unreleased`
until the next meaningful package batch.

Before choosing a version, answer three questions:

1. What user-visible problem or coherent capability does this release deliver?
2. Which stable surface changes, if any, require a minor rather than patch
   version under [stability.md](stability.md)?
3. Can a user understand the release from one concise summary plus the tool
   surface line?

If the first or third answer is unclear and no urgent exception applies, keep
the work on `main` and batch it. This policy changes cadence, not rigor: every
published version still uses the complete readiness, build, provenance, SBOM,
publication, and post-release verification path below.

---

## Local readiness gate: `scripts/release_readiness.py`

This gate is the maintainer-local preflight before relying on GitHub Actions.
It does not call the network by default and it is not part of the user-facing
`recon` CLI. It checks:

1. Branch, worktree, and `origin/main` tracking state.
2. Version consistency between `pyproject.toml` and the package fallback, plus
   current-version references in both roadmaps, `CITATION.cff`, and the
   supply-chain consumer-verification recipe.
3. The exact maintainer uv toolchain (`0.13.9`), followed by `uv.lock`
   freshness with `uv lock --check`. A toolchain mismatch is reported
   separately and must be corrected with `uv self update 0.13.9`; readiness
   never changes the maintainer's toolchain automatically.
4. Coverage authority in `scripts/check.py` and main CI, with the release helper
   and release workflow required to delegate to that canonical gate.
5. README usage anchors, supply-chain recipe anchors, and repository hygiene.
6. No tracked private corpus files, validation outputs with target-domain
   fields, or root per-domain JSON dumps.
7. Commit-message hygiene across the relevant local commit range.

The release workflow independently validates that the tag, package version,
dated nonempty changelog section, tagged commit, and current `main` ancestry
agree. It then reruns the exact MCP SDK matrix for the v1.28.1 rollback,
v2.0.0 production floor, and v2.3.0 current stable pins, plus the complete canonical gate on the tagged tree,
before a build can be sealed or published. A manually pushed tag cannot bypass
the controls on `main`.

The main CI workflow exposes one final `ci-gate` result that depends on every
other job in that workflow. After the aggregate first succeeds on `main`, branch
protection uses that stable result alongside the separate Gitleaks and CodeQL
results. Individual main-CI jobs stay visible for diagnosis, while the
aggregate prevents a new matrix row or job from being omitted from branch
protection.

During active edits, this is useful as a planning report:

```bash
uv run python scripts/release_readiness.py --allow-dirty
```

Before tagging or pushing a release, run it strictly:

```bash
uv run python scripts/release_readiness.py
```

After publishing the current version from the exact checked-out tag, add the
optional remote check. In remote mode the gate first requires the remote and
local current project-version tag plus `HEAD` to resolve to the same full
commit. It then verifies required GitHub Actions checks for `HEAD`, the active
default-branch ruleset, and public
Scorecard API freshness and code-owned control scores, PyPI's exact
current-version record, and the exact four GitHub Release assets for the current
version, with the human maintainer as release author and every asset uploader. It verifies
both PyPI files with pinned `pypi-attestations==0.0.31`, validates the completed
CycloneDX SBOM without repairing it, and verifies the GitHub subjects required
by the exact release policy against the downloaded bundle with the release
workflow, tag ref, local release tag commit digest, and hosted-runner boundary.
The exact v2.6.3 historical exception requires wheel and sdist provenance plus
SBOM structure validation; every later release also requires SBOM provenance.
Its PyPI metadata reader is bounded and accepts only the exact version-scoped
pair from HTTPS `files.pythonhosted.org` URLs before any verifier runs. It also
reports the SHA-256 parity of both distribution files across PyPI and GitHub.
The ruleset check requires strict `ci-gate`, `gitleaks`, and `CodeQL Python
analysis` contexts together with deletion, non-fast-forward, linear-history,
and pull-request protections. It reports bypass actors rather than silently
assuming none exist. The remote check therefore requires the current release
tag locally plus an authenticated `gh` session or `GH_TOKEN`:

```bash
uv run python scripts/release_readiness.py --remote
```

For automation or an optional maintainer loop, use JSON:

```bash
uv run python scripts/release_readiness.py --json
```

The JSON output is deliberately local and deterministic unless `--remote` is
passed. Text and JSON both identify the assessed scope. Default text states
that remote publication checks were not assessed; default JSON reports
`"scope": "local"` and `"remote_checks_assessed": false`. With `--remote`,
those fields become `"local-and-remote"` and `true`. It is a maintainer signal,
not a runtime contract for recon users.

---

## CLI surface change line: `scripts/summarize_cli_surface_changes.py`

Every release section should include a short `### Tool Surface Changes` entry
so skill and agent authors can scan command and flag changes without diffing
help output. Generate the line from the checked surface inventory:

```bash
uv run python scripts/summarize_cli_surface_changes.py --old-ref vX.Y.Z
```

Replace `vX.Y.Z` with the last released tag. The helper reads
`docs/surface-inventory.json` from that tag with `git show`, compares it with
the current generated inventory, and prints one changelog-ready sentence. Use
`--json` when release automation needs the structured diff instead of prose.

If commands and flags did not change, keep the generated no-change line. It
is cheap signal for downstream skill maintainers and avoids forcing them to
infer silence from the rest of the changelog.

---

## Human half: `scripts/release.py`

### PR-first preparation

The recommended `--prepare-only` mode requires a clean, named non-main branch
whose `HEAD` exactly equals freshly fetched `origin/main`. Finalize the dated
changelog in the preceding implementation PR before creating this branch.
The helper validates the next version, synchronizes every release-owned
surface, runs the complete quality gate and local readiness, and commits only
those owned paths. The readiness exceptions apply only to the expected dirty
preparation branch. They do not waive a quality gate or authorize publication.

This mode creates no tag, makes no push, and offers no push prompt. Push its
commit as a normal PR and wait for all hosted checks before merging. The
preparation commit is not the publication identity: a squash merge produces a
different commit. An exception inside preparation restores the starting
commit, index and owned file bytes without deleting any tag.

### Tagging reviewed main

After the preparation PR merges:

1. Fetch `origin/main`, switch to `main`, and fast-forward only. Require a clean
   worktree and exact equality among local `HEAD`, refreshed `origin/main`, and
   the preparation PR's merge commit. Stop on unexpected upstream changes.
2. Verify all PR checks and the exact merged-main CI run succeeded. Run strict
   `uv run --frozen python scripts/release_readiness.py` without branch or
   dirty-tree exceptions. Inspect remote and local refs to establish that the
   proposed release tag does not already exist.
3. Run `scripts/validate_release_tag.py --tag vX.Y.Z --sha <checked-main-sha>`
   with the full verified SHA. Require the package version, dated changelog and
   main ancestry checks to pass.
4. Create a lightweight tag on that exact SHA with
   `git tag --no-sign vX.Y.Z <checked-main-sha>`. Do not use `-a`, `-s` or `-m`.
   Verify `git rev-parse refs/tags/vX.Y.Z` equals the checked SHA. Lightweight
   tags are required because the remote verifier compares the exact ref object
   to the release commit; `--no-sign` also avoids a local `tag.gpgSign` setting
   silently creating a different tag object.
5. Push only `refs/tags/vX.Y.Z:refs/tags/vX.Y.Z` to `origin`, without force.
   Watch the Release workflow and then run strict remote readiness from the
   unchanged clean main/tag. A tag push alone does not establish publication.

Replace the version and SHA placeholders with the checked values. Do not rerun
the preparation helper after merging: the project is already at that version,
and the helper intentionally requires a greater next version. Do not bypass PR
checks, change branch rules, or move an existing tag to complete this handoff.

### Legacy direct-main transaction

The original mode remains available for repositories whose governance permits
a direct-main release transaction. It is not the recommended path for this
repository's PR-protected main. Without `--prepare-only`, the script enforces:

1. **Branch and tree**: require a clean `main` worktree.
2. **Current upstream**: fetch `origin/main` and require `HEAD` to match it
   exactly. Being merely ahead, behind, or ancestrally related is insufficient.
3. **Current version**: require `pyproject.toml` and the package fallback to
   agree.
4. **New version**: accept stable `X.Y.Z` SemVer only, with no leading-zero
   components, and require it to be greater than the current version.
5. **Release notes and tag**: require a dated, calendar-valid
   `## [X.Y.Z] - YYYY-MM-DD` changelog section and an absent local release tag.
6. **Confirmation**: default to No before any mutation.
7. **Snapshot**: capture every file the release transaction owns.
8. **Synchronize surfaces**: update `pyproject.toml`, the package fallback,
   both roadmaps, the engineering refinement plan, supply-chain recipe,
   exact-version POSIX and PowerShell installer helpers,
   correlation and statistical-assurance review headers, Claude Code plugin
   manifest, `CITATION.cff`, `uv.lock`, generated surface inventories, and the
   generated CLI surface.
9. **Authoritative validation**: run the complete `scripts/check.py` gate on
   the prospective tree, then run release readiness with the expected dirty
   release-owned files.
10. **Commit and tag**: stage only the owned release paths, create the release
    commit, and create `vX.Y.Z`.
11. **Atomic push prompt**: default to No. If accepted, push `main` and only the
    exact new tag in one `git push --atomic` transaction. If declined, the
    commit and tag remain local for review.

Any exception or interruption inside the file-mutation, validation, commit, or
tag boundary deletes the owned tag if created, restores the starting index and
commit, and restores every snapshotted file. A declined or failed final push
does not discard the successfully validated local commit and tag.

### Dry-run mode

```bash
uv run python scripts/release.py --dry-run
uv run python scripts/release.py --prepare-only --dry-run
```

Checks the current clean `main` tree, or the named non-main preparation branch,
against the locally known `origin/main`
ref, validates the proposed version, changelog entry, and local tag absence,
then runs the complete quality gate on the current tree. It makes no
release-owned file or Git-ref changes and performs no network calls; validation
may write local coverage, test and cache artifacts. It reports the prospective
synchronization and release transaction, but it cannot simulate the post-bump
tree or its release-readiness result.

---

## Automated half: `.github/workflows/release.yml`

Triggered by any tag matching `v*` pushed to the repo. The workflow:

1. **preflight**: checks out full history, fetches the current remote `main`, and
   validates exact stable tag syntax, package-version agreement, a dated
   nonempty changelog section, the tagged SHA, and containment in current
   `origin/main`.
2. **test**: after preflight, runs the exact stable v1.28.1 and v2.0.0 MCP SDK
   matrix, then delegates to the complete `scripts/check.py` gate with
   added-line text hygiene covering the full previous-release-to-tag range. A
   separate hash-pinned requirements export covering runtime dependencies, all
   development groups, and all extras is audited with `pip-audit`. The audit
   runner resolves the installed auditor under Python isolated mode and retries
   once only for recognized transport failures; findings, unknown failures, and
   a second transport failure remain fatal.
3. **build**: after `test`, exact uv 0.13.9 uses the hash-locked build graph to
   produce one sdist, constructs one wheel from that exact sdist, and
   immediately seals both under `dist/`. Main CI runs the same sequence twice,
   requires matching hashes, and passes the same built wheel to blocking
   Windows, Linux, and macOS installed-artifact jobs.
4. **package-smoke**: after `build`, downloads the sealed artifact into a
   separate read-only job, requires exactly one tag-matching canonical wheel
   and sdist, and downloads the standalone smoke helper and portable manifest
   from a separate test-job artifact. It installs the wheel in a fresh
   environment outside the workspace, verifies both CLI entry points and
   import origin/version, checks packaged catalogs and MCP resources/tools,
   and exercises two relocated manifest launches sharing persistent plugin
   data. The job has no source checkout. Dependency installation may download
   packages; the subsequent probes perform no domain lookups and include a
   Python socket tripwire. This is not an OS sandbox, a real external client
   evaluation, or a cross-environment reproducible-build claim.
5. **sbom**: after `test`, generates the CycloneDX release SBOM independently of
   the package build path, adds the project root and dependency edge, and
   validates the resulting document. Every nonzero audit status is fatal here,
   including a finding first disclosed after `test`; SBOM tool or validation
   failure is also fatal.
6. **attest**: after `build` and `sbom`, records one GitHub provenance
   attestation whose subject set contains the wheel, sdist, and completed SBOM.
7. **export-attestations**: after `build`, `sbom`, and `attest`, exports the
   GitHub artifact-attestation bundles as
   `recon-tool-<version>.intoto.jsonl` so the GitHub Release carries an offline,
   Scorecard-recognized provenance asset.
8. **publish-pypi**: after `build`, `attest`, `package-smoke`, and `sbom`, uses
   `pypa/gh-action-pypi-publish@release/v1` with OIDC Trusted Publishing and PEP
   740 attestations. No static API tokens.
9. **verify-pypi-parity**: after `publish-pypi`, downloads the sealed pair in a
   read-only job, waits for the exact two PyPI records, and requires both
   SHA-256 digests to match before GitHub publication can proceed.
10. **publish-mcp-registry**: after `verify-pypi-parity`, checks out the tag and
    publishes `server.json` with `mcp-publisher login github-oidc`. The binary
    is pinned to `v1.8.9` and verified with cosign before it runs. The job does
    not download `dist/` or execute project code. The Registry entry is a
    metadata pointer. It does not block the human GitHub Release check, and the
    workflow stays red until this job succeeds. The Registry is preview and can
    reset.
11. **github-release**: after `build`, `attest`, `export-attestations`,
    `package-smoke`, `sbom`, and `verify-pypi-parity`, verifies the human-published
    release against all four sealed files from this original run. This job has
    `contents: read` and performs no release creation, upload, edit or deletion.
    It fails with a human handoff until that release exists. The verifier binds
    local HEAD and local/remote tag to the original workflow SHA, exact tag/title
    and published stable state, the human `blisspixel` User account as release
    author and every asset uploader, exact four-asset inventory and bytes,
    completed SBOM, hosted tag-bound provenance, and canonical PyPI parity.

The dependency graph blocks both publication channels when tag preflight, the
complete test gate, package build, installed-wheel smoke, provenance
attestation, or SBOM validation fails, while allowing `build` and `sbom` to run
independently after `test`. Once PyPI accepts its immutable files, a parity
failure blocks only the GitHub Release and leaves a visible partial-publication
state. Diagnose the failed row, preserve the existing PyPI files, and rerun the
same tag only when its sealed pair is byte-identical to PyPI. Never manually
rebuild or replace evidence, and never bypass a failed verifier to complete the
second channel.

### Human GitHub Release handoff

The final job's expected initial failure does not undo PyPI publication. Keep
its run ID and original source SHA. GitHub releases and asset uploads belong to
the maintainer's existing authenticated session, never the workflow token. No
new token, exported credential or repository secret is needed. Confirm
`gh api user --jq '[.login, .type] | @tsv'` reports `blisspixel` and `User`.
Do not use a bot-created draft: publishing an existing object is not a supported
way to change its author.

Before any release mutation, require the clean exact tag/main and original-run
binding described below. Inspect the failed final job and require all upstream
jobs to have succeeded. Download only that original run's `dist`, `sbom`, and
`provenance` artifacts into separate empty directories with
`gh run download <original-run-id> --name <artifact-name> --dir <directory>`.
Never manually rebuild or replace evidence. Inspect the exact wheel, sdist,
completed SBOM and provenance inventory, verify their SHA-256 hashes against the
original run's attested subject digests, validate the SBOM without rewriting it with the existing
`scripts.finalize_sbom.validate_completed_sbom(Path(<sbom>), "X.Y.Z")` Python
function, and verify wheel, sdist and SBOM provenance as documented in
[supply-chain.md](supply-chain.md). Run the canonical
`scripts/check_release_channel_parity.py --version X.Y.Z --dist-dir <dist>`
against that sealed pair. Preserve the output. Any mismatch blocks promotion.

Inspect the release endpoint first. A new draft is appropriate only after an
authenticated lookup confirms that the matching release is absent. An unknown
lookup error is not absence. If an existing release is partial, bot-owned or
mismatched, stop and inspect it; neither this workflow nor this runbook repairs,
replaces or clobbers its assets. A complete matching human-owned published
release can go directly to original-job verification, including if immutable.

For an absent release, use the maintainer session to create a draft with the
exact `vX.Y.Z` tag and title, notes extracted from that version's checked
`CHANGELOG.md` section, and only the four sealed files. The command shape is
`gh release create vX.Y.Z --repo pueo-labs/recon --verify-tag --draft
--title vX.Y.Z --notes-file <notes-file> <wheel> <sdist> <sbom> <provenance>`.
Use explicit file paths, not a wildcard over a mixed directory. Do not use
automatically generated contributor notes. Inspect the draft author and every
asset uploader, then run the read-only draft verifier before publishing. Run it
in the project environment; a bare system `python3` can lack its dependencies:

```bash
uv run --frozen python scripts/verify_github_release.py --version X.Y.Z \
  --source-sha <original-full-source-sha> \
  --dist-dir <sealed-dist-directory> --sbom-dir <sealed-sbom-directory> \
  --provenance-dir <sealed-provenance-directory> --check-draft --release-id <draft-numeric-id>
```

Use the draft's positive numeric release ID from the creation response or its
authenticated metadata, not an asset ID. This mode reads the numeric release
and asset REST endpoints; the by-tag endpoint is for published releases.
It requires that response ID to match and requires a complete human-owned
draft and all the same byte,
provenance and parity checks; it does not establish published status. After it
passes, re-read the draft through its numeric REST endpoint. Require the same
positive release ID, exact tag and title, human author and asset uploaders,
draft state and complete verified inventory. Recheck the existing remote tag
against the original workflow SHA; stop if the draft or tag changed.

Promote that same numeric object with the maintainer session, replacing the
placeholders only with the verified draft ID and stable version:

```bash
gh api --method PATCH "repos/pueo-labs/recon/releases/<draft-numeric-id>" \
  -f tag_name=vX.Y.Z -F draft=false -F prerelease=false -f make_latest=true
```

The REST update explicitly supplies the checked tag, published stable state
and latest-release designation; it does not substitute for the preceding
identity, inventory and remote-tag verification. Re-read the published object
and require the same release ID before rerunning the final verifier.
Rerun only the original failed `github-release` job. Its default verification
requires published status and read-only credentials; it cannot create a new
release or upload assets on a retry. Never delete and recreate a mismatched
release to make a check pass.

### Recovery after partial publication

A failed tagged run is recoverable only through the original run and unchanged
tag. GitHub reruns retain the original `GITHUB_SHA` and `GITHUB_REF`; failed jobs
and jobs that depend on them may execute again. The parity gate therefore
remains the boundary that proves any rerun distribution bytes still match the
immutable PyPI files. The run-selection check also requires the chosen run's
`headSha` to equal the unchanged local tag and `HEAD` before a rerun begins.

Inspect and rerun the failed path with the exact run ID:

```bash
set -euo pipefail

recovery_fail() {
  printf 'FAIL: release recovery requires %s\n' "$1" >&2
  exit 1
}

VERSION="$(uv run python -c 'import pathlib, tomllib; print(tomllib.loads(pathlib.Path("pyproject.toml").read_text(encoding="utf-8"))["project"]["version"])')" || recovery_fail "uv to read the project version"
CURRENT_BRANCH="$(git branch --show-current)" || recovery_fail "git to report the current branch"
if ! test "${CURRENT_BRANCH}" = "main"; then
  recovery_fail "a clean main branch"
fi
WORKTREE_STATUS="$(git status --porcelain --untracked-files=normal)" || recovery_fail "git to inspect the worktree"
if ! test -z "${WORKTREE_STATUS}"; then
  recovery_fail "a clean worktree"
fi
HEAD_SHA="$(git rev-parse HEAD)" || recovery_fail "git to resolve HEAD"
TAG_SHA="$(git rev-list -n 1 "refs/tags/v${VERSION}" 2>/dev/null)" || recovery_fail "git to resolve the local tag v${VERSION}"
if ! test -n "${TAG_SHA}" || ! test "${HEAD_SHA}" = "${TAG_SHA}"; then
  recovery_fail "the local tag v${VERSION} to resolve to HEAD"
fi
RUN_ROW="$(gh run list --workflow Release \
  --branch "v${VERSION}" --event push --limit 1 --json databaseId,headSha \
  --jq '.[0] | [.databaseId, .headSha] | @tsv')" || recovery_fail "GitHub CLI to list the Release workflow run"
read -r RUN_ID RUN_HEAD_SHA <<< "${RUN_ROW}"
if ! test -n "${RUN_ID}"; then
  recovery_fail "an exact Release workflow run for v${VERSION}"
fi
if ! test "${RUN_HEAD_SHA}" = "${HEAD_SHA}"; then
  recovery_fail "the selected Release run to target HEAD"
fi
printf 'PASS: release recovery preconditions hold for run %s at %s\n' "${RUN_ID}" "${HEAD_SHA}"
gh run view "${RUN_ID}" --log-failed
gh run rerun "${RUN_ID}" --failed
gh run watch "${RUN_ID}" --exit-status
uv run python scripts/release_readiness.py --remote
```

Run this block in Bash or Git Bash so strict mode and the here-string use the
documented shell semantics. A named precondition failure exits before any rerun.

Use that rerun path for transient timeouts, rate limits, temporary 5xx
responses or delayed PyPI visibility. Once only the final job has failed,
complete the human handoff first and rerun only that original failed final job. Do not rerun blindly after a digest,
inventory, tag, signer, source, SBOM, or provenance mismatch. Preserve the
failed output and inspect the original workflow artifacts first.

This runbook applies to recovery of the current project version while clean
`main` still points at that exact release tag. The final job rechecks the
remote tag against the original workflow SHA and requires a complete matching
human-owned published release. A draft, prerelease, partial inventory,
unexpected asset, duplicate asset, malformed response, missing tag, moved tag,
wrong author/uploader or any byte/provenance mismatch stops recovery. It never
mutates release state. If PyPI contains incorrect immutable bytes, do not
attempt to overwrite them; follow the documented PyPI project-management
yanking path and cut a corrected version. A run is recovered only after the
strict remote readiness command passes in full.

Workflow permissions are least-privilege: every job has `contents: read`;
`attest`, `publish-pypi`, and `publish-mcp-registry` receive `id-token: write`
only where OIDC is needed.
The existing attestation export uses the workflow token for read-only evidence
access. No publishing token is added to the final job.

---

## Pre-release checklist

Before running `scripts/release.py --prepare-only`:

- [ ] All planned changes, including the new dated changelog section, are
      merged through a checked PR to `main`; current-main CI has passed, and
      the clean preparation branch starts exactly at refreshed `origin/main`.
- [ ] `CHANGELOG.md` has a finalized `## [X.Y.Z] - YYYY-MM-DD` section.
- [ ] `CITATION.cff`, both roadmaps, the package fallback, and the supply-chain
      recipe match the current project version. The helper updates them to the
      prospective version and changelog date inside its transaction.
- [ ] `docs/roadmap.md` still describes the next work accurately and does not
      duplicate `CHANGELOG.md`.
- [ ] `docs/stability.md` has been updated if any public surface changed.
- [ ] `docs/schema.md` has been updated if any top-level JSON field changed.
- [ ] `CHANGELOG.md` includes the generated `### Tool Surface Changes` line.
- [ ] README examples and docs references still match the shipped CLI behavior.
- [ ] Exact stable v1.28.1 and v2.0.0 MCP SDK compatibility passes on the
      release tree when MCP compatibility code or dependencies changed.
- [ ] `docs/supply-chain.md` keeps the consumer verification quick path on the
      current version and release asset names.

After the tag is published and the PyPI release exists:

- [ ] Confirm the GitHub Release contains exactly the wheel, sdist, SBOM, and
      `recon-tool-<version>.intoto.jsonl`.
- [ ] Run `uv run python scripts/release_readiness.py --remote` after the
      release so CI, the live branch ruleset, public Scorecard API freshness,
      PyPI files, PyPI provenance, exact GitHub Release assets, completed SBOM,
      tag-bound GitHub provenance, cross-channel digests, and citation metadata
      are checked together.

The direct `pipx` / `uv` / `pip` install paths need no per-release action. The
release transaction updates and validates both reviewed installer-helper pins
before creating the tag.

---

## Hotfix releases

For a patch-level fix to the last released minor version:

1. Branch from the tag: `git checkout -b hotfix/v1.0.1 v1.0.0`
2. Cherry-pick or write the fix.
3. Add a `## [1.0.1] - YYYY-MM-DD` section to `CHANGELOG.md`.
4. Merge the hotfix through a checked PR to `main` and wait for exact-main CI.
5. Follow the PR-first preparation and reviewed-main tagging steps above. Do
   not tag the hotfix or preparation branch directly; publication must name
   the checked merged-main commit.

---

## Yanking a broken release

PyPI supports yanking (not deleting) a broken release. This discourages new
installs but leaves the version available for reproducibility of systems
that already pinned it. Twine does not provide a yank command. An authorized
project maintainer must open the affected release in the PyPI project management
UI, choose the yank action, and record a concise reason.

After yanking:
1. Cut a `X.Y.(Z+1)` release with the fix using the normal process.
2. Add a note to the yanked version's CHANGELOG section explaining the yank.
3. Pin dependents to the new version where possible.

Never delete a tag from `origin`. Tags are part of the reproducibility
contract. If a tag is wrong, yank the PyPI release and cut a new one.

---

## Version numbering

recon follows [Semantic Versioning](https://semver.org) per the
[stability policy](stability.md).

- **MAJOR** (e.g. 1.x → 2.0): breaking change to any **stable** surface
  listed in `docs/stability.md`. Requires a deprecation window in the prior
  minor release.
- **MINOR** (e.g. 1.0 → 1.1): backward-compatible additions. New CLI flags,
  new optional JSON fields, new MCP tools, new fingerprints/signals.
  Breaking changes to **experimental** surfaces are allowed here.
- **PATCH** (e.g. 1.0.0 → 1.0.1): backward-compatible bug fixes. No new
  features, no schema changes.

Pre-1.0 releases did not honor this contract; v0.9 and v0.10
included breaking changes within the minor. From 1.0 onward the contract
is enforced.

---

## Python support policy

The supported range is the set advertised in `pyproject.toml` classifiers and
tested in CI.

Current tested range: **Python 3.11 through 3.15**.

Dropping a Python version is a compatibility change and should be called out in
`CHANGELOG.md`. A minor release should warn first when practical.

## Repository transfer checklist

The 2026-10-29 transfer changes the repository to `pueo-labs/recon`, not the
PyPI project name. Keep `recon-tool`, the `recon` command, and existing release
versions. This change prepares metadata only: it does not publish a package,
move a tag, replace old artifacts, or migrate an existing registry record.

Before the next separately authorized release, complete these external steps:

1. **PyPI Trusted Publishing.** On the existing `recon-tool` project's
   Publishing settings, register the GitHub owner `pueo-labs`, repository
   `recon`, workflow filename `release.yml`, and environment `pypi`. Verify the
   new configuration, then remove the obsolete publisher for the old owner.
   Do not rename or recreate the PyPI project, upload another 2.27.0, or add a
   long-lived API token. The workflow already uses OIDC. See the
   [PyPI configuration guide](https://docs.pypi.org/trusted-publishers/adding-a-publisher/).
   PyPI project URLs and the rendered description come from uploaded package
   metadata; merging this change does not update the already published files.
2. **GitHub controls.** Check organization Actions policy and repository app
   access, required status checks and rulesets/branch protection, release-tag
   protection, and the existing `pypi` environment's permitted refs and
   reviewers. Keep the human `@blisspixel` CODEOWNER and release author/uploader
   checks; an organization is not a human account. Confirm that maintainer
   retains repository write access. Review repository/environment secrets and
   organization-secret access after the transfer. The checked-in workflows
   reference only the automatic `GITHUB_TOKEN`; PyPI and MCP publication need
   no new credential. The required `gitleaks` job uses the checksum-pinned
   standalone open-source CLI; the organization-only license required by
   `gitleaks-action` is not needed. Keep its full-history scan and fail-closed
   result. Do not disable protection to get a green run.
3. **Discovery and hosting.** Update the repository URL on OpenSSF Best
   Practices project 15800 and verify Scorecard at the new repository path.
   If GitHub Pages is enabled, review its source, custom domain, DNS, HTTPS,
   and public URL; this repository has no Pages deployment workflow. Check
   external integrations and local Git remotes. Existing Claude Code users
   should follow the [marketplace migration](../agents/claude-code/README.md#marketplace-migration).
4. **MCP Registry, in order.** `server.json` and the README now prepare
   `io.github.pueo-labs/recon`. The official rules allow
   `io.github.<orgname>/<server>`; the hyphenated organization is retained.
   [GitHub OIDC](https://modelcontextprotocol.io/registry/github-actions)
   authenticates the repository-owner namespace. Keep the job's
   `id-token: write`, pinned and verified publisher, and dependency on PyPI
   parity. First publish a separately approved new package version containing
   `<!-- mcp-name: io.github.pueo-labs/recon -->` in its PyPI description, then
   let the tag's workflow publish the matching registry entry. The
   [PyPI ownership check](https://modelcontextprotocol.io/registry/package-types)
   reads the published description, not this checkout. Until then, v2.27.0
   remains under `io.github.blisspixel/recon`; do not retry that immutable
   version with new package metadata or claim the new entry is already live.
5. **Deprecate the old registry entry only after the new entry is verified.**
   With separate authorization and authentication as the old namespace owner
   (`blisspixel`), use the pinned publisher's
   [status command](https://github.com/modelcontextprotocol/registry/blob/v1.8.9/docs/reference/cli/commands.md).
   Do not try this with the new repository's OIDC identity, which does not
   own the old namespace. Deprecation preserves history; do not delete it.

   ```bash
   mcp-publisher login github
   mcp-publisher status --status deprecated --all-versions \
     --message "Moved to io.github.pueo-labs/recon." io.github.blisspixel/recon
   ```

   Re-read the old entry to confirm its deprecated status and migration
   message, and the new entry to confirm the intended package/version. No
   registry status change is part of this repository-only transfer.
