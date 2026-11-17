# Security Threat Model

This is the engineering-level threat model. For **how to report a
vulnerability**, see [`SECURITY.md`](../SECURITY.md) in the repository root.

recon's default interfaces are a target-read-only CLI and local stdio MCP server
with a passive collection scope. Collection uses no target credentials, port
scanning, or user-code execution; the default interfaces open no inbound
listener. recon can write local caches, artifacts, and MCP client configuration.
DNS resolver traffic can be externally visible, MTA-STS is the only default
target-owned HTTP request, and Google CSE and BIMI certificate requests are
explicit opt-in direct probes. The separately opted-in
[draft remote adapter](../deploy/container/README.md) opens an HTTP listener
and requires bearer authentication or authenticated platform ingress. Its
credentials, local retention, and hosting controls are additional trust boundaries.

---

## Trust boundaries

| What recon trusts | Rationale |
|---|---|
| Operator-selected DNS view | Trusted CLI uses host DNS unless the operator opts in with `RECON_DNS_VIEW=caller-safe`. MCP binds a caller-safe view at startup; legitimate split DNS can otherwise disclose private answers without resolver compromise. See the CNAME boundary below. |
| Public OIDC / UserRealm / Google identity / CT endpoints | These are Microsoft, Google, and Sectigo-operated services. recon validates response shapes but cannot out-verify the underlying TLS-authenticated origin. |
| `src/recon_tool/data/fingerprints.generated.json` (built-in fingerprints) | Installed wheels load the checked-in generated JSON. Canonical split YAML is contributor source and ships in the source distribution, not as a second wheel runtime catalog. Both have the same trust level as Python source. |
| `src/recon_tool/data/*.yaml` and `src/recon_tool/data/profiles/*.yaml` (signals, posture rules, profiles) | These ship with the package and are loaded via `yaml.safe_load`. Same trust level as Python source. |
| Python stdlib + pinned dependencies in `uv.lock` | Standard supply-chain trust. CI and release jobs audit locked runtime dependencies, all development groups, and all extras on every build. |

| What recon does NOT trust | Mitigation location |
|---|---|
| User-supplied domain strings | `src/recon_tool/validator.py` - regex + length cap + scheme stripping |
| Raw DNS responses (TXT values, MX hostnames, CNAME targets) | Length caps + structured parsing in `src/recon_tool/sources/dns.py` |
| Environment variables (`RECON_CONFIG_DIR`) | Treated as arbitrary user input. Cache operations bind one resolved parent directory, validate lexical child paths, and use descriptor identity checks for reads. |
| Custom fingerprint and signal YAML | Required-field validation, regex compilation, and conservative ReDoS admission. Additive-only; cannot override built-ins. |
| Custom profile YAML | Validated profile schema. Same-name local profiles intentionally override packaged profiles; this is operator configuration, not an additive catalog rule. |
| CT provider response bodies | Size-capped, filtered for wildcards and malformed entries in `sources/cert_providers.py` |
| Malicious HTTP redirect targets / private-IP redirects | `src/recon_tool/http.py` `_SSRFSafeTransport` validates every hop |
| Queried-namespace MTA-STS declarations and policy responses | Exact TXT admission plus bounded RFC 8461 parsing in `src/recon_tool/sources/mta_sts.py`; the policy request never follows redirects |
| Caller-supplied observation capsules | `src/recon_tool/capsule.py` accepts only bounded, stable regular JSON files; rejects symbolic links, mutation during read, excessive nesting, non-finite values, unknown contract fields, malformed normalized snapshots, and fact or capsule digest mismatch |

---

## Attack surface & mitigations

### Malicious domain input

**Surface:** A user (or an agent) passes an arbitrary string to `recon <domain>` or a MCP tool.

**Mitigation:** [`src/recon_tool/validator.py`](../src/recon_tool/validator.py):

- Raw input is capped at 500 characters before parsing.
- Only `http://` and `https://` URL schemes are recognized and stripped.
  Bare inputs may include a copied path, query, fragment, or numeric port.
- Unicode hostnames are accepted only when the standard-library IDNA conversion
  round-trips without changing the normalized hostname.
- DNS labels use the letter, digit, and hyphen alphabet with no leading or
  trailing hyphen. The final label is at least two characters and begins with
  an ASCII letter, which admits validated Punycode TLDs while rejecting numeric
  TLDs.
- The normalized ASCII presentation form is capped at 253 octets total and 63
  octets per label before optional Public Suffix List apex reduction.
- A conventional `www.` prefix is removed only when the remainder is still a
  valid domain. A trailing root-label dot is removed, and output is lowercase.
- Invalid input raises `ValueError`; the CLI maps it to exit code 2
  (`EXIT_VALIDATION`). See the full [exit-code contract](schema.md#exit-codes).

### Diagnostic output and local failure artifacts

**Surface:** Debug logs and unexpected-crash artifacts can contain queried
namespaces, local paths, configuration context, or exception details. An
unexpected per-domain batch exception could otherwise copy those details into
structured output consumed or shared downstream.

**Mitigation:** Default batch output replaces unexpected exception details with
stable recovery text in JSON, NDJSON, CSV, and human modes. The full exception
is logged only at debug level. Root help warns operators to review diagnostics
before sharing. The top-level crash handler keeps its existing redaction notice,
and normal downstream pipe closure does not create a crash artifact. Structured
MCP validation-failure logs retain only a request ID and stable reason, never
the rejected domain or validation exception. Dynamic fields rendered by the
default doctor, `doctor --mcp`, `doctor --client`, `doctor --fix`,
`recon mcp install`, and live `recon mcp doctor` paths strip control bytes,
escape Rich markup, and bound displayed detail before rendering.
The live MCP doctor validates local JSON resource structure but never copies a
resource payload into its failure text. A failed later protocol phase retains
only prior check summaries plus bounded spawned-server stderr.

### Malicious DNS responses

**Surface:** A compromised or adversarial DNS response could attempt to exfiltrate via crafted values or trigger injection in downstream formatting.

**Mitigation:**
- Length caps on all DNS string values (`sources/dns.py`)
- A-to-PTR hosting detection only reverse-resolves globally routable unicast
  A-record IPs; private, loopback, link-local, reserved, multicast,
  unspecified, and other non-global addresses are skipped before PTR lookup.
- Rich-text rendering uses `Text.append(value, style=...)` which escapes Rich markup in the user-controlled portion
- Error, warning, and batch-progress sinks that print untrusted strings (a bad domain echoed back, a per-source error reason) escape Rich markup and strip control bytes (`render_error`, `render_warning`; output-injection sweep, v2.1.2), so a crafted domain or DNS value cannot inject terminal escapes or markup
- Markdown rendering backslash-escapes structural characters and existing
  backslashes in source-derived service labels, posture observations,
  explanation text, identity fields, insights, certificate issuers, and domain
  lists after control-byte stripping
- JSON output uses `json.dumps` (escapes)
- No DNS value is interpolated into shell, SQL, or exec contexts anywhere in the codebase

### Malicious observation capsules

**Surface:** A caller replays or compares a capsule file created outside the
current process.

**Mitigation:** Capsule reads are capped at 10 MiB and bind metadata and content
to one stable regular-file descriptor. Symbolic links, mutation during read,
excessive nesting, invalid UTF-8 or JSON, non-finite values, invalid timestamps,
unknown fields, malformed normalized snapshots, and digest mismatches fail with
a validation error. Replay does not call the resolver or any network source.
Writes enforce the same 10 MiB bound before creating a temporary file, refuse
an existing path unless `--force` is explicit, and use a same-directory
exclusive temporary file plus atomic replacement. Interpretation digests bind
the effective catalog and prior overrides, including custom and ephemeral
rules; older packaged-only context digests remain readable but compare as
different contexts. SHA-256
detects modification but provides no signer identity or authenticity guarantee.

### Malicious CNAME chains (surface-attribution walker)

**Surface:** The surface-attribution pipeline walks related names using CNAME
queries, up to five hops per chain and 100 related hosts. A public-looking
name can receive a private-view alias the queried domain owner did not choose.
Classified chains appear in ordinary JSON evidence, matching motif hops in
ordinary motif output, and unclassified chains only in explicit diagnostics or
discovery. A confidentiality crossing requires a lower-trust output consumer;
a query observed in internal logs alone does not establish remote disclosure.

**Mitigation (layers + ambient bounds):**
- **Entry-point validation (v1.9.13).** The walker checks `_is_public_dns_name(host)` before issuing the first CNAME query. Catches the rare case where an unvalidated name made it into `ctx.related_domains` (e.g. from a populator that didn't suffix-check before adding); that name is rejected at the door without touching the resolver.
- **Per-hop suffix denylist (v1.9.3.5).** Every CNAME target returned by the resolver is validated against `_is_public_dns_name` before the walker continues. Names ending in `.local`, `.localhost`, `.intranet`, `.private`, `.corp`, `.lan`, `.home`, `.home.arpa`, `.internal`, `.test`, `.example`, `.invalid`, `.onion`, and the `.arpa` family are rejected. Single-label names and IP literals are also rejected.
- **Query type restriction across the entire walk (v1.9.4 + v1.9.14).** The walker issues CNAME queries only, on every hop including the terminus. CNAME responses do not cause recursive resolvers to chase further records, so an attacker-controlled name cannot drive the operator's resolver to query deeper internal names while answering. v1.9.3.5 had added an A/AAAA-on-each-hop check that caused exactly that recursive chase, and v1.9.4 removed it. v1.9.13 attempted to add the check back on the terminus only, on the assumption that a CNAME NoAnswer proved the terminus had no CNAME to chase; v1.9.14 reverted the check after a follow-up scanner pass showed authoritative DNS can return type-dependent answers, so the same recursive chase can be triggered by the A or AAAA query even when the prior CNAME query returned nothing.
- **Defense-in-depth on M365 redirect_domain extraction (v1.9.13).** `_detect_m365_cnames` suffix-validates the redirect_domain extracted from a non-Microsoft autodiscover CNAME response before adding it to `ctx.related_domains`. Prevents a private-suffix apex from being planted in the related-domains set even though the walker's own entry-point check would reject it subsequently.
- **Source scoping for CT-derived related domains.** `filter_subdomains` (`sources/cert_providers.py:197`) drops every CT entry that does not end in `.<queried_domain>`. An attacker cannot put `internal.victim.example` in their own cert and have it picked up by recon: the filter requires the name to be under the queried apex.
- **Per-call bounds.** Five-hop maximum, 100-host surface cap, 30-concurrent-query cap, five-second per-query timeout.

**Resolver-view boundary:** MCP automatically binds an immutable caller-safe
policy at process startup, reusing saved settings or a recognized public DNS
service already selected in host configuration. Otherwise it binds the
maintainer-approved encrypted default, Cloudflare DNS-over-HTTPS; an
enterprise or stub resolver is never used for MCP collection.
`RECON_DNS_VIEW=none` or invalid settings produce an explicit unavailable
capability with a setup link; failures do not fall back to host DNS or another
provider. The same policy covers all collector record types,
related enrichment, recursive chains and HTTP hostname resolution. Certificate
verification, bootstrap-address selection and public HTTP socket admission
remain separate checks. Process and persistent caches are bound to the policy
identity/version; reloads and tool arguments cannot change authority.

Trusted `recon <domain>` keeps its existing host resolver and output semantics,
with no new prompt or required flag. Split-horizon results remain sensitive
operator-view data. Advanced operator-view MCP is available only as trusted
startup configuration and must serve callers permitted to see that view.
See [DNS view isolation](mcp.md#dns-view-isolation) for saved configuration and
[the audit disposition](security-audit-resolutions.md#closed-in-v2220-cname-chain-walking-can-query-and-leak-internal-dns-names)
for the conditional Medium baseline assessment and v2.22.0 boundary repair.
The repair does not claim a deployed change or protection for an agent that
can independently rewrite its launcher or run unrestricted shell/network tools.

**Pinned by:** `tests/test_cname_chain_validation.py` (including `test_walker_does_not_resolve_a_aaaa_during_walk` and `TestNoAAAAQueriesFromWalker` for the v1.9.4 + v1.9.14 invariant on all three exit paths, `TestEntryPointValidation` for the v1.9.13 entry-point check, and `TestM365RedirectDomainFilter` for the v1.9.13 redirect_domain filter).

### Malicious YAML / user-supplied regex

**Surface:** Custom fingerprint/signal YAML files and process-local MCP
fingerprint injection can supply arbitrary regex patterns.

**Mitigation:** [`src/recon_tool/fingerprints.py`](../src/recon_tool/fingerprints.py):
- `yaml.safe_load` (not `yaml.load`) - no arbitrary constructor execution
- Pattern length capped at 500 chars
- Structural checks first remove ignored inline comments and verbose-mode
  whitespace, honoring scoped flags, escapes and continued comments. The
  original expression is compiled only after admission; comment text cannot
  hide a reviewed unsafe repetition shape from the guard.
- ReDoS heuristic (`_validate_regex` in `fingerprints.py`) rejects nested
  quantifiers like `(a+)+`, `(a*)+`, and `(\w+)+`; a balanced-paren scan
  (`_has_nested_quantifier`, v2.1.1) also catches the redundantly-nested
  `((a+))+` that a flat pattern misses; and an alternation-overlap check
  (`_alternation_redos`) rejects a quantified group whose branches can match
  the same input. That covers prefix-overlapping branches like `(a|aa)+` and,
  since v2.6.12, branches that overlap by character class rather than by
  literal text, such as `(.|a)*`, `(\w|a)*`, and `([a-z]|a)*`. Those share no
  prefix, so the earlier literal-only comparison admitted them even though
  they cost roughly twice as much per added input character. Disjoint
  alternation such as `(foo|bar)+` and branches beginning with an escaped
  literal such as `\.` remain accepted. The alternation check walks enclosing
  groups too, so wrapping ambiguous branches in another group cannot bypass
  admission. Under repetition, only provably disjoint, prefix-free ASCII
  literal branches are accepted; character classes, encoded escapes, nested
  groups, assertions, empty alternatives, and whitespace-dependent branches
  fail closed. Since v2.7.1 the nested-quantifier scan
  also counts `?` as an inner repetition operator, so `(a?){50}a{50}$` is
  rejected; it distinguishes that `?` from the one opening `(?:`, `(?=`, and
  `(?i)`, which stay accepted. This is a heuristic guardrail, not a formal
  regex verifier. Do not assume the input-length caps bound what it misses: the
  pattern above backtracks past a minute on a 49-character subject, three
  orders of magnitude below the 4096-character cap. The caps bound cost for
  patterns the heuristic accepts as linear, not for an admitted exponential one.
- All patterns compile-validated via `re.compile` before use
- Same checks run on `~/.recon/signals.yaml` via `_validate_signal` in `signals.py`
- Custom entries are **additive only** - cannot override built-ins (design invariant)

### SSRF via malicious HTTP redirects

**Surface:** An adversarial upstream (or a DNS-rebound attacker) could redirect an HTTP request to a private, internal, or special-use IP, potentially exposing cloud-metadata services (169.254.169.254) or internal infrastructure.

**Mitigation:** [`src/recon_tool/http.py`](../src/recon_tool/http.py) `_SSRFSafeTransport`:
- Every hop - initial request AND every redirect - validated
- Blocks anything that is not globally routable unicast, including loopback,
  private, link-local, shared-address, unspecified, reserved, documentation,
  multicast, and IPv6 unique-local ranges
- Literal IP check on URL host
- Asynchronous DNS resolution check (every answer vs public-unicast policy)
- Missing hosts, DNS errors, empty answers, and invalid resolved addresses fail
  closed before a connection is attempted
- Used by default in all outbound HTTP (OIDC discovery, UserRealm, cert providers, Google identity)

The connection backend in
[`http_backend.py`](../src/recon_tool/http_backend.py) independently resolves
and validates the complete answer set when opening a socket, then dials only
those numeric addresses. The original origin, Host header, TLS server name,
and certificate verification remain intact. This closes the earlier gap
between preflight resolution and socket resolution. Dual-stack attempts are
interleaved, staggered, and capped; DNS and dialing share a connect deadline.
Cancelled and losing attempts close their sockets. Tests cover changed DNS,
mixed public/private answers, TLS identity, pool reuse, and cancellation without
contacting real infrastructure. Address checks do not establish that a public
service is trustworthy, nor replace operator-controlled egress policy.

Google identity follows only bounded HTTPS redirects within
`accounts.google.com` on port 443. A validated external redirect is retained as
routing evidence without fetching the destination. Google query strings and
SSO-looking path text alone do not establish federation. Invalid redirect
locations become unavailable observations.

### MTA-STS declaration and policy integrity

**Surface:** A queried namespace controls both its `_mta-sts` TXT record and
the HTTPS response from `mta-sts.<domain>`. Loose record matching, redirect
following, or partial body parsing could turn an invalid declaration or an
unrelated redirected response into an observed email-control mode.

**Mitigation:** [`src/recon_tool/sources/mta_sts.py`](../src/recon_tool/sources/mta_sts.py)
and [`src/recon_tool/sources/dns_email.py`](../src/recon_tool/sources/dns_email.py):

- Policy fetching starts only when exactly one record begins with the
  case-sensitive `v=STSv1;` marker and carries a 1 to 32 byte alphanumeric ID.
- The request disables redirects even though the shared HTTP client normally
  follows SSRF-validated hops. RFC 8461 permits only a direct HTTP 200 policy
  response at this endpoint.
- The response must declare `text/plain`. The parser accepts only valid UTF-8,
  refuses policy bodies above 64 KiB, and requires the exact version, mode, and
  bounded `max_age` fields.
- Enforcing and testing policies require at least one validated ASCII MX
  pattern. Unknown extension fields, including valid UTF-8 values, remain
  forward-compatible, while malformed required fields make the policy
  unavailable rather than partially trusted.
- The shared transport independently limits wire responses to 10 MiB, requests
  identity encoding, refuses compressed responses, validates the public
  destination, and applies a five-second policy timeout.

An invalid policy does not become an observed mode. Transport failures and
transient HTTP responses retain the existing degraded-source signal; a valid
TXT declaration can remain visible without fabricating a policy-mode claim.

### Local launcher and validation credential boundaries

**Surface:** `recon update` executes the package manager that owns the current
installation. Maintainer-only validation helpers can import paid-provider SDKs
and read API credentials.

**Mitigation:**

- [`src/recon_tool/updater.py`](../src/recon_tool/updater.py) resolves `uv` and
  `pipx` to absolute paths and refuses any launcher inside the resolved current
  workspace tree, including launchers reached through relative nested PATH
  entries. A refused or missing launcher degrades to a manual command.
- Pip upgrades download the pinned release before replacing installed files.
- Every pip subprocess and recovery command uses the current interpreter's
  safe-path option (`-P`), so implicit current-directory imports cannot select
  a workspace `pip.py` or `pip` package. User-site installs remain available.
  Explicit Python environment configuration is still operator-controlled.
  Regression tests execute synthetic modules without downloading or installing
  packages: `tests/test_updater_module_safety.py`.
  The Windows worker is a private copy of
  [`src/recon_tool/updater_windows.py`](../src/recon_tool/updater_windows.py)
  run with the base interpreter in isolated mode. It waits until `recon.exe`
  has exited, skips the package manager while another `recon.exe` is running,
  and prints a direct recovery command that does not require `recon` to start.
- Paid-provider SDKs are absent from the runtime and default development
  dependency graphs. The optional `agentic-validation` group has exact roots in
  `pyproject.toml` and artifact hashes in `uv.lock`.
- Validation CLIs accept credentials only from provider-specific environment
  variables. They explicitly refuse `--api-key` and never echo a supplied
  value, preventing supported invocations from placing credentials in process
  arguments or generated reports.

### Path traversal in local caches

**Surface:** `recon cache show ../../etc/passwd`, `recon cache clear ../../settings`, or a crafted `RECON_CONFIG_DIR` could cause a cache layer to read, write, or delete outside its intended directory.

**Mitigation:** [`src/recon_tool/ct_cache.py`](../src/recon_tool/ct_cache.py),
[`src/recon_tool/cache.py`](../src/recon_tool/cache.py), and the shared bounded
JSON loader:

- Resolve and bind one cache parent directory for each write operation.
- Validate the domain without reducing literal-host keys and require the
  lexical child path to remain inside that parent.
- Reject stable symbolic links and Windows reparse-point cache directories,
  use no-follow open semantics where the operating system provides them, and
  verify the opened regular file still has the path's identity.
- Recheck size and metadata after the read, then reject mutation before JSON
  admission.
- Bind decoded payload identity to the expected domain and schema version.
- Reject or ignore invalid paths and entries without raising to the caller
  (tests: `tests/test_ct_cache.py`, `tests/test_cache_roundtrip.py`,
  `tests/test_cache_cli.py`, `tests/test_json_limits.py`).
- Keep operator inspection payload-free. The default `recon cache show`
  overview enumerates filenames for exact totals but validates only the
  lexicographically first 100 cached objects per layer; `--all` is the explicit
  complete mode. Both render only bounded metadata, distinguish absence from
  inspection failure, withhold raw exceptions outside debug logging, and exit
  4 when a requested entry cannot be inspected.
- Count only `*.tmp` artifacts matching the cache writer's domain-and-random-
  nonce filename shape without reading their payload, report them as an
  incomplete exit-4 state, and remove them only in the already-confirmed
  clear-all path. Unrelated temporary files remain untouched. Deletion stays
  nonrecursive and inside the validated cache directory.

**Boundary:** The operator chooses the cache root and controls its location.
An explicit root may be a symlink. Result and CT cache operations bind the
direct child directory before reading, publishing, or deleting entries. POSIX
uses a no-follow directory descriptor. Windows holds the layer open and
rejects reparse points. Another writer with access to the cache can still
modify entries within that directory. Use a private root for cache integrity.

### Malicious CT provider responses

**Surface:** A compromised crt.sh / CertSpotter could return extremely large subdomain sets or adversarially crafted names attempting to amplify downstream work.

**Mitigation:** `src/recon_tool/sources/cert_providers.py`:
- Bounded crt.sh extraction before filtering/sorting: at most
  `MAX_SUBDOMAINS * 20` JSON entries inspected, `MAX_SUBDOMAINS * 10`
  raw names collected, and `MAX_SUBDOMAINS * 10` cert-summary entries retained
- CertSpotter pagination stops early after enough raw names are collected
- Filtering of wildcards, duplicates, and noise prefixes
- Final cap at `MAX_SUBDOMAINS = 100` after prioritization
- 8-second timeout per provider
- Pagination capped at 2 pages on CertSpotter

### MCP server exposure

**Surface:** The MCP server is a local subprocess communicating with the user's AI client over stdio. The client controls what tools are called.

**Mitigation:**
- The lookup and analysis tools are read-only; `reload_data` and the
  ephemeral fingerprint tools only modify in-memory or local process
  state (verified in `src/recon_tool/server/app.py` ToolAnnotations and Server
  Instructions)
- Tools accept domain strings that go through the same `validator.py` pipeline
- Invalid domain arguments produce a target-free structured warning with a
  request ID and stable reason code. Raw rejected values and repeated exception
  text are not written to MCP operator logs.
- Importing the server does not mutate shared logging. A default stderr handler
  exists only for the running stdio loop and is removed on exit.
- Unexpected server exits retain one bounded control-free diagnostic line with
  the exception type, so exception text cannot forge terminal rows.
- `inject_ephemeral_fingerprint` only persists in current process memory; it
  never writes to built-in files, custom config files, or the cache.
- Ephemeral fingerprint injection is quota-bounded in-process: 100 fingerprints,
  20 detections per injected fingerprint, and 500 total ephemeral detections.
  Rejected injections return JSON errors instead of growing memory or lookup
  work without bound.
- 120-second TTL cache and per-domain rate limiter prevent repeated-lookup abuse
- No HTTP / OAuth transport, no network listener

All posture and hardening tools operate exclusively on the same public-metadata
observables used by the core correlation engine (see
[correlation.md](correlation.md)). The MCP surface adds no new data
sources; it only exposes the existing inference pipeline through a
different transport.

---

## Out of scope

recon does **not** defend against:

- **Active scanning attacks.** recon does not scan ports, crawl arbitrary target
  applications, or test exploitability. An attacker with a shell on your machine
  can do more than recon can see.
- **Target credential theft during collection.** Collectors use no target
  credentials. This does not cover credentials in the optional remote adapter,
  maintainer-only validation environment, or an operator's surrounding system;
  those still require protection.
- **DNS cache poisoning at the OS level.** If the user's resolver is compromised, the entire threat model is compromised regardless of what recon does.
- **Supply-chain compromise of transitive dependencies.** Locked runtime
  dependencies, all development groups, and all extras are checked by
  blocking `pip-audit` gates in CI and release workflows. Their runner resolves
  the installed auditor under Python isolated
  mode, retries once only for recognized transport failures, and never converts
  a finding or exhausted retry into success. The later isolated SBOM job also
  blocks on every nonzero audit status. This detects known advisories; it does
  not prevent a compromise or inspect dependencies in-process.
- **Side-channel timing attacks against the user's identity.** Every query recon makes is visible to the intermediary services (OIDC endpoints, CT providers, the user's DNS resolver). See [`legal.md`](legal.md#what-sees-your-queries) for the exposure inventory.
- **Logging / telemetry exfiltration.** recon emits no telemetry. All output goes to the user's terminal or files they own.
- **Malicious plugin systems.** recon has no plugin system and executes no user code.

---

## Reporting vulnerabilities

See [`SECURITY.md`](../SECURITY.md). TL;DR: email `nick@pueo.io`, do not open a public issue.
