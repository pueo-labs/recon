# Contributing

For atomic fingerprint and structural-pattern maintenance, start with the
harness-neutral
[maintenance skill](agents/maintainer/skills/recon-catalog-maintenance/SKILL.md)
and its [offline example and monthly receipts](docs/catalog-maintenance.md).

Thanks for your interest in contributing to recon. Read the section below
first: it is the project's single non-negotiable rule. By taking part you also
agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## No evaluated-target data

**Never commit evaluated-target data.** This includes real organization names
used as targets, real target apexes or hosts, tenant identifiers, target-owned
record values, screenshots, and per-domain output. The rule applies to commits,
PRs, issue comments, code comments, YAML fingerprints, test fixtures,
snapshots, and discussion threads.

Use explicit synthetic identities under `.invalid` or `.test`, or IETF
reserved placeholders (`example.com`, `example.org`, `example.net`). These
names teach the method without implying an organization or evaluated target.

It does **not** apply to:

- Vendor / product names recon detects as part of a tech stack
  (Cloudflare, Okta, Microsoft 365, Google Workspace, etc.).
  These are detection classes, not targeting examples.
- Upstream service hostnames recon itself queries
  (`login.microsoftonline.com`, `crt.sh`, `api.certspotter.com`,
  `dns.google`, etc.).

Accuracy reports and live-validation work use real apexes locally;
that's why `validation/corpus-private/`, `validation/runs-private/`,
`validation/live_runs/`, and `validation/local/` are permanently gitignored.
The committed validation tooling (the
runner, gap finder, triage script, synthetic-corpus generator, the
synthetic corpus itself) is allowed; real-apex inputs and per-domain
outputs are not. Aggregate counts produced by the corpus aggregator
may be committed; per-domain results never.
`scripts/check_validation_hygiene.py` runs in the local gate and release
readiness to catch forced-added private paths and target-domain fields in
validation artifacts. It is a backstop, not a substitute for reviewing prose.

If a bug report needs a real domain to reproduce, do not open a public issue.
Use the private non-security report path in
[`docs/data-handling-policy.md`](docs/data-handling-policy.md#private-non-security-reports),
or describe the behavior with a reserved synthetic fixture when the real identity is not
load-bearing. Public issue forms require an acknowledgement that target names,
records, identifiers, screenshots, and per-domain output were removed.

Reviewers actively check incoming PRs for evaluated-target data before merge.
A PR found to contain it will be rejected and the contributor asked to
refactor it against reserved synthetic sentinels.

---

This doc answers:

- [What kinds of contributions we're looking for](#what-were-looking-for)
- [Help improve and review recon](#help-improve-and-review-recon)
- [What's out of scope](#whats-out-of-scope)
- [Local customization vs upstream contribution](#local-customization-vs-upstream-contribution)
- [How to contribute a fingerprint](#adding-fingerprints)
- [How to contribute a signal or profile](#adding-signals-and-profiles)
- [How to contribute code](#code-changes)
- [How to report a bug or suggest an idea](#bug-reports-and-ideas)

## Quick Start

Use uv 0.13.5 for repository tasks: CI, the release workflow, and artifact
builds all pin that exact release, so it is the version that reproduces lock,
constraint, test, and release-shaped build behavior. `pyproject.toml` requires
uv `>=0.13.4,<0.14`, excluding the affected bundled CA store. Dependabot and
other lock-update tooling must meet the same security floor. If a hosted
updater still bundles older uv, its update must fail closed until that tool is
upgraded; do not lower the floor to restore compatibility. The hosted
Dependabot executable is not verified by the local gate.

`.python-version` pins the local toolchain to final CPython 3.15.2. uv 0.13.5
can use an installed 3.15.2 interpreter. Its managed download index does not
yet offer a 3.15.2 build, so install that interpreter before recreating the
environment. CI asks setup-python for 3.15 and sets `UV_PYTHON` to that
request, which tracks setup-python's maintained 3.15 patch.
Existing managed interpreters and virtual environments are not updated just
by changing this manifest. See the
[toolchain remediation procedure](docs/supply-chain.md#toolchain-ca-remediation)
for environment updates and verification. CI installs each matrix interpreter
with setup-python.

```bash
git clone https://github.com/pueo-labs/recon.git
cd recon
uv self update 0.13.5      # select the repository's reproducible uv release
uv --version                # must report uv 0.13.5
uv sync                    # installs the dev group (pip: pip install -e . --group dev, pip 25.1+)
uv run pre-commit install              # activate pre-commit hooks
uv run pre-commit install --hook-type commit-msg
uv run python scripts/release_readiness.py --allow-dirty
uv run python scripts/check.py         # canonical local gate (--fast skips tests)
```

The `commit-msg` hook is required separately: file-content hooks cannot check
commit trailers. Read the [authorship rule](AGENTS.md#attribution-and-authorship)
before committing or pushing.

`uv run python scripts/check.py` is the canonical local gate: Ruff, Pyright using the
complete `pyproject.toml` include and exclude contract, the coverage-gated test
run, catalog and generated
artifact checks, validation and text hygiene, tracked Markdown link and local
heading-anchor validation, workflow and dependency-export guards, interface and
paper checks, and file-size/complexity ratchets. A local pass is required before
every push, but it does not replace remote CI. GitHub Actions also exercises the
supported OS and Python matrix, the package-index MCP matrix, actionlint,
`pip-audit`, hostile fuzzing, and reproducible-build checks. CI supplies the
complete pushed or pull-request revision range to the text-hygiene stage so an
earlier prohibited line cannot be hidden by a later cleanup commit. The complete
local test stage uses at most four file-grouped workers and combines branch
coverage; focused tests remain serial by default.
The standards this project holds itself (and any AI working in it) to are in
[docs/engineering-practices.md](docs/engineering-practices.md); load-bearing
design decisions are in [docs/adr/](docs/adr/). Coding agents should read
[AGENTS.md](AGENTS.md#working-in-this-repository) for the short operational
briefing, then this file and the engineering-practices standard.

Project hygiene: keep examples reserved and synthetic, keep validation artifacts
aggregate-only, and avoid dead code or placeholders. Use IETF reserved `.invalid`
namespaces or the other reserved examples described above.

---

## What we're looking for

recon is a **narrow tool** focused on one thing: passive, zero-creds
domain intelligence. Contributions that tighten what the tool already does
are welcome:

| Contribution type | Bar | Examples |
|---|---|---|
| **New fingerprints** | Must use documented public metadata only. Specific pattern, not generic substring. Tested against a public record shape expected to match. | "Add Statsig TXT verification", "Add Workspace ONE CNAME" |
| **Freshness backfill** | Confirm an independently reviewed family against the vendor's current public page. Add or refresh `verified` and `reference`. Relabel a still-supported host as legacy when the vendor now documents a newer default. Do not stamp today's date without that page. | "Date the Microsoft 365 MX family against the current Learn article"; "Relabel Google Workspace `aspmx.*` as the documented pre-2023 series" |
| **Refined fingerprints** | `match_mode: all` to eliminate false positives, improved regex, broader selector coverage. | Converting ambiguous slug to a chained pattern |
| **New signals** | Must derive from existing evidence. Hedged language. | "AI tooling indicators observed alongside identity-provider signals" |
| **New profiles** | Must reweight existing observations; cannot invent new ones. | "Retail / e-commerce" profile |
| **Bug reports** | Reproducible with a reserved domain, a minimal synthetic fixture, and sanitized diagnostics. Real target output uses the private non-security report path. | Wrong provider classification, insight wording, display glitch |
| **Accuracy reports** | A controlled or otherwise well-understood public record shape, plus the exact observation recon got wrong. | "The `alpha.invalid` fixture publishes the documented M365 MX shape, but recon reports custom or unclassified MX" |
| **Documentation fixes** | Typos, clarifications, better examples. | README, CONTRIBUTING, docs/* |
| **Performance improvements** | With before/after measurement. Hot paths: `detect_provider`, `_curate_insights`, DNS query batching. | Reducing average lookup time, eliminating redundant DNS queries |
| **Test additions** | Sparse-data fixtures, adversarial inputs, corner cases. | Domain with zero MX + no tenant, IDN / punycode, wildcard DNS |

The **engine stays lean; the data grows**. The engine is feature-complete as
of v2.16; the standing work is keeping fingerprints current. Most
contributions should be YAML additions, refinements, or dated freshness
backfills; that is the intended scaling path for the tool. Code changes earn
their place against the post-1.0 ethos: correctness, reliability,
explainability, composability, then new features, in that order.

---

## Help improve and review recon

Interested in public DNS, email, identity, or explaining what evidence can
actually support? There is room to help make recon better. A small correction,
a careful review, or a useful counterexample is a good first contribution. You
do not need to be an expert or bring a private domain inventory.

Useful starting points include:

- Check a fingerprint against the vendor's current documentation.
- Add synthetic lookalike, sparse-data, or provenance regression cases.
- Improve a confusing explanation or review a proposed change's evidence.
- Help keep dependency updates, releases, and contributor documentation current.

For a bounded change, open a pull request against `main` with its supporting
evidence and verification. If you would like to help regularly, including
independent review or a future maintainer role, open a privacy-safe
[idea issue](https://github.com/pueo-labs/recon/issues/new/choose) describing
your interests. The maintainer can help identify a manageable first task.

recon currently has one maintainer. A sustained review role can grow from
useful contributions; it does not require committing to ongoing maintenance
at the outset. Independent human review would strengthen the project and allow
the [solo-maintainer review exception](docs/supply-chain.md#solo-maintainer-review-exception)
to be revisited when a qualified reviewer is available. No additional
maintainer or reviewer has been appointed.

---

## What's out of scope

These are **intentional rejections**, not gaps waiting to be filled. Don't
spend effort on PRs that will be closed:

### Violates invariants (hard no)

- **Collection beyond the documented public-metadata boundary.** The allowed
  surface is public DNS, certificate transparency, unauthenticated identity
  discovery, the default MTA-STS policy fetch, and opt-in Google CSE and BIMI
  document fetches. No arbitrary target HTTP requests, port scans, service
  probes, or brute-forcing. See
  [ADR-0011](docs/adr/0011-public-metadata-collection-boundary.md).
- **Anything requiring credentials or API keys.** No OAuth, no PAT, no
  paid APIs (SecurityTrails, Censys, Shodan, etc.).
- **Aggregated local database.** Per-domain JSON files only. No SQLite/DuckDB
  store.
- **Bundled ML models, embeddings, or large data files.** ASN / GeoIP /
  fingerprint embeddings are all out.
- **Plugin systems that run user code.** YAML-only extensibility.

### Not this tool (soft rejections)

- HTML / PDF output, web dashboard, TUI, `recon serve`, interactive REPL
- STIX / MISP / Maltego / Excel / SBOM / Sigstore exports
- Scheduled / daemon mode with alerts
- Generic subdomain brute-forcing (DNS wordlist attacks)
- People-search / email-harvesting OSINT
- Docker image, PyInstaller single-binary

If you want any of these, **pipe `--json` into the right tool**. recon is a
CLI + a local-stdio MCP server; the integration surface is JSON, pipe it
wherever you need.

If unsure whether your idea fits, open an **idea** issue (template below)
and ask before writing code.

---

## Local customization vs upstream contribution

recon supports both.

**Local customization** (for your own use, never pushed):
- `~/.recon/fingerprints.yaml`: custom fingerprints (additive only; cannot override built-ins)
- `~/.recon/signals.yaml`: custom signal rules
- `~/.recon/profiles/*.yaml`: custom posture profiles
- `RECON_CONFIG_DIR`: override the default `~/.recon` location

Anything that's specific to your organization, your vendors, or your
internal naming should stay local.

**Upstream contribution** (shared with everyone via a PR):
- Detections that apply to at least one publicly-known service
- At least one vendor-published example, documented public record shape, or
  maintainer-local observation supporting the pattern. Real apexes stay local;
  use a reserved synthetic or aggregate description in the PR.
- General-purpose (not a specific org's internal pattern)

---

## Validation strategy

The committed corpus is synthetic-only. The 79-fixture synthetic
corpus lives at `validation/synthetic_corpus/` along with its
generator and the per-run aggregate output. Both are safe to commit
and reproducible by anyone who clones the repo.

Real-apex validation is maintainer-side. Real corpora land in
`validation/corpus-private/` (gitignored). Per-run scans land in
`validation/runs-private/<UTC-stamp>/` (gitignored). The corpus
aggregator (`validation/corpus_aggregator.py`) emits aggregate
counts only and is safe to run locally; per-domain results never
leave the maintainer's machine.

Release notes default to citing synthetic numbers. Real-corpus
aggregate counts may be cited in release docs when they are
load-bearing (the v2.0 corpus-run runbook in
`validation/v2.0-corpus-run-runbook.md` documents this path), but
the per-domain corpus stays local.

---

## Adding fingerprints

The most common contribution. Fingerprints live under
`src/recon_tool/data/fingerprints/`, one YAML file per category. These split
YAML files are canonical contributor source. Installed wheels use the checked-in
generated JSON catalog and do not ship a second YAML runtime copy.

### 1. Find the right file

```bash
recon fingerprints list --category ai       # where do AI tools live?
recon fingerprints show openai              # what does the existing pattern look like?
```

Current layout:

```
src/recon_tool/data/fingerprints/
├── ai.yaml                 AI / LLM providers and agent frameworks
├── crm-marketing.yaml      CRM, sales intelligence, and ad platforms
├── data-analytics.yaml     Warehouses, BI, and observability
├── discovered-signals.yaml Catalog discoveries promoted through review
├── email.yaml              Email providers, gateways, and policy tooling
├── infrastructure.yaml     Cloud, CDN, DNS, CAs, and CI/CD
├── productivity.yaml       Suite tools, helpdesk, and HR
├── security.yaml           EDR, SIEM, IdP, and zero-trust access
├── surface.yaml            Public custom-domain and hosting surfaces
├── verifications.yaml      Public ownership and service verification tokens
└── verticals.yaml          Education, nonprofit, and payments
```

Pick the file that matches your service's primary category. If nothing
fits, open an issue before adding a new category file; the split is
intentionally coarse.

### 2. Add your entry

Use the scaffolding command when possible:

```bash
recon fingerprints new service-slug
```

It walks through the stable schema and specificity checks before emitting YAML.

```yaml
- name: Service Name
  slug: service-slug          # lowercase, unique across ALL files
  category: Category Name     # use an existing category if possible
  confidence: high             # rule-level evidence strength, not a probability
  detections:
    - type: txt                # txt, spf, mx, ns, cname, cname_target, subdomain_txt, caa, srv, dmarc_rua
      pattern: "^service-domain-verification="
      description: What this record means
      reference: https://vendor.example/docs/domain-verification
      verified: 2026-07-17
```

`description` should explain the observable record. `reference` is optional,
but preferred when public vendor documentation exists. Every new detection
needs a valid, non-future `verified` date recording when its provider reference
or disclosure-safe aggregate basis was checked. The diff-aware catalog gate
allows the legacy undated backlog but rejects new undated rules. Freshness
backfill of that backlog is a first-class contribution: re-read the vendor
page, date only the detections it still names, and relabel a still-supported
host as legacy when the vendor now documents a newer default. See
[catalog-strategy.md](docs/catalog-strategy.md#3-freshness). Do not add
fields that are not in the stable data-file schema unless a separate schema
change has already been accepted.

### 3. Validate locally before opening a PR

```bash
recon fingerprints check                    # validates the built-in catalog
recon fingerprints check path/to/custom.yaml  # validate a candidate file
```

The `check` command runs the same validation recon uses at runtime
(regex safety via a ReDoS heuristic, required fields, known detection
types, weight range 0.0 to 1.0, `match_mode` value), **plus** a cross-file
duplicate-slug check. Exits 0 on success, 1 on failure with per-entry
error messages.

Under the hood this uses the packaged `recon_tool.fingerprint_validator`
module, so it works from installed wheels as well as source checkouts.
Contributors who prefer invoking the wrapper script directly can still run
`python scripts/validate_fingerprint.py <path>`.

After editing any built-in YAML file, regenerate the runtime artifact:

```bash
uv run python scripts/generate_fingerprint_catalog.py --write
uv run python scripts/generate_fingerprint_catalog.py --check
```

The full local and remote gates compare the generated bytes exactly and reject
stale package data. Generation preserves sorted source-file order, entry order,
detection order, and repeated slugs. Do not edit
`src/recon_tool/data/fingerprints.generated.json` by hand.

### Chained patterns (`match_mode: all`)

For stronger observed-pattern discrimination where a single record could be a
false positive, use `match_mode: all`: the fingerprint only fires when every
listed detection matches. This does not turn the rule's confidence tier into a
calibrated probability or establish active service use. See
[docs/fingerprints.md](docs/fingerprints.md#chained-patterns-match_mode-all) for
details.

For multi-detection changes, run:

```bash
python -m validation.audit_fingerprints
```

The audit is advisory. Use it to document whether the entry should remain
`any`, move to `all`, or be tightened before changing behavior.

### Fingerprint PR checklist

- [ ] Validates locally with `recon fingerprints check`
- [ ] `scripts/generate_fingerprint_catalog.py --check` reports the artifact current
- [ ] `recon fingerprints show <slug>` displays your new entry after load
- [ ] Slug does not collide with an existing one (`recon fingerprints list | grep <slug>`)
- [ ] At least one detection pattern uses a service-specific token (not a generic substring)
- [ ] Detection metadata includes `description`, `verified`, and `reference` when public vendor docs exist
- [ ] Tested against a documented public record shape expected to match, without treating the match as proof of active service use
- [ ] The service's DNS footprint is documented or publicly-observable (not leaked from a customer engagement)
- [ ] Multi-detection entries include a `match_mode` rationale from the audit output or PR notes
- [ ] Common legitimate false-negative cases are captured in the PR body, or in `docs/weak-areas.md` when broadly useful
- [ ] `pytest tests/` passes; property tests must still hold on the sparse-data corpus
- [ ] If the service could trip false positives on domains that merely *visited* the vendor's marketing site, used `match_mode: all`

### Detection description rubric (v1.9.7+)

Every detection rule in `src/recon_tool/data/fingerprints/*.yaml` must
carry a non-empty `description` field. The metadata-coverage gate
(`scripts/check_metadata_coverage.py`) enforces presence at commit
time via pre-commit and at release time via CI. There is no
percentage threshold. Every detection, every category.

The gate enforces *presence*, not quality. The rubric below raises
the bar for new contributions; reviewer judgement is the enforcer
of quality.

**Three-part rubric:**

1. **What the slug detects.** Vendor and the specific evidence
   pattern the detection matches (TXT verification token, MX
   record terminus, CNAME chain, NS pattern, certificate SAN,
   and so on).
2. **What it doesn't detect.** When the slug fires, what claim is
   *not* being made. Common framings: "fires on `X`, not on `Y`";
   "indicates administrative binding to `TENANT`, not active use";
   "evidence of `PRODUCT`, not of `RELATED_PRODUCT` in the same
   vendor family."
3. **Common false positives if known.** Patterns where the
   detection fires correctly but the operator-facing inference
   would be misleading. Skip if no known FPs. Do not invent them.

**Tone:** humble, factual, no overclaim. recon's catalog reads
like an analyst's careful notes, not marketing copy. Avoid
adjectives like "strong", "robust", "cleanly", "the best", and
similar self-congratulatory framings. State what the evidence
shows and what it does not show. Acknowledge limits.

**Style:** no em-dashes (use commas, periods, or parentheses
instead). No emojis. Length target: 1 to 3 sentences. Terser
than docstrings, longer than slug names. The goal is that a
future contributor (or an AI agent reading the YAML) understands
the claim's edge cases without grepping source.

**Worked examples:**

Good (`microsoft365` TXT detection):

```yaml
detections:
  - type: txt
    pattern: ^MS=ms\d{8}$
    description: >-
      Microsoft 365 domain-verification TXT token. Indicates the
      domain is administratively bound to a Microsoft 365 tenant.
      Does not prove the tenant is actively used for email. Some
      orgs verify the domain to claim the namespace but route
      mail elsewhere, so corroborate with MX evidence before
      reading this as "they run M365 email."
```

Good (`cloudflare` NS detection):

```yaml
detections:
  - type: ns
    pattern: \.cloudflare\.com\.$
    description: >-
      Apex NS records resolve to Cloudflare nameservers,
      indicating Cloudflare is the authoritative DNS provider
      for the domain. Does not prove the apex sits behind
      Cloudflare's CDN or WAF (those are separate products on
      the same vendor). Corroborate via Server headers or
      CDN-specific chain motifs for the front-the-origin claim.
```

Placeholder (rejected):

```yaml
detections:
  - type: txt
    pattern: ^MS=ms\d{8}$
    description: "Detects Microsoft 365."
```

Rejection reason: does not explain what the pattern matches, or
what claim is or is not being made. Empty-string presence is the
floor; the rubric is the bar.

### Vendor-doc-sourced `cname_target` rules

`cname_target` rules in `src/recon_tool/data/fingerprints/surface.yaml`
can be added two ways:

1. **Corpus-observed.** The default historical path: a private-corpus
   scan surfaces an unclassified CNAME terminus, the
   `/recon-fingerprint-triage` skill proposes a slug, and the rule
   ships in a release-window catalog-growth pass.
2. **Vendor-doc-sourced** *(v1.9.3.9+)*. A cloud vendor (GCP, AWS,
   Azure, Oracle, IBM, Alibaba, SSE/SASE platforms, PaaS providers,
   etc.) documents customer-facing custom-domain CNAME targets in
   their own product docs. Reading those docs and seeding fingerprints
   from them closes coverage blindspots BEFORE a customer of that
   vendor lands in our private corpus. Corpus-observed alone has a
   built-in bias toward the segments our corpus already represents.

Both paths are encouraged. The **`reference`** field on each
detection makes the source explicit:

- Vendor-doc-sourced: `reference` MUST point at the canonical vendor
  documentation URL that names the CNAME pattern (e.g.
  `https://firebase.google.com/docs/hosting/custom-domain` for
  Firebase Hosting). The PR description should quote the relevant
  doc excerpt so review can verify the pattern is documented as
  stable, not a transient internal endpoint.
- Corpus-observed: `reference` SHOULD point at the vendor's
  marketing page or main docs index, and the PR description should
  cite the private-corpus delta count (e.g. "fired on 23/4270
  domains in the v1.9.2-pre-release scan").

Either way, `reference` exists so a future maintainer can re-verify
the pattern. A rule shipped without a `reference` is allowed but
will be flagged by the advisory metadata-richness audit
(`scripts/check_metadata_coverage.py --report-richness`, v1.9.8+).

Use the fingerprint PR template; GitHub surfaces it automatically.

---

## Adding signals and profiles

> **Heads up: engine changes go through a design doc.** Fingerprints
> are data; contributors can iterate on them freely. The signal,
> fusion, and absence engines are inference code; bad changes there
> affect every domain recon analyses, not just the one you tested.
> Before PRing a change to `src/recon_tool/signals.py`,
> `src/recon_tool/merger.py`, `src/recon_tool/absence.py`,
> `src/recon_tool/fusion.py`, or the two-pass evaluator, please open
> an issue with:
>
> 1. What inference pattern you want to add or change.
> 2. Which domains in the validation corpus would fire differently.
> 3. How you'd guard against false positives on sparse-signal domains.
>
> Data-only contributions (new signals in `signals.yaml` that reuse
> the existing engine) don't need this; they follow the fingerprint
> PR workflow.

### Signals

Custom signal rules derive insights from fingerprint matches. Go in
`~/.recon/signals.yaml` (local) or `src/recon_tool/data/signals.yaml`
(upstream):

```yaml
signals:
  - name: My Custom Signal
    category: Custom
    confidence: medium
    description: Hedged explanation of what this signal suggests
    requires:
      any: [slug-a, slug-b, slug-c]    # fingerprint slugs to match
    min_matches: 2                       # how many must be present
```

Signals must use **hedged language** in their `description` (observed,
likely, fits a pattern) unless the evidence density genuinely justifies a
firmer claim. Sparse-data targets should never see confident verdicts.

See [docs/signals.md](docs/signals.md) for the full schema, including
`metadata` conditions, `contradicts`, `requires_signals`, and
`positive_when_absent`.

### Profiles

Profiles reweight existing observations for a specific audience (fintech,
healthcare, higher-ed, etc.). Go in `~/.recon/profiles/{name}.yaml` (local)
or `src/recon_tool/data/profiles/{name}.yaml` (upstream):

```yaml
name: retail
description: E-commerce / retail posture lens
category_boost:
  email: 1.5          # email security matters more for retail
  saas_footprint: 1.2
signal_boost:
  strong_email_security: 1.5   # keyed by the posture rule name (data/posture.yaml)
focus_categories: [email, identity, consistency]
```

Profiles are **additive only**: they cannot introduce new observations,
only reweight existing ones, and they cannot create false confidence (caps
at "high" salience). `category_boost` keys are observation categories;
`signal_boost` and `exclude_signals` keys are posture observation rule names
(the `name` field of an entry in `src/recon_tool/data/posture.yaml`), matched
against the rule that produced each observation. `exclude_signals` also
removes an observation when an entry appears as a substring of its statement.

---

## Code changes

- Run the full `uv run python scripts/check.py` gate before pushing. The
  [effective typing policy](docs/typing-policy.md) explains exact legacy
  exceptions and the blocking unmasked diagnostic audit; `uv run pyright`
  alone does not perform that additional audit.
- Run `uv run python scripts/check.py`; branch-aware project coverage must stay
  at or above the enforced 90.2 percent baseline.
- Use [tests/README.md](tests/README.md) to find behavior-owned focused suites;
  do not add new cases to the listed transitional catch-all files.
- Integration tests (`pytest -m integration`) require network access and are skipped by default.
- Keep PRs focused: one concern per PR.
- Keep the branch list clean: `main` is the only long-lived branch. PRs and
  feature branches are encouraged, but they stay short-lived and are deleted on
  merge (the repo auto-deletes merged PR branches); leave no stale local or
  remote branches behind, bot branches included.

### House style (all contributions: code, docs, comments, commits, PRs)

Applies to humans and AI coding agents alike.

- No generated-author markers: never add tool co-author trailers,
  generated-by labels, or assistant or vendor authorship mentions to commits
  or PRs. Re-author automated dependency changes before merging so commit
  history stays under the maintainer account.
- No em-dashes and no emojis, anywhere (this generalizes the catalog-description
  rule above). Use commas, colons, or parentheses.
- Professional, idiomatic code that matches the surrounding file's style and
  density. No AI slop: no comments that narrate the code, no defensive checks
  inside already-validated boundaries, no `try/except` that only re-raises, no
  single-use abstractions.
- Concise, direct prose in docs. State what is true; do not pad.

### Post-1.0 bar for code changes

From 1.0 onward, `docs/stability.md` defines the stable public surface.
Any change that touches a stable surface needs:

- A clear reason the change can't be done as data-only (YAML).
- An explanation of backward compatibility (or a deprecation plan if the
  change is breaking, which requires a major version bump).
- Tests covering both existing consumers and the new behavior.

The bar is deliberately high. Most "I want recon to do X" ideas can be
solved with a new fingerprint, signal, or profile rather than new code.

---

## CPT-change discipline (v1.9.6+)

The v1.9 Bayesian layer (`src/recon_tool/data/bayesian_network.yaml`) is a
**data file with semantic content**, not a free parameter surface to
tune against the corpus. Every CPT entry encodes a claim about how
evidence should move the posterior. Changing a number changes a
claim.

The discipline is one rule: **corpus runs are mirrors, not fitters.**
When the corpus disagrees with the network, the first question is
*is this node asking the right question?*, not *what number gets
the disagreement number down?* Only after the topology is clean do
CPT numbers get re-examined, and only with explicit reasoning
written in the YAML alongside the change.

The deep-dive reference, with worked examples (v1.9.3 topology
surgery on `email_security_strong`, v1.9.6 binding removal on
`email_security_policy_enforcing`), the anti-pattern catalog, and
the concept-comment requirement, lives at
[`docs/bayesian-cpt-discipline.md`](docs/bayesian-cpt-discipline.md).
Read it before changing any CPT entry.

---

## Bug reports and ideas

Three issue templates:

- **Fingerprint request**: you want recon to detect a service it
  currently misses.
- **Bug report**: recon got something wrong, crashed, or behaved
  unexpectedly.
- **Idea**: you want to propose something larger (new flag, new MCP
  tool, new CLI command, etc.).

Bug and fingerprint requests are structured public forms. Both require a
privacy acknowledgement. Fingerprint requests may name the provider or product
being classified and link its public documentation, but may not name customers
or evaluated targets, quote their records, or include per-domain output. If a
real target identity is essential to a non-security bug, use the private path in
the data-handling policy instead of GitHub issues.

For ideas, the template asks you to confirm the proposal fits the
project invariants (passive, zero-creds, no aggregated DB, no active
scanning). Ideas that don't fit will be politely closed with a pointer
to `--json` + pipe to the right tool.

---

## Pull request etiquette

See [Help improve and review recon](#help-improve-and-review-recon) for starting
points and ongoing review opportunities. The maintainer reviews external pull
requests against their evidence and verification.

- Keep PRs focused: one feature or fix per PR.
- Fingerprint-only PRs are welcome and easy to review.
- Include a brief description of what you changed and why.
- Reference the issue number if there is one. Use `Closes #N` only when every
  acceptance criterion is met, and use `Supports #N` for partial work. Post the
  issue closeout comment described in
  [AGENTS.md](AGENTS.md#working-in-this-repository) before merging.
- Be patient: this is a small project with a single maintainer.
