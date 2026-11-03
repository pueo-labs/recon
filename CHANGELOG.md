# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This file records what shipped. What is planned, why it is ordered that way,
and what is deliberately blocked live in [ROADMAP.md](ROADMAP.md) and
[docs/roadmap.md](docs/roadmap.md). Which surfaces are stable and how they may
change is [docs/stability.md](docs/stability.md).

`Unreleased` holds merged work that has not been published to PyPI. It is
routinely empty: the release policy batches coherent changes rather than
cutting one version per merged pull request, and documentation or planning
changes do not by themselves trigger a package release. Every released section
carries a `Tool Surface Changes` line so skill and agent authors can scan
command and flag changes without diffing help output.

Historical release entries preserve the terminology used when those versions
shipped and are not the current semantic contract. Older verification-token
language is superseded by exact administrative-token reuse, and older
cryptographic or provable tenant language is superseded by provider-attested
tenant-ID co-tenancy. Neither observation establishes a shared account
operator, corporate group, ownership, or control.

## [Unreleased]

## [2.27.1] - 2026-11-03

Correct the validation price table, and publish the catalog date passes,
the development toolchain refresh, and the pueo-labs repository metadata.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Changed

- Correct the agentic UX validation price table checked on 2026-11-03.
  Claude Opus 4.7 is $5 / $25 per million tokens. The cheap-tier examples
  are `gpt-6-luna` and `gemini-3.5-flash-lite`. `grok-4` and `grok-4-mini`
  are replaced by `grok-4.3` at $1.25 / $2.50. `grok-4.7` and `grok-4.3`
  use their published rate for the whole request once the prompt reaches
  200,000 tokens, and `claude-haiku-5-5` does the same above 100,000
  tokens. `gemini-3.8-flash` moves from $0.75 / $3.75 to $1.50 / $7.50
  on 2027-01-01. Each row records the provider page and the date it was
  checked. A row whose recorded shutdown date has arrived fails the
  test. Token counts still come from the provider response. Caching,
  batch discounts, and regional premiums stay outside the estimate. A
  one-sided `--input-price` / `--output-price` pair is rejected instead
  of being mixed with the table. (#352)
- Skip the Omarchy Bash syntax check when the `bash` on `PATH` cannot
  execute. On Windows that command can be the WSL launcher, which exits
  before it parses a script when its distribution disk is missing. A
  working Bash still parses `install.sh`, `uninstall.sh`, and
  `lifecycle.sh`.
- Refresh the locked development toolchain and the hash-locked Hatchling
  1.33.0 build root. The development lock moves to pytest 9.2.0,
  pytest-asyncio 1.4.1, hypothesis 6.170.13, ruff 0.17.3, and virtualenv
  21.15.1. Workflow pins move to setup-uv v10.3.3, setup-python v7.1.0,
  and codeql-action v4.39.1. The PLR size ratchet reads Ruff's OSC 8 rule
  hyperlinks, so those ceilings stay enforced. No runtime dependency or
  command changes.
- Update current repository links, installer download instructions, package
  metadata, plugin marketplace, schemas, and release tooling for
  `pueo-labs/recon`. Publish `io.github.pueo-labs/recon` and its matching PyPI
  README marker with this package. Keep the `recon-tool` package identity,
  existing release versions, and historical provenance unchanged.
- Date the Anthropic and Mistral apex domain-verification TXT rules from
  the current vendor pages, and point each rule at that page. The Anthropic
  record is documented for Team, Enterprise, and Console SSO setup. The
  Mistral record is documented as a precondition for email-domain
  authentication and enterprise access features. Neither record proves that
  SSO is enforced or that a product is in active use. Six other undated AI
  rules stay undated because their cited pages do not print the exact
  grammar.
- Date the Emma account-validation TXT and the Eloqua tracking-domain
  CNAME from the current vendor pages, and point each rule at that page.
  The Emma record is an apex TXT whose value begins with
  `e2ma-verification=` and an account-specific hash. It does not prove
  sending is active. The Eloqua record observes a CNAME whose target is
  under `eloqua.com`, documented as pointing at `s[SiteID].t.eloqua.com`.
  It does not prove landing pages, forms, or active campaigns. Six other
  undated CRM rules in this pass stay undated because their cited pages
  do not print the exact grammar.
- Date the Klaviyo branded-sending TXT, the Kartra custom-domain CNAME,
  and the Iterable tracking-domain CNAME from the current vendor pages,
  and point each rule at that page. The Klaviyo record is an apex TXT
  whose value begins with `klaviyo-site-verification=` and a public API
  key placeholder. It does not prove NS delegation, static DKIM CNAMEs,
  SMS, or that sending is active. The Kartra record observes a CNAME
  whose target is under `kartra.com`, documented as `username.kartra.com`.
  It does not prove pages, funnels, checkout, or memberships. The Iterable
  record observes a CNAME whose target is under `iterable.com`, documented
  as `links.iterable.com` or `links.eu.iterable.com`. It does not prove
  email, SMS, RCS, or WhatsApp sends are active. Five other undated
  marketing rules in this pass stay undated because their cited pages do
  not print the exact grammar.
- Date the Account Engagement tracker-domain CNAME and the Salesforce
  application SPF include from the current vendor pages, and point each
  rule at that page. The Pardot record observes a CNAME whose target is
  under `pardot.com`, documented as pointing at `go.pardot.com`. It does
  not prove landing pages, campaigns, or first-party tracking. The
  Salesforce record observes `include:_spf.salesforce.com`. It does not
  prove messages are being sent. Six other undated rules in this pass
  stay undated because their cited pages do not print the exact grammar.
- Date the Yandex Webmaster rights-verification TXT from the current
  vendor page, and point the rule at that page. The record observes a
  TXT value of `yandex-verification:` followed by a confirmation code.
  It does not prove that rights were confirmed, and it does not identify
  Yandex Direct, Metrica, or Connect. Seven other undated rules in this
  pass stay undated because their cited pages do not print the exact
  grammar.
- Date the MongoDB Atlas federated-authentication domain-mapping TXT
  from the current vendor page, and point the rule at that page. The
  record observes a TXT value of `mongodb-site-verification=` followed
  by a 32-character string. It does not prove that verification
  completed, that the domain is associated with an identity provider,
  or that a cluster exists. Seven other undated rules in this pass stay
  undated because their cited pages do not print the exact grammar.
- Date the Pendo organization CNAME and the Afternic parking
  nameservers from the current vendor pages, and point each rule at
  that page. The Pendo record observes a CNAME target under
  `pendo.io`. The guide's examples end in `-content.example.pendo.io`
  and `-data.customer.pendo.io`. It does not prove that guides are
  served, that events are collected, or that setup is complete. The
  Afternic record observes an NS host under `afternic.com`. The
  parking page names `ns1.afternic.com` and `ns2.afternic.com`. It
  does not establish a for-sale listing, parking revenue, or that the
  namespace is unused. Six other undated rules in this pass stay
  undated because their cited pages do not print the exact grammar.

## [2.27.0] - 2026-10-27

Add Codex and Gemini CLI install targets, MCP progress for long lookups,
display titles, a Claude Code marketplace, and MCP Registry metadata.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes. `recon mcp install --client`
and `recon doctor --client` accept `codex` and `gemini`.

### Added

- Publish MCP Registry metadata for `io.github.blisspixel/recon`. `server.json`
  is generated from the project version, and the README carries the PyPI
  `mcp-name` marker. The declared launch is `uvx --from recon-tool recon mcp`.
  The release job publishes that pointer with GitHub OIDC after PyPI parity.
  The artifact remains the attested wheel. (#321)
- Install recon for Codex and Gemini CLI. `recon mcp install --client=codex`
  writes `[mcp_servers.recon]` in `~/.codex/config.toml` or `.codex/config.toml`,
  preserving sibling tables and comments. `--force` replaces only that table's
  span. The install does not write `tool_timeout_sec` or
  `default_tools_approval_mode`. `recon mcp install --client=gemini` merges
  `mcpServers.recon` into `~/.gemini/settings.json` or `.gemini/settings.json`
  and omits `autoApprove`. `recon doctor --client` reads both files. (#323)
- Publish a repository Claude Code marketplace named `blisspixel-recon`.
  `claude plugin marketplace add blisspixel/recon` and
  `claude plugin install recon@blisspixel-recon` install the existing plugin,
  including its skills. The plugin still launches `recon` from PATH, so
  `recon-tool` remains a separate install. The marketplace file is generated
  from the plugin manifest and the project version. (#322)
- Advertise MCP display metadata. On mcp 2.0.0 and newer, `server/discover`
  and initialize `serverInfo` carry title `recon`, the package description,
  and `websiteUrl` `https://github.com/blisspixel/recon`. Every tool, catalog
  resource, and the `domain_report` prompt has a verb-first title. Names are
  unchanged, and recon publishes no icon. The v1.28.1 rollback pin forwards
  `websiteUrl` and those component titles. (#320)
- Send MCP `notifications/progress` from `chain_lookup`, a cache-miss
  `lookup_tenant`, `build_review_bundle`, `cluster_verification_tokens`, and
  `compare_postures`. Messages are stage names and counts. A client that
  resets its tool timeout on progress, or raises that timeout, can keep a
  depth 2 or 3 chain lookup alive. (#317)

### Fixed

- Ignore a `RECON_CONFIG_DIR` that is relative or still contains an unexpanded
  `${...}` placeholder. Cursor and VS Code leave `${PLUGIN_DATA}` literal, and
  recon was writing cache and limiter state into that directory in the working
  directory. `recon doctor` and `recon doctor --mcp` warn and name the
  placeholder. An absolute path is unchanged. (#318)
- Advertise only MCP change notifications recon sends. On mcp 2.3.0 and newer,
  `server/discover` leaves `listChanged` and `resources.subscribe` false, and
  `recon mcp doctor` fails if a later SDK default turns them back on. Older v2
  SDKs still advertise the flags, so the same check warns and the 2.0.0
  compatibility floor stays in place. (#319)

## [2.26.1] - 2026-10-26

Fix routine MCP request logging privacy, reject invalid encrypted DNS views,
and correct collection status, capsule determinism, and validation packaging.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes. Maintainer validation
helpers add provider selection and endpoint overrides.

### Security

- Suppress MCP server request-level logging by default (runtime level WARNING)
  to protect investigated domains from leaking into client log files. Full
  request logging is opt-in via `RECON_MCP_LOG_REQUESTS=1`. Preserve root
  logging configuration during MCP SDK construction.
- Reject typos and invalid values in RECON_DNS_VIEW on CLI lookups with exit
  code 2, preventing quiet fallback to unencrypted host DNS when an operator
  intended encrypted resolution.

### Fixed

- Prevent offline lookups from exiting 0 when old certificate summaries without
  subdomains exist in cache: when all live DNS queries fail and no services are
  observed, a cached certificate summary without subdomains no longer recovers
  the DNS source, correctly exiting 4 (all_sources_failed). (#312)
- Disentangle certificate transparency status on domains with no certificates:
  soft-empty provider responses without recovered certificates or cache are no
  longer recorded as ct_provider_used, eliminating contradictory degraded and
  recovered status messages. (#313)
- Canonicalize lexical observation example order: sort matching subdomain
  labels alphabetically before choosing examples so identical subdomain
  collections yield deterministic statements and zero false interpretation
  changes during capsule comparisons. (#311)
- Include all tracked validation modules in source distributions: allowlist
  validation/run_path_safety.py, validation/evaluate_catalog_promotions.py,
  and four tracked validation notes in .gitignore so VCS-aware sdist builds
  package all files needed by tests. (#314)

### Changed

- Refresh validation model helpers: default to current claude-sonnet-5-5,
  update pricing table and documentation examples with current model identifiers,
  and flag unknown model pricing instead of reporting a misleading $0.00. (#315)
- Support OpenRouter, Google Gemini, and local models (Ollama, vLLM, LM Studio)
  alongside Anthropic, OpenAI, and xAI in validation/agentic_ux and
  validation/triage_llm.py. (#316)

## [2.26.0] - 2026-10-25

Add an opt-in encrypted DNS view for CLI lookups and refresh DNS security,
failure diagnostics, and verification tooling.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Added

- Opt the `recon` CLI in to encrypted DNS with `RECON_DNS_VIEW=caller-safe`.
  Lookups then use the same view as the MCP server (saved `RECON_DNS_*`
  settings, else a recognized host public resolver, else Cloudflare
  DNS-over-HTTPS) and record `resolution_vantage: caller-safe`. The default is
  unchanged: without the exact opt-in value the CLI keeps the system resolver.
  With the opt-in set, invalid settings exit with code 2 before any collection
  (lookup, review, batch, discover, capsule capture and chain) and never fall
  back to the system resolver; total failure names a possibly blocked
  encrypted resolver. Links in these messages wrap only at word boundaries.

### Security

- Require dnspython 2.9.0, which fixes CVE-2026-114605 (GHSA-45c3-73f7-pv4m):
  a crafted DNS message could make name decompression consume excessive CPU.
  recon parses DNS answers controlled by the owner of any queried domain, and
  MCP parses DNS-over-HTTPS responses by default since v2.25.0. Refresh the
  runtime dependency set, including a current Public Suffix List snapshot for
  apex reduction, certifi 2026.10.23 and cryptography 50.0.2.

### Fixed

- When every source fails or times out under the caller-safe MCP DNS view,
  say that a network blocking outbound encrypted DNS is one possible cause and
  link the resolver override, instead of only "Try again". Since v2.25.0 a
  DoH-blocking network reached this generic failure rather than a setup
  message. The hint names no resolver and is absent for the operator and
  disabled views.

### Tests

- Warm the synthetic MCP launch installation before its timed handshakes:
  precompile the copied package and import the server once, untimed. The MCP
  SDK bounds `server/discover` at a fixed 10 seconds, and the first launch of a
  fresh install on a loaded Windows runner had spent that budget on one-time
  bytecode compilation and first-run interpreter cost (issue 303).
- Refresh development and mutation tooling, including ruff 0.17.2 (no code
  changes needed), Hypothesis 6.170.9, coverage 7.17.0 and cosmic-ray 8.7.0,
  and regenerate the build constraints. Hypothesis's improved annotations
  repaired five legacy test typing diagnostics, so the exception inventory is
  narrowed: one stateful test drops its file-level control and another keeps
  only its private-contract exception.

### Documentation

- Run the local draft-release verifier through the project environment in the
  release runbook; a bare system `python3` can lack its dependencies.

## [2.25.0] - 2026-10-25

Make MCP DNS collection work without setup, over encrypted DNS by default.

### Changed

- MCP DNS collection now works without setup on hosts whose resolver is not
  Cloudflare or Google. Instead of reporting an unavailable capability, the
  server binds encrypted Cloudflare DNS-over-HTTPS (`cloudflare-dns.com` via
  `1.1.1.1` and `1.0.0.1`). Saved `RECON_DNS_*` settings and a recognized public
  service in host configuration still take precedence, the host's enterprise or
  stub resolver is still never used, and failures still never fall back.
  `RECON_DNS_VIEW=none` disables DNS-dependent MCP tools; partial or invalid
  settings stay unavailable rather than silently using the default. Trusted CLI
  resolution is unchanged.

### Documentation

- Renumber the duplicate MCP DNS-view ADR to ADR-0019, record the encrypted
  default as an amendment, and list it in the ADR index. Mark closed issues in
  dated review records and note the live Best Practices result in the badge
  worksheet.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes. No MCP tool, resource or
prompt name changes. The MCP DNS capability declaration keeps its fields; its
unavailable setup text now points at fixing or removing `RECON_DNS_*` settings.

## [2.24.0] - 2026-10-24

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Added

- Recognize Vercel's documented nonempty verification marker at `_vercel`.
  Invite contributors interested in catalog validation, independent review,
  and a possible future maintainer role through the contribution guide.

### Fixed

- Exclude mail controls made inapplicable by retained Null MX declarations
  from hardening prompts, review candidates, and index allocation. Require
  explicit deny-all SPF and effective DMARC enforcement before excluding
  sender controls, retain declaration proof, and preserve applicability in
  hypothetical simulations.
- Adapt boxed gap, exposure, and delta reports to up to 100 columns with
  hanging continuation indents and whole identifiers. Keep the ASCII help
  example visible and link sparse-result guidance for installed users.
- Report the checked MCP server's DNS capability in both doctors with an
  actionable warning when no caller-safe view is approved. Refuse unavailable
  collection before reserving rate limits, and advertise and enforce the
  chain-depth range without silently changing caller requests.
- Canonicalize merged evidence before interpretation so shuffled DNS answers
  do not create false capsule changes. Preserve literal `www` hosts with
  `--exact`, retain balanced CAA record quotes, and normalize CT issuer display
  labels across provider and cache paths. Record normalizer version 2 while
  keeping historical capsule artifacts intact.
- Label caches bound to another DNS policy as non-reusable metadata rather
  than inspection failures, while keeping their payloads inaccessible to the
  current view. Reject empty CT metadata as an offline recovery contribution
  so fully failed lookup and review workflows exit 4.
- Share CNAME DNS-label and regex matching between fresh detection and cached
  replay so cached records cannot gain a provider claim from a lookalike.
  Narrow Fly.io, Railway, and Netlify targets to their documented routing
  boundaries, date ten reviewed rules, and distinguish routing and published
  verification markers from completed verification or active deployments.

## [2.23.0] - 2026-10-23

### Added

- Publish a harness-neutral catalog maintenance entry point with a runnable
  fictional offline round, private frozen inputs and budgets, durable start
  receipts, one-use holdout accounting and resumable monthly reference reviews.
  Keep review dates genuine and proposal queues bounded; no recurring job,
  customer collection or automatic promotion is activated.
- Add documented Convex custom-domain routing, ImprovMX and Forward Email MX
  routing and SPF policy references, plus Forward Email's nonempty verification
  marker. Preserve record roles, related-host scope and existing suffix grammar;
  no additional probes or active-use claims.

### Fixed

- Bound supplied maintenance evaluation files, aggregate bytes, directory work,
  JSON nesting and record counts before reduction or holdout consumption. Hash
  and decode the same admitted bytes and reject incomplete malformed inputs.
- Refresh development-only filelock and virtualenv security floors and locks
  for SQLite side-file handling, shell prompts and exclusive file creation.

- Replace global and suite-wide typing relaxations with exact owned scopes and
  a blocking audit that restores their diagnostics. Check JSON containers and
  OIDC endpoint values, type rate-limit snapshots and shared fixtures, and
  repair canonical test imports without changing ordinary lookup commands.

- Gate cross-slug catalog overlaps with shared synthetic witnesses and reviewed
  retained provenance, including equal patterns and differently written
  regexes. Require exact review dispositions for rule additions, retirements
  and claim/provenance edits while keeping source-check dates distinct from
  editorial changes.

- Characterize shared-response identity deductions and distinguish individual
  model-unit masks from complete source withdrawal. Preserve separately
  supported roles, conflicts and missing observations in offline regression
  cases; clarify explanation limits without changing inference parameters.

- Require current role-observation bindings and effective evidence before
  Bayesian assurance assertions. Repair vacuous grouping, sensitivity and
  conflict-band scenarios, retain generic-vendor negatives, and record a
  reproducible finite sensitivity receipt without changing model parameters.

- Bound batch tenant/name peer projection, token expansion and indexed
  ecosystem pair work independently of qualifying results. Preserve small
  groups and existing JSON array/wrapper shapes, and add explicit diagnostics
  for unavailable comparisons, filtering, truncation and unfinished search.

- Keep unrecorded historical delta sets distinct from explicitly empty arrays.
  Withhold unsupported service, slug and signal changes and report missing
  confidence/domain-count comparisons in the existing incomplete diagnostic.

- Match built-in CNAME motif provider domains at validated DNS-label boundaries
  so deceptive prefixes and appended domains cannot create provider-chain
  observations. Preserve ordered matching, queried-host provenance and legacy
  custom substring markers; custom domain markers can select `dns_suffix`.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes. Batch JSON adds optional
correlation completeness diagnostics; existing array/wrapper shapes remain.
No MCP tool, resource or prompt names change. Private catalog maintenance
helpers require a source checkout and do not change ordinary lookup setup.

## [2.22.0] - 2026-10-22

Protect lower-trust collection on split-horizon networks and finish the build-tool CA remediation.

### Security

- Isolate lower-trust MCP collection from the host's split-horizon DNS view.
  Bind DNS and HTTP name resolution to one saved caller-safe startup policy,
  preserve TLS and public-address socket admission, and bind caches to its
  identity/version. Reuse an approved configured public resolver without a new
  chooser; report unavailable capability with one-time server setup guidance
  when approval is missing. Bare CLI lookups keep their existing UX and trusted
  resolver view. Reconcile audit triage by revision and attack path, and correct
  the HTTP pinning fix's release status to v2.19.0.
- Complete the build and publishing toolchain's emSign CA remediation, separate
  from the shipped runtime certifi fix. Select uv 0.13.5 in CI, releases,
  installer bootstraps, local readiness and the digest-pinned container; require
  uv >=0.13.4 for lock updates. Pin PyPI publishing to the verified v1.14.3
  commit with patched sigstore and certifi, preserving trusted publishing and
  artifact provenance gates. Existing tool installations, interpreters, virtual
  environments and custom trust stores require their own update and review.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

## [2.21.6] - 2026-10-22

Correct offline artifact boundaries and refresh the security and Python baseline.

### Fixed

- Exclude unattempted sources from capsule and review-bundle observation
  opportunities. A disabled opt-in probe no longer claims an empty observation
  or changes the state or instance count of an attempted source role.
- Reject artifact timestamps whose conversion to UTC exceeds the supported
  datetime range as validation errors instead of raising an uncaught overflow.

### Security

- Require OpenTelemetry API 1.45.1 or later for the MCP trace-metadata parser
  (CVE-2026-114603). Carry the floor into installed distribution metadata.
- Refresh the development and mutation toolchain to virtualenv 21.14.12,
  GitPython 3.2.1 and pip 26.2.2, including their security and bundled CA fixes.

### Changed

- Use Python 3.15.1 as the exact local patch baseline. Keep uv aligned with
  setup-python's selected interpreter throughout CI, including future patch
  updates and the existing supported-version matrix.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

## [2.21.5] - 2026-10-21

Preserve CLI option values that happen to spell global flags.

### Fixed

- Keep flag-shaped filenames and labels as option values instead of moving
  them into global options or rejecting them as misplaced flags. Follow the
  registered command's option arity, including nested aliases, short-option
  combinations and attached values. A later `--help` stays a help request and
  does not accidentally become a value that allows collection to start.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

## [2.21.4] - 2026-10-20

Refresh the tested MCP SDK baseline and correct CT maintenance summaries.

### Fixed

- Read CT limiter snapshots in maintenance summaries from the runtime's shared
  state-directory resolver, including fresh XDG installations. Preserve legacy
  and explicit override precedence and clarify that persisted counters can
  include earlier runs. This changes validation tooling, not packaged lookups.

### Changed

- Refresh the production lock and blocking current-SDK compatibility row to
  MCP 2.3.0 and its matching types. Keep the 1.28.1 rollback and 2.0.0 floor
  rows, the existing supported dependency range, and the passive collection
  boundary. The SDK update includes stdio event-loop and legacy framing fixes.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

## [2.21.3] - 2026-10-20

Refresh the default CA bundle after an upstream security advisory and complete
the source-verifiable repository assurance evidence. Close four bounded-input
and filesystem gaps found in a fresh source review.

### Security

- Require `certifi>=2026.10.19` in runtime package metadata and refresh the
  locked CA bundle and fuzzing export for `PYSEC-2026-4320`
  (`GHSA-6q48-6c7w-9gw2`). The default HTTPX trust store no longer includes the
  distrusted emSign ECC root. Custom trust stores and operator-managed remote
  TLS ingress remain outside this bundle update; rebuild existing containers.
- Bind implicit workspace MCP configuration reads and atomic writes to retained
  directories. POSIX uses directory-relative operations; Windows rejects
  reparse points and retains ancestor locks and temporary guard entries.
  Explicit user-selected configuration symlinks remain supported.
- Render observed and diagnostic text literally in the Omarchy panel and
  settings so provider-controlled markup cannot trigger Qt image loading.
- Bound numeric regex repetition counts before compilation and specificity
  matching, including repeated zero-width assertions submitted over local MCP.
- Index capsule/cache insight and evidence references once during admission,
  preventing quadratic tuple scans while preserving exact evidence identity,
  order and duplicate occurrences.

### Documentation

- Document the enabled private HTTPS vulnerability-reporting channel and refine
  the OpenSSF questionnaire evidence, including the optional remote adapter's
  authentication boundary, dated maintainer knowledge attestations and checked
  public issue/security-review history. Response-history gaps remain explicit.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

## [2.21.2] - 2026-10-20

Adopt the current GA toolchain, strengthen repository assurance checks, and
refresh the public terminal example.

### Changed

- Adopt Node 26 GA in the typecheck and release jobs, resolving the current
  stable patch rather than waiting for the LTS designation (#240). Python
  3.15.0 remains the development and release default; 3.11 through 3.15 stay
  supported.
- Refresh the README terminal illustration with the production source-health
  summary and corrected source identifiers. The image and accessible transcript
  are generated together from the same synthetic fixture.
- Require stale-approval dismissal, resolved review threads and no bypass actors
  in release readiness, matching strengthened live repository controls. Raise
  the SAST regression floor from 7 to 10 after the public sample reaches 10.
- Prepare evidence-backed OpenSSF questionnaire proposals and clarify the
  external contribution path. Independent review and account-backed badge
  registration remain separate requirements.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

## [2.21.1] - 2026-10-20

Fix Linux interface regressions found during real-terminal and desktop
qualification of the v2.21 follow-ups.

### Fixed

- Stop redrawing the source ladder after every source settles. The final frame
  waits without polling until collection returns, avoiding idle CPU use (#239).
- Qualify Omarchy's palette and font singletons through an explicit QML import
  namespace so Qt's `Color` type cannot shadow the host palette. Bind domain
  input selection to the live accent and contrasting foreground (#238).

### Validation

- Qualify source-ladder rendering in Foot and the native panel in Quickshell on
  a running Linux desktop, including light/dark colors, live theme changes,
  idle CPU and stdout parity. See the
  [qualification evidence](docs/interface-qualification-2026-10-20.md).

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

## [2.21.0] - 2026-10-19

Report collection truth when every source fails or a name does not exist, stop
reusing degraded cache entries, start the generated MCP launcher from any
working directory, adopt Python 3.15 as the default toolchain, and bring the
interface up to the retro-but-modern rules: theme color roles, an ASCII
fallback, a source ladder, narrow-terminal layout, caveat parity and one
doctor vocabulary with JSON output.

### Added

- `--ascii` (also automatic under `TERM=dumb` and on terminals that cannot
  encode the glyphs) prints pure ASCII: `[##-]`, `ok - x`, `H M L` and a `-`
  divider, instead of substituting `?` (#226).
- `recon doctor --json` and `recon doctor --client=<name> --json` emit the
  same checks as the human view as one JSON object on stdout with the same
  exit code (#230).
- `recon doctor` names a resolver that answers names that should not exist,
  using one doctor-only query for a reserved `.invalid` name (#230).
- `RECON_NO_ANIMATION` turns off the animated source ladder (#227).

### Changed

- Python 3.15 is supported and is the default toolchain. CI tests 3.11
  through 3.15 on Linux, macOS and Windows plus a non-blocking free-threaded
  3.15t probe; single-version and release jobs run on 3.15; the draft container
  uses `python:3.15.0-slim-trixie` pinned by digest. Install helpers prefer
  Python 3.15, and `recon doctor` treats 3.11 through 3.15 as the tested range
  (#225).
- CI moves to Node 24 LTS and current action releases (checkout v7,
  setup-python v7, setup-node v7, setup-uv v10, codeql-action v4.39.0,
  scorecard-action v2.5.0). Locked dependencies were refreshed to releases with
  3.15 wheels, and pip-api 0.0.35 restores pip-audit on 3.15 (#225).
- `recon mcp doctor` labels its isolated empty-directory check and adds a
  generated-launch check that runs the installer's exact command, arguments,
  and environment from the current directory or `--launch-cwd`, naming the
  launch it exercised (#220).
- A near-miss command typo followed by more arguments (`recon lookpu
  example.com`) now reports `Unknown command "lookpu". Did you mean "lookup"?`
  with exit 2 (#229).
- Colors come from one role table on the terminal's 16 named colors (accent
  cyan, success green, warning yellow, error red, info blue, muted dim), so a
  theme switch recolors recon. Role color marks state on markers while the
  state word stays in the default foreground; contrast is measured on dark and
  light Omarchy palettes. Low confidence uses the warning color (#226).
- Color precedence is `--color`/`--no-color` > `NO_COLOR` > `TERM=dumb` >
  `FORCE_COLOR` > TTY. `--no-color` removes every escape sequence on stdout
  and stderr, and `FORCE_COLOR=0` no longer forces color (#226).
- Collection progress is a source ladder on stderr: one row per source family
  that settles to matched, no match or unavailable, then collapses into one
  source-health line such as `6 sources: 4 matched, 2 no match`. Animation is
  synchronized, capped at 12 frames per second, and off under `--no-color`,
  `NO_COLOR`, `TERM=dumb`, `CI`, `RECON_NO_ANIMATION`, `--debug` and
  non-terminal stderr (#227).
- Collector warnings no longer print raw between spinner frames. Lookup,
  chain, batch and review print one deduplicated stderr summary such as `2
  hosts could not be resolved (...). Run recon doctor.` A DNS failure reads
  `could not resolve` rather than an SSRF refusal; a refused private
  destination reads `skipped: resolves to a private address`. The collection
  note counts unavailable sources instead of saying "Some" (#227).
- Below 78 columns the lookup panel is laid out once at the real console
  width, so text no longer wraps twice. UUIDs, hostnames, URLs and email
  addresses never break across lines, key-fact values share one column, and
  bordered panels render flat when an 80-column box does not fit. Wide output
  keeps its layout (#228).
- Display names are marked `(unverified)` on the panel, `--plain`, `--md` and
  MCP text, and lookup JSON adds `display_name_verified: false`. A reserved
  special-use name prints `Reserved name: results are public residue, not an
  organization.` on every human surface and adds the conditional JSON field
  `reserved_name: true`. Unavailable values print `n/a`, and output text uses
  a colon for label and value with no em dashes (#229).
- Absence signal names now separate the signal from `Missing Counterparts`
  with a colon (`<signal>: Missing Counterparts`) instead of a spaced em dash.
  Automation that matches the old name string should match the new separator
  (#229).
- `recon doctor`, `--mcp`, `--client` and `recon mcp doctor` share one status
  vocabulary: `ok`, `warn`, `fail`, `info`. A failing run ends with a red
  summary that counts failures and names a `Next:` step; DNS failures are
  explained in plain language (#230).
- The Omarchy panel colors success, warning, error and info from the active
  theme's green, yellow, red and blue, read at open and on theme change, so a
  warning no longer looks like a failure and Medium confidence shows as info.
  The standalone preview gains a light fallback set (#231).

### Fixed

- A lookup or review where every DNS query fails and every identity endpoint
  fails now reports `all_sources_failed` and exits 4 instead of an empty
  success. The disabled CSE probe no longer counts as a clean source. Empty and
  mixed DNS results remain partial lookups (#221).
- An NXDOMAIN for the queried name is now stated on the panel, `--plain`,
  `--md`, and MCP text, carried as the additive JSON field `dns_name_status`,
  and no longer narrated as a parked or web-only domain (#222).
- A lookup whose collection had unavailable sources is no longer reused from
  the result cache, so the next default lookup after a network recovery
  collects again, including for entries saved by earlier releases. `recon cache
  show` reports the same reuse decision as the lookup, and human output served
  from the cache says so in one muted line. `--no-cache` remains a read and
  write bypass; lookup JSON is unchanged (#223).
- The MCP launcher written by `recon mcp install`, and `recon mcp`, no longer
  refuse to start when the client's working directory is the home directory or
  a filesystem root. The startup guard now refuses only a `recon_tool` package
  imported through the working directory, with a bounded, actionable message
  (#220).
- `--color` and `--no-color` now work after the domain or command, matching
  the leading form; the last one given wins. A trailing `--debug`, `-V`, or
  `--version` explains that it is a global option (#224).

### Security

- Bump the locked mutation-testing dependency aiohttp from 3.14.3 to 3.14.5 for
  CVE-2026-111063, CVE-2026-111064 and GHSA-2g87-pp6c-29x5. aiohttp is not a
  runtime dependency of the published package.

### Tool Surface Changes

- Tool surface changes: added flags `--ascii` to `recon`, `--json` to
  `recon doctor`, `--launch-cwd` to `recon mcp doctor`.

## [2.20.1] - 2026-10-11

Keep valid home-managed updates available and preserve installed launcher dispatch.

### Fixed

- Keep home-managed uv and pipx updates available from home, nested and
  unrelated directories; preserve symlink shim dispatch for ownership queries
  and upgrade commands while retaining project-launcher refusal.

### Tool Surface Changes

- Tool surface changes: no CLI command or flag changes.

## [2.20.0] - 2026-10-11

Make installation and update recovery reliable, preserve accessible prose and
partial-comparison limits, and replace the Omarchy bar widget with an on-demand
native desktop panel.

### Changed

- Replace the Omarchy bar widget with plugin 2.0.0, an on-demand native-themed
  panel with canonical inline settings, explicit baseline recording, Copy JSON
  and terminal handoff. Installation verifies enablement without restarting the
  shell; legacy bar placements require an explicit settings export and migration.

### Fixed

- Keep GitHub Release creation and asset uploads under the human maintainer;
  verify the original run's complete sealed artifacts, authorship, provenance
  and PyPI parity in a read-only final job with an explicit recovery handoff.

- Bound Omarchy setup IPC and verify asynchronous registry removal; accept
  canonical lookup JSON so successful CLI reports render in the panel.
- Verify PATH launchers through their lexical entry so symlink shims dispatch
  correctly, and stop home-directory ancestry from hiding user-level installs.
- Announce installer ownership checks and retry a busy uv tool lock once;
  explicitly select supported stable Python for new pipx installs, retain valid
  existing pipx interpreters, and explain interpreter and PATH recovery.
- Preserve Python admission arguments under Windows PowerShell's legacy native
  forwarding, and use native environment paths and PATH separators when running
  the PowerShell helper on Unix.
- Preserve complete insight sentences, uncertainty hedges and guidance in
  `--plain` and `--plain --full`; visibly mark bounded display values while
  retaining shared control-character sanitization.
- Show incomplete Omarchy baseline comparisons with an amber partial badge,
  degraded sources and fields not compared, while retaining comparable changes
  and marking suppressed service lists explicitly.

### Tool Surface Changes

- Tool surface changes: no CLI command or flag changes.
- No lookup schema fields or MCP tool signatures changed. The independently
  versioned Omarchy plugin 2.0.0 replaces the bar-widget integration with an
  on-demand panel and explicit settings, baseline, clipboard and terminal actions.

## [2.19.15] - 2026-10-09

Add thin Omarchy desktop shell integration, support `CLAUDE_CONFIG_DIR` for profile isolation
and account switching, and document Arch Linux and Omarchy environments.

### Added

- Add thin, keyboard-first Omarchy desktop shell integration in `integrations/omarchy/`
  with asynchronous QML execution, direct argument passing, clipboard safety,
  fail-closed timeout bounding, and baseline drift inspection.
- Support `CLAUDE_CONFIG_DIR` when resolving user-scoped Claude Code configuration
  paths in `recon mcp install` and `recon doctor --client=claude-code`, enabling
  profile isolation and automatic compatibility with Omarchy account switching.
- Add Linux and Omarchy environment documentation in `docs/omarchy-and-linux.md`
  covering PEP 668 tool installation, agent launcher integration, terminal rendering
  in Hyprland, and unprivileged DNS resolution.

### Tool Surface Changes

- No CLI commands, flags, schema fields, or MCP tool signatures changed. Added `integrations/omarchy/` desktop bar widget and support for `CLAUDE_CONFIG_DIR` configuration resolution.

## [2.19.14] - 2026-10-09

Harden reverse DNS prefix parsing, enforce strict type guards across core validation
and MCP stdio tools, and bound injected ephemeral fingerprint rules.

### Security

- Fix positional network prefix evaluation in `_is_private_v4_reverse` to prevent private
  reverse DNS bypasses when host octets repeat `172` or `100`.
- Enforce runtime type validation in `validate_domain`, `is_safe_dns_name`, and
  `strip_control_chars` to return structured errors on non-string inputs.
- Enforce strict type validation and length limits on ephemeral fingerprint injection
  fields, detections, and regex patterns.
- Guard MCP tool parameters against invalid types, rejecting booleans and non-integers
  in pagination limits, `chain_lookup` depth, `get_signals` layer, and `explain_signal` name.
- Preflight destination path usability in batch discovery to fail fast on invalid output paths.

### Changed

- Refactor hypothesis matching and DAG explanation format validation to preserve complexity ratchets.

### Tool Surface Changes

- No commands, flags, MCP tools or schema fields changed. Strict runtime type contracts and bounds on core validation, reverse DNS parsing, and MCP tools are enforced.

## [2.19.13] - 2026-10-08

Harden local inputs, neutralize diagnostic and delta terminal controls, and bound
discovery, clustering, simulation and reverse DNS traversal.

### Security

- Neutralize control characters and enforce element and aggregate string bounds on
  compare-snapshot collection values in delta parsing and terminal rendering.
- Reject control sequences in fingerprint YAML names, enforce a 128-character limit,
  and sanitize diagnostics and quiet CI output paths.
- Enforce pre-validation bounds on raw domain counts, item lengths, and aggregate text
  in cluster_verification_tokens, and bound returned validation errors.
- Validate category query length and control characters before catalog search, and
  apply single-pass normalized category matching across MCP and CLI catalog tools.
- Enforce per-item and aggregate character bounds on hardening simulation fixes
  before resolution, and slice unrecognized fix text before sanitization.
- Constrain PTR canonical targets in safe_resolve, preserving RFC 2317 classless
  aliases while discarding chains crossing into private reverse DNS or internal namespaces.
- Harden launcher resolution against untrusted workspace symlinks and ancestor PATH
  executables across updater and doctor commands, rejecting relative and workspace-origin
  candidates before execution.
- Disallow symlinks in implicit workspace MCP client configuration paths and bind
  verified targets during atomic configuration writes.

### Changed

- Tighten complexity ratchet limits and refactor reverse DNS and configuration path
  precondition checks.

### Tool Surface Changes

- No commands, flags, MCP tools or schema fields changed. Input bounds on clustering,
  simulation, category discovery, delta comparisons and workspace MCP paths are enforced.

## [2.19.12] - 2026-10-08

Correct SPF and TXT observations, bound local MCP inputs, and refresh compatible
dependencies with synchronized reproducible build constraints.

### Changed

- Shortened the README around installation, common commands, and local agent
  setup. Detailed installer, research, and maintainer guidance lives in linked
  docs; documentation checks enforce those boundaries at their canonical homes.
- Refresh compatible runtime and development dependencies, optional validation
  SDK pins, and Hatchling 1.32.4 with synchronized hash-locked build constraints.
  Provider SDKs remain outside the runtime and default development groups.
- Reconcile completed roadmap tranches and record the remaining upstream pip
  vendored-transport blocker separately from local maintenance.

### Fixed

- Update failures print the complete recovery command separately from bounded
  error details, preserving long interpreter paths and literal markup characters.
- Withhold SPF policy control credit and stop redirect traversal when an owner
  publishes competing SPF records, including cached replay. Preserve raw TXT
  observations, vendor references and include counts. Invalidate older lookup
  caches that can retain incorrect policy evidence.
- Parse real TXT character-string bytes before protocol admission, preserving
  folding whitespace, quotes, backslashes and multi-string concatenation.

### Security

- Bound relative TXT fingerprint owners and retained ephemeral detection
  patterns, closing a local MCP resource-quota bypass.
- Reject non-regular MCP client configuration files before reading, including
  FIFO substitutions. Preserve regular-file symlinks, BOM and empty-file behavior.
- Require Typer 0.27.3 for its terminal-control escaping fix in CLI error messages.
- Exclude multidict before 6.9.1 from the optional mutation toolchain for
  CVE-2026-104874. It remains outside the runtime dependency graph.

### Tool Surface Changes

- Tool surface changes: no CLI command or flag changes.

## [2.19.11] - 2026-10-01

Correct public observation claims and CLI lifecycle handling. This release
also includes the BIMI and TLS-RPT declaration fixes prepared for v2.19.10,
which was not published.

### Fixed

- Display Adobe's domain-verification TXT marker as `Adobe Admin Console`
  under Business Apps, including retained results with the old display name.
  The token does not identify the organization's IdP or establish SSO or
  product use. Keep the `adobe-idp` slug for compatibility.
- Require a sole distinct `0 .` MX record for a Null MX no-mail declaration.
  Conflicting or malformed root targets no longer create that claim or hide
  ordinary unclassified mail routes. Raw records and valid provider evidence
  remain available.
- Honor `--timeout` for chain lookups, cap each resolution by the remaining
  aggregate budget, and retain completed results with explicit truncation.
- Validate capsule output paths and vantage labels before collection, using
  the same output preflight as review bundles and retaining write-time checks.
- Cancel and join batch workers when task creation fails during streaming
  startup. Both batch schedulers close rejected coroutines.
- Describe lookup-result versus CT caching accurately in help. Corpus help
  follows the configured location and identifies fallback files as live input
  without assuming that their contents are synthetic.
- Correct BIMI and TLS-RPT TXT admission for malformed, conflicting and
  declined records while preserving protocol extensions and the existing
  no-fetch boundary.

### Security

- Raise the development-only GitPython floor to 3.1.62 for the upstream
  submodule path-traversal fix, GHSA-59cr-6r3x-644w. It remains outside the
  runtime dependency graph. Refresh the pinned CodeQL actions to v4.38.2.

### Tool Surface Changes

- No commands, flags, MCP tools or schema fields changed. Existing chain
  timeout flags now take effect; the default per-domain timeout remains 120 seconds.

## [2.19.10] - 2026-09-30

Prepared but not published. These fixes are included in v2.19.11.

Correct BIMI and TLS-RPT declaration observations through the existing DNS
collection path. Compact output and network scope stay unchanged.

### Fixed

- Admit one eligible BIMI or TLS-RPT TXT record before creating service or
  control evidence. Reject version lookalikes, malformed required fields,
  conflicting records and explicit BIMI declination.
- Preserve protocol-specific whitespace and extension rules, including
  repeated TLS-RPT reporting fields. Share URI syntax validation with DMARC
  while keeping its legacy report-size handling separate.
- Extract opt-in BIMI certificate URLs from the same admitted, case-sensitive
  tags. Existing destination guards and the default no-fetch boundary remain
  in force. Record admission does not validate logos, certificates, message
  authentication, endpoint availability or successful report delivery.

### Tool Surface Changes

- No commands, flags, MCP tools or schema fields changed.

## [2.19.9] - 2026-09-30

Tighten DKIM TXT observations without expanding collection or changing the
compact output contract.

### Fixed

- Google and generic DKIM selectors use one bounded tag-list parser. Version
  lookalikes, misplaced version tags, duplicate tags, malformed key material,
  and missing or revoked `p=` values no longer create DKIM control claims.
- Recognize the specified omitted-version default and permitted whitespace.
  Preserve raw positive evidence, later valid selectors and existing CNAME
  delegation observations. This is record-shape admission, not cryptographic
  validation, message verification, or proof of active signing.

### Security

- Raise the development-only virtualenv floor to 21.14.1 and refresh its
  interpreter-discovery dependency. This removes PYSEC-2026-4011 through 4014
  from the locked pre-commit toolchain, including activation, configuration
  injection and downloaded seed-wheel verification fixes. Neither package is
  added to recon's runtime dependencies.

### Tool Surface Changes

Tool surface changes: no CLI command, flag or JSON schema changes.

## [2.19.8] - 2026-09-30

Correct SPF provider observations and bounded redirect handling without adding
collection or changing the compact default view.

### Fixed

- SPF detection requires the complete `v=spf1` version token. Lookalike
  prefixes such as `v=spf10` no longer produce provider or SPF policy claims.
- Provider matching excludes includes after `all` and redirects ignored
  because `all` is present.
  Original TXT records remain available as retained observations.
- Qualified includes remain observable policy references. Detailed service
  roles say "SPF policy reference" rather than claiming sender authorization;
  the default panel continues to show the compact service name.
- Redirect collection requires one exact `redirect=` modifier and applies the
  `all` rule at every hop. Embedded modifier text and repeated redirects no
  longer schedule unrelated DNS requests or inherit a downstream policy.
- SPF specificity is applied to each target independently. A narrow match no
  longer hides a separately listed provider with an overlapping catalog rule.
  Repeated targets still produce one occurrence per matching rule. Live
  collection and cache-only fingerprint replay share the same matching path.

### Tool Surface Changes

Tool surface changes: no CLI command, flag or JSON schema changes.
Detailed service labels and `connection_map` entry roles use "SPF policy
reference" for SPF observations.

### Security

- Raise the development-only urllib3 floor to 2.8.0 and refresh its locked
  artifacts, addressing CVE-2026-97687 and CVE-2026-97689 in the dependency
  audit toolchain. Apply the same floor to the isolated release SBOM tool.
  urllib3 remains outside the published runtime graph.
- Audit the complete frozen exports without launching pip's resolver, avoiding
  its separate vendored transport. CI, release audits and SBOM generation keep
  their existing coverage and fail-closed vulnerability checks.

## [2.19.7] - 2026-09-30

Harden updates and local fingerprint admission, correct agent-discovery
attribution, and keep current agent integrations focused on the requested work.

### Fixed

- `recon update` downloads a pip release before replacing the installation, on
  every platform. A failed download leaves the current files in place. macOS
  and Linux then run the package manager in the foreground. Windows copies an
  isolated worker out of the package, waits until every `recon.exe` has exited,
  retries a transient file lock, and checks that `recon-tool` imports. A failed
  upgrade prints a direct recovery command. The previous Windows failure text
  told the operator to run `recon update` again after the package could already
  have been removed.
- Every updater-managed pip command now suppresses implicit working-directory
  imports, including download, offline install and printed recovery commands.
  A workspace `pip.py` or `pip` package can no longer replace installed pip;
  user-site installs remain supported.
- Regex admission accounts for inline comments, scoped verbose mode and
  escaped comment terminators before checking repetition. Comment syntax can
  no longer hide the reviewed unsafe forms from catalog, specificity or
  process-local fingerprint-injection validation.
- AID detection recognizes current `aid2` and legacy `aid1` declarations and
  uses the vendor-neutral name. The historical `crewai-aid` slug stays stable.
  MCP DNS discovery is labeled as a community proposal. These markers no
  longer establish an AI-platform or autonomous-agent deployment claim.

### Changed

- Adopt stable MCP SDK 2.2.0 and companion types in the lock, retaining the
  existing dependency range and exact 1.28.1, 2.0.0 and 2.2.0 compatibility gates.
- Require PyJWT 2.14.0 or newer for the existing MCP dependency and lock current
  stable 2.15.1. This excludes the affected 2.13.0 release flagged by the
  September dependency audit; the floor also ships in wheel metadata so pip
  upgrades cannot retain it. See the [upstream security fixes](https://pyjwt.readthedocs.io/en/stable/changelog.html#v2-14-0).
- Refine shared development guidance and native/generated skills: concise
  one-off lookups, direct comparisons over supplied domains, relevant evidence
  and collection failures, and posture diagnostics only when requested. Current
  Agent Plugins schemas remain byte-identical to the vendored 1.0.0 copies;
  representative-client acceptance remains a separate uncompleted evaluation.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

## [2.19.6] - 2026-09-20

Close the optional-tooling audit gap identified during final release verification.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Fixed

- Require GitPython 3.1.60 or newer in the optional mutation-testing group to
  address PYSEC-2026-3982, PYSEC-2026-3983, and PYSEC-2026-3984. GitPython is not
  a dependency of the published CLI or MCP wheel.
- CI and release audits now cover every locked development group and extra as
  well as runtime dependencies. A workflow regression test enforces that scope;
  the release SBOM continues to describe the shipped runtime graph.

## [2.19.5] - 2026-09-20

Polish installation, updates, and diagnostics, with mathematical and graph
correctness fixes verified before publication.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Added

- One-command macOS/Linux and Windows installation in the README. The helpers
  bootstrap pinned `uv` and supported Python when needed, preserve an existing
  package-manager owner, configure PATH, and verify the installed version.
- `recon doctor` checks the latest installable release with a short PyPI timeout
  and suggests `recon update` when needed. An unavailable version check is a
  warning, and diagnostics never install updates automatically.

### Fixed

- `recon update` advances installer-pinned copies through the same verified
  package manager, using an in-place uv update compatible with Windows. Source
  installs and unverifiable ownership retain manual recovery guidance.
- README and getting-started instructions now include `pip install recon-tool`,
  update and uninstall paths, and an optional release-tag review workflow.
- The roadmap now reflects shipped work and prioritizes install and update
  quality. Default lookups remain free of the withdrawn fusion notice.
- Consolidated the pending AnyIO 4.14.2 patch into the lockfile and matching
  ClusterFuzzLite runtime export. The wheel also requires the patched minimum
  so upgrades cannot retain an older affected transitive dependency.
- Windows launcher updates now hand off to an isolated background worker after
  the running launchers exit, avoiding executable locks. The command reports
  the local progress and result log instead of claiming premature completion.
- Review output-path access errors now produce a useful diagnostic before
  collection begins.
- CT graph partitions and seed-stability runs now use canonical edge ordering,
  preventing certificate arrival order from changing uncapped results.
- Custom Bayesian models reject duplicate parents and unsafe subnormal
  intermediate products instead of emitting misleading posteriors.
- The README shows its terminal illustration before installation. Correlation
  documentation refreshes measured sensitivity values and clarifies robustness
  radii, continuous boundaries, witness attainment, and valid proof origins.

## [2.19.4] - 2026-09-13

Close the gap that let attribution trailers reach commit metadata, and fix a CI
step that failed on a branch-creation push. No collector, fingerprint, claim, or
output change.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Fixed

- CI no longer fails on a branch-creation push. `github.event.before` is all
  zeros for such an event, and the fingerprint-freshness step passed that
  straight to `git` as a revision, failing with `Needed a single revision` on a
  tree that had not changed. The step now falls back to the first parent and
  skips cleanly when no base revision exists, matching how the text-hygiene step
  already resolves the same event.

### Added

- Attribution enforcement covering commit metadata, not only repository text.
  `scripts/check_text_hygiene.py` gains `--commits <range>`, which audits commit
  messages and author and committer identity, and `--message-file <path>` for a
  `commit-msg` hook. The added-line scope alone could never see an attribution
  trailer, because a trailer lives in commit metadata and never appears in a
  diff. Wired into `scripts/check.py`, the CI text-hygiene step, and
  `.pre-commit-config.yaml`; install with
  `pre-commit install --hook-type commit-msg`.
- Tracked `.claude/settings.json` carrying the attribution policy, so it applies
  to every clone rather than one machine. `.gitignore` keeps the rest of
  `.claude/` local.

## [2.19.3] - 2026-09-13

Prevent duplicate evidence from inflating diagnostic strength, cover Shopify's
documented verification owner, and validate the current MCP SDK and portable
plugin package. Preserve public fields, model weights, and collection boundaries.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Fixed

- Doctor output preserves complete, copyable interpreter and package paths at
  narrow terminal widths, including literal markup characters in paths.
- Section-link validation prunes disposable directories before descent and
  checks sentence-final references without accepting partial identifiers.
- MCP compatibility testing now resolves each SDK with its required companion
  `mcp-types` package while keeping unrelated runtime dependencies locked. Add
  current stable SDK 2.2.0 to the blocking local/CI matrix alongside the 1.28.1
  rollback and 2.0.0 floor; all 24 isolated checks pass on 2.2.0.
- Per-slug evidence strength counts each exact source-type/value pair once,
  including when several rule names match it. Repeated records cannot inflate
  `slug_confidences`; retained provenance and distinct-value weights remain
  intact. This does not add a general dependency or calibration model.

### Catalog

- Recognize Shopify's documented `shopify_verification` TXT owner with exact
  owner, lookalike, wildcard, sparse, and provenance regressions. Keep its
  separately undated apex prefix distinct and remove unsupported account,
  SSO, and live-storefront implications from the family's descriptions.

### Documentation

- Define automated acceptance for authorized local improvement loops, including
  concrete evidence and regression gates, without a human approval checkpoint.
- Refine the existing shared agent instructions with bounded work, current-source
  research, failure-driven verification, and distinct compatibility evidence.

## [2.19.2] - 2026-09-09

Clarify the interpretation of correlation diagnostics in the packaged README
and align the roadmap with shipped behavior and the stopped M365 evaluation.
No runtime, model parameter, collection, or schema change.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Documentation

- Put the calibration and heuristic-band limits beside the README's correlation
  overview, and identify `--explain-dag` as the Bayesian model graph.
- Explain the assumptions behind a `0.9314` posterior, distinguish the complete
  latent-state enumeration from its bounded evidence sweep, and document fusion
  in ordinary MCP JSON as well as dedicated diagnostic tools.
- Replace stale release planning with shipped status. Prioritize documented
  public patterns, synthetic and adversarial fixtures, and renderer truth.
  Independent calibration remains unestablished, with no replacement study or
  company outreach planned.

## [2.19.1] - 2026-09-09

Documented catalog additions for Tailscale, PostHog, and Resend, plus
source-checkout agent briefing, GitHub-safe math rendering, and HTTPX v2
security floors. No collector or model change.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Added

- Documented Tailscale `_tailscale-challenge` and PostHog `_posthog-challenge`
  owner-qualified TXT rules, plus PostHog's US managed-proxy CNAME zone and
  Resend's `links1.resend-dns.com` tracking target. Claims stay routing or
  administrative-verification observations. Synthetic owner, lookalike, sparse,
  and related-host tests cover the new rules. No real-target data is committed.

### Security

- Raise locked `httpx2` and `httpcore2` floors so `pip-audit` clears
  CVE-2026-84378 through CVE-2026-84382. These are transitive MCP HTTP
  packages, not a collector change.

### Documentation

- Add a source-checkout working section to `AGENTS.md` so coding agents get
  seams, the canonical local gate, generated-artifact rules, and safety
  constraints without replacing the consumer invocation contract.
- Repair GitHub/KaTeX rendering of `docs/correlation.md` set braces and
  `\left`/`\right` so formulas no longer fail with "Missing or unrecognized
  delimiter for `\left`". Use `\lbrace`/`\rbrace` and keep sized delimiters on
  one line. The documentation gate now rejects `\{` in math and a `\left` at
  end of line.

## [2.19.0] - 2026-09-05

Compatible assurance improvements to collection boundaries, catalog claims,
numerical behavior, operator displays and release reproducibility. No new
collector or model calibration is introduced.

### Tool Surface Changes

Tool surface changes: added flag `--config-path` to `recon doctor`.

The flag selects the exact client file verified after installation. MCP lookup honors `explain=true` on
text and Markdown as well as JSON. Plain briefings retain material collection
caveats and sparse-result guidance. Maintainer fingerprint audits default to
built-ins, with explicit `--effective-catalog` for local additions. Google
identity no longer follows external IdP destinations. Promotion reports bind
the exact evaluated-rule digest and reject unsupported conjunctions and
operator-local rules. Runtime lookup JSON fields and the MCP tool set remain
unchanged.

### Fixed

- Pin HTTP socket destinations to validated public addresses while preserving
  Host, TLS identity, origin pooling, bounded dual-stack fallback, and cleanup
  on cancellation, including an interrupted TLS handshake.
- Keep Google identity redirects within the documented collector boundary and
  stop inferring federation from Google query-string or path keywords.
- Reject nested-wrapper ambiguous regex alternations before synchronous
  fingerprint specificity evaluation. Keep simple disjoint literals accepted;
  admission remains conservative and heuristic.
- Reject special JSON input files before opening them and prevent FIFO-swap
  reads from blocking on platforms with nonblocking file-open support.
- Bind capsule interpretation context to effective custom/ephemeral catalogs
  and prior overrides. Enforce the capsule write-size bound before temporary
  output creation, preserving existing destinations on failure.
- Validate review coordinates consistently before collection and retain partial
  catalog diagnostics when source or detector work fails.
- Use numerically stable, consistent likelihood-ratio ranking. Correct graph
  evidence attribution, Markdown list layout, DOT escaping, and Mermaid custom
  identifiers without claiming calibrated probabilities or additive causal effects.
- Fail explicitly when a custom Bayesian model underflows or has invalid
  normalization mass, including under optimized Python, instead of emitting a
  fabricated uniform posterior. Ordinary-model parameters remain unchanged.
- Prevent the maintainer promotion evaluator from treating one rule as support
  for a conjunction or evaluating uncommitted operator-local catalog additions.
- Filter CNAME discovery candidates against the effective runtime catalog in
  installed wheels, including custom and ephemeral rules, without relying on
  source-only YAML files.
- Anchor portable-plugin configuration, caches, and state under the client's
  persistent plugin data directory. Prefer connected MCP tools without requiring
  shell access, and distinguish installed-plugin triage from checkout-only
  maintainer workflows.
- Include numerical-limit regressions in the mutation gate and its change
  triggers, with one-sided underflow and exact-zero arithmetic anchors.
- Mark per-certificate SAN clipping as graph-construction truncation and use
  the existing deterministic fallback without a misleading seed-stability
  diagnostic. Graph weights, caps, and public fields remain unchanged.
- Share clean non-match versus unavailable-source labeling across source views,
  preserve caveats in plain briefings, and honor human-format MCP explanations.
- Resolve only the selected client configuration path, verify explicit profile
  files after installation, and require manager ownership and matching upgrade
  destinations before automatic uv or pipx upgrades. A successful upgrade command
  no longer asserts that the latest PyPI version was installed.
- Narrow Vercel routes, retire generic AWS-to-SES and unsupported Okta/GitHub
  verification rules, and correct Slack plan and Glitch lifecycle claims.
- Add exact, dated Retool custom-domain and Postmark return-path CNAME rules,
  with synthetic wrong-owner, lookalike, sparse, wildcard and downstream
  claim-isolation tests. Separately retire two unsupported Postmark CNAME
  suffixes and an SPF owner/target confusion; preserve existing documented SPF
  detection with policy-reference wording. No owner probes are added.
- Keep batch serialization failures out of successful peer, ecosystem and
  cohort accounting; preserve explicit operator failure states.
- Clamp model-bound diagnostic inputs before interval arithmetic and normalize
  extreme count vectors without overflow. Keep unavailable support distinct
  from zero, and show the cohort interval method and eligible denominators.
- Apply DMARC what-if changes to the effective component ledger, including a
  nominal reject policy applied to zero percent of messages. Model weights and
  component ceilings are unchanged.
- Accept UTF-8 byte-order marks in exclusion lists without changing raw-byte
  commitments. Bind shared rank-sampling implementation files into new round
  execution digests and use unrounded ratios for promotion threshold decisions.
  Explicitly label the evaluator's pooled diagnostic and unexecuted policy text.
- Wrap narrow terminal rows with aligned continuation text and a single divider,
  preserve CT unavailable/cache/recovery caveats in MCP text, and remove
  magnitude-based security-grade coloring from the aggregate exposure index.
- Add `scripts/release.py --prepare-only` for a checked preparation PR without
  a tag or push. Keep rollback bounded to owned files, then tag the exact
  reviewed merged-main commit only after hosted checks pass.
- Repair optional model-assisted triage to use the built-in inventory, reject
  malformed or incomplete batches before output, preserve same-slug detections,
  and serialize explicitly private pending proposals. No confidence, review
  date or ready-to-promote status is assigned by the model helper.
- Gate CI on the same built wheel's offline contracts across Windows, Linux,
  and macOS. Release smoke also verifies installed catalogs, MCP resources and
  tools, import origin, executable identity, and portable data relocation without
  adding dependency execution to the isolated build-and-seal job.

### Documentation

- Add repository corpus-planning and catalog-round skills; repair the triage
  skill's typed-summary field and portable-packaging status. Document frozen
  exclusions, untouched holdouts, truthful metrics, and independent review.
- Reconcile correlation math and diagrams with executable behavior, correct
  historical calibration interpretation, and distinguish default local operation
  from the draft remote adapter's authentication and disk-retention obligations.
- Clarify the Agent Plugins package root, executable discovery, persistent-state
  isolation, and installation prerequisites. Standards and local protocol checks
  remain distinct from the frozen representative-client evaluation.
- Correct cache-freshness guidance: internal timestamps are not public lookup
  JSON fields. Document fresh collection routes without implying per-record
  freshness, and reconcile cancelled correlation-study status across documents.
- Document a consistent operator design language and a dated platform research
  review covering Hermes, OpenClaw, Pi, DeepSeek Harness and NemoClaw. Separate
  documented host capabilities from unrun client qualification and keep the
  frozen representative-client evaluation unchanged.

## [2.18.4] - 2026-09-02

Default `recon <domain>` no longer prints a fusion-flag deprecation notice.
The v2 implicit default remains fusion enabled; `--fusion` and `--no-fusion`
still pin the diagnostic on or off.

### Tool Surface Changes

Tool surface changes: lookup and batch no longer emit an interactive stderr
notice when neither `--fusion` nor `--no-fusion` is supplied. Help text for
those flags no longer asks operators to pin a future-release choice. Flag
meanings, the implicit enabled default, JSON fields, and MCP behavior are
unchanged.

### Changed

- **Silent default fusion path.** The v2.12 TTY notice that the implicit
  fusion default is deprecated is withdrawn. Running `recon <domain>` on a
  terminal now emits the panel (or JSON) without a compatibility lecture.
  Fusion still runs when neither flag is supplied. Pass `--no-fusion` for
  deterministic output or `--fusion` to pin the diagnostic on.
- ADR-0013 records the notice withdrawal: the default-off flip remains
  deferred optional compatibility debt, not a scheduled v3 requirement.

## [2.18.3] - 2026-09-01

This patch tightens diagnostic and renderer truthfulness without changing the
CLI command set, collection boundary, stable JSON fields, or briefing versus
full-map split.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Changed

- The panel and Markdown renderer now share one internal collection-status
  projection. Core-source failures, recovered CT fallback, total CT failure,
  and CT cache recovery retain distinct meanings without creating a new public
  output contract.
- The no-argument welcome and onboarding docs now distinguish a real lookup
  command from fresh collection: ordinary lookup may reuse the default 24-hour
  result cache, while `--no-cache` requests fresh collection.
- The fusion transition notice and active compatibility docs no longer promise
  a v3 default change that may never ship. Explicit flags pin behavior across
  future releases; the v2 omitted choice remains enabled.
- The default panel wraps the unclassified-surface explanation, discovery
  command, and examples within its width instead of leaving detached words or
  losing continuation indentation.
- NamespaceReviewBundle Markdown labels `email_security_score` as a public
  compatibility count out of five rather than an unbounded control total.
- The root roadmap is again a short current-state document. Detailed shipped
  history stays in the changelog and roadmap history, while active gates,
  invariants, standing loops, and deliberate exclusions remain visible.
- Pre-commit, the canonical local gate, and CI now let `pyproject.toml` own the
  full Pyright scope. CI also cancels obsolete runs for the same ref.

### Fixed

- The live and static MCP doctors now require all six registered canonical
  resources. The live doctor reads and validates the ReviewBundle schema before
  reporting success, and its summary derives the resource count instead of
  hard-coding a claim.
- Markdown no longer says that every degraded source makes subdomain discovery
  incomplete. Core failures name the affected source, routine recovered CT
  fallback stays quiet, total CT failure names CT incompleteness, and CT cache
  recovery reports its age and retained-host count.
- Contributor documentation now matches the admitted uv `>=0.11.8,<0.13`
  range while reproducible workflows remain pinned to exact uv 0.11.17.
- The portable reporting caveat now includes certificate transparency and
  describes observations for a namespace instead of claiming that one domain
  published every retained item.

### Tests

- Added live six-resource MCP doctor assertions and ReviewBundle schema-envelope
  validation coverage.
- Added panel, Markdown, JSON, full/default, and MCP Markdown coverage for core
  degradation, CT fallback, total CT failure, and CT cache recovery.
- Updated golden renders for accurate collection notes and bounded
  unclassified-surface wrapping.
- Added pre-commit/CI Pyright-scope parity and same-ref concurrency assertions,
  and tightened the existing panel and merger file-size ratchets.

## [2.18.2] - 2026-09-01

v2.18.2 keeps the dependency-maintenance path current without changing any
released CLI, MCP, schema, or runtime behavior. It admits Dependabot's current
uv updater while preserving the exact reproducible release toolchain, and
advances the reviewed workflow and build dependency pins as one coherent
maintenance batch.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Changed

- Re-authored the scheduled dependency updates as one coherent maintainer
  change: CodeQL and build-provenance actions advance at immutable SHAs, and
  the locked build graph advances `packaging` from 26.2 to 26.3 together with
  its generated hash constraints.

### Fixed

- Dependabot's current uv 0.12.7 updater is admitted by the bounded
  `>=0.11.8,<0.13` project range. Reproducible maintainer, CI, package-build,
  and release paths remain pinned to exact uv 0.11.17, and uv 0.13 remains
  excluded pending a separate review.

### Tests

- Bound the updater and reproducible uv versions independently, retained the
  next-minor stop, and updated workflow contract assertions with the reviewed
  action SHAs.

## [2.18.1] - 2026-08-31

v2.18.1 restores CT-discovered related hosts when later CNAME enrichment
degrades, without exposing CNAME-dependent classification or changing the
stable lookup schema.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Fixed

- **CT related hosts survive degraded CNAME enrichment.** A successful live,
  partial, or cached CT result now retains its exact related-domain names when
  the later `dns:cname` classification channel is unavailable. CNAME-owned
  attributions and motifs still fail closed, lexical observations are rebuilt
  from the retained CT names, and lookup, Markdown, panel, MCP, cache, and
  NamespaceReviewBundle surfaces now agree. Existing cache entries without the
  additive CT name-provenance field remain conservatively empty under this
  degraded condition.

### Tests

- Added synthetic regression coverage for live, partial, and cached CT
  provenance; source and merged projection; legacy caches; stable JSON;
  briefing and full renderers; connection-map classification; MCP JSON; and
  NamespaceReviewBundle embedding.

## [2.18.0] - 2026-08-30

NamespaceReviewBundle v1 adds a role-neutral, caller-owned handoff for one
public namespace. A bundle is composed from exactly one fresh ordinary passive
resolution, preserves collection opportunity and failure states, and links
review candidates to retained evidence without turning observations into a
security verdict.

### Tool Surface Changes

Tool surface changes: adds `recon review <domain>` with `--json`, `--output`,
`--force`, `--no-ct`, and `--timeout`; adds the structured MCP
`build_review_bundle(domain, no_ct=false, timeout_seconds=120.0)` tool; and adds
the local `recon://review-bundle-schema` MCP resource. The `domain_report`
prompt now uses the new one-call bundle path. Existing lookup, batch, capsule,
and stable v2 JSON fields are unchanged.

### Added

- **Fresh review artifacts.** The CLI and MCP tool bypass the lookup-result
  cache, perform exactly one ordinary passive resolution, keep direct probes
  disabled, and derive the explained lookup plus review candidates from the
  same in-memory result. The core composer rejects cached lookup inputs and
  contradictory cache or direct-probe attestations. CT remains optional and its
  provider/cache provenance is recorded separately.
- **Evidence-linked handoff.** Stable content-derived evidence and candidate
  identifiers make every candidate reference inspectable. Source opportunities
  distinguish observed values, observed emptiness, partial collection, and
  unavailable collection.
- **Typed failure state.** Failed baselines contain no inferred observations,
  evidence, or review candidates. The workflow records a typed error and
  explicit `not_observed` or `unavailable` collection validity instead.
- **Separate contract.** A generated, self-contained Draft 2020-12 schema is
  published at `docs/review-bundle-schema.json` and shipped byte-identically in
  the wheel. ReviewBundle-owned objects are closed and the stable lookup v2
  schema is embedded mechanically.
- **Runtime contract parity.** Bundle construction and loading apply both the
  semantic integrity checks and the exact packaged Draft 2020-12 schema, so a
  malformed embedded lookup or explanation DAG cannot pass the public loader.
- **Role-neutral rendering.** One deterministic Markdown projection leads with
  collection validity, preserves evidence and candidate identifiers, groups
  candidates by `observation_state`, names unresolved evidence, and ends with
  the fixed scope statement for defenders, consultants, analysts, and admins.

### Changed

- The generated CLI and MCP inventories, agent guidance, MCP compatibility
  contract, stability policy, claim audit, and doctor messaging now include the
  ReviewBundle surfaces and six local JSON resources.
- The fail-closed default-claim audit adds an exact ReviewBundle family covering
  fresh composition, structured transport, and human rendering.

### Tests

- Added success, sparse, degraded, unavailable, timeout, deterministic digest,
  evidence linkage, mutation rejection, schema interoperability, CLI, MCP,
  formatter, packaging, and generated-artifact coverage.

## [2.17.13] - 2026-08-30

The trust paths around defensive reporting, installation, and release
readiness are now explicit and fail closed. Documentation also distinguishes
released runtime installation from source-checkout integration scaffolds, and
the roadmap now separates shipped audience workflows from the prospective
ReviewBundle contract.

### Tool Surface Changes

Tool surface changes: no command, flag, JSON field, MCP tool, or MCP resource
is added, removed, or renamed. The existing `domain_report` prompt now stops
after a failed baseline lookup and requests only fields its bounded tool
sequence can return. Installer scripts now require the first `recon` launcher
on PATH to report the exact installed version before declaring success.

### Fixed

- **Defender report integrity.** `domain_report` calls hardening-gap analysis
  only after a successful explained lookup, does not infer gaps from collection
  failures, and no longer asks for freshness or source-opportunity fields that
  are absent from its allowed outputs.
- **Installation postconditions.** Both installers verify the resolved PATH
  launcher, reject stale, malformed, or failing version output, and show
  bounded candidate diagnostics without mutating competing installations.
- **Launcher resilience.** `recon doctor` treats undecodable or malformed
  launcher output as a diagnostic failure instead of crashing or accepting an
  arbitrary version token.
- **Distribution clarity.** The guides now state that PyPI provides the CLI and
  MCP runtime while plugin and agent scaffolds remain source-checkout material.
  The primary Claude Code path uses the released MCP installer.
- **Portfolio discoverability.** The README and getting-started guide surface
  the complete batch evidence bundle, and `--summary` help explains when the
  combined ecosystem path retains ordered domain rows.

### Changed

- MCP prompt names, summaries, and arguments are now generated into the public
  surface inventory and covered by the fail-closed default-claim audit.
- Release readiness requires the repository's pinned uv version before checking
  lock freshness and verifies the live default-branch ruleset, including exact
  required checks, strictness, history protections, and reported bypass actors.
- The roadmap records the v2.17.12 audience workflows as shipped and stages a
  prospective ReviewBundle v1 behind unresolved freshness and schema contracts.
- The sole over-cap module baseline now reflects the current 1,506-line panel
  implementation, preserving prior decomposition progress in the ratchet.

### Tests

- Added mixed-success `BatchResult` JSON Schema validation, prompt failure-path
  and governance coverage, hostile launcher-output cases, installer behavioral
  postconditions, pinned-toolchain checks, and branch-ruleset drift cases.

## [2.17.12] - 2026-08-30

Audience-specific workflow composition now makes the existing public evidence
easier to use without expanding recon's collection boundary. Admins can see
which installation is actually running, defenders have a fixed validity-first
briefing, and consultants can carry ordered domain records, ecosystem overlaps,
and an aggregate cohort summary in one portfolio artifact.

### Tool Surface Changes

Tool surface changes: no command, flag, MCP tool, or MCP resource is added,
removed, or renamed. The stable `BatchResult` JSON wrapper gains an optional
`cohort_summary` field when `--summary` and `--include-ecosystem` are combined.
The existing `domain_report` MCP prompt now composes one explained JSON lookup
with cache-first hardening gaps. `recon doctor` adds installation identity and
PATH launcher diagnostics.

### Added

- **Portfolio evidence bundle.** `recon batch domains.txt --json
  --include-ecosystem --summary --summary-schema 2.2` retains ordered success
  and error records plus ecosystem hyperedges, then adds the existing
  aggregate-only cohort document. Plain batch JSON, ecosystem-only JSON, and
  summary-only JSON keep their prior shapes.
- **Evidence-first defender briefing.** The `domain_report` prompt now fixes the
  order and boundaries for collection validity, observed mail and identity,
  public connection indicators, state-grouped review candidates, unresolved or
  unavailable evidence, and the standing scope statement. It does not
  automatically score, simulate, recurse, or enable opt-in probes.

### Changed

- **Installation identity is visible.** `recon doctor` reports the running
  version, Python executable, package location, detected installation method,
  and the first PATH launcher. A version collision produces an actionable
  warning. `recon update --check` now distinguishes an installed build that is
  newer than PyPI instead of calling it up to date.
- **First-run wording is consistent.** The CLI and getting-started guide now
  invite review of a domain without implying an authorization prerequisite for
  ordinary public-metadata collection. The README starts with real-domain,
  single-domain, portfolio, and MCP paths while keeping reserved examples
  clearly labeled as syntax or synthetic output.

### Tests

- Added focused update-state, installation collision, defender-prompt,
  combined portfolio, all-failed portfolio, aggregate privacy, and JSON Schema
  contract coverage.

## [2.17.11] - 2026-08-30

Cloudflare infrastructure fingerprinting now follows the provider's current
DNS, partial-zone, Pages, and China Network documentation. Generic or
unsupported match shapes no longer stand in for those exact public roles. The
catalog now contains 1,112 detection rules, including 157 dated rules, with no
currently stale dated rules.

### Tool Surface Changes

Tool surface changes: no command, flag, JSON field, MCP tool, or MCP resource
is added, removed, or renamed. The Cloudflare catalog replaces one unsupported
apex TXT value with an owner-qualified TXT rule, narrows two CNAME patterns,
and adds two current China Network target families.

### Changed

- **Cloudflare verification and edge precision.** The unsupported apex
  `cloudflare-verify=` value is replaced by the documented
  `cloudflare-verify.<domain>` owner. A generic CNAME string match and broad
  `cloudflare.net` target narrow to the current `cdn.cloudflare.net` partial-
  zone family. Exact Cloudflare standard and secondary nameserver roles and the
  Pages role are dated. The current `cdn.cloudflareanycast.net` and
  `cdn.cloudflarecn.net` China Network targets are added. `pacloudflare.com`
  remains an undated legacy observation because current first-party guidance
  does not name it.
- **README claim precision.** Lookup timing is described as provider-dependent,
  the public-metadata workflow no longer implies an authorization prerequisite,
  and the local gate is distinguished from hosted scheduled and supply-chain
  workflows.
- **One blocking CI result.** A final `ci-gate` job now requires every job in
  the main CI workflow, including both MCP compatibility rows and the optional
  cloud artifact checks, to pass before it succeeds. This provides one stable
  branch-rule context while preserving each diagnostic job.

- **The `v2.6.7` tag and its GitHub release were removed on 2026-08-26.** That
  tag was the last reference holding the two pre-rewrite commits whose messages
  still carried generated-author trailers, and the 2.6.8 release already
  republishes identical package content from clean, `main`-reachable history.
  The 2.6.7 distributions stay on PyPI but no longer have a tag or release to
  verify against; use 2.6.8 for any tag-bound provenance check of that content.
  No other tag, release, or published artifact changed.

### Tests

- Added exact metadata, owner-qualified TXT, current global and China Network
  CNAME, Pages, sparse-value, legacy-rule, and deceptive-suffix coverage for
  the reviewed Cloudflare rules.

- **The provider-drift gate no longer goes red on a dropped identity request.**
  `user_realm.source_unavailable` is a transport outcome, so one rate-limited
  request from a shared CI egress address failed the weekly live smoke while
  GetUserRealm itself kept answering, and the job has no retry. The reserved-
  domain tests now resolve up to three times while that source is unavailable.
  A source that stays unavailable across every attempt still fails, the raw
  provider probe still reads `NameSpaceType` directly, and the failure message
  now names the provider's own answer so recon disagreeing with a healthy
  endpoint is distinguishable from an endpoint that is down.

## [2.17.10] - 2026-08-21

Tencent EdgeOne CNAME fingerprinting now covers the current documented shard
0 form and distinguishes four exactly supported shards from two undated legacy
observations. The catalog has 869 entries, 692 unique slugs, and 1,109
detections; 149 detections are dated (13.4 percent), with zero currently stale
dated rules.

### Tool Surface Changes

Tool surface changes: no command, flag, JSON field, MCP tool, or MCP resource
is added, removed, or renamed. One label-bounded `cname_target` fingerprint,
`eo.dnse0.com`, is added under the existing `tencent-edgeone` slug.

### Changed

- **Tencent EdgeOne shard coverage.** Current first-party API examples support
  shards 0, 2, 3, and 5, which now carry exact references and review dates.
  Shards 1 and 4 remain undated because the reviewed current pages do not name
  those exact forms.
- **Tencent EdgeOne claim scope.** All six descriptions now report an observed
  routing relationship without claiming active traffic, enabled CDN or WAF
  features, or current configuration state.

### Tests

- Added exact metadata, all-shard positive, deceptive-suffix negative, tier,
  and stable-slug coverage for the Tencent EdgeOne family.

## [2.17.9] - 2026-08-21

Zendesk DNS fingerprinting now follows the provider's current email-domain and
help-center guidance. The catalog still has 869 entries, 692 unique slugs, and
1,108 detections; 145 detections are dated (13.1 percent), with zero currently
stale dated rules.

### Tool Surface Changes

Tool surface changes: no command, flag, JSON field, MCP tool, or MCP resource
is added, removed, or renamed. One Zendesk fingerprint changes from an
unsupported apex TXT value to the documented owner-qualified TXT form.

### Changed

- **Zendesk TXT precision.** The unsupported apex
  `zendeskverification=` observation is replaced by a query for a nonempty TXT
  value at `zendeskverification.<domain>`, matching Zendesk's current
  external-email verification guidance.
- **Current Zendesk DNS roles.** The exact `mail.zendesk.com` SPF include and
  both `zendesk.com` CNAME roles now cite current first-party guidance, carry
  review dates, and make narrower claims. Two unsupported legacy variants stay
  undated and no longer cite an unusable shared page.
- **README front door.** The synthetic Example Industries terminal demo now
  uses a current Linux-style presentation, and the README links directly to
  the correlation and provenance design document.

### Tests

- Added exact metadata, owner-qualified TXT, empty-value, deceptive-suffix,
  parsed-SPF, CNAME-chain, and provenance coverage for all six Zendesk rules.

## [2.17.8] - 2026-08-21

The development supply-chain lock now excludes the pip versions affected by
`PYSEC-2026-3721` / `CVE-2026-13346`. The published recon runtime was not
affected because pip remains outside its dependency graph.

### Tool Surface Changes

Tool surface changes: no command, flag, JSON field, MCP tool, MCP resource, or
fingerprint pattern is added, removed, or renamed.

### Security

- **Development installer floor.** The `pip-audit` toolchain now carries an
  explicit `pip>=26.2` floor, and the lock resolves the current fixed release.
  This closes the malicious-package-index arbitrary-write advisory for
  contributor and CI environments without adding pip to the runtime package.

### Tests

- Added a dependency-policy contract that requires the fixed pip floor and a
  single lock resolution at or above it.
- The live MCP doctor handshake now runs serially after the parallel suite and
  appends to its coverage data. This preserves the complete coverage gate while
  preventing saturated test workers from consuming the SDK's bounded discovery
  window.

## [2.17.7] - 2026-08-21

The bounded Statuspage freshness review replaces a dead shared reference,
dates only the three exact values in current Atlassian DNS guidance, and narrows
four retained legacy observations. The catalog still has 869 entries, 692
unique slugs, and 1,108 detections; 141 detections are dated (12.7 percent),
with zero currently stale dated rules.

### Tool Surface Changes

Tool surface changes: no command, flag, JSON field, MCP tool, MCP resource, or
fingerprint pattern is added, removed, or renamed. Three existing Statuspage
rules gain current references and scoped descriptions. Four existing rules
remain undated and no longer cite a dead page or claim current configuration.

### Changed

- **Current Statuspage DNS roles.** The exact
  `status-page-domain-verification=` TXT, `stspg-customer.com` SPF include, and
  `<PAGE_CODE>.stspg-customer.com` CNAME-target family now cite Atlassian's
  current DNS guide and carry `2026-08-21` review dates.
- **Legacy Statuspage observations.** The no-hyphen TXT variant plus
  `statuspage.io` and `statuspageio.com` CNAME observations remain undated.
  Their descriptions now distinguish them from the current custom-domain and
  notification-email flows and avoid page-activity, SSO, and ownership claims.

### Tests

- Added exact metadata, positive, deceptive-suffix, parsed-SPF, and provenance
  coverage for all seven Statuspage rules.

## [2.17.6] - 2026-08-20

The Microsoft residual review replaces unsupported product-role wording with
current, bounded descriptions and records a fail-closed portability cost-gate
disposition. The catalog still has 869 entries, 692 unique slugs, and 1,108
detections; 138 detections are dated (12.5 percent), with zero currently stale
dated rules.

### Tool Surface Changes

Tool surface changes: no command, flag, JSON field, MCP tool, or MCP resource is
added, removed, or renamed. Four existing Microsoft 365 rules gain current
first-party references and scoped descriptions. The existing `msv1.invalid`
rule remains undated and now explicitly abstains from inferring mail routing or
migration state.

### Changed

- **Bounded Microsoft endpoint evidence.** `tm-3.office.com`,
  `svc.cloud.microsoft`, and `svc.sovcloud.cn` now point to current Microsoft
  endpoint guidance and describe a Microsoft route without inferring a
  workload, tenant, active use, location, or subscription. The broad
  `eo.outlook.com` MX suffix is narrowed to the currently documented
  `mail.eo.outlook.com` legacy family.
- **Verification-residue semantics.** `msv1.invalid` remains undated because no
  current first-party product page documents its role. Its description now
  states only the observed non-routable domain-verification relationship and
  explicitly rejects Exchange Online routing and migration-state inferences.
- **Portability cost gate stopped before collection.** GPT-5.6 Luna is the
  declared common model for a future resumed run and the hard external-charge
  ceiling is $5 total. Account-side hard stops and a reproducible driver for
  the three required desktop clients could not be verified from this
  environment, so the frozen stop rule applied with zero model sessions and
  $0 external spend.

### Tests

- Added positive, deceptive-suffix, sparse, metadata, and exact-provenance
  coverage for all five reviewed Microsoft residual rules.

## [2.17.5] - 2026-08-20

The standing freshness pass updates provider-documented mail-routing families,
and the portable Agent Plugins track now reflects Published v1.0.0 plus a
passing three-client/runtime preflight. The catalog has 869 entries, 692 unique
slugs, and 1,108 detections; 134 detections are dated (12.1 percent), with zero
currently stale dated rules.

### Tool Surface Changes

Tool surface changes: no command, flag, JSON field, MCP tool, or MCP resource is
added, removed, or renamed. The fingerprint catalog adds 11 documented regional
TrendAI SPF values and 16 documented AWS SES receiving regions. The broad
Marketo `mkto-` CNAME-target fragment is replaced by Adobe's documented
`mkto-[letter][four digits].com` host form. Seven partial regional `aws-nlb`
patterns are consolidated into one partition-aware ELBv2 regex while retaining
the stable slug. Five partial regional `aws-api-gateway` patterns are likewise
consolidated into one partition-aware regex. The existing
`ms-domain-verification=` rule moves from the Microsoft 365 slug to the new,
provider-correct `azure-communication-services-email` slug, and broad Microsoft
365 government, Autodiscover, and SharePoint patterns are narrowed to current
documented roles.

### Added

- **Current TrendAI regional SPF coverage.** Exact documented US, Germany,
  Australia, Japan, Singapore, India, UAE, UK, Canada, South Africa, and
  Indonesia SPF values now have dated references plus fictional positive and
  lookalike-negative fixtures.
- **Complete current AWS SES receiving-region coverage.** The six existing
  regional MX targets are dated and the other 16 endpoints in AWS's current
  22-region receiving table are added with exact suffix matching, fictional
  positives, and deceptive-lookalike negatives.
- **Passing agent-portability readiness evidence.** A disclosure-safe
  2026-08-20 memo records the frozen preflight passing with recon 2.17.4 and all
  three required clients, with zero sessions and zero network requests.
- **Azure Communication Services Email classification.** The exact
  `ms-domain-verification=` administrative token now identifies the service
  Microsoft currently documents for it, with a dated first-party reference and
  a distinct slug.

### Changed

- **Agent Plugins status matches the current standard.** Active documentation
  now describes v1.0.0 as Published while preserving the frozen 2026-08-14
  Working Draft snapshot as historical contract evidence. The canonical plugin
  and MCP schema bytes remain identical to the pinned copies.
- **Current mail-gateway references and roles.** TrendAI regional MX, Barracuda
  Email Gateway Defense inbound MX, and Cisco Secure Email Cloud Gateway
  `iphmx.com` rules use current provider documentation and dated scoped wording.
  Earlier or unsupported public patterns remain undated rather than receiving a
  synthetic freshness date.
- **Current major-provider SPF references.** AWS SES, Google Workspace, and
  Microsoft 365 SPF rules now point to provider pages that name the exact
  include values and carry a 2026-08-20 verification date.
- **Current Akamai edge-hostname references.** `akamaiedge.net`,
  `akamaized.net`, `edgekey.net`, and `edgesuite.net` CNAME rules now point to
  the current Property Manager mapping guide and carry a verification date.
  Akamai patterns not named by that page remain undated.
- **Bounded HubSpot freshness review.** Current HubSpot pages support the
  account-qualified `hubspotemail.net` SPF suffix and `hubspot.net` connected
  domain CNAMEs, so those three rules are dated and boundary-tested. Seven
  other HubSpot patterns remain undated because current first-party pages do
  not name their exact pattern and role.
- **Bounded Marketo freshness review.** Current Adobe pages support
  `include:mktomail.com`, account-qualified `mktoweb.com` CNAME targets, and
  the exact Marketo tracking-link host form. Those four rules are dated and
  boundary-tested. Five other Marketo patterns remain undated without exact
  current first-party support.
- **Bounded Salesforce Marketing Cloud freshness review.** Current Salesforce
  pages support eight `exacttarget.com`, `sfmc-content.com`,
  `sfmc-marketing.com`, `marketingcloudapis.com`, and `exct.net` CNAME or
  discovered-target roles. Those rules are dated, scoped to their documented
  application, CloudPages/content, web-view, API, and Subscription Center uses,
  and boundary-tested. The `exacttarget.com` SPF and `SFMC-` TXT observations
  remain undated without exact current first-party DNS-role support.
- **AWS ELBv2 surface normalization.** Seven partial regional `aws-nlb` rules
  are replaced by one validated pattern covering the current commercial,
  GovCloud, and China `name-id.elb.region.amazonaws.*` forms. The stable slug is
  retained, but the user-facing name and description now state that DNS cannot
  distinguish Application from Network Load Balancers. Current partition and
  deceptive-lookalike fixtures enforce that boundary.
- **AWS API Gateway surface normalization.** Five partial regional rules are
  replaced by one validated pattern for commercial, GovCloud, and China
  regional API targets. Edge-optimized CloudFront targets, private VPC endpoint
  names, bare service endpoints, and deceptive suffixes remain outside the
  claim boundary.
- **Microsoft administrative and endpoint roles corrected.** The current
  `MS=ms########` token remains Microsoft 365 domain verification, while
  `ms-domain-verification=` is no longer attributed to that service. GCC High
  MX is narrowed to `mail.protection.office365.us`; the government SPF and
  `usgovcloud.microsoft` roles are assigned to the stable government variant;
  and commercial Autodiscover is narrowed from `outlook.com` to
  `autodiscover.outlook.com`. The exact SharePoint CNAME role is dated from
  current Microsoft guidance.
- **Regex-shaped CNAME-target rules.** Runtime surface attribution and the
  discovery filter now share one safe matcher for whole-domain suffixes,
  label-bounded literal fragments, and validated regex patterns.

### Fixed

- **CNAME-target runtime and discovery parity.** The discovery filter now uses
  the same label, fragment, and regex boundaries as live surface attribution,
  preventing already-covered decisions from drifting from runtime behavior.
- **Live CNAME label-boundary matching.** Plain whole-domain catalog patterns
  now use DNS-label suffix comparison, matching cached replay and preventing a
  target such as `vendor.example.evil.invalid` from being attributed to
  `vendor.example`. Regex-shaped CNAME rules retain regex matching.
- **Cisco gateway directionality.** `iphmx.com` is described as the current
  Cloud Gateway allocation family; `ess.cisco.com` remains an undated earlier
  observation instead of being labeled current.
- **Deterministic terminal-demo generation under `TERM=dumb`.** The renderer
  now fixes both terminal dimensions, so the committed SVG and canonical local
  gate do not depend on the invoking shell's terminal classification.

## [2.17.4] - 2026-08-20

The Okta custom-domain family is dated from current public pages. Dead
`help.okta.com` custom-url-domain and preview-orgs links, and a 404
government marketing URL, now point at the live developer guide and
allowlist article. `_oktaverification`, `okta.com`, `oktapreview.com`,
`customdomains.okta.com`, `okta-dnssec.com`, and `okta-gov.com` are
dated. `okta-domain-verification` stays undated because the current
guide does not name it. Mimecast inbound MX (`mimecast.com`,
`mimecast.co.za`) and `_netblocks.mimecast.com` SPF are dated from
current support articles. The generic `^mimecast` TXT prefix and
`mim.ec` SPF stay undated. Proofpoint gateway MX/SPF stays undated:
public product pages do not name `pphosted.com` / `ppe-hosted.com`, and
the Essentials connection-details article is login-walled.

### Tool Surface Changes

Tool surface changes: no command or flag is added, removed, or renamed.

### Changed

- **Okta custom-domain family matches the current developer guide.**
  `_oktaverification` is the bring-your-own-certificate ownership TXT;
  Okta-managed certificates use ACME instead. `okta-dnssec.com` is the
  documented DNSSEC custom-domain target. `okta-gov.com` is dated from
  the current IP-allowlist article, not a 404 marketing page.
- **Mimecast gateway family matches current support articles.**
  Regional inbound hosts such as `us-smtp-inbound-1.mimecast.com` and
  `za-smtp-inbound-1.mimecast.co.za` are named on the gateway-
  configuration article. The outbound-SPF article names
  `include:_netblocks.mimecast.com`. The `^mimecast` TXT prefix is not
  named on the current domain-validation article and stays undated.
- **Proofpoint gateway hosts remain undated.** The named mail-routing
  queue still includes Proofpoint, but no current public vendor page
  names the MX or SPF hosts. Dates are not stamped from login-walled
  or generic product pages.

## [2.17.3] - 2026-08-19

The first named fingerprint-freshness pass dates the Google Workspace and
Microsoft 365 MX families against the current vendor pages. `aspmx.*` is
the documented pre-2023 series; `smtp.google.com` is the current default.
`*.mail.protection.outlook.com` remains named on Learn; `*.mx.microsoft` is
the DNSSEC/DANE form. No pattern was added or retired.

### Tool Surface Changes

Tool surface changes: no command or flag is added, removed, or renamed.

### Changed

- **Google Workspace MX family matches the current setup page.** The
  `aspmx.*` rule no longer calls that series the primary inbound cluster.
  Both `aspmx.l.google.com` and `smtp.google.com` now cite the 2026-08-14
  Workspace MX page and carry `verified: 2026-08-19`.
- **Microsoft 365 MX family matches the current Learn pages.**
  `mail.protection.outlook.com` cites the external DNS-records article.
  `mx.microsoft` cites the SMTP DANE article. Both are dated. The older
  host is not retired.

## [2.17.2] - 2026-08-19

The no-args banner and lookup `--help` now name `--md` and `--full` as the
connection map. The reserved-name banner matches the README: live lookups of
`example.com` return stray public residue at High confidence, not an empty
panel.

### Tool Surface Changes

Tool surface changes: no command or flag is added, removed, or renamed.
Lookup `--md` / `--full` help and the no-args usage list name `--full` as
the connection map. The reserved-name banner now says residue, not emptiness.

### Changed

- **No-args banner names `--md`.** The usage list already had `--plain` and
  `--json`. A 2.17.0 playtest looking for the connection map from `recon`
  with no arguments never saw `--md`.
- **Lookup `--help` names the map.** `--md` is "Grouped Markdown report;
  `--full` is the connection map". `--full` now also names host classes.
- **Reserved-name banner matches the README.** The previous "publish little
  or nothing" line was false on live reserved names: they return stray
  public residue at High confidence, not a company result.

## [2.17.1] - 2026-08-19

The briefing related-domain cut now ranks identity and commerce host classes
ahead of test/CDN names. ``auth.`` / ``sso.`` / ``shop.`` / ``workday.`` outrank
``cdn.e2eprod`` residue. The classified host-class list stays on ``--md --full``
and JSON. Default briefing cuts stay. A 2.17.0 playtest on a dense creative-software
target spent six of eight related names on ``cdn.e2eprod`` / ``test`` hosts while
``sso.`` and ``shop.`` waited behind ``--full``.

### Tool Surface Changes

Tool surface changes: no command or flag is added, removed, or renamed.

### Changed

- **High-signal related-domain cut prefers class-named hosts.** The shared
  briefing used to keep the first eight prefix matches in list order, so a
  dense ``cdn.`` / ``api.`` run could hide ``sso.`` and ``shop.``. It now ranks
  identity and commerce prefixes first, deprioritizes e2e/test/stage labels,
  and no longer treats ``cdn.`` as a briefing class. ``--full`` still lists
  every host.

## [2.17.0] - 2026-08-19

Additive connection map. JSON always emits a grouped `connection_map` of every
observed vendor and related-host class. `--md` uses the same lanes as the
panel (Email, Identity, AI, ...) instead of a flat Tech Stack list. `--md
--full` is the downstream face: empty lanes stay visible, evidence roles stay
on every logo, and related hosts are classified rather than capped. Default
`--md` remains the briefing: same names, grouped, still capped, still omitting
unattributed matches. No collection change, and no row is dropped.

### Tool Surface Changes

Tool surface changes: no command or flag is added, removed, or renamed.
`--json` gains the additive `connection_map` object. `--md` headings change
from Microsoft 365 / Google Workspace / Tech Stack to the panel lanes; `--md
--full` adds empty lanes, catalog summaries, and `Related Host Classes`.

### Added

- **`connection_map` on the JSON record.** Derived at format time from the
  existing services, evidence roles, surface attributions, and related
  domains. Every display lane is present, including empty AI. Role-unavailable
  matches stay with `role: unavailable`. Related hosts are grouped by first
  label (`auth.`, `shop.`, `workday.`, `loyalty-`, `other.`). `explicit_absences`
  copies `email_gateway` and `mta_sts_mode`.
- **`--md` lane grouping.** Default `--md` renders Email / Identity / Cloud /
  Security / AI / Data & Analytics / Collaboration / Business Apps the way the
  panel already did. `--md --full` keeps every lane, including empty ones as
  *none observed in public DNS*, prints evidence roles, and classifies related
  hosts instead of listing a capped briefing cut.
- **`--full` related hosts are classified on the panel too.** The complete
  terminal record groups every related host by first-label class (`auth.`,
  `shop.`, `workday.`, `developer.`, `community-`, ...) instead of one comma
  list. The default briefing still shows the high-signal cut.

### Fixed

- **Display-override names now keep their slug on the connection map.** Identity
  hubs such as `Okta SSO hub` are not fingerprint display names. The map
  previously left `slug` null, so a downstream consumer could not join the row
  to `surface_attributions`. The reverse display-override lookup restores the
  slug.
- **Connection-map summaries follow the evidence role.** A slug that appears in
  more than one YAML file no longer donates a later CNAME gloss to every row.
  An MX Microsoft 365 entry uses an MX or TXT description, not the Mira
  service-zone CNAME.

### Documentation

- schema.md and getting-started name JSON / `--md --full` as the downstream
  connection map. Default `--md` stays the briefing.

## [2.16.1] - 2026-08-19

Catalog-gate correctness and published-docs catch-up. `recon fingerprints
check` now rejects duplicate YAML mapping keys that PyYAML was silently
dropping. The published README and roadmap now name the fingerprint-freshness
loop as the standing work after the v2.16 engine close. No stable JSON, CSV,
MCP, cache, or capsule contract changes.

### Tool Surface Changes

Tool surface changes: no command or flag is added, removed, or renamed.

### Fixed

- **Fingerprint YAML now rejects duplicate mapping keys.** PyYAML keeps the
  last value and drops the first, so the catalog gate could not see leftover
  wording. `recon fingerprints check` now fails that class. The first live
  find was a second `description` on the Google Workspace `ghs.google.com`
  detection; the same sweep dropped leftover first `reference` keys on Slack
  plus ten surface-catalog detections. The generated catalog already used the
  surviving last value in every case.

### Documentation

- README, ROADMAP, catalog-strategy, contributing, and the strategic-gap audit
  now name the fingerprint-freshness loop as the standing work after the v2.16
  engine close. Agent portability stays parked on representative-client
  availability and does not queue product work. The first vendor-doc pass
  records two already-matched mail-routing hosts whose family wording still
  treats a legacy or older default as current.
- This package also publishes the post-2.16.0 reader-facing README rewrite,
  the standing-loops reframe, the ADR-0013 fusion-as-debt amendment, and the
  adversarial corpus result, all of which were already on main.

## [2.16.0] - 2026-08-17

One record, one briefing, in every shape. Four consecutive black-box rounds
found defects only in how recon presents a result, never in the data, and always
the same class: a decision applied to one renderer and not the others. This
release makes the default view a single shared definition every human surface
renders, adds a gated parity matrix so the next such drift is a failing check
rather than a fifth report, and reconciles the SemVer contradiction the `--plain`
change left open in 2.15. No stable JSON, CSV, cache, or capsule contract
changes.

### Tool Surface Changes

Tool surface changes: no command or flag is added, removed, or renamed. `--md`
and the MCP `lookup_tenant` text surface now render the default briefing (roles
first, insights and related domains cut with an `--md --full` / `format="json"`
note, `--confidence-mode` honored), with the complete report behind `--md
--full`; this is a breaking change to those two human-facing selections, of the
same class ADR-0016 made to `--plain`. `--md` titles the report on the queried
domain and carries the display name as a labelled, unverified field. The MCP
`lookup_tenant` JSON payload now populates `fusion_enabled`, `slug_confidences`,
and `posterior_observations` (previously advertised but empty). `--plain --full`
gains `mail:` / `identity:` keys on a role split. `--md` ends with a scope
caveat line. `--json` and `--csv` are unchanged.

### Added

- **One shared briefing (ADR-0017).** `build_briefing` returns the default view
  as data (the role split, the related and insight cuts with their reconciling
  notes, the confidence scalars), and the panel, `--plain`, `--md`, and the MCP
  text surface all render it. A renderer can no longer show the default view
  without making the same cuts.
- **A gated cross-surface parity matrix.** `docs/surface-parity.md` is generated
  from one maximal record rendered through all eight surfaces, and the
  `surface-parity` gate fails when a surface gains or loses a claim, or a cut
  stops reconciling, without the matrix moving in the same commit. It would have
  caught the 2.15.1 note-count bug, the `--md` roll call, and the MCP fusion gap
  as failing cells.

### Fixed

- **`--md` renders the briefing.** The report had no provider row, so it could
  not answer who handles mail; it listed every insight and related domain as a
  roll call; it ignored `--confidence-mode`; and it titled itself on the
  attacker-controllable `FederationBrandName`. It now leads with the vendor
  roles, cuts the lists with an `--md --full` note, honors the confidence mode,
  and titles on the queried domain with the display name labelled unverified.
- **MCP JSON stops hiding fusion.** The payload advertised `fusion_enabled`,
  `slug_confidences`, and `posterior_observations` and always emitted them empty,
  because the fusion layer ran only on the CLI path. An agent comparing a CLI and
  an MCP lookup of one domain no longer sees the Bayesian layer vanish.
- **`--plain --full` carries the role split.** The complete record, the surface
  the docs tell parsers to use, was the one output missing the 2.15 `mail:` /
  `identity:` keys. They are added additively, before `provider:`.
- **The `--plain` notes count against the flag they name.** A fourth black-box
  pass found the remainders were computed from the panel's curated list but
  printed on the record surface, so shown plus withheld did not equal what
  `--plain --full` prints; a record whose curated list fit the cap printed no
  note at all while still withholding lines; and the related total skipped the
  wildcard and `*.onmicrosoft.*` names that `--full` prints. Each note now counts
  against, and names, `--plain --full`.
- **`provider:` says why it repeats the vendor.** On a role split it keeps its
  `(MX delivery path)` evidence role, the one place the default view does not
  compact a role (ADR-0012), so a screen reader hears a reason for the second
  vendor word rather than a stutter.

### Changed

- `--md` carries a scope caveat out of the terminal (public observations, not a
  licensing, deployment, or security-rating claim), the way `--gaps` already
  does; the report format is the one most likely to land in a deck. `--json` is
  unchanged: machine consumers already receive the structured hedging.
- The MCP text surface compacts service labels and the provider role by default
  (ADR-0012), matching the panel and `--plain`; `format="json"` restores the
  detail.
- A narrower, more readable Markdown escape was tried and reverted when the
  injection tests caught that service labels and insight text carry substrings
  parsed from source records. The full escape stays; the report reads
  `example\.com` when pasted raw, and the defense is worth more than the polish.
- Panel footers use commas rather than em-dashes, matching the house rule.

### Documentation

- ADR-0017 records the one-briefing decision and the SemVer reconciliation:
  which rows a human view selects is a curated briefing that may change in a
  minor release, while the flags, exit codes, and stable schema key names those
  surfaces print do not. 2.15 is the named precedent. `docs/stability.md` states
  the same rule and updates the `--md` and `--domains` rows; the ADR index adds
  0015, 0016, and 0017; ADR-0016 carries a second amendment on the note basis.

## [2.15.1] - 2026-08-17

Default-view follow-through. A third black-box pass against the published
2.15.0 package confirmed the two decisions that release made and found that the
`--plain` half was implemented only halfway: it emitted the panel's rows but
not the panel's cuts, so a populated record still read its entire
related-domain list aloud, and it dropped the one key the guide tells a
stranger to grep. The panel and the linear view now share one definition of
what the briefing shows and what it withholds. No stable JSON, MCP, cache, or
capsule contract changes.

### Tool Surface Changes

Tool surface changes: no command or flag is added, removed, or renamed.
Default `--plain` output gains two keys, `related_domains_note` and
`insights_note`, and restores `provider:` on role-split records; its
`related_domains` and `insights` lists now carry the default panel's selection
rather than every entry, with `--plain --full` unchanged and still complete.
`--plain` now honors `--confidence-mode`.

### Fixed

- **`--plain` makes the panel's cuts, not just its rows.** Default `--plain`
  carries the panel's high-signal related-domain selection and its five-insight
  cap, each followed by a `related_domains_note:` / `insights_note:` key stating
  how many entries were withheld and how to see them. A rich record rendered
  144 lines where the panel rendered 50, so the surface recon documents for
  screen readers turned back into a hostname roll call on exactly the targets
  worth reviewing. `--plain --full` is unchanged and still emits every entry.
- **`provider:` is emitted on role-split records.** ADR-0015 removed the
  singular `Provider` row from the visual panel for good reason, and the linear
  view followed it by dropping the key entirely, which made the documented
  `grep provider:` miss silently on precisely the record class the role split
  exists for. `provider:` now follows `mail:` and `identity:`, carrying the same
  MX-delivery-path summary it carries on every other surface: a top-down reader
  still meets the roles first, and one grep works everywhere.
- **`--plain` honors `--confidence-mode`.** The linear view is the panel, so a
  flag that changes the panel's insight wording changes this too. It previously
  rendered hedged insight text under `--confidence-mode strict`.

### Changed

- The panel says why its two dot rows can disagree. `Confidence` counts
  corroborating sources and `Model support` is threshold-relative, so a
  one-source record can carry a full model display; three consecutive external
  passes read that as a contradiction. When the two scales sit two steps apart,
  the `Model support` row now adds one dim sentence naming them as different
  questions. Records where the scales agree, or differ by one step, are
  unchanged.

### Documentation

- `docs/getting-started.md` names the `--plain` role keys alongside
  `provider:`, describes the note keys, and explains the `Confidence` versus
  `Model support` distinction at first contact rather than only in
  `how-it-works.md`.
- `docs/mcp.md` states the resolved config and cache directories for custom
  profiles and `cached_at` instead of the legacy `~/.recon/` shorthand, matching
  what `recon doctor` prints and what the same document already says for
  custom fingerprints.
- [ADR-0016](docs/adr/0016-plain-emits-the-panel-record.md) carries a dated
  amendment recording the cuts and the retained `provider:` key, and
  `docs/stability.md` describes the `--plain` contract as shipped.

## [2.15.0] - 2026-08-16

Default-view claim clarity and accessibility. Two independent black-box passes
of the published package found that recon's compact surfaces, not its data,
were misreading themselves: the panel named one vendor on a record carrying
two, and the accessibility flag emitted the least accessible output recon
produces. Both are now decided by ADR rather than documented around. A typo in
a flag also no longer reaches the network.

This release renumbers the agent-portability milestone to v2.16. That work is
blocked on third-party client availability and a runtime match, and unrelated
shipped work should not queue behind it. The frozen evaluation contract keeps
its `v2.15` round id, because a preregistration's identity must not move once
frozen.

### Tool Surface Changes

Tool surface changes: `--plain` default output changes shape. It now renders
the default panel's rows as linear `key: value` text; the complete structured
record it emitted through 2.14.x is unchanged and moves behind `--plain
--full`. Key names are the stable schema names either way, so an existing
`grep tenant_id:` still matches. The default panel gains role-labelled `Mail`
and `Identity` rows in place of `Provider`, but only on records where a mail
vendor and an identity vendor genuinely differ. No JSON field, MCP tool,
resource, cache, or capsule contract changes.

### Changed

- The default panel names both vendors, with their roles, when a domain's mail
  vendor and identity vendor differ. Previously the singular `Provider` row
  named the mail vendor and read as though it named the only vendor, while the
  identity vendor appeared solely as an unlabelled tenant GUID. `Services`
  gains an `Identity` row instead of filing the identity observation under
  `Email` with no mail role, and `Model support` names every above-threshold
  tenant-class claim rather than one of two. Single-vendor records render
  exactly as before. The identity role is derived from evidence provenance
  (`OIDC Discovery`, `GetUserRealm`, `Autodiscover`, `Google Identity
  Routing`), not from a slug's catalog category, because that category states
  what a slug usually means rather than what was observed.
  [ADR-0015](docs/adr/0015-role-split-vendor-claims-in-the-default-view.md).
- `--plain` renders the panel; `--plain --full` renders the complete record.
  The accessibility surface previously emitted ~350 lines opening with schema
  keys, so a screen-reader user heard `interval_low` before they heard which
  vendor handled mail. Two consecutive external play-tests reported the
  accessibility path as the hardest path.
  [ADR-0016](docs/adr/0016-plain-emits-the-panel-record.md).
- An unknown `--profile` and an invalid `--explain-dag-format` are rejected
  before collection instead of after it. Both were validated only once the
  lookup had resolved, so a typo spent a full round of DNS and
  identity-endpoint requests against the target before exit 2. An invalid
  `--explain-dag-format` is now also rejected without `--explain-dag`.
- `recon lookup --help` describes `--plain` consistently with the banner and
  the guide.
- The README terminal transcript labels itself a synthetic fixture, so a reader
  who skims past the surrounding prose cannot take it for a captured run.

## [2.14.1] - 2026-08-15

Front-door and silent-failure patch. A black-box play-test of the published
2.14.0 package walked the documented first-run path using only published docs,
`--help`, schemas, and returned output, and found that several published
descriptions did not match the shipped binary. This release makes the
descriptions true, corrects the MCP discovery order an agent reads first, and
closes the fail-open paths found alongside them. No stable contract changes.

### Tool Surface Changes

Tool surface changes: no public recon CLI command, MCP tool, resource, or
stable JSON field is added, removed, or renamed. The MCP `tools/list` response
changes *order only*: `lookup_tenant` now leads and the four ephemeral catalog
mutators are last, so an agent that reads the list top-down meets the
documented starting tool first. Tool names, schemas, and annotations are
unchanged. A maintainer-only network-free validator checks the frozen v2.15
representative-client evaluation contract and its generated, schema-pinned
portable packaging candidate.

### Changed

- MCP `tools/list` advertises `lookup_tenant` first and the four process-wide
  ephemeral catalog tools (`inject_ephemeral_fingerprint`,
  `list_ephemeral_fingerprints`, `clear_ephemeral_fingerprints`,
  `reevaluate_domain`) last. Registration order previously followed the
  alphabetised import block, so an agent selecting the first advertised tool
  met a process-mutating tool while `lookup_tenant` sat sixteenth, the inverse
  of the stderr banner and `docs/mcp.md`.
- `recon doctor` reports the signal catalog as loaded total plus reportable
  subset (`38 signals loaded (36 reportable via \`recon signals list\`)`).
  Two signals carry no public observation label and never appear in
  `recon signals list`; the counts were both correct and looked like a
  discrepancy.
- The panel's `Model support` row names `the Google Workspace tenant` rather
  than `the Workspace tenant`, which read ambiguously on a record that also
  carries a Microsoft tenant GUID.
- The no-argument welcome banner's examples use reserved `example.com` and
  state that every lookup is live and that reserved and `.invalid` names
  publish little or nothing. The previous `.invalid` examples always returned
  an empty panel when run verbatim.
- `--plain` is described as a linear rendering of the full structured record
  rather than of the default panel, which is what it has always emitted.

### Documentation

- The README no longer presents the synthetic Example Industries terminal
  demonstration as the output of `recon example.com`. The illustration is
  labelled generated-not-captured, and the Quick Start states that every
  lookup is live and that reserved names return public residue rather than an
  organization's stack.
- `docs/schema.md` records that `evidence` is emitted on any structured lookup
  that retained evidence, not only under `--json --explain`, and notes that
  default `--json` therefore carries target-owned public values such as the
  OIDC `tenant_id` and the GetUserRealm `FederationBrandName`. The code was
  already the contract; the document described a narrower gate.
- `docs/fingerprints.md`, `docs/how-it-works.md`, `docs/mcp.md`,
  `docs/stability.md`, and the `reload_data` tool description describe the
  config directory as resolved (`RECON_CONFIG_DIR`, else an existing legacy
  `~/.recon/`, else `$XDG_CONFIG_HOME/recon`) instead of hardcoding
  `~/.recon/`. A fresh install reads `~/.config/recon/fingerprints.yaml`,
  which is what `recon doctor` had been reporting all along.

### Fixed

- Scheme URLs with userinfo, including the `host\@other` paste form, are
  rejected instead of looking up the host after `@`.
- Related-domain enrichment no longer lends BIMI VMC, invalid DMARC, TLS-RPT,
  Null MX, or unclassified MX labels to the queried apex.
- The default Email row omits MTA-STS when the fetched policy mode is `none`.
- Unclassified MX evidence no longer emits an empty-string detection score.
- An SPF `redirect=` hop failure no longer marks the origin apex TXT channel
  unavailable or hides already collected SPF evidence.
- IPv4-mapped IPv6 destinations are classified by the embedded IPv4 address.
- Structured MCP tools sanitize validator errors the same way `lookup_tenant`
  already did.
- `--explain` uses stored confidence dimensions and names a tenant-ID conflict
  instead of claiming a minimum that was not the final value.
- Cache-hit lookups reconstruct source status so `--verbose`, `--sources`, and
  `--explain` stay populated.
- `--cache-ttl` rejects negative values with the validation exit instead of
  silently treating every entry as a miss.
- A failed `--chain` or `chain_lookup` seed domain now fails like an ordinary
  lookup instead of returning an empty success.
- A live permissive SPF record (`+all`, `?all`, or no `all`) is retained as an
  observed policy with no strict-SPF credit.
- Sparse insights no longer mention MX or identity when neither was observed.
- Related-domain enrichment results are stored as inventory labels only, so a
  later rematch cannot treat another namespace's DMARC, SPF, tokens, or CT
  as the queried apex, and a failed related DNS lookup cannot mark the apex
  DNS channel unavailable.
- A related namespace's ``SPF record observed`` label is no longer borrowed
  as an apex email-control claim.
- The compact Email row reports a live permissive SPF record as
  ``SPF observed`` instead of omitting it.
- One TXT record can now contribute every unshadowed vendor match, not only
  the first catalog pattern.
- Deprecated IPv6 site-local destinations (``fec0::/10``) are refused by the
  HTTP destination check.
- ``cluster_verification_tokens`` records whitespace and same-apex duplicates
  in ``errors`` instead of returning empty clusters as if those inputs were
  compared and found no shared tokens.
- ``simulate_hardening`` seeds what-if state from the collection-claim view,
  so a retained DMARC or MTA-STS scalar on an unavailable channel cannot
  silently no-op a requested fix.

### Added

- A digest-bound v2.15 agent-portability preregistration pins the Agent Plugins
  v1.0.0 and Agent Skills snapshots, three required clients, five synthetic
  tasks, two complete-surface variants, privacy rules, failure cases, and
  promote-or-defer thresholds before portable-package implementation or client
  collection.
- A deterministic complete-surface candidate under `agents/agent-plugin/`
  generates root `plugin.json` and `mcp.json`, two portable skill forms, package
  documentation, and the Apache-2.0 license from the current native sources.
- A network-free fail-closed validator checks the candidate against byte-pinned
  canonical Agent Plugins v1.0.0 schemas, the frozen contract, exact package
  layout and server launch, portable Agent Skills frontmatter, the 22-tool
  runtime inventory, version parity, size bounds, path containment, duplicate
  keys, and qualified Working Draft claim language. CI checks both generation
  drift and validation before any representative-client collection.
- A private, network-free representative-client preflight now requires the
  exact recon executable intended for desktop-client launch, records exact
  client versions, writes exclusively under the ignored local workspace, and
  starts no session when a frozen gate fails. The first disclosure-safe local
  result stopped with zero sessions because Cursor was unavailable and the
  selected runtime was 2.6.3 rather than 2.14.0.

## [2.14.0] - 2026-08-14

### Tool Surface Changes

Tool surface changes: no public recon CLI command, MCP tool, resource, or
stable JSON field changes. The maintainer-only `validation/scan.py` command
adds `--drift-prior-contract` and requires an explicit `--compare-to` for a
drift round.

### Added

- A fail-closed prior-sample drift preparer and aggregate evaluator bind the
  retained prior result, its catalog and collection regime, the exact eligible
  frame, the current catalog and execution surface, and a four-outcome
  comparison. The evaluator keeps observation-summary drift separate from
  catalog interpretation changes and emits no target identifiers.
- A public drift declaration freezes the 5,199 measured rows from the July 17
  typed baseline, records the three excluded historical validation errors,
  pins the prior and current digests, and prohibits collection until the
  contract and implementation pass protected main.
- An aggregate-only prior-sample drift result closes all 5,199 frozen rows with
  zero unavailable or unmeasured outcomes, no observed-count decline beyond
  the predeclared threshold, explicit disclosure of the catalog-driven
  `subdomain_txt` measurement-surface change, withheld classification
  comparison across unequal catalog digests, and no rule promotion.
- A bounded vendor-seed source freezer retrieves only exact HTTPS pages under
  predeclared provider domains. It disables redirects, credentials,
  compression, and retries; enforces media-type and byte limits; publishes an
  immutable private receipt atomically; and prints only counts and digests.
  The vendor-seed preparer now requires that receipt and rejects source
  metadata or archive substitution before it can freeze a target frame. The
  measurement admits only release-bound built-in catalog slugs, excluding
  operator-local custom and process-local ephemeral fingerprints.
- A fail-closed vendor-seed contract preparer and aggregate evaluator bind
  provider-controlled source archives, disjoint private holdout membership,
  prior-frame exclusions, catalog slugs and record types, scan results, and the
  pooled catalog aggregate. Public output contains provider-level
  corroborated, observed-silent, unavailable, unmeasured, and error counts plus
  Wilson intervals, never target identities.
- A public vendor-seed protocol declaration fixes the relationship label,
  denominator, disclosure floor, exclusion rules, and non-recall
  interpretation. Its final provider source plan, immutable receipt,
  17,952-namespace exclusion union, receipt-bound dossier, and 33-row disjoint
  HubSpot frame were frozen with aggregate pre-collection commitments before
  target contact.
- An aggregate-only vendor-seed result closes the 33-row HubSpot holdout with
  29 corroborated, 4 observed-silent, and zero unavailable, unmeasured, or
  error outcomes. It records the 0.878788 relationship-corroboration rate,
  Wilson interval, exact result and reducer commitments, and explicit decision
  to promote no rules without publishing target identifiers.
- Six provider-documented regional-round catalog additions across Cloudflare
  Email Service, Hostinger DNS, Hostinger Email, Locaweb Email, OVHcloud Email,
  and Titan Mail. The 16 new detections have current primary references, review
  dates, scoped claim boundaries, positive fixtures, lookalike negatives,
  sparse fixtures, and provenance assertions.
- An aggregate-only regional-round result records the complete 1,000-row
  baseline, five-stratum classification rates, explicit candidate
  dispositions, accepted fixed-observation zero-regression decision, and
  complete clean protected-main replay.
- Four provider-documented catalog families from the frozen rank round:
  Cloudflare Email Routing MX, Alibaba Cloud DNS NS, Alibaba Cloud Application
  Load Balancer CNAME, and Yandex 360 for Business MX and SPF. Every rule has a
  current primary reference, review date, claim boundary, positive fixture,
  lookalike negative, sparse fixture, and provenance assertion.
- A disclosure-safe fixed-observation evaluator separates additive catalog
  uplift from public DNS drift between live passes. It binds the frozen round
  membership, result digest, candidate catalog, and promotion budget and emits
  aggregate counts only.
- A no-network regional-frame preparer freezes equal secret-keyed discovery
  quotas across ccTLD-delegation groups, commits source and implementation
  digests, excludes declared prior corpora, and makes the non-geolocation
  interpretation boundary explicit before target contact.
- A bounded regional-source freezer archives the exact official IANA root-zone
  and UN M49 English-table responses, derives their ASCII ccTLD intersection,
  and commits raw-source, mapping, and implementation digests without
  contacting any sampled namespace.

### Changed

- The 1,000-row, four-band catalog rank round is closed with an aggregate memo,
  explicit promoted, rejected, deferred, unavailable, and unmeasured outcomes,
  and a zero-regression counterfactual.
- The regional round now has a public pre-collection declaration binding its
  official source archives, exact IANA and UN M49 mapping, independent
  five-stratum frame, collection options, code and catalog digests, and
  aggregate-only interpretation boundary. Its baseline, candidate disposition,
  fixed-observation decision, and protected-main replay are complete. The
  vendor-seed measurement protocol, bounded source acquisition, receipt
  binding, preparer, evaluator, exact disjoint frame, protected-main collection,
  aggregate reduction, and candidate dispositions are complete. The 5,199-row
  frozen-sample drift collection, aggregate reduction, measurement-surface
  disposition, and zero-promotion decision are also complete.

### Fixed

- GitHub now renders every diagram and equation in the correlation guide. The
  documentation gate rejects Mermaid style names that collide with parser
  keywords and math macros that GitHub replaces with visible error panels.
- The validation guide uses package-safe module entry points for every active
  catalog preparation command, with a subprocess regression gate that launches
  each documented preparer from the repository root.
- The vendor-seed scan command now passes its frozen minimum-occurrence
  threshold explicitly, with a semantic regression test that keeps the
  published invocation aligned with fail-closed manifest preflight.
- Local package-invariant builds and isolated MCP compatibility environments
  use uv copy mode so cloud-backed or cross-device Windows caches cannot fail
  on incompatible hardlinks. Artifact contents, compatibility semantics, and
  release build commands are unchanged.
- The MCP compatibility harness uses the current asynchronous-generator type
  annotation required by Python 3.14 static analysis.

## [2.13.0] - 2026-08-13

### Tool Surface Changes

Tool surface changes: adds the `recon capsule capture`, `replay`, and `compare`
CLI commands plus a separate observation-capsule JSON Schema. No MCP tool,
resource, or stable lookup JSON field changes.

### Added

- Caller-owned, integrity-bound observation capsules record collection
  windows, source opportunities, retained normalized facts, collection options,
  cache and vantage metadata, interpretation-version digests, stable signal
  identifiers, and a deterministic SHA-256 content digest generated by recon.
- `recon capsule replay` verifies and re-renders a capsule without network
  access. `recon capsule compare` separates observation, collection-regime,
  time-evaluation, and interpretation changes, and withholds fact changes for
  source roles that were partial or unavailable at either endpoint.
- A separate Draft 2020-12 capsule schema ships in the documentation and wheel,
  with independent validation, deterministic replay, degraded-source,
  integrity, bounded-input, symlink, no-clobber, and CLI regression tests.
- ADR-0014 defers an Open Knowledge Format v0.2 projection until a named
  consumer can justify the provenance, trust, lifecycle, freshness, and privacy
  mapping. Versioned recon JSON remains authoritative, and Agent Plugins
  packaging remains a separate later decision.

## [2.12.0] - 2026-08-13

### Tool Surface Changes

Tool surface changes: no CLI command, flag, MCP tool, resource, or stable JSON
field changes. The v2 implicit fusion behavior remains enabled for
compatibility, while interactive omission now receives a transition notice;
explicit `--fusion`, `--no-fusion`, and `--explain-dag` behavior is unchanged.

### Added

- A network-free structural-identifiability gate exhaustively checks all 64
  M365 DNS evidence-role states through the shipped scoring, observation, and
  Bayesian paths before any private evaluation can contact targets.
- ADR-0013 records the fusion non-promotion decision, the v2 compatibility
  transition, and the v3 major boundary for changing the omitted CLI choice.

### Changed

- The v2.11 M365 live evaluation is cancelled before target contact. Its frozen
  arms collapse into two decision pairs and A3 is structurally dominated by
  A0, making the preregistered positive-benefit condition unreachable. The
  dated memo and amendment preserve this negative design result.
- Fusion is now positioned as an advanced diagnostic. v2 preserves the stable
  implicit enabled CLI behavior, warns only interactive omitted choices, keeps
  redirected and machine output silent, and asks operators to pass an explicit
  flag before v3. Ordinary MCP lookup remains deterministic, while the existing
  `get_posteriors` and `explain_dag` tools remain the explicit advanced path.
- The roadmap now assigns the actual default-off switch to v3 instead of
  violating the documented stable-default policy in v2.12. The next build
  milestone is the v2.13 observation capsule and OKF v0.2 projection decision.

## [2.10.4] - 2026-08-13

### Tool Surface Changes

Tool surface changes: no CLI command, flag, MCP tool, resource, or stable JSON
field changes.

### Added

- A blocking independent Draft 2020-12 interoperability gate now loads both
  published schema copies, rejects external or unresolved references, enforces
  explicit structure and time bounds, and validates a production-formatted
  record plus a required-field negative control with `jsonschema`.
- `validation/characterize_live_quality.py` measures the real single-domain
  path, warm disk and MCP paths, allocation, degradation, and paired CT value
  without emitting identifiers or per-domain rows. The first reviewed
  aggregate completed 50 of 50 no-CT attempts and 47 of 50 CT attempts and is
  published with its limits rather than treated as population evidence.
- The v2.11 evaluation now has a public Tranco-derived frame declaration, a
  private HMAC-SHA-256 frame commitment, an immutable eligibility window, and a
  fail-closed preparer that performs no target collection. The reference label
  requires concordant Microsoft identity endpoints, and collection remains
  blocked until the declaration is public and the window opens.

### Changed

- The README terminal example now uses the reserved `example.com` namespace and
  a richer fictional service mix, making the demo immediately recognizable as
  a domain-intelligence result while preserving deterministic, no-network
  generation and an accessible text transcript.
- The roadmap and strategic gap audit now distinguish completed maintenance
  gates from the next decision-bearing v2.11 work, place the v2.12 fusion
  application directly after that decision, and track Agent Plugins v1.0.0 and
  Open Knowledge Format v0.2 as additive future interoperability work without
  claiming current conformance.
- The locked direct patch set now uses Typer 0.27.1, Hypothesis 6.165.5,
  pre-commit 4.6.2, and Ruff 0.16.2. No direct runtime or development dependency
  reports a newer release in the final pre-release inventory.

### Fixed

- Related-domain inventory enrichment now reprojects final insight claims
  against apex collection availability, so retained but degraded evidence
  cannot support a claim and newly relevant retained apex evidence is attached
  exactly. The narrow pre-enrichment sparse-scope exception remains preserved.
- Cached claim evidence now accepts the model's valid empty catalog slug for
  typed non-catalog observations instead of rejecting an otherwise exact cache
  round trip.

### Security

- The mutation-testing environment now resolves GitPython 3.1.59 instead of
  3.1.57, incorporating the upstream option, clone-directory, and configuration
  parsing hardening that superseded the already-green 3.1.58 Dependabot update.
  The runtime package surface is unchanged, and the locked environment passes
  strict dependency audit with no known vulnerabilities.

## [2.10.3] - 2026-08-07

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes. The default human views
render service and provider labels without their evidence-role qualifier and
omit matches with no established role; `--explain`, `--verbose`, and `--full`
restore both, and `--json`, `--csv`, and the MCP payloads are unchanged.

### Added

- `scripts/check_doc_rot.py` is a new blocking gate stage rejecting Markdown
  that renders silently wrong on github.com: LaTeX `\(` and `\[` delimiters the
  renderer treats as escaped literal brackets, unclosed `$$` display blocks, and
  sections hollowed out into pointers that redirect the reader without carrying
  content. It runs in `scripts/check.py` and CI, and it found one live defect on
  its first run.
- `scripts/quality_scorecard.py` emits the Phase 1 product-quality baseline as
  one dated, revision-bound, aggregate-safe artifact. It is network-free and
  corpus-free, and it is a diagnostic rather than a gate. It measures the one
  Phase 1 quantity with no existing owner, MCP context cost, names the owner for
  quantities other harnesses already produce, and records the rest as unmeasured
  with the reason. The first run reports 22 tools costing 91,876 bytes of
  session context before any call, 63.9 percent of it output schemas, and 26 of
  1,070 detection rules carrying a verification date.
- `docs/quality-baseline-preregistration.md` freezes the v2.11 product-quality
  decision rule before any collection or run: the primary claim family selected
  by elimination, four arms pinned to code paths, the channel-split reference
  label and its named common-cause limit, both estimands, the paired
  Clopper-Pearson rule with a 0.02 safety margin, and the disclosure boundary.
- `validation/quality_power_analysis.py` reproduces the preregistration's power
  analysis with exact Clopper-Pearson bounds and no third-party dependency. It
  shows the nominal 30-unit negative floor supports no margin tighter than
  0.1157, and fixes the required sample at 155 reference-positive and 183
  reference-negative labeled units.

### Fixed

- `recon mcp doctor` no longer reports a cleanup error in place of the
  handshake failure that caused it. The server is spawned with an empty
  tempdir as its cwd, and on Windows that directory stays locked until the
  child has fully exited, so tearing the transport down after a failed
  handshake could raise `PermissionError: [WinError 32]` out of the tempdir's
  own cleanup and overwrite the diagnosis with it. Cleanup of that isolation
  boundary is now best-effort; the cwd-shadow defense it exists for is
  unchanged. Seen as an intermittent Windows CI failure in
  `tests/test_mcp_doctor.py`, with a platform-independent regression test.
- `docs/statistical-assurance.md` rendered its signed marginal entropy formula
  as literal bracketed LaTeX rather than math, so github.com printed the raw
  expression between plain brackets. Same defect class as the
  `docs/correlation.md` repair, in a file that repair did not touch, found by
  the new doc-rot gate on its first run.
- The scheduled provider-drift gate no longer asserts that a reserved domain
  carries a third-party Microsoft 365 tenant. `example.org` lost its tenant
  registration, GetUserRealm answered `NameSpaceType: Unknown`, and the gate
  read that stable negative as an unhealthy source. The identity check now
  compares recon's parse against the raw GetUserRealm response and asserts the
  provider still returns the `NameSpaceType` field recon depends on, so it
  catches contract drift without tracking tenant churn. No shipped behavior
  changed: `SourceResult` already recorded the negative with
  `source_unavailable` false, and that field is what merge and delta consume.
- The default human views no longer repeat an evidence-role qualifier on every
  service and provider label. `Slack (public TXT account indicator)`,
  `Okta (CNAME endpoint binding)`, and `Microsoft 365 (MX delivery path)` now
  read as `Slack`, `Okta`, and `Microsoft 365` on the default panel, `--plain`,
  `--md`, and the `--chain` tree, with one dim line naming the flag that
  restores the detail. `--explain`, `--verbose`, and `--full` are unchanged, as
  are the `--json` record (including the stable `provider` field), `--csv`, and
  every MCP payload. A match whose role could not be established is omitted
  from the default view and counted in that line rather than rendered as a bare
  vendor name, so removing the qualifier never upgrades a claim; the provider
  row re-hedges as `(no supporting record)` instead of dropping, and the
  downstream and unobserved-gateway hedges survive in shortened form. Recorded
  in [ADR-0012](docs/adr/0012-default-view-evidence-role-visibility.md), which
  also restates the renderer obligations on the `runtime.service-label.v1` and
  `runtime.email-topology.v1` claim families.
- Insight curation moved out of `formatter/panel.py` into
  `formatter/insight_curation.py`. It is editorial policy over insight strings
  rather than rendering, it depends on nothing else, and the move ratchets the
  panel module's file-size ceiling down from 1719 to 1615 lines. No behavior
  change.

## [2.10.2] - 2026-08-04

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Fixed

- MCP text tools (`lookup_tenant`, `chain_lookup`, `explain_dag`) now raise
  `ToolError` on rate-limit and lookup failures so FastMCP marks `isError`
  instead of returning error prose as successful tool content.
- CertSpotter partial pages cut short by HTTP 429 retain partial CT data and
  mark the provider degraded via `CertProviderPartialRateLimit` instead of
  looking like a complete CT success.
- Soft-empty CT provider responses add the provider to `degraded_sources`
  rather than reading as observed-empty certificate history.
- BIMI VMC probe transport failures mark `http:bimi_vmc` degraded; Autodiscover
  XML parse failures mark `identity:autodiscover` degraded instead of empty
  domain lists.
- Default batch panel mode prints a completion footer (`ok · failed · total`)
  while keeping the record-oriented exit-code contract.

### Changed

- Root roadmap now states a clear version path from the v2.10.x maintenance
  line through v2.11 quality baseline, later 2.x application stages, and v3.0
  contract maturity, without calendar estimates.

## [2.10.1] - 2026-08-04

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Security

- Upgraded locked transitive dependencies that Scorecard and `pip-audit`
  reported as vulnerable: `cryptography` 49.0.0 to 50.0.0 (via MCP / PyJWT),
  `gitpython` 3.1.54 to 3.1.57 and `aiohttp` 3.14.1 to 3.14.3 (via the
  mutation-group Cosmic Ray stack). Refreshed the ClusterFuzzLite frozen
  requirements export to match.

### Changed

- Tightened the README around install, the Globex Ltd / `globex.invalid`
  terminal demo, and MCP or skill agent usage examples, while restoring the
  documentation contract anchors for onboarding, install helpers, surface
  inventory policy, and research decision links.

## [2.10.0] - 2026-08-01

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Changed

- Added a fail-closed default-claim audit that assigns every discovered primary
  panel, JSON, MCP, generated-guidance, recommendation, and score surface to a
  machine-readable claim family. The local and CI gates now reject new or stale
  surfaces, malformed family states, incomplete families marked complete,
  escaped or role-inappropriate repository references, and unreviewed JSON or
  MCP surface-set changes. All 27 claim families are now complete, with no
  material runtime family carrying incomplete lineage. The final static review
  aligns shipped agent guidance, live MCP instructions and tool descriptions,
  generated surface inventory, and current SDK adoption docs with exact
  process scope, collection boundaries, output forms, cache behavior, score
  limits, and abstention rules. Focused contract tests reject stale session
  semantics, simplistic confidence formulas, invented payload-size bounds,
  related-namespace ownership claims, and obsolete production dependency text.
- Built-in generated insights now retain the exact emitting rule and either
  supporting evidence occurrences or bounded observation scope at generation time.
  Collection projection and related-domain enrichment regenerate those
  associations from only reportable evidence, CLI and MCP explanation paths
  consume them before legacy text reconstruction, and result-cache version 4
  persists them. Older result-cache versions miss cleanly instead of serving
  insight strings without their generation-time associations. Positive catalog
  and service insights now abstain without a retained occurrence, preventing
  related-domain inventory from becoming an apex claim or declarative signal.
  Canonical observation scopes fail closed for degraded collection, including
  Autodiscover and OIDC metadata subchannels; email-control observations cannot
  coexist with the no-email observation; and cache reads and writes reject
  missing, duplicate, or inconsistent generated-insight lineage without
  dropping valid degraded results. Gateway explanations now attach only the MX
  records that established the gateway role, related sender-platform inventory
  remains isolated even for an evidence-empty apex, and malformed role labels
  cannot escape the best-effort cache boundary.
- Explanation terminals now report whether their rule association is exact,
  exact-rule-only, reconstructed, or unsupported. Explained JSON adds
  `exact_provenance_complete` and `lineage_disconnected_terminals`, which
  require an explicit evidence-to-rule path, while preserving the stable
  schema-version-1 reachability diagnostics. Exact generated insights and
  simple positive signal or posture rules expose retained rule identity;
  metadata-dependent, bounded non-observation, legacy text, confidence, and
  proxy-matched paths remain visibly incomplete or reconstructed. Flat JSON,
  Rich, Markdown, CLI, and MCP explanation renderers carry the same status.
- Exposure assessments now carry a complete nine-component evidence ledger
  with exact retained evidence, metadata dependencies, observation scope, and
  explicit observed, unresolved, unavailable, or hypothetical states. The
  compatible public-evidence score is the ledger's evidence-backed floor;
  structured and panel output also expose its ceiling, unresolved capacity,
  current 90-point model maximum, and both ledgers in comparisons. Hardening
  simulations distinguish hypothetical arithmetic from observed evidence, and
  contradictory or evidence-empty positive inputs fail closed without credit.
- Sparse public-signal diagnoses now use colon punctuation consistently. The
  text-hygiene gate compares an ahead branch's effective working tree with
  `origin/main`, so a local repair supersedes the corresponding unpushed line
  instead of producing a stale historical violation. The explanation refactor
  also lowers the enforced excessive-branch ceiling from 10 to 8.
- Default Rich panel assembly now uses the queried namespace as its subject
  coordinate instead of substituting a differing tenant default domain; an
  observable differing value remains available as an explicit `Tenant domain`
  fact. Failed Autodiscover collection now masks a stale cached default domain
  back to the queried namespace across Rich, MCP text, JSON, and Markdown.
  Multi-cloud summaries consume only collection-observable endpoint-binding
  evidence, so a failed CNAME channel cannot create a workload-provider claim
  from retained raw provenance. The panel and MCP text assemblers now have
  explicit producer, evidence, and regression paths in the default-claim audit.
- Service rows now state the bounded role established by retained public-record
  evidence, including MX delivery paths, CNAME endpoint bindings, SPF sender
  authorization, DMARC report destinations, SRV discovery, DNS delegation,
  CAA authorization, and TXT account indicators. Missing or incompatible
  catalog lineage renders as unavailable, degraded channels cannot supply a
  role, and normalized gateway names retain their source role. Stable delta
  JSON and terminal output continue to expose canonical service names.
- Posture observations now retain the exact rule that emitted them, the
  branch-local public-record occurrences used by slug conditions, and typed
  values for every metadata predicate. Optional explanations consume that
  generation-time state instead of borrowing matching evidence globally.
  CLI and MCP profile paths now share the same profile-relative expectation
  behavior, preserve lineage while reweighting, and withhold absence-shaped
  expectations whenever collection is degraded. Built-in rule identities take
  precedence over colliding custom names, and later duplicate custom rules are
  skipped so explanations cannot bind an observation to another definition.
  The synthetic `profile:` identity namespace is reserved and cannot be used
  by custom posture rules.
  The stable four-field posture output remains unchanged, profiles remain
  lenses rather than scores, and the shared predicate evaluator lowers the
  enforced excessive-return ceiling from 22 to 21.
- Hardening review prompts now retain and expose exact generator IDs, explicit
  basis states, satisfied typed metadata predicates, canonical bounded scopes,
  and branch-local evidence. Observed weak configurations and compound
  inconsistencies require retained raw support that agrees with derived scalar
  state, bounded absences require a successful collection opportunity, and
  common-selector DKIM remains explicitly unresolved. Invalid or ambiguous
  DMARC material remains an evidence-backed review prompt with a distinct
  basis. MTA-STS guidance keeps its DNS activation and conditional HTTP policy
  scopes distinct,
  multi-gateway prompts retain every contributing MX record, and hardening
  simulations replace superseded control evidence before re-evaluation.
  Unavailable channels emit no absence prompt. Terminal output labels each
  basis and includes the passive-observation disclaimer; the older
  `absence_confirmable` field remains available for compatibility.
- README now embeds a crisp terminal image generated by the real default panel
  renderer from a deterministic reserved-namespace fixture. The self-contained
  SVG contains no external font request or real organization data, and local
  plus CI drift checks keep it synchronized with renderer behavior.
- Refreshed the locked runtime and development stack, migrated the repository
  to its current Ruff formatter, enforced formatting in local and CI gates,
  and advanced every Dependabot-proposed GitHub Actions pin to its reviewed
  full commit. Typer 0.27 narrow help remains within 40-column terminals,
  surface inventory keeps stable dependency-independent type names, and the
  frozen ClusterFuzzLite runtime export is synchronized with the lock through
  a platform-canonical command header.

### Security

- MTA-STS collection now follows the exact RFC 8461 boundary. Only one
  syntactically eligible `_mta-sts` record can trigger the policy request, the
  request never follows redirects, and only a direct HTTP 200 `text/plain`
  response with a complete bounded policy can produce a mode. Invalid UTF-8,
  oversized bodies, missing required fields, malformed MX patterns, ambiguous
  declarations, and unrelated redirected content now fail closed.
- `recon update` now refuses `uv` or `pipx` resolved anywhere below the current
  workspace, closing the nested relative-PATH variant of the existing
  current-directory launcher guard.
- Maintainer-only paid-provider validation now uses an optional exact-root,
  lockfile-hashed dependency group. Its CLIs accept credentials only from
  provider-specific environment variables and safely refuse `--api-key`
  without echoing a supplied value into diagnostics.

## [2.9.0] - 2026-07-31

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Changed

- Production now runs the MCP v2 SDK, so recon serves the 2026-07-28 protocol
  revision. This is what makes recon reachable from a modern-only client: the
  spec's own compatibility matrix says a modern client against a legacy server
  fails, and `server/discover`, per-request `_meta`, `resultType`, and cache
  hints all come from the SDK. A v2 server still answers the legacy
  `initialize` handshake, so existing clients on 2025-11-25 keep working, and
  recon's compatibility gate verifies that rather than trusting it. 1.28.1
  remains the documented rollback pin and stays blocking in the matrix, so both
  generations keep being exercised.
- The optional remote adapter runs on both SDK generations instead of refusing
  anything but v1. Two things had to move: the read-only allow-list read
  `annotations.readOnlyHint`, which does not exist on v2, so every tool looked
  non-read-only and the remote surface would have come up empty; and the
  transport options moved from a mutable `settings` object to keyword arguments
  on `streamable_http_app`. Both differences are resolved once in
  `sdk_compat` rather than at the call sites.

### Fixed

- A Google CSE probe failure now stays an unavailable channel instead of
  reporting no CSE configured, so a transport error cannot become a negative
  observation.
- A degraded email channel can no longer become a weak-email-security posture
  claim. The score counts observed controls, so an unread channel dragged it to
  zero and fired the weak-posture observation off a collection gap. The same
  rule exists separately on the signal path and both are now pinned.
- Parent-platform presence no longer becomes a child-product use claim through
  a TXT verification token: the role-establishing record requirement is now
  enforced for both the module and infrastructure insight paths.
- A dormant provider slug alone no longer produces an email security score. A
  tenant discovered through identity endpoints with no mail configuration
  rendered "Email security 0/5", which reads as configured but badly secured
  rather than not measured.
- `chain_lookup` over MCP clamped depth with a literal `3` instead of the
  shared `MAX_CHAIN_DEPTH`, so the two copies of that bound could drift apart
  silently. Depth also scales the aggregate timeout.

### Changed

- The result-cache poison table asserted nothing. Every one of its twelve rows
  wrote a payload for one domain into another domain's cache file, so
  `cache_get` rejected on the domain binding before reaching the field under
  test. Re-keying the rows made all twelve real and immediately caught a
  range check that had never been exercised. A control row now fails if the
  table goes vacuous again.
- `recon fingerprints`, posture, chain-depth, and Google CSE invariants that
  were enforced in code but named by no test are now pinned by tests verified
  to fail when the guard is removed.

## [2.8.0] - 2026-07-31

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Fixed

- The MCP doctor read server identity from a top-level `serverInfo` field. The
  2026-07-28 revision moves it into `_meta` under
  `io.modelcontextprotocol/serverInfo`, so `recon mcp doctor` printed a bare `?`
  for a server that was identifying itself correctly. Both locations are now
  accepted.
- The MCP server set no application version, so under the 2026-07-28 SDK it
  advertised an empty version string and a client could not tell which recon it
  was connected to.

### Changed

- The MCP compatibility gate gained five wire-level probes for the 2026-07-28
  requirements, so they rest on recon's own evidence rather than on SDK release
  notes: dual-era `initialize` serving, `-32602` for a request missing the
  required `_meta` envelope, `-32022` with the supported-version list for an
  unsupported version, `-32602` rather than the retired `-32002` for an unknown
  resource, and a `server/discover` payload carrying instructions and server
  identity. All pass on the 2.0.0 SDK; the legacy-era probes report
  not-applicable on 1.28.1 rather than passing vacuously.
- Tool annotations are built in one place rather than at each of the 22
  registrations. The two SDK generations spell the fields differently, and
  passing the newer spelling to the older one does not raise: it stores an
  unrelated extra attribute and leaves the real hint unset. Centralizing the
  spelling that both generations read removes that trap from a future migration.
- The ephemeral fingerprint tools now state that their state is scoped to the
  whole server process rather than to one conversation, which is what MCP
  2026-07-28 assumes when it says a stdio process is not a session.
- Production stays on the v1 MCP SDK. An adoption review ran the v2 pin end to
  end: the stdio server is clean on 2026-07-28 and the full matrix passes, but
  `build_remote_application` refuses any family but v1, so the pin change would
  disable the optional remote adapter rather than degrade it. The evidence and
  the remaining steps are recorded in `docs/mcp-2026-07-28-readiness.md`.

### Security

- `recon update` now resolves `uv` and `pipx` to an absolute path and refuses a
  launcher found in the current working directory. Windows resolves a bare
  program name against the current directory before `PATH`, so running
  `recon update` from a directory an attacker could write to executed a planted
  `uv.exe` or `pipx.exe` as the operator. An unresolvable launcher now degrades
  to the printed manual command, and the manual hint is correct per install
  method instead of always suggesting pip.
- The regex safety heuristic now counts `?` as an inner repetition operator, so
  a nested-quantifier pattern such as `(a?){50}a{50}$` is rejected from operator
  fingerprint and signal files. Counting only `+`, `*`, and `{` admitted it, and
  49 subject characters were enough to backtrack past a minute, far below the
  pattern-length cap that was assumed to bound whatever the heuristic misses.
  The `?` that opens `(?:`, `(?=`, and `(?i)` is still not a quantifier, so
  ordinary non-capturing groups stay accepted; all 1,008 catalog patterns remain
  valid. `docs/security.md` no longer claims the length caps bound this class.
- The release workflow pins `pip-audit`, the last unpinned software install
  across the workflows, and the CI text-hygiene step passes event fields through
  `env` rather than expanding them into the script body.

### Fixed

- GetUserRealm answers HTTP 200 with `NameSpaceType: Unknown` for any domain
  with no Azure AD tenant. That successful negative answer was accepted as an
  auth type, so nearly any domain reported a Microsoft 365 detection and
  persisted an `auth_type` outside the `Federated`/`Managed`/null contract that
  `recon delta` then rejected. Only tenant-positive values are accepted now.
- `recon batch -` decoded piped input with the platform default codepage. On
  Windows a UTF-8 domain list mojibaked into a different registrable domain and
  was looked up with exit 0. Both the stdin and file paths now decode UTF-8 and
  strip a leading byte order mark.
- `--exposure` and `--gaps` wrote CT-degraded (`--no-ct`) and probe-derived
  (`--direct-probes`) results into the shared default-scope result cache, so a
  later full lookup could be answered from a degraded entry. They now apply the
  same scope rule as a standard lookup.
- `recon cache clear <domain> --all --force` cleared the entire cache: the
  `--all` branch ran first and ignored the domain. The pair is now refused, as
  `cache clear` with no arguments now reports to stderr like its siblings.
- `--include-unclassified` reported an empty catalog on any cache hit. The
  per-record-type summaries and unclassified observations are now cached
  alongside the chains, so a cache hit no longer reads as "nothing
  unclassified" rather than "not measured".
- `recon batch --md` silently discarded invalid domains: no stdout, no stderr,
  exit 0. Every output mode now accounts for every input row.
- `recon delta` could never report `changed_email_security_score`. The score is
  derived rather than stored, so reading it from the cache export always found
  nothing; it is now derived from the same projected snapshot the other
  comparisons use.
- `recon delta` reported removals a prior run never observed when that run's
  identity source had failed. Identity markers are source names rather than
  observation channels, so they escaped the masking gate that channel markers
  hit.
- `recon fingerprints new --output <bad path>` reached the crash handler and
  exited 4 with a crash log. A bad output path is operator input and now exits 2
  with a clear message, creating missing parent directories like
  `discover --output` already did.
- `recon doctor --mcp` and `recon mcp install` printed diagnostics on stdout
  beside the JSON, so the config could not be piped. Diagnostics now go to
  stderr.
- `lookup_tenant`, `explain_dag`, and `chain_lookup` returned error-shaped
  success payloads on invalid input instead of raising a protocol error, so a
  connected model could not self-correct through the protocol's own error
  channel. They now match the contract their sibling tools already followed.
- `--plain` silently ignored `--explain` and `--posture`, which made the screen
  reader and grep path the only output mode that could not show evidence.
- `--depth` outside the documented range of 1 to 3 was silently clamped, so
  `--depth 99` exited 0 having run a traversal that was never requested.
- `recon batch --include-ecosystem` built every shared-slug pair before
  truncating to the output cap, which is quadratic in domains: 4,000 domains
  produced 3.5 million intermediate edges and 929 MiB. The candidate scan is now
  bounded, and the bucketed builders iterate in sorted order so their selection
  is unchanged.
- `--chain` alphabetized each domain's insight list, demoting the deliberately
  first "Conflicting tenant IDs detected" warning. Correlation lines are now
  appended instead.

### Changed

- An MTA-STS policy fetched with RFC 8461 `mode: none` no longer counts as a
  present control. That mode means the policy is not in effect, so a domain that
  published and then disabled MTA-STS scored the same as one enforcing it and
  raised no hardening gap, while `mode: testing` correctly did. It now scores 0,
  reports `present=False` with a detail saying the policy is not in effect, and
  raises a medium-severity gap. `mta_sts_mode` still reports `none`, so the
  observation stays visible. This can lower `email_security_score` by one for
  affected domains, including across a delta.
- The README is rebuilt as a front door rather than a specification: install and
  first lookup, what recon is good for, the command set, the JSON and MCP
  contracts, limitations, and where to read more. Cache bounds, catalog search
  semantics, batch scheduling, summary schema versions, packaging internals, and
  the catalog-round detail now live only in the docs that own them, which also
  removes a duplicated network-disclosure paragraph and a third copy of the
  roadmap. A security-reporting section and a link to the stability policy were
  missing entirely and are now present.
- `docs/README.md` is grouped by audience, so a visitor sees the using and
  integrating sections before maintainer planning and research documents.
- Three documents each claimed a different, stale current catalog size. They now
  agree with the generated catalog at 860 entries, 683 unique slugs, and 1,070
  detections, and a test keeps the prose tied to the artifact.
- `cache.py` and `exposure.py` were split along existing seams into
  `cache_catalog.py`, `exposure_gaps.py`, and `exposure_copy.py`, lowering the
  `exposure.py` size ratchet from 858 to 637 lines.

## [2.7.0] - 2026-07-29

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Added

- An opt-in, stateless Streamable HTTP MCP adapter for operators who need
  authenticated remote access. The adapter exposes only the reviewed read-only
  tools and resources, supports either application bearer authentication or a
  trusted authenticated platform boundary, and enforces request, Host, and
  Origin guards. The local stdio MCP server remains the default.
- A non-root OCI container, a draft Terraform module for Google Cloud Run, and
  a cross-platform deployment plan covering AWS, Azure, Google Cloud,
  Cloudflare, Kubernetes, generic OCI hosts, Anthropic clients, and OpenAI
  clients. These artifacts are optional, directionally useful starting points,
  not provider-validated production templates.

### Changed

- MCP compatibility now runs against both SDK 1.28.1 and stable 2.0.0 in CI
  and the release gate. The published dependency remains on the stable v1 line
  until a separate production-adoption decision.

## [2.6.14] - 2026-07-26

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Added

- Six apex verification-TXT detections promoted from one private
  5,199-namespace round, each with a vendor-named prefix, a vendor-owned
  reference, a verification date, and a lookalike-negative fixture: IBMid
  (95 namespaces), Infoblox (139), Cisco Intersight (130), ElevenLabs (63),
  QuoVadis (50), and Trend Micro Email Security (43). All six pass the
  pattern-specificity gate with zero matches against the adversarial corpus.
  The IBMid and Trend Micro rules attach to slugs that already existed, so
  they add a second and fourth evidence path rather than a new claim; the
  other four are new vendor entries.

### Fixed

- A wildcard TXT zone no longer reports every probed vendor at once. The
  subdomain probe asks several unrelated owners in one pass, and three catalog
  patterns accept any non-empty value, so a zone answering every owner with the
  same unrelated record matched all three and was reported as running Slack,
  GitLab, and GitHub Advanced Security simultaneously. Across one private
  5,199-namespace round those three fired on 272, 342, and 244 namespaces from
  identical values that were a certificate-authority verification token, an SPF
  record, and a mail hostname. An answer set returned for more than one owner is
  now treated as carrying nothing specific to any of them and is recorded as an
  unclassified observation. A genuine token, and two distinct tokens at two
  owners, still attribute normally.

## [2.6.13] - 2026-07-25

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Fixed

- A queried domain no longer reports email controls that only a related
  domain publishes. Related-domain enrichment merges a related namespace's
  detections into the queried record, and an email-control label asserts that
  the queried namespace publishes that record, so the union must not carry one
  across. The claim-safe projection was computed and then used only for the
  insight arguments, while the stored services and slugs kept the raw union. A
  domain whose related namespace published DMARC, DKIM, SPF, MTA-STS, and BIMI
  therefore reported all five as its own while its own `dmarc_policy` stayed
  null and its email-control count stayed zero, so one record contradicted
  itself. The borrowed slugs also reached signal evaluation and the panel's
  email summary, and were written to the result cache. Non-control detections
  are inventory labels rather than record claims and still merge, so
  enrichment keeps working as intended.
- The generated-schema gate compares committed bytes rather than parsed
  objects. It read both sides through `json.loads`, so it accepted any file
  that merely parsed to the same object: a reserialization with different
  indentation, key order, or separators passed while the committed bytes were
  stale, and the very next `--write` rewrote them. The sibling generators for
  the surface inventory and the fingerprint catalog already compare text. This
  gate now compares text as well, and additionally requires the documented
  schema and the packaged one to be byte-identical, since they are one
  contract.

## [2.6.12] - 2026-07-25

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Security

- The pattern-admission gate rejects a quantified alternation whose branches
  overlap by character class, not only by literal prefix. A branch that is a
  wildcard, a shorthand class, or a character class shares no prefix with its
  siblings while matching the same characters, which is what makes the group
  partition a subject ambiguously, so a shape such as `(.|a)*` was admitted.
  Matching that shape costs roughly twice as much per added input character,
  and the same pattern passed the stricter subset that guards the
  fingerprint-injection tool exposed to a connected agent. Disjoint
  alternation and branches beginning with an escaped literal are unaffected,
  and every shipped catalog pattern still validates.

### Fixed

- The exposure ceiling accounts for a degraded identity channel. The score
  reports a floor together with the points an unavailable channel could be
  hiding, and every DNS channel contributed to that total while identity did
  not. A masked identity channel therefore lowered the reported ceiling below
  the value the same domain reports when nothing is degraded, so it was not an
  upper bound and nothing indicated that identity had been masked.
- The GitBook detection matches a real published site. A published custom
  domain resolves to a per-site target whose identifier is joined to the
  hosting label by a hyphen rather than a dot, so the recorded pattern was not
  a label suffix of any observed target and the detection could not fire.
- BigCommerce storefronts served from the platform's second provider-owned
  namespace are recognized; the previous pattern covered only the store
  namespace.

### Added

- Recruitee applicant-tracking detection, from a branded careers site
  published through the vendor's hosted namespace.

## [2.6.11] - 2026-07-24

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Fixed

- The dominant certificate issuer reported for an infrastructure cluster no
  longer depends on the order certificates arrive in. Up to thirty-two issuer
  strings were kept per edge and the budget was consumed first come first
  served, so the issuer whose certificates arrived first won the vote even as
  a minority contributor. On an identical hundred-certificate set the reported
  issuer flipped with arrival order and named the issuer holding forty of the
  hundred. The module already documents arrival order as unstable and carries
  a tie-break intended to keep that instability out of this field.
- A cluster's shared-certificate count no longer saturates at that cap, so a
  cluster and the edge beneath it in the same document no longer report
  different counts for the same relationship.
- A certificate feed that omits the issuer name no longer produces a cluster
  reporting zero shared certificates. The count is tracked independently of
  issuer metadata, so absent metadata is no longer reported as an observed
  zero.
- Delta reporting requires a baseline that recorded the field. A snapshot that
  never carried `auth_type` or `dmarc_policy` reported a transition from null
  to the current value as a confirmed change and described the comparison as
  complete. The gate is now key presence rather than value, so a full export
  that observed no policy still reports a newly added one as a change, while a
  partial snapshot suppresses the comparison and names it.
- Replay of cached DNS records compares DNS labels, matching the live
  detectors it states it mirrors. A cached MX, NS, or CNAME value matched a
  catalog pattern anywhere inside it, and the SPF path searched the whole
  record rather than its parsed targets, so a lookalike target was attributed
  to the provider whose name appeared in an interior label. The target parser
  now lives beside the other stateless DNS parsers so the live and replay
  paths share one implementation.

### Changed

- Cohort posterior-claim shares are scoped to the records that carried the
  node, matching the mean beside them and the documented formula. The share
  counted only those records but divided by the whole cohort, so a node
  present on a tenth of a cohort reported a mean model score of 0.97 beside a
  share of 0.1. This changes the emitted `high_score_share` and its
  compatibility alias whenever a node is absent from some records. The aliases
  continue to carry the same numbers as the fields they alias, and
  `observed_n` is still emitted so a consumer can derive a cohort-scaled
  figure deliberately.

## [2.6.10] - 2026-07-24

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Fixed

- SPF policy is read as a record term rather than a record suffix. RFC 7208
  section 6 allows `exp=` and `redirect=` anywhere, including after the `all`
  mechanism, so any record with a trailing modifier lost its policy and its
  contribution to the observed email-control count. Section 6.1 also requires
  `redirect` to be ignored whenever an `all` mechanism appears, which the
  previous tail check could not see for `+all` or `?all`; a redirect target's
  strict policy was credited to a record whose own policy passes everything.
  Redirect targets share the same parser, so a target with a trailing modifier
  now propagates its qualifier correctly.
- Domain normalization is a fixpoint. It stripped at most one leading `www`
  label, so its own output was not always a stable input. Both cache layers
  rebuild their key from an already-normalized domain, so for a host whose
  normalized form still began with `www` the payload-versus-key guard rejected
  the write, and that host could never be cached.
- A non-default collection scope is no longer shared through the result cache.
  The key is the domain alone, so a `--skip-ct` run published a
  certificate-transparency-degraded result under the shared key and a later
  full lookup was answered from it for the rest of the cache lifetime, with no
  network call and no signal. `--direct-probes` had the mirror problem.
- Hardening simulation copies the observed result instead of rebuilding it
  field by field. The rebuild silently dropped every field it did not name,
  including the observed email gateway, so applying no fixes reported a loss
  and every gateway-fronted simulation understated its gain.
- The exposure assessment reports each observed record once. Its subsections
  overlap by construction, so a single record appeared several times and a
  reader counting corroborating records saw about twice the support that
  exists.
- Catalog paging matches the cap convention used elsewhere in the server. A
  zero limit returned an empty page instead of the full remainder, and a
  negative limit returned an empty page instead of an error, producing the
  no-catalog-match false negative the server instructions warn against. An
  empty and a whitespace-only category filter now agree.
- Supplied flag combinations are rejected rather than discarded. An empty
  `--compare` path was treated as an absent flag, which also defeated the
  `--chain` and `--compare` exclusion, and `--explain-dag` silently overrode
  `--json`, `--md`, and `--plain`. An unreadable snapshot path and an
  unreadable batch path now exit as invalid input rather than as internal
  faults.
- Batch input lines are bounded by their content rather than their terminator,
  so the same line is no longer accepted or rejected depending on its position
  in the file.

### Security

- MCP error text no longer echoes caller-supplied terminal control characters.
  The validator names the value it rejected, and four tools returned that
  message verbatim, so escape and operating-system-command sequences reached
  tool results that agents and terminals consume.
- Two MCP tools reported resolver failures by stringifying the internal error,
  which carried resolver addresses, proxy URLs, and transport-security detail
  from the host environment, and discarded the error kind. Both now use the
  shared outcome mapper the other tools already use.
- Certificate-transparency and DKIM attribution no longer accept a lookalike.
  ESP DKIM hints that are whole domains are matched on label boundaries, so a
  selector target such as a vendor name placed in an interior label is no
  longer attributed to that vendor.

## [2.6.9] - 2026-07-24

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Fixed

- RFC 7505 Null MX and RFC 2782 unavailable-service SRV records are detected
  again. Record normalization stripped the trailing dot from every non-TXT
  value, so a bare root-label target lost the character that carries its
  meaning. A domain publishing `0 .` to declare that it accepts no mail was
  reported as a live but unclassified delivery host, and the merged result
  treated it as evidence that the domain accepts email. SRV records publishing
  `0 0 0 .` to declare a service unavailable were reported as detected CalDAV
  and XMPP services. Both downstream guards were already written for the
  correct values and could not fire. A Null MX apex is now reported as its own
  explicit declaration instead of being folded into sparse or unclassified
  wording that claimed the operator could not be identified.
- Fingerprint discovery consults the real catalog again. `discover_fingerprint_candidates`
  and `recon discover` resolved their catalog path from the calling module's
  own directory, which does not contain one, and the loader treats a missing
  directory as zero known patterns rather than an error. The step that drops
  terminals an existing fingerprint already covers therefore never ran, and
  both surfaces re-proposed catalogued suffixes as new candidates.
- A downstream consumer closing the output pipe exits 0, as the operational
  contract states. The command framework converted the pipe error into exit 1
  before recon's handler observed it, so the closed-pipe branch was
  unreachable for real pipes.
- `--explain` output is deterministic. The email-control branch iterated a set,
  so matched slugs and evidence were ordered by hash seed and changed between
  processes.

### Security

- CSV output now removes terminal control characters, as the panel, markdown,
  and plain-text sinks already did. `display_name` originates from a provider
  response and the batch error column echoes rejected input, so an escape,
  operating-system-command, or bell sequence reached the file and acted on the
  terminal when an operator inspected it. Spreadsheet formula-prefix
  neutralization is unchanged.
- Updated the development toolchain's transitive GitPython dependency to
  3.1.54, clearing eight high-severity advisories. GitPython enters the graph
  only through the mutation-testing group and is not part of the shipped
  runtime, so end users were not exposed.

### Changed

- The `--exposure` panel labels the 0-100 value as a public-evidence index
  rather than a posture score, matching every other surface and the documented
  evidence semantics. The stable `posture_score` and `posture_score_label`
  JSON fields are unchanged.
- Removed em dashes from source comments, docstrings, and operator-facing
  messages so the tracked source satisfies the project text standard directly.

### Notes for downstream consumers

- 2.6.8 was tagged but never published. Its pipeline stopped at the quality
  gate before any artifact was built, so no 2.6.8 distribution exists on any
  channel. 2.6.9 supersedes it.

## [2.6.8] - 2026-07-24

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Changed

- Re-released the v2.6.7 content from rewritten commit history. Repository
  history was rewritten to remove generated-author trailers from commit
  messages, which changed every commit identifier from the v2.3.1 range
  onward. Package content is unchanged from 2.6.7; this release restores the
  invariant that the published release tag and its provenance commit are
  contained in current `main`. The v2.6.7 tag and its published distributions
  remained available and internally verifiable against their original commit,
  which was no longer reachable from `main`. That tag and its GitHub release
  were removed on 2026-08-26; see `Unreleased`. The 2.6.7 distributions remain
  on PyPI, and this release is the tag-bound equivalent of their content.

## [2.6.7] - 2026-07-24

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Changed

- The `--exposure` panel now labels the 0-100 value as a "Public-evidence
  index" instead of "Posture Score", so the last human surface matches every
  other surface and the documented evidence-semantic contract that the value
  is a model-bound public-evidence index, not an overall security grade. The
  stable `posture_score` and `posture_score_label` JSON fields are unchanged.

### Fixed

- Dependabot can update Python dependencies again. The `[tool.uv]`
  `required-version` was an exact `==0.11.17` pin, which Dependabot's bundled
  uv (0.11.8) cannot satisfy, so every `uv lock` update failed closed and no
  Python dependency or security update could land. The floor is now
  `>=0.11.8,<0.12`. Reproducible builds are unchanged: CI, the release
  workflow, and artifact builds still pin the exact 0.11.17 uv release through
  `astral-sh/setup-uv`, and the committed `uv.lock` is still verified in CI. A
  build-toolchain test now asserts the workflows pin the reproducible version
  and that the pyproject floor admits it, instead of coupling the two.

### Security

- Updated the development toolchain's transitive GitPython dependency from
  3.1.50 to 3.1.54, clearing eight high-severity GitPython advisories.
  GitPython enters the graph only through the mutation-testing group and is not
  part of the shipped `recon-tool` runtime, so end users were not exposed; the
  update hardens the contributor and CI environment. The bump could only land
  after the `required-version` floor above unblocked Dependabot.

## [2.6.6] - 2026-07-18

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Changed

- CodeQL now analyzes every push to `main` in addition to pull requests,
  scheduled scans, and manual runs, keeping exact default-branch evidence
  current without a release-time dispatch.
- Roadmap, OpenSSF, supply-chain, security, and release guidance now separates
  shipped behavior, durable policy, and volatile external evidence without
  pinning current trust claims to an obsolete release or sample size.

### Fixed

- Enforcing CI and release dependency audits now retry exactly once only for a
  strict allowlist of recognized transport failures. Vulnerability findings,
  malformed input, unknown failures, and exhausted retries remain nonzero and
  keep publication blocked.
- The dependency-audit runner now resolves the installed auditor under Python
  isolated mode, preventing checkout files from shadowing the blocking audit
  module. The later isolated SBOM job now blocks on every nonzero audit status,
  including a finding first disclosed after the enforcing audit ran.
- The latest security-audit resolution now records v2.6.4 as its actual closure
  release instead of retaining an Unreleased label.

## [2.6.5] - 2026-07-18

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Changed

- CodeQL now runs on every pull request targeting `main` while retaining its
  weekly and manual default-branch scans, and the active `main` ruleset requires
  the passing CodeQL job. Remote release readiness keeps every other required
  code-owned Scorecard control at `10` and enforces the observed SAST transition
  floor of `7` until the public recent-PR window is fully covered by supported
  SAST checks.
- OpenSSF and supply-chain guidance now records the current v2.6.4 Scorecard
  snapshot, explains the merged-PR-head scoring boundary, and distinguishes
  dated external state from the enforced release policy.

### Fixed

- Release version synchronization now fails when an owned document contains an
  ambiguous current-version occurrence instead of globally rewriting historical
  release evidence.

## [2.6.4] - 2026-07-18

### Tool Surface Changes

Tool surface changes: added flag `--all` to `recon cache show`.

### Changed

- Synthetic tenant-domain fixtures now keep every listed domain unique and use
  only reserved namespace values. Privacy regression assertions check complete
  input domains so harmless aggregate text cannot cause false failures.
- Release source distributions now explicitly exclude every private validation
  and agent-work path. The package regression test creates an ignored local
  sentinel before building and rejects private paths or retired target-example
  identities in the resulting archive.
- Live CLI help, agent guidance, public documentation, structured examples,
  schemas, snapshots, and tests now use one neutral reserved target vocabulary.
  The release hygiene gate scans every tracked and nonignored-untracked text
  candidate for the retired fictional target vocabulary while preserving
  genuine ACME protocol references and provider-controlled catalog patterns.
- Tracked validation fixtures now use explicit synthetic identities under the
  reserved `.invalid` namespace. Deterministic tests bind both validation
  generators to their JSON, NDJSON, and CSV outputs without retaining
  company-shaped target identities.
- Detailed agentic transcripts, provider metadata, raw run records, and panel
  snapshots now default to gitignored local paths. The tracked historical
  agentic record and panel review retain aggregate results only.
- Fingerprint-candidate ADD and EXTEND tables continue to retain generic
  provider-controlled detection patterns. Rejected target-like candidates are
  now represented only by aggregate counts and rejection reasons.
- The validation hygiene gate now parses tracked JSON, NDJSON, and CSV
  structurally, includes nonignored untracked candidates before staging, scans
  previously exempt validation directories, rejects malformed CSV shapes,
  target-domain fields, nested certificate-name lists, raw target records,
  non-synthetic tenant identifiers, verification values, and detailed candidate-rejection
  rows, and reports failures without echoing sensitive values.
- The data-handling policy now records the complete bounded set of pre-policy
  artifacts found by the full-history and distribution audit. It distinguishes
  mutable release assets from immutable package bytes and explains why a
  Git-only rewrite cannot retract mirrors, caches, copies, or attestations.
  Contributor, legal, artifact-review, performance, onboarding, and roadmap
  guidance now distinguish reserved target examples from allowed provider
  references and record the bounded historical exception separately from the
  clean current-tree contract.
- Agentic validation report and raw-record paths now reject trackable
  in-repository destinations before provider initialization; external and
  gitignored local output paths remain available.
- Root help and callback copy now say "Passive domain intelligence from public
  sources," name the primary `recon DOMAIN` shorthand, and point to the
  no-argument examples.
- The no-argument welcome banner now surfaces plain linear output, structured
  JSON, evidence review, batch use, online diagnostics, and MCP client setup in
  that order. README and getting-started documentation now expose `--plain` for
  screen readers and grep.
- Batch help now groups output, collection, analysis, and evidence controls by
  task. It also states the 1 to 20 concurrency clamp and the existing rule that
  per-domain failure records do not change a valid batch invocation's exit 0.
- Root `--debug` help now warns operators to review diagnostics before sharing
  because logs can contain domain inputs and local details.
- `recon doctor --help` now names its default synthetic Microsoft identity,
  `example.com` DNS, and crt.sh contacts and identifies `--fix`, `--mcp`, and
  `--client` as local-only modes.
- MCP setup guidance now presents the complete verification sequence: static
  registry check, live local stdio tools and resource check, then the named
  client's saved-config check. Installer completion text names all three
  verification commands, and live success copy states that client configuration was not
  inspected.
- Fingerprint and signal category filters now use one word-prefix or phrase
  matcher across CLI and MCP discovery. A short query such as `ai` therefore
  no longer produces different category sets between interfaces. Explicit
  empty category and detection-type values now fail validation instead of
  expanding into a full human catalog dump.
- Human fingerprint search now previews at most ten unique slugs, reports the
  complete record and unique-slug totals, and points to `--json` for the full
  record set. Fingerprint and signal rows use field-associated layouts that
  remain understandable when a terminal wraps them. Locally extended catalog
  detail text cannot emit terminal controls and is visibly bounded at 1,024
  characters.
- Catalog onboarding now limits its no-network promise to list, search, and
  show. `fingerprints test --help` discloses that corpus rows use ordinary live
  lookup boundaries. Corpus input is validated, apex-normalized, and
  deduplicated before the first lookup and is bounded to 1 MiB, 1 KiB per line,
  and 500 domain rows. A malformed row prevents all collection. Human and JSON
  output now distinguish lookup errors from clean non-matches; existing JSON
  keys remain intact. Valid invocations retain exit 0 when lookups report
  errors, and the documented automation contract requires checking each row's
  tri-state `status`.
- Ranked signal search now keeps relevance order without reopening
  noncontiguous category headings. Each human result carries explicit Category
  and Confidence fields, and ambiguous show failures point to search.
- Nested command help now keeps concise, complete summaries at 40 columns, and
  detailed help no longer exposes documentation-source markers.
- The canonical local-gate wrapper now emits ANSI styling only to a capable
  terminal. Redirected and captured logs are plain text without changing any
  stage, command, or pass condition. Local and CI Ruff stages now disable the
  cache so rapid same-size edits cannot reuse a stale lint result.
- The documented partial-release recovery path now checks the exit status from
  both local tag resolution and Release-run discovery separately from output,
  so plausible partial output cannot bypass a failed Git or GitHub CLI call and
  reach rerun mutation.
- Extracting fingerprint search ranking and rendering reduced the repository's
  remaining too-many-branches count from 11 to 10; the enforced PLR0912 ceiling
  is tightened to retain that reduction.
- Extracting bounded corpus loading reduced the remaining too-many-statements
  count from 9 to 8; the enforced PLR0915 ceiling is tightened to retain that
  reduction.
- Extracting static MCP registry checks and reference-config rendering reduced
  the remaining too-many-statements count from 8 to 7; the enforced PLR0915
  ceiling is tightened to retain that reduction.
- `recon cache show` now reports metadata for the 24-hour result cache and the
  30-day CT cache independently. It shows reusable, expired, missing, and
  unreadable states without printing cached tenant, service, or evidence data.
  Its default overview opens at most the first 100 JSON files per layer while
  reporting exact total and uninspected counts; `--all` opts into complete
  inspection. Rows select compact or vertical layout from their actual rendered
  width, so long values remain field-associated at ordinary terminal widths.
  Cache-writer-shaped interrupted-write artifacts are counted without payload
  reads, produce a visible exit 4, and are removed and counted by confirmed
  clear-all; unrelated `*.tmp` files are preserved.
- Default low-confidence panels now point to `--explain` for evidence and
  `--verbose` for per-source status. Verbose and explain output suppress the
  repeated cue.
- Delta panel human label for the 0-5 email control inventory is now
  "Email control count (0-5)" instead of "Email Security Score." The stable
  JSON field `changed_email_security_score` is unchanged.
- Delta command help now states confirmed change fields, including email
  control count, and incomplete-collection suppression.
- Explain-path confidence derivation for email-control insights now says
  "Email control count" instead of "Email security score."
- Public bug and fingerprint issue forms now require a target-data
  acknowledgement and request only reserved synthetic fixtures, sanitized
  diagnostics, generic provider patterns, and provider-controlled references.
- New fingerprint detections must include a valid, non-future `verified` date;
  the diff-aware local and CI gate leaves the legacy undated backlog available
  for reviewed backfill.
- `--include-unclassified` now adds bounded, typed catalog accounting and
  unmatched-value diagnostics across every current DNS fingerprint path. The
  default JSON and stable schema remain unchanged. Private scan runs now split
  detailed gap evidence from a target-free aggregate report and revision
  manifest.
- The built-in catalog now has 855 entries and 1,062 detections. Eleven
  provider-documented CAA, CNAME, SPF, TXT, and owner-qualified TXT rules were
  added from a frozen private recurrence pass and a documented vendor seed.
  CAA authorization and legacy-SPF slugs remain distinct from stronger service
  indicators.
- A dated, aggregate-only typed catalog baseline now accounts for every bounded
  DNS fingerprint path while keeping all target names, target-owned values,
  tenant identifiers, and per-domain rows out of the repository.
- A frozen 366-namespace unseen vertical holdout observed every newly admitted
  pattern at least once. Only aggregate counts are published, and no additional
  rule was tuned from the holdout.
- Project documentation now describes the shipped package, CLI, JSON, and local
  MCP surfaces without implying a separate top-level library facade, and the
  release process now batches ordinary work into coherent package releases.
- `--explain` and `--plain` documentation now distinguish retained evidence
  and reconstructed explanation links from exact generation-time lineage, and
  standard lookup output from mode-specific reports.
- Local release-readiness text and JSON now identify whether only local checks
  or local plus remote publication checks were assessed.
- Installer helper guidance now requires a reviewed release-tag checkout and
  no longer recommends piping mutable branch content into a shell. README
  helper discovery now leads to the latest release selection page instead of
  mutable `main` files.
- Main CI and the tagged release workflow now execute both installed CLI entry
  points from a built wheel. Publication waits for the separate read-only
  sealed-wheel smoke job.
- Artifact builds now select uv 0.11.17 and an exact, hash-locked Hatchling
  dependency graph. CI and release build the sdist first, reconstruct the wheel
  from that exact file, and keep the constrained replay recipe in the
  supply-chain guide.
- The release package-smoke gate now rejects missing, duplicate, unexpected, or
  tag-mismatched distribution artifacts before either publication channel can
  run. A valid release contains exactly one canonical wheel and one canonical
  sdist.
- GitHub Release publication now waits for PyPI to expose the exact wheel and
  sdist and for both SHA-256 digests to match the sealed build pair. Recovery
  runs cannot replace GitHub assets with different bytes from a skipped PyPI
  upload. If parity fails after PyPI accepts immutable files, the workflow now
  documents the resulting partial-publication state and evidence-preserving
  recovery boundary.
- Existing GitHub Release recovery now validates the exact tag, title,
  non-draft, non-prerelease, and mutable state, and expected-only asset
  inventory, complete or partial, before any replacement upload. It rechecks
  the remote tag against the workflow commit immediately before mutation.
  Malformed, duplicate, unexpected, or immutable state fails before
  `--clobber`, and new release creation refuses to synthesize a missing tag.
- Partial-publication recovery instructions now use strict Bash mode and named
  branch, worktree, tag, run-selection, and run-commit guards. A visible
  checkpoint is required before the first rerun command, and every failed
  precondition stops before mutation.
- Remote release readiness now validates the completed CycloneDX SBOM. For
  releases produced by the current workflow, it verifies the wheel, sdist, and
  SBOM against the downloaded provenance bundle, exact release workflow, exact
  version tag and commit digest, and hosted-runner boundary. The exact v2.6.3
  historical exception verifies its wheel and sdist provenance while retaining
  mandatory SBOM structure validation. The release workflow signs all three
  subjects. Remote PyPI checks now reuse the bounded exact-pair metadata
  validator, reject untrusted file
  URLs before invoking the verifier, pin the PEP 740 verifier, bound external
  commands and downloaded evidence, and report cross-channel digest parity.
  It also rejects mixed-state reports unless the remote and local current
  project-version tag plus `HEAD` resolve to the same full commit.
- Release-tag installer helpers now install exactly the reviewed version,
  preserve a sole existing `uv` or `pipx` owner, refuse dual or unmanaged
  ownership, and surface manager inspection and installation failures.
- The consumer verification guide now provides complete fail-closed POSIX and
  PowerShell paths with prerequisites, exact release inventory, SBOM and
  bundle validation, PyPI provenance, channel parity, both wheel entry-point
  smokes, optional verified-wheel installation, and one final success state.
  Both require a clean exact-tag checkout, bind provenance to its commit
  digest, pin the PEP 740 verifier, reject empty or oversized assets, and
  classify recovery actions by failure type. Releases produced by the current
  workflow verify the completed SBOM as a signed subject; the published v2.6.3
  recipe binds its distribution-only historical exception to the exact tagged
  commit and still validates the completed SBOM structure.

### Fixed

- CLI surface summaries now use singular or plural flag grammar and the
  directionally accurate `to` and `from` prepositions.
- `recon doctor --mcp` no longer exits successfully when server instructions
  or canonical tools are missing. It now independently verifies all canonical
  local resource registrations, so a tool-list failure cannot hide a resource
  registration failure.
- `recon mcp doctor` now lists and reads all five canonical local JSON
  resources, validates their URI, media type, text envelope, and JSON object
  shape plus minimal catalog, schema, and surface-inventory structure, and
  checks candidate-v2 cache metadata. A later protocol failure keeps
  successful prior rows and names the failed phase instead of collapsing the
  report into one generic handshake failure. Resource payloads are never copied
  into diagnostic errors.

- `recon fingerprints show` no longer returns only the first catalog record
  for a slug defined in multiple records. Human and JSON output retain every
  record and its exact semantic fields while preserving the original top-level
  JSON projection for compatibility. Near-match suggestions are deduplicated.
- Signal list and search JSON no longer expose different summary field sets;
  both now use the same projection including `min_matches`. An empty signal
  search result also points back to the local catalog list.

- The PyPI consumer-verification path can no longer report shell success after
  a failed metadata producer or zero matched artifacts. It consumes a newly
  created file containing exactly two validated URLs and requires both
  attestation checks.
- The release transaction now updates, snapshots, stages, and rolls back both
  installer version pins with the other release-owned surfaces, preventing a
  newly tagged helper from retaining the prior package version.
- The parity gate now reads version-scoped PyPI metadata and retries only
  transport or not-yet-visible states; permanent metadata, digest, and safety
  violations fail immediately.
- Completed SBOM validation now converts non-UTF-8 input into a named failed
  readiness result instead of allowing a decoding traceback to escape.

- Outbound HTTP destination validation now fails closed when the hostname is
  absent or DNS fails, returns no address, or returns an invalid address. The
  request is refused before the HTTP transport can perform its own unchecked resolution;
  public addresses and the existing every-redirect validation remain intact.
- Importing the MCP server no longer installs a process-wide logging handler.
  Default stderr logging exists only while the server loop runs, and unexpected
  server exits now emit one bounded, control-free line with the exception type.
- `recon doctor` now converts every ordinary `httpx.RequestError`, including
  protocol and proxy failures, into a named row and continues independent
  checks. Core failures exit 1; optional CT failures remain warnings.
- Narrow command help no longer exposes literal Rich tags or truncated root
  summaries. The no-argument welcome path keeps descriptions indented beneath
  their commands at 40 and 60 columns.
- CT cache overview rows now label fresh entries `reusable` and entries older
  than the 30-day TTL `expired`, matching single-entry inspection and the
  documented metadata-only cache contract.
- Batch `error_kind` now follows structured resolver state instead of timeout
  words in the display message. Unexpected per-domain exceptions use stable,
  redacted output across JSON, NDJSON, CSV, and panels while retaining details
  in opt-in debug logs. The closed four-key error schema is unchanged.
- `recon cache clear` now distinguishes a missing entry from a deletion
  failure, reports partial layer success, and exits 4 after an unlink failure
  without exposing the underlying path or exception in ordinary output.
- `recon cache show` no longer reports an unreadable or rejected cache entry as
  absent. It reports the affected layer, retains raw failure detail for debug
  logs, and exits 4 after rendering all available metadata.
- Default and MCP doctor rows now strip control bytes, escape Rich markup, and
  bound dynamic diagnostic fields before terminal rendering.
- Live MCP doctor output, MCP install plans and failures, client doctor output,
  and doctor-fix paths and failures now cross the same bounded terminal-safety
  boundary.
- Timeout and all-source-failure lookups now direct the operator to
  `recon doctor` before retrying, while preserving the original error and exit
  code on stderr.
- Exit-code documentation now distinguishes handled general failures from the
  CLI last-resort crash handler, which reports unexpected runtime failures as
  exit 4.
- Early-closing output pipelines now exit cleanly without creating a crash log.
  Unrelated operating-system errors still use the existing internal-error path.
- `recon doctor --fix` now lists every supported fingerprint detection type in
  its generated template and no longer advertises unsupported `http` rules.
- MCP validation-failure logs now retain only a request ID and stable
  `invalid_domain` reason. Rejected argument values and exception text remain
  out of operator logs while existing tool-facing correction messages stay
  unchanged.
- Human confidence output now uses singular `source` when exactly one source
  supports a result across terminal panels, Markdown, and MCP text. Invalid
  lookup input now includes one accepted example and a path to the existing
  no-argument guidance while preserving exit code 2.
- Bare undotted or otherwise invalid first arguments (for example
  `recon example`) route to domain validation instead of Click's
  "No such command" path.
- Added `python -m recon_tool` package entry so local and scripted installs can
  invoke the CLI without relying only on the console script.
- Welcome banner now states that inputs need a public-suffix domain and shows
  `python -m recon_tool --version` as an offline install check path.
- Fingerprint loading now accepts native YAML dates in `verified` metadata and
  rejects impossible ISO-looking calendar dates instead of silently treating
  both forms as undated.
- The maintained corpus scanner invokes the supported `python -m recon_tool`
  entry path, restoring end-to-end scan execution after the CLI became a
  package.
- SPF, MX, NS, and CAA catalog matching now respects DNS-label and CAA issuer
  boundaries. CAA `iodef` values and deceptive hostname lookalikes no longer
  create provider attributions, while legacy dotless NS provider labels remain
  supported on exact or hyphen-suffixed labels.
- Private catalog reduction now reports measured inputs separately from batch
  errors, distinguishes owner-qualified TXT value shapes, reads nested JSON or
  NDJSON runs, and supports direct script execution. Corpus exclusions now read
  streamed NDJSON scan output as well as JSON arrays.

## [2.6.3] - 2026-07-14

### Tool Surface Changes

Tool surface changes: no CLI command, flag, JSON, MCP, cache, or public import
changes.

### Changed

- Replaced eager retained-batch coroutine fan-out with a fixed outer worker
  pool. Ordered output is preserved, while later inputs are admitted only when
  a worker becomes available. NDJSON keeps its completion-order streaming path.
- Made the local and CI Pyright stages use the complete configuration-owned
  project scope, added the interface-layout check to CI, made all four tracked
  complexity rules reject stale ceilings, and lowered the two improved ceilings.

### Fixed

- Made adaptive CT rate limiting recheck breaker and pacing state without
  holding its reservation lock during sleeps, enforce one deterministic total
  wait budget, and bind limiter instances to their event-loop lifecycle.
- Counted CertSpotter transport and HTTP failures exactly once in limiter
  feedback while keeping HTTP 429 accounting distinct.
- Closed compressed HTTP response streams before refusing unsupported content
  encodings, preventing connection-resource leaks on the rejection path.
- Rejected stable cache-directory symlinks, Windows junctions and reparse
  points, and self-referencing redirects without violating the caches' no-throw
  contract across supported Python versions.

## [2.6.2] - 2026-07-13

### Tool Surface Changes

Tool surface changes: no CLI command, flag, JSON, MCP, cache, or public import
changes.

### Fixed

- Made repository documentation links in the package description resolve from
  PyPI instead of becoming project-relative 404 responses.
- Synchronized the current release and remaining MCP v2 adoption gate across
  the roadmap and readiness documents.

## [2.6.1] - 2026-07-13

### Tool Surface Changes

Tool surface changes: added `--exact` to `recon cache show` and
`recon cache clear` so operators can inspect or remove the literal-host cache
entries created by `recon <host> --exact`. No MCP tools, annotations, defaults,
or public JSON schemas changed.

### Changed

- Bound result-cache payloads and versioned CT-cache payloads to their exact
  validated cache keys. Existing unbound CT entries are intentionally treated
  as misses and repopulate on demand.
- Versioned persisted adaptive-rate-limiter state and bound it to the provider
  name, with strict finite numeric ranges and complete constructor invariant
  validation.

### Fixed

- Isolated literal-host cache entries from registrable-apex entries so an
  exact lookup cannot reuse or overwrite observations collected for another
  host.
- Replaced path-level cache reads with descriptor-bound, size-limited JSON
  admission that rejects symbolic links, path replacement, concurrent file
  mutation, expired entries before decoding, excessive nesting, and materially
  future modification times.
- Replaced the rate limiter's predictable temporary state filename with a
  random exclusive file and atomic replacement, and made corrupt, non-finite,
  cross-provider, or arbitrarily large numeric state degrade to fresh defaults.
- Bounded and depth-checked PyPI update metadata, and made truncated HTTP
  responses return an unavailable update result instead of escaping the
  command's failure boundary.

## [2.6.0] - 2026-07-13

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes, and no MCP tool names,
parameters, schemas, annotations, or defaults changed. Batch CSV adds an
`error` column so failed rows are machine-visible instead of blank.

### Changed

- Batch lookup now applies its line and total limits to UTF-8 bytes and resolves
  equivalent URL, sub-host, and apex inputs only once at their canonical apex.
- Release preparation now starts from the exact current `origin/main`, validates
  the fully synchronized prospective release tree, rolls back failed mutations,
  and pushes `main` plus the reviewed tag atomically.
- Release tags now pass a version, changelog, commit, and main-ancestry preflight
  before the complete local quality gate can build or publish artifacts.

### Fixed

- Rejected domain labels over 63 ASCII octets and normalized DNS presentation
  names over 253 ASCII octets before collection; Unicode and ASCII `www`
  inputs now follow the same exact-host normalization contract.
- Made result and CT cache readers treat non-object, wrong-shaped, non-finite,
  overflowing, or corrupt JSON as a cache miss instead of crashing or silently
  coercing strings into character sequences, including malformed nested
  posterior diagnostics, impossible posterior intervals, and invalid
  infrastructure algorithms or edges.
- Preserved full certificate summaries and infrastructure cluster reports in
  the CT cache, including wildcard sibling clusters and deployment bursts, and
  made summary-only cache entries reusable.
- Kept MCP timeout and total-source-failure messages distinct from true no-data
  results, routed `domain_report` through the shared domain validator, and
  removed raw URL/path text from every post-validation MCP result and log.
- Prevented MCP installation from replacing a config symlink or silently
  overwriting a non-object `mcpServers.recon` stanza without `--force`; client
  doctor now fails diagnostics for non-string, blank, or control-bearing
  process commands and arguments.
- Made HTTP retry handling reject negative and non-finite `Retry-After` values,
  use bounded backoff for malformed values, and honor zero without sleeping.
- Made release SBOM generation fail closed on tool or JSON errors and include a
  complete `recon-tool` root component and dependency edge.
- Expanded CI text hygiene to the full pushed or pull-request commit range and
  added a repository-wide gate for tracked Markdown links and heading anchors.
- Rejected cross-domain delta comparisons, impossible prior scalar values, and
  schema-invalid prior enum values before resolution, plus nonpositive or
  non-finite timeouts; JSON first-run delta errors now stay on stderr so stdout
  remains parseable.
- Preserved batch lookup failures in the new CSV `error` column and rejected
  explicit unknown batch-record discriminators instead of treating them as
  legacy success records.
- Made profile boost parsing ignore boolean and non-finite multipliers while
  normalizing key whitespace, and made update checks reject malformed PyPI
  response shapes while correctly ordering prereleases, development and local
  builds, distinct local build labels, final releases, and trailing release
  zeroes.
- Reduced autodiscover redirect observations to boundary-safe registrable
  apexes, including multi-label public suffixes, instead of dropping two-label
  targets or retaining arbitrary sub-hosts.

## [2.5.8] - 2026-07-13

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes, and no MCP tool names,
parameters, schemas, annotations, or defaults changed. Schema descriptions and
the packaged surface inventory were synchronized with the existing behavior.

### Changed

- Aligned the README, roadmap, contributor guidance, MCP integrations, security
  model, schema reference, research package, release guidance, and historical
  validation records with the shipped v2 behavior and current repository
  layout.
- Corrected Elastic and Splunk examples to preserve observation confidence,
  use their documented field and configuration semantics, and avoid implying
  vulnerability severity or organizational ownership.
- Replaced the superseded "strictly passive" shorthand with an explicit
  public-metadata collection boundary that distinguishes DNS visibility,
  provider identity discovery, the default MTA-STS request, and opt-in direct
  probes.
- Raised the remote OpenSSF Scorecard floor to 8.0 and made SAST a required
  score-10 code-owned control.

### Fixed

- Made generated-surface checks verify both the documentation copy and the
  packaged inventory so release artifacts cannot silently drift.
- Added documentation-integrity tests for indexed canonical documents,
  historical commit receipts, semantic review stamps, installer behavior,
  error contracts, SIEM mappings, and research-proof boundaries.
- Kept the cross-platform test matrix shallow while making a required
  repository-policy job fetch history once and enforce every documented commit
  receipt. Release tests repeat the full-history proof before publication.
- Corrected stale module paths, invalid historical commit receipts, frozen-draft
  wording, first-run delta behavior, MCP installer paths, and result-error
  semantics across maintained documentation.
- Updated `recon mcp install` to emit VS Code's required `type: "stdio"` and to
  remove the unsupported legacy `autoApprove` field from VS Code and Claude
  Code recon blocks while preserving documented client-specific fields.
- Made degraded-MX collection views mask the current neutral sparse-result
  message as well as superseded cached self-hosting wording.

## [2.5.7] - 2026-07-13

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes, and no MCP tool names,
parameters, schemas, annotations, or defaults changed. MCP server routing
instructions were corrected and made more context-efficient.

### Changed

- Made every agent-facing workflow request `format="json"` together with
  `explain=true` when it needs the lookup provenance DAG. Posture guidance now
  distinguishes flat observation explanations from the lookup DAG.
- Prefer bounded fingerprint pages for browsing while requiring an exhaustive
  page walk or full resource read before reporting that the catalog has no
  match. The MCP guide now documents all pagination parameters and all four
  explicit process-state tools.
- Recorded a reproducible MCP discovery and result-body characterization. The
  complete stable tool surface remains the default because serialized byte
  reduction alone does not prove an end-to-end client context benefit.

### Fixed

- Made documentation drift tests reject missing `readOnlyHint` annotations,
  synchronize live parameter names and stateful tools, and protect the exact
  explained-lookup and catalog-completion contracts.

## [2.5.6] - 2026-07-13

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Changed

- Grouped all 28 `lookup` options into five task-oriented help panels without
  changing any token, alias, default, validation rule, or runtime behavior.
  At 80 columns, the measured help surface is 109 lines instead of 154 and
  every canonical option remains visible without truncation.
- Added a common-path summary before the lookup options that distinguishes
  opt-in Google CSE and BIMI probes from the default MTA-STS request. Task
  panels bring collection, cache, and scope controls substantially earlier.
- Replaced contributor-internal wording on `--include-unclassified` with a
  concise description of its public JSON and fingerprint-discovery behavior.

## [2.5.5] - 2026-07-13

This release includes the v2.5.4 changes, which were tagged but not published
to PyPI or as a GitHub Release.

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Changed

- Made the first-run sequence use `recon --version` as the offline install
  check and label `recon doctor` as an online diagnostic. The README, getting
  started guide, no-argument banner, and platform installers now disclose DNS
  visibility, the default MTA-STS request, and opt-in Google CSE and BIMI
  probes before the first lookup.
- Clarified that strict mode changes panel wording only for High-confidence
  results with at least three sources and does not change the underlying
  evidence, validation, or confidence.
- Made `recon mcp install --dry-run` emit the client-specific top-level config
  stanza, including `servers` for VS Code and `mcpServers` elsewhere. Static
  MCP doctor output now identifies its generic block as a reference, preserves
  the interpreter-bound launcher literally, and directs operators to the safe
  merge installer.
- Preserved complete MCP client repair guidance in terminal diagnostics while
  retaining control-character filtering and an explicit display bound.

### Fixed

- Made `recon doctor --fix` exit nonzero on directory, publication, or template
  failures, reject conflicting doctor modes, continue independent repairs, and
  publish complete templates with an atomic no-replace boundary. Existing or
  concurrently created user files are never overwritten, and failed staged
  writes leave no partial target.
- Replaced timestamp-only crash-log names with exclusive temporary files,
  added review and redaction guidance before sharing diagnostics, and made the
  no-log fallback actionable without exposing exception details.
- Made release validation independent of the current Rich SGR color sequences
  so the user-facing doctor help contract is checked consistently on Linux and
  other supported environments.

## [2.5.4] - 2026-07-13

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Changed

- Made the first-run sequence use `recon --version` as the offline install
  check and label `recon doctor` as an online diagnostic. The README, getting
  started guide, no-argument banner, and platform installers now disclose DNS
  visibility, the default MTA-STS request, and opt-in Google CSE and BIMI
  probes before the first lookup.
- Clarified that strict mode changes panel wording only for High-confidence
  results with at least three sources and does not change the underlying
  evidence, validation, or confidence.
- Made `recon mcp install --dry-run` emit the client-specific top-level config
  stanza, including `servers` for VS Code and `mcpServers` elsewhere. Static
  MCP doctor output now identifies its generic block as a reference, preserves
  the interpreter-bound launcher literally, and directs operators to the safe
  merge installer.
- Preserved complete MCP client repair guidance in terminal diagnostics while
  retaining control-character filtering and an explicit display bound.

### Fixed

- Made `recon doctor --fix` exit nonzero on directory, publication, or template
  failures, reject conflicting doctor modes, continue independent repairs, and
  publish complete templates with an atomic no-replace boundary. Existing or
  concurrently created user files are never overwritten, and failed staged
  writes leave no partial target.
- Replaced timestamp-only crash-log names with exclusive temporary files,
  added review and redaction guidance before sharing diagnostics, and made the
  no-log fallback actionable without exposing exception details.

## [2.5.3] - 2026-07-13

### Tool Surface Changes

Tool surface changes: no CLI command, flag, JSON field, MCP tool, resource,
prompt, cache, or public import name changes.

### Changed

- Added one generation-aware MCP SDK boundary so the same local stdio server
  runs on stable SDK v1.28.1 and candidate SDK v2.0.0b1 without duplicating
  registration or domain logic. Production remains constrained to stable v1.
- Raised the MCP dependency floor from 1.0 to the first fully characterized
  stable release, 1.28.1. Exact isolation proved that 1.0 lacks both server APIs
  recon requires, while 1.28.1 and 2.0.0b1 pass the complete matrix.
- Made both MCP doctors report the installed SDK path and use public registry
  and discovery APIs. The live doctor uses `initialize` on stable v1 and
  `server/discover` on v2, where it also verifies complete-result cache
  metadata.
- Added a blocking CI matrix for exact stable and candidate SDK pins. It checks
  server import, stdio discovery, 22 tools, five resources, one prompt, JSON
  Schema 2020-12 conformance, structured success and error results, catalog
  reload concurrency, prompt rendering, explicit cache policy, cache metadata,
  and the live doctor.

### Fixed

- Corrected MCP documentation that omitted the registered `domain_report`
  prompt and overstated support for untested early SDK releases.

## [2.5.2] - 2026-07-12

### Tool Surface Changes

Tool surface changes: no CLI command, flag, JSON, MCP, cache, or import changes.

### Changed

- Kept the 11 split fingerprint YAML files as canonical contributor source and
  sdist content while shipping one deterministic generated JSON runtime catalog
  in the universal wheel. Local, CI, and release gates reject byte drift;
  exact differential tests preserve all 847 entries, 1,045 rules, ordering,
  repeated slugs, metadata, accessors, and matching behavior.
- Replaced repeated built-in YAML parsing with bounded JSON decoding followed by
  the canonical fingerprint validator. A 15-repetition CPython 3.14.4 local
  characterization at clean commit `1b9fe26` measured 558.188 ms median for
  the YAML reference and 44.339 ms for the generated runtime, a 12.59-times
  stage gain with 72.0
  percent less traced peak Python allocation. This is a dated local diagnostic,
  not a portable SLO.

### Fixed

- Rejected list-valued confidence, slug, or category fields and non-boolean
  `m365` values in custom fingerprint YAML without crashing catalog loading or
  discarding valid sibling entries. Custom regex safety, caps, ordering, and
  additive behavior remain unchanged.

## [2.5.1] - 2026-07-12

### Tool Surface Changes

Tool surface changes: no CLI command, flag, JSON, MCP, cache, or import changes.

### Changed

- Reused bounded compiled standard-library regular expressions across repeated
  TXT, CNAME, subdomain TXT, PTR-region, and cached-DNS replay matching. The
  cache is capped at 2,048 entries, rejects oversized or invalid patterns, keys
  by flags, and is cleared on catalog reload or process-catalog mutation.
  Exact differential output and existing ReDoS admission controls are
  preserved. The checked 1,000-value by 298-rule Python 3.14.4 fixture fell
  from a 348 ms historical median to 115 ms at clean commit `9b90af0`.
- Loaded the Bayesian network and prior override once per fusion-enabled batch
  and reused one coherent invocation-local snapshot. A 25-record synthetic
  fusion fixture fell from an 864 ms repeated-setup reference to 355 ms without
  introducing a process-global model cache or changing output.
- Reused the primary seed-1729 Louvain partition in the existing eight-seed
  CT stability calculation. The seed set, pairwise adjusted Rand statistic,
  deterministic ordering, and graph output remain unchanged while one
  duplicate partition run is removed.
- Added file-grouped pytest execution with at most four workers to local, CI,
  and release coverage gates. The full OS and Python 3.11 through 3.14 matrix
  remains intact, and pytest-cov combines worker coverage. The blocking project
  floor is ratcheted from 82 percent to 90.2 percent, just below the 90.22
  percent minimum observed across the prior complete matrix.
  The checked local suite completed 4,522 tests in 88.83 seconds with coverage,
  compared with 4,502 tests in 330.53 seconds in the earlier serial no-coverage
  reference. This is a local characterization, not a CI timing SLO.
- Documented the Python compatibility and optimization policy. Python 3.14 is
  preferred for new development and characterization, while `requires-python`
  remains `>=3.11`. Rust, free-threading, subinterpreters, eager task execution,
  and the experimental JIT remain evidence-gated rather than runtime
  requirements.

### Fixed

- Validated both arguments to posture comparison before resolving either one,
  so a malformed second domain cannot trigger a lookup for the first domain.
- Removed accidental live DNS and domain-resolution work from unit tests and
  replaced real retry waits with captured clocks that assert exact attempt and
  delay schedules. Production retry behavior is unchanged; roughly 32.5 seconds
  of confirmed real waits and network calls were removed from the focused test
  paths.

## [2.5.0] - 2026-07-12

### Tool Surface Changes

Tool surface changes: added flags `--summary-schema` on `recon batch`.

### Added

- Added the first bounded internal claim contract for the exact observation
  that a fresh valid apex DMARC record declares `p=reject`. The contract keeps
  construction, collection, time, and four-state claim semantics separate;
  carries minimal positive and explicit-disconfirming dependency-unit
  certificates; recomputes monotone closure after canonical ledger union; and
  fails closed rather than truncating proof antichains. Raw evidence must match
  the scalar policy before it can sign a certificate. Empty, invalid,
  unavailable, stale, and lineage-incomplete observations remain unresolved.
  Opt-in cohort schema 2.2 consumes the contract through two transient internal
  projections, claim state and raw-bound effective policy, that are never added
  to tenant JSON, cache, MCP, or package output.
- Added `--summary-schema 2.2` to `recon batch --summary` and
  `--schema-version 2.2` to the standalone aggregate reducer. Both retain 2.1 as
  the default so existing cohort consumers keep the released shape and
  denominator semantics.

### Changed

- Updated DMARC parsing for RFC 9989: ASCII whitespace around `=` and
  case-insensitive tag names are accepted while `DMARC1` remains case-sensitive;
  a missing or invalid `p`, `sp`, or `np` follows the valid-`rua` effective-none
  fallback; and invalid subdomain-policy tags no longer retain an enforcing
  policy. Fallback records retain DMARC service and raw evidence while the stable
  `dmarc_policy` field stays null rather than fabricating an explicit `p=none`.
  Reporting-URI vendor attribution now parses syntax-checked `mailto` URIs and
  requires an exact or label-boundary match against a valid DNS domain, closing
  malformed-tail and substring false positives. Historic `pct` parsing remains
  a documented compatibility extension.
- Added opt-in `cohort_summary` schema 2.2. Its in-core DMARC rates use the
  fresh, raw-evidence-bound contract; the downstream sidecar labels its
  timestamp-free compatibility view `atemporal_explicit_policy_rate`. Unknown
  DMARC and MTA-STS values no longer enter denominators as negative observations,
  and gateway detection is reported as model support coverage. Schema 2.1
  remains the default and unchanged for compatibility.

## [2.4.0] - 2026-07-11

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Changed

- Added `DeltaReport.incomplete_comparison` to distinguish a fully observed
  empty delta from a comparison masked by degraded collection. Existing MCP
  result schemas also expose the additive diagnostic fields
  `degraded_sources`, `unavailable_controls`, and `collection_masked_units`.
- Bounded NDJSON batch streaming to a rolling concurrency-sized task window
  and stopped retaining completed tenant objects in the batch-wide enrichment
  map. Large streaming runs now honor their constant-result-memory contract
  instead of creating and retaining work for the full input corpus.
- Aggregated consecutive repeated certificate SAN sets before expanding their
  CT graph pairs. Renewal-heavy certificate feeds preserve edge weights,
  issuer ordering, deterministic output, and existing caps while avoiding the
  same quadratic pair expansion for every identical certificate. On the dated
  local 1,000-entry, 60-SAN repeated fixture, median graph time fell from 2.31
  seconds to 0.16 seconds; this characterization is not a general product SLO.
- Established an evidence-gated performance architecture decision. A dated,
  reproducible, network-free CPU characterization harness now separates
  catalog loading, fingerprint
  matching, Bayesian inference, CT graph construction, and rendering. The
  default runtime remains pure Python; Python algorithm and cache improvements
  precede any optional Rust prototype, while Go and Mojo remain outside the
  current local product boundary. Native promotion now requires material
  end-to-end value, exact Python-reference parity, compiler-free installation,
  full quality gates, reproducibility, SBOM coverage, provenance, and rollback.
- Narrowed the mutation exclusions from the whole BitOr operator family to six
  line-scoped postponed-annotation unions. All five runtime set and frozenset
  union expressions, representing 55 mutants, now remain in the tested
  surface. A deterministic AST test prevents a mutation pragma from covering a
  runtime union. Local preflight killed 52 of the newly tested mutants and left
  three behaviorally unchanged under current invariants. The authoritative
  sweep confirmed 655 killed, 62 survived, and 8.65 percent survival across 717
  tested mutants, with zero incompetent or pending jobs.
- Strengthened the Bayesian mutation gate with exact closed-probability,
  strictly-positive likelihood, neutral marginal fallback, collection-
  opportunity, degraded-source adapter, slug extraction, and real-ratio
  contracts. The authoritative GitHub sweep generated 801 jobs and filtered
  139 mutants under the configured operator exclusions. It killed 603 of 662
  tested mutants and left 59 survivors for an 8.91 percent survival rate
  against the unchanged
  12 percent ceiling. Independent review rejected out-of-domain entropy tests
  rather than manufacturing two additional kills.
- Rebuilt the documented correlation research program around proof-carrying
  public observation and provenance-constrained claim robustness. The formal
  proposal now separates construction, collection, claim state, and time and
  specifies certificate antichains, Boolean must/may envelopes, bounded
  provenance algebra, claim implication, inverse compatibility, forward
  sensitivity, typed budgets, conditional verification plans, typed topology,
  and four temporal-delta classes. These claim contracts, solvers, and
  observation capsules are not runtime features yet. Graded score bounds remain
  secondary, and probability or partial-identification language remains gated
  on a coherent joint evidence law and observation kernel.
- Formalized the four snapshot claim states as a two-coordinate knowledge
  lattice. The proposed merge unions canonical provenance ledgers, recomputes
  rule closure and certificates, and produces a monotone state projection for
  reviewed monotone rules. The projection is not assumed to preserve joins
  because premises can be split across views. Expiry and retraction require
  ledger replay. This is a research contract, not a new public output.
- Corrected Bayesian terminology across CLI, panel, MCP, schema, source
  documentation, assurance records, and validation memos. `slug_confidences`
  are documented as additive evidence-strength scores, network means as exact
  only for the committed manually encoded, partly corpus-informed model,
  `interval_low` and
  `interval_high` as evidence-responsive uncertainty bands rather than credible
  intervals, and `entropy_reduction_nats` as signed marginal entropy change.
  Stable field names and shapes are unchanged.
- Made declarative Bayesian absence collection-aware. Transient apex TXT,
  DMARC, and MTA-STS DNS failures, MTA-STS policy-fetch failures, and whole DNS
  source failures now mask only the affected declarative evidence units instead
  of becoming negative evidence. Successful `NXDOMAIN` and `NoAnswer` responses
  remain observed empty results. New granular channel markers surface through
  `degraded_sources`, set `partial` for core DNS channels, and retain the
  existing one-level confidence downgrade for degraded collection.
- Aligned declarative inference with its provenance: every applied non-neutral
  public absence, including weak MTA-STS nonfire, now contributes to effective
  display mass, appears in unit counterfactuals, and sets
  `absence_informative`. Transient MTA-STS HTTP 408, 429, and 5xx responses are
  unobserved degradation; a stable 404 remains an observed invalid policy.
- Fixed per-slug evidence-strength prior selection so A and CNAME observations
  use their configured `(2, 2)` prior instead of being shadowed by the unknown-
  source default. Mixed-source scoring remains deterministic and order-
  independent.
- Expanded the product-quality ablation to compare deterministic abstention,
  per-slug evidence strength, the strongest reviewed evidence unit, and the
  full Bayesian network. Added dependent follow-on gates for a
  provenance-constrained robustness prototype and CT graph qualification.
- Removed the expired PyJWT advisory exception from CI and release dependency
  audits after PyJWT 2.13.0 cleared the unqualified frozen-runtime audit.
- Corrected source documentation to distinguish the default target-visible
  MTA-STS policy fetch from opt-in CSE and BIMI direct probes.
- Made validation inference reproducible by pinning benchmark, reference,
  tenancy, and posture harnesses to committed priors. DMARC reference labels
  now distinguish successfully observed no-record negatives from collection
  failures, and reliability bins no longer split tied scores. Naive iid
  bootstrap and Wilson ranges are labeled as diagnostics without coverage
  claims.
- Reframed current conformal results as dependent empirical re-split
  diagnostics until scorer-development disjointness is established. Synthetic
  calibration and Bayesian layer ablation are now explicitly independent-
  Bernoulli misspecification stress tests, and differential verification claims
  only the configurations it actually sweeps.
- Added model-relative cohort field aliases `mean_model_score` and
  `high_score_share`. Hideable M365 and Google entries now report whole-cohort
  model support coverage and unresolved share, while the legacy prevalence and
  lower-bound fields remain null because evidence-selected denominators cannot
  estimate deployment prevalence.
- Added additive explanation-DAG completeness diagnostics and additive delta
  incompleteness diagnostics. The DAG reports unreachable terminal claims;
  delta reports endpoint-specific degraded sources and the additions, removals,
  or dependent scalar changes withheld as unconfirmable.

### Fixed

- Corrected the resolver API documentation to state the enforced 120-second
  aggregate default timeout rather than the obsolete 60-second value.
- Made human service disclosure additive and documented its stable behavior.
  Default, verbose, and full panels now retain one compact Email row containing
  observed provider, gateway, and principal control facts before any secondary
  email indicators. Verbose and full add detail without removing those facts.
  Possible downstream providers retain their evidence-role qualifier, and MX
  gateway fingerprint aliases collapse into the canonical topology label using
  only collection-observable evidence. A degraded MX channel therefore cannot
  hide or overstate a surviving TXT indicator.
  `--services` remains accepted for compatibility because Services are
  already shown by default, and help, onboarding, stability guidance, and the
  full-panel golden now state and test that contract.
- Made interactive diagnostics quieter and more dependable. `--debug` now
  enables both owned logger namespaces, installs one identifiable CLI stderr
  handler per namespace without duplicating it on repeat configuration, and
  does not leak records into host root handlers. Explicit direct handlers
  installed by an embedding host remain under that host's control. Lookup
  progress uses one deterministic, outcome-neutral message instead of rotating
  through phases that may not be running; chain mode has its own
  operation-specific label. The default panel now wraps its passive-DNS
  limitation cue within the 78-column content width with stable continuation
  indentation.
- Kept single-domain output and failure channels machine-safe and truthful.
  `--full --json` and `--verbose --json` now keep human source diagnostics on
  stderr instead of prefixing an otherwise successful JSON payload. Structured
  resolver timeouts and all-source failures preserve their concrete message and
  exit 4 as caught pipeline failures; exit 3 is reserved for completed
  collection with no reportable data. Verbose source rows now distinguish
  `match`, `no match`, and `error`, so a clean negative observation is not
  painted as a failed source. The welcome banner and stable flag docs describe
  `--verbose` as expanded evidence and per-source status and show `--posture`
  separately.
- Kept apex claims scoped to apex evidence. Related-domain enrichment can add
  inventory observations, but its evidence, failures, and declarative controls
  no longer change the queried apex's posture, confidence, or email-control
  claims. Legacy cached catalog slugs without retained role lineage remain
  visible as role-unavailable details and cannot create multi-cloud rollups.
- Repaired cached ephemeral-fingerprint reevaluation with deterministic,
  network-free DNS replay for supported TXT, SPF, MX, NS, and apex or `www`
  CNAME observations. Replay preserves original evidence, respects unavailable
  channels, deduplicates results, and rejects unsupported owner-qualified
  replay types explicitly.
- Reserved parser-owned semantic names and slugs from custom and ephemeral
  fingerprint registration, preventing extension labels from impersonating
  DMARC, DKIM, SPF, CAA, email-topology, or provider-identity facts.
- Corrected DMARC candidate isolation. A record with an invalid or missing
  `p=` tag remains explicit `dmarc-invalid` evidence and cannot emit the DMARC
  service, policy fields, aggregate-reporting vendor fingerprint, or email
  control credit merely because its `rua=` address is syntactically valid.
- Completed multi-channel detector failure projection. Microsoft 365 CNAME
  detection now also masks its partial SRV contributions on failure, while IdP
  hub and Exchange endpoint detection mask partial A contributions as well as
  CNAME contributions. A failed detector can no longer leave an earlier
  channel-specific claim reportable.
- Removed unsupported organization-size, Microsoft license-tier, and endpoint-
  fleet conclusions from generated insights. Tenant-domain cardinality and
  security, device-management, and network-security matches now remain exact
  public-indicator observations. Gateway prose now requires the MX-backed
  topology field and no longer invents a downstream delivery path from generic
  provider slugs. Federated identity output no longer guesses ADFS, Okta, or
  Ping when the external IdP is unidentified; separate vendor matches remain
  indicators. Email-security prose no longer credits DKIM from a gateway plus
  enforcing DMARC, and Google Workspace module matches are labeled as observed
  indicators rather than active modules. Same-version legacy cache entries keep
  their raw insight data, while the collection-observable reporting view hides
  removed claims from current CLI, MCP, JSON, Markdown, and panel output.
- Prevented unavailable granular DNS channels from becoming absence evidence in
  structured and panel output. In particular, MX collection failures now
  withhold no-email and MX-dependent sparse-footprint insights; bounded
  channel-owned insight prefixes cover DMARC, DKIM, apex TXT, MX, and CAA
  conclusions without broad substring filtering. Provider and explanation
  summaries use only evidence from available channels while retaining raw
  evidence as provenance.
- Made temporal delta comparison collection-aware at both endpoints. Previous
  degradation can no longer create confirmed additions, current degradation can
  no longer create confirmed removals, and dependent DMARC, email-score,
  identity, domain-count, or confidence changes require the relevant
  opportunities at both snapshots. CT-only degradation does not suppress
  unrelated identity scalars. Signal deltas are explicitly best-effort until
  snapshots carry stable signal IDs and interpretation manifests.
- Repaired explanation-DAG evidence identity and topology. Record-local indexes
  no longer collide with global evidence occurrences, fired-rule nodes are
  terminal-scoped, and evidence links only to an exactly matching retained rule
  occurrence. Composite or source-status rules without that exact association
  remain terminal metadata instead of receiving Cartesian evidence links.
  Incomplete provenance remains explicit instead of becoming reachable through
  unrelated evidence or a shared rule label.
- Corrected cross-domain semantics. Shared administrative tokens now report
  exact reuse without inferring a shared account or operator; shared tenant IDs
  are provider-attested administrative co-tenancy, not ownership proof; generic
  issuers and parent vendors are lower-specificity coincidences. The adaptive
  shared-slug denominator now includes empty batch rows, the runtime and schema
  agree on the three-slug threshold, and graph and token caps are disclosed.
  Cross-domain token, slug, and BIMI correlation now consumes the
  collection-observable view, while normalized BIMI organization keys make
  ecosystem output invariant to input order.
- Documented merge-candidate confidence as source-result completeness rather
  than field reliability and disclosed the six-field conflict-coverage limit.

- Grouped inference confidence by canonical claim. Record types and successful
  sources for unrelated slugs no longer combine into stronger inference, and a
  Google authentication observation no longer corroborates a separate
  Microsoft tenant ID. Two record types or sources for one claim produce
  medium confidence; three record types, or OIDC plus independent Microsoft
  tenant evidence, produce high confidence. Duplicate result objects from one
  source count once, and source results carrying an error cannot contribute
  merged data or confidence. Google Workspace CSE evidence correctly supports
  the canonical Google Workspace claim. All source-status views apply the same
  error-safe contributor rule. Confidence explanations now identify the winning
  claim, qualifying source types and sources, and only that claim's evidence.
- Escaped source-derived service labels, posture observations, and explanation
  text at every Markdown sink using the complete CommonMark punctuation set,
  including pre-existing backslashes. Dynamic text can no longer introduce
  block structure, links, HTML, code spans, or emphasis. Markdown service
  groups now form a single
  partition, exact Microsoft 365 fallbacks no longer misclassify generic DKIM
  or unrelated Microsoft products, Google Workspace DKIM remains grouped with
  its provider, and the Microsoft 365 US Government cloud label remains in the
  Microsoft 365 section. CommonMark hard breaks no longer depend on trailing
  spaces and appear only between adjacent lines.
- Removed unsupported Microsoft Copilot and Google Gemini service labels that
  were inferred solely from Microsoft 365 or Google Workspace presence. Direct
  AI domain-verification evidence continues to render normally.
- Unified provider-line derivation across panel, JSON, CSV, MCP text, and chain
  output. TXT-only account evidence no longer appears as an email secondary,
  and chain panels no longer append an explanatory unknown-provider label.

## [2.3.9] - 2026-07-10

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Changed

- Reframed the canonical roadmap around evidence-semantic integrity, an
  isolated MCP v2 beta compatibility matrix, and a reproducible product-quality
  baseline. Publication and process work now remains a separate maintainer
  track instead of defining product priority.
- Corrected stale or misleading documentation about MCP v2 availability,
  bundled AI inference, sovereignty unknown-state behavior, CT cache lifetime,
  batch concurrency, fingerprint-catalog size, ephemeral fingerprint behavior,
  runtime dependency count, and the interpretation of public-evidence scores.
- Replaced the completed interface-migration detail in the active roadmap with
  graph-backed hotspot, acceptance, and stop-rule guidance; historical shipped
  work remains in the changelog, roadmap history, and ADRs.

### Fixed

- Preserved interpreter-bound MCP launcher JSON verbatim in `mcp install
  --dry-run`; Rich markup no longer consumes the launcher's Python list
  expression and produces an unusable manual preview.
- Corrected live MCP instructions and tool descriptions to disclose the default
  target-visible MTA-STS fetch, distinguish opt-in CSE and BIMI requests, and
  describe the 0-100 compatibility value as a model-bound public-evidence index
  rather than an overall security score.
- Replaced the stale hard-coded MCP startup tool count with an explicitly
  selected-tool label.

## [2.3.8] - 2026-07-10

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes.

### Fixed

- **Version-independent JSON nesting bounds.** Client configuration and delta
  snapshot readers now perform a deterministic string-aware structural depth
  scan before decoding. This preserves the 100-level nesting ceiling on Python
  releases whose JSON decoder can parse deeply nested arrays without raising
  `RecursionError`, while ignoring brackets inside escaped JSON strings.

## [2.3.7] - 2026-07-10

### Tool Surface Changes

Tool surface changes: no CLI command or flag changes. The existing
`reevaluate_domain` MCP tool is now correctly advertised as stateful because it
replaces a cached result.

### Changed

- Expanded the rotating CLI lookup status messages with more varied, still
  professional wait-screen copy across DNS, certificate, identity, inference,
  posture, and passive-observation phases.
- Added a scheduled and manually runnable provider-drift workflow that runs the
  passive live integration smoke suite against public reserved-domain fixtures,
  giving upstream DNS, certificate transparency, and identity-endpoint changes a
  visible non-default gate.
- Added optional compact-output caps for MCP graph tools:
  `get_infrastructure_clusters(member_limit_per_cluster=...)` and
  `export_graph(node_limit=..., edge_limit=...)`. The default zero-cap path
  still returns the raw bounded graph payload, while compact calls report
  omitted counts and deterministic selection rules.
- Added `cluster_verification_tokens(peer_limit_per_domain=...)` for compact
  batch-correlation output with per-domain omitted counts and a raw-request
  pointer.
- Added `chain_lookup(result_limit=...)` for compact recursive-domain output
  while keeping the zero-limit raw JSON response unchanged.
- **MCP client installation is interpreter-bound.** `recon mcp install` now
  always persists the Python interpreter running the installer plus the
  existing sys.path-stripping launcher. Generated client configuration no
  longer depends on a later shell PATH lookup resolving the same installation.
- **BIMI certificate observations no longer imply identity.** The opt-in direct
  probe records a syntactically plausible PEM certificate document, but does
  not promote unverified subject fields into the stable nullable
  `bimi_identity` field. That field is reserved for a future source that
  validates the certificate chain and VMC profile.

### Fixed

- **RFC 9989 DMARC testing-mode alignment.** recon now parses DMARC `np=`
  and `t=` tags internally, and `t=y` lowers the effective DMARC enforcement
  level used by scoring and Bayesian signals without expanding stable JSON or
  MCP output fields. The disk cache schema version was bumped so pre-change
  cached records cannot preserve stale over-enforcing DMARC scores.
- **DMARC parser compatibility.** Invalid or missing `p=` tags with a valid
  aggregate-reporting `rua=` address now fall back to monitoring mode
  (`p=none`), while malformed DMARC version values such as lowercase
  `v=dmarc1` are ignored and only a leading exact `v=DMARC1` tag identifies a
  DMARC policy record.
- **Effective-policy signal contexts.** CLI explanation and MCP server signal
  evaluation now build metadata through the canonical tenant-info context, so
  gateway gap signals use the effective DMARC policy rather than only the raw
  published policy.
- **Bounded local JSON ingestion.** MCP client configuration and delta snapshot
  readers now cap bytes, reject excessive nesting and numeric values, require
  consumed snapshot fields to have their documented shapes, and report clean
  errors instead of propagating parser failures.
- **Bounded certificate-transparency retention.** CertSpotter aggregation now
  enforces one total retained-name ceiling across all admitted certificate
  entries instead of multiplying the per-entry cap across a response page.
- **Bounded process-local regex complexity.** Process-injected fingerprint patterns
  now permit at most one repetition operator in addition to the existing
  length and structural checks. Catalog regex validation moved into a focused
  module without changing built-in matching behavior.
- **MCP cooldown consistency.** A started lookup now retains its short
  per-domain cooldown after failure or cancellation, preventing repeated
  immediate work from bypassing the limiter.
- **Unicode display normalization.** Output sanitization now removes invisible
  bidirectional formatting controls while preserving ordinary international
  text.
- **Exact release-tag push.** The release helper pushes `main` and only the tag
  created for the reviewed version, rather than every local tag.
- **MCP configuration diagnostics.** Client checks no longer perform filesystem
  metadata calls on commands supplied by workspace configuration and report
  network-path commands without probing them.

## [2.3.6] - 2026-07-09

### Tool Surface Changes

No CLI command or flag additions or removals. Ambiguous `--exposure --gaps`
invocations now fail validation instead of selecting one mode by branch order.

### Changed

- **Typed lookup options model.** The Typer lookup command now translates raw
  flags into a structured `LookupOptions` object at the CLI boundary, reducing
  the async lookup implementation from a 34-parameter signature to `domain` plus
  one coherent options value.
- **Centralized lookup mode validation.** Output, display, operation, inference,
  and execution options now carry their own normalization and validation rules,
  with focused tests covering full/profile normalization and mutually-exclusive
  mode combinations.

### Fixed

- **Ambiguous exposure and gap mode selection.** `recon lookup <domain>
  --exposure --gaps` now exits with the validation error `--exposure and --gaps
  are mutually exclusive`, matching the rest of the lookup mode surface.

## [2.3.5] - 2026-07-09

### Tool Surface Changes

No CLI command or flag changes.

### Changed

- **Interface locality ratchet tightened.** The local layout guard now rejects
  resurrected monolith filenames such as `cli.py`, `formatter.py`, and
  `server.py` beside the package-local interface modules, with focused tests
  for the guard.
- **Package-local documentation sharpened.** Live interface-layer docstrings now
  describe the current `cli/`, `formatter/`, `server/`, and `mcp_client/`
  package boundaries instead of the retired flat-module names.

### Fixed

- **Manual update hint accuracy.** `recon update --check` no longer says
  `or just: recon update` for retired Homebrew installs or editable checkouts
  that require manual action.

## [2.3.4] - 2026-07-09

### Tool Surface Changes

No CLI command or flag changes.

### Changed

- **Homebrew release surface retired.** The project no longer ships or checks a
  Homebrew formula or maintainer tap workflow; supported package-manager paths
  remain `uv tool`, `pipx`, and `pip`.

## [2.3.3] - 2026-07-08

### Tool Surface Changes

No CLI command or flag changes.

### Changed

- **Interface package locality.** CLI, formatter, MCP server, and MCP client
  implementation now live under package-local modules, with historical
  top-level imports retained as compatibility shims and guarded by the local
  interface-layout check.

### Fixed

- **Remote release-readiness Scorecard floor.** The remote gate now treats
  Scorecard SAST `7` as the documented floor for scheduled/manual CodeQL, while
  keeping the other code-owned Scorecard controls pinned at `10`.

## [2.3.2] - 2026-07-08

### Tool Surface Changes

No CLI command or flag changes.

### Changed

- **Release metadata refreshed.** Citation metadata, supply-chain verification
  snippets, and roadmap status now point at v2.3.2 for the CI posture hotfix
  package.

### Fixed

- **CodeQL CI trigger alignment.** The CodeQL workflow is back to scheduled and
  manual runs, matching the Scorecard posture guard that keeps normal push CI
  focused on the main lint, test, audit, secrets, and Scorecard checks.

## [2.3.1] - 2026-07-04

### Tool Surface Changes

No CLI command or flag changes.

### Changed

- **Homebrew tap published.** The formula is now available at
  [`blisspixel/homebrew-tap`](https://github.com/blisspixel/homebrew-tap),
  so `brew install blisspixel/tap/recon` works without a manual checkout.
- **Accurate fingerprint count in MCP tool descriptions.** The `lookup_tenant`
  and fingerprint-listing tool docstrings now report "800+ fingerprints"
  instead of a stale "185+", matching the current catalog.

### Fixed

- **`discover_fingerprint_candidates` no longer poisons the shared cache.** A
  `skip_ct=True` mine resolved without certificate-transparency data but wrote
  that CT-degraded result into the shared per-domain cache, so a following
  `lookup_tenant`, `export_graph`, or `get_infrastructure_clusters` on the same
  domain could return confidently-wrong "no cert data" for the cache TTL window.
  A `skip_ct` result is now used locally without being shared.
- **`reevaluate_domain` errors no longer leak raw exception text.** A merge
  failure now returns the request_id and exception class name (and logs the
  traceback server-side), matching the other MCP tools, instead of embedding
  `str(exc)` in the client-facing message.
- **A cached re-merge no longer extends data freshness.** `cache_refresh_info`
  (used by `reevaluate_domain` and ephemeral-fingerprint clears) kept the
  re-merged result but reset the entry's fetch timestamp, so repeated re-merges
  could serve DNS data older than the intended TTL window. The original
  timestamp is now preserved.

## [2.3.0] - 2026-07-03

### Tool Surface Changes

No CLI command or flag changes.

### Added

- **Fingerprint catalog: Uptime.com and ngrok.** Surface attribution now
  recognizes Uptime.com hosted status pages (CNAME to `cname.uptime.com`) and
  ngrok custom-domain edges (`*.ngrok-cname.com`), both backed by vendor
  documentation and covered by regression tests.
- **Fingerprint freshness tracking.** Detection rules now accept an optional
  `verified` date (`YYYY-MM-DD`), and `python -m validation.audit_fingerprints
  --freshness` reports verified-date coverage and stale-rule counts. The date is
  advisory and does not affect matching. The catalog growth and quality plan is
  documented in [docs/catalog-strategy.md](docs/catalog-strategy.md).

### Fixed

- **MCP lookup errors are now debuggable, and a cancelled resolve no longer
  rate-limits the retry.** When a resolve failed unexpectedly, the MCP tools
  returned a generic "an internal error occurred" with no request_id and no
  error class. They now include the request_id (to correlate with the server log
  that holds the full traceback) and the exception class name, without leaking
  the message text. Separately, a cancelled resolve (client cancellation,
  shutdown, or timeout) now releases the per-domain rate-limit slot it acquired
  instead of leaking it, so an immediate retry is not spuriously rate-limited.

## [2.2.19] - 2026-07-03

### Tool Surface Changes

No CLI command or flag changes.

### Changed

- **Source hygiene guard.** Source hygiene now rejects placeholder-style
  incomplete-code phrasing such as reserved-for-future assignments, and the
  formatter insight curator no longer carries unused parameters for speculative
  tuning.
- **Compact subdomain surface summary.** The default panel's `Subdomain` row
  now uses aligned wrapped rows so a large provider count does not hide other
  detected surface providers behind a single overflow marker.
- **Fingerprint catalog refinement.** Surface attribution now recognizes
  Marketo tracking-link CNAME targets and OCI WAF / WAAS CNAME targets found
  during local passive fingerprint-mining rounds.
- **Fingerprint catalog refinement.** Surface attribution now recognizes
  Transcend consent-sync CNAME aliases and Queue-it waiting-room CNAME targets
  found during local passive fingerprint-mining rounds.
- **Fingerprint discovery tooling.** Candidate triage now mirrors runtime
  DNS-label-aware `cname_target` matching so future mining rounds do not hide
  service-specific CNAME variants behind broader substring matches.
- **Bayesian evidence grouping.** The correlation-group over-counting
  correction now covers the `aws_hosting` and `email_gateway_present` nodes, so
  a target exposing several redundant AWS facets (or gateway vendors) no longer
  receives an over-confident posterior with a too-tight credible interval. This
  matches the existing Microsoft 365 and Google Workspace grouping.
- **Fingerprint catalog refinement.** Surface attribution now recognizes the
  Marketo `mktoapps.com` landing-page backend and the Edgecast/Edgio
  `zetacdn.net` CDN domain, both found in a 2026-07 passive fingerprint-mining
  round and added to their existing vendor entries with public references and
  regression tests.
- **MCP subdomain surface summary.** `lookup_tenant` text output now includes
  the same compact provider-count summary used by the default panel, so agents
  see multiple attributed subdomain surfaces without switching to JSON.
- **Subdomain surface documentation.** The architecture and MCP docs now
  clarify which output modes show compact provider counts, per-subdomain
  details, structured `surface_attributions`, and unclassified-chain hints.
- **Host-suffix security hardening.** Exchange DKIM tenant extraction and
  Microsoft cloud-instance insights now use DNS-label-aware suffix matching
  instead of raw string suffix or substring checks.
- **Cost-surface guard.** The local gate and CI now enforce that packaged
  runtime code, wheel packaging, project dependencies, and workflows do not
  introduce paid-provider SDKs, model API keys, image API calls, or
  validation-only paid harness invocations.
- **Submission-freeze proof refresh.** The local public proof memo and
  external write-up plan now cite the current smoke and full proof runs from
  the cost-surface-guarded checkout.
- **File-size ratchet.** The formatter module ceiling is tightened to its
  current size so future growth remains visible in the local and CI gates.

### Fixed

- **Bad `recon batch` input and `recon discover --output` errors now report
  cleanly instead of crashing.** A non-UTF-8 batch file (or stdin) raised an
  uncaught decode error that read as an internal bug; it is now rejected with
  exit 2. Writing `recon discover --output` to a directory or an unwritable path
  is likewise reported cleanly with exit 2 rather than reaching the
  "please report a bug" handler.
- **`--md` is now rejected with `--exposure`, `--gaps`, `--chain`, and
  `--compare` instead of being silently dropped**, matching how `--plain` is
  already handled for those modes.
- **`recon <domain> --profile <unknown>` now exits 2, not 4.** An unknown
  profile (or an invalid `--explain-dag-format`) is a validation error, but the
  deliberate exit was caught by the lookup command's generic handler,
  reclassified to the internal-error code, and printed as a bare `Exit` line.
- **`recon batch --ndjson` no longer prints a human notice to stdout.** A
  duplicate input domain emitted a "N duplicate(s) removed" line into the ndjson
  stream, breaking line-by-line JSON parsers. The notice is now suppressed for
  ndjson as it already was for `--json`, `--md`, and `--csv`.
- **`recon batch --md` no longer leaks an internal error sentinel.** A resolve
  failure in markdown mode echoed a NUL byte and an internal `ERR:` marker into
  stdout. The error is now surfaced on stderr like the default panel, keeping the
  markdown output clean.
- **`recon doctor` now signals check failures through its exit code.** A failed
  core check (identity endpoint, DNS, catalog load, or schema field) exits 1,
  while an all-pass run or an optional-enrichment-only degradation (for example
  a crt.sh outage) exits 0, so a CI or monitoring job can gate on `recon doctor`
  instead of always reading success. The rendered summary is unchanged.
  `recon doctor --mcp` likewise exits 1 when the MCP server cannot be validated
  (package missing, server import failure, or no tools registered) and 0 when the
  setup is healthy, so an MCP install script can gate on it too.
- **Strict-SPF signal now reaches the fusion layer.** The
  `email_security_policy_enforcing` node's `spf_strict` evidence is derived from
  the merged service set where strict SPF (`-all`) is actually recorded, instead
  of an SPF-typed evidence record that the DNS pipeline never produced. The
  signal previously could not fire in production.
- **Dot-less CNAME fingerprint spoofing.** Dot-less `cname_target` fragments
  (such as Marketo's `mkto-`) now match only at a DNS-label or hyphen boundary,
  so a host that merely embeds the fragment mid-label (for example
  `promkto-analytics.attacker.net`) is no longer mis-attributed to the vendor.
- **Prior-override validation on the argument path.** A prior supplied directly
  to `infer(priors_override=...)` is now range-checked like a file-supplied one,
  so a value of 0, 1, or outside `(0, 1)` is ignored rather than building a
  degenerate or invalid inference factor. A boolean calibration value is also
  rejected instead of being silently coerced.
- **DMARC partial rollout scored as full enforcement.** The
  `email_security_policy_enforcing` fusion signal now applies the DMARC `pct=`
  coverage tag: a monitoring-only `pct=0` record no longer counts as full
  `reject`, and a partial rollout (`0 < pct < 100`) steps the policy down one
  level, so a phased-rollout domain is not overstated as fully enforcing.

## [2.2.18] - 2026-06-30

### Tool Surface Changes

- Tool surface changes: no CLI command or flag changes.

### Changed

- **DMARC standards currency.** Comments, validation notes, and DMARC tests now
  reference the current RFC 9989 protocol specification and RFC 9990 aggregate
  reporting split instead of the obsolete RFC 7489 citation.
- **MCP security guidance currency.** External write-up control docs now pair
  the MCP security best-practices guidance with the current 2025-11-25
  authorization specification.
- **Artifact-attestation guidance currency.** External write-up and freeze
  docs now cite GitHub's current artifact-attestation how-to path.
- **Agent working-directory hygiene.** Maintainer-loop and generated
  surface-inventory guidance now point agent scratch records at the root
  `.agent/` directory.
- **Repository hygiene guard.** Tests now lock the root `.agent/` and `logs/`
  ignore contract and reject tracked root-package shadow paths.
- **Pass-statement hygiene.** The source-hygiene test now covers tests as well
  as runtime and maintainer Python, and the remaining test-only pass statements
  were replaced with explicit no-op control flow.
- **Secrets-scan workflow contract.** Scorecard posture tests now pin the
  gitleaks workflow to full-history checkout, read-only permissions, and
  explicit finding-fail behavior.
- **Placeholder-marker hygiene.** Source hygiene now rejects common unfinished
  code markers in runtime, maintainer, validation, and test Python.
- **Submission-freeze local proof.** Added a public proof memo for the current
  local submission-freeze smoke and full reproduction runs.
- **Submission-freeze proof refresh.** Added the 2026-06-30 public proof memo
  after rerunning the public smoke and full paper profiles plus ancillary
  validation gates.
- **Proof-pointer currency.** Claim-audit guards and research docs now point to
  the latest local submission-freeze public proof memo while preserving the
  final claim-audit refresh boundary.
- **OpenSSF badge readiness.** Added questionnaire answer discipline so badge
  evidence stays public, source-backed, and separate from Scorecard signals.
- **OpenSSF posture refresh.** Updated Scorecard posture docs from the
  2026-06-30 public API recheck for the pushed submission-freeze proof refresh
  state.
- **Scorecard snapshot churn guard.** OpenSSF posture docs now avoid turning a
  live Scorecard API check into a durable commit-hash promise.
- **External status claim guard.** Public status surfaces now have a regression
  check against placeholder DOI, archive, OpenSSF badge, contributor-diversity,
  and outside-replication completion claims.
- **Archive metadata stop rules.** Archive readiness now treats `.zenodo.json`,
  preferred citations, and DOI metadata as release-policy changes backed by
  explicit tests.
- **Replication outcome discipline.** The public replication runbook now
  constrains future outside-replication notes to aggregate command outcomes and
  reviewed environment details.
- **Scorecard publication guard.** Maintenance checks now lock the Scorecard
  workflow to public result publishing, SARIF export, and bounded artifact
  retention.
- **Remote-readiness wording.** Strategic gap docs now distinguish the
  published remote baseline from local commits that still need push and remote
  readiness reruns.
- **Consumer provenance recipe.** Supply-chain docs now include a short
  consumer verification path for GitHub release assets, exported attestations,
  SBOM assets, and PyPI-hosted provenance.
- **Supply-chain recipe freshness.** Release readiness now fails if the
  consumer provenance recipe drifts from the current package version or omits
  required verification anchors.
- **Release documentation parity.** Release, artifact-review, and agentic-loop
  docs now name the supply-chain recipe freshness check in the local readiness
  gate.
- **PyPI recipe version guard.** The supply-chain freshness check now covers the
  Python snippet that reads PyPI file URLs, not only the shell release asset
  variable.
- **Remote evidence refresh.** Strategic gap docs now record that the pushed
  hardening stack has current remote CI, Scorecard, PyPI, GitHub Release, and
  provenance checks passing.
- **Root-anchored scratch hygiene.** The `.agent/` and `logs/` ignore rules are
  now root-anchored, tests verify nested scratch directories are not silently
  ignored, and the stale local documentation-nested agent workspace copy was
  removed.
- **Local tool artifact hygiene.** Repository hygiene tests now verify common
  local cache and environment artifacts stay ignored and untracked.
- **Fingerprint CLI coverage and JSON hygiene.** The `fingerprints test --json`
  command now emits machine-readable JSON without a human banner, its default
  example corpus lookup points at the repository fixture during contributor
  runs, and focused CLI tests cover list, search, show, new, test, and check
  paths.
- **Signals CLI coverage.** Focused CLI tests now cover signal list, search,
  and show behavior, including JSON output, validation exits, no-match paths,
  and Rich text rendering under terminal wrapping.
- **Fingerprint validator coverage.** Focused validator tests now cover shape
  errors, YAML parse failures, empty directories, duplicate-slug semantics,
  specificity failures, skip-specificity behavior, bare-list input, and the
  script entrypoint.
- **OpenSSF questionnaire manual queue.** Badge readiness docs now separate
  repository-file evidence from live process facts such as issue response
  history, vulnerability response history, maintainer attestations, and
  cryptography applicability.
- **Replication handoff packet.** The public replication runbook now defines
  the exact outside-reviewer request fields, environment notes, outcome notes,
  and redaction boundaries for a clean-machine public-artifact rerun.
- **Archive path decision packet.** Archive readiness now defines the fields
  required before adding DOI language or Zenodo metadata, including the frozen
  release object, metadata authority, proof state, and data boundary.

## [2.2.17] - 2026-06-29

### Tool Surface Changes

- Tool surface changes: no CLI command or flag changes.

### Changed

- **Package-visible wording cleanup.** CLI help, JSON Schema descriptions,
  validation docs, and release-readiness fixtures now use neutral
  `/recon-fingerprint-triage` wording without naming a specific assistant
  client where the client is not part of the behavior.
- **Agentic UX runbook portability.** The v1.9.9 agentic-UX runbook now points
  maintainers at configured provider and model environment variables instead of
  pinning stale model-specific cost guidance.

## [2.2.16] - 2026-06-28

### Tool Surface Changes

- Tool surface changes: no CLI command or flag changes.

### Added

- **Adversarial add/remove perturbation proof.** `validation.adversarial_properties`
  now reports aggregate paired evidence-removal and planted-evidence movement
  over the shipped Bayesian network, and the public reproduction bundle has an
  aggregate-only memo for the full paper profile run.
- **Paper claim audit gate.** `scripts/check_paper_claims.py` now runs in the
  local CI mirror and keeps the paper draft, outline, claim map, artifact-review
  guide, and external write-up plan aligned.
- **Scorecard hardening tests.** Installer, workflow-pin, documentation, and
  Scorecard-posture tests now pin the repository's supply-chain posture and
  public-doc boundaries.

### Changed

- **Reader-facing roadmap focus.** The README and roadmap now present the
  current plan as hardening, small refinements, and humble external write-up
  readiness instead of leading with internal validation-track labels.
- **Dependency currency refresh.** `uv.lock` now resolves current compatible
  package versions, and the MCP dependency is bounded to the stable v1 line
  until the v2 line is production-ready for this project.
- **Public sampling boundary.** The public label snapshot decision now closes
  the public probability-sampling path for this submission: public-list numbers
  stay framed as robustness checks rather than population rates, benchmark
  prevalence, or evidence that transfers to the private curated cohort.
- **Documentation synchronization.** README, roadmap, docs index,
  artifact-review guide, data-handling policy, paper claim map, external
  write-up plan, and supply-chain docs now describe the same release focus,
  publication boundaries, and Scorecard posture.
- **Installer supply-chain posture.** The Unix and PowerShell installers no
  longer execute remote package-manager bootstraps. Users install `uv` or
  `pipx` through their trusted channel, then recon's installer installs or
  upgrades only `recon-tool`.
- **Scorecard workflow currency.** The Scorecard SARIF upload step now uses
  CodeQL Action v4, and live repository settings require full-SHA GitHub Action
  pins, dependency security updates, and an active `main` required-check
  ruleset.

## [2.2.15] - 2026-06-28

### Tool Surface Changes

- Tool surface changes: added flags `--timeout` on `recon batch`, `-t` on
  `recon batch`.

### Added

- **Equal-mass ECE estimator.** Validation calibration summaries now report the
  legacy fixed-width ECE beside an equal-mass, mean-confidence ECE with a
  deterministic 80 percent bootstrap interval, so future calibration reruns can
  separate estimator choice from model behavior without changing runtime
  surfaces.
- **External write-up readiness plan.** `docs/external-writeup-plan.md` now
  records the researched next step after C3 closure: citation metadata,
  public-reproduction smoke, claim-to-artifact mapping, and paper tightening
  without runtime surface expansion.
- **Citation metadata readiness gate.** `scripts/release_readiness.py` now
  checks `CITATION.cff` against the current `pyproject.toml` version and the
  matching `CHANGELOG.md` release date.
- **C3 CT validation plan.** `docs/c3-ct-validation-plan.md` now records the
  researched closure plan for the CT-enabled C3 track: seven-session aggregate
  state, public-provider limits, Infobip candidate disposition, and the rule
  that future live retries require a new concrete validation reason.
- **Schema generator drift gate.** `scripts/generate_schema.py --check` now
  verifies both published JSON Schema copies against code-owned required-field
  metadata and explicit conditional-field metadata, and CI enforces it.
- **Descope CNAME-target fingerprint.** The surface-attribution catalog now
  recognizes Descope custom-domain CNAME targets (`cname.descope.com` and
  `cname.euc1.descope.com`) as identity-surface bindings, backed by Descope's
  public custom-domain documentation and boundary tests.
- **Descope identity taxonomy.** The `descope` slug now maps to the Identity
  panel category and the exposure identity-provider view instead of falling
  through to the generic Business Apps fallback.
- **Infobip email-tracking surface attribution.** The surface catalog now
  recognizes Infobip's documented `email-messaging.com` tracking and sending
  host family as an `infobip` CNAME-target signal, with a lookalike boundary
  test.
- **Surface-inventory promotion decision.** ADR-0007 keeps
  `docs/surface-inventory.json` and `recon://surface-inventory` as generated
  discovery context, with a concrete-consumer gate before any 2.3 stable subset.
- **Batch timeout control.** `recon batch` now accepts `--timeout` / `-t`,
  matching `lookup` and `discover`, so corpus operators can bound each domain's
  resolve pipeline without changing the default 120-second behavior.

### Changed

- **Documentation front door refresh.** The README is now a shorter product
  front door with install, common commands, JSON/MCP pointers, limitations, and
  development gates. Detailed install workflow moved to
  `docs/getting-started.md`, the plain-language model overview moved to
  `docs/how-it-works.md`, the docs index is reorganized by reader task, and the
  roadmap is now a concise current-plan and invariant document instead of a
  shipped-history archive.
- **C3 planning docs clarified.** The README, docs index, roadmap,
  maintainer-validation notes, validation workspace guide, limitations,
  how-it-works overview, weak-areas guide, paper outline, and historical v2.0
  runbook now treat the C3 CT plan as closed and point current maintainer work
  at the external write-up plan.
- **Citation metadata refreshed.** `CITATION.cff` now tracks the current
  2.2.15 release version and 2026-06-28 release date.
- **Markdown house-style cleanup.** Tracked Markdown docs, examples, agent
  guidance, and validation memos now avoid em dashes, en dashes, pictographs,
  and literal AI-attribution phrases.
- **Homebrew formula freshness.** The bundled formula now points at the
  published `recon-tool` 2.2.14 sdist and sha256 from PyPI.
- **CT corpus sessions are recoverable partial runs.** `validation/scan.py` now
  passes the batch timeout through, supports `--max-runtime` for controlled
  partial NDJSON sessions, supports no-network `--finalize-existing` recovery of
  interrupted run directories, skips noisy diffs for partial scans, records
  valid streamed record counts in `meta.json`, and terminates the batch process
  tree on controlled timeout. The first recovered C3 partial aggregate is
  documented in `validation/2026-06-26-c3-ct-partial.md`.
- **C3 CT retry path is private and resumable.** `validation/scan.py
  --ct-retry-from` now accepts prior run directories, `results.ndjson`, or
  legacy `results.json`; skips malformed streamed tails; deduplicates retry
  domains; and writes synthesized retry inputs under the validated private
  output root instead of a public validation path. Synthesized retry domains are
  revalidated before writing so malformed prior records cannot inject extra
  corpus lines. The first bounded retry aggregate is appended to
  `validation/2026-06-26-c3-ct-partial.md`.
- **C3 CT session aggregation.** `validation/summarize_ct_sessions.py` now
  combines partial private CT sessions into aggregate-only JSON with raw outcome
  counts, best outcome by unique domain, and CT data coverage, without emitting
  domains, tenant IDs, organization names, or per-domain rows.
- **C3 Retry Session C.** A bounded retry completed the 33 CT-degraded records
  from Retry Session B, added one live CT success, and raised combined CT-data
  coverage to 40 domains out of 2,647 unique observed domains.
- **C3 live retry loop closed.** Retry Sessions D through F added four more
  live CT successes, raised aggregate CT-data coverage to 44 domains out of
  2,647 unique observed domains, promoted the public-source-backed Infobip
  email-tracking rule, and produced no new candidates in the final retry. The
  public memo now closes C3 as a bounded partial CT validation track rather than
  a full-coverage CT collection effort.
- **Infobip panel taxonomy.** The `infobip` slug now maps to the Email panel
  category instead of falling through to generic Business Apps.
- **C3 scan options reject incoherent retry recovery.** `validation/scan.py` now
  rejects `--finalize-existing` combined with `--ct-retry-from`, keeping
  no-network recovery separate from synthesized CT retry runs.
- **CT attempt-outcome accounting is more precise.** `breaker_open` is now
  reserved for failed CT attempts where every failed provider was stopped by an
  open local breaker. Mixed provider failures now surface the live attempted
  failure cause, such as `live_rate_limited` or `live_other_failure`, while
  keeping the existing best-effort enum.
- **DNS target attribution is more boundary-aware.** Microsoft 365, Microsoft
  Teams, Intune, Office ProPlus, Google Workspace module CNAMEs, and Google
  Workspace DKIM CNAMEs now match vendor targets by hostname suffix instead of
  raw substring. SRV matching parses the target host from the final SRV field
  and ignores explicit unavailable targets (`.`).
- **CT failure classification is less brittle.** Local max-wait `RateLimited`
  exceptions now classify as rate-limit outcomes even when wrapped, and
  non-429 HTTP errors that merely mention a numeric domain such as `429.com` no
  longer classify as rate limits.

### Fixed

- **Validation helper typing is clean under the broad Pyright pass.** Legacy
  validation analyzers and synthetic-corpus helpers now use typed JSON record
  aliases, avoid importing a private cache constant, type rendered TenantInfo
  snapshots, and pass DNS-only tenancy calibration results as `SourceResult`
  instances.

## [2.2.14] - 2026-06-26

### Tool Surface Changes

- No runtime CLI command or flag changes.

### Fixed

- **IdP names match by hostname suffix, not raw substring.** The OIDC/CSE
  (`google.py`) and federated-redirect (`google_identity.py`) IdP-name helpers
  matched vendor domains as substrings of the whole URL, so a lookalike host
  such as `notokta.com` or a vendor name in a path or query matched. Both now
  parse the URL hostname and match by exact host or dotted suffix. Display-name
  only; no schema or classification change.
- **Exchange Online DKIM attribution matches by hostname suffix.** A DKIM CNAME
  with `onmicrosoft.com` or `protection.outlook.com` as an internal label (for
  example `x._domainkey.onmicrosoft.com.example.com`) is no longer misread as a
  Microsoft 365 tenant. The match now requires the vendor host to be the
  record's suffix, validated against maintainer-local corpus evidence
  (aggregate-only memo in `validation/2026-06-26-onmicrosoft-suffix-match.md`).
- **Google identity routing checks the redirect host boundary.** The federated
  Google Workspace redirect classifier now parses the final URL and checks the
  hostname against `google.com` by exact host or dotted suffix. A lookalike host
  such as `evilgoogle.com`, or a `google.com` string in a path or query, no
  longer affects the Google-vs-third-party routing decision.

## [2.2.13] - 2026-06-26

### Tool Surface Changes

- No runtime CLI command or flag changes.

### Added

- **UltraDNS Web Forwarding surface attribution.** The surface catalog now
  recognizes `crs.ultradns.net` as UltraDNS Web Forwarding redirect evidence,
  scoped to infrastructure-tier routing rather than destination hosting.
- **Squarespace managed-subdomain surface attribution.** The surface catalog now
  recognizes `ext-sq.squarespace.com` as a Squarespace-hosted subdomain target,
  complementing the existing `ext-cust.squarespace.com` custom-domain rule.

### Changed

- **Homebrew formula freshness.** The bundled formula now points at the
  published `recon-tool` 2.2.12 sdist and sha256 from PyPI.
- **Fingerprint triage noise is lower.** `validation/triage_candidates.py` now
  checks sample terminals and CNAME chain hops against existing `cname_target`
  patterns, so bucketed suffixes do not keep already-covered endpoints as
  candidates.
- **Schema-source audits are easier to inspect.** `scripts/check_schema_sources.py`
  now has a `--json` mode that emits the top-level schema source map, intentional
  `TenantInfo` omissions, and issue lists for generator prep.

### Fixed

- **Profile `signal_boost` and `exclude_signals` now reweight observations.**
  These keys were matched against the rendered statement text and the built-in
  profiles keyed them by signal display names, so they never fired against the
  posture observations `--profile` actually reweights. Observations now carry
  their originating posture rule name, the profile engine matches `signal_boost`
  and `exclude_signals` against it (`exclude_signals` keeps the statement
  substring path for back-compat), and the built-in profiles reference real
  `data/posture.yaml` rule names. A new test asserts every built-in profile key
  names a real posture rule so stranded config cannot ship again. `--profile`
  salience and ordering shift where a boosted rule fires.
- **SPF complexity survives multiple SPF TXT records.** Malformed domains with
  more than one SPF record now report complexity from the largest observed
  include count instead of whichever SPF record DNS returned last.
- **Local text-hygiene check matches CI on Windows.** `scripts/check_text_hygiene.py`
  read git diff output in the platform locale, so on Windows (cp1252) an em dash
  decoded to other code points and went undetected while CI (UTF-8) flagged it.
  It now decodes git output as UTF-8 explicitly, with a regression test over the
  previously-untested git-diff path. Maintainer tooling only; no runtime change.

## [2.2.12] - 2026-06-25

### Tool Surface Changes

- No runtime CLI command or flag changes.

### Changed

- **The README license section is simpler.** It now points directly to Apache
  2.0 and the LICENSE file without a separate enterprise-contact sentence, and
  release readiness now fails if that wording returns.
- **Private validation run outputs now fail closed inside the repo.**
  `validation/run_calibration_bundle.py` and `validation/scan.py` reject
  in-repository output roots outside the gitignored private validation
  workspaces, while still allowing operator-local paths outside the checkout.
- **Maintainer-loop guidance now names side-effect and resume boundaries.**
  `docs/agentic-balance.md` and `docs/maintainer-loop-runbook.md` now require
  explicit action boundaries, resume keys, trace records, and maintainer
  approval before externally visible release, distribution, schema, CPT, or
  catalog changes.
- **The file-size ratchet tightened for two already-shrunk modules.**
  `scripts/check_file_size.py` now locks `exposure.py` at 981 lines and
  `merger.py` at 955 lines, preserving the shrinkage reported by the full local
  gate.

### Fixed

- **MCP setup guidance now matches the safe installer fallback.** `recon doctor
  --mcp` emits the same sys.path-stripping Python fallback that `recon mcp
  install` writes when `recon` is not on PATH, and `recon doctor --client`
  warns on hand-written `python -m recon_tool.server` launch blocks in client
  configs. The agent setup docs now prefer the installer or an absolute `recon`
  script path, and the Claude Code skill points at the stable v2.0 JSON
  contract with a valid schema link.
- **DMARC policy with whitespace around `=` is now parsed.** A spec-legal
  `p = reject` (RFC 7489 / 6376 tag syntax permits whitespace around `=`) was
  dropped, silently understating the email-security posture. The parser now
  splits each tag on its first `=` and strips both sides.
- **Trailing-dot FQDNs are accepted.** An absolute FQDN like `alpha.invalid.` was
  rejected as malformed; it now normalizes to the apex the same way the scheme,
  `www.`, and port paste-artifacts already do.
- **The retry transport no longer returns a closed response when the cumulative
  sleep cap trips.** Under repeated `429`/`503` with a `Retry-After` that reached
  the cap, the intermediate response was closed and then returned, so a caller
  reading its body got `StreamClosed` instead of the status. The response handed
  back on the cap path now stays readable.
- **`infrastructure_clusters` dominant issuer is deterministic.** The tie-break
  followed certificate arrival order (unstable across requests), so a two-issuer
  count tie could change the emitted `dominant_issuer` between runs. Ties now
  break by count, then lexicographically.
- **Geo-Distribution region matching no longer misses a valid region after a
  coincidental substring.** A label like `house1-use1` (where the region code
  `use1` also appears inside `house1`) lost its valid trailing match; the matcher
  now scans every occurrence, matching the sibling environment matcher.
- **Certificate-transparency subdomain ordering no longer over-ranks suffix
  coincidences.** The high-signal sort matched prefixes as suffixes (so `webapp`
  ranked high because it ends in `app`), skewing which subdomains survived the
  cap. It now uses the boundary-aware predicate already used during enrichment.
- **`--explain` provenance labels PKI and infrastructure insights correctly.**
  Any `Label: value` insight was routed to the generic signal classifier,
  leaving the dedicated `pki:` and `infrastructure:` rules unreachable.

## [2.2.11] - 2026-06-22

### Tool Surface Changes

- No runtime CLI command or flag changes.

### Fixed

- **Email-security score is now one definition shared by every surface.** The
  score (0-5) was computed in six places that diverged from the canonical
  exporter: they counted both DKIM service labels separately (a domain with
  Exchange Online and a generic DKIM selector scored DKIM twice) and credited
  raw `DMARC` presence instead of an enforcing policy. So `--exposure`, posture
  statements, and the MCP signal context could disagree with the top-level
  `email_security_score` JSON field for the same domain. All paths now route
  through a single `email_security_score` helper: DKIM counts once, DMARC counts
  only when the published policy is `reject`/`quarantine`. This extends the
  v2.2.10 delta fix to the remaining surfaces.
- **DMARC `rua` report-size suffix no longer pollutes the vendor domain.** An
  RFC 7489 `!<size>` suffix (e.g. `rua=mailto:reports@vendor.com!10m`) was folded
  into the parsed domain (`vendor.com!10m`); the address capture now stops at the
  `!` delimiter.
- **`recon delta` exit code on no data.** When a fresh resolve returned nothing,
  `delta` exited `4` (internal error) instead of `3` (no data), violating the
  exit-code contract every other command follows.
- **`delta` signal diffing recognizes humanized signal names.** Signal insights
  now render their matched products humanized (e.g. `Multi-Cloud: Amazon Web
  Services`), which the slug-shaped heuristic dropped, so real signal additions
  and removals went unreported. Signals are now identified by name.
- **`www.<tld>` registrable domains are no longer rejected.** Blindly stripping
  `www.` turned the real domain `www.com` into a bare TLD that failed validation;
  the strip now only fires when the remainder is still a valid domain.
- **Bare `host:port` input normalizes like the URL form.** `alpha.invalid:8443`
  was rejected on the stray colon while `https://alpha.invalid:8443` succeeded; the
  bare-host path now strips a trailing port too.
- **Atomic CT cache writes.** `ct_cache_put` now writes via a temp file and
  `os.replace`, matching the main cache: a concurrent reader can no longer see a
  half-written file and a pre-planted symlink target is not followed.
- **Deterministic SPF include-count parse.** The "SPF complexity: N" lookup now
  iterates in sorted order so a result never depends on set iteration order.
- **Homebrew formula freshness.** The bundled formula now points at the
  published `recon-tool` 2.2.10 sdist and checksum.

## [2.2.10] - 2026-06-21

### Tool Surface Changes

- No runtime CLI command or flag changes.

### Changed

- **License is now Apache 2.0.** recon moves from MIT to the Apache License 2.0
  (Author: Nick Seal, nick@pueo.io). Package metadata, the README, and the
  citation, plugin, Homebrew, and third-party-notice files are updated to match.

### Fixed

- **DMARC `rua` comma-separated addresses are no longer dropped.**
  `extract_dmarc_rua` now reads every address inside a comma-separated `rua=`
  tag (a valid RFC 7489 form), not just the first, so vendor fingerprints on the
  second and later report addresses are detected. Forensic `ruf=` addresses stay
  excluded.
- **Delta email-security-score consistency.** `recon delta` recomputed the live
  email-security score with a service-presence formula while the exported
  `email_security_score` field uses the policy-based formula, so a `p=none`
  DMARC domain reported a phantom score change against its own snapshot. Both
  paths now share the one exporter scorer.
- **Homebrew formula freshness.** The bundled formula now points at the
  published `recon-tool` 2.2.9 sdist and checksum.

## [2.2.9] - 2026-06-20

### Tool Surface Changes

- No runtime CLI command or flag changes; the generated `docs/cli-surface.md`
  reference now mirrors the existing command tree for release-note checks.
- MCP resources now include `recon://surface-inventory`, a no-network generated
  discovery snapshot matching `docs/surface-inventory.json`.
- CI now includes a SHA-pinned ClusterFuzzLite PR fuzzing workflow for local
  parser and serializer boundaries.

### Fixed

- **Docs currency.** Updated README, contributor, roadmap, engineering-practice,
  release-process, and supply-chain docs to reflect the local readiness gate,
  current coverage target, optional MCP positioning, Scorecard posture, and the
  remaining order of operations.
- **Maintainer automation guidance.** Captured the gate-first rule for any
  future maintainer loops: repeated task, bounded cost, persistent state, and an
  automated verifier before the loop is worth keeping.
- **Surface inventory drift gate.** Added a generated
  `docs/surface-inventory.json` manifest derived from the CLI command tree, MCP
  tool registry, and JSON schema, plus a local and CI check that fails when it
  drifts.
- **Generated CLI surface reference.** Added a drift-checked
  `docs/cli-surface.md` generated from the live Typer command tree so skill and
  agent authors can sync command and flag usage without copying README snippets.
- **MCP resource consumption examples.** Documented no-network reads for
  `recon://fingerprints`, `recon://signals`, `recon://profiles`, and
  `recon://schema` so agents can inspect capability context before domain
  analysis calls.
- **Surface inventory MCP resource.** Added `recon://surface-inventory`, a
  no-network resource that serves the packaged generated CLI, MCP,
  JSON-schema, and agent-integration inventory as discovery context, with drift
  tests keeping it byte-identical to `docs/surface-inventory.json`.
- **Maintainer context packet inventory.** Extended the generated surface
  inventory with the maintainer-loop context packet, including role metadata
  and path-existence checks for the files every loop must refresh.
- **ClusterFuzzLite parser fuzzing.** Added a Python Atheris fuzz target for
  domain normalization, control-byte stripping, cache deserialization, and
  formatter serialization, plus a read-only, SHA-pinned, runtime-bounded PR
  workflow and local config tests.
- **Calibration corpus preflight.** The maintainer-local calibration bundle now
  checks the consolidated corpus size and per-stratum `--min-cell` eligibility
  before any network harness starts, and dry runs report eligible and suppressed
  strata.
- **Maintainer loop runbook.** Added a compact CI triage, private calibration,
  and fingerprint proposal loop contract with ignored local state,
  deterministic gates, explicit stop conditions, spend tracking, and maintainer
  review boundaries.
- **Nested schema drift guard.** Added tests that bind model-backed JSON Schema
  `$defs` to their dataclass field sets, with explicit exceptions for
  intentionally omitted JSON fields.
- **Schema source-map guard.** Added `scripts/check_schema_sources.py` to trace
  every top-level JSON Schema property to a `TenantInfo` field or explicit
  formatter, envelope, batch, or explain-mode source, and wired it into the
  local CI mirror.
- **Stability-doc surface counts.** Updated the JSON contract count summary in
  `docs/stability.md` and added a docs test that ties it to
  `docs/recon-schema.json` plus the live MCP tool registry and stability table.
- **Dependency security alert closure.** Updated the `uv.lock` entry for the
  dev-audit transitive dependency `msgpack` from 1.1.2 to 1.2.1, closing
  GHSA-6v7p-g79w-8964 while leaving runtime dependencies unchanged.
- **Pydantic settings advisory closure.** Updated `pydantic-settings` from
  2.14.0 to 2.14.2 in `uv.lock` and the ClusterFuzzLite requirements export,
  closing GHSA-4xgf-cpjx-pc3j from the MCP dependency path.
- **Dependency currency batch.** Updated `mcp` to 1.28.0,
  `publicsuffixlist` to 1.0.2.20260615, and the dev toolchain entries for
  Hypothesis, pytest, pytest-asyncio, Ruff, Pyright, pre-commit, and
  pip-audit. The newer Pyright check exposed a typed `getaddrinfo` boundary in
  the SSRF guard, now fixed by normalizing the socket address field before it
  reaches the IP blocker.
- **ClusterFuzzLite hash-pinned install.** Split the fuzz-build bootstrap into
  hash-pinned runtime requirements and `PYTHONPATH` source loading, so the
  Scorecard Pinned-Dependencies check no longer sees unpinned pip resolution.
- **ClusterFuzzLite requirements drift guard.** Added
  `scripts/check_clusterfuzzlite_requirements.py` and wired it into
  `scripts/check.py` so `.clusterfuzzlite/requirements.txt` must match the
  frozen runtime export from `uv.lock`.
- **Fast guard CI parity.** The CI validation job now runs the same fast
  generated-artifact and ratchet guards as `scripts/check.py`: ClusterFuzzLite
  requirements, schema sources, surface inventory, CLI surface docs,
  experimental-label hygiene, file-size ratchet, and PLR ratchet.
- **Added-line text hygiene guard.** Added `scripts/check_text_hygiene.py` to
  reject new diff lines containing attribution markers, em dashes, or
  pictographic symbols, and wired it into the local fast gate and CI validation
  job.
- **Advisory diff coverage.** Added `scripts/diff_coverage.py`, a local
  maintainer signal that reports changed executable Python line coverage from
  Coverage.py JSON and a unified diff without gating documentation-only changes.
- **Release readiness commit hygiene.** The local readiness check now inspects
  every commit in the `origin/main..HEAD` stack when the branch is ahead, and
  rejects attribution markers, em dashes, or pictographic symbols before push.
- **PLR size-rule ratchet.** Added `scripts/check_plr_ratchet.py` to block new
  `PLR0911`, `PLR0912`, `PLR0913`, and `PLR0915` debt while the existing
  function-size violations are paid down.
- **MCP output schema precision.** Added precise `TypedDict` item schemas for
  `get_fingerprints`, `get_signals`, `explain_signal`, the simple
  ephemeral-fingerprint process tools, the graph data tools, and the compact
  agent-facing posture helpers, plus `get_posteriors` and the exposure report
  tools, discovery candidate lists, `analyze_posture`, and `reevaluate_domain`,
  so FastMCP advertises concrete `outputSchema` fields for these MCP surfaces.
- **Automation parser examples.** Added docs for consuming single lookup,
  batch array, batch wrapper, NDJSON, delta, and cohort-summary JSON modes,
  with tests that parse the snippets against the schema and runtime classifier.
- **Verification fingerprint metadata.** Added official references for five
  verification-token fingerprints and taught the advisory richness audit to
  recognize account-binding, program-binding, and tenant-binding scope language.
- **Weak-area guidance.** Added a DKIM selector false-negative note to the
  sparse-result documentation and pinned it with a docs test.
- **Unclassified CNAME guidance.** Documented how to read unclassified CNAME
  chain termini as fingerprint proposals rather than vendor claims, with a docs
  guard test for the conservative wording.
- **High-value-target profile baseline.** Added explicit `Identity` and
  `Security & Compliance` expected categories to the high-value-target posture
  profile, with tests pinning hedged absence observations.
- **Public validation memo.** Added an aggregate-only smoke memo for
  `validation.reproduce_paper_numbers --profile smoke`, with hygiene tests that
  keep the committed artifact free of per-domain data.
- **Cache edge coverage.** Added regression tests for URL-to-apex cache-key
  normalization, top-level-only `cache_clear_all()` deletion, and the
  batch-only `shared_verification_tokens` non-persistence contract.
- **CrowdStrike fingerprint precision.** Converted the CrowdStrike TXT
  fingerprint to `match_mode: all` and taught TXT bookkeeping to record
  same-record corroborating matches, so canonical Falcon verification still
  detects while generic TXT mentions are suppressed.
- **Supabase surface fingerprint.** Added a high-confidence Supabase
  `cname_target` fingerprint from the official custom-domain docs, with
  classifier coverage and a validation memo explaining why the generic ACME TXT
  challenge is not catalogued as vendor-specific evidence.
- **Microsoft internal chain motif.** Added a complete
  `tm_to_azurefd_to_msedge` motif for Traffic Manager to Azure Front Door to
  Microsoft Edge CNAME chains, with before/after public candidate-chain delta
  coverage.
- **Workflow action pinning.** Pinned every GitHub Actions dependency to a full
  commit SHA, replaced the actionlint download-and-run step with a pinned action,
  removed installer-side pipx bootstrapping, and added a local / CI gate that
  keeps workflow pins in place.
- **Workflow pin gate coverage.** Fixed the workflow-pin checker so it also
  validates shorthand `- uses:` steps, not only named-step `uses:` lines.
- **Validation hygiene gate.** Added a local and release-readiness check that
  blocks forced-added private validation run paths, root per-domain JSON dumps,
  and target-domain fields in committed validation artifacts. Documented the
  aggregate-only disclosure controls for future calibration memos.
- **Calibration memo renderer.** Added aggregate JSON output for conformal
  coverage and a renderer that rejects target-identifying fields and
  unsuppressed small strata before a private-run validation memo is reviewed.
- **Calibration bundle runner.** Added a maintainer-local runner that executes
  the reference, tenancy, and conformal calibration harnesses into a gitignored
  run directory, captures aggregate JSON without shell redirects, and renders
  the checked memo.
- **Calibration bundle path containment.** The maintainer-local calibration
  runner now validates `--stamp` as a safe path segment and resolves the run
  directory under `--output-root`, preventing traversal before private aggregate
  artifacts are written.
- **Paper reproduction path containment.** The public paper-number reproduction
  runner now applies the same safe `--stamp` validation and output-root
  containment before writing local artifacts. Both validation runners share the
  same path-safety helper so the local artifact boundary cannot drift.
- **Scorecard supply-chain posture.** Added explicit read-only workflow token
  defaults, low-noise dependency update configuration, and scheduled CodeQL
  analysis so Scorecard-detected token-permissions, dependency-update, and SAST
  posture match the repository's intended security baseline. The structural tests now
  require every workflow to default to read-only token permissions and every
  elevated job scope to match an explicit allowlist, and every checkout step
  disables persisted Git credentials. Every workflow job now also carries an
  explicit bounded timeout.
- **Release provenance gate.** PyPI publishing and GitHub release publication
  now wait for build-provenance attestation, and GitHub releases attach the
  exported `recon-tool-<version>.intoto.jsonl` provenance bundle so future
  releases fail closed and expose Scorecard-recognized provenance.
- **Release-readiness preflight.** Added a maintainer-local readiness gate for
  branch state, version drift, coverage wiring, lockfile freshness, Homebrew
  formula freshness, private-data hygiene, and latest-commit attribution
  hygiene before relying on remote CI.
- **Homebrew formula freshness.** The bundled formula now points at the current
  `recon-tool` 2.2.8 sdist and checksum.

## [2.2.8] - 2026-06-17

### Fixed

- **Wheel package invariant.** CI now builds and inspects the wheel to pin the
  intended data files and direct runtime dependency surface, keeping ML, ASN,
  GeoIP, aggregate stores, and paid-vendor SDKs out of the package.
- **Homebrew formula freshness.** The bundled formula now points at the current
  `recon-tool` 2.2.7 sdist and checksum.

## [2.2.7] - 2026-06-17

### Fixed

- **Homebrew formula freshness.** The bundled formula now points at the current
  `recon-tool` 2.2.6 sdist and checksum.
- **Assurance proving-test backlog.** Production HTTP and resolver bounds are
  now pinned by value, the DNS per-query timeout is asserted in isolation, and
  custom profile and motif YAML overlays now have hostile-input coverage.
- **Profile and motif YAML overlay bounds.** Custom profile and motif YAML
  documents over 1 MiB are skipped before parsing, and recursive parse failures
  degrade cleanly instead of escaping the loader.

## [2.2.6] - 2026-06-17

### Fixed

- **Homebrew formula freshness.** The bundled formula now points at the current
  `recon-tool` 2.2.5 sdist and checksum.
- **Roadmap and assurance docs currency.** The roadmap now names v2.2.6 as the
  current release, and the assurance case describes the broadened HTTP
  non-global IP guard.

## [2.2.5] - 2026-06-17

### Fixed

- **HTTP SSRF special-use IP guard.** The shared HTTP transport now blocks all
  non-global or special-use IP literals and resolved addresses, not just the
  explicit RFC1918, loopback, and link-local ranges. This closes gaps for
  unspecified, shared-address, documentation, multicast, and reserved addresses.
- **Homebrew formula freshness.** The bundled formula was refreshed after the
  2.2.4 publish so local checks no longer lag the latest released sdist and
  checksum.

## [2.2.4] - 2026-06-17

### Fixed

- **Live docs currency.** Fixed source-layout relative links in schema and
  security docs, updated roadmap and ADR layout guidance to match v2.2.4 and
  the adopted `src/` package layout, and added a regression test for relative
  Markdown links in live docs.
- **Source-tree version resolution.** `_source_tree_version()` now reads
  `pyproject.toml` from the repository root after the `src/` layout move, so a
  source checkout reports the checked-in version instead of stale editable
  metadata or the baked fallback.
- **Release typecheck parity.** The local release script and tag-triggered
  release workflow now run pyright over both `src/recon_tool/` and `tests/`,
  matching main CI.
- **Homebrew formula freshness.** The bundled formula was refreshed after the
  2.2.3 publish so local checks no longer lag the latest released sdist and
  checksum.
- **Portable Unix installer version check.** `scripts/install.sh` no longer uses
  GNU-only `sort -V`, so the Python 3.11+ fallback path works on macOS as well
  as Linux.
- **Development command drift.** README and contributor setup instructions now
  use the `src/recon_tool/` typecheck path and include `tests/`, matching CI.

## [2.2.3] - 2026-06-17

### Fixed

- **Browser URL normalization.** Lookup validation now parses `http://` and
  `https://` inputs through the URL host field, so copied browser URLs with a
  query string, fragment, or explicit port normalize to the registrable apex
  instead of failing validation.
- **Batch input line bounds.** Batch input now rejects a logical line that
  exceeds the per-line cap instead of splitting it into multiple pseudo-domains.
  This keeps the documented hostile-input bound enforceable for file and stdin
  batch inputs.
- **Release-script source-layout path.** `scripts/release.py` now reads and
  bumps `src/recon_tool/__init__.py`, matching the package layout. The previous
  path would abort a clean release before version consistency checks could pass.

### Dependencies

- **Typer floor and lockfile.** Raised the runtime Typer floor to `>=0.24.1`
  and refreshed the lockfile to Typer `0.26.7`. This avoids the older
  Typer/newer Click help-rendering crash while staying current with the
  published Typer line.

## [2.2.2] - 2026-06-16

### Fixed

- **Credible-interval accuracy claim.** The `_credible_interval` docstring and
  `correlation.md` section 4.4 stated the Wald-style normal band matches exact
  Beta quantiles to within +/-0.02. Measured against exact Beta quantiles the
  deviation reaches ~0.06 near the 0/1 probability boundary and ~0.05 in the
  interior, so the stated bound is corrected and the interval is documented as
  approximate, with `TestCredibleIntervalVsBeta` added to pin the deviation. The
  shipped interval values are unchanged: this is a documentation and test
  correction, not a behavior change.

### Security

- **Transitive dependency CVE bumps.** Bumped cryptography, python-multipart, and
  starlette in the lockfile to pick up published CVE fixes. These are transitive
  and dev-environment dependencies; recon's runtime requirement specifiers in
  `pyproject.toml` are unchanged, so already-installed wheels are unaffected.

## [2.2.1] - 2026-06-14

### Added

- **Exact-host lookups (`--exact`).** `recon <host> --exact` analyzes the literal
  host you typed instead of reducing to the registrable apex, for the narrow case
  of wanting DNS facts about one specific sub-host.

### Changed

- **Apex input normalization.** Any lookup target is now reduced to its
  registrable apex (eTLD+1) by default, so a pasted browser URL or sub-host
  (`https://mail.example.co.uk/login`) is analyzed at `example.co.uk`, where recon's
  signal lives (tenant, MX, `_dmarc`, CT). This generalizes the previous
  special-case `www.` strip and is backed by the Public Suffix List, so
  multi-label TLDs (`example.co.uk`, `example.com.au`) reduce correctly. A sub-host
  reduction prints a one-line note naming what was analyzed; `--exact` opts out.
  Applies everywhere a domain is validated (CLI, batch, delta, MCP, cache keys).

### Dependencies

- **Added `publicsuffixlist`** (MPL-2.0) for apex reduction. Pure-Python with
  zero required runtime dependencies and a bundled, self-updating Public Suffix
  List, so it adds no transitive tree and stays within recon's lean, offline,
  no-C-extension floor. It flows through the existing supply-chain controls
  automatically: hash-pinned in `uv.lock`, surfaced in the CycloneDX SBOM, and
  scanned by `pip-audit` in CI. This is recon's first non-permissive (weak
  copyleft) dependency license; MPL-2.0 is file-level and does not affect recon's
  MIT licensing, since recon consumes the package unmodified.

### Internal

- **God-file decomposition (completed).** Further split the oversized modules
  under the file-size ratchet, each step golden/snapshot byte-identical and
  CI-gated. `formatter.py` is down to ~2160 lines (from 4413): the markdown
  report renderer moved to `formatter_markdown.py` and the non-Rich data
  serializers (the json-dict / json / plain / CSV layer, including the shared
  `format_tenant_dict`) to `formatter_serialize.py`. `cli.py` is down from 3941
  to ~2830: all four Typer sub-apps moved to sibling modules under a pattern
  where the sub-app defines and exports its `Typer` and `cli.py` registers it  -
  `cache` → `cli_cache.py`, `mcp` → `cli_mcp.py`, `signals` → `cli_signals.py`,
  `fingerprints` → `cli_fingerprints.py`  -  with the one cross-module helper
  (`_fmt_exc`) lifted to `cli_shared.py` first to avoid a cycle. The two modules
  just over the cap are now under it: `exposure.py` (1130 → 983) split its frozen
  result-type family (`EmailPosture` / `ExposureAssessment` / `GapReport` /
  `PostureComparison` and kin) to `exposure_models.py`, and `merger.py` (1131 →
  958) split its gateway/provider slug sets and slug-humanizing name maps to
  `merger_tables.py`. Both origin modules re-export every moved name (the merger
  tables under their historical `_NAME` aliases) so the import and test surface is
  unchanged. The four large modules then followed the same pattern and the track
  is now complete: `sources/dns.py` (2524 → 840) into `dns_tables` / `dns_base` /
  `dns_email` / `dns_infra`; `bayesian.py` (1411 → 926) into `bayesian_models` /
  `bayesian_loader`, with the inference engine left in place so the mutation-gated
  surface stays byte-identical; `server.py` (2859 → 406) into `server_app` /
  `server_runtime` plus the per-domain tool modules registering on the shared
  FastMCP instance; and `cli.py` (→ 702) into `cli_lookup` / `cli_batch` /
  `cli_doctor`. Every package module is now under the 1000-line cap except
  `formatter.py`'s cohesive panel core (~2160, kept whole by design). No behavior
  or contract change. See the roadmap "Module
  decomposition" section.

## [2.2.0] - 2026-06-13

The 2.2.0 minor: a coherent batch of new *stable surfaces* off the locked v2.0
JSON contract. The headlines are the evidence-semantics diagnostics (per-node
entropy reduction, exact leave-one-unit-out counterfactuals, graph partition
stability) and the MCP tool-output contract revision below. The CLI `--json`
v2.0 schema is unchanged.

### Changed  -  MCP tool output contract (aligned to MCP 2025-11-25)

The MCP data tools now return structured results instead of JSON strings, so a
client gets navigable `structuredContent` with a generated per-tool
`outputSchema`, while the same payload still ships as serialized-JSON text for
backward compatibility. Tool failures (invalid input, an unresolvable or
uncached domain, a rate limit, an internal error) now surface as `isError` tool
results (a raised `ToolError`) so a model can recognize the failure and
self-correct, instead of a success-shaped `{"error": ...}` payload. Eighteen data
tools are affected (catalog, posture, graph, ephemeral, and inference tools); the
narrative tools (`lookup_tenant`, `chain_lookup`, `reload_data`, `explain_dag`)
render prose or DOT and stay text. The posture tools now share a single
resolve-or-raise helper.

Note for MCP consumers: this revises the agent-consumed wire shape. Errors now
arrive as `isError` rather than an `error` field, and the text representation of
the list tools is one JSON block per item. The CLI `--json` / `--ndjson` / delta
contract (the locked v2.0 schema in `docs/recon-schema.json`) is a separate
surface and is unchanged. Full contract in [docs/mcp.md](docs/mcp.md). Pinned by
`tests/test_mcp_structured_output.py`.

### Added  -  CLI ergonomics & robustness (best-practices pass, tier 1)

Graded against the 2026 CLI-first rubric (clig.dev, 12-factor CLI), this closes
the highest-value ergonomics gaps. None touches the locked v2.0 JSON schema.

- **stdout/stderr discipline.** Errors, warnings, and progress spinners now go
  to a dedicated stderr `Console` (`get_err_console()`), never stdout  -  so a
  consumer piping `recon … --json` gets only the data stream, never an error
  line or spinner mixed in. `render_error`/`render_warning`, the three
  `console.status` spinners, and the batch `[n/total]` counter were moved;
  pinned by `tests/test_formatter.py::TestStdoutStderrDiscipline`.
- **`-h` and `-V` aliases.** `recon -h` (and any subcommand `-h`) now shows
  help, and `recon -V` shows the version; previously both errored with exit 2.
- **Clean crash & interrupt handling.** `run()` now wraps the app: an
  unexpected exception writes its full traceback to a `recon-crash-*.log` file
  and prints a clean one-liner with the path (no raw stack trace on the
  terminal, exit 4); Ctrl-C exits 130 quietly; normal Typer/Click exits pass
  through. Covered by `tests/test_cli_crash_handler.py`.
- **`--color` / `--no-color`.** Explicit global flags to force or disable
  colored output, overriding `NO_COLOR`/TTY auto-detection (which is still
  honored by default).
- **`cache clear --all` is guarded.** It now confirms interactively (TTY) or
  requires `--force` in a non-interactive context, instead of wiping all cached
  data unprompted.
- **`--plain` linear output (tier 2, accessibility).** `recon <domain> --plain`
  emits the lookup as greppable, screen-reader-friendly `key: value` lines with
  no color or box-drawing  -  the accessibility/scripting complement to the
  default Rich panel. Built from the same dict as `--json`, so it carries every
  field; mutually exclusive with `--json`/`--md`. Untrusted values are
  control-char stripped like the other sinks. Covered by
  `tests/test_formatter.py::TestPlainOutput` and a CLI exclusivity test.
- **`get_fingerprints` pagination (tier 2, additive).** The MCP tool gains
  optional `limit`/`offset` so an agent that needs only a slice of the ~840
  fingerprints can cap the response; omitting them returns the full list, so the
  result shape is backward-compatible. (The `structuredContent` / `outputSchema`
  / `isError` half of the agent-protocol polish shipped in this release; see
  "Changed  -  MCP tool output contract" above. A default pagination *envelope* on
  the list tools remains deferred.)
- **OSC 8 terminal hyperlinks.** Vendor-doc reference URLs in `fingerprints show`,
  the crash-log file path, and the issues URL in the crash handler are now
  clickable on capable terminals via the OSC 8 standard (rendered through Rich's
  `link` style), with a plain-URL fallback when piped or unsupported.
- **XDG Base Directory support (tier 2).** A new `recon_tool.paths` module
  centralizes config/cache/state resolution. Behavior is unchanged for existing
  setups  -  `RECON_CONFIG_DIR` (the test/CI seam) still maps every category under
  one directory, and an existing `~/.recon/` keeps being used so no data moves  -
  but a *fresh* install now uses `$XDG_CONFIG_HOME/recon`, `$XDG_CACHE_HOME/recon`,
  and `$XDG_STATE_HOME/recon` (defaults `~/.config`, `~/.cache`,
  `~/.local/state`) instead of littering `~/.recon`. The spec's
  relative-`XDG_*`-path-is-invalid rule is honored. All thirteen previously
  inlined resolution sites (cache, CT cache, rate-limit state, priors, motifs,
  fingerprints/signals/posture/profiles overlays, corpus, doctor) now delegate
  to it; the priors loader, which previously ignored `RECON_CONFIG_DIR`
  entirely, now honors it (tighter test hermeticity). Covered by
  `tests/test_paths.py` (override / legacy / XDG tiers).

### Fixed (validation)

- **`conformal_coverage` consumed the reference collector's old shape.** When
  the held-out residual landed, `reference_calibration.collect` started
  returning `CalibrationPair` (full + held-out) instead of bare
  `CalibrationRecord`; `conformal_coverage.main` still read `.posterior`
  directly and crashed at runtime. The unit tests missed it because the
  network orchestration was untested  -  a live public-list run surfaced it. It
  now reads `.full` (conformal is a statement about the deployed predictor),
  and a monkeypatched `main()` contract test
  (`tests/test_conformal_coverage.py::TestCollectorContract`) pins the
  cross-harness shape so it can't drift silently again.

### Added  -  agent-facing uncertainty legibility

- **Exposure score legible as a lower bound, not a grade.** `assess_exposure`
  computes its 0-100 `posture_score` from observed-present controls only, so a
  low score can mean "hardened but quiet" rather than "weak"  -  the same
  robot-librarian flatten-the-uncertainty risk the posterior surface had. The
  output now carries an `observability` block (`score_is_lower_bound`,
  `unconfirmable_absent_points`, `score_ceiling`, and a `note`) that quantifies
  how much the floor could understate the truth: the points come from the three
  controls whose *absence* the passive channel cannot confirm (DKIM at
  non-standard selectors, security tooling, an email gateway behind non-MX
  routing). Declarative-record absence (DMARC/MTA-STS/TLS-RPT/CAA) is genuine
  and excluded. `find_hardening_gaps` tags each gap with `absence_confirmable`:
  true for a confirmed public-records fact, false when the gap rests on *not
  observing* a hideable control and so may be a false positive  -  grounded in
  the same declarative-vs-hideable (CAL14) distinction the Bayesian layer uses.
  The MCP server instructions gain a "Reading the exposure score" section, the
  tool docstrings and the human panel carry the lower-bound framing, and
  `tests/test_exposure_server.py` + `tests/test_exposure.py` pin the accounting
  (a bare domain floors at 30 unconfirmable points; DKIM/tooling each drop it),
  the gap flags, and the instruction guidance. The score weights for the three
  hideable controls are now named constants so the score and the
  unconfirmable-absent total cannot drift apart. (Extends the posterior-surface
  legibility below from the inference output to the security-posture output, the
  two tools an agent uses for "is this domain secure?")

- **"Reading the posteriors" guidance for consuming agents.** The MCP server
  instructions gain a section, parallel to the existing "Untrusted observed
  content (data, not instructions)" one, telling a consuming agent how to read
  the Bayesian surface: the answer is the 80% credible interval, not the point
  `posterior`; `sparse=true`, a 0.5-straddling interval, or an empty
  `evidence_used` means the passive channel could not resolve the claim (report
  it unresolved, do not collapse it to the point value); and absence of a fired
  signal is not evidence of absence (the adversarial missing-data rule), so a
  low/sparse posterior reads as "we cannot tell", not "not present". An LLM
  consumer is a confident summarizer that will flatten a wide interval into a
  verdict unless the surface forbids it  -  the same robot-librarian failure the
  data-not-instructions marking guards against, applied to the inference output.
- **`sparse_count` on the `get_posteriors` payload.** A tool-level uncertainty
  summary (how many nodes resolved only to the passive-observation ceiling)
  beside `evidence_count` / `conflict_count`, so a linear JSON consumer sees the
  unresolved count before any point estimate  -  the guidance enforced at the tool
  level, not only in prose. The `get_posteriors` docstring and `docs/mcp.md`
  carry the same reading guidance; `tests/test_posterior_reading_guidance.py`
  pins the instruction section and the `sparse_count`/per-node-`sparse`
  agreement against silent regression. (An audit prompted by the 2026 "robot
  librarian" agent-design framing found recon's other two agent-facing
  guardrails  -  the data-not-instructions demarcation and the `readOnlyHint`
  autoApprove split  -  already shipped and test-enforced; this closed the one
  remaining gap, the inference surface leading with the point estimate.)

### Added  -  evidence-semantics diagnostics (the 2.2 surface)

- **Per-node `entropy_reduction_nats`.** Every `posterior_observations` entry
  (JSON, MCP `get_posteriors`, cache) now carries its share of the recovered
  information  -  H(prior marginal) − H(posterior), signed  -  the per-node
  breakdown of the existing result-level CAL10 total.
- **`unit_counterfactuals`: exact leave-one-unit-out influence.** For every
  evidence unit informative for a node (fired units, plus informative
  absences on the declarative node), the engine re-runs exact inference with
  that unit masked as structurally unobserved and reports
  `posterior_without` and `delta`, sorted by `|delta|`. The mask is global
  across the DAG, so the counterfactual honestly reflects support still
  flowing from other nodes' evidence through the CPTs (a masked
  `m365_indicators` does not collapse `m365_tenant` to its prior while a
  federation signal still supports it through the child CPT). Framed as
  evidence counterfactuals over the model, never causal claims; deltas are
  individually exact but not additive (units interact through the DAG). The
  load-bearing test cross-checks every reported counterfactual against an
  actual `masked_units` run (`tests/test_evidence_semantics_diagnostics.py`).
- **`partition_stability` on `infrastructure_clusters` (CAL11).** The graph
  layer now reports partition consensus across an 8-seed Louvain sweep (mean
  pairwise adjusted Rand index, pure-Python contingency implementation):
  1.0 means every seed produced the identical partition; lower values flag
  the partition degeneracy (Good et al. 2010) a single modularity score
  cannot see. Null outside the Louvain path, where the partition is
  deterministic; the *reported* clusters still come from the fixed shipped
  seed, so output stays deterministic.
- All three are schema-additive: `docs/recon-schema.json` (and the bundled
  copy served by the MCP schema-discovery resource) gains `NodeEvidence`
  (closing a pre-existing gap  -  `evidence_ranked` was emitted but never in
  the schema file) and `NodeUnitCounterfactual` definitions plus the new
  properties; `docs/schema.md` documents each with its stability marker. The
  cache round-trips the new fields in both directions (pre-2.2 entries load
  with honest "not measured" defaults). The default panel is unchanged.

### Added

- **Leave-one-unit-out inference: `infer(..., masked_units=...)`.** The engine
  (and `infer_from_tenant_info`) accepts evidence units  -  a correlation-group
  name (`m365_indicators`, `dmarc_policy`) or an ungrouped binding's name  -  to
  treat as *structurally unobserved*: no firing contribution, no
  informative-absence contribution on declarative nodes, no n_eff contribution.
  On hideable nodes masking equals the unit not firing (the MNAR LR=1 rule);
  on the declarative policy node the two differ, which is the point  -  masking
  is "unobserved", not "observed to be absent". Default empty; behaviour is
  unchanged (pinned by an equivalence property in
  `tests/test_bayesian_masked_units.py`: masking a unit reproduces, exactly,
  the unmasked engine on a network with that unit deleted, plus hand-computed
  posteriors on the isolated policy node). This is the primitive under the
  held-out reference calibration below and the planned evidence-semantics
  counterfactual diagnostics.

### Assurance

- **Posture-distribution harness (the paper's last two experiments).**
  `validation/posture_distributions.py` reads the engine's per-domain
  behaviour as distributions, both consuming the 2.2 diagnostics: the
  information-recovered distribution (CAL10 entropy reduction) bucketed by
  observable hardening posture (edge-proxied vs direct × evidence tier),
  and the interval-width-vs-evidence diagnostic (CAL7) reporting mean 80%
  interval width per node by n_eff bucket, grouped vs ungrouped nodes
  separated so the documented residual over-confidence on
  richly-instrumented grouped nodes is a number, not just catalogued.
  Pure classification/aggregation unit-tested
  (`tests/test_posture_distributions.py`); the run is maintainer-local,
  aggregates only. Completes the paper's evaluation inventory  -  every row
  now maps to a built harness.
- **Layer ablations, shipped and run (the paper's ablation experiment).**
  `validation/layer_ablation.py` measures, on fully synthetic data
  (model-sampled worlds; planted partitions with fictional hostnames; no
  corpus, no network, deterministic, publishable), what each layer adds:
  the Bayesian posterior vs the deterministic any-fired baseline and a
  strongest-single-binding baseline (with the node's marginal prior, so the
  comparison isolates evidence propagation), pooled and split by fired
  regime; and Louvain vs connected components on planted org clusters under
  shared-CDN bridging noise (scored by ARI). The committed run
  (`validation/layer-ablation.md`) shows the posterior winning the fired
  regime on every node, the DAG-only propagation node unreachable by slug
  matching, the declarative policy node winning pooled (the CAL14 asymmetry
  demonstrated), the hideable roots paying a quantified ~0.05-0.10 Brier
  MNAR price under benign missingness (the deliberate trade, now measured),
  and Louvain holding ARI 1.0 across a noise grid where naive grouping
  collapses to 0. Unit tests in `tests/test_layer_ablation.py`.
- **Held-out residual reference calibration (the clean tier-4 construction).**
  `validation/reference_calibration.py` now computes, beside the full
  posterior, a held-out residual posterior with the `dmarc_policy` unit
  masked, so the predictor sees only the strict-SPF + MTA-STS channel and the
  DMARC record serves purely as the label  -  predictor and label disjoint by
  construction (the overlap caveat the shipped tier-4 claim carries). Both
  single and `--stratify-dir` modes print full and held-out blocks; the
  residual's invariance to the DMARC signal and its hand-computed values are
  unit-tested. The maintainer-local corpus run fills in the numbers
  (`validation/reference-calibration.md` has the method and the honest
  expectations: a deliberately weak predictor whose *calibration* is the
  claim under test).
- **Tenancy reference calibration against the provider endpoints
  (CAL3/CAL4 tenancy extension).** New
  `validation/tenancy_reference_calibration.py` corroborates the
  `m365_tenant` posterior against Microsoft's own identity-endpoint
  attestation, with predictor and label split by *observation channel*:
  the predictor is inference over the DNS channel alone (the `dns_records`
  source re-merged by itself  -  masking cannot decircularize this node, its
  whole direct evidence is one group), and the label is the endpoint answer
  (tenant ID / Managed / Federated positive; OIDC HTTP 400 or NameSpaceType
  Unknown negative; channel disagreement lands in a counted conflict
  bucket, never a guess). The full-pipeline posterior is reported only as a
  CAL1-style consistency number. Google Workspace is reported one-sided
  (recall on attested-federated tenants) because recon's passive Google
  channel never attests managed tenancy and has no authoritative negative  -
  a calibration there would restate the channel, not test it. Pure logic
  unit-tested (`tests/test_tenancy_reference_calibration.py`, including the
  channel-split exclusion and the no-footprint-stays-near-prior property);
  `--stratify-dir` supported; maintainer-local run pending.

- **`--json` structured output on both calibration harnesses.**
  `reference_calibration.py` and `tenancy_reference_calibration.py` gain a
  `--json` flag that emits the same aggregates as a machine-readable object
  (no apex, exactly the text path's numbers) for cross-list agreement checks
  and the PV2 drift loop. Single mode emits the full/held-out (refcal) or
  DNS-only/full/GWS (tenancy) summaries; `--stratify-dir` emits the
  per-stratum + pooled structure. The orchestration is covered by a
  monkeypatched-collector `main()` integration test on each harness
  (`TestJsonMain`), guarding the untested-network-path regression class that
  the conformal collector bug came from  -  the machine-readable path the
  multi-list comparison depends on is tested, not just the pure functions.

- **Multi-list public calibration cross-check, two independent lists agree.**
  `validation/public-list-calibration.md` now reports two sector-disjoint,
  public, reproducible lists side by side (List A ~210 domains across
  banking/healthcare/SaaS/higher-ed/public-sector/retail/tech; List B ~175
  across automotive/consumer-internet/energy-industrial/media/nonprofit/
  telecom/travel). The harnesses reproduce across the two independent samples:
  email-policy ECE 0.061 vs 0.069 (base rate 0.876 vs 0.878, both at agreement
  1.000, both populating the empirical-zero `p=none` class); M365 DNS-only
  corroboration ECE 0.082 vs 0.105 (the same low-DNS-visibility 0.2-0.3
  reliability bin on both); conformal coverage 0.986 and 1.000 (both ≥ 0.90);
  posture entropy reduction p50 1.967 vs 1.932 with the sparse tier the
  hardening signal on both. Agreement across disjoint lists is the evidence
  the harnesses measure a property of the method, not one sample's bias  -  the
  reproducibility column the paper rests on, beside the private-corpus tier.
  Aggregates only; the lists live outside the repo and are never committed.

- **CAL12: the priors-elicitation ledger, written down.**
  `docs/bayesian-cpt-discipline.md` gains "The priors ledger": every root
  prior with its grounding status (corpus-grounded / hand-set /
  hand-set-with-known-gap), the observed 2026-06 corpus rate where one was
  recorded, and the elicitation reasoning  -  including why the documented
  m365 (0.30 vs ~60% corpus) and aws (0.40 vs ~28% observable) gaps are
  deliberate (enterprise-skewed corpus vs arbitrary-domain stance;
  passive under-detection), with `~/.recon/priors.yaml` as the
  scope-skew escape hatch. The unrecorded rates are marked as the open
  cells the next full-corpus pass fills; prior moves stay under the
  CPT-change discipline.
- **CAL9: the proper scoring rule leads the calibration output.**
  `calibration_summary` (shared by the reference- and tenancy-calibration
  harnesses) now computes and prints `log_score`, the mean negative
  log-likelihood, beside Brier and ECE  -  the proper scoring rule CAL9 asks
  the memos to lead with. Clamped at 1e-6 so a confidently-wrong record
  costs ~13.8 nats instead of returning infinity (reported behaviour, not
  hidden); hand-pinned in `tests/test_reference_calibration.py`.

### Theory

- **The suppression-monotonicity proposition, formalized and machine-checked.**
  `docs/correlation.md` section 4.3 now states and proves it: holding other
  evidence fixed, a node's presence posterior is monotone in its fired set, so
  under the positive-indicator hypothesis hiding any fired binding moves the
  posterior toward its all-absent floor B_X (the prior for a hideable node, and
  below the prior for the declarative node, where absence is disconfirming) and
  stays at or below the fully-observed value. An operator can only move a claim
  toward "we cannot tell," never to a confident false positive by hiding. The
  contract is "robust to evidence removal, exposed to evidence addition": the
  boundary is removal versus addition, not the passive/active line, because a
  passive operator can publish a decoy record and force a confident false
  positive (correlation.md 4.11, Pattern I).
  `validation/adversarial_properties.py` ships it as a machine-checked invariant
  over every per-node binding subset under a sweep of external-evidence contexts
  (zero violations on the shipped network), gated by
  `tests/test_adversarial_properties.py`.
- **The operator/provider hideability spectrum.** A new subsection distinguishes
  operator-vanity bindings (free to hide), operator-functional bindings (MX
  cannot be dropped without breaking mail, and relocates rather than erases the
  evidence), and provider-attested bindings (the M365/GWS identity endpoints the
  operator cannot hide at all), which is why the tenancy claims are
  reference-calibratable. Section 1.5 reframes the small, hand-specified Bayesian
  layer as the precondition for the guarantee, not a limitation.
- **The provider-attested tier, sharpened by the tenancy-harness source review.**
  The spectrum subsection now distinguishes the two providers honestly:
  Microsoft's endpoints are a two-class registry answer (presence *and* the
  documented tenant-not-found negative), while recon's passive Google channel is
  provider-*behavioral* and one-sided (it attests only an observed federated-IdP
  redirect, never managed tenancy, no authoritative negative  -  managed-Workspace
  response heuristics were removed as a false-positive source). So
  `m365_tenant` is reference-calibratable with both label classes;
  `google_workspace_tenant` is not, and the dossier ledger now splits the two
  nodes accordingly.

### Assurance

- **Reference calibration against the DMARC record (CAL3/CAL4), shipped and run.**
  `validation/reference_calibration.py` calibrates the `email_security_policy_enforcing`
  posterior against the authoritative DMARC policy (its own ground truth), with
  pure label/Wilson/calibration logic unit-tested in
  `tests/test_reference_calibration.py` and a per-vertical `--stratify-dir` mode.
  The maintainer-local run landed: two independent corpus samples agree at ECE
  about 0.077, agreement about 1.0, the miss conservative (under-confident), so
  the policy node is reported at tier 4 for the strict-SPF + MTA-STS residual,
  an agreement check for the DMARC-driven bulk (DMARC is also the dominant
  input). Aggregates only, no apexes; memo in
  `validation/reference-calibration.md`.
- **The statistical-assurance dossier** (`docs/statistical-assurance.md`) places
  every claim at the highest of four evidence tiers (observed / consistency /
  evidence-responsive / empirical coverage) and says where the support stops; the
  assurance case gains the suppression-guarantee and reference-calibration rows.
- **The data-handling policy** (`docs/data-handling-policy.md`): the complete
  "no real-company data, ever" rule mapped to its enforcing mechanisms.

### Tests

- Pinned the Brier/ECE calibration math the assurance claims rest on
  (`tests/test_calibration_metrics.py`), the mutation-gate floor-script decision
  logic (`tests/test_mutation_floor.py`), and the EXPERIMENTAL-label CI gate
  (`tests/test_no_experimental_labels.py`, made testable via an optional path
  argument).

### Docs

- Added the version milestone map and consolidated build order to the roadmap,
  and archived about 1,470 lines of shipped-release history into
  `docs/roadmap-history.md` so the roadmap stays forward-looking (now about
  2,090 lines).
- Corrected the mutation-gate kill-score claims (the v2.1.16 "1,642 of 1,642 /
  100%" was a wrong-interpreter artifact the CI baseline step caught) to the
  measured 91.4% (123 survivors of 1,431 tested), in the CHANGELOG, the
  traceability matrix, the roadmap, and `validation/mutation-gate.md`.
- Added `CODE_OF_CONDUCT.md` and linked it from `CONTRIBUTING.md`, completing the
  GitHub community-health profile; documented the MCP output contract in
  `docs/mcp.md` and gave the docs index self-routing descriptors.

### CI

- The mutation gate now filters equivalent-by-construction operators, scores
  survival over tested mutants with an explicit honest floor
  (`scripts/mutation_floor.py`), and runs a strengthened kill-set; bumped
  `astral-sh/setup-uv` 8.1.0 to 8.2.0 across the workflows.

### Internal

- **God-file decomposition (formatter).** Began splitting the ~4,400-line
  `formatter.py` by concern, preserving the public import path and keeping golden
  renders byte-identical: exposure/gaps rendering moved to `formatter_exposure`,
  and the shared service-classification layer to `formatter_classify` (logic) plus
  `formatter_classify_tables` (data). A CI-gated file-size ratchet
  (`scripts/check_file_size.py`) baselines the remaining oversized modules as
  shrink-only ceilings so they cannot regrow, and new modules cap at 1,000 lines.

## [2.1.18] - 2026-06-11

### Fixed

- **Services panel: long category labels no longer collide with their value.**
  The sub-category label column was a fixed 15 characters, one short of the
  longest label ("Data & Analytics", 16), so `ljust(15)` left no trailing space
  and a value rendered flush against the label ("Data & AnalyticsMongoDB
  Atlas"). The column width is now `max(15, longest label present + 1)`, so a
  long label gets its gap while short-label panels keep their established width
  and value space (existing output is byte-identical). Regression tests in
  `tests/test_services_label_width.py`.

### Changed

- **Lookup spinner now rotates through a wider, themed message pool.** The
  status pool grew from 11 to 28 messages grouped by what recon is actually
  doing (DNS, certificate transparency, identity endpoints, the inference layer,
  posture) plus a few that nod to the passive-only ethos, and a single lookup
  now cycles a shuffled sequence rather than showing one static line. The
  rotation is purely cosmetic and wrapped so a status-update failure can never
  affect a lookup's result; `tests/test_status_spinner.py` pins that contract.

### Docs

- Roadmap gains an aspirational "Research write-up (arXiv paper)" item: an
  honest contribution statement, the no-real-data publication constraint treated
  as a reproducibility-against-public-oracles feature, and the additional
  experiments (layer ablations, public-oracle coverage, posture stratification,
  entropy-reduction) to design into the existing validation harnesses.

## [2.1.17] - 2026-06-11

### Assurance: requirements-and-invariants traceability matrix, machine-checked

Completes the committed post-2.0 assurance track: every promise maps to the
test that keeps it, and the map itself cannot rot.

- **`docs/traceability-matrix.md`** maps the six box invariants, the
  operational-contract bounds (each named constant to the test that pins it),
  the output contract (schema drift, batch shapes, exit codes), the layered
  inference trust chain (differential verification, drift gate, interval
  coverage, mutation gate, evidence semantics), and release integrity. Rows
  whose proof is structural rather than test-shaped say so explicitly, as
  closable gaps.
- **`scripts/check_traceability.py`** resolves every backticked reference in
  the matrix and in `docs/assurance-case.md` against the AST of the current
  tree: test files, test nodes (including `file::method` shorthand and
  `Class::method` chains), source constants (`recon_tool/x.py::NAME`), and
  referenced files. No imports, no test execution; prose tokens are skipped.
- **`tests/test_traceability.py`** is the CI gate: a renamed or deleted test or
  constant now fails the build instead of silently orphaning a trust-doc row.
  The negative tests prove the checker catches broken references and ignores
  prose. The checker also surfaced and the matrix now corrects two stale
  constant homes (`_MAX_TXT_MATCH_LENGTH` lives in `fingerprints.py`; the exit
  codes live in `exit_codes.py`).
- Docs index gains the matrix under Trust and assurance; the roadmap marks the
  committed assurance track complete (remaining items are operator-paced:
  CAL3/CAL4 oracle calibration, the C3 CT-enabled corpus pass, two docs, and
  the diagnostics candidates).

Gate: full pytest + the new gate, ruff, pyright (0 errors), validate_fingerprint
(841), branch coverage 85%.

## [2.1.16] - 2026-06-11

### Assurance: mutation testing promoted to a gate with a score floor

The next assurance-track item, completing the plan the v1.9.10 memo deferred to
CI: cosmic-ray mutation testing over the inference core, blocking with a score
floor.

- **Gate.** `.github/workflows/mutation.yml` mutates `recon_tool/bayesian.py`
  and runs a focused kill-set per mutant, with a baseline step proving the
  kill-set passes unmutated first and a score floor failing the job if survival
  over tested mutants exceeds the bound. Blocking on any change to the mutated
  surface, the kill-set, the config, or the workflow; weekly on a schedule; on
  demand via dispatch. Not per-push: a docs or catalog change cannot change the
  mutation score of an untouched module.
- **Baseline result (corrected).** The kill-score figure first reported in this
  entry, "1,642 of 1,642 (100%)", was a wrong-interpreter artifact: the local
  sweep ran its kill-set under an interpreter that could not import the test
  conftest, so every mutant died of a collection error rather than a test
  verdict. The CI baseline step exposed it. The corrected authoritative sweep
  measured 123 survivors of 1,431 tested (8.6% survival, 91.4% kill), with the
  residual classified as equivalent-by-construction. The full story, the
  equivalent-mutant classification, and the honest 12%-survival floor are in
  `validation/mutation-gate.md`. (Corrected after release; the gate's own
  baseline check is what caught the false number.)
- **Tooling.** New `mutation` dependency group (cosmic-ray) so the per-push dev
  environment stays lean; `mutation.toml` is the committed config; the session
  DB is gitignored. cosmic-ray runs on both the Linux CI runner and Windows, so
  the local gate can match CI.

Gate: full pytest, ruff, pyright (0 errors), validate_fingerprint (841), branch
coverage 85%, actionlint on the new workflow.

## [2.1.15] - 2026-06-11

### Assurance: credible-interval perturbation-coverage gate

The next assurance-track item: a standing, CI-gated coverage check on the 80%
credible intervals, framed per CAL1/CAL13 as model-internal coverage against
parameter misspecification, never as ground-truth calibration.

- **Harness.** `validation/interval_coverage.py` builds synthetic worlds whose
  evidence likelihoods (and declarative `group_absence` pairs) are each scaled
  by an independent factor inside a band, samples domains from those worlds,
  runs the shipped model on the observations, and measures how often the
  shipped 80% interval contains the world's own conditional probability. The
  truth path is the independent full-joint reference from
  `validation/differential_verification.py`, not the engine. Synthetic-only,
  offline, aggregate output, reproducible under a fixed seed.
- **Result.** At the CAL8 +/-20% band, per-node coverage measured at or above
  0.999, marginal and conditional-on-fired-evidence; under gross
  misspecification (delta >= 0.5) coverage degrades first on the
  narrowest-interval node, the expected failure order. A diagnostic column
  also quantifies, with a number, the documented cost of the MNAR absence rule
  in a world where absence is genuine evidence. Full sweep and framing in
  `validation/interval-coverage.md`.
- **Gate.** `tests/test_interval_coverage.py` runs a reduced seed-pinned sweep
  in CI: total coverage at delta=0 (truth-path sanity), the nominal-80% floor
  on every node at delta=0.2, a falsifiability case at delta=0.9 proving the
  check can still fail, plus hand-computed anchors for both truth paths.
- `docs/assurance-case.md` Promise 5 gains the corresponding mechanism row;
  the roadmap assurance track marks the item shipped.

Gate: full pytest + new coverage tests, ruff, pyright (0 errors),
validate_fingerprint (841), branch coverage 85%.

## [2.1.14] - 2026-06-10

### Assurance: PV2 maintainer-validation loop + inference drift gate

The "Adaptive" assurance-track item: keep the Bayesian CPT numbers honest as the
world drifts. The committable, CI-gated core ships now; the corpus-dependent tier
stays maintainer-local.

- **Inference drift gate.** `validation/drift_check.py` fingerprints the Bayesian
  network's CPT-implied marginals (each node's no-evidence prior, all-bindings-
  present posterior, and interval width) deterministically from the network YAML,
  with no corpus. `validation/inference_baseline.json` is the committed baseline
  (node names and numbers only, no company data), and `tests/test_drift_check.py`
  gates it: an edit that shifts an implied distribution beyond 0.01 fails until
  the baseline is regenerated with `python -m validation.drift_check --update` and
  committed, so the shift is reviewed in the same diff. This mechanically enforces
  the CPT-change discipline.
- **`docs/maintainer-validation.md`** documents the full tiered loop: the
  committed drift gate (tier 0), the no-data synthetic harnesses (tier 1), the
  public case-study spot-check (tier 2), and the maintainer-local corpus
  re-grounding + firing-rate drift (tier 3), plus how an agent runs it on a
  `/schedule` routine. Only deterministic / aggregate output is committed; the
  corpus stays gitignored.
- pyright `extraPaths` now resolves repo-root packages so the gate test can import
  `validation.drift_check`.

Gate: full pytest (2910 passed), ruff, pyright (0 errors), validate_fingerprint (841), branch coverage 85%.

## [2.1.13] - 2026-06-10

### Assurance: auditable trust docs + closed proving-test gaps

Makes recon's trust claims inspectable for anyone evaluating it as a primitive to
build on. A traceability audit (each mitigation mapped to its implementing code
and the test that proves it) produced two durable artifacts and surfaced a few
mechanisms that were present but not directly asserted; the cheap ones are now
closed.

- **`docs/assurance-case.md`** maps each promise (passive, bounded / resilient,
  safe output, safe-to-point-at-an-untrusted-target, honest about uncertainty,
  verifiable artifact) to its mechanism, its proving test, and its residual risk,
  and lists the standing proving-test gaps honestly.
- **`docs/operational-contract.md`** documents the concrete runtime contract:
  timeouts, resource caps, exit codes, cache and partial-result semantics, and
  determinism. The docs index gains a "Trust and assurance" section linking these
  plus the existing threat model and the supply-chain doc.
- Closed four proving-test gaps the audit named: the `match_txt`
  `_MAX_TXT_MATCH_LENGTH` cap, the `MAX_REDIRECTS` redirect bound, the cumulative
  retry-sleep cap (`_MAX_TOTAL_RETRY_SLEEP`), and the rate-limiter
  `_load_persisted` RecursionError degrade on a poisoned state file.

Docs and tests only; no package code changed.

Gate: full pytest (2905 passed), ruff, pyright (0 errors), validate_fingerprint (841), branch coverage 85%.

## [2.1.12] - 2026-06-10

### Assurance: reproducible builds + sigstore-signed PyPI attestations

The "Trusted" assurance-track item: make a published release verifiable back to
its source. Builds were already attested (GitHub-native build provenance) with a
CycloneDX SBOM and OIDC trusted publishing; this adds the two missing pieces.

- **Reproducible builds.** The release build pins `SOURCE_DATE_EPOCH` to the
  tagged commit's timestamp, so the wheel and sdist are byte-identical to a
  rebuild from the same source. A new `reproducible-build` CI job gates the
  property on every change (it builds twice and compares the artifact hashes).
- **Sigstore-signed PyPI attestations (PEP 740).** The publish step now emits
  signed digital attestations to PyPI, so installers and auditors can verify an
  artifact's provenance directly from the index, alongside the existing
  `gh attestation verify` path.
- **`docs/supply-chain.md`** documents the full posture (trusted publishing,
  both attestation roots, the SBOM, a reproducible-build verification recipe,
  and the supply-chain isolation contract), and records the full SLSA L3
  generator workflow as deferred by proportionality.

Release-pipeline and docs only; no package code changed.

## [2.1.11] - 2026-06-09

### Assurance: complete the Resilient-track residuals

Closes the small residuals left after the v2.1.10 fuzz gate (roadmap "Resilient"
track).

- The OIDC and Azure metadata sources now scrub control bytes and bound the
  length of the tenant-influenced `tenant_region_scope` field at the source,
  matching its `cloud_instance` / `tenant_region_sub_scope` / `msgraph_host`
  siblings. A direct or library caller that bypasses the merger's free-text
  scrub now gets a safe, bounded `region` too.
- New bound assertions for the two remaining parser caps that lacked them
  (`_MAX_SUBDOMAIN_TXT_MATCH_LEN` and `_MAX_CNAME_MATCH_LEN`): an oversized TXT
  value or a CNAME match token beyond the cap is skipped before the regex runs.
- An explicit `(HTTP identity source x failure-mode)` matrix asserts that OIDC,
  userrealm, Google, and Azure metadata each degrade to a clean SourceResult
  under malformed / wrong-shape / 404 / 500 / timeout / network-error / empty
  responses, so a source that stops degrading under one mode is caught.

Gate: full pytest (2902 passed), ruff, pyright (0 errors), validate_fingerprint (841), branch coverage 85%.

## [2.1.10] - 2026-06-09

### Assurance: hostile-input fuzz CI gate + per-parser resource-bound tests

Promotes the hostile-input fuzz suites from incidental coverage under the
generic test job to a dedicated, separately-visible CI gate, and locks the named
resource caps at every parser boundary with oversized-input assertions (the
roadmap "Resilient" track: proven resource bounds, fuzz promoted to a gate).

- New `hostile_input` pytest marker and a dedicated `hostile-input-fuzz` CI job
  that runs the marked tests at a higher Hypothesis example budget (a `ci-fuzz`
  profile, loaded when `RECON_FUZZ` is set). The render and Bayesian fuzz suites
  and the resilience-hardening tests carry the marker; they still run inside the
  normal test job where they count toward coverage, so a parser-bound regression
  is now its own red check.
- `tests/test_hostile_input_bounds.py` drives crafted oversized / flooded /
  malformed input straight at each parser and asserts the cap holds: userrealm
  `_MAX_AUTODISCOVER_DOMAINS`; crt.sh `_MAX_SANS_PER_CERT` and
  `_MAX_CRTSH_CERT_SUMMARY_ENTRIES`; the CT burst and wildcard-cluster caps; the
  SPF redirect depth bound; and the DMARC rua extraction under a mailto flood.
- The Autodiscover XML parser now degrades cleanly on a defusedxml
  entity-expansion (billion-laughs) or external-entity (XXE) payload: those
  raise `EntitiesForbidden` / `ExternalReferenceForbidden` (not `ParseError`),
  which previously propagated out of the parser; the guard now catches the
  defusedxml base exception and returns an empty result, asserted by the gate.

Gate: full pytest (2867 passed), ruff, pyright (0 errors), validate_fingerprint (841), branch coverage 85%.

## [2.1.9] - 2026-06-09

### Resilience: close confirmed ingestion-boundary fault-injection gaps

A fault-injection sweep across every external-input boundary (DNS, CT / cert,
identity endpoints, HTTP, file / cache) confirmed four gaps reachable by an
attacker who controls a queried domain or a CT provider. Each now degrades
cleanly. The same sweep rejected seven other candidates as already neutralized
by existing guards (recorded in `docs/security-audit-resolutions.md`).

- **HTTP decompression bomb (High):** the 10 MB body cap counts compressed
  transfer bytes, but httpx decodes Content-Encoding downstream, so a ~9 MB gzip
  body could decode to ~9 GB and exhaust memory on `resp.json()` / `resp.text`.
  recon now requests `Accept-Encoding: identity` and the SSRF transport refuses
  any response that still carries a compressing Content-Encoding (a host that
  ignores the identity request is the bomb vector). The two `http.py` docstrings
  that claimed the byte cap defended against this are corrected.
- **Poisoned-cache RecursionError (Medium):** a deeply-nested JSON file under
  `~/.recon` raises `RecursionError` (a `RuntimeError`, not `ValueError`), which
  the cache loaders did not catch, so a poisoned file crashed the next lookup
  instead of degrading to a clean miss. `RecursionError` is now caught in
  `cache_get`, `ct_cache_get`, `ct_cache_show`, and `rate_limit._load_persisted`,
  with a pre-read file-size cap on the cache loaders.
- **CT graph entry-count amplification (Medium):** a small SAN set reused across
  many CertSpotter issuances never tripped the node cap but re-ran the per-cert
  clique build and grew the per-edge issuer list without bound (about 21 s and
  150 MB worst case, blocking the event loop). Graph construction is now bounded
  by `_MAX_GRAPH_ENTRIES`, per-edge issuer samples by `_MAX_EDGE_ISSUER_SAMPLES`,
  and CertSpotter's accumulated entry list is capped like crt.sh's.
- **CT provider RecursionError (Low):** the providers' `resp.json()` guard caught
  only `ValueError`, so a deeply-nested payload skipped the provider-local
  degrade (the orchestrator still prevented a crash); it now catches
  `(ValueError, RecursionError)`.

Gate: full pytest (2853 passed), ruff, pyright (0 errors), validate_fingerprint (841), branch coverage 85%.

## [2.1.8] - 2026-06-09

### Passive by default: direct probes to target-controlled hosts are opt-in

Closes the residual items from an external review batch. The review noted that
the README's "nothing the target can see beyond a single MTA-STS policy fetch"
understated recon's contact with the queried domain's own servers: the Google
CSE discovery probe (`cse.<domain>`) ran on every lookup, and the BIMI VMC
certificate fetch ran whenever a domain published one.

- Both direct probes are now off by default and gated behind a new
  `--direct-probes` opt-in (the `active_probes` argument on `resolve_tenant`).
  A default lookup makes no direct HTTP request to a target-controlled host
  beyond the standard MTA-STS policy fetch, so the documented passive posture
  holds by construction rather than by caveat. BIMI presence is still read from
  the DNS TXT record either way; only the VMC enrichment is gated.
- README and `docs/legal.md` are updated to describe the passive default and
  the opt-in. `docs/legal.md`'s query table no longer contradicts its own prose
  (it listed `cse.<domain>` while the text claimed MTA-STS was the only direct
  contact), and the BIMI VMC fetch is listed there too.
- `analyze_posture` (MCP) now guards its `profile` argument with an `isinstance`
  check before the length slice. MCP arguments arrive unenforced at runtime, so
  a truthy non-string profile would have raised `TypeError`; it is now treated
  as no lens, matching the `None` case.

The rest of that review batch was already resolved in v2.1.4 to v2.1.6 (cache
temp-file symlink, cname_target substring overmatch, IDNA2003 lossy mapping,
client-doctor terminal-escape, overlapping-alternation ReDoS, the
`batch --summary` domain leak, the `--no-fusion` cache round-trip, the scan.py
buffering regression, and the declarative-absence explanation phrasing); each
was re-confirmed against current code before this patch.

Gate: full pytest (2839 passed), ruff, pyright (0 errors), validate_fingerprint (841), branch coverage 85%.

## [2.1.7] - 2026-06-08

### Assurance: differential verification of the inference core

The first of the post-2.0 trust-hardening items (roadmap "Trusted" track). An
independent reference cross-checks the Bayesian engine; no engine or output
change, verification only.

- `validation/differential_verification.py` carries a second inference
  implementation that enumerates the full 512-state joint directly and reads
  each marginal off the normalized sum, with no factor algebra. It re-derives
  the factor construction (correlation-group reduction, declarative absence
  conditioning, soft evidence) from the documented spec, independently of the
  variable-elimination path it checks.
- It sweeps the enumerable evidence space (every node at none/one/all of its
  bindings, ~2.9k configs) plus an exhaustive per-node subset sweep over the
  grouped and declarative nodes. Variable elimination matched naive enumeration
  on every node of every configuration (worst gap 4.95e-05, the engine's
  4-decimal posterior rounding).
- `tests/test_bayesian_differential.py` anchors the reference to hand-computed
  no-evidence marginals (so the oracle is known-correct, not merely consistent
  with the engine), then holds variable elimination to it on the prior, the
  exhaustive tricky-node sweep, and a strided sample of the full sweep.

Gate: full pytest (2832 passed), ruff, pyright (0 errors), validate_fingerprint (841).

## [2.1.6] - 2026-06-07

### Inference layer (bug-hunt follow-up, maintainer-reviewed)

The four inference-layer items held back from 2.1.5, resolved after review.

- `spf_strict` now requires `-all` as a standalone SPF mechanism token rather
  than a substring; a record like `include:foo-all.com ~all` (soft-fail) no
  longer sets the strict-SPF signal. This is the one behavior change (it sharpens
  the email-security signal); the other three are non-behavioral.
- `compute_slug_posteriors`: the "alpha double-count" concern was a misleading
  inline comment, not a code defect. The code matches the module-docstring model
  (`alpha_new = alpha_prior + weight` per record; the prior is the outset trust
  level, not an encoded first observation). The comment is corrected and the
  always-true `slug_primed` dead code removed; posteriors are unchanged.
- A declarative Bayesian node whose grouped bindings lack a `group_absence`
  entry now logs a load-time warning (its absence was silently treated as
  uninformative, LR=1). The shipped network is already fully covered, so this is
  a guard for future edits.
- `InferenceResult.entropy_reduction` is documented as a signed quantity (it can
  be negative when evidence widens a node); it is reported, not clamped, so the
  net information-gain total stays honest.

Gate: full pytest, ruff, pyright (0 errors), validate_fingerprint (841).

## [2.1.5] - 2026-06-07

### Security and correctness (self-driven bug-hunt)

A five-area parallel bug-hunt (inference, ingestion, merge/cache, CLI/formatter,
fingerprints/server). Fifteen findings fixed; four inference-layer items are held
for maintainer review because they would shift calibrated posteriors.

Security:
- Rich markup injection in `recon <domain> --verbose`: the per-source line
  printed attacker-controlled `auth_type` / `dmarc_policy` / `error` through
  `console.print` without escaping; both are now escaped and control-stripped.
- Control-character and markup scrub gaps closed on attacker-controlled paths
  that bypassed the central merger scrub: the OIDC discovery fields
  (`cloud_instance`, `tenant_region_sub_scope`, `msgraph_host`), the resolver's
  related-domain enrichment services, the unclassified-CNAME and surface panels,
  the conflicting-tenant-ID insight, and the `--md` related-domains list.
- crt.sh `name_value` is length-capped before the per-character SAN scan, so a
  single newline-free field cannot turn the whole response body into a scan.
- Non-capturing-group ReDoS: `(?:a|aa)+c` slipped past the alternation-overlap
  guard because `(?:` corrupted the first branch; the guard now normalizes
  non-capturing and inline-flag groups before splitting branches.
- `inject_ephemeral_fingerprint` returns a clean error instead of crashing when
  a detection element is not a dict; `simulate_hardening` no longer echoes the
  raw caller-supplied fix string; `analyze_posture` caps the profile name.
- The v2.1.4 cache `mkstemp` now uses the resolved cache dir, so a symlinked
  `RECON_CONFIG_DIR` cannot move the temp off-volume and make `os.replace`
  non-atomic.

Correctness:
- `merge_conflicts` now survives the cache round-trip; it was serialized but
  never read back, so a cached result lost its conflict data and the Bayesian
  n_eff conflict penalty.
- The CT semaphore and rate-limiter maps key on the loop object through a weak
  map instead of `id(loop)`, which could be reused after GC and return stale
  state.
- The `cname_target` specificity corpus is now the CNAME corpus rather than the
  mismatched generic one, so the ephemeral-injection gate is meaningful for the
  most common detection type.

Held for maintainer review (each would shift calibrated posteriors): a possible
alpha double-count in `compute_slug_posteriors`, the `spf_strict` `-all`
substring match, declarative group-absence LR=1, and the signed
entropy-reduction total.

Gate: full pytest, ruff, pyright (0 errors), validate_fingerprint (841).

## [2.1.4] - 2026-06-07

### Security and correctness (external review batch)

An external agentic security review of the recent commits surfaced eight
findings; every real one is fixed with a regression test, two were already
closed by earlier hardening.

Security:
- Cache atomic-write symlink vector (Medium): the v2.1.3 atomic write used a
  predictable `<domain>.json.tmp` that was not validated, so a pre-created temp
  symlink in a shared or world-writable cache directory could be followed and
  overwrite a victim-writable file. It now uses `mkstemp` (random name,
  O_CREAT|O_EXCL, mode 0600, never follows a symlink) inside the validated cache
  directory, then `os.replace`.
- cname_target substring overmatch (Medium): the surface-attribution classifier
  matched the vendor pattern as a bare substring, so an attacker-controlled CNAME
  target like `manageengine.com.attacker.tld` matched the `manageengine.com`
  rule. Matching is now DNS-label-aware (exact or proper subdomain).
- IDNA2003 wrong-domain mapping (Medium): the stdlib idna codec is lossy
  (`faß.invalid` maps to `fass.invalid`, a different registrable domain). A round-trip
  check now rejects lossy compatibility mappings rather than querying the wrong
  domain; non-lossy IDNs (`café.invalid` to `xn--caf-dma.invalid`) still convert. No
  new dependency.
- Terminal-escape injection in client-doctor output (Medium): `recon doctor
  --client` printed config-derived strings (a workspace MCP `command`) through
  rich markup escaping only; it now control-strips them, the sibling of the
  v2.1.2 output-injection sweep.
- CNAME custom-regex ReDoS (Medium): already closed by the v2.1.1 ReDoS-guard
  hardening (the alternation-overlap and balanced-paren checks reject the
  reported `(a|aa)+c`); a regression test pins it.

Correctness and privacy:
- `recon batch --summary` leaked input domain names through the per-domain
  progress line in default-panel mode, against the aggregate-only contract; the
  progress print is now suppressed under `--summary`.
- `--no-fusion` could be bypassed by cached fusion fields; a no-fusion cache hit
  now clears `slug_confidences` and `posterior_observations` so the opt-out is
  honored.
- The declarative-absence DAG explanation already branches on
  `absence_informative` (the CAL14 work), so a posterior moved by informative
  absence no longer reads as "follows priors."
- validation/scan.py streams the NDJSON CT-budget summary line-by-line again (the
  prior version buffered the whole results file).

Gate: full pytest, ruff, pyright (0 errors), validate_fingerprint (841).

## [2.1.3] - 2026-06-06

### Hardening: engine internals

A deeper bug-hunt over the internals the 2.1.1/2.1.2 reviews did not cover
(Bayesian inference, the merge/resolve/cache layers, graph/CT parsing), via three
independent adversarial subagent passes. The inference math, the
SSRF/resource/path/deserialization surface, and the schema contract were
re-confirmed clean; the fixes:

- Determinism: the infrastructure-cluster (Louvain) partition was sensitive to
  cert-entry arrival order (not stable across CT responses), so the same domain
  could yield different clusters across runs. Nodes are now inserted in a
  content-determined (sorted) order before partitioning.
- Correctness: related-domain enrichment re-ran insight generation with a
  truncated parameter set, defaulting `has_mx_records` to False (a spurious "no
  email infrastructure" insight) and silencing the score / SPF / issuance signals
  on enriched-then-cached results. The metadata is now re-passed.
- Cache: `ct_attempt_outcome` now round-trips (it was silently dropped, so cached
  `--json` reported it as null); cache writes are atomic (temp-then-replace, so a
  crash or concurrent read cannot see a truncated file); cert `top_issuers`
  deserialization coerces elements like its siblings.
- Bayesian: `load_network` now rejects boundary priors / CPT values `{0, 1}` (the
  open interval the rest of the module already requires; a degenerate 0/1 pins a
  posterior), and a degenerate all-zero query factor falls back to the uniform
  prior rather than a non-normalized result. The bundled model is unaffected.
- Lexical: the environment-token boundary check now considers every occurrence in
  a label, not just the first.

Deferred (tracked): the cache round-trip of `merge_conflicts` (needs a
deserializer; cached `evidence_conflicts` is currently empty), and a few
low/latent items (enrichment slot fairness, conflict-candidate pre-scrub for the
JSON path, a cache-version check).

Gate: full pytest, ruff, pyright (0 errors), validate_fingerprint (841).

## [2.1.2] - 2026-06-06

### Security: output-injection sweep

A dedicated sweep of every render path for the class the 2.1.1 `render_error` fix
revealed: attacker-influenceable strings (CT issuer/subject, federation brand
name, autodiscover domains, per-source error text) reaching the terminal or
markdown without escaping or control-stripping. Most paths were already safe (the
merger scrubs the primary fields and the panel renders via markup-safe
`Text.append`); four siblings were fixed, each with a regression test:

- `render_warning` now escapes and control-strips the domain and the per-source
  error reasons (a `console.print` markup sink carrying server-influenced text).
- `render_conflict_annotation` (verbose) control-strips the raw candidate values
  it renders, for example a tenant-controlled federation brand name, under
  `--explain --verbose`.
- The `delta` command's two error sinks now use the sanitized `render_error` path
  like every other lookup error.
- The markdown report escapes `default_domain` and `tenant_domains` (autodiscover
  values that are control-stripped but not charset-restricted upstream).

The SSRF/network, ReDoS, resource/path/deserialization, and MCP reviews from 2.1.1
stand; no new high or medium issues outside this class.

Gate: full pytest, ruff, pyright (0 errors), validate_fingerprint (841).

## [2.1.1] - 2026-06-06

### Hardening and security

A focused hardening pass over the v2.1 cohort-summary surface (four review rounds,
two of them independent adversarial passes) plus a security review of recon's core
attack surface. Every finding is fixed with a regression test.

Security:
- ReDoS guard: the catastrophic-backtracking heuristic missed a quantified group
  wrapped in an extra paren (for example `((a+))+`), which the input-length caps
  cannot contain. Added a balanced-paren scan that catches nested quantified
  groups. The shipped catalog is unaffected (841 still validate). Reachable via
  the MCP ephemeral-fingerprint tool and custom `~/.recon/fingerprints.yaml`.
- `render_error` now escapes rich markup and strips control characters from its
  message, so an untrusted batch-file domain echoed in an error cannot inject
  terminal escapes or markup; the batch per-domain progress line is sanitized the
  same way.
- The SSRF / network and resource / path / deserialization reviews found no high
  or medium issues; the existing guards (private-IP blocklist, bounded redirects,
  body cap, capped expansions, `validate_domain` plus path containment,
  `safe_load`, `defusedxml`) hold.

Cohort-summary (`recon batch --summary`) robustness:
- Deterministic mix ordering and distinctiveness ranking; `_safe_float` coercion
  and record/field-type guards so malformed or NaN/inf posteriors, non-dict
  records, and non-list fields from untrusted reducer input cannot crash the run
  or emit invalid JSON; an unhashable posterior `name` is skipped.
- `wilson_interval` clamps `positives`; `resolution_rate` is guarded; the
  small-cell suppression doc is honest (a rate over a known denominator can imply
  the count, so the small-n warning is the disclosure signal); `--summary`
  rejects `--include-ecosystem`; a malformed NDJSON line is skipped.

Gate: full pytest, ruff, pyright (0 errors), validate_fingerprint (841).

## [2.1.0] - 2026-06-06

### Aggregate state: stateless cohort summary

`recon batch --summary` emits one aggregate-only cohort summary over a batch:
observability-adjusted prevalence (observed rate, conservative lower bound, and
observability fraction, so missing-not-at-random absence is encoded honestly),
aggregated posterior mass with a separate high-confidence share, and provider and
cloud concentration (entropy and HHI). Add `--json` for machine output; the
default renders a compact panel. Stateless and compute-and-forget: it ships no
baselines, stores nothing, makes no baseline-relative anomaly score, infers no
unobserved services, and names no domain in its output.

- The summary carries its own record type (`cohort_summary`, `schema_version`
  2.1); the locked v2.0 per-domain schema is unchanged.
- Caller-grouped analysis (grouping, distinctive-slug ranking, partial pooling)
  stays in a downstream reducer under `validation/aggregate/`, which shares the
  per-cohort math with core so the two never drift. See `docs/aggregate-state.md`
  for the methodology and a fully synthetic worked example.
- `--summary` pairs with `--json` or stands alone; it does not combine with
  `--md`, `--csv`, or `--ndjson`.

Gate: full pytest, ruff, pyright (0 errors), validate_fingerprint.

## [2.0.1] - 2026-06-05

### Panel disclosure: posterior-backed confidence dots

The default panel now reflects the Bayesian layer that v2.0 turned on, while
staying quiet on the easy cases.

- The Confidence dots are posterior-backed when fusion has run: they show a
  claimed node's posterior support relative to the present/absent decision
  threshold, in three levels (`●●●` the whole 80% credible interval above the
  threshold; `●●○` the point estimate above but the interval dipping below, thin;
  `●○○` the point estimate below the threshold, the evidence leans against the
  call). The dots are one defined quantity (posterior support); the deterministic
  corroboration stays in the `(N sources)` text.
- The panel is as confident as its weakest claimed node (a node with fired
  evidence). A declarative node correctly reporting absence does not demote a
  strong verdict.
- When the weakest claimed node is below full confidence, a dimmed line under the
  Confidence row names the claim in plain English: "thin on <claim>" or "the
  evidence does not back <claim>".
- `--verbose` lists each claimed node's posterior and 80% credible interval under
  a labeled heading so the range is not read as a frequentist confidence interval.
- Accessibility: solid versus hollow carries the signal with no color; the hue is
  a second channel; glyphs are limited to `●` and `○` for terminal-font safety.
- Without posteriors (`--no-fusion`) the panel is byte-identical to v1.x, and the
  dot fill is a pure, property-tested function so it cannot drift through the UI.

Deferred past this release: localized dimming of a disputed claim's span in the
Provider line.

Gate: full pytest, ruff, pyright (0 errors), new dot-fill property test and panel
disclosure tests.

## [2.0.0] - 2026-06-05

The v2.0 stability lock. No new capability ships in 2.0 itself; everything new
since v1.9.0 shipped and was validated across the v1.9.x bridge. 2.0 locks the
JSON schema as the v2.0 contract, turns the Bayesian fusion layer on by default,
and ratifies the accumulated work.

### Schema lock (G1)

- `docs/recon-schema.json` is bumped from "Stable v1.0 contract" to "Stable v2.0
  contract"; additive changes stay non-breaking within 2.x. The locked surface
  is the post-schema-hardening shape (SH1 to SH9): the `slug_confidences` object
  map, named `wildcard_sibling_clusters` objects, the `fusion_enabled` /
  `record_type` / `schema_version` discriminators, machine-readable `error_kind`,
  and the `--include-ecosystem` always-wrapper. Both schema copies stay
  byte-identical.
- `recon doctor`'s first line now reads "v2.0 stable schema".

### Fusion on by default (G2)

- The Bayesian inference layer runs on every lookup; it was opt-in behind
  `--fusion` through v1.9.x. `--json` always emits `posterior_observations` and
  `slug_confidences`, and `fusion_enabled` disambiguates the opt-out case. The
  computation costs no extra network calls.
- `--no-fusion` (new) opts out, reverting to the rule-based shape (empty fusion
  arrays, `fusion_enabled: false`). `--fusion` is kept as a now-default no-op for
  compatibility.
- The default panel stays clean: it renders the deterministic verdict as before
  and does not dump the credible interval. The panel "speak up when the layers
  disagree" refinement (surface the interval inline and demote the confidence dot
  on sparse or disagreement cases) lands as a 2.0.1 fast-follow.

### Validation baseline

- Locked against a full-corpus fusion re-run (5238 successful domains, post-CAL14
  build): 100% deterministic-vs-Bayesian consistency (13560 of 13560
  high-confidence firings, zero disagreements), the CAL14 declarative
  email-policy behavior confirmed on real input, and zero cross-source conflicts.
  See `validation/v2.0-corpus-run.md`.

The migration guide is `docs/migration-v2.md`; the full validation trail and the
lock-ceremony record are under `validation/`.

## [1.9.99] - 2026-06-05

### Schema description fix (SH9 follow-up) and the v2.0 lock-ceremony recipe

- The root schema description still said `--include-ecosystem` "falls back to the
  bare array when no domain resolved," which SH9 (v1.9.95) removed. It now states
  the wrapper is always emitted, with error records under `domains` and an empty
  `ecosystem_hyperedges` on an all-failed batch. Both schema copies stay
  byte-identical; a readiness audit found this was the only stale reference left.
- Adds `validation/v2.0-lock-ceremony.md`, the exact mechanical steps to cut
  2.0.0 (G1 schema description bump, G2 fusion default-on with its test-update
  discipline, G4 changelog move and tag), so the lock is a well-understood pass
  rather than improvised at tag time.

Gate: full pytest, the schema tests.

## [1.9.98] - 2026-06-05

### Bayesian explanation consistency (CAL7, CAL14)

Two explainability fixes so the reported evidence matches what actually drove the
posterior.

- CAL7: grouped evidence was reported as independent. Correlated co-firing
  bindings that share a group (the M365 / GWS indicators, the DMARC policy pair)
  are redundant readings of one fact, so the posterior already reduces them to
  one effective binding. The influence ranking (`evidence_ranked`), effective
  sample size (`n_eff`), and `evidence_count` now use that same contributing set
  instead of the raw fired list. Previously `--explain-dag` showed each grouped
  binding as a separate influence with its own percentage, and `n_eff`
  over-counted them, giving too tight an interval. The Evidence line still lists
  every observed binding; only the influence and interval math use the
  contributing set.
- CAL14: declarative absence was hidden from explanations. For a declarative
  node (`email_security_policy_enforcing`), the absence of an expected public
  declaration moves the posterior, but the DAG renderer printed "no direct
  evidence (posterior follows network priors)" when no binding fired, which is
  false. `NodePosterior` now carries an `absence_informative` flag, and the
  renderer explains the posterior as driven by informative absence for those
  nodes.

Gate: full pytest, ruff, pyright (0 errors). The `--explain-dag` snapshot and
the multi-influence tests were updated to the corrected (group-reduced) output;
multi-influence ranking is now exercised with ungrouped evidence and the top-3
truncation with a direct renderer test.

## [1.9.97] - 2026-06-05

### Security hardening: terminal-escape sanitization and CNAME ReDoS

Two Medium-severity hardening fixes from the external review.

- Terminal-escape injection in the client doctor. `recon doctor --client=<name>`
  reads workspace-scoped MCP config files (`.vscode/mcp.json`, `.cursor/mcp.json`,
  and similar) that an untrusted repository can supply. The config `command`
  value was copied into the report and rendered with Rich markup escaping only,
  which does not remove terminal control bytes, so a crafted command could emit
  ANSI / OSC sequences (screen control, clipboard writes) to the operator's
  terminal. The command is now passed through `strip_control_chars` before
  display; `args` and `autoApprove` already went through `json.dumps`, which
  escapes control bytes.
- CNAME-matcher ReDoS. The CNAME infrastructure detector runs catalog and
  custom / MCP-injected regex patterns against attacker-controlled CNAME
  targets. The regex validator caught nested quantifiers like `(a+)+` but not
  prefix-overlapping quantified alternation like `(a|aa)+`. `_validate_regex`
  now rejects the prefix-overlap shape, and the matcher bounds the CNAME input
  to 255 chars (the DNS name limit) before matching, capping backtracking
  amplification. Disjoint alternation like `(foo|bar)+` stays allowed, and no
  catalog pattern is affected.

Gate: full pytest, ruff, pyright (0 errors), new ReDoS and sanitization tests.

## [1.9.96] - 2026-06-05

### Batch-record validation hardening and introspection fixes

Three correctness fixes from an external review pass, all in code shipped earlier
this session.

- `classify_batch_record` no longer trusts `record_type` alone. The SH7
  discriminator selects which shape to validate, but the full shape is still
  enforced: a `record_type="lookup"` record must carry every required success
  field, and a `record_type="error"` record must be exactly the closed four-key
  error shape `{domain, error, error_kind, record_type}`. A malformed mapping
  that only sets `record_type` now classifies as `unknown` instead of being
  accepted as a valid record. The docstring is corrected to match.
- `schema_contract.py` (`Mapping`) and `explanation.py` (`Callable`) imported
  these only under `TYPE_CHECKING` while referencing them in runtime
  annotations, so `typing.get_type_hints()` raised `NameError`, breaking doc
  generators and introspection tooling. Both are now runtime imports.

Gate: full pytest, ruff, pyright (0 errors), new bypass and introspection tests.

## [1.9.95] - 2026-06-05

### Schema hardening 5/5: include-ecosystem always emits the wrapper (SH9)

Last of the pre-2.0 schema-hardening patches. When --include-ecosystem is set,
`recon batch --json` now always emits the BatchResult wrapper object, even when
no domain in the batch resolved. Previously it fell back to a bare array on an
all-failed batch, flipping the top-level type from object to array exactly when
a consumer's error path is already stressed (a consumer doing `result["domains"]`
would raise). The wrapper now always carries the error records under `domains`
with an empty `ecosystem_hyperedges`. The BatchResult and BatchArray schema
descriptions drop the removed fallback, and a regression test covers the
all-failed case.

This completes the SH1 to SH9 schema-hardening track from the four-lens pre-lock
review (the SH track in `docs/roadmap.md`); the v2.0 schema lock (G1) now applies
to a surface with no known regret.

Gate: full pytest (2755 passed), the schema / batch tests, ruff, pyright (0
errors), validate_fingerprint (841).

## [1.9.94] - 2026-06-05

### Schema hardening 4/5: record discriminator and machine-readable error_kind (SH7, SH8)

Adds self-describing record fields so a consumer (especially an agent handed a
detached payload without invocation context) can identify and version a record
without inferring the output mode from which keys are present. SH7 and SH8 ship
together because both touch the batch error record and the record classifier.

- SH7: every object-shaped output mode gains a required `record_type`
  discriminator (`lookup` on a single-domain success object, `batch_result` on
  the --include-ecosystem wrapper, `delta` on a delta report, `error` on a batch
  error record), and the single-domain root gains a required `schema_version`
  ("2.0") so a payload separated from the schema's $id can be routed across a
  future 2.x to 3.0 boundary. `classify_batch_record` is rewritten to branch on
  `record_type` first, with the prior key-set rules kept as a pre-v2.0 fallback
  (the v2.0-added required fields are excluded from that fallback so old records
  still classify).
- SH8: the batch error record gains a machine-readable `error_kind` enum
  (`validation` / `lookup` / `timeout`) so a consumer can route or alert on a
  code rather than the free-text `error` message. The error record stays
  `additionalProperties: false`, now with the four keys domain, error,
  error_kind, record_type.

The schema $defs (root, BatchErrorRecord, BatchResult, DeltaReport) and schema.md
update in lockstep; both schema copies stay byte-identical.

Gate: full pytest (2754 passed), the schema / batch / delta / contract tests,
ruff, pyright (0 errors), validate_fingerprint (841).

## [1.9.93] - 2026-06-05

### Schema hardening 3/5: fusion_enabled flag (SH6)

Adds a required top-level `fusion_enabled` boolean so a consumer can tell the
two fusion arrays (`slug_confidences`, `posterior_observations`) being empty
because fusion was not computed apart from them being empty because fusion ran
and found nothing. Derived at output time from whether the Bayesian layer
produced its node posteriors, so it adds no new stored state. The fusion-field
descriptions now point at `fusion_enabled` for the disambiguation;
`REQUIRED_TOP_LEVEL_FIELDS` updates in lockstep. Both schema copies stay
byte-identical.

(The SH7 record discriminator and SH8 error_kind ship together in the next
patch, since both touch the batch error record and the record classifier.)

Gate: full pytest (2754 passed), the schema tests (34), ruff, pyright (0 errors),
validate_fingerprint (841).

## [1.9.92] - 2026-06-05

### Schema hardening 2/4: per-field reshapes (SH2, SH5)

Second pre-2.0 schema-hardening patch. Reshapes two experimental or v2.0-new
fields from positional or bare-list forms into self-describing shapes that can
grow additively, so a future per-entry attribute does not force a major bump.

- SH2: `slug_confidences` changes from a positional `[slug, posterior]` tuple
  array to an object map `{slug: posterior}`, parallel to its structural twin
  `detection_scores` (the other slug-keyed scalar map). Both serialization sites
  (`cache.py`, `formatter.py`) now emit `dict(info.slug_confidences)`, mirroring
  the existing `detection_scores` pattern; the cache reader accepts both the new
  map and the legacy list so pre-v2.0 cache entries still load.
- SH5: `wildcard_sibling_clusters` (inside `cert_summary`) changes from a bare
  list of string lists to a list of `{names: [...]}` objects, matching the
  adjacent `deployment_bursts` / `CertBurst` shape and leaving room for a future
  per-cluster attribute. The cache reader accepts both forms.

The internal `TenantInfo` representations are unchanged (still tuples); only the
serialized output shape changes. Both schema copies stay byte-identical.

Gate: full pytest (2754 passed), the schema / cache / contract tests, ruff,
pyright (0 errors), validate_fingerprint (841).

## [1.9.91] - 2026-06-05

### Schema hardening 1/4: descriptions and contract loosening (SH1, SH3, SH4)

First of the pre-2.0 schema-hardening patches. A four-lens pre-lock review of
`docs/recon-schema.json` found a finite set of field shapes cheaper to fix now
than after the lock (the SH1-SH9 track in `docs/roadmap.md`). This patch carries
the changes that do not alter the emitted output shape:

- **SH1**: reconcile the contradictory `partial` description (the JSON's "core
  sources only, CT-only degradation does not flip it" definition is canonical;
  `schema.md` now matches). Rewrite the `PosteriorObservation` / `sparse` /
  interval-bound descriptions so they survive CAL14 (a declarative node can be
  confidently-absent: low posterior, narrow interval, `sparse=false`) and carry
  the CAL13 "evidence-responsive, not frequentist coverage" framing.
- **SH3**: remove the three CT-pipeline telemetry fields (`ct_provider_used`,
  `ct_cache_age_days`, `ct_attempt_outcome`) from the required set so the CT
  pipeline can evolve later without a major bump; they are still emitted
  best-effort. `REQUIRED_TOP_LEVEL_FIELDS` updates in lockstep. `ct_subdomain_count`
  (a result, not pipeline-internal) stays required.
- **SH4**: drop the closed host enum on `cloud_instance` (Microsoft controls
  those values and adds sovereign clouds); the type stays `string|null` with the
  known values documented.

No emitted field changed shape. Both schema copies (`docs/` and
`recon_tool/data/`) stay byte-identical.

Gate: full pytest (2755 passed), the schema tests (34), ruff, pyright (0 errors),
validate_fingerprint (841).

## [1.9.90] - 2026-06-05

### Bayesian: node-dependent missingness for the email-policy node (Track C-cal, CAL14)

The Bayesian layer now supports per-node missingness. Hideable nodes keep the
asymmetric LR=1 absence rule (a non-firing binding contributes nothing, correct
for infrastructure an operator can hide). Declarative nodes treat the absence of
a public-declaration signal as genuine disconfirming evidence, because DMARC /
SPF / MTA-STS policy cannot be hidden from passive DNS.

`email_security_policy_enforcing` is the first (and currently only) declarative
node. The changes are corpus-grounded on a 2026-06 5,238-domain run and
documented in the YAML:

- prior 0.25 -> 0.62 (61.7% of the corpus publishes an enforcing DMARC policy; a
  CAL12 base-rate correction)
- `mta_sts_enforce` likelihood [0.70, 0.05] -> [0.06, 0.01] (only ~6% of
  enforcing domains publish MTA-STS; the old value was an order of magnitude off,
  and its low present-likelihood correctly makes its absence near-neutral)
- `spf_strict` likelihood [0.70, 0.45] -> [0.53, 0.27] (LR ~2.0, regrounded)
- the two DMARC bindings join a `dmarc_policy` correlation group with an explicit
  whole-group absence likelihood [0.05, 0.85], because reject and quarantine are
  mutually exclusive and a per-binding complement-product would double-count

Semantic ruling (definition A, RFC 7489): "enforcing" means an observable DMARC
reject/quarantine policy; strict SPF alone is hygiene, not enforcement. The new
YAML fields are `missingness: declarative` and `group_absence`, both validated in
the loader. A declarative node's `n_eff` counts informative absences, so a
confidently-non-enforcing domain gets a narrow interval around a low posterior
rather than a wide "sparse" one (the criterion-(a) baseline tests are reframed to
exempt declarative nodes).

Result: the synthetic-calibration conditional ECE for this node drops from ~0.31
to ~0.03. The numbers are directionally-accurate corpus-grounded estimates that
the maintainer-validation loop (roadmap PV2) re-checks each release, not frozen
values; the credible interval carries the residual uncertainty. Hideable-node
behavior is unchanged.

Gate: full pytest (2754 passed), pyright (0 errors), ruff, validate_fingerprint
(841).

## [1.9.89] - 2026-06-04

### Catalog: third full-corpus gap-mining batch, C2 deferred set cleared (Track C, C2)

Batch 3 closes the C2 deferred vendor set from the v1.9.87 to v1.9.88 run. Three
vendors verified against public docs and merged as `cname_target` rules; the
catalog grows from 838 to 841 entries.

- `bamko` (`bamkounified.com`) - BAMKO branded-merchandise company stores
- `gamania-cloudforce` (`cloudforce.gamania.com`) - Gamania CloudForce, a Taiwan
  CDN / DNS / anti-DDoS provider
- `turbify` (`turbify.biz`) - Turbify (formerly Yahoo Small Business) SMB hosting

Two deferred candidates were resolved without a new rule: Marketo landing pages
(`mktoweb.com`) are already covered, and the `mktoapps.com` terminus seen in the
corpus is Marketo's own first-party host, not a customer target; `ejoco` is
dropped (no public vendor identity, and every in-corpus sample is one parent
media group, so it fails the general-purpose bar). `bamko` joins the business-
apps fallback; `gamania-cloudforce` and `turbify` map to the Cloud panel category
and the multi-cloud rollup-exclusion set, the same convention regional CDNs
(azion, cloudinary) and SMB hosting (wpengine, kinsta) already follow. For
consistency, `byteark` (v1.9.88) is aligned into that exclusion set as well, so a
regional CDN no longer inflates the at-a-glance multi-cloud count.

This closes Track C C2's named third-party residual; the remaining unclassified
termini are org-internal GSLB / load-balancers that by design are not catalogued.
Corpus and per-domain results stay gitignored, no real-company data committed.

Gate: validate_fingerprint (841), metadata coverage, ruff, pyright (0 errors),
full pytest (2754 passed), slug-category and cloud-vendor-coverage invariants.

## [1.9.88] - 2026-06-04

### Catalog: second full-corpus gap-mining batch (Track C, C2)

Batch 2 from the same 5,241-domain run as v1.9.87, re-triaged at min-count 2 to
reach the lower-frequency tier, plus verification of vendors deferred from batch
1. Five vendors merged as high-precision `cname_target` rules; the catalog grows
from 833 to 838 entries.

- `entra-app-proxy` (`msappproxy.net`) - Microsoft Entra Application Proxy, the
  on-premises-app publishing CNAME target (vendor-doc-sourced from Microsoft
  Learn)
- `workato` (`apim.workato.com`, `apim-custom.workato.com`) - Workato API
  platform (iPaaS)
- `byteark` (`byteark.com`) - ByteArk CDN and video streaming
- `sitedetour` (`sitedetour.com`) - SiteDetour URL-redirect / dynamic-QR platform
- `claranet` (`.clara.net`) - Claranet managed-services and hosting

`entra-app-proxy` maps to the Identity panel category; `byteark` and `claranet`
join the Cloud category and the multi-cloud rollup; `workato` and `sitedetour`
join the business-apps fallback. Each was verified against public vendor
documentation before merge; the Entra App Proxy rule uses the documented
`msappproxy.net` target rather than the `msidentity.com` intermediate observed in
the corpus. Vendors still deferred (Gamania, BAMKO, Turbify, ejoco, Marketo
landing pages) await a corpus-observed customer instance or pattern confirmation;
the defunct Edgio CDN is dropped. Corpus and per-domain results stay gitignored,
no real-company data committed.

Gate: validate_fingerprint (838), metadata coverage, ruff, pyright (0 errors),
full pytest (2754 passed), slug-category and cloud-vendor-coverage invariants.

## [1.9.87] - 2026-06-04

### Catalog: first full-corpus gap-mining batch (Track C, C2)

The first catalog-growth batch sourced from a full-corpus gap-mining run rather
than vendor-doc reading (C1). A deterministic-pipeline scan over the 5,241-domain
gitignored corpus (concurrency 5, CT off, 0.1% error) surfaced 1,335 unclassified
CNAME-terminus buckets; triage at min-count 3 reduced that to 30 candidates, of
which 5 vendors merged as high-precision `cname_target` rules. The catalog grows
from 829 to 833 entries.

- `reblaze` (`reblaze.com`) - Reblaze WAAP front, part of Link11
- `indusface` (`indusguard.com`, `induscdn.com`) - Indusface AppTrana managed WAAP
- `sharpspring` (`marketingautomation.services`) - SharpSpring marketing automation
- `hugedomains` (`hugedomains.com`) - HugeDomains parking / for-sale host
- `aws-nlb` extended with the two AWS GovCloud ELB regions
  (`elb.us-gov-east-1.amazonaws.com`, `elb.us-gov-west-1.amazonaws.com`), closing
  the GovCloud gap in the existing commercial-region set

The two WAAP fronts join the Cloud panel category and the multi-cloud rollup
alongside `imperva`; `sharpspring` and `hugedomains` join
`EXPECTED_BUSINESS_APPS_FALLBACK`. About half the candidates were org-internal
GSLB / load-balancer hostnames or first-party hyperscaler properties and were
correctly excluded (a `cname_target` rule marks a third-party service distinct
orgs point at, not one org's own internal plumbing); a handful of real vendors
(Claranet, Gamania, BAMKO, SiteDetour, Turbify, ejoco, and the observed-but-
defunct Edgio) are deferred to a later batch pending pattern verification. The
aggregate triage trail is in `validation/v1.9.87-c2-corpus-batch.md`; the corpus
and per-domain results stay gitignored, no real-company data committed.

Validated against `validate_fingerprint.py` (833 entries), the metadata-coverage
gate, ruff, pyright (0 errors), and the full test suite (2754 passed), plus the
slug-category and cloud-vendor-coverage invariants.

## [1.9.86] - 2026-06-03

### Catalog: four more cname_target fingerprints from a live-analysis batch (Track C, C1)

A fifth live-analysis gap-fill batch. Four distinctive vendors with custom-domain
CNAMEs the catalog did not cover, added as high-precision `cname_target` rules in
`surface.yaml`. The catalog grows from 825 to 829 entries.

- `extole` (`extole.com`) - referral / customer-advocacy marketing
- `staffbase` (`staffbase.com`) - employee-communications / intranet
- `superfiliate` (`superfiliate.com`) - creator / affiliate commerce
- `transcend` (`transcend-cdn.com`) - data-privacy / consent management (GDPR / CCPA)

Same discipline: intra-org and unattributable targets dropped, only vendor
patterns and neutral descriptions committed, no observed apex in the repo. The
four slugs join `EXPECTED_BUSINESS_APPS_FALLBACK`. Validated against
`validate_fingerprint.py`, the metadata-coverage gate, and the shadowing /
specificity / expansion tests.

This is the fifth catalog batch of the session; the live-analysis loop has added
21 vetted `cname_target` rules (808 to 829) across `surface.yaml` while keeping
every committed example free of real-company data.

## [1.9.85] - 2026-06-03

### Catalog: three more cname_target fingerprints from a live-analysis batch (Track C, C1)

A fourth live-analysis gap-fill batch. Three distinctive, well-known vendors with
custom-domain CNAMEs the catalog did not cover, added as high-precision
`cname_target` rules in `surface.yaml`. The catalog grows from 822 to 825 entries.

- `manageengine` (`manageengine.com`) - ManageEngine (Zoho) IT service / asset management
- `northflank` (`northflank.com`) - Northflank developer platform (PaaS)
- `urlgenius` (`urlgeni.us`) - URLgenius mobile deep linking / app attribution

Conservative curation continued: from this batch's candidates, intra-org
infrastructure and two substring-risky patterns were deliberately dropped
(`files.com` would match `profiles.com`; `classy.org` would match
`classy.organic.com`, and "classy" is not a distinctive label). Only the vendor
patterns and neutral descriptions are committed. The three slugs join
`EXPECTED_BUSINESS_APPS_FALLBACK`. Validated against `validate_fingerprint.py`,
the metadata-coverage gate, and the shadowing / specificity / expansion tests.

## [1.9.84] - 2026-06-03

### Catalog: seven more cname_target fingerprints from a live-analysis batch (Track C, C1)

A third live-analysis gap-fill batch over a fresh spread of example domains. Seven
SaaS vendors with distinctive custom-domain CNAMEs that the catalog did not cover,
each added as a high-precision `cname_target` rule in `surface.yaml`
(`tier: application`). The catalog grows from 815 to 822 entries.

- `lumapps` (`lumapps.com`) - employee-experience / intranet
- `vgs` (`verygoodproxy.com`) - Very Good Security tokenization / data-redaction proxy
- `securitypal` (`securitypal.com`) - security-questionnaire / compliance automation
- `greatquestion` (`greatquestion.co`) - user-research / customer-interview platform
- `heymarvin` (`heymarvin.com`) - Marvin qualitative-research repository
- `airmason` (`airmason.com`) - digital employee-handbook platform
- `nudata` (`nudatasecurity.com`) - NuData (Mastercard) behavioral-biometrics / fraud

As with the prior batches, every pattern is distinctive enough that the substring
matcher will not false-positive; intra-org infrastructure, already-covered vendors
(Marketo), and ambiguous targets from the same run were dropped. Only the vendor
patterns and neutral descriptions are committed; no observed apex reaches the repo.
The seven slugs join `EXPECTED_BUSINESS_APPS_FALLBACK`. Validated against
`validate_fingerprint.py`, the metadata-coverage gate, and the shadowing /
specificity / expansion tests.

## [1.9.83] - 2026-06-03

### Catalog: six cname_target fingerprints from a live-analysis batch (Track C, C1)

A second live-analysis gap-fill batch. Passive lookups across a spread of example
domains surfaced unclassified custom-domain CNAMEs to six SaaS vendors the catalog
did not cover; each was added as a high-precision `cname_target` rule in
`surface.yaml` (`tier: application`). The catalog grows from 809 to 815 entries.

- `crowdin` (`crowdin.com`) - localization / translation management
- `evervault` (`evervault.app`) - developer field-level encryption / Relay
- `intellum` (`intellum.com`) - corporate learning / LMS
- `rocketlane` (`rocketlane.com`) - customer onboarding / PSA
- `bettermode` (`bettermode.io`) - community platform (formerly Tribe)
- `impartner` (`impartner.io`) - partner-relationship management (PRM)

Each pattern is distinctive enough that the substring matcher (the cname_target
classifier matches `pattern in hop`) will not false-positive on unrelated hosts;
short/ambiguous candidates from the same batch were deliberately dropped. Per the
catalog discipline, only the vendor patterns and neutral descriptions are
committed: no observed apex or per-domain finding reaches the repo. The six slugs
join `EXPECTED_BUSINESS_APPS_FALLBACK` (conservative panel bucket). Validated
against `validate_fingerprint.py`, the metadata-coverage gate, and the shadowing
/ specificity / expansion tests.

## [1.9.82] - 2026-06-03

### Catalog: Thinkific cname_target fingerprint (Track C, item C1)

A live-analysis gap-fill: a passive lookup surfaced an unclassified
`learn.`-style subdomain CNAMEd to a `*.thinkific.com` target (Thinkific, the
online-course / LMS storefront platform), which the catalog did not cover. Added
a high-precision `cname_target` rule (`surface.yaml`, `tier: application`,
slug `thinkific`). The catalog grows from 808 to 809 entries.

Per the catalog discipline, only the vendor pattern and a neutral description are
committed: no observed apex or per-domain finding reaches the repo. `thinkific`
joins `EXPECTED_BUSINESS_APPS_FALLBACK` in `tests/test_slug_category_invariant.py`,
the same conservative panel bucket as its LMS peers `coursera` and `northpass`.
Validated against `validate_fingerprint.py`, the metadata-coverage gate, and the
shadowing / specificity / expansion tests.

## [1.9.81] - 2026-06-03

### Round-six ingestion audit: output-sink control stripping (Track D, item D1)

A fresh adversarial pass over the ingestion / parse paths re-traced every
attacker-controlled string to its output sink and closed two new MED findings
(folded into `docs/security-audit-resolutions.md` as round six). Both are
source-derived strings that reached the live terminal panel via rich
`Text.append` (which does not strip ESC) without passing through the round-three
merger scrub:

- **Service strings.** `GoogleSource` builds `f"CSE Key Manager: {host}"` from
  the `urlparse(...).hostname` of a `cse.<domain>` config's `discovery_uri`, and
  `urlparse` preserves control bytes in the host. A domain owner controlling
  `cse.<domain>` could land an ANSI / newline payload on the operator's terminal.
- **DMARC `p=` value.** `_apply_dmarc` stored the policy token unvalidated
  (only `.lower()`, which keeps control bytes), unlike the allowlist-validated
  `mta_sts_mode` and range-checked `dmarc_pct`.

Fixed in one consistent place: `merge_results` now control-strips the whole
`services` set, `dmarc_policy`, and `google_idp_name` (the last as defense in
depth) at the finalization boundary, alongside the existing
`display_name` / `auth_type` / `region` scrub. Any future source that emits a
control-bearing service string or policy is covered without a per-source change.
Legitimate values are unchanged. Pinned by `tests/test_ingestion_sanitization.py`.

## [1.9.80] - 2026-06-03

### Server-tool coverage: the Bayesian + clustering MCP tools (Track B, item B4)

A new `tests/test_server_bayesian_tools.py` covers `get_posteriors`,
`explain_dag`, and `cluster_verification_tokens`, the three largest untested
blocks in `server.py`. Test-only change; no production code touched.

Following the established server-tool test pattern (patch `resolve_tenant` so the
cache-miss path runs without network), the tests exercise:

- `get_posteriors`: the posterior block shape (entropy reduction, evidence count,
  per-node posterior / interval / n_eff / sparse), the cache-hit short-circuit,
  and the validation / lookup-error / unexpected-error branches.
- `explain_dag`: the text and DOT renderers (asserting they differ), the
  invalid-format rejection, and the validation-error branch.
- `cluster_verification_tokens`: a shared-token cluster across two domains, the
  empty-input and too-many-domains guards, and the JSON envelope shape.

This lifts `server.py` branch coverage, completing the testable items of Track B
(B1 to B4). The global coverage gate stays at 82% branch; it is deliberately not
ratcheted here, to avoid flaky failures on unrelated future changes that dip
slightly.

## [1.9.79] - 2026-06-03

### Source-boundary fault injection (Track B, item B3)

A new `tests/test_source_fault_injection.py` asserts the resolver's aggregate
behaviour when sources fault. The per-source tests already prove each source
turns a malformed / truncated / timed-out / non-object provider payload into a
clean `SourceResult` with an error; this covers what happens when those faults
combine across the pool. Test-only change; no production code touched.

A `_FaultySource` injects each fault mode (raise, hang, upstream error, degraded,
good) deterministically with no network, driving:

- exception hygiene: a raising source is converted by `_safe_lookup` into an
  error `SourceResult` and never propagates;
- partial failure: a good source still produces its tenant alongside crashing
  and erroring siblings, which surface as error results;
- degraded surfacing + hedging: a degraded source appears in the merged
  `TenantInfo.degraded_sources` and the result is never HIGH confidence;
- all-fail: when no source yields a tenant, `resolve_tenant` raises
  `ReconLookupError(all_sources_failed)`;
- timeout: a hanging source trips the aggregate timeout as
  `ReconLookupError(timeout)`.

One test pairs a real `OIDCSource` (fed a truncated body via
`httpx.MockTransport`) with a good faulty source, showing a malformed provider
payload is isolated end to end through `resolve_tenant` while the good source's
tenant still wins.

## [1.9.78] - 2026-06-03

### Cache-lifecycle stateful machine (Track B, item B2)

A new `tests/test_cache_stateful.py` adds a Hypothesis `RuleBasedStateMachine`
that drives arbitrary sequences of cache operations (write, write-with-unknown-
future-fields, corrupt, stale, clear, clear-all) over a small pool of valid and
invalid domain keys, and reconciles the on-disk state against a model after
every step. Test-only change; no production code touched.

The `@invariant` asserts, after each operation, that:

- a domain written with a good payload reads back equal (load-known);
- a payload carrying extra future fields still reads back equal (ignore-unknown
  / forward-compat);
- a corrupt payload reads back as None and never raises (skip-malformed);
- a TTL-stale entry reads back as None (lazy eviction);
- invalid / traversal keys never store and always read None (the
  `_safe_cache_path` containment guard).

This complements the single-operation cache tests (`test_cache_roundtrip`,
`test_cache_forward_compat`, `test_cache_cli`) by reaching the sequence-level
interleavings (corrupt-then-rewrite, clear the wrong key, stale after a
particular order) a single-shot test cannot. The machine isolates each example
in a temporary `RECON_CONFIG_DIR` and restores the environment on teardown.

## [1.9.77] - 2026-06-03

### deal contracts on the boundary validators (Track B, item B1)

The third `deal` Design-by-Contract pass, after the inference core (v1.9.31) and
the engine matchers (v1.9.35). `validator.py` gains postconditions on its two
boundary functions:

- `strip_control_chars` carries `@deal.post(_has_no_control_chars)`, asserting no
  C0 (0x00-0x1F), DEL (0x7F), or C1 (0x80-0x9F) control character survives in its
  output. This is the load-bearing security invariant: the result is rendered to
  terminals and into JSON / markdown / MCP output, where a surviving ESC or
  newline would be an injection vector.
- `validate_domain` carries `@deal.post(_is_normalized_domain)`, asserting every
  successful return is lowercase and matches the domain grammar (the
  ValueError-raising paths are unconstrained).

Both predicates are named and unit-tested in `tests/test_contracts.py`
(`TestBoundaryValidators`: accept valid shapes, reject control bytes and
unnormalized domains), with fire-on-violation tests proving the postconditions
raise `deal.PostContractError` when a decorated function returns a violating
value. Contracts remain no-ops under `python -O` (proven by the existing
`TestContractsDisabledUnderO`), so installed users pay no runtime cost.

## [1.9.76] - 2026-06-03

### Complexity decomposition: the server tool pair (Track A, item A8) - Track A complete

The two remaining `# noqa: C901` markers, both in `server.py`, are removed.
With this patch **zero `# noqa: C901` markers remain in `recon_tool/`**, so
Track A (complexity decomposition) of the pre-2.0 hardening phase is complete:
every function in the package is under the mccabe cap of 15, and the gate from
v1.9.37 now holds the whole tree, not just new code. Behaviour is preserved,
held by the server, exposure, and GWS suites (`test_server`, `test_server_cache`,
`test_exposure_server`, `test_gws_features`, `test_mcp_introspection`).

- `lookup_tenant`: the text-format rendering moves to `_lookup_tenant_text`, with
  the Google Workspace lines in `_lookup_tenant_gws_lines`. The cache /
  rate-limit / resolve block with its structured logging is left inline (it is
  not shared with `_resolve_or_cache`, which does not log), so observability is
  unchanged.
- `simulate_hardening`: the fix-parsing if/elif chain moves to `_simulate_fixes`
  over a small `_SimState`, dispatched through `_apply_one_fix` with
  `_apply_dmarc_fix` and `_apply_mta_sts_fix` for the two stateful controls.
  Keyword precedence (first match wins) and the recognised-no-op cases (a
  quarantine request when the policy is already reject; a bare mta-sts when a
  mode is already set) are preserved exactly, including that they append no
  message rather than "Unrecognized".

The mccabe gate comment in `pyproject.toml` is updated to reflect that the
grandfathered backlog is now cleared.

## [1.9.75] - 2026-06-03

### Complexity decomposition: merge_results (Track A, item A7)

`merge_results` (complexity ~64) drops under the C901 cap and loses its
`# noqa: C901`. It is now an orchestrator that calls focused, single-purpose
helpers; the output TenantInfo is identical, held by the merger property tests
(`test_merger`, `test_merger_error_surfacing`, `test_conflict_provenance`) plus
`test_email_topology`, `test_degraded_sources`, and the insights suites.

- First-wins scalar merge moves to `_merge_scalar_fields` (returning a
  `_ScalarFields` NamedTuple); conflict tracking to `_compute_merge_conflicts`;
  the all-sources-failed guard to `_raise_if_all_sources_failed`.
- Display-name resolution, free-text scrubbing, detection aggregation, the
  email-security score, and the SPF include-count parse move to
  `_resolve_display_name`, `_scrub_free_text`, `_aggregate_detections`,
  `_email_security_score`, and `_extract_spf_include_count`.
- The metadata propagations move to `_merge_ct_metadata`, `_merge_oidc_metadata`,
  `_collect_evidence`, `_collect_degraded`, and a generic `_first_non_none`
  (cert_summary, dmarc_pct, infrastructure_clusters).
- Confidence finalization moves to `_finalize_confidence` (the dual-confidence
  min plus the degraded-source downgrade with the CT-recovery exception);
  lexical observations to `_append_lexical_observations`; and the three
  subdomain-keyed dedupes to `_dedupe_surface` / `_dedupe_unclassified` /
  `_dedupe_motifs`.

Behaviour is preserved exactly, including the placeholder display-name skip and
the first-source-wins ordering. Two `# noqa: C901` markers remain, both in
`server.py` (`lookup_tenant`, `simulate_hardening`).

## [1.9.74] - 2026-06-03

### Complexity decomposition: _batch (Track A, item A6)

`_batch` (complexity ~19 once its marker was removed; the mccabe count folds in
its nested coroutines) drops under the C901 cap and loses its `# noqa: C901`.
The outer body becomes a thin pipeline and the per-domain coroutine moves to a
module-level helper so it is measured on its own. Output is held unchanged
across all five modes (panel, JSON, markdown, CSV, NDJSON); `test_batch`,
`test_ecosystem`, the cli coverage suites, and `test_siem_examples` stay green.

- Flag validation and domain loading (the stdin / file read plus order-preserving
  dedupe) move to `_batch_validate_flags` and `_batch_load_domains`.
- The per-domain work moves to module-level `_batch_process_one`, with
  `_batch_error_result` / `_batch_success_result` shaping the result for the
  active output mode. `_batch` keeps a small `_run_one` closure that binds the
  batch-scoped state (semaphore, `batch_infos`, flags) and delegates to it.
- The cross-domain enrichment splits into `_batch_attach_shared_tokens` (v0.9.3
  shared verification tokens) and `_batch_attach_peers` (v1.3 tenant-ID and
  display-name peers); `_batch_emit_json`, `_batch_emit_ndjson`, and
  `_batch_render_results` own the output paths.
- `_batch_apply_fusion` holds the batch Bayesian recompute. It deliberately
  preserves the shipped batch shape, which omits `evidence_ranked` on each
  posterior (the single-domain `_lookup_apply_fusion` includes it). That
  difference is pre-existing and is left intact here; reconciling the two is a
  separate question, not part of this behaviour-preserving decomposition.

Three `# noqa: C901` markers remain: `merge_results` and the two `server` tools
(`lookup_tenant`, `simulate_hardening`).

## [1.9.73] - 2026-06-03

### Complexity decomposition: _lookup (Track A, item A6)

The `_lookup` orchestrator (the largest function in the tree, complexity ~77)
drops under the C901 cap and loses its `# noqa: C901`. It is now a thin
dispatcher: normalize the output flags, validate the domain and the
mutually-exclusive flag combinations via `_lookup_validate`, then hand off to a
mode helper. Output is held unchanged; the 155 cli-focused tests
(`test_cli`, `test_cli_coverage`, `test_cli_coverage_extra`, `test_cli_explain`,
`test_exposure_cli`, `test_chain`, `test_delta_cli`, `test_profiles`,
`test_strict_mode`, `test_explanation_dag`, `test_fusion_integration`) stay
green.

- Each mode moves to its own helper: `_lookup_compare`, `_lookup_chain`,
  `_lookup_exposure`, `_lookup_gaps`, and `_lookup_standard`.
- The repeated spinner/resolve pattern collapses into `_resolve_with_spinner`
  (status spinner unless output is machine-readable) and `_resolve_cached`
  (cache read, resolve on miss, write back), shared by the exposure/gaps paths.
- The standard path's heavy sub-blocks split out too: `_lookup_resolve_standard`
  (cache + resolve + fusion + write-back), `_lookup_apply_fusion` (the Bayesian
  posterior recompute), `_lookup_compute_observations` (posture + profile),
  `_lookup_emit_explain_dag` / `_lookup_emit_json` / `_lookup_emit_markdown` /
  `_lookup_emit_panel`, and `_synthetic_source_results` (the cache-hit
  SourceResult reconstruction for the `--explain` status panel).
- The lazy-import discipline is preserved: each helper imports its heavy
  dependencies at call time, and the resolver is still imported from
  `recon_tool.resolver` so the existing test mocks keep working.

Four `# noqa: C901` markers remain: `_batch`, `merge_results`, and the two
`server` tools (`lookup_tenant`, `simulate_hardening`).

## [1.9.72] - 2026-06-03

### Complexity decomposition: signals_show and _doctor (Track A, the cli leaves)

Two more `# noqa: C901` markers removed (roadmap Track A, the cli set, item
A6). Both are leaf functions, so the decomposition is low-risk and the output
is held unchanged.

- `signals_show` (`cli.py`) splits into `_signal_show_payload` (the `--json`
  dict), `_render_signal_not_found` (the not-found error plus near-miss
  suggestions), `_render_signal_section` (a shared blank-line / bold-header /
  bulleted-list helper that no-ops on an empty list so callers stay
  branch-free), and `_render_signal_detail` (the human-readable view); the
  command body becomes a thin dispatcher. A new `tests/test_signals_show_cli.py`
  pins the JSON payload, each text-mode section, and the not-found exit code,
  since the command had no direct coverage before.
- `_doctor` (`cli.py`) splits into one helper per check group
  (`_doctor_identity_checks`, `_doctor_dns_check`, `_doctor_ct_check`,
  `_doctor_mcp_check`, `_doctor_fingerprint_db_check`,
  `_doctor_custom_fingerprints_check`, `_doctor_signal_db_check`,
  `_doctor_schema_fields_check`, `_doctor_custom_signals_check`) plus
  `_doctor_print_header` and `_doctor_render`; the orchestrator appends the
  checks in the same order. That order is load-bearing for the httpx mock in
  `tests/test_doctor.py` (a positional side-effect list), so it is preserved
  exactly.

Five `# noqa: C901` markers remain (`_lookup`, `_batch`, `merge_results`, and
the two `server` tools); the cap from v1.9.37 still holds new code.

## [1.9.71] - 2026-06-02

### Policy-node calibration: spf_strict recalibration + node-dependent missingness finding

A full-corpus synthetic calibration pass (20,000 samples) found
`email_security_policy_enforcing` poorly calibrated even conditionally
(ECE ~0.31, the [0.85] reliability bin realizing only 0.166), while the other
nodes were within the gates (cdn_fronting 0.02, the M365 / GWS / federated
cluster ~0.08).

- **`spf_strict` down-weight** (`bayesian_network.yaml`): from `[0.75, 0.30]`
  (LR 2.5) to `[0.70, 0.45]` (LR ~1.6). Conceptual, not corpus-fitted: a strict
  SPF `-all` is near-ubiquitous email hygiene that many domains publish without
  enforcing a DMARC reject/quarantine policy, so its discriminating power for
  full enforcement is weak (the same reasoning that removed `dkim_present` in
  v1.9.6). This took the node to conditional ECE ~0.28.
- **Node-dependent missingness finding** (`docs/correlation.md` §4.3, roadmap
  CAL14): the residual is the missingness regime, not one binding. The
  asymmetric / LR=1 absence rule is right for hideable infrastructure (m365,
  okta) but wrong for public-declaration signals (DMARC / SPF / MTA-STS policy)
  whose absence is genuine, not hidden. The principled fix is per-node MAR /
  symmetric conditioning. A prototype confirmed the direction; it is held as its
  own fully-validated patch because it ripples into the n_eff / sparse semantics
  and the per-node stability criterion. v2.0 calibration claims gate on the
  maximum per-node conditional ECE, not the mean.

No public output shape changed. The policy-node posterior moderates on
weak-signal-only domains.

## [1.9.70] - 2026-06-02

### Evidence-group correction for conditionally-dependent bindings

Bayesian-core math (roadmap CAL7; `docs/correlation.md` §4.3). The likelihood
product `L(O | X) = prod ell_b` treated a node's fired bindings as conditionally
independent given the node. For co-firing correlated readings of one fact
(`microsoft365` + `entra-id` + `exchange-online` for `m365_tenant`, or the two
Google Workspace slugs) that over-counts the evidence: it compounds the
log-likelihood-ratio and produces an over-confident posterior with too narrow an
interval. This is the mirror of the asymmetric-likelihood conservatism on
hardened targets (the layer was conservative on hidden targets and
over-confident on richly-instrumented ones).

- `_Evidence` gains an optional `group`. Bindings sharing a group are reduced to
  their strongest fired member (max `|LLR|`) before the product, so a group
  contributes one effective likelihood ratio rather than the sum
  (`lambda_g = max_b lambda_b`, the conservative perfectly-dependent bound).
  Ungrouped bindings are unchanged, so this is a strict refinement that affects
  only nodes whose YAML declares a group.
- `bayesian_network.yaml` groups the three M365 slugs (`m365_indicators`) and
  the two GWS slugs (`gws_indicators`). On a domain exposing two M365 slugs the
  `m365_tenant` posterior moves from 0.998 to 0.950 and the 80% interval widens
  from [0.977, 1.000] to [0.835, 1.000].
- Covered by `tests/test_bayesian_evidence_groups.py`; the `--explain-dag`
  snapshot is updated to the corrected values.

Deterministic-vs-Bayesian consistency is preserved: lowering a correctly-
detected node's posterior cannot create a disagreement. A post-grouping
full-corpus calibration refresh (the interval-width effect) is a follow-up.

### Dependency hygiene: pyjwt 2.13.0

Bump the transitively-pulled `pyjwt` (via `mcp[crypto]`) from 2.12.1 to 2.13.0,
which fixes PYSEC-2026-175, PYSEC-2026-177, PYSEC-2026-178, and PYSEC-2026-179.
These advisories published after the green CI run and the fixed version is
available, so the lockfile is upgraded rather than the advisory ignored. The
disputed no-fix PYSEC-2025-183 remains on the documented ignore list.

## [1.9.69] - 2026-06-01

### Decompose `explain_insights` under the C901 cap

Complexity-decomposition track (item A5).

- `recon_tool/explanation.py`: the 16-branch insight-to-generator dispatch in
  `explain_insights` moves to `_classify_insight`. The two special cases (the
  signal-name `": "` parse and the email-security all-slug scan) are handled
  explicitly; the remaining keyword branches become an ordered
  `_INSIGHT_RULES` table of (predicate, generator label, candidate slugs,
  note), preserving the original first-match order. `explain_insights` becomes
  a thin loop that classifies, appends detection scores, and builds the
  record. The function drops its `# noqa: C901`.

No behavior change: the insight-to-generator mapping, attributed slugs, fired
rules, and confidence derivations are unchanged, verified by the explanation
suite (174 tests).

## [1.9.68] - 2026-06-01

### Decompose the email-security and cert-intel DNS detectors

Complexity-decomposition track (item A3, part 2; `sources/dns.py` now carries
no `# noqa: C901`).

- `_detect_email_security` keeps the concurrent record probes and dispatches to
  per-record appliers: `_apply_dmarc` (with `_apply_dmarc_pct` for the bounded
  `pct=` parse), `_apply_bimi` (presence + best-effort VMC enrichment),
  `_apply_mta_sts` (presence + policy-mode fetch), and `_apply_tls_rpt`.
- `_detect_cert_intel` splits into `_query_cert_providers` (the crt.sh ->
  CertSpotter loop with soft-failure handling), `_classify_ct_failure`,
  `_ct_failure_outcome`, and `_apply_cached_cert_intel` (shared by the
  cache-first and cache-fallback paths). The orchestrator keeps the
  cache-first / live / cache-fallback ordering.
- Both drop their `# noqa: C901`. 8 markers remain across the package, all on
  the `cli` / `explanation` / `merger` / `server` behaviour-heavy functions.

No behavior change: email-security detection, the soft-failure / cache-fallback
semantics, and the per-record outcome labels are unchanged, verified by the
DNS-source / CT / email-security / fallback tests (325 passed).

## [1.9.67] - 2026-06-01

### Decompose the DKIM and BIMI-VMC DNS detectors under the C901 cap

Complexity-decomposition track (item A3, part 1 of the `sources/dns` detectors).

- `_detect_dkim` keeps the concurrent selector probes but moves each provider's
  attribution to a focused `ctx`-mutating helper: `_apply_exchange_dkim`
  (Exchange + onmicrosoft.com tenant capture), `_apply_google_dkim` (TXT then
  CNAME), `_apply_esp_dkim` (Mailchimp / SendGrid / ... by CNAME hint), and
  `_apply_generic_dkim` (generic-selector confirmation). The ESP and generic
  selector tables move to module scope.
- `_parse_bimi_vmc` splits into `_extract_bimi_vmc_url`, `_bimi_vmc_url_is_safe`
  (the SSRF guard), and `_parse_vmc_subject` (cryptography with a regex
  fallback); the async function keeps the fetch and the broad parse-failure
  guard.
- Both drop their `# noqa: C901`.

No behavior change: DKIM attribution, the SSRF guard, and VMC parsing are
unchanged, verified by the DNS-source / DKIM / BIMI / email-security tests.

## [1.9.66] - 2026-06-01

### Decompose the CT-provider `query` C901 pair

Complexity-decomposition track (item A4).

- `recon_tool/sources/cert_providers.py`: the pure-parse cores of the two CT
  provider `query` methods move to module-level helpers,
  `_extract_crtsh_entries` (the bounded crt.sh name / cert-entry extraction)
  and `_parse_certspotter_issuance` (one CertSpotter issuance to safe SAN
  names, a cert entry, and the pagination cursor). Each `query` becomes a thin
  fetch / paginate driver around its parser, and both drop their
  `# noqa: C901`.

No behavior change: the CT fetch, rate-limit handling, pagination, and the
extracted parsing are unchanged (the caps, the safe-SAN filter, and the
429 / degraded-source signals all hold), verified by the CT-pipeline-resilience
and fallback-chain tests.

## [1.9.65] - 2026-06-01

### Decompose the `validation_runner` C901 pair

Complexity-decomposition track (item A2).

- `_classify_change_type` splits into `_change_score` (the positive / negative
  signal-weight sum) and `_change_needs_review` (the no-score-but-worth-a-look
  check); the classifier becomes a thin dispatch over the two.
- `render_summary_markdown` moves its section bodies to `_md_changed_domain_lines`,
  `_md_detailed_comparison`, `_md_attention_section`, and
  `_md_per_domain_snapshot`; the renderer becomes a thin orchestrator.
- Both functions drop their `# noqa: C901`. `validation_runner.py` now carries
  no marker; 14 remain across the package.

No behavior change: change classification and the rendered Markdown are
unchanged, verified by the validation-runner / compare / delta tests.

## [1.9.64] - 2026-06-01

### Decompose `load_network` under the C901 cap

Complexity-decomposition track, the validator/loader tail (item A1, patch 4,
the last of the tail). Every grandfathered `# noqa: C901` validator/loader is
now decomposed.

- `recon_tool/bayesian.py`: the per-node parsing in `load_network` moves to
  `_parse_network_node`, with `_parse_node_prior_cpt` (root prior vs non-root
  CPT validation) and `_parse_node_evidence` (the evidence-binding loop with
  the strictly-in-`(0, 1)` likelihood check) as focused helpers. `load_network`
  becomes the top-level schema check plus a thin node loop, and drops its
  `# noqa: C901`.

No behavior change: every ValueError message and validation rule is preserved,
verified by the bayesian suite and `test_contracts` (255 tests).

## [1.9.63] - 2026-06-01

### Decompose `_validate_and_build_signal` under the C901 cap

Complexity-decomposition track, the validator/loader tail (item A1, patch 3).

- `recon_tool/signals.py`: the long chain of optional-field parsing in
  `_validate_and_build_signal` moves to three focused helpers:
  `_parse_strict_str_list` (a malformed value rejects the signal, used for
  `contradicts` / `requires_signals`), `_parse_lenient_str_list` (defaults to
  empty on error, used for `expected_counterparts` / `positive_when_absent`),
  and `_parse_requires_block` (the `requires.any` / `min_matches` / metadata
  fallback logic). The function becomes a thin orchestrator and drops its
  `# noqa: C901`.

No behavior change: signal validation, warning messages, and reject-vs-default
semantics are unchanged, verified by the signal suite (255 tests).

## [1.9.62] - 2026-06-01

### Decompose `_validate_motif` under the C901 cap

Complexity-decomposition track, the validator/loader tail (item A1, patch 2).

- `recon_tool/motifs.py`: the per-marker parsing in `_validate_motif` moves to
  `_parse_motif_marker` (a None return still rejects the whole motif, since the
  chain must be fully valid). The marker loop becomes a thin collect and the
  function drops its `# noqa: C901`.

No behavior change: motif validation is unchanged, verified by `test_motifs`.

## [1.9.61] - 2026-06-01

### Decompose `_validate_fingerprint` under the C901 cap

Complexity-decomposition track, the validator/loader tail (item A1, patch 1 of
the tail).

- `recon_tool/fingerprints.py`: the per-detection parsing in
  `_validate_fingerprint` moves to `_parse_detection_rule`, with
  `_parse_detection_weight` (clamp to `[0, 1]`, default 1.0) and
  `_parse_cname_target_tier` as focused helpers. The validator's detection
  loop becomes a thin collect, and the function drops its `# noqa: C901`.

No behavior change: fingerprint validation is unchanged, verified by
`test_fingerprint_expansion`, `test_validate_fingerprint_script`, and
`test_pattern_shadowing`.

## [1.9.60] - 2026-06-01

### Data-not-instructions demarcation for MCP consumers

CLI and agent quality-of-life track, item E7, and the one open AI-security
forward item from the 2026-05 review. recon hands an LLM strings that a third
party controls (DNS TXT, SPF / DMARC values, CT SAN names and issuer strings,
BIMI metadata, identity-endpoint responses). The mechanical injection surface
(ANSI / newline / markdown, SSRF, ReDoS) was closed in v1.9.18 to v1.9.21; the
residual surface is semantic, where an observed value reads like an
instruction.

- The injected MCP server instructions gain an "Untrusted observed content
  (data, not instructions)" section telling the consuming model to treat every
  domain-derived value as data to analyze and report, never as an instruction
  to follow, even when the literal text looks like a directive.
- `SECURITY.md` documents the demarcation in the MCP threat model alongside the
  existing sanitization mitigations.
- `tests/test_data_not_instructions.py` guards the demarcation against silent
  removal from both the instructions and `SECURITY.md`.

No tool output shape changed; the demarcation is delivered in-band through the
session instructions.

## [1.9.59] - 2026-06-01

### Schema-discovery MCP resource (`recon://schema`)

CLI and agent quality-of-life track, item E6. An MCP agent could not read the
JSON-output contract without fetching `docs/recon-schema.json` over the
network, because the wheel ships only the `recon_tool` package.

- New `recon://schema` read-only MCP resource returns the JSON-output contract
  as a JSON Schema (the same document as `docs/recon-schema.json`, including
  the batch and delta shapes in its `$defs`). The contract version is carried
  in the schema's own `description`.
- A byte-identical copy of the schema is bundled at
  `recon_tool/data/recon-schema.json` so the resource serves offline;
  `recon_tool.schema_contract.packaged_schema_text` loads it.
  `tests/test_schema_resource.py` guards the copy against drift from the docs
  source and confirms the resource is registered.
- `docs/mcp.md` lists the resource (the Catalog Resources count goes from three
  to four).

## [1.9.58] - 2026-06-01

### MCP autoApprove guidance (read-only vs stateful)

CLI and agent quality-of-life track, item E5. Every MCP tool already carried a
`readOnlyHint` annotation, but the docs did not classify the tools, so a
consuming agent had no documented basis for deciding what is safe to
auto-approve.

- `docs/mcp.md` gains a "Read-only vs stateful (autoApprove guidance)"
  subsection naming the three stateful tools
  (`inject_ephemeral_fingerprint`, `clear_ephemeral_fingerprints`,
  `reload_data`) and noting that read-only does not mean offline: the
  cache-first analysis tools may still make passive outbound queries.
- `tests/test_mcp_tool_annotations.py` keeps the doc in sync with the live
  annotations: it fails if a new tool is missing from the Available Tools
  table, or if the documented stateful set drifts from the tools whose
  `readOnlyHint` is false.
- The README manual-approval note links to the guidance.

No runtime behavior change.

## [1.9.57] - 2026-06-01

### `batch` reads domains from stdin

CLI and agent quality-of-life track, item E3. `recon batch -` now reads the
domain list from stdin, the natural piping ergonomic
(`cat domains.txt | recon batch - --json`).

- A literal `-` for the file argument routes to stdin; any other value is
  still treated as a file path.
- The bounded line reader is extracted into `_read_batch_domains`, shared by
  the file and stdin paths, so both honor the same per-line, cumulative-size,
  and domain-count caps. Over-bound input raises a typed `_BatchInputError`
  that maps to the validation exit code.
- Help text and the README usage block document the stdin form. Covered by
  `tests/test_batch_stdin.py` (the reader's caps directly, plus the
  end-to-end stdin path).

## [1.9.56] - 2026-06-01

### `_SUBCOMMANDS` matches the registered command tree

CLI and agent quality-of-life track, item E2. The root callback uses
`_SUBCOMMANDS` to tell a bare domain argument apart from a subcommand, but the
set omitted the real `discover` command. It was harmless today (the set only
gates a dotted, non-flag first argument, and `discover` is rarely passed a
domain-like first token), but it was a latent mis-routing risk and an
inconsistency.

- `discover` added to `_SUBCOMMANDS`, so the set now equals the registered
  command tree (`lookup`, `batch`, `discover`, `doctor`, `delta`, `mcp`,
  `cache`, `fingerprints`, `signals`).
- `tests/test_subcommands.py` pins the set against the Typer app's registered
  commands and groups, so a future command that is not added here fails CI
  rather than silently mis-routing.

## [1.9.55] - 2026-06-01

### Exit-code reference and named constants

CLI and agent quality-of-life track, item E1. The exit-code contract existed
but was scattered and partly unnamed.

- **One reference block.** `docs/schema.md` gains an "Exit codes" section
  documenting the full `0` / `1` / `2` / `3` / `4` contract for scripters
  (success, general error, validation, no data, internal), including that no
  JSON is emitted on the `2` and `3` paths and how `recon fingerprints check`
  maps its own codes. `docs/security.md`, the README, and the `recon delta`
  note cross-link to it instead of restating partial lists.
- **Single source of truth.** A new `recon_tool/exit_codes.py` holds the five
  constants. `cli.py` imports and re-exports them (back-compat for callers
  that import `EXIT_*` from `recon_tool.cli`), and `server.py` and
  `fingerprint_validator.py` now share them too.
- **No more bare literals.** The remaining raw exit integers are named:
  `cli.py`'s `cache clear` validation exit and the two MCP-dependency-missing
  fallbacks, `server.py`'s cwd-shadow refusal (`2`) and unexpected-fault
  fallback (`1`), and `fingerprint_validator.py`'s `0` / `1` / `2` returns.

No behavior change: every exit code is the same integer as before, now named.
Covered by `tests/test_exit_codes.py`.

## [1.9.54] - 2026-06-01

### Core-module C901 cleanup (posture)

- **`recon_tool/posture.py`.** `_validate_and_build_rule` drops under the
  complexity cap by extracting `_parse_slug_condition` (the
  slugs_any / slugs_min / slugs_max sub-parse, with the same defaulting and
  skip-warnings as before). The function loses its `# noqa: C901` and
  `posture.py` is now fully under the cap.

No runtime behavior change: posture-rule validation is unchanged, verified by
`test_posture_validation` and `test_enhanced_yaml`.

## [1.9.53] - 2026-06-01

### Begin the core-module C901 cleanup (insights)

With `formatter.py` fully under the complexity cap, the decomposition moves into
the core modules.

- **`recon_tool/insights.py`.** `_email_security_insights` splits into
  `_has_scoreable_email` (the honesty gate that avoids scoring email on a domain
  with no MX-backed signal), `_email_score_parts` (the observed hardening
  controls, including gateway-inferred DKIM), and `_non_scoring_email_summary`
  (the monitoring-mode / soft-SPF fallback line). The function drops under the
  cap of 15 and loses its `# noqa: C901`. A vestigial `score` counter that was
  only assigned (`_ = score`) is removed; the branch already keys off
  `score_parts`.

No runtime behavior change: the email-security insight lines are unchanged,
verified by `test_insights_unit`, `test_hedging_invariants`, and
`test_explain_integration`.

## [1.9.52] - 2026-06-01

### Finish the formatter C901 sweep

The last two over-cap functions in `formatter.py` are decomposed, so the whole
file is now under the complexity cap of 15 with no remaining `# noqa: C901`.

- **`recon_tool/formatter.py`.** `_categorize_services` splits into its two
  classification passes (`_categorize_pass1_slugs`, `_categorize_pass2_names`,
  sharing `_is_service_artifact`) plus the three post-passes that tidy the
  result (`_dedup_identity_echoes`, `_consolidate_caa_issuers`,
  `_infer_bundled_ai`); the function becomes a thin pipeline over `by_cat`.
  `_compact_email_summary` splits into `_email_summary_providers` and
  `_email_summary_controls` over a shared `_append_unique` helper.

No runtime behavior change: the categorized Services block and the compact email
summary are held byte-identical by the panel golden snapshots, the provider-line
unit tests, and `test_formatter_coverage`.

## [1.9.51] - 2026-06-01

### Decompose _render_key_facts under the C901 cap

- **`recon_tool/formatter.py`.** The key-facts block builder (Provider, Tenant
  / Region, Auth, Cloud, Multi-cloud, Confidence) drops under the cap of 15. Its
  `_field` closure becomes the module-level `_append_field`, and the three
  branch-heavy lines move to pure builders: `_key_facts_provider_line`,
  `_key_facts_auth_line` (with a small `_with_idp` helper for the shared
  "label via IdP" pattern), and `_key_facts_multicloud_line`. `_render_key_facts`
  is now a flat sequence of field appends and loses its `# noqa: C901`.

No runtime behavior change: output held byte-identical by the panel golden
snapshots in `tests/test_golden_renders.py`.

## [1.9.50] - 2026-06-01

### Decompose detect_provider under the C901 cap

- **`recon_tool/formatter.py`.** `detect_provider` (the email-topology-aware
  provider line, C901 29) splits into three path helpers: `_provider_exchange_onprem`
  (Exchange on-prem / hybrid), `_provider_from_topology` (single promoted
  primary, gateway, and deduped secondaries, with `_topology_slug_secondaries`
  for the slug-confirmed list), and `_provider_slug_fallback` (the no-topology
  slug path). `detect_provider` is now a thin dispatcher, drops under the cap of
  15, and loses its `# noqa: C901`.

No runtime behavior change: the provider line is unchanged, verified against the
existing provider-line unit tests (`test_backward_compat`, `test_email_topology`,
`test_formatter_coverage`) and the panel golden snapshots.

## [1.9.49] - 2026-06-01

### Decompose format_tenant_markdown under the C901 cap

- **`recon_tool/formatter.py`.** The markdown report renderer's eight sections
  move to focused builders (`_md_header`, `_md_services_split`,
  `_md_gws_details`, `_md_insights`, `_md_cert_intel`, `_md_tenant_domains`,
  `_md_related_domains`, `_md_footer`), each returning its list of lines (empty
  when the section does not apply). `format_tenant_markdown` becomes a thin
  orchestrator that concatenates them in the original order, drops under the
  cap of 15, and loses its `# noqa: C901`.

No runtime behavior change: the output is held byte-identical by the
`markdown_dense`, `markdown_sparse`, and `markdown_rich` golden snapshots.

## [1.9.48] - 2026-06-01

### Extend the golden net for the markdown renderer

Before decomposing `format_tenant_markdown` (the next C901 target), pin the
render branches the existing markdown fixtures leave dark.

- **`tests/test_golden_renders.py`.** A `_markdown_rich_info` fixture (Synthetic Alpha,
  fictional) carries a Google Workspace service set, GWS auth type / identity
  provider / active modules / CSE, and a degraded source. The new
  `markdown_rich` snapshot pins the GWS services split, the GWS details block,
  and the degraded-sources footer note, none of which the dense or sparse
  fixtures reach.

No runtime behavior change.

## [1.9.47] - 2026-06-01

### render_tenant_panel decomposition part 3 (final): under the C901 cap

Completes the incremental decomposition of `render_tenant_panel`, the main
user-facing panel, which stood at C901 96 when the gate was enabled in v1.9.37.
With this patch the function drops under the cap of 15 and its grandfathered
`# noqa: C901` is removed.

- **`recon_tool/formatter.py`.** The remaining inline sections move to focused
  helpers, each under the cap: `_render_services` (with `_strip_email_noise`
  and `_append_subdomain_summary`), `_render_passive_dns_ceiling`,
  `_render_related_compact`, `_render_unclassified_surface`,
  `_render_full_tenant_domains`, `_render_full_related`, `_render_insights`
  (with the shared `_append_wrapped_lines`), `_render_certs`,
  `_render_degraded_note` (with `_degraded_note_parts`),
  `_render_verbose_detail`, and `_render_explain_conflicts`. `render_tenant_panel`
  is now a thin orchestrator that appends whatever each section returns, in the
  original order.

No runtime behavior change: every panel mode (default, full, verbose, explain,
sparse, hardened, and the surface-rich fixture) is held byte-identical by the
golden characterization tests in `tests/test_golden_renders.py`.

## [1.9.46] - 2026-06-01

### Fix a flaky merge property test

`merge_results` deliberately discards placeholder tenant display names
("Default Directory" / "Directory", what Microsoft shows when a tenant owner
never set a custom name) and falls through to better signals. The property
test `test_first_none_skipped` ("second source's display_name wins when the
first is None") generated its candidate name with a free text strategy that
could produce exactly those placeholders, then asserted the placeholder
survived. It passed almost always and failed only when the strategy happened to
draw a denylisted value (e.g. `direcTory`).

- **`recon_tool/merger.py`.** The `_PLACEHOLDER_DISPLAY_NAMES` frozenset moves
  from inside `merge_results` to module scope so it is a single source of truth
  that tests can import. No behavior change.
- **`tests/test_explanation_engine.py`.** The shared `_safe_text_st` strategy
  now excludes those placeholder names, so a "this value wins" property never
  generates a value the merger is designed to reject.

## [1.9.45] - 2026-06-01

### render_tenant_panel decomposition part 2: External surface section

Continues the incremental decomposition of `render_tenant_panel` (the main
user-facing panel, C901 96 at the v1.9.37 gate-enable point) under golden
characterization tests.

- **`recon_tool/formatter.py`.** The ~100-line External surface section (the
  full-mode per-subdomain attribution map) moves out to a new
  `_render_external_surface` helper, itself split into `_surface_partition`
  (group attributions into individually-listed rows and collapsed per-service
  groups), `_append_individual_rows`, and `_append_collapsed_rows`. Each new
  function is under the C901 cap of 15, so no `# noqa` is added.
  `render_tenant_panel`'s complexity drops from 74 to 59 (its `# noqa: C901`
  stays until the remaining sections are extracted).

No runtime behavior change: the output is held byte-identical by the v1.9.44
`panel_surface_full` golden snapshot.

## [1.9.44] - 2026-06-01

### Extend the golden-output safety net before more panel decomposition

`render_tenant_panel` is being decomposed incrementally (v1.9.39 onward) under
the protection of golden characterization tests. The existing
`fully_populated_tenant_info` fixture left several render branches dark: the
Services subdomain summary, the Unclassified surface block, and the full-mode
External surface section. Decomposing those without a snapshot would risk a
silent output change, so this patch pins them first.

- **`tests/test_golden_renders.py`.** A `_surface_rich_info` fixture (Synthetic Alpha,
  fictional) populates `surface_attributions` (a collapsed CDN group, layered
  application-plus-infrastructure rows, a standalone app) and
  `unclassified_cname_chains`. Two new snapshots, `panel_surface_default` and
  `panel_surface_full`, pin the previously-dark branches: the subdomain
  summary line, the unclassified-termini block, and the External surface
  rendering (individual rows, collapsed group with apex stripping, layered
  service labels, discovery hint).

No runtime behavior change. Branch coverage rises as the formatter paths that
only these branches reach are now exercised.

## [1.9.43] - 2026-06-01

### Relax the Python floor back to `>=3.11`

v1.9.29 raised the floor to `>=3.12`. Revisiting that decision, the only
3.12-only code in the tree was three PEP 695 `type` aliases in `cli.py`,
and no runtime dependency needs 3.12 (networkx sets the practical floor at
3.11). Since 3.11 still receives security fixes (through ~Oct 2027) and
recon is meant to be a broadly-consumed building block, supporting 3.11
costs little and widens reach. This reverses the v1.9.29 raise.

- **`pyproject.toml`.** `requires-python = ">=3.11"`, re-added the 3.11
  classifier, `ruff target-version = "py311"`, `pyright pythonVersion =
  "3.11"`.
- **`recon_tool/cli.py`.** The three `type X = ...` aliases are written as
  `X: TypeAlias = ...` (the only 3.12-only syntax). No behavior change;
  `datetime.UTC`, builtin `TimeoutError`, and `enum.StrEnum` are all 3.11.
- **`.github/workflows/ci.yml`.** 3.11 re-added to the test matrix
  (`3.11 / 3.12 / 3.13 / 3.14`). Dev toolchain stays pinned at 3.14.
- **`uv.lock`.** Regenerated for the `>=3.11` floor.

Verified on CPython 3.11.15: import, `recon --help`, and `recon doctor` all
run; the full suite passes with pyright at `pythonVersion=3.11`.

## [1.9.42] - 2026-06-01

### Restore the bare `recon <domain>` shorthand on fresh installs

`recon alpha.invalid` (the shorthand that routes a domain-like first argument
to the `lookup` command, without an explicit subcommand) stopped working on
fresh installs. The cause was a dependency change, not our routing logic:
Typer >=0.25 vendors its own copy of Click, so the `UsageError` raised during
command resolution is `typer._click`'s, not the top-level `click`'s. The
group's `except click.UsageError` catch-and-retry never saw the vendored
exception, so a bare domain fell through as "No such command".

- **`recon_tool/cli.py`.** `_DomainGroup.resolve_command` now routes a
  domain-like first argument (contains a dot, is not a known subcommand, does
  not start with `-`) to `lookup` before normal resolution, rather than
  catching a resolution error and retrying. The up-front form does not depend
  on which Click raised the error.
- **`tests/test_cli.py`.** A `test_bare_domain_routes_to_lookup` regression
  guard exercises the routing through `CliRunner` so a future Typer or Click
  change that breaks the shorthand fails CI.

## [1.9.41] - 2026-05-30

### IDN handling + aggregator fix from a $0 corpus validation (hardening phase, patch 4)

A zero-cost (`--no-ct`, passive only) end-to-end run of the engine against
a random 200-domain subset of the private corpus confirmed the whole
pipeline works on real input (199/200 processed, exit 0, healthy
confidence / provider / detection-density distributions; aggregate counts
only, no apex names committed). It also surfaced two fixable issues that
unit tests alone would not have:

- **IDN handling (`recon_tool/validator.py`).** `validate_domain` rejected
  raw-Unicode internationalized domains (an IDN apex was the only failure
  in the run). It now IDNA-encodes them to punycode
  (`café.invalid` to `xn--caf-dma.invalid`) using the stdlib codec before the
  format check, so an operator can paste an IDN directly. No new
  dependency; un-encodable labels still fall through to the clear
  "Invalid domain format" rejection. Tested with the failing case and
  scheme/www/uppercase variants.
- **Aggregator NDJSON parsing (`validation/corpus_aggregator.py`).** The
  aggregator did a single `json.loads`, which fails on the NDJSON that
  `scan.py` writes by default, so the aggregation step crashed. It now
  parses NDJSON line-by-line and skips input-validation error records.
  Covered by a new `TestCliInputParsing`.

The 55 detection gaps the run found feed the catalog-growth track; a
full-corpus, CT-enabled run remains the v2.0 calibration gate.

## [1.9.40] - 2026-05-30

### Decompose tenant_info_from_dict (hardening phase, patch 3)

Fully decomposes the cache deserializer `tenant_info_from_dict` (C901 35),
dropping it under the cap so its `# noqa: C901` is removed. The five
nested-loop block parsers are extracted into named helpers:
`_cert_summary_from_dict`, `_surface_attributions_from_dict`,
`_infrastructure_clusters_from_dict`, `_unclassified_chains_from_dict`,
and `_chain_motifs_from_dict`. The main function is now a flat sequence of
field reads and helper calls, and each parser is independently readable.

Behavior is unchanged, confirmed by the cache round-trip, forward-compat,
and cross-version-compatibility suites (131 tests). First grandfathered
C901 marker removed from the v1.9.37 backlog.

No source behavior changed.

## [1.9.39] - 2026-05-30

### Decompose render_tenant_panel, part 1: extract the key-facts block (hardening phase, patch 2)

First decomposition of `render_tenant_panel` (C901 ~96, the ~940-line main
panel). The key-facts block (Provider / Tenant / Region / Auth / Cloud
sovereignty / Multi-cloud rollup / Confidence, the densest branch cluster)
is extracted into a `_render_key_facts(info) -> Text` helper. The panel
shrinks to ~622 lines and the helper is independently readable and tested.

Behavior is unchanged, guaranteed by the golden-output tests from v1.9.38
(`tests/test_golden_renders.py`): the rendered panel is byte-identical
across dense / sparse / hardened / verbose / explain cases. `render_tenant_panel`
keeps its `# noqa: C901` until the remaining sections (services, surface,
insights, posture, verbose / explain blocks) are extracted in the next
patches and it drops under the cap; `_render_key_facts` carries its own
marker for now (the auth label logic is still branchy).

No source behavior changed.

## [1.9.38] - 2026-05-30

### Golden-output renderer tests + pre-2.0 hardening roadmap (hardening phase, patch 1)

Opens the pre-2.0 hardening phase. v2.0 is deliberately deferred behind
making the engine and catalog solid (more validation, more fingerprints,
the complexity decomposition, robustness work), not behind docs currency.

- `tests/test_golden_renders.py`: golden-output characterization tests
  that pin the exact rendered output of `render_tenant_panel` (C901 ~96,
  ~940 lines) and `format_tenant_markdown` (C901 ~25) across dense,
  sparse, hardened, verbose, and explain cases. The snapshots live under
  `tests/golden_renders/`; regenerate intentionally with
  `RECON_REGEN_GOLDEN=1`. These guarantee byte-identical output when those
  functions are decomposed in the next patches, so the user-facing panel
  cannot change silently. Every fixture uses explicit synthetic labels and
  reserved domains; no real company data.
- `docs/roadmap.md`: a "Pre-2.0 hardening phase" section laying out the
  four tracks (complexity decomposition, test and validation rigor,
  catalog growth, robustness and security) and the corpus-driven
  validation that runs alongside, with v2.0 gated behind the hardening.

No source behavior changed.

## [1.9.37] - 2026-05-30

### Enable the C901 complexity gate (engineering elevation, patch 10)

Turns on ruff's mccabe cyclomatic-complexity cap (`C901`,
`max-complexity = 15`) so new code must come in under 15. This is the
foundational step of the complexity work: it holds the line for new code
immediately, before the existing backlog is decomposed.

- `pyproject.toml`: `C901` added to the ruff `select`, with
  `[tool.ruff.lint.mccabe] max-complexity = 15` and a comment explaining
  the grandfathering.
- The 28 functions over the cap at enable time carry an explicit
  `# noqa: C901` (added mechanically with `ruff --add-noqa`). They are
  being decomposed in later batches; each refactor removes its marker,
  ratcheting the debt down. This is the honest brownfield order: hold the
  line for new code first, then work the backlog rather than attempt a
  single large, risky refactor across 14 files.
- The genuine monsters (`render_tenant_panel` at 96, `_lookup` at 77,
  `merge_results` at 64, `_batch` at 60) are the highest-value targets;
  `render_tenant_panel` (~940 lines, the main user-facing panel) needs a
  golden-output test before it is decomposed. The `PLR` refactor family
  (~107 hits) is deferred so the gate stays focused on cyclomatic
  complexity first.

No source behavior changed; the markers are comments.

## [1.9.36] - 2026-05-30

### Migrate dev dependencies to PEP 735 dependency-groups (engineering elevation, patch 9)

Packaging hygiene from the 2026-05 standards review. The dev toolchain
moves from `[project.optional-dependencies].dev` to a PEP 735
`[dependency-groups].dev` table, so it is no longer published as an
installable `recon-tool[dev]` extra (that was never a real use case).

- `pyproject.toml`: `[dependency-groups].dev`. uv treats `dev` as a
  default group, so `uv sync` installs it and `uv sync --no-dev` /
  `uv export --no-dev` still exclude it (verified). No `[tool.uv]` block
  is needed; the default-group behavior is built in.
- `ci.yml` and `release.yml`: the `uv sync --extra dev` calls became
  plain `uv sync`; the `--no-dev` build and audit-export steps are
  unchanged. The supply-chain isolation contract tests still pass (they
  forbid `--extra dev` in the build and id-token jobs, which now holds
  everywhere).
- `README.md`, `CONTRIBUTING.md`: the dev-setup line now shows `uv sync`
  with the pip equivalent for non-uv users
  (`pip install -e . --group dev`, pip 25.1+). The old
  `pip install -e ".[dev]"` no longer applies, since dependency-groups
  are not pip extras.

No runtime behavior changed; runtime dependencies are untouched.

## [1.9.35] - 2026-05-30

### Design-by-Contract second pass: engine matchers (engineering elevation, patch 8)

Extends the `deal` contracts from the inference core (v1.9.31) to the
fingerprint engine. Same wiring: contracts run under test and local dev,
disabled in production via `deal.disable()` under `-O`.

- `fingerprints.filter_shadowed_matches` gains a `@deal.post` asserting
  no shadowed pair survives: after filtering there is no pair of kept
  detections with different slugs where one pattern is a strict substring
  of the other. That pair is exactly the double-count the filter exists to
  remove, so its survival is a bug. This is the "no double-count after
  shadow filtering" invariant made executable.
- `specificity.evaluate_pattern` gains a `@deal.post` asserting the match
  count stays within `[0, corpus_size]` (a pattern cannot match more
  synthetic-corpus entries than exist).
- `tests/test_contracts.py` adds direct tests for both predicates
  (shadowed pair rejected, same-slug and non-overlapping kept; match count
  out of range rejected).

Both predicates are named, typed validators, consistent with the
inference-core contracts; the two decorator lines carry the same localized
`# pyright: ignore[reportUntypedFunctionDecorator]`. The roadmap's deal
item is updated: the second pass is now shipped.

No runtime output shape changed.

## [1.9.34] - 2026-05-30

### Convert ConfidenceLevel to StrEnum (engineering elevation, patch 7)

Completes the modernization deferred in the v1.9.29 floor raise.
`ConfidenceLevel` now inherits from `enum.StrEnum` (3.11+) instead of
`(str, Enum)`, which clears the `# noqa: UP042` it was carrying.

This was deferred because StrEnum changes `str()` / `__format__` to render
the value (`"high"`) rather than the qualified name (`ConfidenceLevel.HIGH`),
and a wrong move could have changed user-facing output. The audit before
this change found that every render site already goes through `.value`
(panel, markdown, JSON, delta, exposure, explanation), and nothing
interpolates the enum directly, so the conversion changes no output. JSON,
dict-key lookups, and comparisons are unaffected because StrEnum members
are still strings equal to their value. The full suite, which covers all
those renderers, confirms it.

No runtime output shape changed.

## [1.9.33] - 2026-05-30

### Test rigor: stateful rate-limiter machine + free-threaded 3.14t probe (engineering elevation, patch 6)

From the standards review's testing-rigor items. Additive; no source or
runtime behavior changed.

- **Hypothesis stateful testing.** `tests/test_rate_limit_stateful.py`
  drives the `AdaptiveRateLimiter` + circuit breaker with arbitrary
  sequences of success / rate-limited / other-failure outcomes (a
  `RuleBasedStateMachine`) and asserts invariants after every step: the
  interval stays within `[min, max]`, the consecutive-failure counter
  tracks a parallel model exactly and never goes negative, the breaker
  cooldown stays bounded, and an open breaker implies the failure
  threshold was crossed. The existing property tests exercise single
  operations; this reaches the sequence-level bugs they cannot.
- **Free-threaded 3.14t probe.** `ci.yml` gains an Ubuntu `3.14t`
  (PEP 703 free-threaded) matrix entry, marked experimental and
  `continue-on-error`, so it surfaces whether a runtime dependency lacks
  a cp314t wheel without failing CI. recon is asyncio-based with no shared
  mutable thread state, so this is a dependency-readiness probe rather
  than a correctness change.

Deterministic fault injection at the network boundary (timeouts,
malformed and truncated payloads, partial provider failures) is already
substantially covered by the existing resilience suites
(`test_ct_pipeline_resilience.py`, `test_properties_resilience.py`,
`test_fallback_chain.py`); deeper malformed-payload injection is noted as
a possible follow-up.

## [1.9.32] - 2026-05-30

### Build-provenance attestation + hash-pinned audit requirements (engineering elevation, patch 5)

Supply-chain hardening adopted from the 2026-05 standards review. CI and
release configuration only; no code or runtime behavior changed.

- **Build provenance.** A new `attest` job in `release.yml` signs a
  GitHub-native SLSA build-provenance attestation
  (`actions/attest-build-provenance`) for the wheel and sdist, linking
  them to the workflow run that produced them. Consumers can verify with
  `gh attestation verify <artifact> --repo blisspixel/recon`. The job is
  deliberately separate, like `publish-pypi` and `github-release`: it
  downloads the sealed artifacts and runs no project dependency code, so
  the `id-token` it is granted cannot be minted by a compromised
  dependency. This keeps the v1.9.3.3 supply-chain isolation contract
  intact.
- **Hash-pinned audit requirements.** The exported runtime requirements
  the dependency audit reads now carry per-package sha256 hashes (dropped
  `--no-hashes` from the `uv export` in both `ci.yml` and `release.yml`),
  so the audited surface is hash-pinned. pip-audit handles hashed
  requirements (verified locally). The SBOM export is left unhashed since
  its `--no-deps` CycloneDX generation does not benefit from hashes.

Full SLSA L3, Sigstore in-toto signing, and reproducible-build
verification stay deferred as disproportionate for a stdio tool at
current scale; the cheap, GitHub-native provenance step closes most of
the gap. The actual install path was already hash-verified via `uv.lock`.

## [1.9.31] - 2026-05-30

### Design-by-Contract on the inference core (engineering elevation, patch 4)

Adopts `deal` for Design-by-Contract, first pass: the inference math in
`recon_tool/bayesian.py`. Contracts make the invariants the code already
relies on executable, so a violation fails loudly under test instead of
silently producing a malformed posterior.

- New runtime dependency `deal` (pure-Python, so it does not breach the
  no-C-extension floor). It is disabled in production via
  `deal.disable()` when `__debug__` is false (wired in
  `recon_tool/__init__.py`), so installed users running under `python -O`
  pay no runtime cost; contracts run under test and local dev.
- Postconditions on four inference functions, written as named, typed
  validators (not inline lambdas, so they carry no unknown-type noise and
  are unit-tested on their own):
  - `_factor_for_node`: every factor entry is a probability in `[0, 1]`.
  - `_factor_for_evidence`: a returned evidence factor has only
    strictly-positive entries. This encodes the no-degenerate-factor
    invariant (the schema rejects `{0, 1}` likelihoods because a single
    zero would pin a node's posterior permanently).
  - `_query_marginal`: each returned marginal probability is in `[0, 1]`.
  - `_credible_interval`: the interval is ordered and within `[0, 1]`
    (`0 <= low <= high <= 1`).
- `tests/test_contracts.py`: proves the validator logic, that a contract
  actually raises `deal.PostContractError` on a violating result, and
  (via `python -O` subprocesses) that contracts are no-ops in production
  and active otherwise. A contract that never fires is no better than a
  comment; these tests show these fire.
- `deal`'s decorators are dynamically typed, so the four decorator lines
  carry a localized `# pyright: ignore[reportUntypedFunctionDecorator]`;
  the validators themselves are fully typed.

The dependency-floor invariant note in the roadmap is updated: `deal` is
the one deliberate pure-Python addition, accepted for the verifiability
gain. A second pass extending contracts to the engine matchers and
validators is tracked for a follow-up.

No runtime output shape changed.

## [1.9.30] - 2026-05-30

### Branch coverage + measured gate raise (engineering elevation, patch 3)

Until now coverage measured statement execution only, and the gate sat at
80% line coverage. This turns on branch coverage (`--cov-branch`) in the
CI matrix, the release test job, and the local gate
(`scripts/release.py`), and raises the floor to 82% on the stricter
branch metric.

The number is measured, not aspirational: branch coverage is 82.95%
today, so an 82% gate is a real raise (a stricter metric at a higher
number than the old 80% line gate) with enough headroom to absorb the
small cross-platform branch variance the matrix sees. The brief's flat
95% was declined: a blanket target tends to buy execution, not test
quality, and the honest figure for this codebase is near 83.

- `ci.yml`, `release.yml`: `pytest ... --cov-branch --cov-fail-under=82`.
- `scripts/release.py`: the local quality gate matches CI (branch
  coverage, 82%).
- `CONTRIBUTING.md`, `docs/release-process.md`: documented.

`server.py` (around 71% line) stays the named under-covered target for a
later test pass. No code or runtime behavior changed.

## [1.9.29] - 2026-05-30

### Raise the Python floor to 3.12 (engineering elevation, patch 2)

**Breaking for consumers on Python 3.10 or 3.11.** `requires-python` moves
from `>=3.10` to `>=3.12`. This is a deliberate floor raise adopted from
the 2026-05 standards review, not an accident: Python 3.10 reaches EOL on
2026-10-31 and 3.11 on 2027-10, so a 3.12 floor keeps recon on
upstream-supported runtimes through 2028 and lets the core use post-3.11
syntax and typing. Anyone still on 3.10 or 3.11 should pin `recon-tool`
to `<1.9.29` until they upgrade their interpreter.

Changed:
- `pyproject.toml`: `requires-python = ">=3.12"`; dropped the `3.10` and
  `3.11` classifiers; `ruff target-version = "py312"`; `pyright
  pythonVersion = "3.12"`.
- `.github/workflows/ci.yml`: the test matrix is now 3.12 / 3.13 / 3.14
  across Ubuntu, Windows, and macOS (the 3.10-specific excludes are gone
  with the versions they referenced).
- Added `.python-version` (3.14) so the local and CI dev toolchain is
  pinned to the static-analysis baseline without affecting the runtime
  floor.
- Docs that state the supported range (`README.md`,
  `docs/release-process.md`, `docs/stability.md`) updated to 3.12 - 3.14.

Modernization unlocked by the higher floor (ruff pyupgrade at `py312`,
behavior-preserving):
- `datetime.timezone.utc` to the `datetime.UTC` alias across the
  codebase and tests.
- `asyncio.TimeoutError` to the builtin `TimeoutError` (identical since
  3.11).
- The three CLI type aliases (`McpCheck`, `DoctorStatus`, `DoctorCheck`)
  to PEP 695 `type` statements.

Deferred on purpose: converting `ConfidenceLevel` to `enum.StrEnum`
(ruff UP042) is held back behind a documented `noqa`. StrEnum changes
`str()` / `__format__` output and several confidence members are
interpolated into user-facing text, so the conversion needs its own pass
with a golden-output test rather than riding in the floor raise.

No runtime output shape changed.

## [1.9.28] - 2026-05-30

### Packaging and platform currency (engineering elevation, patch 1 of a series)

First step of the engineering-elevation work folded into the roadmap's
Known gaps in v1.9.27. Two good-citizen items, both packaging-facing,
neither changing runtime behavior:

- **`py.typed` marker (PEP 561).** `pyproject.toml` has carried the
  `Typing :: Typed` classifier and CI has run pyright strict for a long
  time, but the package shipped no `py.typed` marker, so a downstream
  consumer's type checker did not actually pick up recon's inline types.
  Added `recon_tool/py.typed` (an empty marker, the correct form for a
  fully-typed package). Verified the marker lands in the built wheel
  (`recon_tool/py.typed` is present in `recon_tool-<version>-py3-none-any.whl`);
  hatchling includes it from the package directory with no extra config.
- **Python 3.14 support.** Added 3.14 to the CI test matrix (Ubuntu,
  Windows, macOS) and a `Programming Language :: Python :: 3.14`
  classifier. The `requires-python >=3.10` floor is unchanged: this adds
  a supported version, it does not drop any. recon imports and its
  targeted suites pass on CPython 3.14.5 locally (all runtime and dev
  dependencies resolve on 3.14), and the matrix exercises the full suite
  there. The 3.14-only baseline from the external standards brief was
  declined for the reason recorded in the roadmap: a broad support window
  is part of the product for a tool meant to be consumed by other tools.

No code paths changed. ruff + pyright clean; full suite green on the
matrix.

## [1.9.27] - 2026-05-29

### MCP-onboarding UX: client-side config check + troubleshooting docs

Acts on field feedback from a Windows 11 / Claude Code install attempt
where both server doctors passed but the tools still did not appear. The
gap was never the server. Nothing told the operator whether the client
had actually been handed the config, and the docs stopped before the
most common failure mode.

Added:
- `recon doctor --client=<name>` reads the config file a client actually
  loads (claude-code, claude-desktop, cursor, vscode, windsurf, kiro)
  and reports whether an `mcpServers.recon` stanza is present and
  well-formed, including a command-sanity check that flags the
  bare-`recon`-not-on-PATH case. For Claude Code it also checks the
  project-nested `projects[...].mcpServers.recon` shape that
  `claude mcp add` writes, and notes that a plugin install keeps its
  config inside the plugin rather than in `~/.claude.json`. Exits
  non-zero when no stanza is found so it can gate a setup script. New
  module `recon_tool/client_doctor.py`: pure-data, no network, reuses
  the install path resolver and the BOM-tolerant read.

Docs:
- `docs/mcp.md` gains a third verify-your-setup check for
  `recon doctor --client`, a "When doctor passes but the tools don't
  load" section (`/mcp`, the `mcp__recon__*` vs `mcp__claude_ai_*`
  naming, restart means a full application quit and relaunch), and a
  note on how approval semantics differ between the `recon mcp install`
  path (`autoApprove: []`, manual) and the plugin path (auto-approved).
- `agents/claude-code/README.md` gains a skill-vs-MCP "what each adds"
  section, the same troubleshooting pointer, the approval-path
  clarification, and a note that the wrapped `mcpServers` form is the
  correct plugin `.mcp.json` schema. The skill-vs-MCP framing is written
  as the accurate split: the one-shot analyses (exposure score,
  hardening gaps, posteriors) are reachable from the CLI via
  `--exposure` / `--gaps` / `--fusion`, so a skill can drive them; the
  MCP server's distinct value is the stateful and iterative workflows.
- Top-level `README.md` gains a one-line troubleshooting pointer and the
  same skill-vs-MCP one-liner.
- `agents/claude-code/skills/recon/SKILL.md` CLI-fallback section gains
  the `--exposure --json`, `--gaps --json`, `--fusion`, and
  `--explain-dag` flags, so the skill in CLI mode reaches the exposure
  score, hardening gaps, and Bayesian posteriors rather than stopping at
  the lookup, plus an explicit list of what stays MCP-only
  (`simulate_hardening` loops, the ephemeral-fingerprint reevaluate
  loop, live two-domain `compare_postures`, `test_hypothesis`).

Not changed:
- The plugin `.mcp.json` format. A field report suggested the wrapped
  `mcpServers` form was wrong for the plugin loader; the official Claude
  Code docs confirm the wrapped form is correct, so the file is left as
  is and the docs clarify the point instead.

Tests: `tests/test_doctor_client.py` covers stanza-present (top-level
and project-nested), missing, mcpServers-without-recon, malformed JSON,
BOM-tolerant read, the bare-`recon`-not-on-PATH warning, the
python-module command form, populated `autoApprove`, the cursor
workspace path, and the CLI exit codes.

### Bug-hunt fixes (same patch)

Adversarial review of the new surface turned up three defects, fixed
here:

- **VS Code config key.** VS Code's `.vscode/mcp.json` maps servers
  under a top-level `servers` key, not `mcpServers` (per the VS Code MCP
  configuration reference). `recon mcp install --client=vscode`
  previously wrote `mcpServers`, which VS Code does not read, so the
  install silently produced a config that never loaded. A new
  `servers_key(client)` helper now drives both `plan_install` and
  `install`: vscode gets `servers`, every other client keeps
  `mcpServers`. The `agents/vscode/mcp.json` scaffold and the
  `docs/mcp.md` config-location note are updated to match, and
  `recon doctor --client=vscode` reads `servers` first (falling back to
  a legacy `mcpServers` block so an older install is still found, with a
  note to move it).
- **Absolute-path command mis-warned.** `recon doctor --client` flagged
  an absolute `command` path ending in `recon` / `recon.exe` (the common
  installed form, since `recon mcp install` persists
  `shutil.which("recon")`) as "unrecognized" when the path did not
  resolve on the machine running the check, for example a config synced
  from another machine. The command-sanity check now recognizes the
  `recon` basename alongside the python / uvx launcher forms.
- **Duplicate stanza mislabelled.** When recon was registered in more
  than one of a client's config files (for example both `~/.claude.json`
  and a project `.mcp.json`), the second file was reported as having no
  recon entry. It is now labelled as a duplicate the first candidate
  already covers.
- **Cross-platform basename of a Windows command path.** The
  command-sanity check extracted the launcher basename with `Path(...)`,
  which on POSIX does not treat `\` as a separator, so a config synced
  from a Windows box (a backslash path like `C:\...\recon.exe`) was
  mis-warned as unrecognized when the check ran on Linux or macOS. The
  basename is now taken with `PureWindowsPath`, which accepts both `/`
  and `\` on any OS. Surfaced by the CI test matrix; the original local
  gate ran on Windows only and did not exercise the POSIX path.

## [1.9.26] - 2026-05-29

### Schema-contract polish (path-to-v2.0 item 1)

Closes item 1 of the "Outstanding before v2.0" list in
`docs/roadmap.md`. Documentation plus a schema-additive set of `$defs`
and a small pure-Python rule set. No runtime output shape changed; this
is a no-behavior-change patch.

The pre-lock schema audit found that `docs/recon-schema.json` described
only the single-domain `--json` output, while batch and NDJSON runs also
emit a `{domain, error}` error record (when a domain fails validation or
lookup) whose shape was declared nowhere. A re-read while grounding the
work also showed the `BatchResult` `$def` was inaccurate: the default
`recon batch --json` emits a bare array, not a `{domains: ...}` wrapper.
Only `--include-ecosystem` wraps, and even that falls back to the bare
array when no domain resolved.

`docs/recon-schema.json`:
- Top-level `description` rewritten to scope the root object to
  single-domain success output and to enumerate the other output modes,
  each pointing at its `$def`.
- New `$defs/BatchErrorRecord`: `{domain, error}`, both required,
  `additionalProperties: false`.
- New `$defs/BatchArray` (default `batch --json`) and
  `$defs/BatchNdjsonRecord` (`batch --ndjson`): each element / line is
  `oneOf {single-domain success object, BatchErrorRecord}`.
- `$defs/BatchResult` description corrected to the `--include-ecosystem`
  wrapper shape with the bare-array fallback noted; `domains` items now
  allow both shapes; `ecosystem_hyperedges` declared required in the
  wrapper.
- `evidence`, `explanation_dag`, and `unclassified_cname_chains`
  descriptions now state their conditional emission plainly so a
  consumer does not read them as always present.
- The batch-only cross-domain fields (`shared_verification_tokens`,
  `shared_tenant`, `shared_display_name`) are declared as optional
  properties with batch-only descriptions.

`recon_tool/schema_contract.py`:
- `BATCH_ERROR_RECORD_KEYS` and `classify_batch_record()`: the single
  deterministic rule set for batch / NDJSON records. Returns `success`
  (key set is a superset of the required single-domain fields), `error`
  (key set is exactly `{domain, error}`), or `unknown`. Pure-Python, so
  consumers validate batch output without a JSON Schema library.

`docs/schema.md`:
- New "Output modes" section with a per-mode shape table, the
  `BatchErrorRecord` shape, and the deterministic classification rule.
- New "Batch-only cross-domain fields" subsection.
- Verbose-modes section names the conditional fields and why they are
  absent from `required`.

### Testing

- `tests/test_batch_ndjson_schema.py` (new): validates a reserved synthetic
  batch NDJSON sample with the rule set, confirms
  every record classifies as success or error, and checks the schema
  file's batch `$defs` agree with the classifier.
- `tests/test_json_schema_file.py` (extended): asserts the four batch
  `$defs` are present.

Validation: `validation/v1.9.26-schema-contract.md`, including the
local command to run the rule set over a gitignored private-corpus
NDJSON run.

## [1.9.25] - 2026-05-28

### CT pipeline resilience (Phase A)

The v1.9.24 corpus run was 99.9% degraded on crt.sh because batch
concurrency burst past per-IP rate limits and CertSpotter's 429-as-
empty responses silently soft-failed without marking the source
degraded. This release rebuilds the CT enumeration path so corpus-
scale runs respect provider rate limits, surface degradation
honestly, and accrue coverage across multiple sessions via cache
and persistent limiter state.

`recon_tool/rate_limit.py` (new): `AdaptiveRateLimiter` with AIMD
pacing (additive decrease on success, multiplicative increase on
429), per-provider circuit breaker (3 consecutive failures opens
for a 60s cooldown that doubles each subsequent trip, capped at
10 minutes), and a bounded `max_wait_s` so saturation falls
through to cache instead of blocking the run. Honors
`Retry-After` headers as a hard floor on the next interval.
Persistent state under `~/.recon/rate-limit-state/`: a fresh
process inherits "crt.sh tripped 8 minutes ago" so the
burst-and-learn cycle does not restart every invocation. Stale
state (>24h) is ignored on load.

`recon_tool/sources/cert_providers.py`: process-wide
`_CT_GLOBAL_CONCURRENCY = 2` semaphore gates both providers, so
batch concurrency cannot multiply per-IP pressure. Each provider's
query is wrapped with `acquire`/`on_success`/`on_rate_limited`/
`on_other_failure` callbacks so the AIMD math sees every outcome.
CertSpotter rate-limited-with-zero-pages now raises
`httpx.HTTPError` rather than returning empty data, so the
orchestrator marks it degraded.

`recon_tool/sources/dns.py`: `_detect_cert_intel` consults the CT
cache **first**; a fresh entry short-circuits both live providers.
`ct_provider_used` carries the seeder's name plus `(cached)`.

`recon_tool/ct_cache.py`: `CT_CACHE_TTL` bumped from 7d to 30d.
Free-tier rate limits make full-corpus enumeration a multi-session
operation; 30 days keeps prior fetches usable across the build-up.

Per-record `ct_attempt_outcome` field on `TenantInfo`: `cache_hit`
/ `live_success` / `live_rate_limited` / `breaker_open` /
`live_other_failure` / `cache_miss` / `skipped`. Distinguishes "no
certs in CT" from "rate-limited" from "breaker open" in the JSON
output. Was previously silent.

`validation/scan.py`: writes `ct_budget_summary.json` at end of
each `--ct` run with outcome counts and persisted limiter
snapshots. New `--ct-retry-from <prior-run>` flag reads a prior
results.ndjson, filters to records with degraded outcomes, and
re-resolves only those domains. Multi-session corpus enumeration
becomes a first-class operator workflow.

### Catalog gap-fill from Phase F corpus output

The 2026-05-28 Phase F corpus run surfaced cname_target endpoints
the v1.9.24 batch had marked EXTEND but where the actual catalog
patterns differed from the corpus form. Twenty entries close the
gap:

Six EXTENDs to existing slugs that had close-but-not-matching
patterns: `wpengine` adds `wpengine.com` (alongside the existing
`wpenginepowered.com` / `wpeproxy.com`); `freshdesk` adds the
cname_target form `freshdesk.com` (previously only SPF);
`swoogo` adds `swoogo.com` (alongside `swoogo.net`); `gigya`
adds `gigya-api.com` (alongside `gigya.com`); `optimizely`
adds the cname_target form (the existing `cname` rule fires
only on apex CNAMEs, not chain hops); `mailjet` adds the
cname_target form (previously only SPF).

Fourteen new vendors: Opendatasoft, Read the Docs, Foleon,
Stoplight, Aptible, Platform.sh, K15t Scroll Viewport, WHECloud,
Inxmail, Bevy, Brilliant Made, Music Today, OpenGov OpenData,
Cvent (event microsites distinct from the existing
`certain-cvent` and `stova-aventri` Cvent-family slugs).

Catalog: 788 -> 808 entries, 617 -> 631 unique slugs.

### Chain motif library expansion

Four new multi-hop motifs surfaced by the Phase B mining
(`validation/phase-b-motif-mine.md`):

- `zpa_to_aws`: Zscaler ZPA edge fronting AWS origin (3 corpus apex).
- `zpa_gov_chain`: 3-hop ZPA Gov tier to AWS (3 apex).
- `msecnd_to_zeta`: legacy Azure CDN fronting Zeta Global CDN (3 apex).
- `episerver_to_optimizely`: legacy Episerver host fronting Optimizely
  DXP edge across the rebrand boundary (3 apex).

Motif library: 18 -> 22.

### Engine: cname matcher regex bug fix preserved

The v1.9.24 cname-matcher regex fix (substring -> `re.search`)
remains in place; the 9 previously-dormant catalog patterns
(langsmith, fastly, flyio, railway, splunk, cyberark,
beyond-identity, workspace-one) continue to fire. New regression
tests pin the behavior.

### Testing

- `tests/test_ct_pipeline_resilience.py` (new): 19 tests covering
  semaphore cap+singleton, 429-raises, partial-page survival,
  AdaptiveRateLimiter (AIMD math, breaker semantics, success
  decrease, persistence round-trip + stale-state-ignored +
  persist=False opt-out), Retry-After parsing, cache-first
  short-circuit.
- `tests/test_rate_limit_properties.py` (new): 6 Hypothesis-based
  property tests verifying interval bounds, breaker-state /
  failure-count correspondence, success-resets, Retry-After floor,
  snapshot JSON-serializability, fail-fast on saturation.
- `tests/test_cname_regex_patterns.py` (new): 14 tests pinning each
  of the 9 regex-shaped cname patterns to real hostnames they
  match (anchored to vendor docs).
- `tests/test_pattern_shadowing.py` (extended): same 7 tests plus
  the v1.9.25 shadow-safety check confirms the 20 new entries do
  not introduce cross-slug substring shadows.
- `tests/test_fallback_chain.py`: 6 pre-existing tests updated for
  cache-first semantics; one bypass fixture for tests that
  exercise the live-fallback chain.
- `tests/conftest.py`: new `_isolated_rate_limit_state` autouse
  fixture isolates each test from persisted limiter state.

### Known limitations the design now surfaces honestly

Free-tier CT enumeration on a fresh IP cannot complete a
5000-domain corpus in a single session: CertSpotter's free-tier
subdomain quota is 10/day, crt.sh's per-IP limit is 5/min and
tightens further under load. The Phase F corpus run with the new
pipeline ended with both breakers open, 10,246 local declines
saved the run from blocking, and 57 records (1.1%) populated
cert_summary, of which 54 came from cache. This is the published-
limit reality; the design surfaces it via degraded_sources,
ct_attempt_outcome, and the ct_budget_summary.json artifact so
operators can plan multi-session enumeration via the
`--ct-retry-from` workflow.

## [1.9.24] - 2026-05-27

A second full pass over the 5241-domain private corpus, combined with
engine work surfaced by the QA pass on the resulting catalog. The
catalog grows from **572 to 788 entries (+216)** covering 156 new
vendors and 60 new detection variants for existing vendors. Three
engine improvements ride along: shadow-handling consistency across
substring matchers, a pre-existing cname-matcher regex bug fix that
re-enables 9 silently broken catalog entries, and two audit residuals
deferred from rounds 4 and 5 (priors clamp tightened, per-file
catalog cap added).

Source: deepmine and unclassified-CNAME-chain mining over the
2026-05-26 full-corpus run. At release, the per-candidate triage record included
detailed accepted and rejected rows. The current tracked copy at
`validation/v1.9.24-candidates-triage.md` retains provider-controlled ADD and
EXTEND patterns while reducing rejected target-like rows to aggregate counts
and reasons. Historical copies are covered by the
[data-handling policy's published-artifact exception](docs/data-handling-policy.md#historical-published-artifact-exception).

Added (156 new vendor entries):

- **79 TXT verifications** (`verifications.yaml`): Yahoo SMB,
  HashiCorp Cloud Platform, Astro, Remote.com, Parsec, Zywave, Infor
  CloudSuite, Proofpoint Wombat, Parkable, BetterComp, Gradle
  Enterprise, DeepL, Heyhack, Make.com, WeWork, Airalo,
  ProjectDiscovery, Dailymotion, Bill One, Formstack, AbuseIPDB,
  SolarWinds Service Desk, Stytch, HeyGen, SafeBreach, Brave, ProdPad,
  Gather, Kiro, Nearmap, Krisp, ActiveProspect, Reftab, Coda, Nulab,
  Fireflies, Virtru, Botify, Northpass, WalletConnect, Barco,
  Coursera, Samsung, Favro, ContractWorks, IdenTrust, DoorDash, Jumio,
  Toast, Feishu (Lark), Ethiack, Happeo, Spacelift, Everlytic,
  SafetyCulture, Microsec, D4Sign, Razorpay, Specops, Gitpod,
  Securiti, Trustpilot, QQ Mail, NordPass, Gem, Arcules, Druide,
  eSputnik, Freepik, Lemlist, Apperio, Read AI, MessageBird (Bird),
  Vitally, Lucidchart, PandaDoc, InVision, Fortinet, Adobe AEM.
- **16 SPF includes** (`discovered-signals.yaml`): Oracle Email
  Delivery, PowerSPF, Sailthru, Amadeus, Elastic Email, Sage Intacct,
  Constant Contact, spf-report, Everbridge, Tipalti, MessageProvider,
  MailChannels, Braintree, Stibee, Ipreo, SMTP.com.
- **7 MX providers**: Mxrecord, Fastmail (`messagingengine.com`),
  Hornetsecurity, AppRiver (Zix), TitanHQ, Apple iCloud Mail,
  Iberlayer Mailguard.
- **13 DMARC rua aggregators**: Cloudflare Email Analytics, CISA
  DMARC (`dhs.gov`), Skout (`sdmarc.net`), cp-dmarc, EmailAnalyst,
  Red Sift, Report URI, DMARC360, MailHardener, DMARC25 (Japan),
  InboxMonster, DMARCInput, GlockApps.
- **12 NS providers**: AT&T DNS, DNSimple (multi-TLD), F5 Cloud DNS,
  NameBright DNS, Etisalat Domains, NetNames, Constellix, Imperva
  SecureDNS, EasyDNS Backup, Com Laude (multi-TLD), Level3 / Lumen,
  DNSPod (Tencent).
- **29 cname_target rules** (`surface.yaml`): Piano (Tinypass),
  Validity Everest, Edgecast, Adestra MessageFocus, Gorgias, Shopee,
  Cleverbridge, Blackbaud Convio, Ovative, ThreatMetrix, BigCommerce,
  Rio SEO, SAP Cloud Kyma, Archbee, Storm Reply, Cloudways,
  BrightSites, Cirrus Identity, Pressable, Sanity SVD CDN, INAP,
  BusinessWire, Gannett Digital, Sourcepoint CMP, Dub, Hund, Emarsys,
  Redocly, Zoomin Software.

Extended (61 new detection variants):

- TXT: Atlassian (sending-domain), Google Workspace (gws-recovery +
  work-accounts), Smartsheet Gov, Pexip portal, Alibaba Cloud
  (aliyun), Oracle OCI, Brevo (sendinblue), Cisco Secure Email,
  Intercom, Heroku, GitHub, Zendesk, Loom (variant), Mailgun
  (mgverify).
- SPF: Mimecast (mim.ec), Oracle Cloud, SAP SuccessFactors
  (.com + sapsf.eu), Emma, Q4 Inc, Oracle Eloqua, Freshservice,
  Brevo, AutoSPF, Zoho (zoho.com + zcsend.net), Qualtrics, GoDaddy,
  Microsoft 365 GCC.
- MX: Google Workspace (smtp.google.com), AWS SES inbound, Microsoft
  365 (mx.microsoft + msv1.invalid + eo.outlook.com), Trellix Gov,
  Fortinet FortiMail Cloud, Cisco IronPort, Trend Micro, Alibaba
  Cloud, ProtonMail, CSC.
- DMARC rua: Cisco Secure Email, Barracuda, Valimail Gov
  (`valigov.email` merged into the canonical valimail entry to
  preserve the SPF-flattener invariant), Brevo, Trend Micro EU,
  Mailgun, GoDaddy, Alibaba Cloud.
- NS: Google Workspace (Google Domains handoff), Oracle Cloud,
  MarkMonitor (.zone), GoDaddy DefensiveDNS.
- cname_target: Netlify, Microsoft 365 (hybrid outlook.com), Heroku
  (herokuspace), Alibaba Cloud (alibabadns + alibaba.com), AWS SES
  (awsapps), Zoho (zohohost), Cloudflare China (pacloudflare),
  Salesforce Desk, Cvent Lanyon (lwcal), MuleSoft CloudHub,
  StackPath / MaxCDN (netdna-cdn), Stova / Aventri (etouches), Adobe
  AEM Cloud (adobecqms).

All new slugs are mapped explicitly in
`recon_tool.formatter._CATEGORY_BY_SLUG` or added to the
`EXPECTED_BUSINESS_APPS_FALLBACK` set in
`tests/test_slug_category_invariant.py`. Cloud-categorized slugs
either roll up via `_CLOUD_VENDOR_BY_SLUG` or are excluded from the
multi-cloud rollup via `_CLOUD_VENDOR_ROLLUP_EXCLUSIONS` (DNS
operators, single-purpose SaaS hosting, specialty CDN). The current tracked
candidate decision record at `validation/v1.9.24-candidates-triage.md` is
aggregate-only for rejected target-like rows; the release-time detailed record
remains in historical copies covered by the
[published-artifact exception](docs/data-handling-policy.md#historical-published-artifact-exception).

### v1.9.24 shadow-handling consistency

A QA pass on the v1.9.24 catalog found three substring shadows
introduced by the batch (cisco.com MX, ondemand.com cname_target,
desk.com cname_target). These are catalog patterns broad enough that
a more specific pattern under a *different* slug would also fire on
the same record, double-counting the underlying vendor.

The catalog fixes (cisco.com removed, ondemand.com narrowed to
k8s-hana.ondemand.com, desk.com narrowed to .desk.com) closed those
three shadows. The underlying engine inconsistency (substring
matchers handled shadow suppression differently across signal types)
was also closed:

- `cname_target` already sorted patterns longest-first in
  `_classify_chain` and did not propagate the slug into ctx.slugs
  (lands in `SurfaceAttribution` instead). Already shadow-safe.
- `mx`, `ns`, `caa`, `dmarc_rua`: now sort patterns longest-first
  before iterating with `break`-on-first-match, so the most specific
  pattern always wins (matches cname_target semantics).
- `spf`: accumulates matches (multiple distinct vendors per record is
  legitimate, e.g. M365 + Salesforce includes), but a new helper
  `recon_tool.fingerprints.filter_shadowed_matches` drops broader
  matches whose pattern is a strict substring of another firing match
  under a *different* slug. Same-slug substring pairs (e.g.
  valimail.com + vali.email both under slug=valimail) survive, since
  the slug accumulates once in ctx.slugs anyway.

`tests/test_pattern_shadowing.py` asserts the catalog has no
unapproved cross-slug substring shadow at build time, with an
explicit allow-list for the cname_target shadows the engine
demonstrably suppresses (aws-region-endpoint vs aws-api-gateway /
aws-nlb, oracle-cloud vs oracle-fusion). Two adjacent invariants
ride alongside the same file: every detection must carry a
description (operator-trace gate) and EXTEND-style YAML entries
sharing slug + name must not repeat the same `(type, pattern)`. The
fingerprint-discovery loop and future catalog additions now have a
CI gate that catches the double-count failure mode before release.

### v1.9.24 cname matcher regex bug fix

The cname loader has always validated `pattern` fields as regex (the
ReDoS-shape audit runs `re.compile` at load time), but the matcher
in `_detect_cname_infra` used substring search (`det.pattern in cl`).
The mismatch silently disabled nine catalog entries whose patterns
carried real regex syntax (escaped dots, `$` anchors, alternation):
`langsmith`, `fastly`, `flyio`, `railway`, `splunk`, `cyberark`,
`beyond-identity`, `workspace-one` (×2). Those entries never fired
on any apex with the original matcher.

The matcher now uses `re.search(..., re.IGNORECASE)` consistent with
the loader's validation contract. The 88 plain-string patterns
behave identically (regex without metacharacters is equivalent to
substring search), and the 9 regex patterns finally fire on the
hosts they were written to match.

### v1.9.24 audit residual hardenings (rounds 4 + 5 follow-ups)

Two items deferred during the round-4 and round-5 reviews:

- `recon_tool/bayesian.py` `load_priors_override`: clamp tightened
  from the inclusive interval `[0, 1]` to the open interval
  `(0, 1)`. A root prior pinned at `0` or `1` is a degeneracy
  operators rarely intend (one mis-belief permanently pins the
  node), matching the documented likelihood `{0, 1}` ban so the
  degeneracy policy is now uniform across priors and likelihoods.
  Operators wanting near-certainty can still use a near-bound
  value like `0.999`.
- `recon_tool/fingerprints.py` `_load_from_path`: caps each
  user-supplied catalog file at a generous per-file ceiling
  (`_MAX_CATALOG_ENTRIES_PER_FILE = 2000`) so an oversized
  `~/.recon/fingerprints.yaml` cannot inflate per-lookup matching
  cost or hold unbounded memory in the long-lived MCP server. The
  bundled catalog ships well under this; the cap is purely a
  defense for third-party / user-config files.

A small Bandit-skip cleanup rides along: the `B405` skip in
`pyproject.toml` covered an `xml.etree.ElementTree` import in
`recon_tool/sources/userrealm.py` that was already replaced with
`defusedxml.ElementTree` (the `ET.ParseError` reference now uses
`DefusedET.ParseError`). The stdlib import is removed, and the
`B405` entry comes out of the skip list with it.

## [1.9.23] - 2026-05-26

### Added

The comprehensive corpus-discovery batch. A multi-signal mine over the
full ~5000-domain private corpus surfaced unfingerprinted patterns
across every detection type recon uses, and this release lands all the
clearly-attributable ones. The catalog grows from 459 to **572 entries**
(+113), spanning five detection types.

- **56 TXT verification fingerprints** (`verifications.yaml`). The first
  batch covered hand-curated new vendors (Docker, HackerOne, TeamViewer,
  Zapier, Palo Alto Networks, GoTo / LogMeIn, SAP SuccessFactors, Pexip,
  JetBrains, Uber for Business, Parallels, Detectify, Foxit, Bugcrowd,
  SpyCloud, BrowserStack, Calendly, Sitecore, Bitrise, HPE GreenLake,
  MindManager, Bluebeam, Validity, Reachdesk, reMarkable, Extensis,
  Lovable, LinkedIn, Pinterest, TikTok, Lucid, Have I Been Pwned, Amazon
  Business, Schneider EcoStruxure, TollBit). A second generator pass
  added Atlassian Statuspage, Mixpanel, Pendo, Shopify, monday.com,
  Zoom, LaunchDarkly, New Relic, GitKraken, ConfigCat, Confluent,
  Keybase, DataDome, Sinch, Site24x7, Censys, Appspace, Nitro, Windsurf,
  Insomnia, Sitecore (TXT + CNAME).
- **17 SPF include fingerprints** (`discovered-signals.yaml`):
  Proofpoint, Salesforce Pardot, Atlassian Statuspage, Mailjet,
  Salesforce Marketing Cloud, Greenhouse, Docebo, Help Scout, Atlassian,
  Postmark, SAP SuccessFactors, Shopify, Exclaimer (two patterns),
  Oracle NetSuite, MailerLite, Campaign Monitor.
- **9 MX provider fingerprints**: Google Workspace (`googlemail.com`),
  Trend Micro, Mimecast (regional), GoDaddy, Mailprotector, Mailgun,
  Proofpoint Essentials, Microsoft 365 US Gov, SecureMX.
- **8 DMARC `rua=` vendor fingerprints**: DMARC Analyzer (Mimecast),
  Postmark, MxToolbox DMARC, DMARC Digests, Netcraft, DMARCLY, Validity
  (`everest.email` and `250ok.net`). Plus new `vali.email`,
  `easydmarc.us`, `easydmarc.eu` patterns added to the existing Valimail
  and EasyDMARC entries so the SPF-flattener invariant holds.
- **12 NS provider fingerprints**: CSC (`cscdns.net`, `cscdns.uk`), DNS
  Made Easy, Foundation DNS (.com / .net / .org), Network Solutions
  (`worldnic.com`), Afternic, MarkMonitor, easyDNS, Gandi. All added to
  the cloud-rollup exclusions (DNS providers, not multi-cloud hosting).
- **8 new `cname_target` rules**: Freshservice, Avature, Help Scout,
  Oracle Service Cloud, TIBCO Mashery, Crownpeak, Infobip, Ad Legend.
  Plus the legacy / alternate domains `bomgarcloud.com` (BeyondTrust)
  and `bynder.com`, added to the slugs introduced in v1.9.22.

All 572 fingerprint entries pass the validator (regex safety and
specificity) and the metadata-coverage gate; new slugs are mapped in
`_CATEGORY_BY_SLUG` or the Business Apps fallback; NS-provider slugs
are added to the cloud-rollup exclusion set so the panel summary stays
focused on actual hosting clouds.

The discovery loop ran across all the detection types recon uses (TXT,
SPF, MX, NS, DMARC `rua=`) and applied each type's matcher to confirm
absence before adding. The long tail (single-domain occurrences and
ambiguous identities) is left for future batches; this release lands
every clearly-attributable, multi-domain signal.

## [1.9.22] - 2026-05-23

### Added

Twenty new `cname_target` fingerprints, harvested from a discovery run
over the private validation corpus (`recon batch --include-unclassified`)
and confirmed absent from the catalog before adding:

- Collaboration / docs: Discourse (`hosted-by-discourse.com`),
  Document360, StatusPal, Tally.
- Security / identity: BeyondTrust, Arctic Wolf, Rootly, Material
  Security, Janrain (Akamai Identity Cloud).
- Marketing / DAM / PR: Substack, Oktopost, Bynder, Brandfolder, Act-On,
  Cision MediaRoom, Impact.com, PartnerPage, Mynewsdesk.
- Infrastructure: Cloudsmith.
- Email: Microsoft 365 US Government cloud (`usgovcloud.microsoft`, GCC
  High / DoD), a previously-uncovered government-cloud M365 signal.

Each carries a description and reference in the surface.yaml style; slugs
are mapped in `_CATEGORY_BY_SLUG` (specific categories) or the Business
Apps fallback. All 233 surface entries pass the fingerprint validator
(regex safety and specificity) and the metadata-coverage gate.

### Validation

Ran the corpus discovery and Bayesian fusion loop on stratified samples
(30 modern-stack domains, then 136 across all 34 categories). The
Bayesian layer held up: 402 of 402 high-confidence posteriors agreed
with the deterministic pipeline (100%), with zero cross-source conflicts
across the 136 diverse domains. One item is recorded for the v2.0
calibration pass: `email_security_modern_provider` never produces a
non-sparse estimate (it fires high for nearly everyone), so its evidence
bindings are worth revisiting.

## [1.9.21] - 2026-05-22

### Security

Round-five audit pass (HTTP response parsing, async / concurrency /
resource lifecycle, and a correctness bug-hunt + v1.9.20 regression
re-audit). The async and bug-hunt reviews found no reachable bug, and the
response-parsing review confirmed every attacker-influenced parser is
type-guarded, isolated, and body-capped. This release lands the
observability and defense-in-depth items the pass surfaced; it does not
fix a new vulnerability.

- **Detector failures are now observable.** The v1.9.20 gather isolation
  swallowed a failing detector at debug level, so a regression that broke
  a detector for every input could silently drop its intelligence. Failed
  detectors are now recorded in `degraded_sources` (surfaced in JSON and
  `--explain`) and logged at warning level. The detector list also
  carries stable names rather than relying on coroutine introspection.
- **Defense-in-depth output hygiene.** The verbose source-detail table
  now control-strips `region` and `error` (parity with the primary
  panel); the Autodiscover federated-domain list is control-stripped and
  count-capped; and the CertSpotter `issuer` name is type-checked before
  use, matching the `isinstance` discipline the rest of CT ingestion
  follows.

Rationale and the pass's deferred items (the `_RetryTransport` unused
base pool, synchronous YAML parse on the loop during `reload_data`, and
the over-1024-byte batch-line split) are in
`docs/security-audit-resolutions.md`.

### Tests

- `tests/test_sources/test_dns.py` extends the gather-isolation
  regression to assert a failed detector surfaces in `degraded_sources`.

## [1.9.20] - 2026-05-22

### Security

Round-four audit pass (data-file / config loading, analysis modules,
detector exception-safety, and a regression re-audit of v1.9.19), plus
the dependency advisory that blocked the v1.9.19 publish.

- **Detector exception isolation (generalizes the BIMI-port fix).**
  `_detect_services` and the surface-classification pass gathered
  detectors with no isolation, so any single detector raising on crafted
  input propagated through `asyncio.gather` to `DNSSource.lookup`, which
  turned it into a whole-source error and discarded every other
  detector's DNS intelligence. The v1.9.19 BIMI fix patched one detector;
  this isolates every detector at the gather boundary (and the surface
  `_process` gather) so one failure degrades gracefully. (HIGH)
- **starlette 1.0.0 to 1.0.1** (PYSEC-2026-161), a transitive dependency
  via mcp. This advisory was published after v1.9.19's CI passed but
  before its release pipeline ran, so the release audit failed and
  v1.9.19 never reached PyPI. The lockfile upgrade clears it; v1.9.20 is
  the published successor and is cumulative over v1.9.19.
- **Uncapped TXT length into a user regex.** `_detect_subdomain_txt` ran
  an operator / ephemeral regex against an attacker-controlled TXT value
  with no length bound, the only DNS path that lacked one. A crafted
  multi-KB TXT plus a greedy regex amplified backtracking. Now capped at
  4096, matching `match_txt`. (MED)
- **Quadratic clustering blowup.** `compute_shared_tokens` built a
  k*(k-1) peer cross-product per shared token; the CLI batch path allows
  up to 10k domains, so one common token could materialize ~100M
  objects. Tokens shared by more than 200 domains (noise / abuse) are now
  skipped. (MED)
- **ReDoS heuristic gaps.** `_REDOS_RE` missed bounded-repetition
  blowups like `(a+){20}`, and its comment falsely claimed it caught
  `(a|a)+`. Extended to flag the `{n}` form; the comment is now honest
  that overlapping-alternation and nested-group ReDoS are bounded by the
  input length caps above (not by the heuristic), since distinguishing
  safe `(foo|bar)+` from dangerous `(a|a)+` needs analysis a regex cannot
  do. (MED)
- **Markdown / token sanitization completed.** `auth_type`, `region`,
  `google_auth_type`, `google_idp_name`, and insights are now
  markdown-escaped in the markdown report (the v1.9.19 escape covered
  only `display_name` and issuer names); `google-site-verification`
  tokens are control-stripped at extraction. (LOW-MED)

Audit items left unchanged, with rationale in
`docs/security-audit-resolutions.md`: the priors-override `0.0`/`1.0`
root prior (likely an intended operator capability, distinct from the
likelihood `{0,1}` ban); catalog-size caps on the file loaders; the
`_RetryTransport` unused base pool; the over-1024-byte batch-line split;
and the PyYAML alias-bomb (all operator-trust-boundary or cosmetic).

### Tests

- Per-module regressions in the file each one exercises: detector gather
  isolation (`test_sources/test_dns.py`), the `compute_shared_tokens`
  cap (`test_clustering.py`), `{n}` ReDoS rejection (`test_security.py`),
  and markdown `auth_type` / `region` escaping (`test_formatter.py`).

## [1.9.19] - 2026-05-21

### Security

Round-three audit pass (four parallel reviews: MCP server, CLI / batch,
output-format injection, DoS / resource). Findings and fixes:

- **HTTP response-body size cap.** The shared client buffered whole
  response bodies (`resp.json()` / `resp.text`), so an attacker-influenced
  endpoint (`cse.<domain>`, `mta-sts.<domain>`, the BIMI `a=` URL, an
  autodiscover redirect) or a decompression bomb could grow memory
  without bound. Responses are now aborted past a 10 MB cap during the
  read (`_MaxBytesStream`), inherited by every call site.
- **Fixed a v1.9.18 regression: a malformed BIMI port aborted the DNS
  source.** The SSRF validation added in v1.9.18 read
  `urlparse(a_url).port`, which raises `ValueError` on a malformed or
  out-of-range port (`:bad`, `:99999`), and that access sat before the
  helper's `try`/`except`. A crafted BIMI `a=` URL therefore made
  `_parse_bimi_vmc` raise, which propagated through `_detect_services`
  and turned the whole DNS source into an error, dropping otherwise
  valid SPF / DMARC / MX / CNAME intelligence for that domain. The port
  is now read inside a guard that refuses the URL cleanly, and the
  `_parse_bimi_vmc` call in `_detect_email_security` is wrapped so this
  best-effort enrichment can never abort the source.
- **Completed the attacker-free-text sanitization class.** Round 2
  scrubbed CT SANs / issuers and the BIMI subject; round 3 found the
  fields it missed, all of which reach the terminal (rich does not strip
  ESC) or markdown / MCP output:
  - `display_name` (GetUserRealm `FederationBrandName`), `auth_type`, and
    `region` are control-char stripped in `merger.py` before they enter
    `TenantInfo` (this one fires on a normal lookup).
  - `dominant_issuer` (the cert issuer feeding `infra_graph` clusters) is
    stripped at the graph layer, closing the issuer path the round-2
    `build_cert_summary` strip missed; `infra_graph._clean_sans` also
    drops non-DNS SAN names so the graph layer is self-protecting.
  - cache `provider_used` / `cached_at` (`cache show`) and the
    `test-fingerprint` evidence detail are markup-escaped and
    control-stripped; the delta panel strips its prior-snapshot
    `auth_type`.
- **Markdown structure injection.** `strip_control_chars` preserves
  printable metacharacters, so an issuer or display name could still
  inject `[](url)` links, code spans, tables, or HTML into the markdown
  report (CLI and MCP). `format_tenant_markdown` now markdown-escapes
  those fields.
- **`chain_lookup` request amplification.** The most expensive MCP tool
  bypassed the per-domain rate limiter; it is now gated like the
  single-domain tools.
- **`cluster_verification_tokens`** caps and deduplicates its input (100
  distinct domains), matching the CLI batch path, so an MCP caller cannot
  drive unbounded sequential resolves.
- **`reload_data`** no longer clears the rate limiter (which let a caller
  bypass it between lookups); it still clears the result cache.
- Smaller bounds: cumulative retry-sleep cap (was up to roughly 90s per
  request); `test_hypothesis` / `simulate_hardening` argument-length
  caps; `domain_report` prompt control-char strip; chain BFS queue cap;
  batch input byte / line bound (a newline-free or all-comment file no
  longer loops or buffers without limit).
- New shared validator helper `is_safe_dns_name`; the cert-provider SAN
  check now aliases it.

Audit items intentionally left unchanged, with rationale in
`docs/security-audit-resolutions.md`: the shared async resolver (safe,
no answer cache to race); `raw_dns_records` accumulation (already bounded
by DNS response size); the `discover` `skip_ct` cache-key sharing
(correctness nicety, deferred to avoid changing the cache contract in a
security release); negative `--timeout` / `--cache-ttl` (cosmetic, no
security impact).

### Tests

- Regressions added in the per-module test file each one exercises:
  `is_safe_dns_name` (`test_validator.py`), the HTTP body cap
  (`test_http.py`), the `dominant_issuer` strip and `_clean_sans` charset
  drop (`test_infra_graph.py`), markdown escaping (`test_formatter.py`),
  the `cluster_verification_tokens` cap (`test_server_agentic.py`), and
  the malformed-BIMI-port cases (`test_bimi_vmc.py`).
- Updated the `reload_data` test to assert the rate limiter is preserved.

## [1.9.18] - 2026-05-20

### Security

Round-two audit pass over the data recon ingests from sources it does
not control (CT logs and the BIMI VMC fetch). Three findings, all
reachable on a normal lookup of a domain whose DNS or certificates an
attacker controls:

- **VMC fetch SSRF.** `_parse_bimi_vmc` fetched the BIMI TXT record's
  `a=` URL with only an `.endswith(".pem")` check, so a record like
  `a=https://attacker.example/x.pem` (or an internal / IP-literal host)
  drove recon's HTTP client to an attacker-named host, with redirects
  on. This was the one outbound call whose host came from
  attacker-controlled data. The URL is now validated before any fetch:
  https only, a public-DNS host (no IP literals, no internal suffixes),
  no embedded credentials, the default port, and `follow_redirects=False`.
  The shared client's transport already blocks private-IP destinations;
  this closes the attacker-chosen public-host case as well.
- **ANSI-escape / newline injection via CT SAN names.** Certificate SAN
  values from crt.sh / CertSpotter flowed into `related_domains` and the
  wildcard / burst surfaces with no character validation, and rich does
  not strip ESC, so a SAN carrying raw control bytes could drive
  terminal escape sequences when rendered, or inject lines into MCP /
  markdown output an agent consumes. SAN values are now rejected at
  ingestion unless they are clean DNS names (`_is_safe_san_name`).
- **ANSI-escape injection via certificate issuer names.** Issuer names
  are free text from the CT log and render under `--verbose`. They now
  pass through the new `strip_control_chars` (drops C0 / C1 control
  bytes, bounds length) before counting and display, as do the VMC
  subject fields.

New shared helper `recon_tool.validator.strip_control_chars`. See
`docs/security-audit-resolutions.md` for the full write-up.

### Tests

- `tests/test_bimi_vmc.py`: the VMC `a=` URL is refused for http,
  IP-literal, internal-suffix, credentialed, non-default-port, and
  single-label hosts (no fetch), and fetched with redirects disabled
  for a public https URL, with the subject control-char scrubbed.
- `TestCertDataSanitization` in `test_cert_providers.py` and
  `TestStripControlChars` in `test_validator.py` pin SAN rejection,
  issuer scrubbing, and the helper's behavior.

## [1.9.17] - 2026-05-20

### Security

- Generalized the internal-DNS-leak guard from the CNAME walker to
  every other resolver path. `_safe_resolve` now discards any
  non-CNAME, non-PTR answer whose recursive-resolver canonical name
  chased a CNAME to a non-public suffix (`.corp`, `.internal`,
  `.local`, an IP literal, and so on). recon queries many subdomains
  of a domain whose DNS the looked-up party controls (DKIM selectors,
  SRV records, IdP and Exchange probe prefixes); any non-CNAME query
  on such a name makes the operator's resolver chase a CNAME
  server-side before recon sees it. Discarding private-canonical
  answers means an internal name is never returned in records (no
  disclosure) and a private-chased query yields the same empty result
  as a name that does not resolve (no observable oracle). CNAME and
  PTR are exempt: the walker validates CNAME targets itself, and
  RFC 2317 reverse delegation legitimately CNAMEs within `.arpa`. The
  residual is a single blind query in the type-dependent-answer case,
  which returns nothing observable; see
  `docs/security-audit-resolutions.md`.
- Converted the A-presence subdomain probes (`_detect_idp_hub`,
  `_detect_exchange_onprem`, and the on-prem wildcard guard) to a
  CNAME-first `_resolves_to_public_endpoint` helper. A prefix the
  domain owner has delegated to an internal name is now rejected by
  suffix before any `A` or `AAAA` query fires, so the common attack
  costs zero internal queries rather than one blind chased query.
  Detection of self-hosted IdPs and on-prem Exchange via direct A
  records is unchanged.
- Synced the release workflow's dependency-audit gate with ci.yml.
  `release.yml`'s gating `pip-audit` step now carries the same
  `--ignore-vuln PYSEC-2025-183` that v1.9.16 added to ci.yml. Without
  this, a tagged release would fail the audit on the disputed no-fix
  pyjwt advisory and never reach PyPI, even though ci.yml accepts it.
  The two gates are now in lockstep.

### Tests

- `TestSafeResolveCanonicalGuard` (mocks the resolver) pins the
  canonical-name guard across the discard, keep-public-chase, and
  no-chase paths plus the CNAME and PTR exemptions.
- `TestResolvesToPublicEndpoint` pins the CNAME-first helper: a public
  CNAME and a direct A record resolve true; a private CNAME target
  returns false with no A query; a non-public entry returns false
  with no query at all.

## [1.9.16] - 2026-05-20

### Security

- Upgraded the locked `idna` from 3.11 to 3.15 to clear
  CVE-2026-45409. `idna` is a transitive dependency (via httpx and
  anyio); the lockfile bump is the fix and the CI dependency audit
  passes on it without an ignore.
- Added a documented, single-advisory ignore for pyjwt
  PYSEC-2025-183 (CVE-2025-45768) in the CI dependency-audit step.
  This is not a blanket suppression: `pyjwt` is pulled transitively
  by `mcp[crypto]` for MCP's HTTP/OAuth transport, no fixed version
  exists (2.12.1 is the latest and the whole 0.1.1-2.12.1 range is
  affected), the maintainer disputes the finding (key length is the
  calling application's responsibility), and recon runs the MCP
  server over stdio only, so pyjwt's signing path is never invoked.
  The ignore is scoped to that one advisory ID with an inline
  rationale and a note to drop it when a fixed pyjwt ships. See
  `docs/security-audit-resolutions.md`.

## [1.9.15] - 2026-05-20

### Security

- Hardened the SPF `redirect=` chaser (`_follow_spf_redirect` in
  `recon_tool/sources/dns.py`) against the same internal-DNS leak
  class as the CNAME walker. The chaser now validates each
  `redirect=` target against `_is_public_dns_name` before resolving
  it, so a queried domain whose SPF record reads
  `v=spf1 redirect=secret.internal.corp` can no longer drive the
  operator's resolver to query an internal or split-horizon name.
  The guard sits at the top of the function, so it also covers the
  recursive hop. Legitimate public targets such as
  `_spf.mail.example.edu` resolve unchanged. This closes a second
  instance of the "query and leak internal DNS names" finding that
  was first addressed for the CNAME walker; the SPF `include:`
  mechanism is only counted, never resolved, so it is not affected.
- Removed the dormant `_hop_resolves_publicly` /
  `_is_private_ip_literal` A/AAAA helper path from
  `recon_tool/sources/dns.py`. The CNAME walker remains strictly
  CNAME-only; deleting the unused helper removes an attractive
  future regression path for the internal-DNS leak class.

### Tests

- Added `TestSpfRedirectBlocksPrivateTargets` in
  `tests/test_cname_chain_validation.py`: a private-suffix
  `redirect=` target is not queried and does not credit SPF strict,
  while a legitimate public target ending in `-all` still does.
- Added a surface-attribution regression proving that an
  attacker-controlled CNAME to an internal/private suffix is not
  followed and cannot be emitted through `EvidenceRecord.raw_value`
  even when a later mocked hop would match a built-in provider
  fingerprint.

## [1.9.14] - 2026-05-17

**v1.9.14 security bridge: revert the v1.9.13 terminus-only A/AAAA
check.** A follow-up scanner pass against the v1.9.13 walker
flagged the new terminus-only A/AAAA check as reintroducing the
v1.9.4 internal-DNS leak through a type-dependent-answer path. The
v1.9.13 safety argument was that a prior CNAME-query NoAnswer
proved the terminus had no CNAME to chase on a subsequent A/AAAA
query. Authoritative DNS servers can return type-dependent
answers, so the argument does not hold: a malicious server can
answer the CNAME query for the terminus with NoAnswer while
returning a CNAME to an internal/split-horizon name on the A or
AAAA query. The recursive resolver follows that CNAME during A
resolution, re-introducing the v1.9.4 leak.

v1.9.14 reverts the terminus-only check. The walker now issues
CNAME queries only, restoring the v1.9.4 invariant
unconditionally. The v1.9.13 entry-point validation and the
M365 `redirect_domain` suffix filter are preserved (neither
depends on A/AAAA). The split-horizon detection the terminus
check was meant to add is left as a documented residual; see
`docs/security-audit-resolutions.md` for the closure trail and
options (a) / (b) for further reduction.

This is the v1.9.14 step of the v1.9.4 → v2.0 linear sequence in
`docs/roadmap.md`.

### Security

- **Reverted the terminus-only A/AAAA check in
  `_resolve_cname_chain` (`recon_tool/sources/dns.py`).** The
  v1.9.13 docstring's claim that "asking A/AAAA on a name that
  has no CNAME cannot cause a CNAME chase" assumed authoritative
  DNS responses are consistent across query types. They are not.
  The walker no longer calls `_hop_resolves_publicly`. The
  helper itself is preserved with `# pyright: ignore` for future
  callers that can guarantee a type-independent resolver path,
  but no current caller uses it.
- **Updated `_resolve_cname_chain` docstring and
  `_hop_resolves_publicly` docstring** to record the v1.9.13
  attempt, the 2026-05-17 scanner finding, and the v1.9.14
  reversion. The docstring is the on-call reference for anyone
  considering reviving the helper.
- **Updated `docs/security-audit-resolutions.md`** with the
  re-flag trail. The "Closed: A/AAAA CNAME validation can
  trigger internal DNS lookups" entry now records v1.9.13's
  reintroduction and v1.9.14's re-closure. The "Mitigated: CNAME
  chain walking can query and leak internal DNS names" entry's
  layer list drops the terminus-only A/AAAA check and notes the
  reversion as a documented design choice.

### Tests

- **`tests/test_cname_chain_validation.py`.** Replaced
  `TestTerminusOnlyAAAACheck` (which pinned the v1.9.13
  behavior) with `TestNoAAAAQueriesFromWalker`, which asserts no
  A or AAAA query fires on any of the three walker exit paths
  (natural exit, `max_hops` exit, suffix-rejection exit).
  Renamed `test_walker_does_not_resolve_a_aaaa_on_intermediate_hops`
  to `test_walker_does_not_resolve_a_aaaa_during_walk` and
  tightened the assertion to "no A/AAAA queries at all from the
  walker," matching the restored v1.9.4 + v1.9.14 invariant.

## [1.9.13] - 2026-05-17

**v1.9.13 security bridge: CNAME chain walker hardening (third
layer).** Tightens the surface-attribution pipeline after a fresh
scanner pass against the v1.5.0 introducing commit
(`332534d`) re-flagged the previously-mitigated chain-walker
finding. The v1.9.3.5 + v1.9.4 closure (suffix denylist +
CNAME-only-during-walk) was already authoritative; v1.9.13 adds
two further layers and one defense-in-depth tightening to reduce
the documented residual surface.

This is the v1.9.13 step of the v1.9.4 → v2.0 linear sequence in
`docs/roadmap.md`. Full closure trail in
`docs/security-audit-resolutions.md` and the threat model in
`docs/security.md`.

### Security

- **Entry-point validation in `_resolve_cname_chain`
  (`recon_tool/sources/dns.py:1827`).** The walker now checks
  `_is_public_dns_name(host)` before issuing the first CNAME
  query. Names with private suffixes, IP literals, or single-label
  form are rejected without touching the resolver. Closes a gap
  where unvalidated entries in `ctx.related_domains` (e.g. from
  `_detect_m365_cnames` redirect_domain extraction) would otherwise
  cause one DNS query through the operator's resolver against an
  attacker-influenced name.
- **Terminus-only A/AAAA check in `_resolve_cname_chain`
  (same file).** After the walk completes naturally (the resolver
  returns no further CNAME for the current name, or returns a
  self-loop), the walker now resolves A and AAAA on the terminus
  only. When every resolved address is in private/loopback/
  link-local/reserved space, the entire chain is dropped - the
  intermediate hop names (which include attacker-chosen text) never
  reach `EvidenceRecord.raw_value`. The v1.9.4 ban on A/AAAA
  during the walk loop is preserved: the new check runs only on
  the natural-exit path where the terminus has been established to
  have no further CNAME, so no recursive CNAME chase is possible.
  Skipped explicitly when the walker exited via `max_hops` or a
  suffix-rejection break (terminus has unfollowed CNAME → chase
  would re-introduce the v1.9.4 leak). The deferred-future option
  from the v1.9.4 `_resolve_cname_chain` docstring is now shipped.
- **Suffix filter on M365 redirect_domain
  (`recon_tool/sources/dns.py:547-562`).** `_detect_m365_cnames`
  now suffix-validates the redirect_domain extracted from a
  non-Microsoft autodiscover CNAME response before adding it to
  `ctx.related_domains`. Defense-in-depth against an
  attacker-controlled autodiscover response that would otherwise
  plant a private-suffix apex in related_domains (the chain walker
  would reject it at entry, but rejecting at the addition point
  keeps related_domains clean for panel/JSON consumers too).
- **Character-class restriction in `_is_public_dns_name`.** Names
  are now required to contain only ASCII alphanumerics, hyphen,
  dot, and underscore (the underscore covers legitimate DKIM and
  SRV selectors). Rejects names with HTML / shell / control /
  whitespace / non-ASCII characters that a lax DNS parser or
  adversarial response could otherwise smuggle into evidence
  output where a downstream renderer might interpret them. The
  v1.9.4-era explicit IPv6 colon check is folded into the
  character-class check (colons are no longer in the allowed set).
- **Entry-point case normalization in `_resolve_cname_chain`.**
  `host` is now lowercased and trailing-dot-stripped before the
  entry-point check and the walk loop, so a mixed-case input
  followed by a lowercased self-loop CNAME is detected on iteration
  1 (the previous behavior wasted one iteration before the
  case-mismatched self-loop was caught). Functional fix; not a
  security gap on its own but tightens the walker's invariants.

### Documentation

- **`docs/security-audit-resolutions.md`.** Closure record for the
  CNAME-walker finding rewritten to enumerate the residual surface
  precisely (three named cases), cite line numbers in current main,
  and add a *Re-flagged* row format for future stale-scanner
  reports. New *Mitigated vs Closed* glossary in process notes.
- **`docs/security.md`.** New dedicated "Malicious CNAME chains
  (surface-attribution walker)" section under the threat model
  listing the three-layer defense, the reduced residual surface,
  and the pinning test. Previous coverage was generic under
  "Malicious DNS responses."

### Tests

- **11 new regression tests** in
  `tests/test_cname_chain_validation.py` (59 total, up from 48):
  three for entry-point validation (private suffix, IP literal,
  single-label all rejected without queries), six for the
  terminus-only A/AAAA check (private terminus drops chain, public
  terminus keeps chain, dangling terminus fails open, mixed
  public/private terminus keeps chain, max_hops case skips
  terminus check, suffix-rejection case skips terminus check), and
  two for the M365 redirect_domain filter (private suffix dropped,
  public suffix still added). Full suite: 2,533 tests pass.
- **Existing
  `test_walker_does_not_resolve_a_aaaa_during_walk` renamed** to
  `test_walker_does_not_resolve_a_aaaa_on_intermediate_hops` and
  updated to allow A/AAAA on the terminus only - the v1.9.4
  invariant (no A/AAAA on intermediate hops during the walk loop)
  remains pinned.

### Changed

- **`_hop_resolves_publicly` docstring rewritten.** Function is
  no longer marked as unused; `# pyright: ignore` removed. New
  contract documented: safe to call only on a fully suffix-
  validated terminus that the walker has established has no
  further CNAME.

## [1.9.12] - 2026-05-16

**v1.9.12 bridge milestone: panel-display polish + doctor schema
verification + Mermaid evidence-DAG output.** Second bridge release
after v1.9.11's documentation polish dry-run. v2.0 remains the
mechanical schema-lock-and-tag event; this release ships the panel
correctness fixes and the doctor schema-fields verification that
the v2.0 quality bar requires.

### Added

- **Mermaid output for `--explain-dag`.** Third format alongside
  `text` and `dot`: `recon <domain> --explain-dag --explain-dag-format
  mermaid` emits raw Mermaid.js syntax. Renders inline in GitHub,
  GitLab, Notion, Obsidian, and most AI chat clients without a
  Graphviz pipe step. Same hedged labels, sparse/dense stroke
  discipline, and top-influence ranking as the DOT renderer. Pure
  text emission; no new dependencies. Pinned by
  `tests/test_bayesian_dag.py::TestMermaidRenderer` (8 cases
  covering header, edge structure, sparse-dash styling, HTML
  escaping, and posterior label inclusion).
- **`recon doctor` schema-fields verification.** Wires up the
  half of the v2.0 quality bar that was print-only: doctor now
  synthesises a minimal `TenantInfo`, runs it through
  `format_tenant_json`, and confirms every required top-level
  field from `recon_tool/schema_contract.REQUIRED_TOP_LEVEL_FIELDS`
  is present in the output. Reports `Schema fields  ok  46 locked
  top-level fields present` on a healthy build. The 46-field
  tuple is pinned to `docs/recon-schema.json#/required` by a new
  drift-guard test, so it fails CI if the schema and the runtime
  mirror disagree.
- **Catalog growth invariant test
  (`tests/test_slug_category_invariant.py`).** Every fingerprint
  slug must either appear in `_CATEGORY_BY_SLUG` (explicit user-
  facing category) or in an allowlist of legacy fall-through
  slugs (`EXPECTED_BUSINESS_APPS_FALLBACK`). A new slug shipped
  without an explicit decision now fails CI rather than silently
  bucketing under "Business Apps" - the same shape of bug the
  28-slug categorization fix below addressed.

### Fixed

- **Slug-categorization regression on the v2.0-prep catalog
  growth.** All 28 new `cname_target` slugs from the 4,270-apex
  scan were missing from `recon_tool/formatter._CATEGORY_BY_SLUG`,
  so detections for AWS regional endpoints, Azion / Baidu / Naver
  / Tencent CDNs, Microsoft Edge Front Door, Adobe Analytics,
  Socrata, Vanta, SafeBase, WeChat, etc. silently bucketed as
  "Business Apps" in the panel. Each now maps to its correct
  user-facing category (Cloud / Data & Analytics / Security /
  Collaboration / Email). Cloud-categorized slugs received the
  required rollup decision in `_CLOUD_VENDOR_BY_SLUG` (AWS,
  Azure, Naver Cloud Platform, Tencent Cloud) or
  `_CLOUD_VENDOR_ROLLUP_EXCLUSIONS` (specialty regional CDNs).
- **Legacy slug miscategorizations.** Sweep of pre-existing slugs
  that fell through to the Business Apps default but were
  unambiguous: observability and data-warehouse slugs (datadog,
  dynatrace, newrelic, sumologic, splunk, sentry, honeycomb,
  grafana-cloud, snowflake, databricks, mongodb, mixpanel,
  amplitude, heap, pendo, segment) now bucket as Data &
  Analytics; MDM and privacy slugs (jamf, kandji, onetrust, hibp)
  as Security; standalone CDN/DNS slugs (imgix, keycdn, stackpath,
  ns1, ultradns) as Cloud (with rollup-exclusion decisions for
  each). 25 legacy slugs corrected.
- **`surface.yaml` comment miscount.** Header for the 4,270-apex
  catalog growth said "30 new cname_target entries"; the actual
  count is 28 unique slugs (one cname_target was added to the
  existing HubSpot slug). Comment now matches.
- **Per-stratum aggregator misbucketing.** `validation/corpus_aggregator.py`
  classified strata from a tenant_id substring matcher
  (`_stratum_for_tenant`). Three v1.9.10 fixtures landed in the
  wrong bucket: `tailspin-firebase` (GCP) and `gamma-oci`
  (Oracle) fell into `baseline` because their tenant_ids lacked
  the `-gcp-` / `-oracle-` substring; `wingtip-azure` (baseline)
  was pulled into the Azure bucket because its tenant_id
  coincidentally contained `-az`. The v1.9.10 aggregate output
  read baseline=20, gcp=9, azure=11, oracle=9 instead of the
  intended baseline=19 + 10 per stratum. Overall multi-cloud and
  ceiling rates (29.1% / 86.1%) were correct; only the
  per-stratum allocation needed correction.

  The fix injects an explicit `_stratum` tag at fixture-generation
  time in `validation/synthetic_corpus/generator.py`, derived from
  the REGISTRY key (the authoritative grouping signal). The
  aggregator now reads `_stratum` from each entry; legacy entries
  and real-corpus entries without the tag bucket as `baseline`.
  `validation/synthetic_corpus/results.json` and `aggregate.json`
  regenerated.

  Pinned by `tests/test_corpus_aggregator.py::TestStratumDerivation`
  and `TestPerStratumAggregation`, covering each historical
  misbucketing path.

### Changed

- **`validation/v1.9.10-pre-lock.md`.** Corrected per-stratum
  table is the live numbers section; the original v1.9.10
  ship-time table is preserved under "Appendix - original
  (v1.9.10 ship-time) per-stratum numbers" so the historical
  receipt remains traceable.
- **`validation/v2.0-corpus-run.md`.** Comparison line updated to
  cite the corrected per-stratum baseline.

## [1.9.11] - 2026-05-15

**v1.9.11 bridge milestone: documentation polish dry-run.** Last
patch before v2.0 schema lock. Every doc reviewed against the v2.0
quality bar; every promised-to-be-stable surface has the
EXPERIMENTAL label stripped; the v1.9.11 worklist from
`validation/v2.0-prep-baseline.md` is fully resolved. No engine
behaviour changes; v2.0 will be a mechanical lock-and-tag event
on top of this build.

This is the v1.9.11 step of the v1.9.4 → v2.0 linear sequence in
`docs/roadmap.md`.

### Added

- **`docs/migration-v2.md` populated.** v1.x → v2.0 migration
  guide with the field-promotion table, `okta_idp` disposition
  section, schema-version bump notes, and downgrade-path
  recommendation. Replaces the skeleton shipped in v1.9.10.1 prep.
- **`docs/recon-schema.json` BatchResult definition.** Closes the
  one known schema gap (`ecosystem_hyperedges` was previously a
  typed property only in description text; now formally a
  property of the BatchResult def). The schema-disposition test
  `tests/test_schema_disposition.py` is fully green with zero
  known gaps.
- **`scripts/check_no_experimental_labels.py`.** Targeted CI gate
  that pattern-matches active EXPERIMENTAL labels (parentheticals,
  bracket-prefixes, markdown stability columns) on user-facing
  surfaces and exits non-zero on any hit. Wired into
  `.github/workflows/ci.yml` after the metadata-coverage gate.
- **`validation/v1.9.11-trend-table.md`.** Public per-release
  trend table v1.6 → v1.9.11. Compiled from per-release
  validation memos and the v1.9.10 stratified aggregate. Anchors
  the v2.0 "engine got progressively more validated" claim with
  named sources, not the maintainer's word.
- **`validation/v2.0-corpus-run-runbook.md`** and
  **`validation/v2.0-corpus-run.md`** (result shell). Maintainer-
  side recipe for the real-corpus aggregator run that gates v2.0,
  plus the empty result-shell the run populates. The v2.0
  release workflow refuses to tag if the result shell still
  contains the `<TO BE POPULATED>` placeholders.
- **`docs/correlation.md` §4a, §4b, §4c.** Three v2.0 snapshot
  sections promised in the roadmap quality bar: Defense ↔
  correlation mapping table, prior-art comparison, and
  dependency-floor manifesto. Each is anchored against the
  existing formal model in §4-§4.8 rather than restating it.
- **`recon doctor` schema-stability indicator.** Doctor's
  header now prints "(pre-v2.0 schema)" on v1.9.x builds and
  "(v2.0 stable schema)" on v2.0+ builds, so operators see the
  lock visibly. v2.0 tag will flip the label without further
  code changes.

### Changed

- **EXPERIMENTAL labels stripped from user-facing surfaces.**
  v1.9.10's baseline (38 hits across 14 files) brought to zero
  active labels. Surfaces touched: `recon_tool/models.py`
  (5 hits), `recon_tool/server.py` (3), `recon_tool/cli.py` (3),
  `docs/stability.md` (3 active labels → table of pre-v2.0 →
  v2.0 promotions), `docs/recon-schema.json` (3 field-description
  rewrites), `recon_tool/fusion.py`, `recon_tool/formatter.py`,
  `recon_tool/data/bayesian_network.yaml`,
  `recon_tool/bayesian_dag.py`, `recon_tool/bayesian.py`,
  `docs/schema.md`, `docs/mcp.md`, `docs/correlation.md`
  (14 hits → 0 active labels; "Validation history" subsection
  replaces the per-release running-commentary framing).
  Past-tense prose discussion of the historical label survives
  in `docs/roadmap.md`, `docs/migration-v2.md`, and
  `docs/release-process.md` - the CI gate pattern-matches for
  active labels (parens, brackets, prefixes), not prose.
- **`okta_idp` disposition applied** per
  `validation/v2.0-prep-baseline.md` §3. Node ships in v2.0 with
  an inline YAML comment recording the corpus-exposure caveat
  (criterion (c) cleared on v1.9.10's stratified synthetic
  corpus with 8+ fixtures firing the node; real-corpus
  authoritative number recorded in `validation/v2.0-corpus-run.md`
  per the v2.0 gate).
- **`tests/test_schema_disposition.py`** updated:
  `ecosystem_hyperedges` moved from `_V2_KNOWN_SCHEMA_GAPS` to
  `_V2_PROMOTED_FIELDS` once the BatchResult schema definition
  shipped. Gap list is empty at v1.9.11 ship; the v2.0 check
  will fail on any future entry to the gap list when version
  reaches 2.0.

### Validation

- All 2502 tests pass (3 skipped, 4 deselected).
- ruff lint + format clean across 207 files.
- pyright on `recon_tool/`, `validation/corpus_aggregator.py`,
  `validation/threshold_sensitivity.py`, and
  `scripts/check_no_experimental_labels.py` reports 0/0/0.
- `scripts/check_no_experimental_labels.py` returns 0 active
  labels.
- `tests/test_schema_disposition.py` 6 tests all green; the
  v2.0-blocks-on-unresolved-gap test confirms the gap list is
  empty.

### What's left before v2.0 tag

The remaining v2.0 blockers all live outside this commit:

- **Real-corpus aggregator run.** Maintainer runs locally per
  `validation/v2.0-corpus-run-runbook.md`; the result-shell
  populates with aggregate counts (no domain names) and is
  committed.
- **Schema-version bump in `docs/recon-schema.json`** when v2.0
  tags. Mechanical: the v2.0 release workflow does it.
- **Final correlation.md proofread** against the v2.0 quality
  bar (dead links, dependency-manifest drift, prose voice).
- v2.0 release notes draft.

Per the roadmap, v2.0 itself is a mechanical lock-and-tag
ceremony on top of v1.9.11; no engine changes between this
release and v2.0 should be required.

## [1.9.10.1] - 2026-05-15

**Docs-only patch.** v1.9.10's sdist shipped with three Mermaid
blocks and one display-math block in `docs/correlation.md` that
GitHub's renderer rejected (the wheel does not bundle docs and is
unaffected). The render errors are visible to anyone unpacking the
sdist or browsing the file via the v1.9.10 git tag. v1.9.10.1
ships the fixed correlation.md in both wheel and sdist so the
release artifacts match the polished version visible on `main`.

### Fixed

- **correlation.md §1 Mermaid block.** The flowchart used `graph`
  as a node id; `graph` is a reserved Mermaid keyword and GitHub's
  parser rejected the entire block. Renamed the node id to
  `graphL`.
- **correlation.md §4.3 display math.** The DRO formula
  `$$P^*(X \mid E^* = \text{missing}) \;=\; ...$$` confused
  GitHub's markdown→MathJax pipeline because the asterisks were
  eaten as italic-emphasis delimiters across math boundaries.
  Rewritten as `^{\ast}` which MathJax handles unambiguously. The
  same fix applied to every inline `E^{\ast}` in the same section
  (6 occurrences total).
- **CONTRIBUTING.md placeholder syntax.** The "Common framings"
  examples used `$X` / `$Y` / `$TENANT` template-variable
  placeholders that GitHub's MathJax tried to parse as math
  expressions. Replaced with backticks so they render as inline
  code.

### Changed

- **correlation.md redundancy trim** (82 lines cut, formal content
  unchanged). The §4.3 literature parade (Manski + Jeffrey +
  Walley + Augustin + Taroni) compressed to one paragraph with
  inline citations preserved. §4.13 (v1.9.7/v1.9.8 narrative)
  and §4.14 (v1.9.9 panel surfaces) collapsed; per-release
  detail moved to the linked validation memos.

### Validation

- All 2497 tests pass (2 skipped, 4 deselected). No code changes
  in this patch.
- ruff + format + pyright clean.
- Doc-only changes; PyPI v1.9.10's wheel is functionally
  identical to v1.9.10.1's wheel.

## [1.9.10] - 2026-05-15

**v1.9.10 bridge milestone: stratified-corpus pre-lock validation.**
Extends the v1.9.9 19-fixture synthetic corpus to 79 fixtures (60
new stratum-tagged fixtures + 19 base) across six cloud strata:
GCP, Azure non-O365, Oracle, Alibaba, PaaS / Vercel / Netlify, and
SSE / SASE. Per-stratum aggregator emits coverage metrics. Bayesian
network re-validated against the v1.9.9 evidence-distribution
shift; v1.9.6 disposition table holds. No engine code changes; no
JSON schema changes.

This is the v1.9.10 step of the v1.9.4 to v2.0 linear sequence in
`docs/roadmap.md`. Full write-up at
`validation/v1.9.10-pre-lock.md`,
`validation/v1.9.10-bayesian-revalidation.md`, and
`validation/v1.9.10-mutation-status.md`.

### Added

- **60 stratum-tagged synthetic fixtures** at
  `validation/synthetic_corpus/fixtures/stratum_*.json` (10 per
  stratum × 6 strata). Generator at
  `validation/synthetic_corpus/generator.py` is deterministic and
  publicly-reproducible. All apex names use Microsoft-fictional
  brands per the no-real-data discipline.
- **Per-stratum aggregator output** in
  `validation/corpus_aggregator.py`. The `_stratum_for_tenant`
  helper buckets fixtures by tenant_id substring; the aggregate
  output now carries a `per_stratum` map with per-stratum counted
  / multi-cloud / ceiling firing rates.
- **`validation/v1.9.10-pre-lock.md`** - per-stratum coverage
  table, behaviour interpretation per stratum (PaaS fires multi-
  cloud most often at 70% because PaaS providers + Cloudflare are
  legitimately multi-vendor; SSE never fires at 0% because the SSE
  provider is SaaS, not cloud), and honest framing about
  synthetic-corpus bias.
- **`validation/v1.9.10-bayesian-revalidation.md`** - audit of the
  network's evidence bindings (5 signals + upstream node
  posteriors), cross-check against v1.9.9 wordlist additions
  (none of the new wordlist tiers feed any binding), and empirical
  re-run of the v1.9.5 stability test suite (20/20 pass on v1.9.9
  codebase).
- **`validation/v1.9.10-mutation-status.md`** - documents the
  cosmic-ray sweep slip from v1.9.10 to v2.0 schema lock with
  rationale (the v1.9.9 catalog-driven Hypothesis tests already
  caught a real bug, which is stronger evidence than a clean
  cosmic-ray run).

### Changed

- **`validation/synthetic_corpus/generator.py`** REGISTRY extended
  from 19 to 79 entries. Each new fixture is named with a
  `stratum_<id>_*` prefix so the per-stratum aggregator can group
  them automatically.
- **`validation/synthetic_corpus/results.json`** regenerated as
  combined 79-fixture results.
- **`validation/synthetic_corpus/aggregate.json`** regenerated
  with `per_stratum` map.
- **`validation/invariant_audit.md`** - item 2 (cosmic-ray)
  milestone updated from v1.9.10 to v2.0 lock.
- **`docs/roadmap.md`** - v1.9.10 section flipped from
  forward-looking to shipped; current-release line updated;
  cumulative pre-v2.0 work list extended.
- **Removed `cosmic-ray-v199.toml` from repo root.** Committed
  in v1.9.9 in error; version-stamped tooling config in the root
  ages poorly. Removal already shipped on `main` between v1.9.9
  and v1.9.10. Doc references updated to describe the cosmic-ray
  sweep as "config to be authored at sweep time".

### Validation

- All v1.9.5 stability tests pass on the v1.9.9 codebase (20/20).
- Synthetic 79-fixture corpus aggregator output: multi-cloud
  rendered 23/79 (29.1%), ceiling rendered 68/79 (86.1%).
  Per-stratum breakdown in `validation/v1.9.10-pre-lock.md`.
- Full pytest suite passes (test counts in pre-tag verification).
- ruff lint and ruff format clean.
- pyright on `recon_tool/` and validation tooling clean.

### Scope notes

- **Real customer data is NOT in the committed corpus.** The
  roadmap original quality bar called for "publicly-documented
  users of that vendor sourced from vendor case-studies, vendor
  blog posts, or job listings". The maintainer's no-real-data
  discipline (explicit synthetic labels and reserved domains) takes precedence;
  v1.9.10 ships with synthetic stratified fixtures modelled after
  public deployment patterns.
- **Trend table v1.6 → v1.9.10 per stratum** deferred to v1.9.11
  doc-polish pass. Requires re-running earlier versions against
  the new strata.
- **Real-corpus aggregator run** remains standing work. The
  maintainer runs `validation/corpus_aggregator.py` locally
  against the gitignored private corpus and drops the aggregate
  output into `validation/v1.9.10-corpus-run.md`. Tracked in
  `validation/invariant_audit.md` item 1.
- **Cosmic-ray full sweep** slipped to v2.0 schema lock with a
  Linux CI runner. Rationale in
  `validation/v1.9.10-mutation-status.md`.

## [1.9.9] - 2026-05-14

**v1.9.9 bridge milestone: detection-gap UX surfaces.** Three additions
to the default panel that make the architectural limits of passive DNS
collection visible without changing what data the tool collects. After
v1.9.9 the panel shows what it cannot see (the passive-DNS ceiling),
casts a wider net for what it can see (extended common-prefix
enumeration), and summarises the distribution (apex-level multi-cloud
rollup). No engine code changes ship; no JSON schema additions ship.

This is the v1.9.9 step of the v1.9.4 to v2.0 linear sequence in
`docs/roadmap.md`. The multi-apex CT SAN traversal mentioned alongside
the wordlist additions in the v1.9.9 roadmap section was deferred to
v1.9.9.1 so the cert-side breadth change can land with its own
validation pass; the three surfaces shipped here are panel-only and
self-contained.

### Added

- **Passive-DNS ceiling phrasing in the default panel.** When the panel
  is sparse on an apex that probably should not be, a one-line teaching
  footer renders under the Services block: "Passive DNS surfaces what
  publishes externally. Server-side API consumption, internal workloads,
  and SaaS without DNS verification do not appear in public DNS
  records." Operators and AI agents reading the panel now have an
  explicit cue against the absence-of-finding-equals-absence-of-service
  misread. Trigger heuristic is conservative on purpose: fires only when
  `info.services` is non-empty (a different surface owns failed runs),
  `info.domain_count >= 3` (the apex has multiple tenant domains, so
  sparse is genuinely surprising), categorized service families are
  fewer than 5, and CNAME-chain subdomain attributions are fewer than 5.
  Both halves of the sparse check must hold so a domain with short
  Services but many surface attributions does not gain a misleading
  footer. `--full` / `--domains` suppresses the line because those modes
  already carry the long surface section.
- **Apex-level multi-cloud rollup indicator.** When the canonicalized
  vendor count across apex slugs and surface attributions is at least
  two, a `Multi-cloud` row joins the key-facts block above Confidence:
  for example `Multi-cloud: 3 providers observed (AWS, Cloudflare,
  GCP)`. A single-vendor apex stays unannotated to avoid adding a
  vacuous row. Sibling slugs collapse: AWS Route 53 plus AWS CloudFront
  is one AWS vote, not two. Firebase rolls up under GCP because that
  matches how operators think about the Google cloud footprint at the
  rollup level. The per-slug Cloud row and per-subdomain Subdomain row
  continue to carry the full distribution; the rollup is the at-a-glance
  summary, not a replacement.
- **Cloud-vendor canonicalization map.** `_CLOUD_VENDOR_BY_SLUG` in
  `recon_tool/formatter.py` is the single source of truth that maps
  cloud-categorized fingerprint slugs to their vendor identity (AWS,
  Azure, GCP, Cloudflare, Fastly, Akamai, Vercel, Netlify, Oracle Cloud,
  IBM Cloud, Alibaba Cloud, and so on). Two public helpers,
  `canonical_cloud_vendor(slug)` and `count_cloud_vendors(apex_slugs,
  surface_slugs)`, sit on top of it so future panels and JSON paths can
  reuse the same canonicalization without duplicating the table inline.
  Slugs not in the map are not counted as cloud vendors, which is the
  right default for things like Slack or Auth0 (SaaS, not cloud
  infrastructure) and developer-platform slugs like Replit or Glitch.
- **Common-prefix wordlist breadth across four stack tiers.** The
  active-DNS probe in `recon_tool/sources/dns.py` and the CT
  high-signal sort in `recon_tool/sources/cert_providers.py` both gained
  the same eight prefixes covering tiers the prior wordlist ignored:
  data and analytics (`data`, `analytics`), AI and ML (`ai`, `ml`),
  operations and internal tooling (`internal`, `ops`, `tools`), and
  security (`security`). Each prefix maps to a recognised stack tier
  with vendor-product backing (Snowflake under `data`, Vertex AI under
  `ai`, internal portals under `internal`, SIEM consoles under
  `security`). The CT-side additions keep prioritization parity so a CT
  response surfacing `data.alpha.invalid` sorts to the top of the bounded
  output rather than falling off the cap.
- **`tests/test_formatter_ceiling.py`** (7 tests). Pins the trigger
  heuristic: fires on sparse-services + multi-domain apex; suppressed
  on single-domain apex, dense categorized services, many surface
  attributions, `--full` mode, and empty services. Phrasing tone is
  asserted to be teaching, not tool-blaming.
- **`tests/test_multi_cloud_rollup.py`** (16 tests). Pins both
  canonicalization (AWS family collapses to AWS, Firebase rolls under
  GCP, non-cloud slugs return None) and trigger discipline (fires on
  multi-vendor, suppressed on single-vendor and SaaS-only apex).
- **`tests/test_subdomain_enumeration_breadth.py`** (10 tests). Pins
  the new wordlist entries in both the active-probe tuple and the
  CT-prioritization tuple. A future refactor that compacts either
  cannot silently drop tier coverage without these tests flagging.
- **`tests/test_cloud_vendor_coverage.py`** (4 tests). Coverage-gap
  enforcement: every Cloud-categorized slug in ``_CATEGORY_BY_SLUG``
  must appear in either ``_CLOUD_VENDOR_BY_SLUG`` or
  ``_CLOUD_VENDOR_ROLLUP_EXCLUSIONS`` (a new explicit exclusion set
  for SaaS hosting, prototyping platforms, and long-tail specialty
  vendors). Map and exclusion set are disjoint and both stay
  consistent with the cloud category. The test caught one real
  inconsistency at introduction: ``aws-waf`` was incorrectly in the
  rollup map even though it is Security-categorized, not Cloud;
  removed.
- **`tests/test_formatter_ceiling_boundary.py`** (8 tests). Off-by-one
  cases that the surrounding fixture tests would miss: exact-threshold
  domain_count (3 fires, 2 suppresses), categorized count (4 fires, 5
  suppresses), surface attributions count (4 fires, 5 suppresses), and
  the AND-gate behaviour where density on one half is enough to
  suppress.
- **`tests/test_count_cloud_vendors_properties.py`** (5 Hypothesis
  property tests). Invariants that hold across the full input space:
  order independence on the apex stream, non-cloud-slug additions are
  no-ops, stream union semantics (apex + surface split equals
  concatenated stream), total count equals input length when all
  inputs are in the map, distinct vendor count is bounded above by
  the input slug count.
- **`tests/test_panel_render_snapshots.py`** (12 end-to-end render
  snapshot tests). Two reference TenantInfo fixtures (Synthetic Alpha
  multi-cloud rich-stack, Synthetic Gamma sparse-hardened) exercised through
  ``render_tenant_panel`` with structural asserts on which v1.9.9
  surfaces fire on which fixture, the layout invariant that
  Multi-cloud renders above Confidence in the key-facts block, and
  the ``--full``-mode suppression behaviour for the ceiling block.
- **``_CLOUD_VENDOR_ROLLUP_EXCLUSIONS`` in formatter.py**. New
  explicit exclusion set documenting which Cloud-categorized slugs
  intentionally do not appear in the rollup, with three rationale
  categories: SaaS hosting (WP Engine, Kinsta, Acquia, GitHub Pages,
  WordPress VIP), developer / prototyping platforms (Replit, Glitch),
  specialty CDN / DAM / hosting that operators would not list
  alongside AWS/Azure/GCP (Cloudinary, Azion, Section.io, MerlinCDN,
  Edgio, Lumen, Ionos, and others). Forces the rollup decision at PR
  time when a new cloud-categorized slug ships.
- **``category_for_slug`` public accessor in formatter.py**. Wraps
  `_CATEGORY_BY_SLUG` so callers outside the formatter (notably the
  v1.9.9 corpus aggregator) can estimate the panel's categorized
  count without re-running `_categorize_services` or reaching into
  the private lookup.
- **`validation/corpus_aggregator.py`**. Pure-function script
  that consumes a `recon batch --json` results file and emits
  anonymized aggregate statistics on Multi-cloud and ceiling
  firing rates. Reads gitignored private corpus runs; emits
  anonymized output safe to commit. The trigger logic mirrors the
  renderer's by design; the test file pins both implementations
  to the same fixtures so they cannot drift.

### Changed

- **`recon_tool/formatter.py`** gains `_CLOUD_VENDOR_BY_SLUG`,
  `_CLOUD_VENDOR_ROLLUP_EXCLUSIONS`, `canonical_cloud_vendor`, and
  `count_cloud_vendors`, plus the Multi-cloud field and the
  Passive-DNS ceiling block in `render_tenant_panel`. The
  categorized-service count threads through a small local helper
  variable so the ceiling check can reference it outside the services
  branch without `categorized` itself escaping scope.
- **AWS rollup family expanded.** Added `aws-nlb`, `aws-api-gateway`,
  `aws-app-runner`, `aws-global-accelerator` to the AWS family so the
  rollup catches them. Added `cloudflare-pages` to the Cloudflare
  family. Removed `aws-waf` (Security-categorized, not Cloud - the
  coverage-gap test caught this at introduction).
- **Standalone vendor coverage expanded** to include Heroku, VMware
  Cloud, Cloud.gov, Edgio, Lumen, F5 Distributed Cloud - each
  represents a cloud vendor an operator would name alongside AWS or
  Azure when describing a footprint at the rollup level.
- **`recon_tool/sources/dns.py`**'s `_COMMON_SUBDOMAIN_PREFIXES` grew
  from 38 to 46 entries; each new entry carries an inline comment naming
  the stack tier it represents and the vendor-product idiom that
  motivates including it.
- **`recon_tool/sources/cert_providers.py`**'s `HIGH_SIGNAL_PREFIXES`
  grew the same 8 prefixes so CT subdomain prioritization stays in
  parity with the active probe.

### Security

- **MCP fallback launch path closed on Python 3.10.** The
  `build_recon_block()` fallback (used when ``recon`` is not on
  PATH) previously persisted ``python -m recon_tool.server`` with
  ``PYTHONSAFEPATH=1``. On Python 3.10 the env var is a no-op, so a
  malicious workspace containing ``recon_tool/server.py`` could
  shadow the installed package and execute attacker code at module
  import time - before the runtime guard in ``server.py`` could
  fire. The v1.9.3.4 mitigation closed this for ``mcp_doctor``
  (which sets a safe tempdir cwd) but left the persisted
  installer block reliant on PYTHONSAFEPATH on 3.10.

  v1.9.9 closes this fully by switching the persisted form to
  ``python -c "<sys.path-stripping launcher>"``. The launcher runs
  ``sys.path[:] = [p for p in sys.path if p not in ('', '.')]``
  BEFORE any ``recon_tool`` import, removing the cwd-equivalent
  entry at the language level. This works on every supported
  Python version, including 3.10. PYTHONSAFEPATH=1 stays in the
  persisted env as belt-and-suspenders for 3.11+.

  New integration test
  ``test_v199_fallback_launcher_blocks_shadow_on_all_pythons``
  exercises the actual persisted launcher against a malicious
  shadow workspace and asserts the shadow does not execute.
  ``docs/security-audit-resolutions.md`` updated to reflect the
  v1.9.9 closure honestly (the v1.9.3.4 entry now distinguishes
  the doctor-path closure from the install-path partial mitigation
  that v1.9.9 completed).

### Fixed

- **`Data & Analytics` category KeyError in panel renderer.** The
  category was added to ``_CATEGORY_BY_SLUG`` in v1.9.3.9 (with the
  ``looker-studio`` slug) but never to ``_SERVICE_CATEGORIES_ORDER``.
  Any apex with the slug fired triggered ``KeyError`` at
  ``by_cat[cat].append(...)`` in ``_categorize_services`` and
  crashed the panel. Fixed by adding the category to the order
  tuple and adding a defensive bucket-creation guard so future
  category drift cannot crash the renderer (the new category will
  be missing from rendered output until added to the tuple, but
  the panel will not crash). Caught at first run by the new
  catalog-driven Hypothesis test
  ``test_catalog_driven_corpus.py::test_low_domain_count_never_fires_ceiling``.
- **Okta surface description used "strong"** (overclaim per the
  project's humble-tone discipline). Rephrased to "load-bearing"
  (`recon_tool/data/fingerprints/surface.yaml`). Caught at first
  run by the new suite-wide humble-tone enforcement test
  ``test_humble_tone_global.py``.
- **`aws-waf` was wrongly in the Multi-cloud rollup map** even
  though it is Security-categorized in `_CATEGORY_BY_SLUG`.
  Removed from `_CLOUD_VENDOR_BY_SLUG`. Caught by the
  coverage-gap test added during v1.9.9 development.

### Validation

- All 2496 tests pass (2 skipped, 4 deselected). v1.9.9 ships **182
  new tests across 23 new test files plus a corpus-aggregator
  script, a synthetic 19-fixture corpus generator, a render-
  snapshot report, a threshold-sensitivity analysis, an invariant
  audit, an agentic-UX runbook, a coverage-gap audit, and a
  performance baseline doc** covering falsifiable surfaces along
  seven orthogonal axes: trigger behaviour (fixture, boundary,
  property), test quality (mutation resistance with 6 named
  mutations + three-way differential agreement check), integration
  (CLI, cross-version cache, JSON shape), robustness (fuzz,
  adversarial, determinism, performance bounds), corpus validation
  (synthetic corpus + catalog-driven Hypothesis + aggregator),
  tone discipline (suite-wide humble-tone enforcement), and
  documentation (validation memo, test-quality manifesto,
  corpus-run report, threshold sensitivity, invariant audit,
  coverage-gap audit, performance baseline, agentic-UX runbook).

  The **catalog-driven Hypothesis test caught a real pre-existing
  bug**: ``looker-studio`` (added in v1.9.3.9 with category
  ``"Data & Analytics"``) was missing from
  ``_SERVICE_CATEGORIES_ORDER``, causing a ``KeyError`` in the
  panel renderer for any apex with the slug. Fixed by adding the
  missing category to the order tuple and adding a defensive
  bucket-creation guard in ``_categorize_services``. Test invariant
  pinned in ``test_cloud_vendor_coverage.py`` so future drift fails
  at PR time.

  The **suite-wide humble-tone test caught a real catalog
  violation**: the okta surface description used the word "strong"
  (overclaim per the project's discipline). Rephrased to
  "load-bearing".

  See `validation/v1.9.9-detection-gap-ux.md` for the per-file
  rationale and the explicit "what we test and what we honestly do
  not" section. See `validation/invariant_audit.md` for the
  distinct-invariant count (51) vs the test count (182), and the
  remediation plan for each "what we honestly do not test" item.
  Test files:
  1. Fixture behaviour on the ceiling trigger
     (`test_formatter_ceiling.py` - 7 tests).
  2. Fixture behaviour on the multi-cloud rollup, including
     canonicalization (`test_multi_cloud_rollup.py` - 16 tests).
  3. Wordlist extensions in both the active probe and the CT priority
     tuple (`test_subdomain_enumeration_breadth.py` - 10 tests).
  4. Coverage-gap enforcement on the rollup map versus
     `_CATEGORY_BY_SLUG`, with explicit exclusion-set discipline
     (`test_cloud_vendor_coverage.py` - 4 tests). Caught one real
     bug at introduction: `aws-waf` was wrongly in the rollup map.
  5. Off-by-one boundaries on the ceiling trigger's three numeric
     thresholds (`test_formatter_ceiling_boundary.py` - 8 tests).
  6. Hypothesis property invariants on `count_cloud_vendors`
     (`test_count_cloud_vendors_properties.py` - 5 tests).
  7. End-to-end render snapshots across two reference TenantInfo
     fixtures (`test_panel_render_snapshots.py` - 12 tests).
  8. Render-fuzz: arbitrary TenantInfo through
     `render_tenant_panel` must not raise
     (`test_render_fuzz.py` - 3 tests, 500 Hypothesis examples).
  9. v1.9.2 agentic-UX fixture compatibility under the v1.9.9
     panel (`test_agentic_ux_compatibility.py` - 7 tests).
  10. JSON-absence contract: v1.9.9 surfaces are panel-only
      (`test_panel_only_surfaces_json_absence.py` - 6 tests).
  11. Rendered-output sanity: no vendor duplication, no orphan
      punctuation, no overclaim words, bounded line length
      (`test_panel_output_sanity.py` - 7 tests).
  12. Wordlist hygiene: deduplication, lowercase, no whitespace,
      parity between active probe and CT priority tuples
      (`test_wordlist_sanity.py` - 8 tests).
  13. Corpus-aggregator script behaviour, mirroring the renderer's
      trigger logic on serialized TenantInfo dicts
      (`test_corpus_aggregator.py` - 11 tests).
  14. **Targeted mutation resistance** on the v1.9.9 helpers. Five
      named mutations (None-guard drop, unknown-slug leak, double
      count, comparator flip, threshold flip) confirmed caught by
      the existing test suite (`test_mutation_resistance.py` - 9
      tests). Honest framing: this is a hand-rolled pilot, not a
      full ``mutmut`` sweep. The bar is "the most likely mutations
      to slip past careful review are caught"; broader coverage
      remains a post-v2.0 backlog item.
  15. **CLI integration smoke** for the Typer entry point.
      ``--help``, ``--version``, every subcommand's help, the
      installed-entry-point shape via subprocess
      (`test_cli_integration_smoke.py` - 15 tests).
  16. **Render determinism** in-process and across processes with
      distinct ``PYTHONHASHSEED`` values. 30 in-process renders
      byte-identical; subprocess renders with three distinct seeds
      identical to each other (`test_render_determinism.py` -
      5 tests).
  17. **Adversarial-input robustness**: unicode display names
      (CJK, RTL, accented, emoji), control characters and ANSI
      escapes in slugs and subdomains, 1000-char display names,
      200-slug and 200-attribution inputs, punycode IDN subdomains
      (`test_adversarial_render.py` - 13 tests). Threat model:
      data-quality robustness, not security boundary enforcement.
  18. **Cross-version cache compatibility**: synthesized v1.9.8-
      shape cache loads through v1.9.9 reader; new v1.9.9 surfaces
      derive from existing cache fields without re-collection;
      ``_CACHE_VERSION`` constant pinning prevents silent schema
      bumps (`test_cache_cross_version_compatibility.py` - 7 tests).
  19. **Render-time performance bounds**: typical (10 slugs), large
      (100), and stress (1000) inputs render under generous time
      budgets; ratio of large-input time to small-input time is
      sub-quadratic (`test_render_performance.py` - 8 tests; 1
      skip on machines too fast for a stable ratio).
  20. **Expanded mutation library**: 6 named mutations beyond the
      original 3 (stream swap, empty-string-vs-None contract,
      case-sensitivity invariant). All caught by the existing test
      suite (`test_mutation_resistance.py` - 15 tests total).
  21. **Three-way trigger differential agreement**: renderer +
      aggregator + regex-parser must agree on every fixture
      (`test_trigger_differential_agreement.py` - 6 tests).
      Breaks the two-implementation circularity by adding a third
      independent code path.
  22. **Catalog-driven Hypothesis property tests**: inputs drawn
      from the live fingerprint catalog rather than hand-curated
      fixtures (`test_catalog_driven_corpus.py` - 5 tests).
      Caught the `Data & Analytics` KeyError bug at first run.
  23. **Suite-wide humble-tone enforcement**: catalog descriptions
      and formatter top-level constants must avoid overclaim words
      (`test_humble_tone_global.py` - 4 tests). Caught the okta
      "strong" violation at first run.
- **Synthetic 19-fixture corpus** at
  `validation/synthetic_corpus/fixtures/` (M365+Okta, GWS+AWS,
  multi-cloud SaaS, hardened minimal, Azure-native, GCP-native,
  hybrid, healthcare, fintech, public-sector, media, education,
  Heroku legacy, SaaS-only, AWS-family-only). Generator at
  `validation/synthetic_corpus/generator.py` is deterministic and
  publicly-reproducible.
- **Corpus aggregator** at `validation/corpus_aggregator.py` emits
  anonymized firing statistics for both the estimator path and the
  authoritative render-based path. At release time the 19-fixture slice
  produced 8 multi-cloud and 11 ceiling firings. The tracked aggregate is now
  regenerated from the expanded 79-fixture reserved-identity corpus.
- **Render review** at `validation/synthetic_corpus/render_snapshots.md`
  now retains aggregate panel-shape counts only. Detailed panel text is
  generated under the gitignored agentic local directory.
- **Threshold sensitivity analysis** at
  `validation/threshold_sensitivity.md` sweeps each ceiling-trigger
  threshold across plausible values and reports the firing-rate
  shape. Makes the threshold choice falsifiable instead of intuitive.
- **Distinct-invariant audit** at `validation/invariant_audit.md`
  collapses the 182-test count to 51 distinct invariants and assigns
  each "what we honestly do not test" item a specific milestone
  (v1.9.10 for empirical corpus, cosmic-ray, Bayesian
  re-validation; v1.9.11 for agentic UX; post-v2.0 for memory
  bounds).
- **Coverage-gap audit** at `validation/coverage_gap_audit.md`
  categorizes the 1648 uncovered lines by risk surface (MCP server
  runtime is the largest gap; per-source error paths is the
  second-largest).
- **Performance baseline** at `validation/performance_baseline.md`
  records the actual measured render times (10 slugs: 0.9 ms,
  100 slugs: 1.5 ms, 1000 slugs: 9.2 ms) so the test budgets can
  be assessed against real numbers instead of intuition.
- **Agentic UX runbook** at
  `validation/agentic_ux_v199_runbook.md` documents the
  smallest-cost LLM invocation for the maintainer to validate
  agent-readability of the new surfaces against API-key-controlled
  cost (~$0.016 per focused run on Haiku 4.5).
- **`category_for_slug` public accessor** added to formatter.py
  for the corpus aggregator and threshold sensitivity script;
  removes the `_CATEGORY_BY_SLUG` private-import warning.
- Coverage at 84% total (89% on formatter.py, up from 83% pre-v1.9.9).
- ruff lint and ruff format clean across 205 files.
- pyright on `recon_tool/` and the validation tooling reports 0
  errors, 0 warnings, 0 informations.
- See `validation/v1.9.9-detection-gap-ux.md` for the per-fixture
  trigger behaviour notes and the test-quality manifesto.
- See `validation/v1.9.9-corpus-run.md` for the synthetic-corpus
  validation evidence.

### Scope notes

- The multi-apex CT SAN traversal item in the v1.9.9 roadmap section
  (pull subdomains from all observed apex certs rather than just the
  queried apex's) is deferred to v1.9.9.1. It touches external HTTP
  behaviour and warrants its own validation pass against the v1.9.4
  hardened corpus; bundling it with the three panel surfaces here
  would have obscured which change drove any behavioural shift in CT
  traversal. The wordlist additions ship in v1.9.9 because they are
  internal to the probe loop and the CT sort, with no observable change
  in HTTP request volume.
- The CT-by-org-name search hinted at in the same roadmap section
  carries the same external-HTTP rationale and likewise defers to
  v1.9.9.1 or later.
- No JSON schema changes ship: the rollup vendor list and the ceiling
  phrasing are panel-only. `tests/test_json_schema_file.py` would catch
  drift if a future patch ever surfaces either as a structured JSON
  field; that decision is explicitly out of scope here.

## [1.9.8] - 2026-05-13

**v1.9.8 bridge milestone: catalog metadata richness pass on top of
the v1.9.7 presence floor.** v1.9.7 lifted every detection to a
non-empty description; v1.9.8 lifts every detection to a
substantive, scope-narrowed, externally-referenced description.
After this pass every detection in every category satisfies all
three proxy signals of the new advisory richness audit
(`--report-richness`): description length, scope-narrowing language,
and external `reference` URL. No engine code changes ship in this
release.

This is the v1.9.8 step of the v1.9.4 to v2.0 linear sequence in
`docs/roadmap.md`.

### Headline numbers

| Metric | Before (v1.9.7) | After (v1.9.8) |
|---|---|---|
| Detections with `reference` URL | 76 of 566 (13.4%) | **566 of 566 (100%)** |
| Categories at 100% reference | 0 of 8 | **8 of 8** |
| Detections passing richness audit (all 3 signals) | partial | **566 of 566 (100%)** |
| Non-default weights with inline rationale | 0 of 4 | **4 of 4** |
| Richness audit (advisory) | not present | `--report-richness` flag |

### Added

- **`scripts/check_metadata_coverage.py --report-richness`.** Advisory
  pass that scores each description against three proxy signals:
  long-desc (length floor of 80 chars, proxies signal 1), scope-narrow
  (presence of scope-narrowing tokens, proxies signal 2), and
  `reference` (external URL). Detections failing two or more signals
  are surfaced as a per-category worklist. The audit never gates;
  presence-gate exit code is unchanged. The token set is tuned to the
  catalog's actual writing style: explicit-negation tokens (`not`,
  `does not`) plus the catalog idioms it uses to narrow scope
  (`alternative`, `legacy`, `functionally equivalent`, `typically
  paired`, `same semantics`, `cname through`, `chain through`,
  `subdomain cnames into`, `government cloud`, and similar).
- **Reference URLs on 490 detections** across every fingerprint file.
  Every detection in every category now points at a canonical vendor
  product or docs root (`help.okta.com/en-us/...`,
  `docs.aws.amazon.com/...`, `docs.github.com/en/organizations/...`),
  chosen to be stable enough for a future maintainer to re-verify the
  pattern without chasing rotted deep links.
- **Description-quality lift across the catalog.** Every short
  cname_target index entry in `surface.yaml` (the v1.9.3.x
  catalog-growth artifacts) was expanded into a proper three-signal
  description: what the slug detects, what the chain narrows to, and
  what it does not prove. Comparable lift in `ai.yaml` and
  `verticals.yaml`. Existing block-scalar descriptions in
  `security.yaml`, `email.yaml`, `productivity.yaml`,
  `crm-marketing.yaml`, and `data-analytics.yaml` were left alone
  where they already satisfied the rubric.
- **Inline weight rationale** on all four non-default weights in
  `security.yaml`: `ping-identity` `pingoneemail=` TXT (0.6),
  `cyberark` `*.idaptive.{com,app}` CNAME (0.7), `sonatype`
  `^OSSRH-\d+$` TXT (0.8), `beyond-identity`
  `authenticator.beyondidentity.com` CNAME (0.5). Comment lives above
  the `weight:` key in each detection block.
- **`validation/v1.9.8-metadata-audit.md`** documenting the pass:
  before/after reference coverage, end-state richness numbers per
  category, weight-rationale table, scope and non-goals.

### Changed

- **`CONTRIBUTING.md` "Detection description rubric".** Stale
  "v1.9.7+" pointer on the advisory metadata-richness reference
  updated to "v1.9.8+ advisory" so contributors land on
  `--report-richness`.

### Fixed

- **`recon_tool/http.py`** `asynccontextmanager` deprecation warning
  surfaced by a recent pyright/typeshed update. Annotation switched
  from `AsyncIterator` to `AsyncGenerator` per the typeshed change;
  no runtime behavior difference.
- **`tests/test_mcp_path_isolation.py`** subprocess.run call now
  carries the `# noqa: S603 - argv list, no shell.` annotation
  matching the pattern in `tests/test_metadata_coverage.py` and
  `scripts/release.py`.

### Scope

In scope:
- Full description-quality lift across the catalog.
- Full `reference` URL coverage across the catalog.
- Inline rationale on every non-default weight.
- `--report-richness` advisory mode in
  `scripts/check_metadata_coverage.py`.
- Rubric pointer cleanup in `CONTRIBUTING.md`.

Out of scope (stays out by design):
- Engine changes (`signals.py`, `merger.py`, `absence.py`,
  `fusion.py`) - v1.9.8 is data + tooling only.
- New fingerprints - v1.9.8 does not add or remove detections.

### Quality gate

`ruff check`, `pyright`, `pytest`,
`scripts/validate_fingerprint.py` (414 entries passed),
`scripts/check_metadata_coverage.py` (PASS, every detection in every
category has a non-empty description, and every detection satisfies
all three richness signals), and all pre-commit hooks pass on a clean
tree.

## [1.9.7] - 2026-05-13

**v1.9.7 bridge milestone: metadata-coverage gate flip (presence,
not coverage) plus full catalog backfill.** The v1.9.0 advisory
gate measured description coverage as a percentage with a 70
percent threshold on three "gated" categories (identity, security,
infrastructure). That framing invited gate-gaming: writing
placeholder descriptions to clear a percentage rather than
explaining what each detection claims. v1.9.7 replaces the
percentage with a presence check, gates every category, and
backfills the full 298-detection gap so the gate ships enforcing
on a clean tree.

This is the v1.9.7 step of the v1.9.4 to v2.0 linear sequence in
`docs/roadmap.md`. The deliverable is the gate flip, the backfill,
the per-detection gap reporting, the pre-commit hook, and the
description rubric in CONTRIBUTING.md.

### Headline numbers

| Metric | Before (v1.9.6) | After (v1.9.7) |
|---|---|---|
| Total detections | 566 | 566 |
| Detections with description | 268 (47 percent) | **566 (100 percent)** |
| Gated categories | 3 (identity, security, infrastructure) | **all 8** |
| Gate type | percentage threshold (70 percent) | **presence (every detection)** |
| CI behavior | advisory (`--report-only` in ci.yml) | **enforcing in CI and release.yml** |

Backfill per category:

| Category | Before | After | Added |
|---|---|---|---|
| ai | 100 percent | 100 percent | 0 |
| crm-marketing | 32 percent | 100 percent | 32 |
| data-analytics | 0 percent | 100 percent | 13 |
| email | 46 percent | 100 percent | 20 |
| infrastructure | 56 percent | 100 percent | 146 |
| productivity | 9 percent | 100 percent | 41 |
| security | 31 percent | 100 percent | 44 |
| verticals | 89 percent | 100 percent | 2 |
| **total** | **268** | **566** | **+298** |

### Added

- **`CONTRIBUTING.md` "Detection description rubric (v1.9.7+)"
  section.** Three-part rubric: (a) what the slug detects, (b)
  what it does not detect, (c) common false positives if known.
  Plus tone guidance (humble, no overclaim, no em-dashes) and
  two worked examples (good vs placeholder). Sets the bar for
  new contributions; reviewer judgement is the enforcer.
- **`.pre-commit-config.yaml` metadata-coverage hook.** Fires
  the presence gate locally before push when any
  `recon_tool/data/fingerprints/*.yaml` is touched. Catches
  missing descriptions in the developer loop rather than in CI.
- **Per-detection gap reporting in `scripts/check_metadata_coverage.py`.**
  On failure the script emits the exact slug + detection-rule
  pairs missing a description, grouped by category, so a
  contributor sees "fix these N entries" rather than "your
  category coverage dropped to 87 percent."

### Changed

- **`scripts/check_metadata_coverage.py`: presence gate replaces
  percentage threshold.** Dropped `--threshold` and
  `_DEFAULT_THRESHOLD = 0.70`; dropped the `_GATED_CATEGORIES`
  allowlist. Every category gates; every detection must carry a
  non-empty `description`. Reference and weight coverage remain
  advisory diagnostics, not gating.
- **`.github/workflows/ci.yml`: metadata-coverage step is now
  enforcing.** Removed `--report-only` from the metadata-coverage
  invocation. CI fails the build when any detection is missing a
  description.
- **`.github/workflows/release.yml` runs the metadata-coverage
  gate.** Added to the `test` job, mirroring `ci.yml`. Prevents
  a catalog regression from reaching PyPI just because the
  tests passed.
- **All 298 backfilled descriptions follow the rubric.**
  Vendor-specific text covers what the pattern matches, what
  inference the slug supports, common false positives where
  known, and acquisition / rebrand history where it affects
  reading the slug name (for example, Pardot is now Salesforce
  Marketing Cloud Account Engagement; Auth0 is an Okta property
  since 2021; SignalFx is sold as Splunk Observability Cloud).

### Notable findings from the backfill

- **The "infrastructure" category is the bulk of the catalog.**
  332 of 566 detections (59 percent) live in
  `infrastructure.yaml` and `surface.yaml` (CNAME-target rules
  for the surface-attribution pipeline). The detection patterns
  there map to CDNs, cloud-provider endpoints, hosted-app
  platforms, and DNS providers; descriptions document both the
  vendor and the specific surface the pattern fires on (apex
  delegation, edge proxying, branded-subdomain hosting, regional
  endpoints, and so on).
- **Many detections cover legacy vendor domains.** The catalog
  carries CNAMEs for products whose vendor was acquired and
  rebranded but whose hostnames persist (ExactTarget for
  Salesforce Marketing Cloud, Mandrill for Mailchimp
  Transactional, FireEye for Trellix, Idaptive for CyberArk
  Identity, Wildbit for Postmark, and similar cases). Each
  description notes the rebrand so the reader does not chase a
  vendor name that no longer markets under that brand.
- **Pure deliverability signals are not enforcement signals.**
  Echoing the v1.9.6 `email_security_policy_enforcing` lesson,
  several email-vendor descriptions explicitly note that SPF
  includes authorize outbound sending only and do not imply
  inbound mail handling. The rubric's "what it does not detect"
  framing surfaces this consistently across the catalog.

### Real-company-data discipline

The backfill describes vendor products and the specific evidence
patterns recon matches against. No real-organization names appear
in descriptions. Acquisition and rebrand history is sourced from
publicly available vendor announcements and does not reveal
customer identities.

### Quality bar verification

- [x] Per-category gap report on failure: the script prints
  every slug + detection-rule pair that lacks a description,
  grouped by category, so a contributor sees "fix these N
  entries" not "coverage dropped to 87 percent."
- [x] Pre-commit hook entry added to `.pre-commit-config.yaml`
  scoped to fingerprint YAML changes; the gate fires locally
  before push.
- [x] "What good looks like" rubric in `CONTRIBUTING.md` with
  two worked examples (good vs placeholder).
- [x] Backfill before flip: zero detections missing
  descriptions in any category before the gate flipped from
  advisory to enforcing. The flip is in the same release as
  the backfill, but the backfill is committed before the
  workflow-file edits.
- [x] Reference-presence reporting remains advisory. Reference
  coverage stays low (22.9 percent on infrastructure, lower
  elsewhere); the rubric notes reference URLs are nice to have
  but harder to source defensively, so they do not gate.

### Tests

- Total: 2314 passed, 1 skipped, 4 deselected (unchanged test
  count, the v1.9.7 change is a data and gate edit).
- Coverage: 83.4 percent (above the 80 percent gate, unchanged).
- ruff, pyright, pre-commit (including the new metadata-coverage
  hook), and the fingerprint validator all clean.

### Roadmap

- v1.9.7 bridge milestone **closed**.
- Next in sequence: v1.9.8 (catalog metadata richness pass) and
  v1.9.9 (detection-gap UX surfaces).
- New post-v2.0 backlog item added: machine-readable CLI surface
  inventory for downstream skill and agent authors. See
  `docs/roadmap.md` Backlog "Machine-readable CLI surface
  inventory" for the rationale (improve recon's surface
  inventory; leave agent-behavior layer to skill files).

## [1.9.6] - 2026-05-13

**v1.9.6 bridge milestone - CPT-change discipline (concept, not
parameter).** Ships the discipline that distinguishes "the corpus
disagrees, so the number must be wrong" (corpus-fitting, prohibited)
from "the corpus disagrees, so the topology must be asking the wrong
question" (concept-driven, the right cycle). Bundles the first
canonical application: the v1.9.5 `email_security_policy_enforcing`
"not yet" disposition closes by removing `dkim_present` as an
evidence binding - DKIM publication is a deliverability hygiene
signal, not a policy-enforcement signal.

This is the v1.9.6 step of the v1.9.4 → v2.0 linear sequence in
`docs/roadmap.md`. Deliverables: the discipline in `CONTRIBUTING.md`,
a PR-template prompt that surfaces the discipline at review time,
the audit confirmation that no automated CPT-fitting tooling has
emerged, the `policy_enforcing` redefinition with its concept
comment in the YAML, the stability-update delta report, and the
audit-resolution document closing four external-audit findings.

### Headline verdict change

`email_security_policy_enforcing` v1.9.5 `not yet` → v1.9.6
**stable**. Binary criterion (b1) goes from 119/129 to 119/119;
criterion (b2) eligible set grows by 10 as the dkim-only domains
correctly move to det-silent + sparse. Total stability verdict count:
**8 stable, 1 not yet** (`okta_idp`, unchanged - corpus-limited).

### Added

- **`CONTRIBUTING.md` "CPT-change discipline (v1.9.6+)" section.**
  Worked examples (v1.9.3 surgery on `email_security_strong`; v1.9.6
  surgery on `email_security_policy_enforcing`), anti-pattern catalog
  (4 reviewer rejection examples), decision tree, and the concept-
  comment requirement. Stays terse; the rubric makes future
  contributors pause before number-driven CPT changes.
- **`.github/pull_request_template.md`** - new root-level default PR
  template (the existing `PULL_REQUEST_TEMPLATE/fingerprint.md` is
  preserved for fingerprint-only PRs via the `?template=` URL
  parameter). Carries the CPT-change-discipline non-blocking
  checkbox plus the fingerprint, no-real-company-data, and
  no-attribution-trailer reviewer prompts. The checkbox is the
  conversation starter, not a CI gate - reviewer judgement is the
  enforcement.
- **`validation/v1.9.6-stability-update.md`** - short delta report
  against `v1.9.5-stability.md`, showing the per-metric movement on
  `email_security_policy_enforcing` and confirming all other nodes'
  verdicts unchanged. Includes "what this does not validate" notes.
- **`docs/security-audit-resolutions.md`** - closure record for
  external audit findings. Keyed by *topic* rather than vendor-
  specific ID so the record is portable across audit tools. Four
  initial entries closing (HIGH) MCP doctor/install shadow-load via
  v1.9.3.4, (MEDIUM) A/AAAA CNAME validation leak via v1.9.4,
  (MEDIUM) original CNAME chain walking via v1.9.3.5+v1.9.4
  mitigation, (INFORMATIONAL) Splunk regex-slug example via v1.9.4.
  Each entry cites the closure commit SHA, the pinning test, and a
  file:line receipt against current code. SECURITY.md gets a
  forward pointer.

### Changed - engine

- **`recon_tool/data/bayesian_network.yaml`:
  `email_security_policy_enforcing` evidence list shrinks from 5
  bindings to 4.** Removed `signal: dkim_present` (was
  `likelihood: [0.85, 0.30]`). Concept comment in the YAML cites the
  v1.9.5 stability report finding (10/129 b1 failures, all
  `evidence_used = (signal:dkim_present,)` alone, producing posterior
  ≈ 0.486 from a single weak-LR signal) and explains why the right
  fix is binding removal rather than likelihood retuning:

  > "The corpus-fitting reflex was to lower the likelihood for the
  > absent case from 0.30 to 0.20, lifting the dkim-only posterior
  > to 0.59. That would have improved the criterion number while
  > making the node a worse predictor of what its name says. The
  > right answer was removing the binding - the node's claim is
  > enforcement, and DKIM doesn't speak to enforcement."

  Node description also tightened: "Observable email-authentication
  policy is enforcing (DMARC reject/quarantine + strict SPF +
  optional MTA-STS enforce)." - removed "+ DKIM" since DKIM is no
  longer evidence.

- **`tests/test_node_stability_criteria.py`:
  `email_security_policy_enforcing` binding list mirrored** - the
  parametrized test's directory must stay in sync with the YAML so
  the directory-completeness sanity check passes. Inline comment in
  the test file cross-references the YAML concept comment.

### Notable findings

- **The redefinition improves the layer's honesty, not just the
  criterion number.** The 10 dkim-only domains in the v1.9.5
  corpus genuinely don't have an enforcing posture (DKIM alone,
  no DMARC, no MTA-STS, no strict SPF). The v1.9.5 layer reported
  them with posterior ≈ 0.486 and non-sparse - confidently
  uncertain, in a way that hurts the (b1) criterion. The v1.9.6
  layer reports them sparse=true with no firings - explicitly
  hedged. Both criterion (b1) and the layer's truthfulness
  improve simultaneously.
- **Diagnostic ECE rises slightly (0.128 → 0.154) - this is a
  numerator artifact, not a regression.** Removing 10
  well-classified non-sparse observations from a small eligible
  set raises per-bin variance. Brier improves (0.0346 → 0.0331).
  Both numbers stay comfortably below the 0.20 / 0.15 advisory
  thresholds. The headline verdict change (not yet → stable) is
  driven by the (b1) binary criterion, not by these diagnostics.
- **Audit-finding closure documentation pattern.** The
  `docs/security-audit-resolutions.md` file is keyed by topic
  rather than audit-tool ID so it stays portable. Scanners that
  re-flag a closed finding (because they trace introduction
  commits but not subsequent fix commits) get authoritatively
  answered by the file. Closure precedence is documented in the
  file's process-notes footer.

### Real-company-data discipline

- Reuses the v1.9.4 / v1.9.5 corpus; no new corpus runs needed for
  the engine-isolated re-inference. The re-inference uses saved
  evidence (slugs + signals) from the gitignored NDJSON, so the
  v1.9.6 stability comparison is fully isolated from upstream DNS
  drift.
- `docs/security-audit-resolutions.md` uses generic placeholder
  hostnames (`internal.example`, `attacker.example`) - no real
  internal infrastructure of any organization, consistent with the
  project's no-real-company-data policy.

### Quality bar verification

- [x] **Worked example in CONTRIBUTING.md** - v1.9.3 surgery is the
  historical case; v1.9.6 surgery on `policy_enforcing` is the
  live case shipping in this release.
- [x] **PR-template addition** - non-blocking CPT-change-discipline
  checkbox added to a new root-level
  `.github/pull_request_template.md`.
- [x] **Anti-pattern catalog** - four worked reviewer rejections in
  `CONTRIBUTING.md` (corpus-rate tuning without concept comment,
  ECE-driven likelihood adjustment, priors-override
  miscalibration patch, automated CPT fitting).
- [x] **No automated CPT-fitting tooling** - confirmed by grep for
  `def (learn_cpt|fit_cpt|auto_tune|optimize_cpt|empirical_bayes|
  fit_likelihood|tune_likelihood)` across the repo (zero matches)
  and for write-paths against `bayesian_network.yaml` (zero
  matches). The audit IS the discipline, not a CI test.

### Tests

- Total: 2314 passed, 1 skipped, 4 deselected (unchanged test count
  - the v1.9.6 fix is a data-file change; the criterion-(a) test's
  binding directory updates without adding new tests).
- Coverage: 83.43% (≥ 80% gate, unchanged).
- ruff + pyright clean on `recon_tool/` + `tests/` + `validation/`.
- pre-commit (ruff, ruff-format, pyright, actionlint) clean.
- `validate_fingerprint.py` 414/414.

### Roadmap

- v1.9.6 bridge milestone **closed**.
- Next in sequence: v1.9.7 (metadata-coverage gate flip - replace
  the percentage threshold with a binary "every detection in
  identity/security/infrastructure has a non-empty description"
  presence check; flip from advisory to enforcing once backfill
  reaches zero).

## [1.9.5] - 2026-05-13

**v1.9.5 bridge milestone - per-node stability dispositions for the
v1.9 Bayesian layer.** Decides, does not ship, per-node stability
criteria for the 9-node v1.9.3+ topology. The atomic EXPERIMENTAL
label that covered the whole `--fusion` layer through v1.9.4 was
over-broad: `m365_tenant` and `email_security_policy_enforcing`
should not share a label. v1.9.5 produces an explicit per-node
verdict against three behavioral criteria; v2.0 ships with that
disposition table baked into the network as committed, without a
`stability` schema field. The field itself enters the schema the
first time a post-v2.0 patch introduces a node that does not
immediately qualify as `stable`.

This is the v1.9.5 step of the v1.9.4 → v2.0 linear sequence in
`docs/roadmap.md`. The deliverable is the verdict report, the
parametrized regression test, and the disposition decisions - no
engine changes, no schema changes, one new validation script and
one new test file.

### Headline verdict

| Verdict | Count | Nodes |
|---|---|---|
| **stable** | 7 | `m365_tenant`, `google_workspace_tenant`, `federated_identity`, `email_gateway_present`, `email_security_modern_provider`, `cdn_fronting`, `aws_hosting` |
| **not yet** | 2 | `okta_idp` (criterion (c) - only 7 firings on the 141-domain combined corpus, threshold 10), `email_security_policy_enforcing` (criterion (b1) - 10 of 129 det-positive-HIGH non-sparse observations have posterior ≤ 0.5, all driven by `signal:dkim_present` alone) |

Both `not yet` nodes carry explicit dispositions in
`validation/v1.9.5-stability.md`. Neither disposition is *Split*
or *Remove*; both stay in the network as v2.0 ships.

### Added

- **`validation/v1.9.5-stability.md`** - full per-node verdict
  report: methodology, per-node table joining the (a) test result
  with the (b1)(b2)(c) analyzer outputs, prose interpretation for
  each `stable` cluster, and explicit dispositions for the two
  `not yet` nodes (`okta_idp`: keep, expand corpus;
  `email_security_policy_enforcing`: redefine in v1.9.6 with a
  CPT-change-discipline concept comment, choosing among raising
  the prior, widening the sparse threshold, or tightening the
  weak-likelihood signals). Anonymized aggregates only; no
  per-domain detail.
- **`validation/compute_node_stability.py`** - analyzer for
  criterion (b) and (c). Reads the v1.9.4 hardened + soft NDJSON,
  computes per-node firing count, (b1) ratio (det-positive-HIGH
  non-sparse → posterior > 0.5), (b2) ratio (det-silent → sparse),
  Brier score, log-score, and 10-bin ECE. Filters slug bindings by
  deterministic high-confidence threshold (≥ 0.70); signal
  bindings are binary. Pure-propagation nodes have criterion (c)
  marked `n/a`. Output is publicly-reproducible from the corpus
  NDJSON.
- **`tests/test_node_stability_criteria.py`** - parametrized
  regression test for criterion (a) (evidence-response
  correctness). 20 assertions covering all 9 nodes:
  bound-evidence sensitivity (any evidence binding raises the
  node's posterior by ≥ 0.01 from baseline) and unrelated-evidence
  inertia (a d-separated binding leaves the posterior at baseline
  within 1e-9). Pure-propagation nodes
  (`email_security_modern_provider`) get the bound-evidence test
  via each parent's evidence - the CPT must propagate. Plus two
  sanity tests pinning root-baseline = prior and directory
  completeness against the shipped network. The test failing is
  a regression signal that future patches must satisfy before
  reaching a release tag.

### Notable findings

- **`email_security_policy_enforcing` (b1) failure is exactly
  one pattern, 10 times.** Every one of the 10 failing
  observations has `evidence_used = ('signal:dkim_present',)`
  and nothing else. With prior 0.25 and likelihood [0.85, 0.30],
  the resulting posterior is ≈ 0.486 - just below the 0.5
  threshold. The n_eff threshold for sparse is satisfied by the
  single binding, so the layer doesn't hedge either. This is the
  exact calibration gap v1.9.6's CPT-change discipline exists to
  address: the disagreement is the *signal*, not the fix; the
  right question is which conceptual claim
  `policy_enforcing` is making (target population for prior,
  evidence requirement for non-sparse, or weak-likelihood
  meaning).
- **`okta_idp` firing count is corpus-limited, not engine-limited.**
  All other criteria pass cleanly (b1=7/7, b2=134/134, Brier
  0.022, ECE 0.144). Okta's public DNS fingerprint is thin; many
  Okta-using orgs don't surface the `okta` slug. The disposition
  is to keep the node and expand the validation corpus, not
  change the engine.
- **Pure-propagation node criterion-(c) handling.**
  `email_security_modern_provider` has no direct evidence
  bindings by design - provider presence is captured entirely
  through CPT propagation from `m365_tenant`,
  `google_workspace_tenant`, and `email_gateway_present`. The
  analyzer marks (c) `n/a` for this node and gates stability on
  (a) and (b) only. The (a) test exercises propagation from each
  of the three parents; all three propagate correctly.
- **Diagnostic calibration metrics are uniformly within
  threshold.** Every node's ECE is ≤ 0.144 (threshold 0.20) and
  Brier is ≤ 0.0346 (threshold 0.15). The criterion-(b) failure
  for `policy_enforcing` is a binary-check failure, not a
  calibration-error failure; the layer is well-calibrated overall
  but fails the strict "det-positive HIGH ⇒ posterior > 0.5" gate
  on the dkim-only pattern.

### Real-company-data discipline

The 141-domain corpus reuses v1.9.4's stratified samples (50
hardened-adversarial across five postures + 91 soft v1.9.0
calibration domains). Per the project's no-real-company-data
policy:

- Corpus files (`v1.9.4-hardened.txt`, `v1.9.0-soft.txt`) and
  NDJSON results are gitignored.
- `validation/v1.9.5-stability.md` carries only per-node
  aggregates - no per-organization detail.
- The analyzer (`validation/compute_node_stability.py`)
  anonymizes by design; no domain names print to stdout.
- The criterion-(a) test uses no corpus data - it operates on
  synthetic inputs against the shipped network.

### Quality bar verification

- [x] Per-node verdict table in `validation/v1.9.5-stability.md`
  (one row per node, three columns plus diagnostics; pass requires
  all three).
- [x] Numeric backing for criterion (b): per-node Brier score,
  log-score, ECE on the v1.9.4 corpus, with ECE ≤ 0.20 and Brier
  ≤ 0.15 thresholds documented (advisory; not gating).
- [x] Independent-firing threshold (c) explicit: N ≥ 10 from
  roadmap §v1.9.5; per-node firing count from the v1.9.4 corpus,
  not a self-report.
- [x] Criterion-(a) test in code as parametrized pytest test -
  20 assertions covering both directions (bound-evidence raises,
  unrelated-evidence inert) across all 9 nodes plus 2 sanity
  tests.
- [x] `not yet` verdicts route to specific dispositions before
  v2.0: `okta_idp` → keep + corpus expansion; `policy_enforcing`
  → redefine in v1.9.6 with a CPT-change-discipline concept
  comment.
- [x] No fast-tracking on numbers alone: `okta_idp` has excellent
  (b) numbers but fails (c) and remains `not yet`. The threshold
  is *all three*.

### Tests

- Total: 2314 passed, 1 skipped, 4 deselected (v1.9.4 → v1.9.5:
  +20 tests from the new `test_node_stability_criteria.py`).
- Coverage: 83.43% (≥ 80% gate, unchanged).
- ruff + pyright clean on `recon_tool/` + `tests/`.
- pre-commit (ruff, ruff-format, pyright, actionlint) clean.
- `validate_fingerprint.py` 414/414.

### Roadmap

- v1.9.5 bridge milestone **closed**.
- Next in sequence: v1.9.6 (CPT-change discipline) - the
  `email_security_policy_enforcing` disposition routes directly
  into v1.9.6's milestone scope: pick one of the three candidate
  changes (raise prior / widen sparse threshold / tighten weak
  likelihoods), document the concept in
  `bayesian_network.yaml`, and re-run this stability report to
  confirm (b1) reaches 129/129.

## [1.9.4] - 2026-05-12

**v1.9.4 bridge milestone - hardened-adversarial behavior validation.**
Validates the **design property** behind the v1.9 asymmetric-
likelihood Bayesian layer (`docs/correlation.md` §4.3): on
minimal-DNS / wildcard-cert / heavily-fronted apexes, the layer
must hedge - flagging `sparse=true`, reporting wide credible
intervals, and refusing to assert high-confidence posteriors on
evidence-binding-silent nodes. The corpus stratifies across five
hardening postures (heavy edge-proxied, privacy-focused, major
financial, defense / national-security, major government).

This is the v1.9.4 step of the v1.9.4 → v2.0 linear sequence in
`docs/roadmap.md`. The deliverable is the validation report and
the failure-mode catalog in `correlation.md` - no engine or
schema changes.

### Headline result

| Metric | Result |
|---|---|
| Spot-check agreement on high-confidence posteriors | **100%** (157/157 non-sparse) |
| Overall sparse-flag rate (hardened) | **64.0%** (288/450 observations) |
| Multi-signal correlation depth (hardened) | 92.0% (46/50 domains have ≥ 2 firings) |
| Cross-source conflicts | 0 / 50 |
| Soft-corpus regression check | -17 high-confidence posteriors v1.9.0 → v1.9.3+ topology, fully accounted for by the `email_security_strong` split |

The asymmetric-likelihood design property holds. The layer
hedges on hardened targets without over-claiming.

### Added

- **`validation/v1.9.4-calibration.md`** - full calibration
  report: per-node sparse-rate trend (v1.9.0 → v1.9.3+ →
  v1.9.4-hardened), high-confidence survival ratios (soft →
  hardened), per-category breakdown across five hardening postures,
  soft-corpus regression tripwire, defensive value interpretation,
  reproducibility instructions. Anonymized aggregates only; no
  per-domain detail.
- **`validation/analyze_v19_4_hardened.py`** - analyzer for the
  trend, survival-ratio, and per-category aggregates from the
  hardened + soft-current + soft-original NDJSON runs. Output is
  publicly-reproducible (no proprietary data).
- **`docs/correlation.md` §4.10 - Failure-mode catalog:
  hardening pattern fingerprints.** Documents the distinctive
  sparse-rate fingerprint each hardening pattern produces at the
  Bayesian layer, with per-pattern defensive read. Patterns
  (edge-proxied, privacy-focused, financial, defense, government)
  carry no per-organization detail. Cross-references the v1.9.4
  calibration report's data.
- **Family-of-companies / portfolio rollup workflow in
  `AGENTS.md` and `agents/claude-code/skills/recon/SKILL.md`.**
  Agent guidance for synthesizing a unified report across an
  operator-supplied set of related apexes (parent + subsidiaries,
  M&A brand portfolio, holding-company structure). The operator
  owns the relationship - recon never infers ownership. Five
  rollup axes: identity stack consistency, email gateway
  consistency, cloud footprint overlap, posture divergence
  (the highest-signal output - outlier siblings are the
  actionable finding), and per-brand notable findings.
  Lightweight agent-side precursor to the heavier
  `recon batch --self-audit` Python rollup in
  `docs/roadmap.md` backlog; ships first because validating
  the report shape on real workflows is cheaper at the skill
  layer than in committed schema.

### Notable findings

- **`email_gateway_present` high-confidence survival ratio = 0.57**
  (soft → hardened). The cleanest demonstration of the asymmetric-
  likelihood design property: hardened orgs do not surface
  Proofpoint / Mimecast / Barracuda MX records publicly, and the
  Bayesian layer correctly retreats rather than over-claiming.
- **`cdn_fronting` high-confidence survival = 0.84** with 60%
  hardened high-conf: CDN-fronting is part of the hardening
  posture, not hidden by it. The layer correctly fires on the
  visible front while reporting everything behind it as sparse.
- **`email_security_policy_enforcing` survival = 0.98**: DMARC
  policy is a public TXT record that defenders publish regardless
  of other hardening. Fires routinely; no posture hides this.
- **Two hardening categories (financial, government) produce an
  identical signature** from the Bayesian layer's perspective -
  "M365 + CDN-fronted + strong DMARC, everything else sparse" -
  even though their internal stacks differ. The layer cannot
  distinguish posture from posture when both apply the same
  public-DNS hygiene.

### Notes on no-regression

The v1.9.0 91-domain soft corpus was re-run on the current
(v1.9.3+) topology and compared against the original v1.9.0
results. All non-`email_security_strong` nodes have sparse rates
within 1-2 percentage points across both runs (within sampling
noise). The 17-posterior reduction in high-confidence count is
fully accounted for by the v1.9.3 `email_security_strong` split:
the original node (78 high-conf at 52.6% deterministic agreement,
the calibration weak spot v1.9.3 fixed) became `modern_provider`
(0 high-conf, always sparse - by design) + `policy_enforcing`
(62 high-conf at 100% agreement). No node had its calibration
*degraded* by the topology surgery.

### Real-company-data discipline

The hardened-adversarial corpus uses real organization apexes
sampled across five categories of public-DNS hardening posture.
Per the project's no-real-company-data policy:

- The corpus file (`validation/corpus-private/v1.9.4-hardened.txt`)
  is gitignored. Real apex names never appear in committed files.
- The NDJSON results file
  (`validation/corpus-private/v1.9.4-hardened/results.ndjson`) is
  gitignored.
- The calibration report (`validation/v1.9.4-calibration.md`) and
  failure-mode catalog (`docs/correlation.md` §4.10) carry only
  category-level aggregates: per-pattern sparse rates, per-pattern
  defensive reads. No per-organization detail.
- The analyzer script
  (`validation/analyze_v19_4_hardened.py`) anonymizes by design;
  no domain names print to stdout.

### Quality bar verification

- [x] Hardened corpus has explicit inclusion criteria documented at
  the top of the corpus file (5 criteria, qualify on ≥ 3).
- [x] Full v1.9.0 91-domain corpus re-run against the v1.9.3 topology
  alongside the hardened subset.
- [x] Per-hardening-pattern result rows in the failure-mode catalog
  (5 categories, each with per-node sparse rate + defensive read).
- [x] Survival rate quantified per node (high-conf% hardened /
  high-conf% soft).
- [x] No regression on the soft corpus (sparse rates within
  sampling noise on every node that exists in both topologies).
- [x] Failure-mode catalog cross-referenced to defensive guidance
  per category.
- [x] Reproducibility section in `validation/v1.9.4-calibration.md`
  documents the corpus-build methodology and the analyzer invocation.

### Tests

- 2294 passed, 1 skipped, 4 deselected (the dns.py walker security
  fix and SIEM regex-slug fix added new pinning tests; net +5
  versus v1.9.3.10).
- Coverage 83.43% (≥ 80% gate, unchanged).
- ruff + pyright clean on `recon_tool/` + `tests/`.
- Local `validate_fingerprint.py` passes 414/414.
- Local pytest passes including the v1.9.3.10 panel tests against
  the new corpus data.
- **Property-test strategy tightened in
  `tests/test_exposure.py`.** The Hypothesis strategy for
  `EvidenceRecord.raw_value` previously used an over-permissive
  alphabet (Unicode `L|N|P` categories), allowing draws like the
  literal English word ``"should"`` - which is in
  `EXPOSURE_DISCOURAGED_COPY_TERMS`. The Property-8 neutral-copy
  test then walked every string field of the exposure assessment,
  including the *echoed* evidence value, and the natural-English
  token spuriously failed a check that exists to validate
  *recon-authored* prose. Strategy now uses a DNS-realistic
  alphabet (alphanumerics + ``. - _ = ; : / @``) and filters out
  any draw containing a discouraged-copy term. The fix narrows the
  strategy toward realistic DNS record content; genuine coverage of
  the discouraged-term gate is unaffected because the test's true
  surface - recon-authored prose - was never the source of the
  failure.

### Security fixes (bundled with the v1.9.4 validation milestone)

The hardened-adversarial validation surfaced two audit findings
already in flight. Bundling the fixes with v1.9.4 keeps the
security work attached to the validation that motivated it.

#### CNAME chain walker: A/AAAA internal-DNS leak (audit finding, MEDIUM)

The v1.9.3.5 fix added a resolved-address private-IP check
(`_hop_resolves_publicly`) called by `_resolve_cname_chain` after
the suffix denylist. A subsequent security audit established that
this call sequence creates an internal-DNS oracle: invoking A/AAAA
on an attacker-influenced target causes the recursive resolver to
chase deeper CNAMEs *while answering the address query*,
potentially querying private/internal names *before* the explicit
walker has applied its suffix denylist to those deeper hops. That
is the original CNAME-chain-leakage vulnerability the chain walker
was supposed to prevent.

**Fix:** removed the inline A/AAAA call from
`_resolve_cname_chain`. The walker now uses **suffix-only**
defense - every hop's name is validated against the private-suffix
denylist, but no A/AAAA queries are issued during the walk. CNAME
queries do not cause recursive resolvers to chase further records,
making them the safe primitive for attacker-influenced names.

**Cost:** the split-horizon protection that v1.9.3.5 added (where a
public-suffix name resolves to private IPs via split-horizon DNS)
is no longer in place. The suffix denylist alone is the primary
defense. A future patch may add a terminus-only A/AAAA check
(resolve A/AAAA only after the entire chain has been suffix-
validated, and only on the last hop) if the split-horizon attack
pattern proves common enough to warrant the bounded leak risk.
v1.9.4 errs on the side of zero internal-DNS leakage.

**Tests:** `tests/test_cname_chain_validation.py::TestResolveCnameChainBlocksPrivateTargets::test_walker_does_not_resolve_a_aaaa_during_walk`
pins the v1.9.4 security invariant by tracking every DNS query
the walker issues and asserting only `CNAME` queries fire - never
`A` or `AAAA`. Future regression that re-introduces inline A/AAAA
fails this test before it can reach a release tag. The
`_hop_resolves_publicly` helper is preserved for callers who already
know the name is trusted (no current callers); the function-level
docstring documents the constraint.

#### Splunk SIEM example: unescaped regex slugs (audit finding, INFORMATIONAL)

The v1.9.3.8 shadow-IT alert example used
`match(current_slugs, mvjoin(baseline_slugs, "|"))`, which treats
every baseline slug value as a regex alternation. A baseline slug
containing regex metacharacters such as `.*` would match any
current slug and silently suppress the shadow-IT alert.

**Fix:** switched to `mvfilter(NOT in(current_slugs, baseline_slugs))`
in both `examples/siem/splunk/savedsearches.conf` and the README's
copy-pasteable SPL snippet. `in()` performs literal set-membership;
slug values are never interpreted as regex.

**Tests:** `tests/test_siem_examples.py::TestSplunkSearchSafety`
pins the safe pattern (3 tests covering the conf, the README, and
absence-of-unsafe-pattern in executable SPL). Future regression
that reverts to the unsafe form fails this test.

#### MCP doctor/install path isolation (audit finding, HIGH - already fixed)

The audit also flagged the v1.9.2.1 MCP doctor/install code path
that called `python -m recon_tool.server` with inherited cwd/env,
allowing a workspace-shadow attack. **This finding was already
closed in v1.9.3.4** (see v1.9.3.4 CHANGELOG entry): `mcp_doctor.py`
spawns the subprocess with an empty `tempfile.TemporaryDirectory`
cwd + `PYTHONSAFEPATH=1` env; `mcp_install.py` persists
`PYTHONSAFEPATH=1` in the fallback launch block + warns operators
when the fallback is used; `recon_tool/server.py` carries a
runtime guard that refuses cwd-shadow loads. Audit replays the
original finding against pre-v1.9.3.4 code; no further action
required.

### Housekeeping (bundled with v1.9.4)

Pre-commit's `ruff` + `ruff-format` surfaced drift unrelated to
the validation milestone but accumulated since the project's last
broad format pass. Bundled here so the v1.9.4 commit lands on a
clean tree rather than carrying the drift forward into v1.9.5.

- **`.pre-commit-config.yaml` ruff hook args fixed.** The hook
  was configured with `args: [check, --fix]`, but
  `astral-sh/ruff-pre-commit@v0.11.6` already invokes
  `ruff check` from the hook entry. The duplicate `check`
  was parsed as a filename, producing
  `E902 The system cannot find the file specified` on every
  run. Reduced args to `[--fix]`.
- **64 files reformatted by `ruff-format`** - line-ending
  normalization (Windows working-copy LF/CRLF drift) plus minor
  whitespace cleanups. No behavioral changes; the diffs are
  whitespace-only.
- **12 `UP038` / `S603` lint fixes** applied across
  `recon_tool/bayesian.py`, `recon_tool/cache.py`,
  `recon_tool/sources/cert_providers.py`,
  `scripts/check_metadata_coverage.py`, and five test files
  (`test_explain_integration.py`, `test_exposure.py`,
  `test_json_schema_contract.py`, `test_mcp_path_isolation.py`,
  `test_server_resources.py`). `isinstance(x, (A, B))` is rewritten
  to `isinstance(x, A | B)` per `UP038` (semantically equivalent on
  Python 3.10+). The single `S603` site in
  `test_mcp_path_isolation.py` - a deliberate subprocess invocation
  that *is* the test's subject - gets a targeted
  `# noqa: S603` with a justification comment rather than a code
  change, because rewriting away the subprocess call would defeat
  the test.

These fixes are why pre-commit had been failing locally on commit;
CI's narrower gate (`ruff check recon_tool/`, no `ruff-format`)
was masking the drift. v1.9.4 is the first commit on the cleaned-
up tree.

### Roadmap

- v1.9.4 bridge milestone **closed**.
- Next in sequence: v1.9.5 (per-node stability dispositions -
  takes the per-node firing counts from this run + the soft-corpus
  re-run as raw inputs).

## [1.9.3.10] - 2026-05-11

**Make subdomain-level surface intelligence visible by default.**
The default panel previously had two surfaces hidden behind `--full`
/ `--domains`: the chain walker's unclassified CNAME termini (chains
we walked but the catalog couldn't classify) and the per-provider
subdomain count (multi-cloud distribution across the apex's surface).
Both addressed real operator-facing detection-gap concerns surfaced
during empirical testing.

The implicit message of the prior panel was "they only use the
services we listed." That's wrong. The correct implicit message is
"they use AT LEAST the services we listed, plus N unclassified
surfaces we walked but couldn't name, plus their subdomains are
distributed across these specific providers in these specific
counts."

### Added

- **Default-panel "Unclassified surface" section.** When the chain
  walker reaches CNAME termini the catalog couldn't classify, the
  default panel now renders a one-line count plus up to two
  representative `subdomain → terminus` examples, with a discovery
  hint pointing at `recon discover <domain>` for triage. Renders only
  when `unclassified_cname_chains` is non-empty; absent otherwise.
  Coexists with the existing `--full`-mode unclassified-chain
  surface - the new section is gated by `not show_domains` so the
  two paths stay mutually exclusive.
- **Per-provider counts in the Subdomain line.** Previously listed
  surface-attributed services as a flat name list (`AWS CloudFront,
  Fastly, Stripe`); now shows counts (`Stripe (18), Fastly (12), AWS
  CloudFront (10)`) sorted by count descending. Dropped the apex-
  evidence filter that hid the multi-cloud picture on tenants whose
  apex and subdomains share a provider - the Subdomain line answers
  a different question from the Cloud line (provider distribution
  across the surface vs apex provider), so the duplication is
  intentional surfacing, not noise.
- **`tests/test_unclassified_surface_panel.py`** - 11 tests pinning
  the new section: singular/plural noun handling, discovery-hint
  presence, example count cap, terminus is chain's last hop, absence
  when field empty, `--domains` mode mutual exclusion, isolation from
  related-domains rendering.

### Changed - documentation

- **`docs/roadmap.md` substantially compressed.** Shipped milestones
  (v1.7.0, v1.8.0, v1.9.0, v1.9.2, v1.9.3) collapsed from full prose
  to one-line shipped stubs that point at the CHANGELOG for detail.
  v1.9.2 and v1.9.3 retain expandable `<details>` blocks for readers
  who want the historical rationale inline. `Current Fingerprint
  Library Assessment` rewritten to reflect v1.9.3.9 totals
  (414 entries, 343 unique slugs) and the empirical finding that the
  catalog is comprehensive for top-tier enterprise vendors. Detection-
  gap honesty paragraph added: passive DNS architecturally cannot see
  server-side API consumption.
- **`docs/roadmap.md` Backlog expanded** with detection-gap items
  surfaced during empirical validation:
  - Passive-DNS ceiling phrasing in the panel (Category-1 framing fix
    so absence-of-finding doesn't read as evidence of absence).
  - Subdomain enumeration breadth (CT SAN-set traversal beyond the
    queried apex, longer common-prefix wordlist, CT-by-org-name).
  - Stratified-corpus validation as standing practice (per-cloud
    10-domain reference sets to surface bias by design).
  - Cloud-provider rollup at apex level (top-of-panel multi-cloud
    indicator when ≥2 cloud-categorized providers across the surface).
  Each is backlog rather than committed because the trigger heuristic
  / wordlist / reference-set curation needs explicit design before
  shipping.

### Empirical validation (documented for the record)

Validated against a stratified sample of 6 known-rich-stack public
companies (gitignored private corpus). Highlight: zero unclassified
CNAME chain termini across the sample on top-tier vendors. The
catalog is comprehensive for known enterprise stacks; residual gaps
are architectural (Category-1 server-side API consumption) rather
than catalog. This finding shifts the v2.0 priority from "add more
fingerprints" to "make the architectural limit visible to operators".

### Tests

- 2289 passed, 1 skipped (+11 unclassified-surface-panel tests, was
  2278 in v1.9.3.9).
- Coverage 83.43% (≥ 80% gate).
- ruff + pyright clean on `recon_tool/` + `tests/`.

## [1.9.3.9] - 2026-05-11

**Catalog growth: cloud-vendor coverage gap fill (29 new
fingerprints, vendor-doc-sourced).** Closes a systematic coverage
blindspot surfaced during operator testing: a Solidifi/realmatters
lookup showed solid M365 + Cloudflare + Mailchimp + Atlassian
detection but missed several known GCP-customer service categories.
Diagnosis: the historical corpus-observed catalog-growth path
(scan a private corpus, fingerprint unclassified CNAME patterns)
has a built-in bias toward the segments our corpus already
represents - heavy GCP, Azure non-O365, Oracle Cloud, IBM Cloud,
Alibaba, the SaaS-PaaS galaxy, and SSE/SASE vendors get
systematically under-classified even when the chain walker
follows CNAMEs to the right terminus.

### Added - vendor-doc-sourced fingerprints in `surface.yaml`

Each entry cites the canonical vendor documentation URL in its
`reference` field. The methodology (vendor-doc-sourced as a
complement to corpus-observed) is documented in `CONTRIBUTING.md`
as standing practice for future catalog growth.

**Google Cloud Platform (5 slugs, 6 detections):**
- `firebase-hosting` - `firebaseapp.com`, `web.app`
- `gcp-cloud-functions` - `cloudfunctions.net`
- `firebase-realtime` - `firebaseio.com`
- `looker-studio` - `lookerstudio.google.com`, `looker.com`
- `gcp-storage` - `c.storage.googleapis.com`

**AWS (3 slugs, 3 detections):**
- `aws-amplify` - `amplifyapp.com`
- `aws-cognito` - `amazoncognito.com`
- `aws-waf` - `awswaf.com`

**Azure non-O365 (5 slugs, 6 detections):**
- `azure-blob` - `blob.core.windows.net`, `web.core.windows.net`
- `azure-static-web-apps` - `azurestaticapps.net`
- `azure-container-apps` - `azurecontainerapps.io`
- `azure-api-management` - `azure-api.net`
- `azure-appservice` extended with `azurewebsites.net`

**Oracle Cloud (2 slugs, 2 detections):**
- `oracle-cloud` - `oraclecloud.com`
- `oracle-fusion` - `fa.oraclecloud.com`

**IBM Cloud (1 slug, 2 detections):**
- `ibm-cloud` - `appdomain.cloud`, `bluemix.net`

**Alibaba Cloud (3 slugs, 4 detections):**
- `alibaba-api` - `alicloudapi.com`
- `alibaba-cdn` - `alikunlun.com`, `cdngslb.com`
- `alibaba-cloud` - `aliyuncs.com`

**Additional PaaS (3 slugs, 4 detections):**
- `railway` extended with `up.railway.app`
- `replit` - `replit.app`, `repl.co`
- `glitch` - `glitch.me`

**SSE / SASE / CASB (4 slugs, 6 detections):**
- `zscaler` extended with `zscaler.net`, `zscalerthree.net`,
  `zscalertwo.net`
- `netskope` extended with `netskope.com`, `goskope.com`
- `cato-networks` - `cato-networks.com`
- `prisma-access` - `prismaaccess.com`

**Identity (3 slugs, 3 detections):**
- `onelogin` extended with `onelogin.com`
- `jumpcloud` - `jumpcloud.com`
- `duo` extended with `duosecurity.com`

### Changed

- **`recon_tool/formatter.py`** - `_CATEGORY_BY_SLUG` updated with
  the 22 new slugs that didn't already have a category mapping
  from prior fingerprints (Cloud / Security / Identity / Business
  Apps / Data & Analytics buckets).
- **`CONTRIBUTING.md`** - adds a "Vendor-doc-sourced `cname_target`
  rules" subsection codifying the methodology: every new rule
  cites a vendor doc URL in `reference`; corpus-observed and
  vendor-doc-sourced are both encouraged paths; rules without a
  `reference` will be flagged once the v1.9.7 metadata-richness
  gate is enforcing.

### Catalog totals

- 414 fingerprint entries validated (was 386 in v1.9.3.8).
- 343 unique slugs.
- All slugs map to a defender-visible category.
- 0 cross-file slug-name collisions.

### Notes on residual coverage

This patch closes the biggest visible cloud-vendor gaps but is not
exhaustive. Real-world coverage still depends on the operator
running recon against the right subdomains - a tenant that uses
Firebase Hosting only on `app.example.com` requires that subdomain
to be in scope of the lookup (CT-log enumeration or known-prefix
probing) before the new fingerprint can fire. The catalog now
*can* classify; surfacing requires the chain walker to reach the
right host.

Verticals or vendors still likely under-represented:
SAP / Oracle SaaS apps beyond Fusion, smaller PaaS (Cyclic, Fl0,
Deta), edge/CDN providers outside the top tier (Fastly variants,
BunnyCDN extras), regional clouds (Yandex, OVH, Hetzner, Kakao),
and the long tail of SSE/SASE vendors (iboss, Versa, Aryaka).
Future catalog-growth passes should target these per the
methodology now documented in CONTRIBUTING.md.

### Tests

- 2278 passed, 1 skipped (same headline as v1.9.3.8 - no new tests
  added; the existing slug-uniqueness and metadata-coverage tests
  exercise the additions).
- Coverage 83.32% (≥ 80% gate).
- ruff + pyright clean on `recon_tool/` + `tests/`.
- Local `validate_fingerprint.py recon_tool/data/fingerprints/`
  passes (414/414 entries; same gate CI runs).

## [1.9.3.8] - 2026-05-11

**Track B quality work - downstream SIEM consumption examples.**
Ships the v2.0 pre-condition for "downstream consumption examples
(at least two SIEMs)" from the v1.9.x quality bar (see
`docs/roadmap.md`). recon's `--json` shape is the v2.0 schema-lock
target; locking that contract without published examples that
actually parse and ingest is premature. This patch makes the
contract real for Splunk and Elasticsearch operators and pins both
mappings against future schema drift via a CI gate.

### Added

- **`examples/siem/`** - cross-SIEM consumption index, plus two
  per-SIEM subdirectories.
- **`examples/siem/splunk/`** - `README.md` (field-mapping table,
  severity mapping, three use-case SPL snippets: shadow-IT
  alerting, DMARC drift, federation discovery), `props.conf`
  (sourcetype definition for `recon:lookup`), `savedsearches.conf`
  (three example saved searches matching the use cases), and
  `expected-splunk-event.json` (the worked output the CI gate
  verifies).
- **`examples/siem/elastic/`** - `README.md` (ECS-aligned field
  mapping table, severity mapping, same use-case framing),
  `ingest-pipeline.json` (Elasticsearch ingest pipeline that
  rewrites recon JSON to ECS namespaces), `index-template.json`
  (field-type pinning so Kibana visualizations don't drift on
  first-write surprises), and `expected-elastic-document.json`
  (worked output).
- **`tests/test_siem_examples.py`** - 33 contract tests pinning
  the worked examples against schema regression. Verifies: the
  shared sample input parses and carries every always-present
  field the SIEM READMEs claim to map; each SIEM's
  expected-output file parses; each README's "always present"
  mapping table references paths reachable in the sample;
  severity mappings consistent between README and worked output;
  the cross-SIEM index README lists both shipped SIEMs.

### Changed

- **`examples/sample-output.json`** enriched with the
  always-present-on-M365 fields the SIEM mappings reference:
  `slugs`, `email_security_score`, `cloud_instance`,
  `msgraph_host`, `primary_email_provider`. Still fictional
  Synthetic Gamma; no real-company data. Existing consumers of
  the sample see additional fields, not renamed ones -
  schema-additive.

### Notes for downstream consumers

- The SIEM examples are **maintainer-authored, vendor-unverified**.
  Per-example READMEs name the author-of-record. A SIEM-vendor
  employee opening a PR to validate or extend a mapping is welcome.
- The severity mapping documented in both READMEs is
  intentionally inverted from intuition (high recon confidence →
  low severity) because high confidence means strong public-signal
  evidence and a well-characterized posture; low confidence on a
  hardened target is the higher-severity signal worth operator
  review. Operators are expected to tune this for their context;
  the mapping is policy, not derivation.
- The CI gate verifies the worked-example file shapes against the
  shared input - a future schema rename that breaks SIEM ingestion
  fails the test before the schema change can reach a release tag.

### Roadmap

- **Track B item #9 of 10 cleared.** v2.0 pre-condition list shows
  one Track B item remaining: catalog metadata richness pass
  (descriptions ≥ 80%, references ≥ 25%). Track A bridge milestones
  v1.9.4 → v1.9.7 unchanged.

### Tests

- 2278 passed (+33 SIEM-example tests, was 2245 in v1.9.3.7).
- 1 skipped (Py3.10 + Windows shadow-workspace integration test).
- Coverage 83.33% (≥ 80% gate).
- ruff + pyright clean on `recon_tool/` + `tests/`.

## [1.9.3.7] - 2026-05-11

**CI fix: skip PYTHONSAFEPATH-only integration test on Python 3.10.**
The shadow-workspace integration test added in v1.9.3.4
(`test_shadow_workspace_cannot_execute`) asserted that
`PYTHONSAFEPATH=1` prevents a hostile cwd from shadowing
`recon_tool` when spawning `python -m recon_tool.server`. The
assertion is correct on Python 3.11+ but `PYTHONSAFEPATH` was
introduced in 3.11 (PEP 686) and is a no-op on 3.10. The CI matrix
includes Python 3.10, so the test failed for v1.9.3.4 / v1.9.3.5 /
v1.9.3.6.

The defense gap is architectural on 3.10, not a regression: the
v1.9.3.4 product code already routes around the unprotected
pattern.

### Changed

- **`tests/test_mcp_path_isolation.py`** - the shadow-workspace
  integration test now carries an explicit
  `@pytest.mark.skipif(sys.version_info < (3, 11), ...)` with a
  reason explaining the architectural limit. The skip reason
  records the recommended Python 3.10 launch path (`recon mcp`
  via the script entry point, not `python -m recon_tool.server`
  from an untrusted cwd). Unit tests in `TestServerRuntimeGuard`
  and source-inspection tests in `TestMcpDoctorSpawnsSafely`
  continue to run on every Python version - they cover the
  runtime guard and the safe-cwd + env-var contract
  independently.

### Notes for downstream consumers

- No code change to product behaviour. The v1.9.3.4 defenses
  (safe cwd in `mcp_doctor`, persisted `PYTHONSAFEPATH=1` in
  `mcp_install` fallback configs, runtime guard in
  `recon_tool/server.py`) are unchanged.
- On Python 3.10, the safe MCP launch pattern is `recon mcp`
  (the script entry point - has no `-m` and therefore no
  cwd-prepend risk). `mcp_install`'s `warn_if_fallback` already
  recommends this when `recon` is not on PATH.

### Tests

- 2245 passed, 1 skipped (the integration test skips on Py3.10
  and on Windows; runs on Py3.11/3.12/3.13 across ubuntu and
  macos).
- ruff + pyright clean.

This is a CI-only patch; no security regression and no defense
weakening. All four v1.9.3.x security findings remain closed by
v1.9.3.3 → v1.9.3.6.

## [1.9.3.6] - 2026-05-11

**Security: validation harness path containment (audit finding,
informational).** Closes the audit finding *"Validation runner
permits local fixture/persona file exfiltration"* against
`validation/agentic_ux/run.py`. The finding is informational
because the affected code is the maintainer-only validation
harness - not packaged in the wheel, not invoked by CI, not on a
recon end-user's product path - but the gap was real: a future
wrapper or agent calling `python -m validation.agentic_ux.run`
with unvalidated `--personas` / `--fixtures` arguments could have
caused arbitrary local `.md` / `.json` files to be read and
shipped to the configured LLM provider as part of the prompt.

This is the fourth and final patch addressing the security audit.

### Added

- **`validation.agentic_ux.run._validate_name`** - strict
  identifier validator (`^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$`) that
  rejects every selector with a separator, traversal sequence,
  leading dot, leading dash, whitespace, or non-ASCII character.
  Accepts every legitimate in-repo persona/fixture name; raises
  `ValueError` on anything else.
- **`_SAFE_NAME_RE`** - the compiled regex, exposed as a module
  attribute so a future maintainer adding a new persona/fixture
  can see the format contract without re-deriving it.
- **`tests/test_validation_harness_path_containment.py`** - 48
  tests covering: 12 legitimate names accepted, 16 unsafe shapes
  rejected (empty, traversal, absolute paths, separators, dots,
  null bytes, over-length), regex anchoring, both loader entry
  points refusing unsafe names before any filesystem read, and a
  sanity check that all in-repo personas/fixtures still load.

### Changed

- **`_load_persona`** and **`_load_fixture`** now run the new
  validator on the input name *before* building the file path,
  and confirm the resolved path is still under the intended
  directory (`is_relative_to`) - defense-in-depth in case a future
  edit loosens the regex.

### Notes for downstream consumers

- The harness is not packaged in the recon-tool wheel; only the
  recon CLI and MCP server are. End users see no change.
- Maintainers running the harness with the existing committed
  persona/fixture names see no behavioural change.
- Any wrapper passing user-supplied `--personas` / `--fixtures`
  values now needs to surface a sensible error message when an
  unsafe selector is rejected (the `ValueError` carries one).

### Tests

- 2245 passed (+48 harness-containment tests, was 2197 in v1.9.3.5).
- Coverage 83.32% (≥ 80% gate).
- ruff + pyright clean on `recon_tool/` + `tests/`.

### Security audit closed

This patch closes the fourth and final finding from the v1.9.3.x
security audit:

  1. v1.9.3.3 - Release workflow supply-chain isolation (HIGH).
  2. v1.9.3.4 - MCP doctor/install path isolation (HIGH).
  3. v1.9.3.5 - CNAME chain target validation, layer 2 (MEDIUM).
  4. v1.9.3.6 - Validation harness path containment
     (informational, this patch).

Each shipped as its own tag through the v1.9.3.3 hardened release
workflow. The CHANGELOG entries for each carry the per-finding
quality-bar verification.

## [1.9.3.5] - 2026-05-11

**Security: CNAME chain target validation, layer 2 (audit finding,
MEDIUM).** Closes the audit finding *"CNAME chain walking can query
and leak internal DNS names"* with the second of two layers. Layer 1
(suffix denylist) was already in place from v1.9.0; this patch adds
layer 2 (resolved-address private check).

The remaining gap: an attacker who controls a public domain returns
a CNAME to a publicly-named host (passes the suffix denylist) whose
A record resolves to RFC1918 or other private space via split-horizon
DNS. The suffix check alone cannot see this - only resolving the
target's A/AAAA records can.

### Added

- **`recon_tool/sources/dns._is_private_ip_literal`** - returns True
  for RFC1918, loopback, link-local, ULA, reserved, multicast, and
  unspecified IPv4/IPv6 addresses. Defensive on parse failure
  (returns False so the caller falls back to other checks rather
  than dropping legitimate hops on garbage input).
- **`recon_tool/sources/dns._hop_resolves_publicly`** - resolves a
  target's A and AAAA records in parallel and returns True iff at
  least one resolved address is in public space. Fail-open on
  unresolved cases (no A/AAAA records) so CNAME-only intermediate
  hops in legitimate chains continue to walk.
- **`tests/test_cname_chain_validation.py`** - 47 tests covering
  both defense layers plus end-to-end walker behaviour: suffix
  denylist on 17 private/malformed names and 5 public names,
  IP-literal classification across RFC1918/loopback/link-local/ULA
  /multicast/v6 and garbage inputs, hop-resolution helper across
  public/private/mixed/unresolved cases, and four chain-walker
  integration tests (suffix-drop, A-drop, legitimate-public,
  truncate-at-first-failing-hop).

### Changed

- **`recon_tool/sources/dns._resolve_cname_chain`** now calls
  ``_hop_resolves_publicly`` after the suffix check passes. A hop
  whose suffix passes but whose A/AAAA records are all in private
  space is dropped without recording - the walker halts at that
  point. Adds at most two DNS queries per accepted hop (A + AAAA),
  well inside the existing ``_SURFACE_MAX_HOPS=5`` and
  ``_SURFACE_CONCURRENCY=30`` budgets.

### Notes for downstream consumers

- Legitimate public CNAME chains continue to walk identically.
- An operator behind split-horizon DNS will see fewer CNAME hops
  recorded when an attacker-controlled public name resolves to
  their internal range - this is the intended defensive behaviour;
  the previously-leaking internal name no longer appears in
  evidence output.
- The new helpers (`_is_private_ip_literal`, `_hop_resolves_publicly`)
  are module-private (leading underscore). They are not part of the
  public API; callers should not rely on them.

### Tests

- 2197 passed (+47 CNAME-validation tests, was 2150 in v1.9.3.4).
- Coverage 83.32% (≥ 80% gate).
- ruff + pyright clean on `recon_tool/` + `tests/`.

This is the third of four security patches. v1.9.3.6 (validation
harness path containment, informational) remains.

## [1.9.3.4] - 2026-05-11

**Security: MCP doctor/install path isolation (audit finding, HIGH).**
Closes the audit finding *"MCP doctor/install can execute shadowed
recon_tool package"* against `recon_tool/mcp_doctor.py` and
`recon_tool/mcp_install.py` (v1.9.2.1). The finding: `recon mcp
doctor` spawned `python -m recon_tool.server` with inherited cwd and
no environment sanitization. Python's `-m` flag prepends the current
working directory to `sys.path` on Python 3.10 (and absent
`PYTHONSAFEPATH=1` on 3.11+), so an attacker-controlled workspace
containing a `recon_tool/server.py` could shadow the installed
package and execute attacker code as the local user. The installer's
fallback config (used when `recon` is not on PATH) persisted the
same launch form, so future MCP-client launches from untrusted
workspaces inherited the same risk.

The fix is defense-in-depth across three layers:

### Changed

- **`recon_tool/mcp_doctor.py`** - the subprocess is now spawned
  with `cwd` pointing at an empty `tempfile.TemporaryDirectory` and
  `env["PYTHONSAFEPATH"] = "1"` set. The empty cwd guarantees no
  `recon_tool/` directory is reachable via cwd-prepend on any Python
  version; the env var disables cwd-prepend entirely on Python 3.11+.
  Both safeguards together close the attack on every supported
  Python version, including 3.10 where the env var alone is a no-op.
- **`recon_tool/mcp_install.py` - `build_recon_block`** now persists
  `env: {"PYTHONSAFEPATH": "1"}` in the fallback launch block so
  future MCP-client launches on Python 3.11+ inherit the protection.
  The preferred form (when `recon` is on PATH) is unchanged - it
  invokes the script entry point, which has no cwd-prepend concern,
  so the env block stays clean.
- **`recon_tool/mcp_install.py` - `warn_if_fallback`** (new) exposes
  a warning when the fallback launch form would be persisted.
  Surfaced by `recon mcp install` so operators on Python 3.10 see
  the residual-risk hint and can install `recon` to PATH for the
  safer launch form.
- **`recon_tool/server.py` - `_detect_cwd_shadow_install`** (new)
  runs at server startup before any tool handlers register. It
  resolves `recon_tool.__file__` and refuses to start when the
  package was loaded from a path under the current working
  directory unless cwd contains a legitimate `recon-tool` named
  `pyproject.toml` (the source-checkout case). The runtime guard
  is the final defense - it catches the attack regardless of how
  the server was launched, including any MCP client config that
  pre-dates the v1.9.3.4 mitigations.

### Added

- **`tests/test_mcp_path_isolation.py`** - 10 tests across the
  three defense layers: (a) source inspection asserts `mcp_doctor.py`
  sets `PYTHONSAFEPATH=1` and passes a safe `cwd`; (b) unit tests
  prove the install fallback persists the env var and the preferred
  form omits it; (c) runtime-guard tests cover normal install,
  shadow workspace (refuses), and legitimate source checkout
  (allows). The shadow-workspace integration test launches a real
  subprocess with a malicious `recon_tool/server.py` and asserts the
  installed module loads, not the shadow.

### Notes for downstream consumers

- MCP clients already configured via `recon mcp install` keep
  working; the persisted env-block addition is backward-compatible.
- Operators with hand-edited MCP client configs that point at
  `python -m recon_tool.server` SHOULD add `"env":
  {"PYTHONSAFEPATH": "1"}` to those configs on Python 3.11+, or
  re-run `recon mcp install` to refresh the canonical block.
- The runtime guard refuses to start if cwd looks suspicious. If
  you legitimately run `python -m recon_tool.server` from a source
  checkout, the checkout's `pyproject.toml` must have
  `name = "recon-tool"` (the project's own pyproject.toml does).

### Tests

- 2150 passed (+9 path-isolation tests passing; 1 shadow-workspace
  integration test skipped on Windows). One pre-existing flaky
  exposure-copy hypothesis test (unrelated; tracked separately).
- Coverage 83.24% (≥ 80% gate).
- ruff + pyright clean on `recon_tool/` + `tests/`.

This is the second of four security patches addressing the audit
findings. Remaining: v1.9.3.5 CNAME chain target validation
(MEDIUM), v1.9.3.6 validation harness path containment
(informational).

## [1.9.3.3] - 2026-05-11

**Security: release workflow supply-chain isolation (audit finding,
HIGH).** Closes the audit finding *"Dev deps can tamper release
artifacts"* against `.github/workflows/release.yml` (introduced in
v1.9.3.1). The finding: the v1.9.3.1 release workflow installed the
dev extra (`uv sync --extra dev`) and ran `pip-audit` for SBOM
generation in the same workspace as the just-built `dist/` directory,
BEFORE `actions/upload-artifact` sealed the wheel and sdist into
GitHub-managed storage. A compromised dev dependency (or transitive
of pip-audit) executing during SBOM generation could have modified
the release artifacts; those modified artifacts would then have been
published to PyPI under the project's trusted-publisher identity.

The fix is structural - workspace isolation, not just ordering.

### Changed

- **`.github/workflows/release.yml` restructured** with an explicit
  supply-chain isolation contract documented in the header comment:
  - **`build` job is now PURE.** Runs only `uv sync --no-dev` and
    `uv build`, then immediately uploads `dist/` as a sealed artifact.
    No dev dependencies installed; no pip-audit; no SBOM generation;
    no `run:` step exists between `uv build` and the dist upload.
    Steps that previously ran here have been moved.
  - **New `sbom` job** runs on a separate runner. Re-derives the
    locked requirements text from `uv.lock`, installs `pip-audit`
    via `uv tool install` (isolated venv), and generates the
    CycloneDX SBOM from the requirements text alone. `dist/` does
    not exist in this runner. A compromised pip-audit cannot reach
    release artifacts because they are sealed in GitHub storage and
    not present on this filesystem.
  - **`sbom` depends on `test`, not on `build`.** This makes the
    parallel-runner isolation structurally obvious - the two jobs
    run on different workspaces with no shared state. A future
    contributor adding `needs: build` to `sbom` would be regressing
    the threat model; the new contract test catches this.
  - **`github-release`** now `needs: [build, sbom]` so the release
    cannot ship without an SBOM. `publish-pypi` is unchanged -
    still the only job with `id-token: write`, still only downloads
    `dist/` and publishes.

### Added

- **`tests/test_release_workflow_contract.py`** - 13 contract tests
  that parse `release.yml` and assert the isolation properties hold:
  build job has no `--extra dev`, no `pip-audit`, no SBOM steps;
  no `run:` step between `uv build` and dist upload; sbom job does
  not depend on build; sbom job does not download `dist/`;
  `id-token: write` is restricted to `publish-pypi`; github-release
  attaches both `dist/` and `sbom/`. The test is structural - it
  inspects the workflow YAML, not the runtime - so it runs in
  ~1 second on every pytest invocation and catches regressions
  that would otherwise only surface after a tampered release.

### Tests

- 2141 passed (+13 release-workflow contract tests, was 2128).
- Coverage 83.31% (≥ 80% gate).
- ruff + pyright clean on `recon_tool/` + `tests/`.

### Notes for downstream consumers

- The `dist/` artifact published to PyPI is structurally unchanged
  by this patch. Existing `pip install recon-tool` workflows are
  unaffected.
- The SBOM artifact attached to the GitHub Release continues to be
  named `recon-tool-<version>.cdx.json`. Consumers pulling the SBOM
  by stable name see no change.
- Future v1.9.x.y releases ship through the hardened workflow.

## [1.9.3.2] - 2026-05-10

**Track B quality work - Top-3 influential edges in `--explain-dag`.**
Closes the v2.0 explainability gap on the `--explain-dag` surface.
The v1.9.0 renderer reported a posterior and a flat evidence list but
didn't show *which* evidence drove the answer - exactly the question
a defending operator asks when disputing a verdict. v1.9.3.2 surfaces
each fired binding's log-likelihood-ratio contribution + its share of
total |LLR| influence, ranked top-3 per node, inline in both the text
narrative and the Graphviz DOT export.

The ranking matches the v1.9.x quality bar: LLR is quantified per
binding (not count or presence), sorted by absolute LLR descending,
ties broken by `(kind, name)` for diff-stability, single-binding case
uses singular header ("Top influence:"), no fake top-3 on sparse
targets, no section emitted when zero bindings fired.

### Added

- **`recon_tool.bayesian.EvidenceContribution`** dataclass - engine-side
  representation of a fired binding's LLR + influence_pct.
- **`recon_tool.models.NodeEvidence`** dataclass - public-facing
  counterpart, surfaced through `PosteriorObservation.evidence_ranked`
  in the cache, JSON output, and renderer.
- **`PosteriorObservation.evidence_ranked: tuple[NodeEvidence, ...]`** -
  schema-additive field. Default empty tuple preserves v1.9.0 / v1.9.3
  JSON shape for consumers that don't read this field.
- **`tests/test_explain_dag_top3.py`** - 16 tests covering LLR
  correctness (hand-verified against three canonical bindings from
  the seed network), ranking determinism (sort key, tie-break),
  sparse/zero-binding behaviour, and a snapshot pinning the rendered
  m365_tenant block. Future renderer changes must update the snapshot
  deliberately.

### Changed

- **`render_dag_text`** emits a "Top influence" or "Top influences
  (ranked, N fired)" section after the evidence list when ≥ 1 binding
  fired. Section header pluralizes correctly; when more than 3 fired,
  header reads "Top influences (ranked top 3 of N fired)".
- **`render_dag_dot`** node labels include a "top influences:" suffix
  with the top-3 ranking inline so DOT-rendered diagrams carry the
  same visibility the text narrative provides.
- **`docs/correlation.md` Example 1 (dense M365-federated stack)**
  regenerated with v1.9.3.2 output. The reading commentary explains
  *why* `entra-id` outranks `microsoft365` in evidence influence
  (likelihood ratio 44 vs 32) and how the ranking lets an operator
  audit which facts drove a verdict.
- **Cache + JSON serialization** round-trips `evidence_ranked` through
  `cache.py` and `formatter.py`. The forward-compat tests added in
  v1.9.3.1 already cover the case where an older reader encounters
  the new field (it ignores it gracefully).

### Roadmap

- **Track B "Top-3 influential edges" item closed.** v2.0
  pre-condition list shows 8 remaining (was 9 after v1.9.3.1).
  Two Track B items remain: catalog metadata richness pass and
  downstream consumption examples. Track A bridge milestones
  v1.9.4-v1.9.7 unchanged.

### Tests

- 2128 passed (+16 top-3 tests, was 2112 in v1.9.3.1).
- Coverage 83.32% (≥ 80% gate).
- ruff + pyright clean on `recon_tool/` + `tests/`.

## [1.9.3.1] - 2026-05-10

**Track B quality work - SECURITY.md and supply-chain hardening.**
Closes four entries from the roadmap "Known gaps" section in one
patch: SECURITY.md (already shipped pre-v1.9.3.1, audited and
left in place), CycloneDX SBOM as a release asset, gitleaks
secrets-scanning in CI, and a forward-compat cache test. Per the
v1.9.x quality bar (docs/roadmap.md), each sub-item ships against
explicit acceptance criteria a reviewer can verify.

### Added

- **CycloneDX SBOM as release asset.** Every GitHub Release now
  carries a `recon-tool-<version>.cdx.json` file generated by the
  release workflow from the same locked dependency set the audit
  gate validates. Consumers can pin their SBOM tooling against the
  stable name. Generated via `pip-audit --format=cyclonedx-json`,
  written to a separate `sbom/` directory so the PyPI publish job
  only sees wheels and sdists. Includes runtime + transitive
  dependencies with their licenses.
- **`.github/workflows/secrets-scan.yml`** - gitleaks runs on
  every PR, every push to main, and a weekly Sunday 06:00 UTC
  scheduled scan against the historical branch tree. Read-only
  workflow permissions; failures non-bypassable. Three triggers
  cover the realistic leak surfaces: pre-merge (PR), bypassed-PR
  (push to main), and historical-leak rotation (weekly).
- **`tests/test_cache_forward_compat.py`** - 10 regression tests
  pinning the implicit "ignore unknown fields, load known fields
  cleanly" contract that `recon_tool.cache.tenant_info_from_dict`
  has always honoured but never tested. Covers unknown top-level
  fields, unknown nested-dict keys (in `cert_summary`,
  `posterior_observations[]`, `evidence[]`), higher
  `_cache_version`, and confirms malformed-input rejection still
  works. The contract matters because a v1.10 cache writer that
  adds a new field must not require a v1.9 reader to crash on the
  file - operators upgrading and downgrading recon between
  machines hit this case routinely.

### Changed

- **`docs/roadmap.md` Known-gaps section updated.** Four of six
  items now strike-through to "shipped"; the remaining two
  (mutation testing, SLSA provenance) explicitly deferred to
  post-v2.0. Track B v2.0 pre-condition list reflects 9 remaining
  items (was 10 before v1.9.3.1).
- **`docs/roadmap.md` Track B "SECURITY.md and supply-chain
  hardening" item** marked shipped with a back-reference to this
  changelog entry. Quality-bar verification per-item:
  - SECURITY.md: real scope (defensive, passive-only,
    explicit out-of-scope), 48-hour ack SLA, 7-day assessment,
    30-day fix; nick@pueo.io reporting channel; coordination
    policy implicit via the MCP-specific threat-model section.
  - Secrets scanning: PR + push + weekly schedule (three triggers).
  - SBOM: CycloneDX format, generated by the release workflow,
    runtime + transitive with licenses.
  - Forward-compat cache test: 10 tests covering both top-level
    and nested unknown-field cases plus malformed-input rejection.
  - Transitive-pin rationale: `python-multipart>=0.0.27` carries
    its `CVE-2026-42561` rationale comment in `pyproject.toml`;
    audit found no other un-rationalized transitive pins.
  - `pip-audit` confirmed fail-on-vulnerability default;
    no advisory-only relaxation.

### Tests

- 2112 passed (+10 forward-compat, was 2102 in v1.9.3).
- Coverage 83.29% (≥ 80% gate).
- ruff + pyright clean on `recon_tool/` + `tests/`.

## [1.9.3] - 2026-05-09

**v1.9.3 bridge milestone - Bayesian-network topology surgery.**
Resolves the `email_security_strong` definitional gap that produced
the 52.6% v1.9.0 calibration disagreement. Per
[docs/roadmap.md §v1.9.3](docs/roadmap.md), this is topology surgery,
not CPT tuning - the v1.9.0 node parameterized its CPT on
modern-mail-provider presence (M365 / GWS / gateway) but tested
policy-enforcement signals (DMARC / DKIM / SPF / MTA-STS) via its
evidence bindings. Different claims; no parameter tuning could
reconcile them.

**Calibration impact.** Spot-check agreement on
`email_security_policy_enforcing` (the evidence-driven half of the
split) is **100%** on the v1.9.3 spot corpus. See
[validation/v1.9.3-calibration.md](validation/v1.9.3-calibration.md)
for the full calibration aggregate and reproducibility instructions.

### Changed (EXPERIMENTAL surface)

- **`bayesian_network.yaml` topology** bumped to v1.9.3 (frozen
  2026-05-09; 9 nodes, was 8). The topology stability contract
  acknowledges bridge milestones as planned exceptions.
- **`email_security_strong` removed** from
  `recon_tool/data/bayesian_network.yaml`. Consumers pinning the
  v1.9.0 node name in `posterior_observations[]` must update. The
  EXPERIMENTAL label on the whole `--fusion` surface accommodates
  this; no separate deprecation patch - the node's calibration was
  the explicit weak spot v1.9.x was committed to fixing.
- **`federated_identity` parents expanded** from `[m365_tenant]` to
  `[m365_tenant, google_workspace_tenant]`. The v1.9.0 single-parent
  network systematically under-attributed federation when the path
  didn't go through M365 (Okta + GWS, Auth0 + custom IdP, standalone
  SAML). Four-entry CPT preserves the M365-path numbers and seeds
  GWS-path values.

### Added

- **`email_security_modern_provider`** node - provider-presence
  claim. Parents `[m365_tenant, google_workspace_tenant,
  email_gateway_present]`; no evidence bindings (pure CPT
  propagation). Provider presence is fully observable through the
  parent slugs.
- **`email_security_policy_enforcing`** node - policy-enforcement
  claim. Root node, prior 0.25. Evidence bindings carried over from
  the v1.9.0 node: `dmarc_reject`, `dmarc_quarantine`,
  `mta_sts_enforce`, `dkim_present`, `spf_strict`. Provider-
  independent - a Zoho or Fastmail tenant with a strict DMARC
  reject policy fires this node identically to an M365 one.
- **`tests/test_bayesian_topology.py`** - 11 regression tests
  pinning the new topology against silent reversion.
- **`validation/v1.9.3-calibration.md`** - per-release calibration
  aggregate (sensitivity, synthetic ECE, spot-check); part of the
  standing per-release publish discipline.
- **`docs/correlation.md §4.9`** - *Definitional discipline: the
  v1.9.3 split.* The v1.9.3 gate the roadmap required: explicit
  definitions of both new nodes, why they are separate claims, and
  the principle behind questioning topology before tuning numbers.

### Roadmap

- **v1.9.3 bridge milestone closed.** v1.9.4 (hardened-adversarial
  behavior validation) is next. The full v1.9.0 corpus will be
  re-run against the v1.9.3 topology as part of v1.9.4 to certify
  cross-vertical calibration.
- **Roadmap restructured** - items previously in
  *v1.9.x - Optional feature additions* that v2.0 polish requires
  (catalog metadata richness, SECURITY.md + supply-chain hardening,
  downstream consumption examples, top-3 influential edges in
  `--explain-dag`) moved to a new *Required quality work for v2.0*
  section. v2.0 pre-conditions now enumerate ten items across two
  tracks: six bridge milestones (Track A) plus four required
  quality items (Track B).

## [1.9.2.2] - 2026-05-08

**Catalog growth from the v1.9.2-pre-release corpus scan - 39 new
fingerprints.** The 4,270-domain scan that gated v1.9.2 surfaced 86
unclassified CNAME patterns. v1.9.2.2 ships the **39 new fingerprints**
(33 application-tier SaaS + 6 infrastructure-tier CDNs) that survived
hand-reviewed LLM-assisted triage against the project's existing
`recon-fingerprint-triage` skill rubric. The remaining 47 candidates
were dropped: 27 intra-org self-references (e.g. Microsoft's own
`dc-msedge.net`, Baidu's `shifen.com`, Alibaba's `tbcache.com`),
12 already-covered slugs, 4 niche one-offs, 2 unclear pending more
corpus exposure.

This is a follow-up patch to v1.9.2 (which was harness-only with no
recon_tool/ changes) and to v1.9.2.1 (MCP UX, also no catalog
changes). The "no bundling" rule applies: shipping fingerprint
additions in their own patch keeps each tag attached to one
user-facing story.

### Added

- **39 new `cname_target` fingerprints** in
  `recon_tool/data/fingerprints/surface.yaml`:
  - **Identity / Security:** Akamai EAA (Zero Trust), Fortinet
    FortiWeb Cloud, plus extended Okta (FedRAMP `okta-gov.com`
    and DNSSEC `okta-dnssec.com` patterns) and Ping Identity
    (PingOne `ping.cloud`).
  - **Email & Communication:** Hostinger Email, Rackspace Email.
  - **Productivity & Collaboration:** BigMarker, CampusPress,
    Fluid Topics (Antidot), Framer, Gatsby Events, GitBook,
    Mintlify, Refined (Confluence theme), Stova (Aventri),
    Tistory (Kakao), Tumblr, Weglot, WordPress.com.
  - **Marketing:** Movable Ink, Prowly, Terminus (Sigstr),
    Uberflip (ZoomInfo).
  - **Business Apps:** Amplience, Q4 Inc. (IR Platform),
    Talentera.
  - **Commerce:** Fanatics Retail Group, SAP Commerce Cloud.
  - **Certain (Cvent)** event management.
  - **Infrastructure-tier CDNs:** Edgio CDN (Limelight),
    EdgeCDN (Bitban), Lumen CDN (Footprint), Medianova CDN,
    Merlin CDN, plus extended Gandi (`partners.gandi.net` +
    `vip.gandi.net` web-redirect), easyDNS URL forwarding,
    IONOS hosting (`adsredir.ionos.info`), Kinsta managed
    WordPress, and Google Cloud (`bc.googleusercontent.com`
    extending the existing `gcp-app` slug).
- **36 new formatter category mappings** in
  `recon_tool/formatter.py:_CATEGORY_BY_SLUG` for the new slugs
  (three slugs - okta, ping-identity, gcp-app - reuse existing
  entries rather than introducing duplicate names).
- **`validation/triage_llm.py`** - programmatic LLM-assisted
  triage runner. Reads a `candidates.json` produced by
  `validation/triage_candidates.py`, batches the entries to an
  Anthropic chat model with the project's triage rubric as the
  system prompt, parses the structured response into a markdown
  triage report (kept local - references real sample subdomains)
  plus a proposed-stanzas YAML diff (only generic patterns,
  safe to commit). Dev tool only; not a runtime dependency.
  End users do not need an LLM API key for any recon CLI
  surface.

### Changed

- `recon_tool/data/fingerprints/surface.yaml` - appended catalog-
  growth section under the existing Microsoft 365 entry. Catalog
  validator confirms **385 / 385 entries pass** schema (was 346).

### Tests

- Existing 2091 tests still pass at 84.03% coverage. No new tests
  added - fingerprint behavior is data-driven and exercised by the
  catalog validator (`recon fingerprints check`), the match-mode
  audit (`validation/audit_fingerprints.py`), and the existing
  per-detection unit tests in `tests/test_fingerprints*.py`.

### Fixed

- **`tests/test_mcp_install.py::test_envvar_expands_in_cli_config_path`
  cross-platform regression.** The test added in v1.9.2.1 used a
  `$VAR` POSIX form with an inverted polarity check that
  reassigned to `%VAR%` (Windows-only) after ``os.path.expandvars``
  successfully expanded the POSIX form. On Linux the resulting
  `%VAR%` literal never gets re-expanded by Python's stdlib, so
  the install never wrote to the temp dir and the assertion
  failed. v1.9.2.1's CI publish job consequently failed on Linux
  even though the local Windows test pass count was 2091. This
  patch swaps to the curly-brace `${VAR}` POSIX form which
  ``os.path.expandvars`` handles identically on every platform.
  Net effect: PyPI did not receive a v1.9.2.1 release; users
  upgrading skip from 1.9.2 to 1.9.2.2.

### Roadmap

- Standing-work discipline restored: every release window now
  includes at least one private-corpus scan plus the resulting
  catalog growth in the same release window (v1.9.2 +
  v1.9.2.2 together). The "no bundling" rule is preserved by
  separating the harness work (v1.9.2), MCP UX (v1.9.2.1), and
  catalog growth (this) into three tagged releases that share a
  release window but not a single tag. v1.9.2.1 was tagged on
  GitHub but its release workflow failed at the test job
  (regression noted under Fixed above), so PyPI never received
  it; the MCP UX features it introduced ride along with this
  v1.9.2.2 wheel.

## [1.9.2.1] - 2026-05-08

**MCP works by default - interactive misuse caught, install + live
self-check shipped.** Three independent UX patches bundled because
they share a single user-facing story: "I ran the MCP server and it
either confused me or didn't connect." Operators who launched
`python -m recon_tool.server` (or `recon mcp`) directly in a shell
hit a Pydantic JSON-parse traceback the first time their stray
newline reached the JSON-RPC parser; this release intercepts that
case with an explicit "this is not a REPL" panel. Operators who
wanted to wire recon into an MCP client had to copy-paste a JSON
block into a per-OS, per-client config file by hand;
`recon mcp install --client=<name>` now does that idempotently.
And operators who installed but couldn't tell whether the wiring
actually worked had only static-shape diagnostics; `recon mcp
doctor` now spawns the server and walks a real initialize +
tools/list handshake the way a client would.

These are roadmap "v1.9.x - Optional feature additions (parallel
to the bridge milestones)" entries - they ship as a bundle here
rather than as three separate patches because the underlying
narrative is one user-facing change, and CHANGELOG readers benefit
from seeing the three components together. The next bridge
milestone (v1.9.3 - `email_security_strong` definitional gap) is
unaffected.

### Added

- **`recon_tool/server.py:_print_tty_misuse_panel` + TTY guard.**
  When `sys.stdin.isatty()` returns True and the
  `RECON_MCP_FORCE_STDIO` env var is unset, `main()` prints a
  human-readable panel explaining that the server speaks JSON-RPC
  over stdio and exits cleanly. The previous behavior - feeding
  the user's stray newlines into the FastMCP JSON parser and
  surfacing a Pydantic stack trace - is preserved behind
  `RECON_MCP_FORCE_STDIO=1` (case-insensitive; `1`, `true`,
  `yes`, `on` all enable the bypass). The TTY check itself
  catches `AttributeError`, `ValueError`, and `OSError` from
  `isatty()` so embedded environments with stubbed-out or
  closed-handle stdin don't crash before the JSON-RPC loop ever
  starts.
- **`recon mcp install --client=<name>` (`recon_tool/mcp_install.py`).**
  Idempotent merge of the canonical `mcpServers.recon` block into
  the right config file for six clients: claude-desktop,
  claude-code, cursor, vscode, windsurf, kiro. Per-OS path table
  (Windows / macOS / Linux), `--scope user|workspace|auto`,
  `--config-path` override (with `~` and env-var expansion),
  `--force` to refresh canonical fields, `--dry-run` to preview
  without writing. `--force` is field-
  preserving: only `command` and `args` are authoritative on the
  install side; the user's hand-curated `autoApprove` list,
  `env` overrides, `disabled` flags, and any other keys they've
  added to the recon block all survive a `--force` rerun. Reads
  with `utf-8-sig` so a UTF-8 BOM (Windows Notepad / certain
  PowerShell redirects) doesn't trip JSON parsing; writes with
  `ensure_ascii=False` and `newline="\n"` so non-ASCII content
  in sibling configs round-trips byte-for-byte and disk format
  stays platform-agnostic. Refuses to clobber unparseable JSON,
  top-level non-object configs, or a `--config-path` that points
  at a directory rather than a file; preserves sibling
  `mcpServers` entries; falls back from `recon` to `python -m recon_tool.server`
  when `recon` is not on PATH so GUI clients (Claude Desktop,
  Windsurf) that don't inherit the shell PATH still launch the
  server. Idempotent rerun is genuinely free - when no canonical
  field would change, the file is not rewritten and its mtime is
  not bumped, avoiding spurious file-watcher reloads in clients
  like Cursor and VS Code. Writes are atomic - content goes to a
  sibling tempfile in the same directory, gets ``fsync``'d where
  the filesystem supports it, then ``os.replace``'d into place,
  so a partial-write failure (disk full, antivirus mid-scan,
  network drive drop, OS crash) leaves either the old config
  intact or the new config fully on disk - never a half-written
  truncation.
- **`recon mcp doctor` (`recon_tool/mcp_doctor.py`).** End-to-end
  self-check: spawns the server through the running interpreter
  (`python -m recon_tool.server`), opens a real `stdio_client` +
  `ClientSession`, performs `initialize` + `tools/list`, and
  asserts the response includes the canonical anchor tools
  (`lookup_tenant`, `analyze_posture`, `assess_exposure`,
  `find_hardening_gaps`, `chain_lookup`). 30-second handshake
  timeout. Spawned-server stderr is captured to a tempfile rather
  than forwarded to the terminal; on a successful run, that
  capture is dropped (no banner flood above the checks); on a
  crash during ``initialize``, the trailing twelve lines of the
  captured stderr are spliced into the failure detail so the user
  sees the actual ImportError / traceback / missing-dependency
  message instead of an opaque ``BrokenPipeError``. Distinct from
  the existing `recon doctor --mcp`, which remains the static-
  shape sibling (package import, FastMCP introspection, copy-
  pasteable config snippet).

### Changed

- **`recon mcp` is now a typer sub-typer instead of a leaf command.**
  Bare `recon mcp` (no subcommand) still starts the server - the
  callback uses `invoke_without_command=True` so backward
  compatibility is preserved. New subcommands (`install`,
  `doctor`) live under it. No change to existing scripts or MCP
  client configs.

### Tests

- 72 new tests across `tests/test_mcp_install.py` (55),
  `tests/test_mcp_doctor.py` (10 including a real
  subprocess-spawning live handshake and a server-stderr
  capture-on-crash case), plus TTY-guard and field-preservation
  cases in `tests/test_server.py`. New tests pin: BOM-stripped
  reads, unicode round-trip without `\u` escapes, LF line endings
  on Windows, idempotent rerun (mtime stable), user `env` /
  non-empty `autoApprove` / `disabled` / unknown-key preservation
  under `--force`, `~` and env-var expansion in `--config-path`,
  directory-path refusal, `Path.home()` failure, `OSError` /
  `ValueError` / `AttributeError` paths through
  `_stdin_is_tty()`, and case-folded / whitespace-tolerant
  `RECON_MCP_FORCE_STDIO` parsing, atomic-write debris cleanup,
  and partial-write-failure preservation of the original config.
  Full suite: 2091 passing.

### Roadmap

- Closes three "v1.9.x - Optional feature additions" entries.
  Bridge sequence (v1.9.3 → v1.9.7 → v2.0) unaffected.

## [1.9.2] - 2026-05-08

**Agentic UX validation harness - first v1.9.x bridge milestone toward
v2.0.** Operators are not the only persona that reads recon's `--fusion`
output: the MCP server is a primary surface, and an AI agent reading
recon JSON is itself a production user. v1.9.2 shipped a reproducible
harness that drives three persona prompts (security analyst,
due-diligence researcher, ops engineer) across one dense and one hand-stripped
sparse fictional fixture under both `--fusion`-on and `--fusion`-off arms -
twelve sessions per run - and scores the transcripts against
the five-check rubric defined in `docs/roadmap.md`. The shipped record included
detailed session rows. The current tracked aggregate at
`validation/v1.9.2-agentic-ux.md` preserves the calibration input for the v2.0
schema-lock disposition decisions. New detailed runs stay in gitignored local
paths; the historical detailed copy is covered by the
[data-handling policy's published-artifact exception](docs/data-handling-policy.md#historical-published-artifact-exception).

### Added

- **`validation/agentic_ux/` harness.** `providers.py` is a
  multi-provider chat adapter (Anthropic / OpenAI / xAI Grok) with
  optional-import SDK loading; `score.py` is the binary rubric
  scorer (regex/keyword scans, no LLM-as-judge); `run.py` is the
  CLI entry point (`python -m validation.agentic_ux.run`) that
  orchestrates the 3 × 2 × 2 matrix, totals realized cost from API
  responses, and writes a self-contained markdown report. The
  module is decoupled from `recon_tool` so the harness can run
  against captured recon JSON from any version.
- **Persona scaffolds.** `personas/{analyst,researcher,ops}.md` -
  none mention `posterior_observations`, `sparse=true`,
  `--explain-dag`, or credible intervals; the rubric measures
  whether the agent finds those affordances unprompted.
- **Committed fixtures.** The release-time dense and sparse fixtures used
  fictional, non-reserved target identities. The current tracked replacements,
  `fixtures/synthetic-dense.json` and `fixtures/synthetic-sparse.json`, preserve
  those semantic shapes with explicit synthetic sentinels under the reserved
  `.invalid` namespace.
- **`validation/v1.9.2-agentic-ux.md`** - originally a detailed session record;
  now a disclosure-safe historical aggregate for the agentic UX workflow. New
  detailed run output stays local.

### Changed

- **`docs/roadmap.md`** - bridge milestones renumbered. v1.9.1 was
  consumed by the conflict-provenance optional feature, so the
  bridge sequence now reads v1.9.2 (this release) → v1.9.3
  (`email_security_strong` topology surgery) → v1.9.4
  (hardened-adversarial validation) → v1.9.5 (per-node stability
  criteria) → v1.9.6 (CPT-change discipline) → v1.9.7
  (metadata-coverage gate). Cross-references and the v2.0
  pre-conditions table updated to match. The introductory
  paragraph of the bridge section now explains the renumbering
  explicitly.
- **`validation/__init__.py`** - added so `validation` is a proper
  package rather than an implicit namespace package. Defeats
  pyright import-resolution flakiness without changing the
  runtime contract (existing `python -m validation.<name>`
  invocations are unchanged).

### Tests

- **`tests/test_agentic_ux.py`** - 26 new tests covering the
  provider-adapter shape with mocked SDK clients (no network),
  rubric scoring on synthetic transcripts (positive and negative
  cases for every check), runner orchestration (12-session matrix,
  fusion-stripping correctness), and the report writer (required
  sections present, cost rendering correct).

Total: 2012 tests passing.

### Roadmap

- Closes the **v1.9.2 - UX validation via agentic QA** bridge
  milestone toward v2.0. Findings from the first canonical run map
  directly to the v2.0 schema-lock disposition decisions in
  `docs/roadmap.md`.

## [1.9.1] - 2026-05-05

**Conflict provenance on `NodePosterior`.** First v1.9.x optional-feature
patch from the bridge plan in `docs/roadmap.md`. The v1.7 conflict-aware
merger captures *which sources disagreed on which fields*; the v1.9.0
fusion layer rolled this into a uniform n_eff penalty and dropped the
detail. v1.9.1 carries the structured provenance through to every
`PosteriorObservation` so both `--explain-dag` and the `--json` output
can name the disagreeing sources alongside the existing top-level
`evidence_conflicts` array. Schema-additive - required key added to
`PosteriorObservation`; emits `[]` when no conflicts dampened the
interval. EXPERIMENTAL alongside the rest of the v1.9 fusion surface.

### Added

- **`ConflictProvenance` (engine) and `NodeConflict` (model) dataclasses.**
  `recon_tool.bayesian.ConflictProvenance` is the inference-side record
  carrying `field`, `sources`, and `magnitude` (n_eff units). The
  `recon_tool.models.NodeConflict` mirror is the serializable
  TenantInfo-side counterpart and round-trips through cache.
- **`infer(..., conflicts=...)` parameter.** Structured per-conflict
  records replace the count-only path when supplied; the legacy
  `conflict_field_count` parameter remains a backward-compatible entry
  point (its callers are unchanged). When both are passed, `conflicts`
  wins and the count is derived from `len(conflicts)`.
- **`PosteriorObservation.conflict_provenance` field.** Always present
  in `--json` output as a (possibly empty) array. Each entry:
  `{field, sources: [...], magnitude}`. Documented in
  `docs/recon-schema.json` under a new `NodeConflict` `$def`.
- **`--explain-dag` rendering.** Text renderer adds a `**Conflicts:**`
  line per node listing each disagreement as
  `` `field` (source-a vs source-b, -1.50 n_eff) `` when non-empty;
  the line is omitted when no conflicts dampened the interval. DOT
  renderer appends `conflicts: <field-list>` to node labels for the
  same nodes.
- **Cache forward-compat.** Pre-v1.9.1 cached entries (no
  `conflict_provenance` key) parse cleanly to an empty tuple; the
  parser tolerates malformed conflict entries via the same
  `try/except` pattern used elsewhere in `_parse_posterior_observations`.

### Changed

- **`PosteriorObservation` schema** in `docs/recon-schema.json` -
  `conflict_provenance` added as a required key (always present, empty
  array when no conflicts). `NodeConflict` `$def` added alongside.
- **`recon_tool/bayesian.py`** - `_conflict_provenance(info)` extracts
  structured records from `MergeConflicts`; the legacy
  `_conflict_count(info)` helper is removed (its single caller now
  uses the structured path).
- **`recon_tool/cli.py`** - fusion construction site maps
  `ConflictProvenance` → `NodeConflict` when populating
  `PosteriorObservation.conflict_provenance`.

### Tests

- **`tests/test_conflict_provenance.py`** - 12 new tests covering:
  empty provenance when no merge_conflicts; populated provenance with
  field/source/magnitude detail; source deduplication; explicit
  `conflicts=` argument overriding `conflict_field_count`; legacy
  count-only path yields empty provenance; JSON shape (always-present
  array, empty when clean); cache round-trip including a pre-v1.9.1
  payload; text renderer surfaces conflicts; text renderer omits the
  conflict line when clean; DOT renderer annotates conflict-bearing
  nodes.

Total: 1982 tests passing.

### Roadmap

- Marks the **conflict provenance on `NodePosterior`** bullet from the
  v1.9.x optional-features list as shipped.
- Patch-release discipline: this lands as a single-feature patch per
  the v2.0 bridge plan; no other unrelated work in this version.

## [1.9.0] - 2026-05-04

**Probabilistic fusion layer (v1.9), EXPERIMENTAL.** Adds the third
correlation layer planned in `docs/roadmap.md`: a small discrete
Bayesian network with exact variable-elimination inference, calibrated
80% credible intervals via effective-sample-size construction, and
asymmetric one-sided likelihoods that refuse overconfident verdicts on
hardened-target sparse evidence. Fully gated behind `--fusion`; the
default panel and v1.0 JSON shape are unchanged. Full validation
report at
[`validation/v1.9-validation-summary.md`](validation/v1.9-validation-summary.md);
formal model and citations in
[`docs/correlation.md` §4.8](docs/correlation.md).

### Added

- **`recon_tool/data/bayesian_network.yaml`** - committed network
  topology and CPTs (8-node seed: m365_tenant, google_workspace_tenant,
  federated_identity, okta_idp, email_gateway_present,
  email_security_strong, cdn_fronting, aws_hosting). Schema v1,
  network topology v1.9.0 (frozen 2026-05-04). Likelihoods
  strictly in `(0, 1)`; degenerate hard-evidence factors rejected.
- **`recon_tool/bayesian.py`** - pure-Python variable-elimination
  inference engine. Topology validation (DAG, complete CPTs,
  parent reachability), TenantInfo adapter, posterior + 80% credible
  interval per node, n_eff calibration with conflict dampener.
  Asymmetric one-sided likelihoods (Jeffrey-style updating;
  cautious-updating literature: Walley 1991, Augustin et al. 2014,
  Taroni et al. 2014).
- **`recon_tool/bayesian_dag.py`** - plain-English narrative
  renderer + Graphviz DOT export for the inference DAG.
- **`PosteriorObservation` model** - new dataclass on TenantInfo;
  populates `posterior_observations` in `--json` output when
  `--fusion` is on. Empty array otherwise. Round-trips through cache.
- **`--explain-dag`** CLI flag with `--explain-dag-format text|dot`.
  Implies `--fusion`. 4 worked examples in correlation.md §4.8a.
- **`get_posteriors`** and **`explain_dag`** MCP tools - read-only,
  cache-aware, rate-limited like `lookup_tenant`.
- **`~/.recon/priors.yaml`** - operator-supplied root-node prior
  override. Local-only, never shipped, never sent over the wire,
  never persisted in cache. Loader logs an info-level message when
  applied so operators see when an override is shaping output.
- **`scripts/check_metadata_coverage.py`** - per-category description
  / reference / weight coverage report. Wired into CI as advisory
  (will flip to enforcing once the catalog reaches the 70% target on
  identity / security / infrastructure).
- **`validation/synthetic_calibration.py`** - publicly-reproducible
  ground-truth calibration experiment using the network's own joint
  distribution. Reports marginal vs conditional ECE, per-node
  reliability tables, and identifies calibration weak spots
  (currently `email_security_strong` and `aws_hosting`).
- **JSON schema entry** for `posterior_observations` in
  `docs/recon-schema.json` ($defs/PosteriorObservation, EXPERIMENTAL).
- **Mermaid diagrams** in correlation.md: three-layer dataflow,
  Bayesian DAG topology, sparse-vs-dense interval illustration.
- **Sensitivity-bound regression guard.** ±0.10 perturbation of any
  single CPT entry produces ≤ 0.139 posterior shift (median 0.019,
  95th percentile 0.109). Test: `tests/test_bayesian_sensitivity.py`.

### Changed

- **`docs/correlation.md`** - substantial expansion of §4.8 with the
  full v1.9 derivation: generative model, variable elimination
  (citations: Zhang & Poole 1994; Koller & Friedman 2009),
  asymmetric likelihood with literature grounding, credible-interval
  calibration (Beta moment-matching; Wilson approximation),
  identifiability discussion, relationship to the existing Beta
  layer, validation strategy with publicly-reproducible numbers.
  §3 expanded to a three-layer comparison table. §4.1-4.7 trimmed
  of repetitive boilerplate. Citations added throughout (Pearl 1988,
  Russell & Norvig, Blondel et al. 2008, Traag et al. 2019,
  Naeini et al. 2015, Jeffrey 1965, Walley 1991, etc.).
- **`docs/roadmap.md`** - v1.9 status updated to shipped.

### Tests

- **244 new tests** added across:
  - `test_bayesian_canonical.py` - verifies engine matches Pearl
    Burglary-Earthquake-Alarm and the medical-test example to four
    decimal places under the noisy-likelihood model.
  - `test_bayesian_inference.py` - schema validation, priors override,
    variable elimination correctness on a hand-checked toy network,
    credible interval shape, TenantInfo adapter.
  - `test_bayesian_dag.py` - text + DOT renderer correctness,
    confidence-label thresholds, sparse-flag rendering.
  - `test_bayesian_fuzz.py` - 39 adversarial schema inputs (empty,
    null, cycles, unicode, boundary likelihoods).
  - `test_bayesian_hypothesis.py` - property-based testing with
    Hypothesis: 550 random valid networks + evidence sets verify
    closed-form Bayes match, prior recovery on no evidence,
    invariants under random conflicts, determinism.
  - `test_bayesian_sensitivity.py` - CPT ±0.10 perturbation bound.
  - `test_bayesian_validation_rounds.py` - 24 inference invariants.
  - `test_fusion_robustness.py` - cache round-trip with malformed
    entries, CLI flag combinations, MCP error paths, determinism +
    concurrency, scale stress (15-node chain, 10-child wide network).
  - `test_fusion_integration.py` - end-to-end --fusion path.
  - `test_metadata_coverage.py` - CI gate behavior.

Total: 1938 tests passing. Coverage on new modules:
`recon_tool/bayesian.py` 98%, `recon_tool/bayesian_dag.py` 92%.

## [1.8.1] - 2026-05-03

**Hardening release driven by a 10-domain diverse deep-dive against
v1.8.0.** Per-target output quality surfaced four issues that the
105-domain batch validation missed because it scored corpus medians
rather than individual results. All four are fixed and re-validated.
Full report at
[`validation/v1.8-validation-summary.md`](validation/v1.8-validation-summary.md).

### Fixed

- **CT-cache fallback gap.** `_detect_cert_intel` early-returned on
  any provider response, even an empty one. CertSpotter rate-limited
  responses look like a successful empty answer (HTTP 200, no
  issuances), so when crt.sh was degraded and CertSpotter was
  rate-limited the CT-cache fallback never fired and `cert_summary`
  stayed null even when a populated cache entry existed. Now an
  empty `(subdomains=[], cert_summary=None, infrastructure_clusters=None)`
  response is treated as soft failure: the loop continues to the next
  provider and, if all return empty, the CT cache is consulted.
- **`chain_motifs` and v1.7 `cert_summary` extensions silently
  dropped on cache write.** `tenant_info_to_dict` did not include
  `chain_motifs`, `wildcard_sibling_clusters`, or
  `deployment_bursts` in its serialized form, so cache-served
  lookups always returned zero motifs and empty wildcard / burst
  collections - even when the original resolve produced matches.
  Both directions of the round-trip now preserve them. Round-trip
  regression tests in `tests/test_cache_roundtrip.py`.

### Added

- **Eight new chain motifs covering Microsoft-internal and
  vendor-specific chain shapes.** Catalog grew from 10 to 18.
  Microsoft: `tm_to_azurefd`, `azurefd_to_msedge`, `akamai_to_msedge`,
  `tm_to_powerapps`. Salesforce: `salesforce_chain`. Adobe:
  `adobe_experience_cloud`, `akamai_to_adobe`. Oracle Cloud:
  `oracle_cloud_chain`. The deep-dive observed that real-world
  chains for hardened-target enterprises terminate inside a single
  vendor's perimeter (e.g. `trafficmanager.net -> azurefd.net ->
  t-msedge.net`), which the v1.7 third-party-only catalog did not
  cover.
- **Twenty-six more fingerprint slugs seeded with relationship
  metadata.** v1.8.0 shipped 8 seeded slugs; v1.8.1 brings the total
  to 34 across openai, anthropic, salesforce, salesforce-mc,
  marketo, segment, meta, sendgrid, mailchimp, akamai, azure-tm,
  fastly, azure-fd, aws-acm, atlassian, workplace-meta, adobe-idp,
  adobe-sign, apple, onetrust, okta, 1password, jamf, stripe,
  docusign, google-site. Surfaced as the `fingerprint_metadata`
  block in `--json`.
- **FastMCP transport smoke test for the v1.8 graph tools.**
  `tests/test_mcp_graph_tools.py::TestMcpToolRegistry` invokes
  `get_infrastructure_clusters` and `export_graph` through
  `mcp.call_tool` - the same dispatch the stdio JSON-RPC handler
  uses on `tools/call`. Confirms registration + reachability beyond
  the unit tests.

### Validation

- 10-domain diverse deep-dive (one apex each from hyperscale tech,
  global payments, productivity SaaS, heavy-industrial manufacturing,
  higher-ed research, EHR, non-profit messaging, federal agency,
  warehouse retail, and national news media) re-run with caches
  cleared. `chain_motifs`: 0 -> 19 observations across 4 domains.
  `fingerprint_metadata`: 6 -> 29 distinct slugs surfaced, per-domain
  coverage 0-4 -> 4-16. Cluster partition quality preserved (the
  hyperscale-tech apex hit modularity 0.82 on 247 nodes).
- 1789 tests passing, 0 failed (was 1774 in v1.8.0 + 15 new
  regression tests). Ruff and pyright clean.

### Internal

- Repo-root `.gitignore` strengthened with `*.com.json`,
  `*.org.json`, `/v1_*_dive/`, `/sc-*.json` etc. patterns so ad-hoc
  validation lookups can't accidentally land in commits.
- MCP server banner tool count corrected from "19 total" to "20
  total" (the v1.8.0 banner forgot `cluster_verification_tokens`).

## [1.8.0] - 2026-05-03

**Graph correlation.** Second milestone of the v1.7-v1.9 build plan in
[`docs/roadmap.md`](docs/roadmap.md). Builds a structural layer on top
of the v1.7 cert intelligence: SAN co-occurrence becomes communities,
fingerprint metadata becomes ecosystem hyperedges, and absence rules
turn vertical profiles into hedged baseline checks. Zero new network
surface - every new field is a re-projection of evidence already in
the pipeline. See [`docs/correlation.md`](docs/correlation.md) for the
formal framing.

### Fixed

- **CertSpotter `Z`-suffix dates rejected on Python 3.10.**
  `build_cert_summary` called `datetime.fromisoformat()` directly on
  CertSpotter `not_before` / `not_after` strings, which end in `Z`.
  Python 3.10's parser rejects `Z` (only 3.11+ accepts it), so every
  CertSpotter cert entry was silently skipped and `cert_summary`
  returned None - disabling `top_issuers`,
  `wildcard_sibling_clusters`, `deployment_bursts`, and the
  `top_issuer` ecosystem hyperedge. New `_parse_iso_datetime()`
  helper in `recon_tool/sources/cert_providers.py` normalizes `Z` →
  `+00:00` before parsing. Pre-existing v1.7.0 bug surfaced by the
  v1.8 corpus validation. Regression test in
  `tests/test_cert_providers.py`.
- **`shared_slugs` ecosystem hyperedge noise floor.** Validation
  showed 195/200 hyperedges firing on trivial "every enterprise has
  Microsoft365 + Adobe + DocuSign" coincidences. `_MIN_SLUG_OVERLAP`
  raised 2 → 3, and a new `_baseline_slugs()` filter strips slugs
  with >50 % corpus prevalence (`_BASELINE_FREQ_THRESHOLD = 0.5`)
  from the overlap intersection before the threshold check. Adaptive
  per-batch - engages only when the batch exceeds
  `_MIN_BATCH_FOR_BASELINE = 5` so synthetic test fixtures stay
  deterministic. Two new tests in `tests/test_ecosystem.py`.

### Added

- **CT co-occurrence graph + Louvain communities** - new
  `recon_tool/infra_graph.py` builds an in-memory graph from cert
  entries (nodes = SAN hostnames, edges = shared-cert co-occurrence,
  attributes carry issuer name) and runs Louvain via pure-Python
  `networkx`. The report - algorithm, modularity, node/edge counts,
  cluster list - surfaces as the always-present top-level
  `infrastructure_clusters` envelope in `--json`. Capped at 500 nodes
  with deterministic connected-components fallback above the cap.
  Skipped envelope when no graph could be built.
- **`get_infrastructure_clusters` + `export_graph` MCP tools** -
  read-only exposure of the already-computed graph. The first emits
  the cluster envelope; the second emits the raw co-occurrence graph
  (nodes + weighted edges + cluster_assignment) for downstream Mermaid
  / GraphViz / CSV pipelines. Edges retained on the report up to
  `MAX_EDGES_RETAINED = 2000`, sorted by weight desc.
- **Fingerprint relationship metadata** - fingerprint YAML schema gains
  three optional fields: `product_family`, `parent_vendor`, and
  `bimi_org`. Eight built-in slugs now carry metadata (Microsoft 365,
  Google Workspace, GitHub, Cloudflare, Slack, AWS Route 53,
  AWS CloudFront, AWS SES). Surfaced as the always-present
  `fingerprint_metadata` map in `--json`, keyed by slug.
- **Ecosystem hypergraph (`recon batch --json --include-ecosystem`)** -
  new `recon_tool/ecosystem.py` builds cross-domain hyperedges of four
  types: shared CT top issuer, shared BIMI VMC organization, shared
  fingerprint parent_vendor, and pairwise fingerprint-slug overlap
  (≥2). Emitted as a `ecosystem_hyperedges` array sibling to the
  per-domain `domains` array in the batch JSON wrapper. Off by default;
  flag is mutually-exclusive with `--md`/`--csv`/`--ndjson`. Capped at
  `MAX_HYPEREDGES = 200`.
- **Vertical-baseline anomaly rules** - profile YAML gains
  `expected_categories` and `expected_motifs`. The new
  `compute_baseline_anomalies()` in `recon_tool/profiles.py` surfaces
  hedged "absence is observable, not a verdict" observations when an
  expected category/motif is missing from the result. Wired into the
  posture pipeline so anomalies appear inline with regular observations
  when `--profile` is set. Seeded for `fintech` and `healthcare`
  profiles.

### Schema

- New top-level fields (always emitted on per-domain `--json`):
  - `infrastructure_clusters` (object) - see
    [`docs/recon-schema.json#/$defs/InfrastructureClusterReport`](docs/recon-schema.json).
  - `fingerprint_metadata` (object) - see
    [`docs/recon-schema.json#/$defs/FingerprintMetadata`](docs/recon-schema.json).
- New batch wrapper shape (only when `--include-ecosystem` is set):
  `{ ecosystem_hyperedges: [...], domains: [...] }`. The hyperedge
  shape is documented under
  [`docs/recon-schema.json#/$defs/EcosystemHyperedge`](docs/recon-schema.json).
- All v1.8 fields are stable. `infrastructure_clusters.edges` is not
  emitted in the default JSON envelope (kept behind the `export_graph`
  MCP tool to bound payload size).

### Changed

- **Repo layout** - `claude-code/` and `clients/` consolidated into a
  unified `agents/` directory: `agents/claude-code/` (full plugin),
  plus per-client folders for Cursor, Windsurf, Kiro, and VS Code.
  Each agent folder ships its own MCP config + README. The unified
  index at [`agents/README.md`](agents/README.md) lists every
  supported client. README, `docs/mcp.md`, and `validation/README.md`
  link references updated; old `clients/` directory removed.
- **CT provider Protocol** - `CertIntelProvider.query()` now returns a
  3-tuple `(subdomains, cert_summary, infrastructure_clusters)`. Both
  built-in providers (`CrtshProvider`, `CertSpotterProvider`) compute
  the cluster report alongside the summary so the graph layer is
  populated on the same code path that already runs CT analysis.

### Internal

- New module `recon_tool/infra_graph.py` (105 stmts, 92% test coverage).
- New module `recon_tool/ecosystem.py` (97 stmts, 95% test coverage).
- 63 new tests across `tests/test_infra_graph.py`,
  `tests/test_ecosystem.py`, `tests/test_baseline_anomalies.py`,
  `tests/test_mcp_graph_tools.py`, plus extensions to
  `tests/test_fingerprints.py` and `tests/test_json_schema_contract.py`.
- `pyright` config gains `venv = ".venv"` + `include = ["recon_tool", "tests"]`
  so type-checking resolves through the editable install rather than
  any stale user-site `recon-tool` wheel that may be present.
- `networkx>=3.0` added as a runtime dependency. Pure-Python; ships no
  learned weights or aggregate intelligence.

### Validation gate

- Full pytest suite green (1774 passed, 0 failed). New v1.8 modules at
  92-95% line coverage. Ruff and pyright both clean across `recon_tool`
  and `tests`. JSON schema drift test updated.
- 105-domain corpus run with `--include-ecosystem` completed with **0
  errors**. Cluster partition quality on the 11 domains with
  buildable graphs: **mean modularity 0.563, max 0.883**. Fingerprint
  relationship metadata fired on **91 / 105** domains. The run
  surfaced two pre-tag hardening items (CertSpotter `Z`-suffix
  parsing, `shared_slugs` noise floor - see *Fixed* above); both
  were resolved and re-validated against the same corpus before
  tagging. Full report at
  [`validation/v1.8-validation-summary.md`](validation/v1.8-validation-summary.md).

## [1.7.0] - 2026-05-03

**Hardened-target signal recovery.** The first of the v1.7-v1.9 build plan
in [`docs/roadmap.md`](docs/roadmap.md). This release squeezes more usable
defensive intelligence out of CT logs and resolution chains we already
collect - every new field is a post-processing layer on existing passive
observables. Zero new network surface, zero new credentials, zero
ownership claims. See [`docs/correlation.md`](docs/correlation.md) for
the latent-variable framing.

### Added

- **Wildcard SAN sibling expansion** - when a CT cert covers `*.example.com`,
  recon now harvests every concrete (non-wildcard) SAN from that same
  cert as a candidate sibling cluster. Surfaced under
  `cert_summary.wildcard_sibling_clusters` in `--json`. Bounded
  (≤10 clusters, ≤20 names per cluster). Works for both crt.sh and
  CertSpotter providers.
- **Temporal CT issuance bursts** - co-issued cohorts inside a 60-second
  window with ≥3 distinct names become `cert_summary.deployment_bursts`
  entries: relative window deltas + name list. Output is intentionally
  relative - co-issuance is observable; "same owner" is not.
  Bounded (≤8 bursts, ≤25 names per burst).
- **CNAME chain motif library** - new `recon_tool/data/motifs.yaml` and
  loader at `recon_tool/motifs.py`. Each motif names an ordered
  proxy/CDN/origin shape (e.g. Cloudflare → AWS origin, Akamai → Azure
  origin); fires on a related subdomain's CNAME chain when its markers
  appear in order. Surfaced as a top-level `chain_motifs` array in
  `--json`. Catalog ships with 11 CDN→origin shapes covering the major
  cloud providers; users extend additively via `~/.recon/motifs.yaml`.
  Chain length capped at 4. Per-lookup observation cap at 50.
- **Cross-source evidence conflicts in `--json`** - top-level
  `evidence_conflicts` array (always present, empty when no conflicts).
  Each entry names a merged field where 2+ sources gave different
  values, with all candidates preserved. The legacy `conflicts` dict
  emitted under `--explain` is unchanged for backwards compatibility.

### Schema

- New stable v1.7+ top-level fields: `evidence_conflicts`, `chain_motifs`.
- New stable v1.7+ nested fields: `cert_summary.wildcard_sibling_clusters`,
  `cert_summary.deployment_bursts`.
- New `$defs` entries in `docs/recon-schema.json`: `EvidenceConflict`,
  `ChainMotif`, `CertBurst`.
- `docs/schema.md` updated with worked examples for each new field.

### Internal

- `models.py` gains `CertBurst`, `ChainMotifObservation`, and
  `serialize_conflicts_array()`.
- `cert_providers.py` `build_cert_summary()` now accepts SAN lists per
  cert entry; both providers attach `dns_names` to each cert metadata
  record so the wildcard / burst pipelines can consume them.
- `dns.py` `_classify_related_surface()` invokes the motif matcher
  alongside the existing `cname_target` rule classifier; results land
  in `_DetectionCtx.chain_motifs` and propagate through the merger.

### Validation gate

- 67 new/updated tests across `test_motifs.py`, `test_cert_providers.py`
  (wildcard cluster + burst paths), and `test_json_schema_*` (new
  fields + conflict-array shape). Every new feature carries explicit
  "does not fire when…" coverage alongside the positive case
  (per-roadmap discipline).
- Full private-corpus run is the user's responsibility (corpus is
  gitignored). The corpus delta will land alongside the v1.7.0 PyPI tag.

## [1.6.1] - 2026-05-03

**Patch release - streaming batch + 26 new fingerprints from a 4,270-domain
corpus run.** Re-ran the discovery loop on a 4.3x-larger private corpus
(~4,270 domains across 5 geos and 9 verticals), surfaced 1,620 unclassified
suffixes, triaged to 117 candidates, added 26 new ``cname_target``
fingerprints. Also fixes the "no visible progress on big batches" UX gap
discovered during the corpus run.

### Added

- ``recon batch --ndjson`` - streams one JSON object per line, flushed as
  each domain completes. Eliminates the buffer-everything-then-emit
  pattern of ``--json``. Recommended for any batch over a few hundred
  domains; gives visible progress and constant memory use. Mutually
  exclusive with ``--json`` / ``--md`` / ``--csv``. Skips post-batch
  enrichment (token clustering, tenant peers) because those need all
  results before any can emit; ``--json`` keeps the enrichment for
  smaller batches.
- ``validation/find_gaps.py`` and ``validation/diff_runs.py`` auto-detect
  input shape: JSON array, single JSON object, or NDJSON. Both also pick
  up ``*.ndjson`` files when scanning a directory.
- ``validation/scan.py`` defaults to NDJSON now (writes ``results.ndjson``);
  ``--json-array`` opts back into the legacy single-array shape.
- 26 new ``cname_target`` fingerprints from the corpus run:
  Paradox.ai Olivia, Jibe Apply, Career.page, Happydance Careers,
  EasyRedir, SAP Customer Data Cloud (Gigya), F5 Distributed Cloud
  (Volterra), Radware Cloud, ForgeRock Identity Cloud, IO River,
  Section.io, Azion Edge, Acquia Cloud, Pagely, Outreach, Zuddl,
  Postman Hosted Status, Site24x7, Salesforce Marketing Cloud
  (exacttarget.com / sfmc-content.com extension), AWS S3 Static
  Website, AWS EC2, Microsoft 365 China (svc.sovcloud.cn extension),
  Webflow proxy-ssl-geo extension, PagerDuty internal status page.
  Catalogue: 163 cname_target rules across ~95 unique slugs.

### Changed

- README MCP-Server section trimmed: the prominent ``> [!WARNING]``
  block was relocated. The full safety details still live in
  ``docs/mcp.md``; the soft "keep approvals manual" line below the
  config snippet remains in the README.

### Notes

- The streaming ``--ndjson`` mode trades batch-wide enrichment
  (``shared_verification_tokens``, ``tenant_id_peers``,
  ``display_name_peers``) for memory bound and visible progress. If you
  rely on cluster fields, use ``--json`` for batches that fit in memory.
- The corpus and run outputs stay private under
  ``validation/corpus-private/`` and ``validation/runs-private/``
  (gitignored). Only the generic patterns surfaced for triage become
  catalog additions.

## [1.6.0] - 2026-05-03

**Minor release - catalog grown from real validation.** Used the
v1.5.2 discovery loop on a curated 986-domain corpus spanning F500
US, US SMB, EU, APAC, LATAM, Africa/ME, government/edu/nonprofit,
B2B SaaS, and dev tools. Mined 548 unclassified terminal suffixes,
triaged to 46 high-quality candidates, added 17 new
``cname_target`` fingerprints. Adds an MCP discovery tool so AI
agents can mine candidates inline. Brand-stem heuristic catches
cross-zone same-brand abbreviations. Adds a ``scan.py`` wrapper
that bundles the four-step loop into a single timestamped
invocation suitable for monthly-cadence runs.

### Added

- 17 new ``cname_target`` fingerprints from the v1.6.0 corpus run:
  Swoogo (events), UptimeRobot (status), bl.ink (URL shortener),
  GoDaddy Workspace Email, cloud.gov (US federal PaaS), Pantheon
  (Drupal/WordPress hosting), jobs2web (recruiting),
  Presspage (PR), Localist (event calendar), RainFocus (event
  management), Squarespace external customer, HubSpot CMS EU CDN,
  Akamai staging zone, Azure App Service / Cloud Services VM
  pattern, AWS API Gateway (5 regions), AWS Network Load Balancer
  (5 regions). Catalog now has 137 cname_target rules across
  ~80 unique slugs.
- New MCP tool ``discover_fingerprint_candidates``. Wraps the
  ``recon discover`` pipeline so AI agents can mine fingerprint
  candidates without shelling out. Same input/output shape as the
  CLI subcommand.
- New ``validation/scan.py`` - bundles
  ``recon batch`` + ``find_gaps`` + ``triage_candidates`` +
  ``diff_runs`` into one timestamped invocation. Each scan writes
  ``results.json``, ``gaps.json``, ``candidates.json``, optional
  ``diff.json``, and ``meta.json`` capturing the run metadata.
  Designed for monthly-cadence drift detection on private corpora.
- Brand-stem abbreviation detection in
  ``recon_tool.discovery.looks_intra_org_brand``. Catches cases
  where a sibling zone uses an abbreviated brand label
  (``examplecorp.com`` → ``ec.net``). The 3-character prefix must
  appear as a standalone DNS label in the suffix; the 5-char
  brand-label floor avoids matching incidental short sequences.
- ``validation/README.md`` documents the monthly cadence with
  ``scan.py`` and the gitignored ``corpus-private`` /
  ``runs-private`` workspace convention.

### Changed

- Brand-label extractor now skips 5+ second-level public
  suffixes (``co``, ``ac``, ``com``, ``net``, ``gov``, ``edu``,
  ``ne``, ``or``, ``go``, ``mil``, ``biz``) when extracting the
  brand stem from a multi-part TLD apex.

### Notes

- The corpus run wasn't shipped to GitHub - only the framework is
  generic and committed; real corpora and run outputs stay local
  under ``validation/corpus-private/`` and ``validation/runs-private/``
  (gitignored).
- ``scan.py`` is the recommended entry point for recurring
  validation. Run monthly (or whatever cadence works) with
  ``--label`` to tag the run; subsequent runs auto-diff against
  the most recent prior unless ``--no-compare`` is passed.

## [1.5.2] - 2026-05-02

**Minor release - discovery loop in production.** Closes the gaps that
showed up the first time we used the v1.5.1 loop end-to-end on real
domains: batch / corpus runners couldn't opt into the discovery hooks,
the three-step pipeline was clunky for single-domain users, the
intra-org heuristic mis-handled multi-part TLDs, and CI's
validate-fingerprints check wasn't gating PyPI deploys. Also adds 11
new fingerprints surfaced from the first discovery-loop runs.

### Added

- New `recon discover <domain>` subcommand. Single-shot pipeline that
  resolves the domain with `--include-unclassified`, applies the
  intra-org and already-covered filters, and emits a candidate JSON
  consumable by the `/recon-fingerprint-triage` Claude skill. Replaces
  the three-command incantation for single-domain discovery.
- New `recon_tool/discovery.py` library: `find_candidates`,
  `extract_brand_label`, `looks_intra_org_brand`,
  `load_existing_patterns`. Shared between the `discover` command and
  the standalone `validation/` scripts.
- `recon batch` accepts `--include-unclassified` and `--no-ct`,
  matching the single-domain flags. Threaded through the resolver to
  the DNS source and into `format_tenant_dict`.
- `validation/run_corpus.py` plumbs the same two flags through to
  `run_batch_validation_sync`. Big corpus runs can now use the
  discovery hook and the polite-mode knob.
- Discovery-loop hint in `--full` panel: when `unclassified_cname_chains`
  is non-empty, a subtle dim-italic line invites the user into the
  catalogue-growth loop with the exact `recon discover <domain>`
  command. Default panel unchanged.
- 11 new fingerprints from the first production discovery runs:
  PingOne (`pingone.com`), Salesloft (`salesloft.com`), Pendo
  (`pendo.io`), Docebo (`docebopaas.com`), Skilljar (`skilljarapp.com`),
  Bizzabo (`bizzabo.com`), Instatus (`instatus.com`), Frontify
  (`frontify.com`), ReadMe (`readmessl.com`), WP Engine variant
  (`wpeproxy.com`), WorkOS variant (`workos-dns.com`).

### Changed

- Intra-org heuristic now skips second-level public suffixes (`co`,
  `ac`, `org`, `net`, `gov`, `edu`, ...) when extracting the apex's
  brand label. `alpha.invalid` correctly resolves to brand `alpha`
  instead of `co`. Same brand-label extractor used by the
  `recon discover` subcommand and `validation/triage_candidates.py`.
- `release.yml` test job now runs the same `validate-fingerprints`
  check as `ci.yml`. Closes the gap where a duplicate-slug regression
  could reach PyPI through release.yml even though ci.yml caught it.

### Notes

- The discovery loop is now usable end-to-end with one command.
  `recon discover pingidentity.com` produces a candidate list, the
  Claude skill turns it into YAML stanzas, the user applies the diff
  and re-runs. Validated on this release: 11 new fingerprints came
  from running the loop on 10 fresh domains.
- No schema changes. v1.0 contract intact.

## [1.5.1] - 2026-05-02

**Minor release - fingerprint discovery loop.** Wires up the
machinery for growing the fingerprint catalog from real-world DNS
data: a JSON hook for unclassified CNAME chains, polite-mode knobs
for big runs, validation tooling that surfaces gap candidates, and
a Claude Code skill that turns those candidates into ready-to-apply
YAML stanzas.

### Added

- New `--include-unclassified` flag on `recon <domain>`. Adds an
  `unclassified_cname_chains` array to `--json` output: every CNAME
  chain the surface classifier resolved but couldn't attribute to a
  fingerprint. Wildcard echoes are filtered before this list is
  populated. Off by default (keeps the v1.0 schema narrow); on for
  the discovery loop.
- New `--no-ct` flag on `recon <domain>`. Skips crt.sh and
  CertSpotter entirely; discovery falls back to common-subdomain
  probes + apex CNAME walks. For high-volume validation runs where
  you want zero load on public CT services. Threaded through the
  resolver to the DNS source.
- New `validation/find_gaps.py` - reads a run (single JSON file or
  directory) and surfaces unclassified terminal hostname suffixes
  ranked by frequency. Filters intra-org chains.
- New `validation/diff_runs.py` - compares two run directories.
  Reports new attributions, lost slugs, aggregate slug-frequency
  changes. Use after adding fingerprints to confirm uplift.
- New `validation/triage_candidates.py` - programmatic filter on
  `gaps.json`: drops already-fingerprinted patterns (substring
  match against the catalog), intra-org chains, and one-off noise
  below `--min-count`. Output is the LLM-triage-ready candidate
  list.
- New Claude Code skill `agents/claude-code/skills/recon-fingerprint-triage/`
  that consumes either a single recon JSON or a `candidates.json`
  and proposes `cname_target` YAML stanzas with tier and category.
- New `UnclassifiedCnameChain` model + `unclassified_cname_chains`
  property on the v1.0 JSON schema (optional, surfaced only with
  `--include-unclassified`).
- `.gitignore` carve-outs: `validation/corpus-private/`,
  `validation/runs-private/`, `validation/local/`. Users can curate
  private corpora without risk of leaking targets.

### Changed

- `recon_tool/fingerprint_validator.py` cross-file duplicate-slug
  check is now name-aware. A slug appearing in multiple files is a
  duplicate only when display names disagree; same-slug, same-name
  across files is the legitimate "split detection rules across
  files" pattern that `surface.yaml` uses to extend apex
  fingerprints with cname_target rules. (This also unblocked the
  v1.5.0 CI regression.)
- `validation/README.md` rewritten to document the discovery loop,
  the polite-mode knobs, the gitignored corpus convention, and how
  to contribute back generic patterns.

### Notes

- The discovery loop is opt-in. Default `recon <domain>` output is
  unchanged; the JSON contract is unchanged unless
  `--include-unclassified` is passed.
- Programmatic vs LLM split is intentional: deterministic noise
  filtering happens in `triage_candidates.py`, judgment calls
  (real SaaS vs intra-org, tier, category, slug canonicalization)
  happen in the skill.

## [1.5.0] - 2026-05-01

**Minor release - external surface attribution.** Per-subdomain
classification of related domains via CNAME chain walks, surfacing
SaaS and infrastructure providers that don't publish apex DNS
verification tokens. The default panel surfaces newly-attributed
slugs through the existing `Services` block; `--full` adds an
`External surface` section that lists each subdomain alongside its
primary service.

The classifier walks the CNAME chain (cap 5 hops, 30 concurrent
queries, 100 hosts max) for each related domain collected from
crt.sh, CertSpotter, and the common-subdomain probe. Application-tier
matches (Auth0, Shopify, Zendesk, Mailgun, Apigee, ...) take
precedence over infrastructure-tier matches (Fastly, CloudFront,
Akamai, Cloudflare, ...) when both appear in the same chain. The
full chain stays in the JSON `evidence` array for `--explain`
consumers.

### Added

- New `cname_target` detection type in the fingerprint YAML schema,
  with a `tier: application | infrastructure` field that governs
  attribution precedence when a chain matches both.
- New `surface.yaml` fingerprint file seeding 50+ application and
  infrastructure CNAME-target patterns drawn from live validation
  across a private corpus spanning consumer goods, payments, retail,
  productivity SaaS, and national news media apexes.
- `surface_attributions` field on `TenantInfo` and the JSON output;
  see `docs/recon-schema.json` for the schema definition.
- `External surface` section in `--full` panel output: two-column
  subdomain → service map, sorted alphabetically.
- New AWS slugs: `aws-app-runner`, `aws-global-accelerator`. New
  third-party slugs: `apigee`, `mulesoft`, `submittable`,
  `loop-returns`, `attentive`, `iterable`, `intercom`, `hubspot`,
  `cloudflare-pages`, `github-pages`.

### Changed

- `_VALID_DETECTION_TYPES` extended with `cname_target`. Existing
  `cname` rules continue to fire on the apex / common-subdomain
  probes; the new type fires on every related domain's CNAME chain.
- Several surface-attribution slugs categorize as Cloud rather than
  the Business Apps fallback: `aws-app-runner`,
  `aws-global-accelerator`, `mulesoft`, `cloudinary`, `apigee`,
  `heroku`, `webflow`, `cloudflare-pages`, `github-pages`.
- Test `test_all_fingerprint_slugs_unique` now allows duplicate
  fingerprint names when the slug also matches (same logical
  service split across YAML files); name collisions on different
  slugs are still a failure.

### Notes

- A-only related domains (no CNAME) remain unclassified. Recovering
  those requires ASN/IP intelligence, which the project's invariants
  exclude.
- The classifier adds at most 100 CNAME queries per lookup, run with
  concurrency 30 - roughly a 2-5x increase in DNS volume on domains
  with sprawling CT footprints. Observed wall-clock impact on the
  validation corpus was under 1s per domain.

## [1.4.8] - 2026-04-29

**Patch release - skill refinements from running it in anger.** Docs-only.
Seven friction points surfaced from real skill use against the v1.4.7
artifact have been smoothed in `agents/claude-code/skills/recon/SKILL.md` and
`AGENTS.md`. No behavior, schema, or fingerprint changes.

### Changed

- MCP-vs-CLI decision is now explicit: agents look at their available-tools
  list for `recon:*` tools rather than calling speculatively to test
  connectivity.
- "Picking a profile" now shows both CLI (`--profile <name>`) and MCP
  (`analyze_posture(domain, profile="<name>")`) invocation syntax.
- `recon delta` section calls out the cache location (`~/.recon/cache/`)
  and the first-run empty-diff case so agents do not report "no changes"
  when there is no baseline to compare against.
- Default mode includes a collapsed sample panel so a cold reader of the
  skill knows what "relay verbatim" actually delivers.
- New "Explain mode" section documents `--explain` and the MCP
  `explanation_dag` field with guidance on summarising the provenance
  chain rather than dumping it.
- Full-mode headline template cites `docs/recon-schema.json` v1.0 so
  future skill editors know where the field-name contract lives.
- Output-size guidance directs agents to save full JSON instead of dumping
  potentially large certificate-transparency and evidence data inline.

## [1.4.7] - 2026-04-29

**Patch release - machine-readable JSON schema.** Adds the v1.0 stable
contract as a committed JSON Schema artifact so downstream consumers
(agents, CI pipelines, SDKs in other languages) can validate
`recon <domain> --json` output without re-deriving the shape from sample
runs. No behavior, fingerprint, or formatter changes.

### Added

- `docs/recon-schema.json` - JSON Schema 2020-12 description of the
  `recon <domain> --json` v1.0 contract, including a `$defs/DeltaReport`
  entry consumers can target for `recon delta` validation.
- `tests/test_json_schema_file.py` - drift guard that fails CI when the
  emitted JSON output and the committed schema fall out of sync in
  either direction (extra output key not declared, or required schema
  field not emitted).
- README - agent-driven install snippet ("paste this prompt to your AI"
  with the stable raw.githubusercontent.com SKILL.md URL) so users with
  AI clients that have file-write tools can wire up the skill in one
  exchange. Pointer to the new schema artifact for downstream
  validators.

### Changed

- `tests/conftest.py` - promoted the fully-populated `TenantInfo`
  fixture from `test_json_schema_contract.py` to a shared pytest
  fixture so the new drift-guard tests use the same object without
  cross-test imports.

## [1.4.6] - 2026-04-29

**Patch release - skill best-practices alignment.** Docs-only change. No
behavior, schema, or fingerprint changes. Refines the Claude Code skill
and portable AGENTS.md against the official Anthropic skill-authoring
guidance and the `anthropics/skills` reference repo.

### Added

- `agents/claude-code/skills/recon/SKILL.md`: `argument-hint` and `allowed-tools`
  fields in skill frontmatter (per Claude Code skill spec).
- "Before first invocation" section: install probe via `recon --version`
  with explicit user approval before `pip install` - useful when the skill
  is loaded outside the bundled plugin (e.g., copied into Kiro skills).
- "Two invocation modes" section: default mode relays the CLI panel
  verbatim; `--full --json` mode writes to disk and replies with a 3-line
  headline so structured output never floods the conversation context.
- Evidence-citation guidance in the output-voice rules - fingerprint
  claims should reference the record type (MX, TXT, CNAME, etc.).

### Changed

- Tightened skill description; trigger phrases and exclusions still
  surface for skill auto-loading.
- AGENTS.md mirrors the SKILL.md body so Kiro / agents.md-aware tools
  pick up the same install-probe and two-mode invocation patterns.

## [1.4.5] - 2026-04-29

**Patch release - multi-client integration assets.** Docs-only change. No
behavior, schema, or fingerprint changes. Adds drop-in install assets so
Claude Code, Kiro, Windsurf, Cursor, and VS Code users can wire up the recon
MCP server and pick up agent guidance without re-deriving it per session.

### Added

- `agents/claude-code/` - full Claude Code plugin scaffold with `.claude-plugin/plugin.json`,
  `.mcp.json` MCP server registration, and a `skills/recon/SKILL.md` skill that
  teaches Claude when and how to use recon in recon's neutral-observation voice.
- `agents/{kiro,windsurf,cursor,vscode}/` - copy-pasteable MCP config snippets
  and per-client install matrix for non-Claude-Code agents. (Originally
  shipped under `clients/`; consolidated into `agents/` in v1.8.0.)
- `AGENTS.md` at repo root - portable agent guidance in the
  [agents.md](https://agents.md) format. Auto-detected by Kiro and other
  agents.md-aware tools; can be referenced from `.windsurfrules`,
  `.cursor/rules/`, or `.github/copilot-instructions.md`.
- `docs/mcp.md` - Kiro added to the per-client config table; PATH gotcha
  expanded to cover all GUI Electron clients.

### Changed

- README links the new `agents/claude-code/` plugin, sibling `agents/` folders, and
  `AGENTS.md` so users of any supported AI client can find their install path.

## [1.4.4] - 2026-04-27

**Patch release - fingerprint hardening and packaged validator reliability.**
Keeps the public surface stable while tightening broad built-in fingerprint
patterns, making catalog validation work from installed wheels, and grounding
the next roadmap work in validation metrics.

### Added

- Fingerprint match-mode audit reports now include catalog health metrics:
  total fingerprints, detection-rule count, match-mode distribution, metadata
  coverage, and weighted-detection count.
- Roadmap and contributor docs now call out measured fingerprint-library
  priorities, metadata expectations, weak-area notes, and MCP/catalog
  consumption guidance.

### Changed

- Broad Marketo, dmarcian, EasyDMARC, Akamai, AWS ELB, and AWS S3 fingerprint
  substrings were tightened and documented with detection descriptions.
- The 50-domain live validation pass completed with 50 successes, no errors,
  no partial results, no low-confidence results, and only optional `crt.sh`
  degradation observed by `recon doctor`.

### Fixed

- `recon fingerprints check` now uses a packaged validator module instead of
  shelling out to a repo-local `scripts/validate_fingerprint.py` path, so the
  stable command works from installed distributions.

## [1.4.3] - 2026-04-27

**Patch release - validation-driven reliability and local-safety hardening.**
Keeps the public surface stable while bounding long-running MCP state,
tightening local cache paths, and fixing passive DNS/fingerprint edge cases
found during review.

### Changed

- The exposure terminology guard now acts as neutral-copy guidance for
  recon-authored prose, not as a runtime blocklist for domain names, evidence
  strings, or caller phrasing.
- Certificate-transparency ingestion now bounds response processing before
  filtering and sorting, reducing CPU and memory spikes from very large
  provider responses.
- Release workflow OIDC permission tests now pin least-privilege publishing
  scope to the publish job.

### Fixed

- Ephemeral MCP fingerprints now have per-process, per-fingerprint, and total
  detection caps to prevent unbounded process growth.
- CSV batch output now neutralizes spreadsheet formula prefixes in exported
  cells.
- Fingerprint specificity validation now reuses regex safety checks and skips
  specificity evaluation when schema validation already failed.
- Result-cache and CT-cache domain operations now validate and normalize
  domain input before constructing paths, blocking traversal outside cache
  directories.
- Reverse DNS hosting detection now skips non-global A records before issuing
  PTR lookups.
- Subdomain TXT fingerprints now require `subdomain:regex` format, and the
  affected built-in records use explicit subdomain prefixes.

## [1.4.2] - 2026-04-26

**Patch release - doctor status calibration and documentation cleanup.**
Keeps runtime behavior stable while making optional enrichment outages less
alarming and tightening public documentation organization.

### Changed

- `recon doctor` now reports `crt.sh` outages as `WARN` optional enrichment
  degradation instead of a hard `FAIL`. Core source failures still render as
  `FAIL`.
- Documentation is now organized from `docs/README.md`; `docs/roadmap.md` is
  forward-looking and no longer duplicates `CHANGELOG.md`.
- MCP, release, stability, limitations, fingerprint, signal, and weak-area docs
  were refreshed to remove stale counts, stale version wording, and outdated
  command references.

### Removed

- Removed tracked `CLAUDE.md` and added it to `.gitignore`; agent-local guidance
  should stay local instead of shipping in the public repository.

## [1.4.1] - 2026-04-26

**Quality release - sparse-result diagnosis and validation-driven
hardening.** Keeps the public product surface stable while improving how
thin passive evidence is explained, compared, and audited.

### Added

- **Sparse-result diagnosis.** Thin default-panel output now distinguishes
  edge-heavy footprints, custom or self-hosted mail, minimal public DNS, and
  generic sparse public signal cases. The wording remains hedged and points
  users at the passive-only weak-area guidance.
- **Semantic validation comparisons.** Live corpus runs now compare
  per-domain provider, confidence, partial/degraded state, services, slugs,
  and sparse diagnoses. Comparison artifacts classify changes by severity and
  by type (`regression`, `improvement`, `mixed`, `review`, `neutral`).
- **Fingerprint match-mode audit tooling.** New validation helpers audit
  multi-detection fingerprints and classify them as alternate evidence,
  corroborating evidence that needs review, or broad patterns that should be
  tightened before any `match_mode: all` change.

### Changed

- Validation summaries now include sparse-diagnosis rollups so weak-area
  trends are visible across a corpus run.
- Sparse-diagnosis insights are promoted earlier in the default panel so a
  thin run reads as an explained passive result.

### Fixed

- Version metadata fallback and `uv.lock` now track the package version
  consistently.

## [1.4.0] - 2026-04-21

**Hardening release - parser, cache, MCP server coherence, and a
sharper sense of scope.** Targets the three hot paths that real
validation runs have stressed most (malformed upstream responses,
cache round-trips under adversarial inputs, MCP server state
transitions), rebundles the MCP server into the default install,
exposes the fingerprint / signal / profile catalogs as MCP
resources, adds staleness timestamps to every result, and uses the
roadmap to state plainly what recon is - and what it deliberately
leaves to sister tooling.

### Changed

- **MCP is bundled in the default install again.** `pip install
  recon-tool` now installs the `mcp` runtime dependency directly; the
  `recon-tool[mcp]` extra is no longer required. Users who had been
  installing the extra keep working unchanged; users who had avoided
  MCP on purpose can still choose not to run `recon mcp`. No public
  API or CLI surface changed.
- Documentation (`README.md`, `SECURITY.md`, `docs/mcp.md`,
  `docs/security.md`, `docs/stability.md`) updated to reflect the
  bundled-MCP default and the expanded MCP threat model.
- **Fictional-example policy codified and enforced across the tree.**
  The project no longer commits real-company apex domains as examples,
  targets, test corpora, or regression fixtures. Rationale: no upside
  from naming real orgs in a passive-recon tool's public materials;
  accumulating reputational, trademark, and defamation exposure over
  the lifetime of the repository and its forks. See the new
  "Fictional-example policy" section in `CONTRIBUTING.md` for the
  full rule and carve-outs (vendor/product detection names and the
  upstream service hostnames recon itself queries are unaffected).
- **`tests/fixtures/corpus-public.txt` removed.** The 38 real-apex
  corpus previously bundled for `recon fingerprints test <slug>` is
  no longer in-tree. The command now looks for `~/.recon/corpus.txt`
  first, falls back to a new fictional-only `tests/fixtures/
  corpus-example.txt`, and prints a banner when the example file is
  in use so operators know zero matches are expected. Supply your own
  corpus with `--corpus path/to/file` to exercise real detections.
  `docs/performance.md` rewritten to describe methodology without
  naming specific targets.
- **Historical CHANGELOG entries sanitized.** v1.3.0 and v1.2.0
  narrative prose that named specific real apexes has been rewritten
  to describe the behavior in neutral terms. No functional content
  was lost; dated release facts remain intact.
- **`/validation/` gitignore carve-outs.** The directory remains
  ignored for local corpora and result artifacts, with three tracked
  exceptions: `validation/run_corpus.py` (the runner, no company
  names), `validation/corpus-example.txt` (fictional format demo),
  and `validation/README.md` (policy + usage).

### Added

- **MCP resources - `recon://fingerprints`, `recon://signals`,
  `recon://profiles`.** Agents can browse the three catalogs as
  read-only JSON without spending a tool invocation on introspection.
  Each resource is a deterministic projection over the already-loaded
  YAML catalogs (no network calls) - the same data that powers
  `recon fingerprints list` / `recon signals list` / `recon profiles
  list` in the CLI. Changes require `reload_data` to take effect.
- **Staleness timestamps - `resolved_at` and `cached_at` on every
  `TenantInfo`.** `resolved_at` is stamped when live resolution
  produces the result; `cached_at` is populated only by the on-disk
  cache read path. Both flow through the JSON serializer so agents
  can tell at a glance whether they are looking at fresh data or a
  2-minute-old cache hit, and decide whether to re-resolve. Cache
  round-trips preserve `resolved_at` - it reflects when the data was
  first produced, not when the cache entry was last written.
- Reusable live-validation tooling around the existing diverse 50-domain
  corpus. `recon_tool.validation_runner` now summarizes batch JSON,
  compares runs, renders markdown summaries, and
  `validation/run_corpus.py` executes a corpus run through the public
  CLI entrypoint and writes `results.json`, `summary.json`, and
  `summary.md`.
- `docs/roadmap.md` now opens with an explicit "What recon is (and
  what it isn't)" section naming recon as the passive-DNS primitive
  and pointing active scanning, credentialed enrichment, company
  research, and GTM briefing generation at sister tooling. The
  "Intentionally out of scope" list grew accordingly (remote / HTTP
  MCP transport, firmographic enrichment, news / funding / hiring
  feeds, verdicted maturity scores) so external contributors know
  what will be declined up front.

### Fixed

- Hardened malformed-upstream handling for `crt.sh`, CertSpotter, Azure
  metadata, OIDC discovery, and GetUserRealm so invalid or unexpected
  JSON shapes fail explicitly instead of collapsing into generic error
  paths.
- Tightened cache safety and correctness: cache and CT cache now use
  path containment on read/write paths, reject traversal consistently,
  preserve empty `display_name` values on round-trip, and narrow
  filesystem/JSON exception handling.
- Closed MCP server state gaps: cache reload now clears rate-limiter
  state, re-evaluation refreshes cached tenant info, ephemeral
  fingerprint clearing re-merges cached detections, and in-flight tenant
  lookups reserve and release rate-limit slots atomically.
- Reworked fingerprint derived caches into a lock-coherent typed cache
  state so ephemeral inject/clear/reload operations keep detection and
  M365-derived views consistent.

### Validation

- Added regression coverage for malformed upstream bodies, cache
  traversal and round-trip edge cases, server in-flight lookup
  semantics, ephemeral fingerprint cache invalidation, and
  validation-runner summaries.
- Quality gate green on release prep: `pytest tests` (1585 passed, 4
  deselected), `ruff check .`, and `pyright recon_tool tests`.

## [1.3.1] - 2026-04-21

**Security patch - six findings resolved.** External static-analysis
pass surfaced a cluster of low-to-medium issues, mostly reachable only
via local CLI or MCP stdio, but all worth closing. No behavior changes
for legitimate use; each fix tightens a containment boundary that was
previously relying on trust rather than enforcement.

### Fixed

- **Unbounded ephemeral fingerprint injection (MCP DoS)** - Medium.
  ``inject_ephemeral_fingerprint`` had no cap; a long-running MCP
  server could be driven into unbounded memory growth by a
  prompt-injected client calling the tool in a loop. Added a
  ``_MAX_EPHEMERAL_FINGERPRINTS = 100`` cap in
  ``recon_tool.fingerprints``; the MCP tool surfaces capacity
  errors as clean JSON rejections (``EphemeralCapacityError``).
- **Release workflow OIDC scope** - Medium. ``id-token: write`` was
  granted at the workflow level, meaning ``test`` and ``build`` jobs
  (which install and execute dependency code) could mint PyPI
  trusted-publisher tokens. Compromised dependency = publishing
  artifact under our identity. Workflow default is now
  ``contents: read``; each job opts into the scope it actually needs.
  Only ``publish-pypi`` and ``github-release`` request elevated
  permissions.
- **CSV formula injection** - Medium. ``display_name`` originates
  from the attacker-influencable ``FederationBrandName`` response
  and was written verbatim to CSV cells. A value starting with ``=``
  / ``+`` / ``-`` / ``@`` / ``\t`` / ``\r`` would execute as a
  formula when the CSV is opened in a spreadsheet. Added
  ``_csv_safe`` which prefixes unsafe leading characters with a
  single quote; applied to every textual field in
  ``format_tenant_csv_row``.
- **Specificity gate unbounded regex** - Low. ``evaluate_pattern``
  compiled and searched regexes against the synthetic corpus
  without the length cap that ``_validate_regex`` enforces at
  schema-validation time. A pathological regex submitted via PR,
  MCP ephemeral injection, or ``recon fingerprints new`` could
  hang CI or the local wizard. Added a 500-char length guard in
  ``evaluate_pattern`` itself so the gate is safe even when called
  outside the schema validator.
- **Cache clear path traversal** - Low. ``recon cache clear
  <domain>`` forwarded the raw domain to ``cache.cache_clear``
  which built a path directly from it. A crafted argument like
  ``../../.config/settings`` escaped the cache directory and
  unlinked whatever ``.json`` file the user could touch. Added
  ``_safe_cache_path`` using ``Path.is_relative_to`` plus an input
  character guard; traversal attempts now return ``False``
  (nothing deleted) rather than following the path.
- **CT cache ``_safe_path`` prefix-bypass** - Low. The containment
  check used ``str(path).startswith(str(cache_dir.resolve()))`` -
  path-prefix rather than path-aware. A crafted domain like
  ``../ct-cache-malice/evil`` resolved to a sibling directory whose
  path string still matched the prefix. Replaced with
  ``Path.is_relative_to`` and added a character-level input guard.
  Same class of bug as the cache-clear traversal; same fix shape.
- **PTR lookup on private IPs** - Low. ``_detect_hosting_from_a_record``
  unconditionally reverse-resolved the apex A-record IP, including
  RFC1918 / loopback / link-local addresses. A malicious domain
  could publish an A record pointing to an internal IP and the
  tool would ask the operator's resolver for the internal PTR -
  leaking internal DNS names into recon's output. Added
  ``ip.is_private or ip.is_loopback or ip.is_link_local or
  ip.is_reserved or ip.is_multicast`` check before the PTR query.
- **crt.sh unbounded accumulation** - Low. ``filter_subdomains``
  added every matching name into a set, then sorted the full set
  before slicing to ``MAX_SUBDOMAINS``. A domain with a very large
  CT history (tens of thousands of entries) would force the whole
  set into memory and sort it. Added a ``hard_cap = max_count * 10``
  break during accumulation - enough headroom to still prioritize
  high-signal subdomains correctly, bounded enough that no single
  domain can spike CPU.

### Validation

- Full quality gate: ruff check + format clean, pyright 0 errors,
  bandit 0 issues, actionlint clean.
- Pytest: 1550 pass (prior count).
- Each fix is targeted at a reported finding; none of them change
  observable behavior for legitimate input (no CHANGELOG entries
  needed in user-facing docs beyond this one).

## [1.3.0] - 2026-04-21

**Portfolio discovery in batch mode.** When ``recon batch`` resolves
multiple domains, the JSON output now surfaces two new correlation
signals: cryptographically-strong tenant-ID sharing (same M365
customer account) and hedged display-name overlap (same brand after
normalization). Uses data already collected - zero new network
calls, zero new sources.

### Added

- **Tenant-ID clustering (``shared_tenant``)**: When 2+ domains in a
  batch share the same Microsoft 365 tenant ID, each domain's JSON
  entry carries a ``shared_tenant`` list naming the other peers.
  Cryptographically strong - same tenant ID = same M365 customer
  account. Not hedged; this is provable via OIDC discovery. Three
  sibling apexes belonging to the same corporate group collapse to a
  shared peer set in the batch output.
- **Display-name clustering (``shared_display_name``)**: When 2+
  domains' tenant display names normalize to the same key,
  each entry carries a ``shared_display_name`` list with the raw
  display names (for audit), the normalized key, and the peer
  domains. Conservative match - exact normalized equality only
  (``Synthetic Delta Corp`` + ``Synthetic Delta Corp.`` cluster; ``Synthetic Delta`` + ``Synthetic Delta Holdings``
  do not). Normalization strips one trailing corporate suffix
  (``inc`` / ``llc`` / ``gmbh`` / etc.) and collapses whitespace /
  punctuation.
- ``recon_tool.clustering.compute_tenant_clusters`` and
  ``compute_display_name_clusters`` - pure functions exposed for
  the MCP server and external consumers who want to run the
  clustering on their own ``TenantInfo`` lists. 11 new unit tests
  covering the tenant / display-name paths.

### Use case

Portfolio discovery on a candidate domain list. An IT reseller or
M&A analyst runs ``recon batch portfolio.txt --json`` and the output
names which apexes belong to the same corporate group, without any
additional lookups. Pairs well with the existing
``shared_verification_tokens`` clustering for a three-tiered signal:

- **Tenant-ID match** - provable, same customer account.
- **Display-name match** - hedged, same brand text.
- **Verification-token match** - hedged, same operator-scoped
  credential.

The JSON fields are independent - a pair can appear in one, two, or
all three. Downstream consumers rank them however they like.

### Validation

- Portfolio smoke test on a three-apex group sharing a single M365
  tenant and display name: all three fields populate correctly with
  symmetric peer lists.
- Full test suite: 1550 pass (1539 + 11 new clustering tests).
- Static gate: ruff + format + pyright + bandit + actionlint all
  clean.

## [1.2.1] - 2026-04-21

**Security patch.** The MCP ``inject_ephemeral_fingerprint`` tool
validated schema but bypassed the v1.2 specificity gate. A caller
could inject a pattern like ``cname:\.com$`` and poison every
subsequent lookup in that server process with false positives. Blast radius
was bounded to memory in one process and could not persist, but the gate
is cheap and worth enforcing everywhere the catalog accepts input.

### Fixed

- ``inject_ephemeral_fingerprint`` now runs every detection pattern
  through ``recon_tool.specificity.evaluate_pattern`` and rejects the
  injection with a clear diagnostic when any pattern exceeds the 1%
  synthetic-corpus match threshold. Same gate as
  ``recon fingerprints check`` and ``recon fingerprints new``, so
  the three ingress paths are now consistent.

### Validation

- Expanded validation sweep against a 31-domain weak-area corpus
  (heavy-Cloudflare, higher-ed, Chinese/APAC, regulated verticals,
  EU fintech, self-hosted, IDN). All 31 resolve without error;
  sparse results on thin-signal domains are honest, not empty.
- Security audit pass on userrealm.py (defusedxml + xml_escape both
  confirmed in use), the ``recon fingerprints check`` subprocess
  path (list form, sys.executable, no shell), and the MCP rate
  limiter (monotonic clock, soft cap, no bypass via table-flood).
  No other findings.

## [1.2.0] - 2026-04-21

**Contribution trust.** v1.1 gave contributors the plumbing; v1.2 adds
the guards that make contributions *safe to merge*. A
pattern-specificity gate rejects over-broad regexes before review; a
scaffolding wizard runs every check before emitting YAML; a test
command resolves a new fingerprint against a public domain corpus so
contributors can see what it actually matches. No engine changes, no
new detections - the point is that the next wave of detections
(community or solo) can't accidentally poison the catalog.

### Added

- **Pattern-specificity gate** (`recon_tool/specificity.py`). Every
  detection regex is now matched against a synthetic adversarial
  corpus of ~1500 strings spanning TXT / SPF / MX / CNAME / NS. If a
  pattern matches more than 1% of the corpus, `recon fingerprints
  check` rejects it as over-broad. The threshold is calibrated so all
  227 built-in entries pass, while a deliberately-broad pattern like
  `cname:\.com$` fails with a clear diagnostic. Off by default with
  `--skip-specificity` for debugging; on by default for PRs and CI.
- **`recon fingerprints new <slug>`** - scaffolding wizard. Prompts
  for name, category, detection type, pattern, optional description
  and reference. Runs three guards before emitting YAML: (1) slug
  uniqueness against the built-in catalog, (2) schema validity,
  (3) specificity. Prints a paste-ready entry or writes to a file
  via `--output`.
- **`recon fingerprints test <slug>`** - runs one fingerprint against
  a domain corpus and reports which match. Contributors point at their
  own corpus with `--corpus path/to/file` or drop a list at
  `~/.recon/corpus.txt`. Helps answer "is my regex too loose or too
  tight" without hand-resolving DNS.
- **`tests/fixtures/corpus-example.txt`** - fictional-company example
  corpus showing the expected file format. Real-company corpora are
  never committed; see CONTRIBUTING.md for the rationale. (Note:
  earlier point releases bundled a public-companies corpus; it was
  removed in v1.4.0.)
- **`docs/weak-areas.md`** - honest list of deployment shapes where
  recon looks sparse by design (heavy-CDN orgs, Chinese / APAC tech
  stacks, regulated verticals behind web proxies, fully self-hosted
  shops, parked / portfolio apexes). Names what the sparse result
  actually means and what to do instead of over-interpreting it.
  Linked from limitations.md.
- **`docs/performance.md`** - published batch wall-clock and memory
  numbers (50 / 100 / 500 domains), methodology for reproducing,
  per-step time budget. Stops users from guessing where the latency
  goes.

### Changed

- **`scripts/validate_fingerprint.py`** - now runs the specificity
  gate on every pattern in addition to the runtime schema check and
  cross-file duplicate-slug check. `--skip-specificity` opts out
  when debugging.
- **CONTRIBUTING.md** - fingerprint PR section updated for the new
  `fingerprints new` / `test` / `check` workflow. New "engine changes
  go through a design doc" heads-up before the signals section -
  fingerprints are data and can iterate freely; signal / fusion /
  absence engines are inference code and bad changes affect every
  domain recon analyses.

### Deferred to post-1.2

- **Bulk fingerprint additions.** Each QA round during v1.2 planning
  suggested 20-100 new fingerprints, mostly based on pattern-matching
  `<vendor>-domain-verification=` by analogy. Spot-checks showed
  most of those patterns don't exist - the SaaS in question uses
  account-based verification or API-key auth rather than DNS.
  Catalog growth is welcome but each entry needs vendor-doc
  verification, which is proper v1.2+ work. The infrastructure in
  this release makes each new entry a small PR going forward.

**Contribution-ready.** The fingerprint catalog is now one file per
category, new CLI inspect commands let contributors audit the data
without opening YAML, and CI gained an `actionlint` gate so the kind
of unresolvable-action-ref regression that broke the first v1.0.2 tag
can't reach `main` again. No user-visible detection or output changes
in this release - this is infrastructure for everything that comes
next.

### Added

- **Per-category fingerprint layout** - ``recon_tool/data/fingerprints.yaml``
  (one 60KB file, 235 entries, 8 duplicate slugs) is now
  ``recon_tool/data/fingerprints/`` (8 per-category files, 227 unique
  slugs, zero duplicates). The eight files:
  - ``ai.yaml`` - AI / LLM providers, agent frameworks.
  - ``email.yaml`` - email platforms, gateways, DMARC / DKIM tooling.
  - ``security.yaml`` - EDR, SIEM, IdP, zero-trust, credential hygiene.
  - ``infrastructure.yaml`` - cloud, CDN, DNS, CAs, CI/CD.
  - ``productivity.yaml`` - suites, helpdesk, HR, knowledge.
  - ``crm-marketing.yaml`` - CRM, sales intel, ad platforms.
  - ``data-analytics.yaml`` - warehouses, BI, observability.
  - ``verticals.yaml`` - education, nonprofit, payments, misc.
  The loader globs ``data/fingerprints/*.yaml`` in sorted order; custom
  ``~/.recon/fingerprints.yaml`` still works as a single file and a
  new ``~/.recon/fingerprints/`` directory is also accepted for users
  who want per-category organization of their overrides. Slug order
  after load is deterministic and identical to the monolith except
  for the 8 duplicates, which are now collapsed into single entries
  with their detection rules merged.
- **``recon fingerprints list`` / ``show`` / ``check``** - contributor
  and user inspection commands for the fingerprint catalog.
  - ``list`` supports ``--category`` substring and ``--type`` exact
    filters, plus ``--json`` for scripting.
  - ``show`` renders the full definition (detection rules, patterns,
    descriptions, references) for a single slug. Synthetic slugs
    (``exchange-onprem``, ``self-hosted-mail``) that are emitted by
    source-layer probes rather than loaded from YAML are documented
    here too - users who see those slugs in their output can always
    find provenance without grepping code.
  - ``check`` validates the catalog against the runtime schema and
    surfaces cross-file duplicate slugs. Wraps
    ``scripts/validate_fingerprint.py`` with sane defaults.
- **``recon signals list`` / ``show``** - same pattern for the signal
  catalog. ``show`` surfaces candidates, metadata conditions,
  contradictions, requires-signals chains, expected-counterparts,
  and positive-when-absent lists - everything the absence and
  two-pass evaluators look at.
- **``actionlint`` in pre-commit and CI.** Catches unresolved action
  refs, bad shell in ``run:`` blocks, and deprecated expressions at
  commit time and in a dedicated ``workflow-lint`` CI job. The
  v1.0.2 release regressed because ``astral-sh/setup-uv@v8`` isn't a
  real floating tag; ``actionlint`` catches that class of error
  locally and in CI. Pinned to ``actionlint@v1.7.12``.
- **``scripts/split_fingerprints.py``** - the one-shot migration
  script that produced the split, kept in the repo for audit. A
  reviewer can re-run it against the pre-split monolith to verify
  the split is reproducible.

### Changed

- **``scripts/validate_fingerprint.py`` now accepts a directory** and
  pools slugs across files for a cross-file duplicate-slug check.
  Single-file invocation is unchanged - directories are an additive
  capability for the split-catalog layout.

### Docs

- **CONTRIBUTING.md** updated for the split-catalog layout -
  "find the right file" step added, PR template checklist swapped to
  the new ``recon fingerprints check`` command, fingerprint-add
  recipe now shows ``recon fingerprints show <slug>`` as the
  post-add verification step.
- **CLAUDE.md** reflects 227-fingerprint count (down from 235) and
  the new ``data/fingerprints/`` directory layout.

### Process guards

The first v1.0.2 tag push failed because ``astral-sh/setup-uv@v8``
isn't a published floating tag - only ``v8.0.0`` and ``v8.1.0`` exist.
Two guards now prevent that class of regression:

1. ``actionlint`` runs in pre-commit on every commit touching
   ``.github/workflows/``.
2. ``actionlint`` runs as the first job in CI so PRs with unresolved
   action refs fail at the workflow-lint stage, before any Python
   work executes.

Before future tag pushes, verify each bumped action ref exists with
``gh api repos/<owner>/<repo>/git/refs/tags/<ref>`` - especially for
actions that don't publish floating majors.

## [1.0.2] - 2026-04-20

**Polish pass.** Toolchain current, test suite pyright-clean, dead code
removed, seven bug fixes surfaced by CLI edge-path audits, provider
attribution improved for self-hosted mail, "we looked and found nothing"
now returns a sparse result instead of an error. Validated against
450 domains across eight corpora (international banking, pharma,
mining, telecom, logistics, government agencies, UN / NGO bodies, EDU /
state gov, DTC startups, plus a 50-domain diverse-industry sweep
covering big tech, automotive, luxury, fast food, Chinese giants,
aerospace, and retail) with zero errors and zero regressions.

### Added

- **Python 3.13** added to the CI test matrix and the package
  classifiers. Supported runtimes are now 3.10 / 3.11 / 3.12 / 3.13.
- **Dependency update automation** configured for GitHub Actions and Python
  dependencies with weekly cadence and patch/minor grouping.
- **README badges** - CI status, PyPI version, supported Python
  versions, license.
- **CI pyright scope now covers `tests/`** so type-annotation drift
  can't re-accumulate the way it did (652 errors pre-polish → 0 now).

### Changed

- **Email security score is now an inventory, not a grade.** The
  score line went from `Email security 3/5 good (DMARC reject, DKIM,
  SPF strict)` → `Email security 3/5: DMARC reject, DKIM, SPF strict`
  → `Email security: DMARC reject, DKIM, SPF strict`. The verdict
  adjectives (`weak` / `basic` / `moderate` / `good` / `strong` /
  `excellent`) came out first - we see apex DNS, not the full posture,
  so a graded assertion is more than the tool can honestly make. The
  `N/5` fraction came out next: even without the adjective, `3/5` was
  read as "mediocre" and the controls aren't equally weighted anyway
  (DMARC `reject` is load-bearing, BIMI is decorative). The machine-
  readable `email_security_score` field stays in `--json` for
  consumers that genuinely need to sort or filter. The same `/5`
  stripping now extends to `--posture` and `--exposure` panels and
  to `compare_postures` assessment summaries so the format stays
  consistent everywhere.
- **Provider attribution no longer over-credits on-prem Exchange.**
  Large orgs with self-operated mail infrastructure used to fall
  through to `Exchange Server (on-prem / hybrid)` as the primary
  provider whenever `owa.<apex>` / `autodiscover.<apex>` resolved,
  even when the public MX clearly routed through their own
  operator-owned mail hostnames. A synthetic `self-hosted-mail`
  slug now fires when MX records exist and none of them match a
  recognized cloud provider or gateway fingerprint, and that slug is
  recognized as a primary email provider in the topology computation.
  The Exchange on-prem detection still fires as a secondary service
  signal in the same output, so the hybrid-identity reality of these
  orgs is still visible - it's just no longer promoted to the
  Provider line. Roughly a third of the diverse 50-domain validation
  corpus got more accurate Provider lines as a result, most of them
  large industrial and APAC orgs running self-operated mail.
- **DKIM inference behind commercial gateway.** When MX points to a
  commercial email gateway (Proofpoint, Mimecast, Cisco IronPort,
  Barracuda, Trend Micro, Trellix, Symantec) AND DMARC is enforcing
  (`quarantine` or `reject`), the score now credits DKIM with the
  annotation `DKIM (inferred via Proofpoint)` (etc.). Fortune-500
  orgs with enforcing DMARC almost always DO sign with DKIM - just at
  custom selectors the tool can't enumerate. Without this inference
  the apex score penalized orgs for a control they effectively have.
  The inference chain is visible in the score string so the user can
  audit it.
- **`partial=True` semantic tightened.** The JSON `partial` flag now
  fires only when a core source (OIDC, UserRealm, Google Identity,
  DNS) is degraded - not when a CT provider (crt.sh, CertSpotter) is
  degraded. CT pipelines are chronically flaky and the code handles
  their degradation gracefully via fallback + cache, so they shouldn't
  flip the global `partial` bit. The per-source status is still
  surfaced in the `degraded_sources` list for consumers who want the
  detail.
- **GitHub Actions bumped to current majors** - `checkout v4 → v6`,
  `setup-python v5 → v6`, `setup-node v4 → v6`, `upload-artifact v4 →
  v7`, `download-artifact v4 → v8`, `setup-uv v5 → v8`,
  `action-gh-release v2 → v3`. Node 20 deprecation warnings are now
  gone; `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24` workaround removed since
  all pinned actions target Node 24 natively.
- **"All sources empty, no errors" returns a sparse `TenantInfo`**
  instead of raising `ReconLookupError`. "We looked and found nothing"
  is a valid observation, not a failure. Previously, a domain with
  no detectable patterns would get a hard error in single-domain
  lookups and an `error` entry in batch output; now both paths emit
  a clean result with `provider = "Unknown (no known provider
  pattern matched)"`. Raising is reserved for the case where every
  source actually failed.

### Removed

- **Three more narrative-judgment signals** in the same class as
  Shadow IT Risk / Complex Migration Window / Governance Sprawl
  (retired in v1.0.1). None were observation - they stitched two
  observable facts into a critique that only DNS can't actually make.
  - `Security Stack Without Governance` - "security investment may
    lack email-layer controls" is opinion; the two underlying
    observations (security tools + DMARC not enforcing) are already
    visible on their own lines.
  - `AI Adoption Without Governance` - inferred "shadow AI
    deployment" from absence of specific IDPs; speculative.
  - `DevSecOps Investment Without Email Governance` - inferred that
    engineering security investment "hasn't extended to email";
    pure narrative.
- **Dead code in `sources/dns.py`** - `_safe_resolve_sync` and
  `_set_resolver` had no callers (including tests). The sync resolver
  helper was for a testing pattern that's no longer in use; the
  resolver override was never wired up.

### Docs

- **`docs/roadmap.md` trimmed from 631 → 207 lines.** The historical
  per-release detail now points to CHANGELOG.md (source of truth);
  the post-1.0 ethos and "intentionally out of scope" sections kept
  but tightened. Invariants and priority order stay front and center.
  Added a concrete v1.1 target describing the planned split of
  `fingerprints.yaml` into per-category files - design sketch, scope
  breakdown, non-goals, and the reason it waits for v1.1 (coherent
  with the community-contribution pipeline).
- **`docs/signals.md` trimmed from 130 → 74 lines.** Large
  auto-generated signal table removed (signals.yaml itself is the
  source of truth and shorter). Design rules section added listing
  retired signals and the invariant each violated, so contributors
  can see why something wouldn't be accepted before proposing it.
- **`docs/fingerprints.md` tightened.** Detection-types table kept.
  Added a concrete "Testing a new fingerprint" recipe. Email security
  score table updated for the gateway-inferred DKIM path. Removed
  implementation-detail notes about enrichment tiers that belonged in
  code comments, not user docs.

### Fixed

- **Test suite pyright-clean.** 652 errors → 0. `tests/` execution
  environment relaxes `reportPrivateUsage` (tests legitimately
  white-box private APIs) and parameter-type rules (pytest fixtures
  inject by name), but keeps structural checks on. Fixture generators
  get proper `Iterator[T]` return types; test assertions now
  null-guard before calling `re.match`; unused destructured variables
  are prefixed with `_`.
- **`recon cache clear` now actually clears everything for a domain.**
  Previously it only cleared the CT subdomain cache at
  `~/.recon/ct-cache/`; the TenantInfo result cache at
  `~/.recon/cache/` was left untouched and silently served stale
  JSON on subsequent runs. This surfaced during validation - after
  updating recon, a cached TenantInfo result kept showing retired
  signals like "AI Adoption Without Governance" even after a
  `cache clear <apex>`. The command now clears both caches and
  reports each count separately; `cache_clear` / `cache_clear_all`
  helpers added to `cache.py`.
- **`recon doctor` no longer emits empty error messages.** Many
  `httpx` exception classes (`ReadTimeout`, `ConnectTimeout`) raise
  with an empty message string, so `str(exc)` rendered as
  `FAIL  crt.sh (cert transparency) - ` with nothing after the em-
  dash. A module-level `_fmt_exc(exc)` helper falls back to
  `type(exc).__name__` when the message is empty; applied
  everywhere in `cli.py` that previously did `render_error(str(exc))`
  on a catch-all `Exception`.
- **Wildcard-DNS guard on Exchange-on-prem detection.** Domains that
  point `*.<apex>` at a single IP (so every subdomain resolves to
  the same address) used to trigger every probed prefix in
  `_detect_exchange_onprem` and get mislabelled as running Exchange
  Server. The detector now probes a nonsense prefix and bails when
  it also resolves - an unambiguous wildcard signature.
- **IDN / Punycode domains accepted.** The validator regex anchored
  the TLD at `[a-z]{2,}`, which rejected every `xn--`-prefixed TLD
  (e.g. `xn--p1ai` for Russian, `xn--fiqs8s` for Chinese). The
  pattern now allows letters, digits, and internal hyphens in the
  TLD (letter-first, alphanumeric-last, min two chars) so IDN
  domains are accepted while numeric and hyphen-bracketed TLDs
  still reject.
- **`--profile` no longer a no-op without `--posture`.** Profile
  lenses only apply to posture observations, so running
  `recon <domain> --profile fintech` without a posture-enabling
  flag silently produced identical output to `recon <domain>`.
  Passing `--profile` now auto-enables posture rendering.
- **Hardening Controls panel renders colored check marks.** The
  `--exposure` panel built its ✓/✗ line with f-string Rich markup
  (`[green]✓[/green]`) appended to a `Text` object. `Text.append`
  does not parse markup, so those tags rendered as literal text.
  Style is now passed via the `style=` kwarg.

### Refactor

- **Test file names de-versioned.** Fourteen test files named after
  the QA round or release when they were written (e.g.
  `test_v090_absence.py`, `test_v093_clustering.py`) renamed to
  their subject matter (`test_absence_engine.py`,
  `test_clustering.py`, etc.) via `git mv` so history is preserved.
  Docstring leading lines also stripped of the `v0.9.x - QA Round
  N:` preamble. Post-1.0 the version of introduction is no longer
  meaningful context for where tests live.

## [1.0.1] - 2026-04-20

**Accuracy & reliability pass** driven by a 150-domain validation sweep
across large, mid-size, and regional targets in multiple regions and
industries. All fixes stayed inside the project invariants
(passive-only, zero credentials, no engine expansion, hedged output).

### Fixed

- **`autodiscover.<apex>` no longer false-positives `exchange-onprem`
  on Microsoft 365 cloud tenants.** The detector queried type A and
  relied on dnspython returning empty when the name was a CNAME to
  `autodiscover.outlook.com`. dnspython chases CNAMEs on type-A
  queries, so M365 domains were flagging as on-prem. The detector now
  queries CNAME first for `autodiscover` and suppresses when the
  immediate target is in the M365 cloud zone
  (`*.outlook.com` / `*.office.com` / `*.cloud.microsoft` /
  `*.mail.protection.outlook.com` / `*.office365.com`). Genuine
  hybrid Exchange (CNAME to org-owned infra, or direct A) still
  fires. Other prefixes (`owa`, `outlook`, `exchange`, `mail-ex`,
  `webmail`) keep the A-or-CNAME path - those names are on-prem-only
  when they resolve. See `sources/dns.py::_detect_exchange_onprem`,
  regression tests in `test_dns_subdetectors.py::TestExchangeOnpremAutodiscover`.

- **`GoogleIdentitySource` no longer claims "Managed" Workspace on
  every domain.** The `_is_workspace_domain` heuristic searched the
  `accounts.google.com/ServiceLogin` response body for the `hd=`
  parameter and the word `"identifier"`. Both are always present in
  Google's sign-in page (the URL parameter is echoed verbatim into
  the body, and the page is an identifier-capture form), so the
  check returned `True` for every queryable domain - including
  fabricated ones. The body heuristic is removed. Managed Workspace
  customers are still detected via the DNS fingerprint path (MX
  `aspmx.l.google.com`, SPF `_spf.google.com`, DKIM
  `google._domainkey`, GWS module CNAMEs to `ghs.googlehosted.com`).
  A federated IdP redirect still triggers the `Federated` detection.
  This removes the cascade of phantom "Dual Email Provider",
  "Google-Native Identity", and "Google Cloud Investment" insights
  from M365-primary targets.

- **`cisco-identity` TXT no longer mis-attributed as the SSO IdP.**
  The slug fires on the `cisco-ci-domain-verification=` TXT token,
  used by many Cisco products (Duo, Customer Identity, Secure Email,
  Intersight) - not specifically the org's SSO IdP. Removed from
  `_IDP_SLUG_MAP` in `insights.py`; the federated-auth insight now
  correctly falls back to the generic `ADFS/Okta/Ping` line when
  no dedicated IdP evidence is present. The slug still emits the
  `Cisco (Identity)` service fact.

- **12% of big-enterprise lookups timed out at the 120s aggregate
  budget - now 0%.** Root cause: when CertSpotter rate-limited with
  HTTP 429, `_RetryTransport` slept **30s × 3 retries = 90s** per
  query while CertSpotter's own application code already handled 429
  by breaking the pagination loop. HTTP-layer retry was fighting
  application-layer handling and burning the aggregate budget.
  `http_client(retry_transient=False)` is a new flag that skips
  `_RetryTransport`; CertSpotter opts in. Page-level
  `@retry_on_transient` on `_fetch_page` also removed for the same
  reason (3 × 8s = ~25s of accumulated delay on slow-CT targets).
  Single-domain lookup time on the worst-case targets went from 120s
  (timeout) to 2-12s.

### Changed

- **`CertSpotter _MAX_PAGES` 4 → 2, `_CT_TIMEOUT` 8 → 6,
  `MAX_RELATED_ENRICHMENTS` 25 → 15.** Budget tightening to reduce
  per-domain fan-out under batch concurrency. Two CertSpotter pages
  still cover ~500 certs, and the enrichment cap is prioritised so
  high-signal subdomain prefixes (auth, login, sso, api, …) survive.

### Removed

- **`Shadow IT Risk` signal.** Framed sanctioned enterprise SaaS
  (Canva / Mailchimp / Airtable) as "shadow IT risk" at any scale.
  Violated the "observable facts in neutral language" invariant and
  misread the common-case consumer-brand SaaS footprint of a large
  org as a defect.
- **`Complex Migration Window` signal.** Narrative synthesis on top
  of "security stack + dual-provider email" observations. The tool
  can observe the two inputs; it cannot observe that a migration is
  in progress. Violated the "no timeline narrative generation"
  invariant.
- **`Governance Sprawl` signal.** Depended on `Shadow IT Risk`.
- **`expected_counterparts` on `AI Adoption` and
  `Agentic AI Infrastructure`.** Produced "Missing Counterparts"
  absence insights like `AI Adoption - Missing Counterparts: Lakera,
  Okta, CyberArk, Beyond Identity` on nearly every AI-adopting
  target. The listed slugs were vendor recommendations, not
  observable co-occurrence relationships - their absence does not
  constitute a defect observable from DNS. The
  `expected_counterparts` mechanism itself remains available for
  user-customised signals in `~/.recon/signals.yaml`; no built-in
  signal currently uses it.

### Note on exit codes

Sparse-evidence domains (zero slugs, zero services, no provider pattern
matched) previously raised `ReconLookupError` in the CLI path, printed
"No information found for {domain}", and exited with code 3
(`EXIT_NO_DATA`). They now render a clean `Unknown` panel and exit 0.

- Scripting consumers that relied on exit code 3 as "no data found"
  must switch to checking the JSON output's `provider` field for
  `"Unknown (no known provider pattern matched)"` or the empty
  `services` / `slugs` lists.
- Exit code 3 still fires when the resolver genuinely can't get a
  clean result from *any* source (all sources errored). That's rare.
- Exit code 4 (`EXIT_INTERNAL`) is unchanged.

### Note on upgrade

- `google_auth_type` is now `None` more often: the source only
  populates it on a genuine federated redirect. Any consumer that
  depended on the previous "Managed" default on every domain was
  consuming a bogus signal - switch to the DNS-backed
  `primary_email_provider` / slug set instead.
- Consumers relying on `Shadow IT Risk`, `Complex Migration Window`,
  or `Governance Sprawl` in the signals output will no longer see
  those names. No replacement - the underlying observations (consumer
  SaaS slugs, dual-provider detection, security stack) are still
  present in the slug/service set.

## [1.0.0] - 2026-04-17

**Stability commitment.** recon is now 1.0. From this release forward,
all surfaces tagged **stable** in `docs/stability.md` will not break
between patch or minor releases. Breaking changes require a major
version bump and a deprecation window.

### Added

- **`docs/security.md`** - engineering-level threat model. Trust
  boundaries, attack surface, mitigations with file:line refs
  (validator.py domain regex, http.py SSRF protections, fingerprints.py
  ReDoS heuristic, ct_cache.py path-traversal guard), known limitations
  (DNS rebinding with sub-second TTLs), out-of-scope.
- **`docs/limitations.md`** - honest inventory. What recon can't see
  (Copilot/Gemini, heavily proxied domains, internal services,
  network-level facts), what it underclaims on (bundled AI, dormant
  dual-provider, sovereignty when OIDC is silent), known noise
  patterns, when to reach for something else.
- **`docs/schema.md`** - JSON output contract. ~45 stable fields
  documented with types, nullability, allowed values. Nested object
  shapes for `cert_summary` and `bimi_identity`. Experimental fields
  (`slug_confidences`) separately tagged.
- **`tests/test_json_schema_contract.py`** - conformance tests that
  assert every stable field is present and correctly typed on both
  rich and sparse fixtures.
- **`scripts/release.py`** - semi-automated release flow. Clean-tree
  check, version-bump consistency, CHANGELOG entry check, quality gate
  (ruff + pyright + pytest + coverage), git commit + tag, confirm-to-push.
  `--dry-run` flag for testing.
- **`docs/release-process.md`** - full release documentation. Human
  half (`scripts/release.py`), automated half (GH Actions), pre-release
  checklist, hotfix workflow, yanking a broken release, SemVer
  commitment, Python support policy.

### Changed

- **`docs/stability.md`** - fully expanded. Full CLI flag table, all 17
  MCP tools (stable), full list of stable JSON fields, CLI exit codes,
  YAML schema commitments, Python support policy (CPython N-2 = 3.10,
  3.11, 3.12).
- **JSON output - always-present fields.** `detection_scores`,
  `cert_summary`, and `bimi_identity` are now always present in
  `--json` output (null when unavailable) rather than conditionally
  emitted. Backward compatible for consumers that check
  `field is not None`; slight breaking change for consumers that
  relied on `field in payload` as a presence check. This was a
  schema-conformance fix for 1.0.
- **Dev Status classifier** - `pyproject.toml` updated from
  `Development Status :: 4 - Beta` to
  `Development Status :: 5 - Production/Stable`.

### Roadmap

- All v1.0 deliverables shipped. `docs/roadmap.md` updated accordingly.
- Post-1.0 ideas (NetworkX graph, portfolio detection, temporal CT
  evidence, feedback-driven posterior tuning) remain in the roadmap as
  non-commitments.

## [0.11.0] - 2026-04-17

Community & confidence. The biggest build yet. Three themes:
(1) `--confidence-mode strict` drops hedging qualifiers when evidence
is dense. (2) Community fingerprint pipeline enables outside
contributions without drowning in bad YAML. (3) Bayesian fusion
(experimental) replaces the three-bucket detection-score threshold
with a principled per-slug posterior.

### Added

- **`--confidence-mode {hedged,strict}`** CLI flag. Default `hedged`
  (unchanged). `strict` drops hedging qualifiers ("observed",
  "likely", "indicators") on dense-evidence targets (High confidence
  + 3+ corroborating sources). Sparse-data output is never touched -
  the "never overclaim when evidence is thin" invariant stays
  load-bearing. New module `recon_tool/strict_mode.py`.
- **Community fingerprint pipeline.**
  - `scripts/validate_fingerprint.py` - local validator that runs the
    same checks recon uses at runtime (regex safety, required fields,
    detection types, weight range, `match_mode`). Exits 0/1 with
    per-entry error messages.
  - `CONTRIBUTING.md` - new fingerprint submission section with
    validate command, chained-pattern guidance, PR checklist.
  - `.github/ISSUE_TEMPLATE/fingerprint_request.md` - structured
    template for requesting new fingerprints.
  - `.github/PULL_REQUEST_TEMPLATE/fingerprint.md` - structured
    template for fingerprint PRs.
  - `.github/workflows/ci.yml` - new `validate-fingerprints` job that
    runs on every PR.
- **Bayesian fusion (experimental).** New module `recon_tool/fusion.py`.
  Pure-Python Beta conjugate update. Per-source priors ranked by
  informational content (OIDC > DKIM > MX > TXT > A/CNAME). Opt-in
  via `--fusion`. Emits `slug_confidences` tuple on TenantInfo and
  in `--json` output. Tagged **experimental** - algorithm and field
  shape may evolve.
- **`docs/stability.md`** - stability policy for 1.0. Lists stable
  vs experimental surfaces. Documents what "stable" means
  (backward-compat guarantee between patch and minor releases).

### Changed

- No behavior change by default. Strict mode, fusion, and the
  community pipeline are all opt-in or additive.

## [0.10.3] - 2026-04-17

MCP agent ergonomics. The server now self-documents so AI clients
call tools correctly without prompt babysitting. All changes stay
inside the local-stdio-only invariant - no HTTP transport, no
hosted mode, no server mode.

### Added

- **Rich Server Instructions.** FastMCP is now initialized with a
  3400-character instructions block that injects a user manual
  into the model's context every session. Covers: when to use
  which tool, composition patterns (`lookup_tenant` → `analyze_posture`
  → `simulate_hardening`), the passive-only invariant, confidence
  semantics, and when to use `explain=True`.
- **`recon doctor --mcp`** flag. Validates the MCP server setup:
  mcp package installed, server module imports cleanly, Server
  Instructions present, tools enumerate, `recon` on PATH. Emits
  copy-pasteable JSON config for Claude Desktop, Cursor, VS Code +
  Copilot, and Windsurf.
- **Windsurf config** documented in `docs/mcp.md`
  (`~/.codeium/windsurf/mcp_config.json`).
- **PATH gotcha note** for GUI MCP clients (Claude Desktop,
  Windsurf) that don't inherit the shell PATH. Includes the
  `python -m recon_tool.server` fallback pattern.

### Changed

- No behavior change in the MCP tools themselves. Just better
  agent ergonomics on top of the existing surface.

## [0.10.2] - 2026-04-17

Passive coverage depth. Three targeted expansions to detection
coverage and run-over-run intelligence, all staying inside the
passive / zero-creds / per-domain-storage invariants.

### Added

- **Medium-tier subdomain enrichment.** New `medium_subdomain_lookup`
  in `sources/dns.py` adds MX + DKIM probing on top of the lightweight
  CNAME + TXT tier for the highest-signal subdomain prefixes (`auth`,
  `sso`, `login`, `idp`, `api`, `mail`). Catches SaaS and email tenants
  that publish verification records on subdomains distinct from the
  apex. Capped at 6 subdomains per lookup to stay within the DNS budget.
- **`recon delta <domain>`** CLI command. Reads the previous cached
  `TenantInfo` from `~/.recon/cache/`, runs a fresh lookup, diffs
  services / slugs / auth / DMARC / confidence / email-security-score,
  and updates the cache with the new snapshot. No manual export file
  required. The existing `--compare previous.json` flag still works
  for explicit baselines.
- **Chained fingerprint pattern documentation.** Added a `match_mode: all`
  section to `docs/fingerprints.md` explaining how to require multiple
  detections (across record types) before a fingerprint fires.
  Infrastructure has been in place since earlier versions; now documented
  for contributors.

### Changed

- **Resolver enrichment pipeline.** `_enrich_from_related` now splits
  capped subdomains into medium-tier (top-signal prefixes, MX + DKIM)
  and lightweight (everything else, CNAME + TXT only). Separate domains
  continue to get the full DNS lookup.

### Roadmap

- Added **v0.10.3 - MCP agent ergonomics** (Server Instructions, tool
  docstring polish, `recon doctor --mcp`).

## [0.10.1] - 2026-04-16

Provider accuracy + UX depth. Follow-up to v0.10 that addresses
structural detection issues exposed during real-world validation:
SSO hub mislabeling, DKIM undercount on Fortune 500 targets,
service miscategorization, and the "everyone has both providers"
noise problem.

### Added

- **Generic DKIM selector probing.** dns.py now probes `s2`,
  `dkim`, `mail`, `k2` as TXT records on top of the existing
  Exchange (`selector1`/`selector2`), Google (`google`), and ESP
  selectors. Large enterprises using non-standard selectors now
  get DKIM credit on the email security score instead of
  "No DKIM selectors observed" false negatives.
- **`email_confirmed_slugs` parameter** in `detect_provider()`.
  Filters slug-based secondary providers to only those with MX
  or DKIM evidence - dormant account registrations no longer
  clutter the Provider line.

### Changed

- **SSO hub label.** `federated-sso-hub` slug display changed
  from "Shibboleth / SAML SSO hub" to "SSO hub". A DNS A record
  at `sso.domain.com` can't distinguish Entra ID from Okta from
  Shibboleth - the previous label overstated what the tool
  knows. Okta and ADFS specific detections (via `okta.*` /
  `adfs.*` subdomains) keep their specific labels.
- **Service categories rethink.**
  - `"Other"` renamed to `"Business Apps"` across
    `_SERVICE_CATEGORIES_ORDER`, `_CATEGORY_BY_SLUG`, and
    `_categorize_service()`.
  - Microsoft Teams, XMPP/Jabber, Slack → Collaboration (was
    Business Apps / Other).
  - Intune / MDM → Identity (was Business Apps / Other).
- **Gateway + DKIM → confirmed primary.** `_compute_email_topology`
  now promotes gateway+DKIM evidence to `primary_email_provider`
  (confirmed) instead of `likely_primary_email_provider`
  (inferred). DKIM proves the provider signs mail for this
  domain - that's not inference, it's confirmation. Weaker non-MX
  evidence (TXT, OIDC, UserRealm) still sets `likely_primary`.
- **Provider-line secondaries filtered.** Dormant account
  detections (M365 tenant exists but no DKIM or MX evidence) no
  longer show as "(secondary)" in the default Provider line.
  They still appear in `--full` and `--json` output.

### Example diffs

Hybrid-Exchange target before: `Provider     Exchange Server (on-prem / hybrid) behind Trend Micro gateway + Microsoft 365 (account detected) + Google Workspace (account detected)`

Hybrid-Exchange target after: `Provider     Microsoft 365 (primary) via Trend Micro gateway + Google Workspace (secondary)` - M365 confirmed via DKIM, GWS confirmed via DKIM too.

GWS-primary target before: `Provider     Google Workspace (primary) + Microsoft 365 (secondary)`

GWS-primary target after: `Provider     Google Workspace (primary)` - M365 tenant exists but has no MX/DKIM evidence, so it's not shown in the default Provider line.

## [0.10.0] - 2026-04-16

CT resilience + UX overhaul. Two themes: (1) when live CT providers
both fail, a per-domain cache serves as fallback; (2) the default
panel output is now tight enough for a CEO glance - zero redundancy
between header, services, and insights.

### Added

- **Per-domain CT cache.** New `recon_tool/ct_cache.py` stores CT
  provider results as JSON files in `~/.recon/ct-cache/{domain}.json`.
  Seven-day default TTL, one file per domain, no aggregated store.
  Successful provider queries automatically populate the cache.
- **CT cache fallback.** When both crt.sh and CertSpotter are
  degraded, the fallback chain now checks the per-domain CT cache
  before returning an empty subdomain set. The panel shows "CT: from
  local cache, N days old" so users know they're seeing cached data.
- **Cache CLI commands.**
  - `recon cache show [domain]` - inspect cache state for a domain
    or list all cached domains with subdomain counts and age.
  - `recon cache clear [domain]` - remove cache for a specific domain.
  - `recon cache clear --all` - remove all cached CT data.
- **Cache age in panel output.** When CT data comes from cache, the
  Note section shows "CT: from local cache, N days old (M subdomains)"
  in info tone (not warning) so it reads as a recovery event, not an
  error.
- **`ct_cache_age_days` field** in JSON output - `null` when data
  comes from a live provider, integer when from cache.

### Changed

- **`_detect_cert_intel()` now caches on success.** Every successful
  CT provider query writes to the per-domain cache, so future
  degraded runs have fresh fallback data.
- **Degraded-source rendering** updated to distinguish live fallback
  ("CT fallback: crt.sh → certspotter") from cache fallback ("CT:
  from local cache, 3 days old").
- **UX overhaul - insight curation.** Aggressive dedup: 18
  restatement prefixes dropped (insights that just re-list services
  already visible in the categorized block). Default mode caps at 5
  insights + email score; `--full` shows all. Vague labels like
  "Complex Migration Window" and "Governance Sprawl" cut entirely.
- **UX - Email row cleanup.** Protocol config (DKIM, DMARC, SPF,
  MTA-STS, BIMI, TLS-RPT, Exchange Autodiscover) removed from the
  default Email services row - the email security score insight
  already covers these. Provider-line services (M365, Google
  Workspace, gateway) also stripped from Email to eliminate
  duplication. `--full` still shows everything.
- **UX - no decorative color.** Section headers changed from
  `bold cyan` to `bold`. Color reserved for functional meaning
  (green=high confidence, yellow=warning) per modern CLI norms.
- **UX - CT note suppressed.** Routine "CT fallback: crt.sh →
  certspotter" notes suppressed in default output - infrastructure
  plumbing that added noise on nearly every run. Cache fallback
  and actual warnings still surface.
- **Provider accuracy.** When Exchange Autodiscover AND an M365
  tenant are both detected, the Provider line now reads "Microsoft
  365 via [gateway]" instead of "Exchange Server (on-prem / hybrid)".
  On-prem only leads when no M365 tenant is found (e.g. vatican.va).
- **Bundled AI inference.** M365 presence → "Microsoft Copilot
  (likely)" in Services > AI. Google Workspace → "Google Gemini
  (likely)". Hedged with "(likely)" to distinguish from DNS-
  confirmed detections like Anthropic.

## [0.9.4] - 2026-04-16

Infrastructure-only release. No feature changes. Toolchain and release
hygiene to make the 1.0 stability commitment credible.

### Added

- **`SECURITY.md`** - vulnerability reporting policy at the repo root
  (GitHub's standard location). Separate from the `docs/security.md`
  threat model planned for 1.0.
- **Pre-commit hooks** - `.pre-commit-config.yaml` with Ruff (lint +
  format) and Pyright. Prevents bad code from reaching CI.
- **`pip-audit` in CI** - dependency vulnerability scanning runs on
  every PR and every release build.
- **Coverage gate** - CI now fails if test coverage drops below 80%.
  Current coverage: 87%.
- **`uv.lock`** - reproducible builds via uv lockfile. Development
  workflow uses `uv sync --extra dev`; end-user install instructions
  (`pip install recon-tool`) are unchanged.

### Changed

- **MCP packaging changed in this release.** At the time, `pip install
  recon-tool` no longer pulled in the MCP dependency tree. Current
  releases ship the MCP server in the default install; see the README
  for up-to-date packaging guidance.
- **CI migrated from pip to uv.** Both `ci.yml` and `release.yml` now
  use `astral-sh/setup-uv@v5` for faster, reproducible installs.
- **Trusted Publisher on PyPI** - release pipeline already uses
  OIDC-based publishing via `pypa/gh-action-pypi-publish`; no static
  API tokens.

### Developer notes

- `pip install -e ".[dev]"` still works but `uv sync --extra dev` is
  now the recommended development workflow.
- Pre-commit can be activated with `pre-commit install` after cloning.
- `pip-audit` is included in the `[dev]` extra for local use.

## [0.9.3] - 2026-04-15

This release is the *Sparse-Target Amplification + UX Refinement* pass.
Themes: (1) extract more hedged signal from the same passive sources -
especially on heavily-proxied, minimal-DNS, managed-auth targets where
older releases went silent; (2) redesign the default CLI output so
professional users never feel like they're looking at hobbyist-grade dump
output; (3) validation-driven fixes from real-world runs against EDU,
nonprofit, religious, and sparse commercial targets. Everything stays
within the passive / zero-creds / zero-additional-network invariants.

### Validation-driven refinements

- **Categorized Services refinements**:
  - `"AWS Route 53"` renders as `"AWS Route 53 (DNS)"` under Cloud so
    the row can't be misread as "primary cloud = AWS". Same treatment
    for `azure-dns`, `gcp-dns`, CDN providers (`(CDN)`),
    edge/serverless platforms (`(edge)`), and WAFs (`(WAF)`).
  - `google-managed` / `google-federated` slugs render as
    `"Google Workspace (managed identity)"` / `"(federated identity)"`
    instead of the raw slug.
  - CAA issuer fingerprints collapse to one `"CAA: N issuers
    restricted"` entry instead of four separate rows overwhelming
    Security.
  - `"CAA: "` prefix stripped when a CAA-derived fingerprint is
    classified in a non-Security category (e.g.
    `"CAA: AWS Certificate Manager"` → `"AWS Certificate Manager"`
    in Cloud).
  - Exchange Autodiscover classified as Email instead of Other.
  - Verification-token artefacts (`"(site verified)"`,
    `"(domain verified)"`, `"Domain Connect (…)"`) filtered from
    the categorized Services block - they're ownership receipts,
    not deployed products.
  - Identity row dropped when its only entry is a
    `"<provider> (managed identity)"` echo of an Email row.
- **Insights dedup and curation**:
  - Four overlapping dual-provider signals (`Dual provider`,
    `Dual Email Provider`, `Dual Email Delivery Path`,
    `Secondary Email Provider Observed`) collapse to one canonical
    line.
  - Three overlapping AI-adoption signals collapse to one
    `"AI Adoption Without Governance"` line when the governance
    version fires.
  - On sparse targets (`Email security 0/5` / `1/5` / `2/5`), the
    subsequent `"No DMARC record"`, `"No DKIM selectors"`, and
    `"DMARC: none"` lines are dropped as redundant - the score
    line already says it.
  - `"Cloud-managed identity indicators (Entra ID native)"` only
    fires on pure M365 targets (no Google Workspace present) -
    on dual-provider targets the Auth line already says
    `"Managed (Entra ID + Google Workspace)"` so the insight
    would be pure restatement.
  - Meta-signals (`requires_signals` only, no candidates) that
    fire with an empty `matched` list - for example
    `"Complex Migration Window"` - render as a bare name instead
    of a `"Name: "` dead-end with nothing after the colon.
  - Raw slugs in signal insight text now humanize through a
    ~90-entry map: `"sendgrid, mailchimp"` → `"SendGrid, Mailchimp"`,
    `"crewai-aid"` → `"CrewAI"`, `"google-managed"` →
    `"Google Workspace (managed)"`, etc.
  - Variant-slug dedup: when a signal's matched list carries both
    `"google-workspace"` and `"google-managed"`, the variant
    collapses into the parent so the insight doesn't read
    `"Google Workspace, Google Workspace (managed)"`.
- **Sparse-signal observation**: new hedged two-sided insight that
  fires when service density is low and the target isn't an M365
  tenant. States explicitly: *"Sparse public signal - few
  observable records beyond MX and identity. Consistent with a
  small organization, a parked or dormant domain, or a
  heavily-proxied target. Observation, not a verdict."* This is
  the explicit answer to "why is this panel thin" that the
  previous output left the user guessing about.
- **Provider line / Auth line consistency**:
  - Slug-only fallback in `detect_provider` always adds the
    `"(primary)"` qualifier now (was inconsistent before -
    topology path labelled, fallback path didn't). Multi-provider
    fallback follows the same `"primary + secondary"` format as
    the topology path.
  - Auth line `"Unknown + Managed (GWS)"` bug: `GetUserRealm`
    returns `NameSpaceType=Unknown` for non-M365 domains; that
    value now gets filtered at display time so Google-only
    domains read `"Managed (Google Workspace)"` instead of
    leaking the "Unknown" token.
  - Auth line `"(GWS)"` abbreviation replaced with
    `"(Google Workspace)"` in the mismatched-auth branch (the
    same-auth compound branch already used the full name -
    inconsistent before).
  - Auth line `"Entra ID"` claim only fires when `microsoft365`
    is in `slugs`, not just when `tenant_id` is set. A domain
    with a registered but inactive M365 tenant no longer gets
    a false "Entra ID" label on the Auth line.
- **Panel layout**:
  - Hero header shows `display_name` once - when it falls back to
    the raw domain (no company name extractable), the duplicated
    hostname line that looked like a bug is gone.
  - Long Provider-line values wrap with an explicit continuation
    indent matching the label column, instead of Rich's default
    column-0 wrap that made `"…Google \\nWorkspace"` ugly.
  - Panel width reduced from 80 → 78 to avoid terminal
    wrap-to-next-line artefacts at the 80-char boundary.
  - Confidence line single-space between dots and label (was
    double-space).
- **Degraded-sources Note reframing**:
  - Two tiers now: **info tone** (default color) when only CT
    sources were degraded AND a CT fallback successfully reached
    another provider (reads as a routine fallback event, not a
    warning); **warning tone** (yellow) when a non-CT source is
    down or every CT provider failed.
  - When CT fallback succeeded with zero subdomains, the Note
    line is suppressed entirely - the outcome is identical to a
    clean run on a domain with no related CT data, so mentioning
    the fallback every time was persistent noise.
  - Wording changed from `"Some sources unavailable"` (false
    alarm when fallback recovered) to `"CT fallback: crt.sh →
    certspotter (N subdomains)"` in the recovered-but-informative
    case, and `"All CT providers unavailable"` when genuinely
    failed.
- **Confidence downgrade logic**:
  - v0.9.2 auto-downgraded confidence on any `degraded_sources`.
    v0.9.3 skips the downgrade when the ONLY degraded sources
    are CT providers AND a CT fallback successfully recovered
    data. Previously, every domain looked up while crt.sh was
    flaking got stuck at `medium` even when the fallback chain
    fully recovered.
- **JSON schema hole fixed**: `format_tenant_dict` now emits the
  `slugs` field explicitly. Downstream tooling used to have to
  reconstruct slug sets from the `detection_scores` field because
  the top-level `slugs` field was missing from the output.
  Also added `cloud_instance`, `tenant_region_sub_scope`,
  `msgraph_host`, and `lexical_observations` to the emitted
  dict - they were on `TenantInfo` but not surfaced in
  `--json`.

### Docs and roadmap

- **Roadmap rewritten** (`docs/roadmap.md`): collapsed from the
  original 191-line, four-release (`v0.9.3 → v0.9.4 → v0.9.5 →
  v1.0`) gold-plated plan into a tighter ~150-line priority-
  ordered list. CT source resilience promoted from "Later/maybe"
  to `What's next #1` - three-provider fallback chain + local
  per-domain JSON cache with 7-day TTL. Community fingerprint
  pipeline elevated from "Later/maybe" to 1.0 scope.
  `--confidence-mode strict` flag added as a future item for the
  hedging-on-dense-evidence complaint. Bayesian evidence fusion,
  property-graph core, counterfactual simulation, temporal CT
  all demoted to "Post-1.0 ideas". Forward dates and version-
  number sequencing removed per feedback. 1.0 metrics made
  explicit (≥80% signal coverage, zero unhedged assertions on
  sparse-evidence fixtures, MCP idempotent/cache-aware, stability
  tags on every public surface).
- **README example panel updated** to the v0.9.3 hero layout. The
  old bordered-panel example no longer matched reality - a new
  user reading the README would see an example format the tool
  doesn't produce anymore.

### Added - Sparse-target inference

- **`positive_when_absent` absence-engine extension + hedged
  hardening observations.** The `Signal` schema gains a new
  `positive_when_absent` field. When a parent signal fires AND none
  of the listed adversary-friendly / consumer-SaaS slugs are
  detected, the absence engine emits a hedged two-sided positive
  observation: *"Edge Layering - Hardening Pattern Observed: fits a
  deliberately hardened target, a dormant / parked domain, or a
  small shop behind an edge proxy. Hedged observation, not a
  verdict."* The v0.9.3 `Edge Layering` signal carries a 14-slug
  exclusion set (`slack`, `notion`, `atlassian`, `dropbox`, `canva`,
  `hubspot`, `salesforce`, `zoom`, `miro`, `airtable`, `intercom`,
  `mailchimp`, `monday`, `clickup`) so a hardened-enterprise proxy
  target finally gets a positive reading without any confident
  verdict. Wired through `merger.build_insights_with_signals`,
  `cli._build_explanations`, and `server._lookup_tenant_json_with_explain`
  so the hardening observation shows up in every `--explain` output
  path. 14 unit tests pin the invariant.
- **CT subdomain lexical taxonomy** (`recon_tool/lexical.py`). A
  pure-Python rule parser that classifies CT-discovered subdomains
  into environment (`dev-`, `stg-`, `uat-`, `prd-`, `sbx-`), region
  (`us-east`, `eu-west`, `ap-southeast`, `apne1`), and tenancy-shard
  (`t-1234`, `org-delta`, `tenant-xyz`) taxonomies. No ML, no bundled
  embeddings, no generated candidates. Emits hedged
  ``LexicalObservation`` entries on the standard insights list:
  "Mature environment separation pattern observed (3 env-prefixed
  subdomains e.g. dev, stg, prod) - consistent with multi-environment
  deployment pipelines. Observation, not a verdict." A threshold of
  `MIN_MATCHES=2` prevents single-subdomain coincidences from firing
  the signal; sample labels are capped at 3 so `--explain` shows
  evidence without flooding. 30 unit tests cover env/region/shard
  classification, label boundary rules, and observation hedging.
- **OIDC tenant metadata enrichment** (`sources/oidc.py`). The
  `parse_tenant_info_from_oidc` parser now extracts the Microsoft
  extensions `cloud_instance_name`, `tenant_region_sub_scope`, and
  `msgraph_host` from the discovery response - fields that were
  already in the JSON we fetched but silently discarded. These
  distinguish commercial M365 (`microsoftonline.com`), US Government
  Community Cloud (`microsoftonline.us` + `GCC`), GCC High / DoD
  (`microsoftonline.us` + `DOD`), Azure China 21Vianet
  (`partner.microsoftonline.cn`), and Azure B2C (`*.b2clogin.com`)
  tenancies. Surfaced in `TenantInfo.cloud_instance`,
  `TenantInfo.tenant_region_sub_scope`, and `TenantInfo.msgraph_host`;
  rendered by a new `_sovereignty_insights` generator in
  `insights.py` as a hedged insight line ("Likely US Government
  Community Cloud (GCC) tenant (observed
  cloud_instance=microsoftonline.us)"). 13 unit tests pin the
  detection rules and the hedging invariants.
- **Shared verification token clustering**
  (`recon_tool/clustering.py`, new module). In-memory, batch-scope,
  never persisted. When two or more domains in a single `recon batch`
  run share the same `google-site-verification`, `MS=`,
  `atlassian-domain-verification`, Zoom, or similar TXT token, each
  domain's JSON output gains a `shared_verification_tokens` array
  with per-token peer attribution. Exposed programmatically via a
  new read-only `cluster_verification_tokens` MCP tool that accepts
  a list of domains and returns the cluster map from cached
  `TenantInfo` - zero extra network calls. Shared tokens are
  **hedged "possible relationship (observed)"** signals, never
  acquisition verdicts - a reused token implies a shared SaaS
  account operator, not corporate identity. 21 unit tests cover
  normalization, symmetry, multi-peer clusters, and deterministic
  ordering.
- **Custom profile templates + `--profile` flag**
  (`recon_tool/profiles.py`, new module). YAML files in
  `~/.recon/profiles/*.yaml` (or the built-in `data/profiles/`
  directory) define a lens: `category_boost` multipliers,
  `signal_boost` per-signal multipliers, `focus_categories` filters,
  `exclude_signals` blocklists, and a `prepend_note` header.
  Profiles are additive-only - they reweight and reorder existing
  observations, never add new intelligence. Six built-in profiles
  ship in `data/profiles/`: `fintech`, `healthcare`, `saas-b2b`,
  `high-value-target`, `public-sector`, `higher-ed`. The CLI gains `--profile
  <name>` on the lookup command; the MCP `analyze_posture` tool
  gains an optional `profile` argument. Custom profiles override
  built-ins when the name matches - one of the few exceptions to
  the usual additive-only invariant, on the grounds that profiles
  are explicitly user-facing lenses and explicit override is the
  expected mode. 25 unit tests cover built-in discovery, custom
  profile loading, invalid YAML handling, boost multipliers,
  category filtering, and deterministic ordering.
- **DMARC aggregator fingerprinting** - four new vendors added to
  the existing `dmarc_rua` detection pipeline: URIports,
  DMARC Advisor, PowerDMARC, Mimecast DMARC Analyzer. Total
  fingerprint count now **227** (was 208). The `DMARC Governance
  Investment` signal's `requires.any` list was expanded to cover
  the new slugs, so RUA addresses pointing to these vendors now
  fire the governance-maturity signal end-to-end.
- **EDU / nonprofit / marketing fingerprints** - 15 new
  fingerprints: Canvas LMS, Blackboard, Moodle, Ellucian
  Banner, Handshake, Top Hat (higher-ed LMS/SIS), Dynamics 365
  Marketing, Salesforce Marketing Cloud (SFMC), Emma, iContact,
  MailerLite (marketing automation), VMware Cloud, Salesforce
  NPSP, Blackbaud, Classy (nonprofit CRM/fundraising).
  TXT-verification detection merged into existing Netlify and
  WP Engine entries.
- **Exchange on-prem / hybrid detection**
  (`dns._detect_exchange_onprem`). Probes `owa.`, `outlook.`,
  `exchange.`, `mail-ex.`, `webmail.`, `autodiscover.` subdomains.
  `autodiscover` uses A-only resolution (not CNAME) to avoid
  M365 false-positives - M365 autodiscover is CNAME to
  `outlook.com`. Emits `exchange-onprem` slug. Wired into the
  parallel `asyncio.gather` detector set.
- **Federated SSO hub detection** (`dns._detect_idp_hub`).
  Probes 15 identity-provider subdomain prefixes (`shibboleth`,
  `weblogin`, `idp`, `wayf`, `sp`, `sso`, `saml`, `cas`,
  `raven`, `webauth`, `harvardkey`, `kerberos`, `okta`, `adfs`,
  `federation`) for A records. Emits `federated-sso-hub`,
  `okta-sso-hub`, or `adfs-sso-hub` slugs depending on match.
- **SPF redirect chain following** (`dns._follow_spf_redirect`).
  Follows `redirect=` directives in SPF records up to 3 hops,
  collecting additional SaaS fingerprint matches from the
  redirect targets. Silent failure via try/except.
- **A → PTR cloud hosting detection**
  (`dns._detect_hosting_from_a_record`). Resolves the apex A
  record, then performs a PTR lookup on the resulting IP.
  Pattern table covers AWS EC2/ELB, Azure VM, GCP Compute,
  Linode, DigitalOcean, Hetzner, OVH, and Vultr.
- **Higher-ed profile** (`data/profiles/higher-ed.yaml`). Sixth
  built-in posture profile for universities, colleges, research
  institutions, and academic computing. Boosts identity (1.6×),
  email (1.5×), infrastructure (1.3×). Prioritises federated
  identity, LMS detection, email governance. Excludes GTM
  signals that don't apply to universities.
- **MX always-emit for `has_mx_records` plumbing**. `_detect_mx`
  now emits an `EvidenceRecord` for every MX host even when no
  fingerprint matches, so the downstream `has_mx_records` check
  works regardless of fingerprint coverage.
- **Email security scoring honesty**. The email security score
  now requires MX-backed evidence (`primary_email_provider`,
  `likely_primary_email_provider`, `dmarc_policy`, or
  outbound-email slug) before scoring. Domains with zero email
  infrastructure no longer get a misleading `0/5 weak` label.
  Score `0` with monitoring records reads "DMARC monitoring
  mode, SPF soft/neutral - no strict controls" instead of
  "no protections detected".
- **Provider "account detected" variants**. When identity
  endpoints show a registered account but MX records don't
  confirm active email delivery, the provider line now reads
  `"(account detected, no MX)"` or `"(account detected,
  custom MX)"` instead of claiming the provider as primary.
- **Explanation DAG serialization** (`explanation.build_explanation_dag`).
  Produces a JSON-serializable provenance DAG from any list of
  `ExplanationRecord` instances: node types `evidence`, `slug`,
  `rule`, `signal`, `insight`, `observation`, `confidence`; edge
  types `detected-by`, `contributes-to`, `fired`. Every terminal
  node is reachable from at least one evidence node via a short
  path (asserted by the v0.9.3 property-based harness). `--explain
  --json` on the CLI and the MCP `lookup_tenant` with `explain=true`
  both emit the DAG under a new `explanation_dag` key alongside
  the existing flat `explanations` list - old consumers stay
  working, new consumers get the structured view. 17 unit tests
  pin the shape, the node types, the edge semantics, and
  determinism.
- **Property-based hedging regression harness**
  (`tests/test_v093_hedging_invariants.py`). Hypothesis-driven
  fuzz testing that asserts five hedging invariants against
  random slug subsets and random OIDC metadata: (1) every
  `positive_when_absent` output is hedged and two-sided; (2) the
  emitted SignalMatch name carries the `"Hardening Pattern
  Observed"` suffix; (3) sovereignty insights never claim
  certainty; (4) the signal pipeline never raises or emits
  duplicate names; (5) every absence signal references a
  legitimately-firing parent. Plus a static pass over every
  loaded signal to reject forbidden confident-verdict language
  (`definitely`, `proven`, `confirmed `, `guaranteed`). Runs in
  under 5 seconds on default settings so it's always on. This is
  the mechanical floor that makes every other v0.9.3 item safe to
  ship - a future PR that reintroduces confident-wrong language
  fails CI before merge.

### Added - UI/X refinements

- **Default panel redesign** (`formatter.render_tenant_panel`).
  Complete visual rewrite of the lookup output. The old bordered
  Rich Panel with an 80-column frame is replaced by a plain-text
  hero layout: company name in bold, apex domain on a dim second
  line, a horizontal rule, then a 13-column label / value fact
  block (Provider, Tenant, Auth, Cloud, Confidence), then a
  hierarchical Services section broken into seven display
  categories (Email, Identity, Cloud, Security, AI, Collaboration,
  Other), then a compact 1-2 line High-Signal Related Domains
  section, then curated Insights, and - only when sources are
  actually degraded - a subtle yellow Note line. `--full`,
  `--verbose`, `--explain`, and `--domains` add additional
  sections (full tenant_domains list, evidence chain, conflict
  annotations, cert summary) after the core layout without
  breaking its structure.
- **Disciplined color palette**: subtle cyan/teal for section
  headers (`Services`, `High-signal related domains`, `Insights`),
  green **only** when confidence is `High`, default text for
  Medium/Low confidence (no alarmist yellow, no red, no
  high-chroma anywhere), subtle yellow for the degraded-sources
  Note line (only when it appears). Graceful monochrome fallback
  - terminals without color support still render the full layout
  as plain text.
- **Categorized services classifier**. A 120+ slug → category
  lookup table (`_CATEGORY_BY_SLUG`) gives every detected slug a
  deterministic home in one of the seven display categories.
  Services whose slug isn't in the table fall through to a
  prefix-based classifier (`DMARC`/`DKIM`/`SPF` → Email,
  `DNS:`/`CDN:`/`Hosting:` → Cloud, etc.). Pass-2 dedup via
  lowercase-prefix matching prevents the same detection from
  appearing twice under two different display names (e.g.
  `"Atlassian"` + `"Atlassian (Jira/Confluence)"`).
- **Curated Insights filter** (`formatter._curate_insights`).
  Drops the repetitive laundry-list entries the old panel dumped
  verbatim (`Security stack: …`, `Infrastructure: …`,
  `PKI: …`, `Google Workspace modules: …`, mid-size org-size
  hints). Kept: signal firings, hardening observations,
  sovereignty hints, email security scores, topology notes.
- **Compact related-domains block**. Picks up to 8 high-signal
  subdomains (prefixes `login.`, `sso.`, `auth.`, `idp.`, `api.`,
  `admin.`, `portal.`, `dashboard.`, `support.`, `status.`,
  `app.`, `cdn.`) and displays them as a wrapped 1-2 line comma
  list with a `(N total - M more, use --full to see all)`
  footer. The old panel's 10-entry vertical list is replaced
  entirely - it was the single biggest consumer of vertical
  space on enterprise targets.
- **Fixed misleading Provider line** (`formatter.detect_provider`
  + new `_pick_single_primary` helper). The old format
  `"{gateway} (email gateway, likely delivering to X + Y)"`
  read as ambiguous dual email; the new format promotes ONE
  primary and demotes the rest to `"(secondary)"`. Selection
  rule: Microsoft 365 first (most common enterprise primary),
  then Google Workspace, then list-order fallback. Target
  output: `"Microsoft 365 (primary) via Trend Micro gateway +
  Google Workspace (secondary)"`. The word `(dual)` never
  appears anywhere in provider output - and the v0.9.3 property
  tests assert this.
- **Elevated bare `recon` command**. Running `recon` with no
  arguments no longer dumps the raw Typer help. Instead it
  prints a curated 15-line banner: version + one-line value
  prop, the recommended first command, progressive disclosure
  (`--verbose`, `--full`, `--explain`), three worked examples,
  and a gentle hint about `recon doctor`. Calm, professional,
  no emojis. Subtle cyan accents on the version label and
  section headers.
- **Elevated `recon mcp` startup + shutdown UX**
  (`server._print_mcp_banner`, `server.main`). Running `recon
  mcp` no longer hangs silently. The MCP server now prints a
  professional banner to stderr before handing control to the
  FastMCP loop: version, transport (`stdio`), loaded fingerprint
  and signal counts, a curated list of the top 10 tools with
  one-line descriptions, a config hint pointing at
  `docs/mcp.md`. Ctrl+C produces a clean `"MCP server stopped."`
  line, never a raw `asyncio.CancelledError` traceback.
  `BrokenPipeError` / `ConnectionResetError` are caught as clean
  client-disconnect events. Any other exception is rendered as a
  one-line summary, not a Python scream. The banner goes to
  **stderr** so `stdout` stays clean for the stdio transport's
  JSON-RPC framing.

### Added - Models / storage plumbing

- `SourceResult` gains `cloud_instance`, `tenant_region_sub_scope`,
  `msgraph_host` (all `str | None`, default `None`).
- `TenantInfo` gains `cloud_instance`, `tenant_region_sub_scope`,
  `msgraph_host`, `shared_verification_tokens` (tuple of
  `(token, peer_domain)` pairs - batch-scope only, not cached),
  and `lexical_observations` (tuple of hedged observation
  statements).
- `Signal` gains `positive_when_absent: tuple[str, ...]`.
- `cache.py` round-trips every new field except
  `shared_verification_tokens` - that one is intentionally
  batch-scope-only to prevent a single-domain lookup from
  inheriting peers from a previous batch run.
- New `recon_tool/clustering.py` - `ClusterEntry` frozen
  dataclass + `cluster_tokens` + `compute_shared_tokens` pure
  functions.
- New `recon_tool/lexical.py` - `LexicalObservation` frozen
  dataclass + `classify_subdomains` + `lexical_observations`
  pure functions.
- New `recon_tool/profiles.py` - `Profile` frozen dataclass +
  `load_profile` / `list_profiles` / `reload_profiles` /
  `apply_profile`.

### Changed

- **Fingerprint count: 208 → 227**. Added URIports, DMARC
  Advisor, PowerDMARC, Mimecast DMARC Analyzer, Canvas LMS,
  Blackboard, Moodle, Ellucian Banner, Handshake, Top Hat,
  Dynamics 365 Marketing, Salesforce Marketing Cloud (SFMC),
  Emma, iContact, MailerLite, VMware Cloud, Salesforce NPSP,
  Blackbaud, Classy. Merged TXT-verification detection into
  existing Netlify and WP Engine entries.
- **Signal schema: `positive_when_absent` field added** (opt-in,
  defaults to empty tuple, fully backward compatible with
  pre-v0.9.3 signals.yaml).
- **Default panel layout**: the v0.9.2 bordered Rich Panel with
  80-char width is gone. See UI/X section above. The
  `render_tenant_panel` function signature is unchanged; callers
  still pass its return value to `console.print`.
- **Provider line format**: the v0.9.2
  `"{primary} (primary email via {gateway} gateway)"` format is
  gone. The v0.9.3 format is
  `"{primary} (primary) via {gateway} gateway"`. Same
  information, half the parentheses. When `primary` is inferred
  from non-MX evidence the label becomes `"(likely primary)"`.
- **Gateway-only format**: the v0.9.2 `"{gateway} (email
  gateway)"` is replaced with `"{gateway} gateway (no
  inferable downstream)"` - more explicit about why no primary
  is shown.
- **Insights curation**: the v0.9.2 panel dumped every generated
  insight verbatim. v0.9.3 curates out repetitive laundry lists
  (Security stack, Infrastructure, PKI, Google Workspace
  modules, low-signal org-size hints) that duplicated data
  already visible in the Services block.

### Fixed

- **Provider line ambiguity on dual-DKIM domains.** The old
  `detect_provider` concatenated every likely-primary-email
  provider name with ` + `, producing "Trend Micro gateway
  (likely delivering to Google Workspace + Microsoft 365)" on
  targets where DKIM selectors for both providers existed. The
  new `_pick_single_primary` helper promotes one primary and
  demotes the rest, eliminating the ambiguous "dual" reading.
- **Bare `recon` UX failure**. Running `recon` with no arguments
  used to dump the raw Typer help - ~30 lines of
  machine-generated flag documentation with no value
  proposition, no examples, no suggested first command. Now
  emits a curated banner that tells users what the tool does
  and gives them the exact command to run next.
- **`recon mcp` silent-start failure**. Running `recon mcp`
  used to produce no output at all - just a silent hang on
  stdio. First-time users reported thinking the command had
  crashed. Now prints a professional startup banner to stderr
  with the tool list and config hint, and catches `KeyboardInterrupt`
  cleanly so Ctrl+C produces a `"MCP server stopped."` message
  instead of a raw `asyncio.CancelledError` traceback.
- **Categorized Services double-counting.** In edge cases where
  a service name matched a slug via fingerprint display-name
  lookup AND the raw service name didn't round-trip back
  through the `name_to_slug` map, the categorizer could file
  the same detection under two display names. The new
  lowercase-prefix dedup in pass 2 of `_categorize_services`
  catches both cases.

### Internal

- **Test count**: 1479 passing (1483 total, 4 integration tests
  deselected by default). 123 net new tests across v0.9.3 - 14
  for positive-absence, 30 for lexical, 21 for clustering, 13
  for OIDC enrichment, 25 for profiles, 17 for explanation DAG,
  1 compound test class (TestHardeningObservationIsHedged et
  al.) with ~10 individual tests for the property-based
  hedging harness.
- **Coverage**: 88% package-wide (up from 89% baseline; the
  small dip is because new modules start at high coverage and
  pull the weighted average slightly toward the larger existing
  surfaces). New v0.9.3 modules: `clustering.py` 100%,
  `lexical.py` 98%, `profiles.py` 90%, `absence.py` 100%.
- **Dead code removed**: ~320 lines of v0.9.2 panel body in
  `formatter.py`, plus three unused helper functions
  (`_is_compact_noise`, `_low_scored_service_names`,
  `_annotate_single_source`) that only existed to support the
  old panel. Net formatter change: +~700 lines of new v0.9.3
  layout code minus ~600 lines of deleted old code.
- **Ruff clean**: all checks pass.
- **Pyright clean**: 0 errors, 0 warnings on the package.

### Breaking (for JSON / CLI consumers)

- **Panel output format**. If your tooling parses the default
  `recon <domain>` terminal output (text scraping), it will
  break - the layout is entirely redesigned. Use `--json` for
  programmatic consumers; the `--json` shape is unchanged
  except for the new additive fields (`cloud_instance`,
  `tenant_region_sub_scope`, `msgraph_host`,
  `shared_verification_tokens`, `lexical_observations`, and
  the new `explanation_dag` key under `--explain --json`).
- **Provider string format** in `--json` output follows the new
  `"(primary) via gateway + (secondary)"` convention described
  above. Consumers matching on the exact v0.9.2 string
  `"(primary email via X gateway)"` need to update.

## [0.9.2] - 2026-04-14

This release is a reliability and honesty pass driven by real-world batch
runs across 15 diverse enterprise domains. v0.9.1 was catastrophically
unreliable on CT-heavy targets (27-93% batch failure rate depending on
upstream CT provider state). v0.9.2 raises that to 100% on the same
corpus while surfacing per-source failure reasons so users can see
exactly what went wrong when a lookup is incomplete.

### Breaking (for JSON / signal-name consumers)

- The signal **"Legacy Provider Residue"** has been renamed to
  **"Secondary Email Provider Observed"**. The detection logic and
  `exclude_matches_in_primary` guard are unchanged - only the surface
  name and description differ. Any downstream tool matching on the old
  signal name (in `--json` output's `signals[].name`, in MCP tool
  responses, or in `signals.yaml` overrides) needs to update its
  reference. The rename is described under the Fixed section below.

### Fixed

- **Catastrophic batch timeout rate on CT-heavy domains.** The 60-second
  aggregate resolver timeout cancelled the entire pipeline when crt.sh
  and CertSpotter both exhausted retries, producing 27-93% failure rates
  on enterprise targets depending on upstream CT state. Raised default
  `RESOLVE_TIMEOUT` to 120 seconds and made it configurable via the
  `--timeout` CLI flag.
- **"No information found" hid real errors.** When every source
  transiently failed, the CLI rendered a single generic message with no
  indication of which source failed or why. `ReconLookupError` now
  carries a `source_errors` tuple of `(source_name, reason)` pairs, and
  the CLI renders each one as a dim second line so users can tell
  whether the domain is genuinely empty or whether a transient failure
  hid real data.
- **No source-level retry for transient network failures.** The HTTP
  transport layer retried 429/503 status codes, but timeouts and
  connection resets caused individual sources to return immediately
  with an error - cascading up to a false "no information" verdict on
  domains that would have resolved fine on a retry. A new
  `retry_on_transient` decorator in `recon_tool/retry.py` retries up to
  two times on `httpx.TimeoutException`, `ConnectError`, `ConnectTimeout`,
  `ReadError`, `WriteError`, `RemoteProtocolError`, `asyncio.TimeoutError`,
  and `OSError`, with 0.5s and 1.5s backoff. Applied to `OIDCSource`
  and `GoogleIdentitySource` - the two single-point-of-failure sources
  most sensitive to transient failures. UserRealm and DNS already have
  internal fallback paths.
- **CertSpotter pagination missing.** The provider sent a single GET
  with no `after=` cursor, returning only the first page of issuances.
  Large enterprise domains silently truncated to a fraction of their CT
  footprint, and the caller had no idea the response was partial. Added
  a pagination loop capped at 4 pages (controlled by `_MAX_PAGES`) with
  graceful handling of HTTP 429 - on rate limit, the provider returns
  what's been collected rather than raising.
- **CT provider attribution invisible.** When crt.sh was degraded and
  CertSpotter picked up the fallback, users saw the same generic
  "Some sources unavailable (crt.sh)" note regardless of whether the
  fallback produced 0 or 100 subdomains. New `ct_provider_used` and
  `ct_subdomain_count` fields on `SourceResult` and `TenantInfo` track
  which provider actually contributed, and the panel bottom Note line
  now reads e.g. *"Some sources unavailable (crt.sh) - CT data via
  certspotter (87 subdomains)"*. Plumbed through the disk cache too.
- **"Legacy Provider Residue" mislabeled active dual-use.** On a major
  dev platform owned by a major tech company (M365 primary + Google
  Workspace secondary via DKIM), the signal fired as "Legacy Provider
  Residue: google-workspace". But in that case, both providers are
  actively used - not legacy residue at all. Renamed to **"Secondary
  Email Provider Observed"** with neutral two-sided wording that
  describes the observation without asserting whether it's active dual
  use, migration residue, or a legacy tenant.
- **Provider field silent when MX patterns don't match.** On
  custom/self-hosted email setups, `primary_email_provider` came back
  as `None` and the Provider line said just "Unknown". Rewrote the
  fallback to "Unknown (no known provider pattern matched)" so users
  understand that the tool looked and came up empty rather than
  silently skipping MX analysis.
- **`compute_inference_confidence` missed non-Microsoft corroboration.**
  The corroboration check required `m365_detected`, `display_name`, or
  `auth_type` on a non-OIDC source - fields that only populate for
  Microsoft-side sources. A domain with a tenant_id from OIDC and
  Google Workspace auth confirmation couldn't reach HIGH inference
  confidence because the Google-side fields weren't recognized as
  corroboration. Expanded the check to include `google_auth_type` and
  `tenant_domains` as valid signals.
- **Related-domains list indent regression.** (Carried over from
  v0.9.1 - not a v0.9.2 change, but the bank-run validation exposed a
  latent edge case where the footer line's text was slightly too long
  for the panel, causing Rich to wrap the last word to the panel
  margin. Shortened the footer text.)

### Added

- **`--timeout` CLI flag** - configurable per-lookup aggregate timeout,
  defaults to 120s (was 60s hardcoded). The batch pipeline and every
  resolve path honors the override.
- **`retry_on_transient` decorator** (`recon_tool/retry.py`) - shared
  async retry helper for source-level transient failures. Narrow
  exception list, short backoff, bounded attempts. 12 unit tests
  covering every transient exception class and the non-retry path.
- **CertSpotter pagination loop** - `CertSpotterProvider.query` now
  iterates up to `_MAX_PAGES` pages via the `after=<id>` cursor,
  accumulating subdomains and cert metadata across the full response.
  Stops early on 429, empty page, or missing issuance id.
- **CT provider attribution fields** on `SourceResult` and `TenantInfo`:
  `ct_provider_used` (which CT provider actually succeeded) and
  `ct_subdomain_count` (how many came back after filtering). The count
  is the **filtered** subdomain count - what's left after the wildcard
  removal, noise-prefix skip, and `MAX_SUBDOMAINS` cap in
  `filter_subdomains` - not the raw issuance count returned by the API.
  Surfaced in the JSON output, the disk cache, and the panel bottom
  Note (panel only when degraded sources are also present, so clean
  runs aren't cluttered with reassurance text).
- **`render_source_status_panel()`** in `formatter.py` - compact
  per-source status panel (✓/✗ with brief reason) rendered under
  `--explain` so users can see which sources succeeded and which
  failed without needing `--verbose`. Previously only available in
  the verbose status-line stream during resolution.
- **Partial-success rendering at the merger boundary.** `merge_results`
  already returned a partial `TenantInfo` when `tenant_id` was `None`
  but any source produced services - v0.9.2 tightens the rejection
  path so that when every source returns zero services AND zero
  tenant_id, the raised `ReconLookupError` carries the concrete
  per-source reasons instead of a generic message.
- **18 new tests in `tests/test_retry.py`** covering the retry decorator
  against every supported transient exception class, the non-retry
  semantic-failure path, and instance-method binding.
- **23 new tests in `tests/test_cache_roundtrip.py`** covering every
  `TenantInfo` field including v0.9.1 topology fields and v0.9.2 CT
  provider attribution. Fully exercises the serialize/deserialize
  round-trip and the cache_put/cache_get disk operations in isolated
  temp directories.
- **23 new tests in `tests/test_posture_validation.py`** covering the
  posture rule YAML validator (malformed rules, custom rule loading,
  metadata condition edge cases).
- **21 new tests in `tests/test_formatter_coverage.py`** covering panel
  render edge cases (empty services, degraded + no CT, truncation,
  single-source annotation, M365 classification).
- **30 new tests in `tests/test_cli_coverage_extra.py`** covering
  version and debug callbacks, doctor --fix scaffold, batch
  validation and JSON/CSV modes, exposure/gaps/posture/explain/full/md
  flag combinations, and mutually-exclusive output flag rejection.
- **25 new tests in `tests/test_explanation_coverage.py`** covering
  explanation insight classification branches, `explain_confidence`,
  `explain_observations`, and `serialize_explanation` round-trip.
- **4 new tests in `tests/test_merger_error_surfacing.py`** - R2
  regression guards: source errors carried on the exception, partial
  success when any source produced services, neutral message when
  sources returned empty without errors.
- **13 new tests in `tests/test_cert_providers.py`** covering the
  CertSpotter pagination loop (cursor advance, 429 handling, empty
  pages, missing id, MAX_PAGES cap).
- **1310 total tests** (was 1165 on v0.9.1), 100% passing,
  **88% total coverage** (was 84%), every core logic file ≥80%.

### Changed

- `ReconLookupError` - added `source_errors: tuple[tuple[str, str], ...]`
  field carrying per-source failure reasons. Backward compatible
  (defaults to empty tuple).
- `TenantInfo` - added `ct_provider_used: str | None` and
  `ct_subdomain_count: int` fields. Backward compatible.
- `SourceResult` - added matching `ct_provider_used` and
  `ct_subdomain_count` fields.
- `detect_provider()` in `formatter.py` - when nothing matches, returns
  *"Unknown (no known provider pattern matched)"* instead of the bare
  "Unknown" label, so users know the tool looked and came up empty.
- `compute_inference_confidence()` in `merger.py` - corroboration check
  now accepts `google_auth_type` and `tenant_domains` as valid signals
  in addition to the existing Microsoft-side fields. Raises HIGH
  inference confidence on domains where tenant_id comes from OIDC and
  corroboration comes from Google Identity.
- `OIDCSource.lookup` and `GoogleIdentitySource.lookup` - refactored to
  use a `_fetch` inner coroutine decorated with `retry_on_transient`.
  External API is unchanged (still never raises; always returns a
  `SourceResult`).
- Signal rename in `data/signals.yaml`: "Legacy Provider Residue" →
  "Secondary Email Provider Observed". Logic and `exclude_matches_in_primary`
  guard unchanged; only the surface name and description are different.
  All tests referencing the old name updated.
- `docs/signals.md` and `tests/test_v090_provider.py` updated for the
  rename.
- `render_warning(domain, error=None)` in `formatter.py` - accepts an
  optional `ReconLookupError` argument and renders its `source_errors`
  as dim second lines. All CLI call sites updated.
- Console initialization: `get_console()` now uses `cast(Any, ...)` on
  `sys.stdout` / `sys.stderr` before calling `reconfigure()` so pyright
  accepts the optional-method access pattern while still working
  correctly on Windows where the Python 3.7+ `reconfigure` method
  exists on `_io.TextIOWrapper`.

### Removed

- Nothing. v0.9.2 is purely additive + bug fixes.


This release is a correctness and honesty pass driven by real-world runs
against heavily-proxied enterprise targets. Several v0.9.0 outputs were
confidently wrong or framed misleadingly; this release fixes them without
changing the core architecture.

### Fixed

- **DKIM wording overclaim** - insights, exposure gaps, and the exposure
  panel all said "DKIM not configured" when the tool had only checked
  common selector names (mail, selector1, google, k1, etc.). Rewrote to
  "No DKIM selectors observed at common names - actual DKIM status
  unknown" so the absence of a match at known selectors is never
  reported as a configured-or-not claim. 3 files touched.
- **Legacy Provider Residue false positives** - the signal was firing
  on the *current* primary email provider, so a GWS-primary domain
  would show "Legacy Provider Residue: google-workspace" and a
  dual-M365+GWS domain would show both primaries flagged as residue.
  New `exclude_matches_in_primary` field on the Signal schema filters
  matched slugs whose display name appears in either
  `primary_email_provider` or the new `likely_primary_email_provider`.
  When neither primary is known, the signal refuses to fire - a
  residue claim is meaningless without a known primary to be residue
  against.
- **Multi-Cloud miscategorizing CDNs** - Cloudflare, Akamai, Fastly,
  and Imperva were triggering a "Multi-Cloud" signal despite being
  edge/CDN providers, not cloud providers. Split into two signals:
  `Multi-Cloud` (AWS/Azure/GCP/fly.io only) and new `Edge Layering`
  (CF/Akamai/Fastly/Imperva). New `edge_layering` posture rule.
- **Absence engine treating competitors as missing counterparts** -
  `expected_counterparts` entries on Enterprise Security Stack,
  Enterprise IT Maturity, and DMARC Governance Investment listed
  alternative vendors (Proofpoint/Mimecast/Barracuda for one;
  Jamf/Kandji and CrowdStrike/SentinelOne for another). Removed
  those three entries. The two remaining entries (AI Adoption,
  Agentic AI Infrastructure) describe genuine complements.
- **"Split-Brain Email Config" pejorative framing** - renamed to
  "Dual Email Delivery Path" (phrase already used in insights).
  Common deliberate enterprise pattern; previous name read as a
  defect.
- **Confidence overclaiming on degraded sources** - headline confidence
  now downgrades one rung (High→Medium→Low) when any source is in
  `degraded_sources`. Previously "High (4 sources)" would render
  while the bottom note said "crt.sh unavailable" - a self-contradiction.
- **v0.9.0 email topology fields were silently broken** -
  `_detect_mx` in the DNS source never passed `source_type` or
  `raw_value` to `ctx.add()`, so no MX EvidenceRecords were ever
  created. `_compute_email_topology` filters evidence by
  `source_type == "MX"` and consequently always returned
  `(None, None)` on live data. The v0.9.0 `primary_email_provider`
  and `email_gateway` fields have never populated from a real
  lookup. Same issue on Google DKIM detections. Fixed both - MX,
  Exchange DKIM, Google DKIM, and ESP DKIM all now create
  EvidenceRecords with correct source types.
- **v0.9.0 topology fields were never serialized to disk cache** -
  `primary_email_provider`, `email_gateway`, `dmarc_pct`, and the
  new `likely_primary_email_provider` are now persisted and restored
  from `~/.recon/cache/*.json`.
- **Related-domain dump indent regression** - continuation lines on
  the Related: section wrapped to the panel border (column 2)
  instead of the value column (column 14). Same issue on the
  bottom degraded-sources note. Both now wrap cleanly with manual
  column-aware indent.
- **Windows cp1252 Unicode crash** - the panel uses `●` confidence
  dots, `→` arrows, ` - ` em-dashes, and box-drawing glyphs that
  cp1252 cannot encode. On Windows terminals with the default
  codepage this crashed with `UnicodeEncodeError`. The console
  initializer now reconfigures stdout/stderr to UTF-8 with
  error replacement as a safety net.

### Added

- **`likely_primary_email_provider` - hedged downstream inference**
  for gateway-fronted domains. When MX points to an enterprise email
  gateway (Proofpoint, Mimecast, Symantec, Barracuda, Trellix, Trend
  Micro, Cisco IronPort / Secure Email) and no direct provider
  appears in MX, non-MX evidence (DKIM selectors, identity endpoint
  responses, TXT verification tokens) is scanned for provider slugs.
  When found, the tool emits `likely_primary_email_provider` and
  the Provider line renders as e.g. *"Proofpoint (email gateway,
  likely delivering to Google Workspace + Microsoft 365)"*. Hedged
  on purpose: the word "likely" in the field name is load-bearing.
  Never set when `primary_email_provider` is also set, so the two
  fields do not contradict each other. Plumbed through `TenantInfo`,
  `SignalContext`, the formatter `detect_provider` helper, the
  residue-guard filter, the JSON output, and the disk cache.
- **New `Edge Layering` signal** - fires on 2+ CDN/edge providers
  (Cloudflare/Akamai/Fastly/Imperva) as a deliberate hardening
  indicator. Also added `edge_layering` posture rule.
- **B1: single-source detection annotation in the default panel** -
  service names backed by only one weak evidence type render with a
  dim `*` suffix and a one-line footnote explaining the marker.
  No information loss. Uses the existing v0.3.0 per-detection
  corroboration scoring.
- **B2: related-domains truncation** - default panel shows the first
  10 priority-sorted related domains (via existing HIGH_SIGNAL_PREFIXES
  ordering) with a dim footer `…and N more - use --full for the
  complete list`. Full list still renders behind `--domains` or
  `--full`. Continuation lines and footer manually wrapped to the
  value column.
- **B3: panel color hierarchy for insights** - neutral insights
  render in dim so they read as a scannable secondary column below
  the services list. `Label: value`-shaped insights get a bold-dim
  label with the value in normal-dim. Warnings and hedged insights
  punch through in terracotta; transitions in amber.
- **12 new synthetic regression tests** in `tests/test_hardened_corpus.py`
  across six archetypes (hardened edge, dual-provider baseline, true
  legacy residue, dormant/parked, small-shop-on-CDN, and the new
  likely-primary inference cases). Every fixture uses fabricated
  slugs - no real company names anywhere.
- **6 new regression guards** for `_compute_email_topology` covering
  the likely-primary inference paths.
- 1165 total tests (was 1147), 100% passing.

### Changed

- `TenantInfo.likely_primary_email_provider` - new field, defaults to
  `None`, backward compatible.
- `SignalContext.likely_primary_email_provider` - new field, defaults
  to `None`, backward compatible.
- `Signal.exclude_matches_in_primary` - new field, defaults to `False`,
  backward compatible. When `True`, `_evaluate_single_signal` filters
  matched slugs whose display name appears in the combined
  primary/likely-primary string, and refuses to fire when neither is
  known.
- `_compute_email_topology` now returns a triple
  `(primary_email_provider, email_gateway, likely_primary_email_provider)`
  instead of a pair. Call sites and tests updated.
- `detect_provider()` in `formatter.py` accepts an optional
  `likely_primary_email_provider` parameter and renders the hedged
  "email gateway, likely delivering to X" form when appropriate.
- `google_identity.py` now emits a second `EvidenceRecord` with
  `slug="google-workspace"` (in addition to `google-federated` or
  `google-managed`) so the inference path can see Google as a
  downstream provider on gateway-fronted domains.
- `tests/test_integration.py` - replaced real corporate apex
  references with RFC-2606 reserved `example.com` / `example.org`.
  Repo is now clean of real company names outside of fingerprint
  detection targets and the Synthetic Alpha/Synthetic Gamma/Synthetic Beta fictional-
  example convention.
- Refined roadmap with a tight "Now / Soon / Later" plan driven by
  real-world findings from hardened enterprise targets.

### Removed

- `expected_counterparts` from Enterprise Security Stack, Enterprise
  IT Maturity, and DMARC Governance Investment (see Fixed above).
  Tests rewritten as regression guards that pin the *absence* of
  those counterparts.

## [0.9.0] - 2026-04-14

### Added

- **Primary Email Provider Detection** - MX-based topology computation distinguishes primary email providers from secondary/legacy detections. New `primary_email_provider` and `email_gateway` fields on TenantInfo. Enhanced Provider line formatting shows email delivery path (e.g., "Microsoft 365 (primary email via Proofpoint gateway)"). New "Email Gateway Topology" and "Legacy Provider Residue" signals. New email topology insights.
- **Negative-Space Analysis** - new `absence.py` module evaluates `expected_counterparts` on signal definitions. When a signal fires but expected companion services are absent, an absence signal is produced with hedged language. 5 built-in signals ship with `expected_counterparts` definitions for out-of-the-box absence detection. Absence signals appear alongside standard signals in all output formats.
- **DMARC Intelligence Expansion** - `rua=mailto:` extraction identifies paid DMARC report vendors (Agari, Proofpoint EFD, OnDMARC, dmarcian, Valimail, EasyDMARC). `pct=` parsing surfaces phased DMARC rollout. 6 new DMARC vendor fingerprints (detection type `dmarc_rua`). New "DMARC Governance Investment" signal. New `dmarc_phased_rollout` posture observation.
- **Ephemeral Fingerprints via MCP** - 4 new MCP tools: `inject_ephemeral_fingerprint` (inject temporary detection patterns), `reevaluate_domain` (re-evaluate cached data with zero network calls), `list_ephemeral_fingerprints`, `clear_ephemeral_fingerprints`. Process-scoped, in-memory, thread-safe. Validated through the same regex/ReDoS pipeline as built-in fingerprints.
- 6 new DMARC vendor fingerprints: Agari, Proofpoint EFD, OnDMARC, dmarcian, Valimail, EasyDMARC. 208 fingerprints total.
- 3 new signals: Email Gateway Topology, Legacy Provider Residue, DMARC Governance Investment. 44 signals total.
- 1 new posture observation: `dmarc_phased_rollout`.
- 1 new module: `recon_tool/absence.py` (absence signal evaluation engine).
- 189 new tests (958 → 1147 total). 6 Hypothesis property-based tests covering all correctness properties.

### Changed

- `TenantInfo` extended with `primary_email_provider`, `email_gateway`, `dmarc_pct` fields.
- `SignalContext` extended with `dmarc_pct`, `primary_email_provider` fields.
- `Signal` dataclass extended with `expected_counterparts` field.
- `SourceResult` extended with `dmarc_pct`, `raw_dns_records` fields.
- `detect_provider()` in `formatter.py` now accepts topology fields for enhanced Provider line formatting. Falls back to existing slug-based detection when topology fields are None (backward compatible).
- `merge_results()` in `merger.py` computes email topology, propagates DMARC metadata, and runs absence evaluation.
- `_detect_email_security()` in `dns.py` extracts `rua=` and `pct=` from DMARC records.
- MCP server now exposes 16 tools (was 12).
- All backward compatible with existing YAML files - new fields default to safe values.

## [0.8.1] - 2026-04-13

### Changed

- README: removed `~` approximation from fingerprint counts - exact 206 fingerprints, 41 signals throughout. Added `--explain` example after the panel. Added multi-step MCP prompt example.
- docs/fingerprints.md: added YAML snippet example for custom fingerprints. Added "Best for" column to detection types table.
- docs/signals.md: added two-pass evaluation note. Updated Layer 1/2/4 tables with all v0.8.0 signals and updated slug lists.
- docs/mcp.md: added multi-step example prompt for deeper analysis workflows.
- docs/roadmap.md: refined "Now" section with intelligence amplification thesis.
- CHANGELOG.md: added standard [Unreleased] section.
- CLAUDE.md: updated stale fingerprint/signal/test counts to current values.

## [0.8.0] - 2026-04-13

### Added

- 12 new fingerprints: CrewAI AID (`crewai-aid`), LangSmith Enterprise (`langsmith`), MCP DNS Discovery (`mcp-discovery`), Container Signing Attestation/Cosign (`cosign-attestation`), Fastly CDN (`fastly`), Fly.io (`flyio`), Railway (`railway`), AutoSPF (`autospf`), OnDMARC/Red Sift (`ondmarc`), dmarcian (`dmarcian`), EasyDMARC (`easydmarc`), Valimail (`valimail`). ~206 fingerprints total.
- 5 enriched fingerprints with additional detections: Sonatype (+OSSRH Maven Central pattern, weight 0.8), Snyk (+alternate site verification), Ping Identity (+PingOne email trust, weight 0.6), CyberArk (+Idaptive CNAME, weight 0.7), Beyond Identity (+authenticator CNAME, weight 0.5).
- 7 new signals: "Agentic AI Infrastructure" (Layer 2 composite), "AI Adoption Without Governance" (contradiction), "AI Platform Diversity" (Layer 2), "Software Supply Chain Maturity" (Layer 2), "DevSecOps Investment Without Email Governance" (contradiction + metadata), "Edge-Native Architecture" (Layer 2), "Enterprise Email Deliverability" (Layer 1). 41 signals total.
- 4 new posture rules: `agentic_ai_detected`, `supply_chain_security_detected`, `edge_compute_detected`, `email_deliverability_management`.
- 62 new tests (896 → 958 total).

### Changed

- GitHub Advanced Security fingerprint pattern corrected from `_github-challenge:.` to `^_github-challenge-` (hyphen, not colon).
- "AI Adoption" signal updated with new agentic AI slugs (crewai-aid, langsmith, mcp-discovery).
- "Enterprise Security Stack" signal updated with beyond-identity.
- "Dev & Engineering Heavy" signal updated with flyio, railway, fastly.
- "Multi-Cloud" signal updated with fastly, flyio.
- `ai_tooling_detected` posture rule updated with new agentic AI slugs.

## [0.7.3] - 2026-04-12

### Changed

- README: restored "the art is in the correlation" in "What it does" section - it's the thesis, not hype.
- README: Limitations section sharpened - more direct about Cloudflare/proxy gaps producing near-empty results, fingerprint staleness being inevitable without community contributions, and confident-looking output sometimes being wrong.

## [0.7.2] - 2026-04-12

### Changed

- README rewritten with honest, grounded tone. Removed "leading platform" positioning, "Explainable Correlation Engine" branding, inflated comparison table, and repetitive zero-credentials copy. Added Limitations section acknowledging project maturity, fingerprint staleness risk, lack of accuracy benchmarks, and heuristic nature of signal rules. Comparison table now honestly notes paid tools typically have broader coverage.
- Roadmap intro simplified - removed aspirational "signal intelligence" branding.
- Fingerprint count normalized to "~190" across all docs (was inconsistent between 187/194).
- Changelog: removed "Explainable Correlation Engine" branding from v0.7.0 entry.

## [0.7.0] - 2026-04-12

### Added

- `--explain` CLI flag - shows why each insight and signal was produced, including matched evidence, fired rules, confidence derivation, and weakening conditions. Works with `--json` (adds `explanations` key), `--md` (adds Explanations section), and `--chain` (per-domain explanations).
- Explanation module (`recon_tool/explanation.py`) - generates `ExplanationRecord` frozen dataclasses with provenance chains for signals, insights, confidence, and posture observations.
- Enhanced YAML signal engine: `contradicts` key (negation logic - suppress signal when specific slugs are present), `requires_signals` key (meta-signals that fire when other named signals are active), `explain` field (curated human-written explanation text per signal/posture rule).
- Enhanced YAML fingerprint engine: `match_mode: all` (AND logic - require all detections to match), detection `weight` (0.0-1.0 evidence strength per detection rule).
- Two-pass signal evaluation: non-meta signals first, then meta-signals against first-pass results. Cycle prevention at load time.
- Weighted `compute_detection_scores()` - incorporates detection weights into per-slug confidence scoring.
- Conflict-aware merge - `MergeConflicts` frozen dataclass on `TenantInfo` tracks disagreements between sources. Surfaced in `--json` (`conflicts` key) and Rich panel (dim annotations with `--explain`).
- 5 new MCP tools: `get_fingerprints` (list loaded fingerprints with filters), `get_signals` (list loaded signals with layer/category filters), `explain_signal` (query signal definition + live evaluation against a domain), `test_hypothesis` (agent proposes theory, gets likelihood + evidence assessment), `simulate_hardening` (what-if exposure re-scoring with hypothetical fixes).
- `explain` parameter on `lookup_tenant` and `analyze_posture` MCP tools - when true, includes structured explanations in JSON response.
- 7 new fingerprints: n8n, Dify, AutoGen, Snyk, GitHub Advanced Security, Sonatype, Beyond Identity. ~190 fingerprints total.
- 5 new signals using v0.7.0 engine features: "Incomplete Identity Migration" (contradicts), "Split-Brain Email Config" (contradicts), "Security Stack Without Governance" (contradicts + metadata), "Complex Migration Window" (meta-signal), "Governance Sprawl" (meta-signal). 34 signals total.
- 173 new tests: unit tests for all engine changes, 10 Hypothesis property-based tests covering all correctness properties, CLI/MCP integration tests, backward compatibility tests. 896 tests total, 84% coverage.

### Changed

- `evaluate_signals()` now uses two-pass evaluation with `contradicts` suppression. File order within each pass is deterministic.
- `Signal` dataclass extended with `contradicts`, `requires_signals`, `explain` fields.
- `DetectionRule` dataclass extended with `weight` field.
- `Fingerprint` dataclass extended with `match_mode` field.
- `_PostureRule` dataclass extended with `explain` field.
- `render_tenant_panel()` accepts `explain` parameter for conflict annotations.
- MCP server now exposes 12 tools (was 7).
- All backward compatible with existing YAML files - new fields default to safe values.

## [0.6.1] - 2026-04-12

### Changed

- README panel alignment fixed (all lines exactly 72 characters).
- At release time, test fixtures and examples were converted to fictional
  identities. The later full-history audit recorded in the data-handling policy
  supersedes the historical claim that the complete repository history had no
  evaluated-target identities.
- Validation corpus fixtures are gitignored - never committed.
- Release workflow: `skip-existing: true` prevents PyPI duplicate upload failures on tag re-pushes.

## [0.6.0] - 2026-04-12

### Added

- CertIntelProvider protocol - abstracts certificate transparency querying behind a clean interface. Two implementations: CrtshProvider (primary) and CertSpotterProvider (fallback). Shared filtering helpers ensure behavioral parity.
- CertSpotter fallback - when crt.sh is down (slow, rate-limited, or unreachable), the tool automatically falls back to CertSpotter's free, unauthenticated API. Zero API keys, zero accounts.
- Generalized `degraded_sources` - replaces the single-boolean `crtsh_degraded` with a `degraded_sources: tuple[str, ...]` field on both SourceResult and TenantInfo. Users and agents always know which public data sources were unavailable and how that affects result quality.
- Degraded sources surfaced in all output formats: Rich panel, JSON (`degraded_sources` list + backward-compatible `partial` key), markdown, and MCP text.
- 61 new tests: unit tests for providers, fallback chain, degraded_sources propagation, and 6 property-based tests (Hypothesis). 723 tests total, 84% coverage.
- Validation corpus - integration test runner (`pytest -m integration`) and accuracy report generator (`python -m tests.validation.generate_report` → `docs/accuracy.md`). Fixture files are local-only (gitignored).

### Changed

- `_detect_crtsh` replaced by `_detect_cert_intel` fallback chain in DNS sub-detector.
- `crtsh_degraded` is now a computed `@property` on SourceResult and TenantInfo (backward-compatible).
- Merger collects and deduplicates `degraded_sources` from all source results.
- README: defensive-use-only banner, "organization" replaces "target" throughout, zero-accounts emphasis.
- Legal docs: "What sees your queries" table showing exactly which services see your IP.
- Roadmap: dependency-ordered Now/Soon sections, custom profiles and `--explain` in Soon.

## [0.5.1] - 2026-04-12

### Added

- Full test coverage for defensive security tools: 12 property-based tests (Hypothesis), MCP integration tests, CLI flag tests, import safety test, banned-terms integration test. 660 tests total, 83% coverage.

### Removed

- `--html` output flag - markdown renders everywhere that matters. HTML was bloat for a focused CLI tool.

### Changed

- All test tasks are mandatory, not optional. No skipping.

## [0.5.0] - 2026-04-11

### Added

- `assess_exposure` MCP tool - structured security posture summary with email/identity/infrastructure sections, hardening control inventory, and 0-100 posture score based on publicly observable controls. For defensive security posture assessment only.
- `find_hardening_gaps` MCP tool - identifies missing or weak security configurations with categorized gaps (email, identity, infrastructure, consistency), severity levels, and "Consider ..." recommendations. For defensive security posture assessment only.
- `compare_postures` MCP tool - side-by-side comparison of two domains' security postures with metrics, control differences, and relative assessment. For defensive security posture assessment only.
- `--exposure` CLI flag - runs exposure assessment from the terminal.
- `--gaps` CLI flag - runs hardening gap analysis from the terminal.
- New `recon_tool/exposure.py` module - pure analysis functions operating exclusively on existing TenantInfo data. Zero new network calls. 14 frozen dataclasses for structured output.
- Extended banned terms enforcement - all new tool output validated against 16 banned terms to ensure neutral, defensive language throughout.
- Legal documentation updated with "Defensive Security Assessment Tools" section covering intended use cases, data source constraints, and language policy.

### Changed

- MCP server now exposes 7 tools (was 4): `lookup_tenant`, `analyze_posture`, `chain_lookup`, `reload_data`, `assess_exposure`, `find_hardening_gaps`, `compare_postures`.

## [0.4.1] - 2026-04-11

### Changed

- Added PyPI trusted publishing via GitHub Actions (OIDC, no API tokens).
- Added package metadata: classifiers, keywords, project URLs for PyPI listing.
- Fixed duplicate file warnings in wheel build by removing redundant `force-include`.

## [0.4.0] - 2026-04-11

### Added

- `--csv` output for batch mode - flat CSV with one row per domain. Columns: domain, provider, display_name, tenant_id, auth_type, confidence, email_security_score, service_count, dmarc_policy, mta_sts_mode, google_auth_type.
- Lightweight local disk cache - `~/.recon/cache/` with configurable TTL (default 24h). CLI flags: `--no-cache` to bypass, `--cache-ttl` to override. JSON files on disk, lazy eviction, no external dependencies.
- `recon mcp` subcommand - start the MCP server from the CLI instead of `python -m recon_tool.server`.
- `recon doctor --fix` - scaffolds template `~/.recon/fingerprints.yaml` and `~/.recon/signals.yaml` with inline YAML comments explaining the format.

### Changed

- Inference language tightened across insights and signals. Derived claims now use hedged language ("suggests," "indicators," "likely") instead of declarative phrasing. Factual observations (DMARC values, DKIM presence, email security scores) remain declarative.
- Removed `_preprocess_args()` sys.argv mutation hack. Domain shorthand routing (`recon alpha.invalid`) now uses a custom Typer group with `resolve_command()` override - cleaner, safer for library imports, no global state mutation.
- `_SUBCOMMANDS` now includes `"mcp"`.
- Mutual exclusion enforced for output format flags (`--json`, `--md`, `--csv`).

## [0.3.0] - 2026-04-11

### Added

- Google Workspace identity routing - new `GoogleIdentitySource` detects federated vs. managed auth by querying Google's public login flow. Extracts IdP name (Okta, Ping, Entra, etc.) for federated domains. Produces `google-federated`/`google-managed` slugs.
- Google Workspace CNAME module probing - detects active GWS modules (Mail, Calendar, Docs, Drive, Sites, Groups) via `ghs.googlehosted.com` CNAME resolution. Concurrent queries for all 6 prefixes.
- BIMI/VMC corporate identity extraction - fetches VMC certificates from BIMI `a=` URLs and extracts legally verified organization name, country, state, locality. Falls back to regex parsing when `cryptography` library is unavailable.
- Google site-verification token extraction - captures `google-site-verification` token values from TXT records for cross-domain organizational relationship mapping.
- MTA-STS policy fetch - when `_mta-sts` TXT record is found, fetches the policy file and extracts the mode (enforce/testing/none). Adds `mta-sts-enforce` slug for enforcing domains.
- TLS-RPT detection - detects `v=TLSRPTv1` records at `_smtp._tls.{domain}` with `tls-rpt` slug.
- Enhanced CSE config probing - extracts KACLS URL and multiple key service provider names from Google Workspace CSE configuration.
- Evidence traceability - new `EvidenceRecord` frozen dataclass captures source type, raw value, rule name, and slug for every detection. Propagated through the merge pipeline to `TenantInfo`. Included in `--json` output and `--verbose` display.
- Confidence separation - dual confidence model: `evidence_confidence` (how many sources contributed) and `inference_confidence` (strength of logical chain). Backward-compatible `confidence` field = min of both.
- Per-detection corroboration scoring - each detected slug gets a confidence score (high/medium/low) based on how many independent record types corroborate it.
- Fingerprint metadata enrichment - `provider_group` and `display_group` fields on fingerprint YAML entries. Formatter uses these for categorization, falling back to keyword heuristics.
- Cross-domain site-verification correlation in chain mode - domains sharing identical `google-site-verification` tokens are surfaced as organizationally related.
- 5 new Google Workspace signals: Google Workspace Full Suite, Google Federated Identity, Google MTA-STS Enforcing, plus updates to Google-Native Identity and Google Cloud Investment.
- 4 new posture rules: google_federated_identity, google_managed_identity, mta_sts_enforcing, tls_rpt_configured.
- Google Workspace insight generators: federated/managed identity insights, module summary insights.
- New data models: `EvidenceRecord`, `BIMIIdentity`. Extended `SourceResult`, `TenantInfo`, `Fingerprint` with new fields.
- 98 new tests (506 → 604 total). Test coverage 84%.

### Changed

- `default_pool()` now includes `GoogleIdentitySource` (5 sources total).
- `merge_results()` propagates evidence, computes dual confidence, detection scores, and merges Google auth/BIMI/MTA-STS/site-verification data.
- `build_insights_with_signals()` accepts `google_auth_type` and `google_idp_name` parameters.
- `format_tenant_dict()` includes all new fields in JSON output.
- `format_tenant_markdown()` includes Google Workspace section and dual confidence.
- `render_tenant_panel()` shows GWS auth/modules, verbose evidence chains and detection scores.
- `lookup_tenant` MCP tool text format includes GWS auth and module summary.
- `_detect_email_security()` now also queries TLS-RPT, fetches MTA-STS policy, and parses BIMI VMC.
- `_detect_txt()` extracts site-verification tokens and creates evidence records.
- Fingerprints YAML: added `provider_group`/`display_group` to Microsoft 365, Google Workspace, and other key entries. Added TLS-RPT fingerprint.
- 29 signals (was 26). 22 posture rules (was 18).

## [0.2.0] - 2026-04-11

### Added

- Certificate intelligence - crt.sh metadata extraction (issuance velocity, issuer diversity, cert age, top issuers) from the existing crt.sh JSON response. No additional HTTP requests. Surfaced in panel, JSON, and markdown output.
- Metadata-aware signal engine - signals can now match on `dmarc_policy`, `auth_type`, `email_security_score`, `spf_include_count`, and `issuance_velocity` via YAML `metadata` conditions. Supports slug-only, metadata-only, and conjunction signals. 23 → 26 signals (4 layers).
- Neutral posture analysis - new `--posture` flag and `analyze_posture` MCP tool. Produces factual observations about domain configuration (email, identity, infrastructure, SaaS footprint, certificates, consistency) without attack/defense framing. YAML-driven rules in `data/posture.yaml` with `~/.recon/posture.yaml` additive override.
- Delta mode - `--compare previous.json` compares a live lookup against a previous JSON export. Surfaces added/removed services, slugs, signals, and scalar field changes (auth type, DMARC, confidence, domain count). Panel output with +/- markers, JSON output with structured diff.
- Recursive domain chaining - `--chain --depth N` (max 3) follows the resolver's bounded related-name observations using BFS. 50-domain cap, visited-set deduplication, aggregate timeout. New `chain_lookup` MCP tool.
- 3 new metadata-aware signals: Federated Identity with Complex Email Delegation, Active Email Sending with Minimal Security, High Certificate Issuance Activity.
- 18 posture observation rules across 6 categories.
- 7 new frozen dataclasses: `CertSummary`, `MetadataCondition`, `SignalContext`, `Observation`, `DeltaReport`, `ChainResult`, `ChainReport`.
- 51 new tests (455 → 506 total). Test coverage 83%.

### Changed

- `--full` now implies `--posture` in addition to `--services`, `--domains`, `--verbose`.
- `evaluate_signals()` now accepts a `SignalContext` instead of positional args. All callers updated.
- "Security Gap - Gateway Without DMARC Enforcement" signal moved from hardcoded Python check to YAML metadata conditions.
- `reload_data` MCP tool now also clears posture rule cache and reports posture rule count.
- README updated: broader audience description, new feature table rows, new CLI examples, new MCP tools listed.
- Roadmap updated: completed items marked, new future items added.

## [0.1.3] - 2026-04-11

### Added

- Common subdomain probing - ~35 high-signal prefixes (auth, login, sso, shop, api, status, cdn, etc.) are probed directly via DNS CNAME lookups. Works even when crt.sh is down.
- 30 new CNAME-based fingerprints for SaaS services discovered via subdomain CNAMEs: Okta (CNAME), Auth0, OneLogin, Salesforce Marketing Cloud, AWS ELB/S3/Elastic Beanstalk, Azure Front Door, Google Cloud Run/App Engine, Zendesk/Freshdesk (hosted), Contentful, Braze, Segment, Statuspage, LaunchDarkly, Cloudinary, Imgix, Optimizely, WalkMe, and more (156 → 186 total).
- crt.sh degraded notice - when crt.sh is unreachable, a subtle note appears in panel, markdown, and JSON output (`"partial": true`) so users know results may be incomplete.
- Lightweight subdomain enrichment - subdomains get CNAME+TXT-only lookups (2 queries each) instead of full DNS fingerprinting (~20 queries each), keeping enrichment fast.

### Changed

- crt.sh subdomain cap raised from 20 to 100, with signal-based prioritization (auth/login/shop/api subdomains first, deep internal subdomains last).
- Enrichment cap raised from 10 to 25, with priority sorting so high-signal subdomains survive the cap.
- Two-tier enrichment: subdomains get lightweight CNAME+TXT lookups, separate domains get full DNS fingerprinting.
- Updated 8 signal rules to include new CNAME-detected slugs (imperva, auth0, onelogin, salesforce-mc, aws-elb, aws-s3, gcp-app, azure-fd, optimizely, walkme, braze, iterable, customerio, launchdarkly, contentful, etc.).

## [0.1.2] - 2026-04-11

### Added

- Google Workspace source - passive CSE config probing (`cse.{domain}/.well-known/cse-configuration`) for detecting Client-Side Encryption and external key managers.
- Google DKIM attribution - `google._domainkey` now adds the `google-workspace` slug, so Google Workspace is detected even when MX points to an email gateway (Proofpoint, Mimecast, Trend Micro, etc.).
- 4 new signal rules: Google-Native Identity, High-Security Posture (CSE), Google Cloud Investment, Dual Email Provider (13 → 24 total).
- Custom signals support via `~/.recon/signals.yaml` (additive, mirrors fingerprint extensibility).
- Certificate transparency integration via crt.sh for passive subdomain discovery.
- Expanded DKIM selector coverage - now checks common ESP selectors (Mailchimp, SendGrid, Mailgun, Postmark, Mimecast) in addition to Exchange and Google.
- SRV record detection for Microsoft Teams (legacy SIP/federation), XMPP, CalDAV, CardDAV.
- 13 new fingerprints: Box, Egnyte, Glean, Datadog, New Relic, PagerDuty, Render, Ping Identity, CyberArk, Lakera, Cato Networks, Rippling, Deel (143 → 156 total).
- `recon doctor` now checks crt.sh connectivity, signal database loading, and custom signals path.
- "Why recon?" comparison table in README.
- Expanded MCP Server section with setup steps, tools table, and config file locations per client.
- `CLAUDE.md` for project context.
- `CHANGELOG.md`, `CONTRIBUTING.md`.
- `examples/` folder with sample JSON output and batch file (all fictional data).
- GitHub Actions CI workflow (Python 3.10-3.13, lint, type check, tests).

### Changed

- Confidence scoring - M365 domains now reach High when OIDC tenant ID is corroborated by UserRealm (display name, auth type, or tenant domains). Previously required 2+ sources returning the same tenant ID, which never happened in practice.
- Non-M365 confidence - domains with 8+ DNS services and 2+ successful sources now reach High. Thresholds adjusted (was: 5 services for Medium, High unreachable).
- Skype for Business / Lync → Microsoft Teams - SRV records `_sip._tls` and `_sipfederationtls._tcp` pointing to `lync.com` now labeled as "Microsoft Teams" (deduplicated with CNAME-based detection). Microsoft retired Skype for Business Online in July 2021.
- Dual provider insight - shortened from "Hybrid/migration signal: Google email + Microsoft services detected" to "Dual provider: Google + Microsoft coexistence". No longer styled as a warning.
- Panel color palette - muted, modern tones replacing harsh ANSI primaries. Labels use `dim` instead of `bold`. Panel border is `dim`. Confidence colors: sage green (High), sky blue (Medium), terracotta (Low).
- Panel alignment - services and insights now use consistent label:value column alignment. Service continuation lines align under the first service name. Long insights word-wrap within the panel.
- All README examples now use explicit synthetic labels and reserved domains.
- README tagline updated to be more precise and humble.
- Panel output: fixed width (80 chars), related domains now dim instead of cyan.
- Updated Enterprise Security Stack, Zero Trust Posture, and Enterprise IT Maturity signals to include new security slugs.

## [0.1.0] - 2026-04-10

### Added

- Initial release.
- Domain intelligence CLI (`recon lookup`, `recon batch`, `recon doctor`).
- MCP server with `lookup_tenant` and `reload_data` tools.
- Three concurrent data sources: OIDC Discovery, GetUserRealm + Autodiscover, DNS records.
- 143 SaaS/service fingerprints in `data/fingerprints.yaml` across 14 categories.
- Signal intelligence engine with 3-layer evaluation (single-category, cross-category composites, consistency checks).
- Email security scoring (0-5) based on DMARC, DKIM, SPF strict, MTA-STS, BIMI.
- Related domain auto-enrichment from CNAME breadcrumbs.
- Custom fingerprint support via `~/.recon/fingerprints.yaml`.
- Rich terminal output with bordered panels, colored signals, and provider detection.
- Output formats: default panel, `--json`, `--md`, `--services`, `--full`, `--sources`.
- Batch mode with configurable concurrency (1-20) and ordered output.
- Input normalization (URLs, schemes, www prefix, paths, whitespace).
- SSRF protection in HTTP transport.
- Retry with exponential backoff on 429/503 responses.
- Structured exit codes (0, 2, 3, 4).
- `defusedxml` for safe XML parsing.
- Strict type checking with Pyright, linting with Ruff.
