# Operational contract

The concrete runtime behavior a downstream integrator can depend on: the
timeouts, resource caps, exit codes, cache and partial-result semantics, and
determinism guarantees. These are not part of the locked JSON schema (see
[schema.md](schema.md) for that), but they are the operational behavior recon
holds itself to. Values here are current as of the latest release; they can move
within the stability contract, and the load-bearing ones are gated by tests
(see [assurance-case.md](assurance-case.md)).

The central engineering objective is to bound attacker-influenceable work and
represent failed collection as unavailable rather than negative evidence.
Named caps, deadlines, and regression tests enforce the boundaries below. They
are not a proof that every possible input is harmless: regex admission remains
heuristic, and a process-level budget or egress policy adds useful containment
when embedding recon in a long-lived service.

## Timeouts

| Timeout | Value | Scope |
|---|---|---|
| `RESOLVE_TIMEOUT` | 120 s | Aggregate wall-clock for the whole resolve pipeline (all sources + related-domain enrichment); on expiry raises `ReconLookupError(error_type="timeout")`. Override per call or with `--timeout`. |
| `DNS_QUERY_TIMEOUT` | 5 s | Per-DNS-query lifetime (total, including retries across nameservers); on expiry the query returns empty, not an error. |
| `_CT_TIMEOUT` | 6 s | Per CT-provider HTTP call (crt.sh, CertSpotter). |
| `DEFAULT_TIMEOUT` | 10 s | Default httpx client timeout for the shared HTTP client. |
| Google CSE / BIMI VMC / MTA-STS fetch | 5 s | The two opt-in direct-probe classes and the standard default MTA-STS policy fetch. |
| `_MAX_TOTAL_RETRY_SLEEP` | 30 s | Cumulative cap on retry backoff sleeping for a single HTTP request across all retries, so repeated 429s cannot stack toward the aggregate budget. Per-attempt `Retry-After` is also clamped to 30 s. |

For 429 and 503 responses, a numeric `Retry-After` value is accepted only when
it is finite and non-negative, then clamped to 30 seconds. Date-form,
malformed, negative, and non-finite values use exponential backoff instead.
`Retry-After: 0` retries without sleeping. The cumulative sleep cap still
applies across all attempts.

Before each shared-client request and redirect, recon resolves the destination
and requires every returned address to be public unicast. A missing hostname,
DNS error, empty answer, or invalid address fails closed before the HTTP
transport runs. When opening a connection, the backend revalidates the complete
answer set and dials validated numeric addresses, preserving the original Host
and TLS identity. DNS and dialing share the connection timeout. At most 16
interleaved IPv4/IPv6 candidates are raced at 250 ms intervals; unused sockets
are closed. Google identity redirects stay within HTTPS `accounts.google.com`
on port 443; external identity routing is observed without following it.

## Resource caps

A representative set; the full list lives in the source constants the
[assurance case](assurance-case.md) cross-references.

| Boundary | Cap |
|---|---|
| HTTP response body | `_MAX_RESPONSE_BYTES` = 10 MB, aborted mid-read; compressing `Content-Encoding` is refused (decompression-bomb guard) since recon requests identity encoding |
| HTTP redirects / retries | `MAX_REDIRECTS` = 5; `MAX_RETRIES` = 3 (429/503 only) |
| Domain input | `_MAX_INPUT_LENGTH` = 500 chars before normalization; normalized DNS presentation form = 253 ASCII octets total and 63 per label; source-derived display strings `_MAX_DISPLAY_LEN` = 200 |
| DNS regex-match inputs | `_MAX_TXT_MATCH_LENGTH` = 4096; `_MAX_SUBDOMAIN_TXT_MATCH_LEN` = 4096; `_MAX_CNAME_MATCH_LEN` = 255; SPF redirect depth = 3 |
| Related-domain enrichment | `MAX_RELATED_ENRICHMENTS` = 15 (6 deeper-tier) |
| CT extraction | `MAX_SUBDOMAINS` = 100; `_MAX_CRTSH_ENTRIES` = 2000; `_MAX_SANS_PER_CERT` = 2000; `_MAX_CRTSH_CERT_SUMMARY_ENTRIES` = 1000 (bounds CertSpotter too); `_MAX_PAGES` = 2; `_CT_GLOBAL_CONCURRENCY` = 2 |
| CT cert intelligence | wildcard clusters 10 (20 names); bursts 8 (25 names) |
| CT co-occurrence graph | `MAX_GRAPH_NODES` = 500; `_MAX_GRAPH_ENTRIES` = 1000; `_MAX_SANS_PER_CERT_FOR_EDGES` = 60; `_MAX_EDGE_ISSUER_SAMPLES` = 32; clusters 20 (50 members); `MAX_EDGES_RETAINED` = 2000 |
| Identity | `_MAX_AUTODISCOVER_DOMAINS` = 1000 federated domains |
| Fingerprint catalog | pattern length 500; `_MAX_CATALOG_ENTRIES_PER_FILE` = 2000; ephemeral (MCP) fingerprints 100 / 20 detections each / 500 total / 200-char fields |
| Cache files | `_MAX_CACHE_FILE_BYTES` = 5 MB; `_MAX_CT_CACHE_FILE_BYTES` = 5 MB (oversized = miss) |
| Observation capsule input | `MAX_CAPSULE_BYTES` = 10 MiB; regular files only; symbolic links, mutation during read, excess JSON nesting, non-finite numbers, invalid timestamps, and digest mismatches are rejected |
| NamespaceReviewBundle artifact | `MAX_REVIEW_BUNDLE_BYTES` = 10 MiB; validated before atomic local writes and after bounded regular-file loads; unknown owned fields, invalid references, non-finite numbers, invalid timestamps, and digest mismatches are rejected |
| Persisted rate-limiter state | 64 KiB per provider; versioned, provider-bound, finite numeric fields only |
| PyPI update metadata | 5 MiB response body and 100 JSON nesting levels |
| Batch input | 10,000 non-comment input records before deduplication; 1 KiB UTF-8 per logical line; 10 MiB UTF-8 total |

## Exit codes

A script can branch on the outcome without parsing output (full contract in
[schema.md](schema.md#exit-codes)):

| Code | Constant | Meaning |
|---|---|---|
| 0 | `EXIT_SUCCESS` | Completed and produced output |
| 1 | `EXIT_ERROR` | Explicitly handled general command or server failure, plus Python's default before the CLI last-resort handler is active |
| 2 | `EXIT_VALIDATION` | Bad input rejected before work (malformed domain, missing file, mutually exclusive flags, refused unsafe invocation) |
| 3 | `EXIT_NO_DATA` | Target resolved but no information available, or `recon delta` had no cached baseline |
| 4 | `EXIT_INTERNAL` | recon caught a network/pipeline failure, or the CLI last-resort handler caught an unexpected runtime crash |

For single-domain lookup paths, only a structured resolver error with
`error_type="no_data"` maps to exit 3. A first `recon delta` call also exits 3
when no cached snapshot exists; it performs no live resolution and emits no
delta payload. Aggregate timeout,
`all_sources_failed`, and unknown structured resolver failures preserve their
concrete message and map to exit 4. Successful JSON, Markdown, and plain
payloads are written alone to stdout. Human progress and `--verbose` source
diagnostics use stderr, so a successful structured stdout stream can be parsed
without removing presentation lines. Verbose source diagnostics use explicit
`match`, `no match`, and `unavailable` states; a clean negative observation
is not styled or labeled as a transport failure. Those rows are printed for
the collection that produced the source-health line. A result reused from
cache keeps the expanded panel and does not invent unit states.

Batch processing is record-oriented. Once batch arguments and input are valid,
per-domain validation, lookup, timeout, and internal failure records retain
exit 0 even when every record is an error. JSON and NDJSON consumers must
inspect `record_type` and `error_kind`; CSV consumers must inspect `error`.
Changing that run-level behavior requires a compatibility decision. Unexpected
per-domain exception details are replaced with stable output and retained only
in opt-in debug logs.

When a downstream consumer closes a normal output pipe early, recon exits 0
without creating a crash log. Other unexpected runtime and operating-system
errors caught by the top-level CLI handler retain the exit 4 crash-artifact
path. Code 1 remains available for explicitly handled general command and
server failures, and for exceptions that escape before that handler is active.

Capsule capture bypasses the result cache and records CT cache provenance from
the live resolver result. Capsule writes refuse existing paths unless `--force`
is explicit, use a same-directory exclusive temporary file, flush it, and
replace the destination atomically. Replay and comparison do no network work.
Malformed or integrity-invalid capsule inputs use exit 2; a caught capture
pipeline failure uses exit 4. The capsule digest is deterministic integrity
metadata, not authentication.

`recon review` validates its domain and output path before collection, bypasses
the lookup-result cache, fixes direct probes off, and resolves once. A
successful baseline exits 0. A typed no-data bundle exits 3; timeout and other
handled collection failures exit 4. With `--json`, the success or failure
bundle is the only stdout payload. `--output` writes that same validated object
atomically and refuses an existing file unless `--force` is explicit. The
ReviewBundle digest is deterministic integrity metadata, not authentication.

MCP validation rejections emit one structured warning containing a request ID
and the stable reason `invalid_domain`. The rejected argument and exception
text are returned only through the caller's private tool response and are not
copied into operator logs. Successful validation is required before a domain
value can appear in ordinary cache, resolution, or failure diagnostics.

Human cache-miss lookups (the panel and `--plain`, including the exposure,
gaps and compare views) report collection on stderr through the source ladder:
one row per source family, settled only by a progress event the resolver
emits when that source returns, never by elapsed time. The ladder animates
only on an interactive stderr and is static under `--no-color`, `NO_COLOR`,
`TERM=dumb`, `CI`, `RECON_NO_ANIMATION`, and `--debug`. Every human cache-miss
lookup ends its stderr progress with one source-health line, such as
`6 sources: 4 matched, 2 no match`, counted per collection unit. `--json`,
`--md` and `--explain-dag` print no ladder and no health line. Chain
resolution keeps a separate outcome-neutral label for that operation. Progress
text does not claim that an inference pass or posture analysis is running.

Without `--debug`, warnings logged by collectors during a lookup, chain, batch
or review are captured and printed once on stderr after collection, grouped by
condition, deduplicated, bounded to three named hosts per line, and reduced to
hostname characters: for example `1 host could not be resolved (...). Run recon
doctor.` This applies to `--json` too, where the summary replaces raw warning
lines on stderr and stdout carries only the payload. A DNS resolution failure
is worded `could not resolve`; only a destination refused for a private
address uses `skipped: resolves to a private address`. `--debug` enables diagnostics from both
owned logger namespaces (`recon` and `recon_tool`), installs one CLI stderr
handler per namespace without adding another on repeat configuration, and
prevents propagation to host root handlers. Direct handlers explicitly
installed on an owned or child logger by an embedding host are preserved and
remain the host's responsibility. Debug diagnostics can include domain inputs,
local paths, configuration context, and exception details. Review and redact
them before sharing.

Importing the MCP server does not add a process-wide logging handler. When the
stdio server actually runs without an existing logging configuration, it adds a
temporary stderr handler for that runtime and removes it on exit. Request-level
logging of queried targets is disabled by default (level WARNING) and opt-in
via `RECON_MCP_LOG_REQUESTS=1`. Warning and exception diagnostics can still
contain domain inputs; review client logs before sharing them. An unexpected
server failure emits one bounded control-free line with the exception type;
exception text cannot inject a second row or terminal control sequence.

MCP lookup tools preserve the same distinction. Only `error_type="no_data"`
uses `No information found for ...`; timeouts and total source failure retain
truthful failure text instead of being presented as an empty observation.

The `recon doctor` health check follows the same convention: it exits 0 when
every check passes or only optional enrichment is degraded, and exits 1 when
a core check fails, so a CI or monitoring job can gate on environment health
instead of always reading success. Certificate transparency is optional
enrichment. Doctor probes crt.sh and CertSpotter. It calls certificate
transparency unavailable only when both probes warn. One provider answering
means lookups can fall back. `recon doctor --mcp`
follows the same rule for MCP setup: it exits 1 when the package or server
cannot load, instructions are absent, or any canonical tool or local resource
registration is missing. `recon mcp doctor` separately spawns the local stdio
server twice, once in an empty temporary directory and once with the exact
launcher `recon mcp install` writes from the current directory or
`--launch-cwd`, names each launch it exercised, checks discovery and canonical tool registrations, and reads all six
canonical JSON resources. It exits non-zero on an invalid resource envelope,
URI, media type, JSON object, catalog count/list/identifier relationship,
schema or surface-inventory envelope, cache metadata, missing registration,
timeout, or protocol failure. Completed protocol phases remain visible when a
later phase fails. This live server check does not inspect a client's saved
configuration; `recon doctor --client=<name>` covers that boundary.
Default mode contacts Microsoft identity endpoints, DNS for `example.com`, and
one certificate-transparency request each to crt.sh and CertSpotter, using
synthetic inputs. It does not accept or query a target namespace.
It also asks the system resolver for one random name under the reserved
`.invalid` top-level domain. Any answer other than NXDOMAIN is a `warn` row
naming a resolver that answers names that should not exist, a condition that
makes related-domain results unreliable (see
[limitations](limitations.md#resolvers-that-answer-names-that-should-not-exist)).
That query runs only in doctor; lookups add no probe for it.
Every doctor mode prints the same lowercase status words, `ok`, `warn`, `fail`,
and `info`, and closes with a summary in the color of its worst status. A
failure summary counts the failed rows and ends with a `Next:` step.
`recon doctor --json` and `recon doctor --client=<name> --json` emit the same
rows as one JSON object on stdout with the human view's exit code; see
[schema.md](schema.md#doctor-report-recon-doctor---json).
The `--fix`, `--mcp`, and `--client` modes are local-only. Every dynamic doctor
row strips control bytes, escapes terminal markup, and bounds displayed detail.
Every ordinary `httpx.RequestError` becomes a named failed row for a core probe
or a warning row for optional CT enrichment, and remaining independent checks
continue before the final summary and exit status.

## Batch CSV contract

`recon batch <file> --csv` emits RFC 4180 CSV with this canonical column order:

`domain,provider,display_name,tenant_id,auth_type,confidence,email_security_score,service_count,dmarc_policy,mta_sts_mode,google_auth_type,error`

Every input retained after batch deduplication produces one data row. A
successful lookup leaves `error` empty. A failed lookup populates `domain` and
`error` while leaving the observation columns empty, so spreadsheet users and
machine consumers can distinguish an observed sparse result from a lookup
failure without parsing human text.

Before RFC 4180 quoting, recon neutralizes spreadsheet formulas in every
textual cell. If the first character after leading ASCII spaces is `=`, `+`,
`-`, `@`, a tab, a carriage return, or a newline, recon prefixes the cell with
a single quote. This applies to successful observation fields and to failure
domains and messages. Consumers that require the unmodified structured values
should use JSON rather than the spreadsheet-oriented CSV surface.

## Cache and partial-result semantics

- **Disk caches never raise to the caller.** Any read failure (missing, stale,
  corrupt, non-object, wrong-shaped, numerically invalid, oversized, or
  deeply-nested JSON) degrades to a clean miss. Normal
  TenantInfo reads use a 24 h TTL; `recon delta` may retain the same entry for up
  to 30 days as its comparison baseline. The per-domain CT cache TTL is 30 days.
  Both caches admit data through a bounded regular-file descriptor, reject
  symbolic links, stable redirected cache directories, mutation during the
  read, materially future mtimes, and expired data before JSON decoding, then
  write atomically with a sibling `mkstemp` file followed by `os.replace`.
- **Cache identity follows lookup identity.** Result and CT payloads are bound
  to the validated domain in their filename. Registrable-apex and literal-host
  entries are independent. `recon cache show <host> --exact` inspects literal
  result and CT keys; `recon cache clear <host> --exact` removes that host from
  both caches.
  Without `--exact`, cache commands retain normal apex reduction. CT entries
  written before v2.6.1 lack the binding metadata and repopulate on demand.
- **Cache inspection is metadata-only and failure-aware.** `recon cache show`
  reports both disk layers independently in single-entry and overview modes,
  including reuse status, age, TTL, timestamps, and file size, plus CT provider
  and subdomain count. The default overview enumerates filenames for exact
  totals while retaining and opening only the lexicographically first 100 JSON
  files per layer; it reports the exact uninspected count. `--all` explicitly
  opts into complete payload inspection. It never renders cached tenant,
  service, evidence, or raw record fields. Missing files remain a successful
  `no entry`; an invalid, redirected, unreadable, or rejected entry is `could
  not inspect`, retains its raw reason only in debug logging, and causes exit 4
  after other available metadata is shown. Expired files remain visible but are
  labeled for refresh instead of reuse. Cache-writer-shaped `*.tmp` residue is
  counted without payload inspection and also causes a visible exit 4.
  A structurally identified envelope from another collection policy is an
  expected, separate state: `other collection policy; not reusable here`.
  Bounded JSON decoding precedes the envelope check; its typed payload is not
  admitted or rendered, its resolver identity is not printed, and the mismatch
  does not cause exit 4. Both cache read paths still refuse to serve it.
  Invalid JSON, version/domain bindings, or policy-identity syntax remain
  inspection failures even when the file claims another policy.
- **Cache deletion failures remain visible.** The CLI clears CT and result
  layers independently, including completed JSON entries and interrupted-write
  artifacts matching the cache writer's filename shape during confirmed
  clear-all. Unrelated `*.tmp` files are preserved. The command reports each
  completed deletion class, identifies any layer that failed, and exits 4
  after partial work. Missing entries remain a successful no-op. Ordinary
  output never includes the raw filesystem exception; opt-in debug logging
  retains it for diagnosis. Existing Python bool and count helpers remain
  non-raising compatibility surfaces.
- **Rate-limiter warm starts fail closed.** Persisted state is versioned and
  provider-bound. Oversized, nested, stale, cross-provider, non-finite,
  overflowing, or out-of-range fields are ignored as one invalid snapshot.
  Writes use a random exclusive temporary path and atomic replacement.
- **Partial / degraded results are honored, not dropped.** `all_sources_failed`
  is raised only when *every* attempted source errored and no tenant was found;
  if any source returns a clean result (even with no services), it is kept as a
  sparse "looked and found nothing" answer. A source that makes no attempt by
  default (the opt-in Google CSE probe) is excluded from that decision rather
  than counted as a clean result. The DNS source reports a whole-source error
  (`dns_records`) when none of its queries received a usable resolver response
  (every query timed out or found no usable nameserver) and nothing else, such
  as CT, contributed. One answered query, a NoAnswer, or an NXDOMAIN response
  is a usable response, so successful-empty and mixed DNS results stay partial
  lookups. With every source unavailable, `recon <domain>` exits 4 with the
  concrete `all_sources_failed` message, `recon review` exits 4 with a failed
  workflow, and MCP `lookup_tenant` returns its all-sources-failed error. If a
  rendered result ever carries every default source as unavailable, the note
  says "All N sources unavailable" rather than "Some". A failed source is recorded in
  `degraded_sources`, and confidence is downgraded one level when a source is
  degraded, except when only the CT providers degraded and a CT cache fallback
  recovered the data.
- **Partial results are answered, not reused.** A result is a collection
  failure when `degraded_sources` holds any non-CT marker, or holds CT provider
  markers while no CT path (another provider, a partial page, or the CT cache)
  supplied data. Such a result is returned for the current lookup and still
  written to the result cache, where `recon delta` can use it as a baseline,
  but read admission never serves it to an ordinary lookup or the `--exposure`
  and `--gaps` reports. The rule applies on read, so entries written by earlier
  releases recover without a manual clear. Sparse results with no failure stay
  reusable; low confidence and empty service lists are not rejection rules.
  `recon cache show` uses the same admission function, so its status matches
  what a lookup does, and it reports metadata only. `--no-cache` bypasses both
  the read and the write. A human lookup served from the cache names the reuse
  in one muted line from the internal `resolved_at` time; the lookup JSON does
  not gain `resolved_at` or `cached_at`. The MCP server's bounded in-process
  cache (`CACHE_TTL`, 120 seconds) is separate and unchanged.
- **Granular failure is not negative evidence.** DNS and detector markers may
  identify one unavailable observation channel, including `dns:apex_txt`,
  `dns:dmarc`, `dns:mta_sts`, `http:mta_sts_policy`, or `dns:mx`. Bayesian
  absence factors, cohort denominators, exposure scores, and hardening-gap
  output mask only the affected channel. `NXDOMAIN` and `NoAnswer` remain clean,
  observed empty responses. Legacy `dns` and current `dns_records` markers mask
  every DNS channel.
- **Queried-name NXDOMAIN is stated, not narrated.** The DNS adapter retains
  each query's response class (answer, NoAnswer, NXDOMAIN, or unavailable)
  before rendering. When every clean response for the queried name itself was
  NXDOMAIN, the panel, `--plain`, `--md`, and MCP text say "No DNS name: the
  resolver returned NXDOMAIN for this domain.", JSON carries the additive
  `dns_name_status: "nxdomain"`, and the web-only, parked, staging, and
  sparse-footprint narration is withheld. Exit code 0, `partial`, and the
  confidence rules are unchanged. NoAnswer, transport failure, and a missing
  subdomain under an existing apex never produce that statement.
- **Observed empty is not authenticated denial.** The resolver adapter does not
  retain the authority section, recursive-resolver identity, or DNSSEC denial
  validation, and its private-canonical safety suppression also returns an
  empty list. Current public surfaces may describe the operational result as no
  record observed, but the internal claim-contract layer does not promote it to
  an authoritative or authenticated negative certificate.
- **DMARC follows RFC 9989 discovery semantics.** ASCII space or tab around
  `=` and case-insensitive tag names are accepted; the `DMARC1` value remains
  case-sensitive. A missing or invalid `p`, or an invalid `sp` or `np`, falls
  back to effective `none` only when `rua` contains a syntactically valid
  reporting URI. The exact reject claim signs only an explicit valid `p` value,
  so fallback `none` remains unresolved for that narrower predicate. The DMARC
  service and raw record remain visible, while stable `dmarc_policy` stays null
  rather than fabricating an explicit `p=none`.
- **CT is cache-first and fault-tolerant.** A fresh CT cache entry short-circuits
  the live providers; on live failure the cache is the final fallback, annotated
  with `ct_attempt_outcome` (`cache_hit`, `live_success`, `cache_miss`,
  `live_rate_limited`, `live_other_failure`, `breaker_open`). A mid-pagination
  429 returns partial CT data rather than an error. When providers fail in
  different ways, live attempted failures are labeled ahead of a separate open
  breaker so `breaker_open` means every failed provider was stopped locally.
  Cache reuse preserves the full certificate summary and infrastructure
  cluster report, including wildcard sibling clusters and deployment bursts;
  a summary-only entry with a positive certificate count is still a usable hit.
  Empty graph or summary containers are not contributions. If every DNS query
  is unavailable and CT contributed no retained names, certificate metadata,
  or graph observations, the DNS source fails even if an empty CT cache file
  exists. Fully failed lookup and review workflows retain exit 4.
- **Batch identity is canonical.** Valid URL, sub-host, and apex spellings that
  reduce to the same registrable apex are resolved once, preserving the first
  occurrence. Malformed inputs deduplicate by their trimmed, lowercased raw
  spelling, so each distinct normalized malformed spelling produces one
  diagnostic record. The 10,000-record limit is enforced before this
  deduplication. Line and stream limits are applied to UTF-8 bytes, not Unicode
  code-point counts.
- **Sparse is flagged, not hidden.** `sparse=true` means the uncertainty band's
  effective display mass is at its floor. The model score and band remain
  model-relative and do not replace explicit unresolved output (see
  [correlation.md](correlation.md)).

## Determinism and reproducibility

- **Same captured evidence and version, same interpretation.** A domain string
  alone is not the complete input: DNS, CT, identity responses, cache state,
  catalog data, model data, and software versions can change. Given the same
  normalized evidence snapshot, options, and installed recon, catalog, model,
  and Public Suffix List versions, interpretation is deterministic. The CT
  community-detection layer uses a fixed Louvain seed and normalizes node
  insertion order before partitioning; above the node cap it falls back to
  deterministic connected components. Cluster, member, edge, burst, and
  subdomain orderings are sorted and canonical. Enriched services, slugs, and
  `degraded_sources` are emitted sorted.
- **Constrained same-job build repeatability is checked.** With
  `SOURCE_DATE_EPOCH`, uv 0.13.9, and the hash-locked backend graph fixed, CI
  builds the sdist, reconstructs its wheel, repeats that sequence inside one
  Ubuntu job, and requires matching hashes. This does not promise byte identity
  across different Python, runner, operating-system, or archive environments;
  signed provenance remains the source-to-workflow verification mechanism. See
  [supply-chain.md](supply-chain.md).
- **Published distribution channels must agree byte for byte.** After PyPI
  publication, a read-only release job requires the exact wheel and sdist and
  matches both SHA-256 digests against the sealed build pair before GitHub
  Release assets can be created or replaced. Remote readiness repeats that
  comparison and validates the completed SBOM. Releases produced by the current
  workflow verify the wheel, sdist, and SBOM against the exported provenance
  bundle bound to the source tag and commit digest; the exact v2.6.3 historical
  exception verifies its wheel and sdist. Existing-release recovery also rejects
  unsafe publication state before replacing assets. A mismatch after PyPI
  publication is a visible partial-publication state that blocks GitHub Release
  creation; it does not roll back immutable PyPI files. This is
  publication-state integrity, not a promise that a fresh build on another host
  will reproduce the same bytes.
- **Apex normalization is deterministic per installed version.** Input is
  reduced to its registrable apex (eTLD+1) using the Public Suffix List bundled
  in the pinned `publicsuffixlist` dependency, so the same input yields the same
  `queried_domain` for a given install. The reduction can change only when that
  dependency is upgraded and the PSL itself has changed (a new or retired public
  suffix), never within a version. It is not a security boundary: an unknown
  suffix falls back to the validated host rather than guessing.
