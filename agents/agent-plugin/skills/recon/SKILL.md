---
name: recon
description: Public-metadata domain intelligence - Microsoft 365 / Google Workspace tenant identification, email security configuration (DMARC, DKIM, SPF, MTA-STS, BIMI), SaaS fingerprinting from DNS, certificate-transparency findings, related-domain discovery. Use when a domain name appears alongside phrases like "what does <company> use", "tenant", "DMARC", "email security posture", "SaaS stack", "fingerprint", "passive recon", or "vendor diligence". Passive in scope - never use for active scanning, port scans, credentialed access, or vulnerability checks.
license: Apache-2.0
compatibility: 'Requires recon-tool 2.27.1 or a compatible v2 release and Python 3.11+. Use connected MCP tools or a shell with recon on PATH. Live lookups require public network access. '
metadata:
  author: pueo-labs
  version: 2.27.1
---

# recon

Public-metadata domain intelligence. Given an apex domain, recon returns hedged
observations about that queried public namespace and its evidence-linked service
and identity indicators. It uses public DNS, certificate transparency, and
unauthenticated identity-discovery endpoints without credentials or API keys.
Default collection performs no active scanning or port probing: authoritative
DNS may observe resolver traffic, and MTA-STS is the only default target-owned
HTTP/application request. Google CSE and BIMI certificate requests are explicit
opt-in direct probes.

## When this is the right tool

Reach for recon when the user wants to understand a domain's public-facing configuration:

- "Is `delta.invalid` on Microsoft 365? What's their tenant ID?"
- "Score the email security on `gamma.invalid`."
- "What SaaS vendors does `beta.invalid` appear to use?"
- "Find related domains for `alpha.invalid`."
- "Compare the posture of `a.invalid` and `b.invalid`."

Do not reach for recon when the user wants:

- Active scanning, port scans, or credentialed inventory.
- Vulnerability assessment or exploit checks.
- Company financials, news, hiring signals, or firmographic data.
- Generic target-owned application crawling. The only direct target interactions are the standards-compliant `mta-sts.{domain}` request on the default path and the documented CSE / BIMI certificate probes when explicitly enabled.

If the user wants a verdict like "is this company secure," recon is not that tool. It surfaces observations; the user supplies the judgment.

## Before first invocation

First inspect the available tools for the connected recon server. Client tool
namespaces vary; identify recon by its server identity and the exposed tool
names and descriptions, not a required prefix. Already-connected MCP tools are
sufficient: use them without requiring a shell or running `recon --version`.
Do not register a second server or install another runtime to use that connection.

Only for the CLI fallback, confirm recon is installed before the first command:
if no shell is available, report that limitation instead of attempting a tool
that the client does not expose.

```bash
recon --version
```

If the command is not found:

> "`recon-tool` is not installed. It's a Python CLI from github.com/pueo-labs/recon that reads public DNS, identity endpoints, and certificate transparency - no credentials needed. Install with `pip install recon-tool`? (Python 3.11+ required.)"

Wait for explicit approval, then `pip install recon-tool` followed by `recon doctor` to verify connectivity. If `recon --version` succeeds, continue immediately - do not re-prompt on subsequent calls in the same session.

If the user separately asks you to wire recon into another MCP client (Claude Desktop, Cursor, VS Code, Windsurf, Kiro), use `recon mcp install --client=<name>` rather than instructing them to copy-paste a JSON block by hand. Run `recon mcp doctor` afterward for a live JSON-RPC handshake check.

## Detecting whether MCP is connected

Use the tool names actually exposed by the client for recon's `lookup_tenant`,
`analyze_posture`, and other capabilities. Examples such as
`mcp__recon__lookup_tenant` are not a portable naming requirement. Prefer the
connected MCP server; otherwise use the CLI when a shell is available. Do not
call a lookup speculatively to test connectivity.

The portable MCP process stores recon configuration, caches, and limiter state
under the client-managed `PLUGIN_DATA/recon` directory. It does not implicitly
share the CLI's user configuration. Keep user-requested reports in the user's
chosen workspace, not the installed plugin directory; ask for an output location
if the client has not provided a writable workspace.

## Domain validation before any CLI invocation (mandatory)

When falling back to the CLI, **never** interpolate a user- or context-supplied domain into a Bash command without first validating it against this exact pattern:

```
^[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?$
```

Lowercase the input and strip a leading `https://` or `http://`. For ordinary apex lookups, also strip a leading `www.`; preserve it when the user requests the literal host with `--exact`. Then match. If the resulting string does **not** match - including any presence of whitespace, quotes, `;`, `|`, `&`, `$`, backticks, parentheses, redirection (`>` `<`), path components (`/` `\`), or non-ASCII - refuse to run the command and tell the user the domain is malformed. Do not "fix it up" by stripping characters; reject the input.

Pass the validated domain inside double quotes in the Bash command (`recon "validated.example.com"`) as defense-in-depth; the regex is the primary control. The MCP path takes structured arguments and is not subject to this rule.

Once a domain passes validation, recon reduces it to the registrable apex (eTLD+1) before analysis, so `mail.example.co.uk` is analyzed as `example.co.uk` and `queried_domain` is the apex - almost always what you want, since the signal lives at the apex. Pass `--exact` only when the user specifically wants DNS facts about that one literal sub-host. This does not relax the validation rule above.

Use the CLI for an explicitly requested literal-host lookup with `--exact`.
The MCP domain tools normalize to the apex and do not offer that flag.

## Two invocation modes

### Default mode - panel output

Use this when the user asks recon-shaped questions conversationally - "recon alpha.invalid", "what does beta.invalid run on" - without explicitly requesting full or structured data.

When MCP is connected, call `lookup_tenant(domain)` and reformat to a panel-equivalent summary. End with "Ask for full details or evidence." Then stop. Otherwise shell out (after validating `<domain>` per the rule above):

```bash
recon "<domain>"
```

**Relay the CLI panel output verbatim.** Do not reformat it into Markdown bullets, tables, or headers. The panel is purpose-built and tighter than anything reformatted. End with a single short pointer such as *"Run with `--full` for everything, or ask me to `--explain` the reasoning."* Then stop. No interpretation, no commentary.

<details>
<summary>Sample panel (collapsed)</summary>

```
Synthetic Alpha Ltd (unverified)
alpha.invalid
Reserved name: results are public residue, not an organization.
──────────────────────────────────────────────────────────────────────────────
  Provider     Microsoft 365 + Proofpoint gateway
  Tenant       a1b2c3d4-e5f6-7890-abcd-ef1234567890 • NA
  Auth         Federated
  Confidence   ●●● High (4 sources)

Services
  Email          Microsoft 365, Proofpoint, DMARC, DKIM, SPF: strict (-all), BIMI
  Identity       Okta, Entra ID
  Cloud          Cloudflare (CDN), AWS Route 53 (DNS)
  Security       Wiz, CAA: 3 issuers authorized
  Collaboration  Slack, Atlassian (Jira/Confluence)

Insights
  Federated identity observed; identity-vendor indicators: Okta
  Email security: observed controls: DMARC reject, DKIM, SPF strict, BIMI
  MX gateway observed: Proofpoint
```

That is the shape recon emits. Pass it through unchanged.

</details>

### Full / structured mode - `--full --json`

Trigger this mode when the user explicitly says "full", "max details", "give me everything",
or when downstream automation needs structured data.

With connected MCP, call `lookup_tenant(domain, format="json")` using the actual
tool name exposed by the client. No Bash command is needed. On success, save the
returned JSON text only if the client exposes both a file-write tool and a
writable user workspace. Use the user's chosen output location, and report a
filename only after the write succeeds. The three-line headline below also
applies to a successfully saved MCP result.

If file writing or a writable workspace is unavailable, give a brief hedged
summary and state that artifact delivery is unavailable in this client. Do not
claim a file was saved, attempt an unavailable shell or file tool, or dump raw
JSON unless the user explicitly requests inline JSON. If the lookup itself
fails, report that failure instead of claiming full JSON was collected. Then
stop; the CLI-only recipe below does not apply to the connected MCP branch.

For the CLI fallback only, do **not** use shell redirection; capture stdout and
write the file with your own file-write tool:

```bash
recon "<domain>" --full --json
```

In this mode, **do not dump the JSON inline.** Output is often several KB and
may grow materially with certificate-transparency and evidence data, so inline
output consumes context for no benefit. Instead:

1. Capture stdout from the Bash call. Use your file-write tool to save it to `recon-<validated-domain>.json` in the current working directory (or a path the user specifies). Never substitute the unvalidated domain into a shell redirect.
2. Reply with a 3-line headline only (field names per the stable v2.0 contract in [`docs/recon-schema.json`](https://github.com/pueo-labs/recon/blob/v2.27.1/docs/recon-schema.json)):
   > **{display_name}** - {provider}, confidence {confidence}.
   > {N services detected, {ct_subdomain_count} CT subdomains, email security {email_security_score}/5}.
   > Full JSON saved to `recon-{domain}.json`. Ready for the next ask.
3. Stop. Wait for the user.

If the user later asks for a structured summary of the JSON, follow the output-voice rules below.

### Explain mode - `--explain`

Use when the user asks "why", "how do you know", or "show your reasoning".
Plain `recon <domain> --explain` emits the panel, per-source status, and flat
evidence and explanation sections. `recon <domain> --json --explain` adds the
structured provenance graph as `explanation_dag`; the MCP equivalent is
`lookup_tenant(domain, format="json", explain=true)`. Each flat and graph
terminal reports `exact`, `exact_rule_only`, `reconstructed`, or `unsupported`
lineage. Read `exact_provenance_complete` and
`lineage_disconnected_terminals` for exact evidence-to-rule coverage.
Schema-version-1 `provenance_complete` retains its broader graph-reachability
meaning. The separate `--explain-dag` flag renders the Bayesian
inference DAG and is not the same graph.

Surface the *summary* of the chain - which evidence drove which insight - rather than dumping the full DAG. Offer the full DAG on follow-up.

## Preferring MCP over CLI

When the `recon` MCP server is connected, use it instead of shelling out - typed arguments avoid command interpolation. `lookup_tenant` and the narrative tools return text, while many analysis and catalog tools expose structured results. Common starting points:

- `lookup_tenant(domain, format="json", explain=true)` - full domain intelligence with provenance.
- `build_review_bundle(domain)` - one fresh, cache-bypassed single-namespace handoff with an explained baseline, source-opportunity states, evidence-linked review candidates, and no direct probes. Use this for a bounded review artifact or the `domain_report` prompt.
- `analyze_posture(domain, profile=...)` - posture observations, optionally biased by a profile lens.
- `assess_exposure(domain)` - model-bound public-evidence index on a 0-100 compatibility scale, with an exact-evidence floor, bounded ceiling, and complete component ledger. The current component model assigns at most 90 points. It is not an overall security score. Cache first; it may run the ordinary base lookup on a miss, while index computation adds no network calls after resolution.
- `find_hardening_gaps(domain)` - categorized gaps with neutral "Consider" notes.
- `simulate_hardening(domain, fixes=[...])` - what-if index arithmetic with hypothetical fixes applied, not a prediction of overall security change.
- `compare_postures(domain_a, domain_b)` - side-by-side comparison of public configuration evidence, not overall security.
- `cluster_verification_tokens(domains=[...])` - report exact administrative TXT token reuse while leaving shared administration, copied configuration, managed service, and stale residue as compatible explanations.
- `chain_lookup(domain, depth)` - recursively follow every `related_domains` observation from each ordinary lookup, including bounded CT, CNAME, Exchange/identity endpoint, autodiscover, and DKIM tenant-domain breadcrumbs. Each queued name can trigger another full public-metadata lookup. Discovered names do not establish ownership or a corporate relationship.

For quick catalog browsing, start with `get_fingerprints(limit=20, offset=0)`. For an exhaustive no-match check, either read the full `recon://fingerprints` resource or continue 20-item pages until a page has fewer than 20 entries; a first page cannot establish absence. Browse `recon://signals` and `recon://profiles` before guessing what recon can detect. These local calls are free, make no network requests, and return the live catalogs.

CLI fallbacks when the MCP server is not connected:

- `recon review <domain> --json` - fresh NamespaceReviewBundle; add `--output review.json` for a caller-owned local artifact.
- `recon <domain> --json` - structured output.
- `recon <domain> --explain` - panel, source status, and flat retained-evidence explanations.
- `recon <domain> --json --explain` - structured lookup plus the lineage-qualified provenance graph.
- `recon batch <file> --json` - list of domains with cross-domain token clustering.
- `recon delta <domain>` - diff against the last cached snapshot. Relay verbatim like the default panel.

Most of the analysis the MCP tools expose is reachable from the CLI too. Reach for these rather than stopping at the plain panel when the user wants the model-bound index or categorized observations:

- `recon <domain> --exposure --json` produces the 0-100 model-bound public-evidence index. This is the CLI equivalent of `assess_exposure`; the plain panel does not carry this compatibility value, and it is not an overall security score.
- `recon <domain> --gaps --json` produces the categorized hardening gaps with neutral "Consider" notes. CLI equivalent of `find_hardening_gaps`.
- Bayesian fusion is enabled by default; `--no-fusion` skips it. `recon <domain> --explain-dag --explain-dag-format mermaid` renders the separate Bayesian inference DAG inline in chat. These are the CLI equivalents of `get_posteriors` and `explain_dag`.

What stays MCP-only, because it needs cached process state or an iterative loop:
`simulate_hardening` what-if loops, cache-only ephemeral-fingerprint replay for
retained apex/root TXT, SPF, MX, NS, and CNAME observations, live two-domain
`compare_postures`, and `test_hypothesis`. Owner-qualified ephemeral rules need
the fresh-lookup path described below. When the MCP server is not connected and
the user asks for one of these, say so plainly rather than approximating it.

## Workflow patterns

Single-domain lookup (the common case):

1. Use `lookup_tenant(domain)` or the bare CLI command for the compact answer.
2. Request JSON and `explain=true` when the question needs evidence or downstream processing; keep the human answer focused on the requested services.
3. Use `assess_exposure` or `find_hardening_gaps` only for a requested posture discussion, and `simulate_hardening` only for an explicit what-if question.

Service questions across a supplied domain list:

1. The supplied list authorizes lookups of those domains. Use `lookup_tenant(domain, format="json")` for each, or write a domain file and run `recon batch <file> --json`. Use `--ndjson` for streamed results on a large list.
2. Return a compact table with domain, requested service indicators, evidence type, confidence and relevant collection failures. Preserve per-domain errors and partial results. "Not observed" is not "not used"; a failed relevant source is unavailable evidence.
3. Add token clustering, ecosystem relationships or detailed posture only when the question needs them. Do not follow related domains beyond the supplied set without a request.
4. If only company names are supplied, ask for their domains. Do not require confirmation that the companies actually use the observed services.

Family-of-companies / portfolio rollup:

The operator supplies a group of related apexes - parent + subsidiaries, an M&A target's brand portfolio, a holding-company structure - and wants a unified report. recon does **not** infer ownership. The operator owns the relationship; recon describes observable structure across the set.

1. **Use the supplied domains.** Ask for apexes only when missing; do not derive ownership from company names or require reconfirmation of an already supplied list. The operator's list is authoritative.
2. **Fan out.** For ~5 or fewer apexes, call `lookup_tenant(domain, format="json", explain=true)` per apex. For larger sets, `recon batch <file> --json --include-ecosystem` returns the per-domain lookups plus the v1.8 ecosystem hypergraph and cross-domain token clustering in one payload.
3. **Report administrative token overlap without validating the relationship.** `cluster_verification_tokens(domains=[...])` surfaces exact shared TXT token strings. Reuse is compatible with shared administration, copied configuration, managed service, or stale residue. Absence is non-informative because publication is optional; do not call the domains administratively separate.
4. **Synthesize the rollup along these axes:**
   - Identity stack consistency - same M365 tenant across siblings, or distinct tenants per brand?
   - Email gateway consistency - same Proofpoint / Mimecast / Cisco upstream, mixed, or none?
   - Cloud footprint overlap - which providers appear across the set.
   - **Configuration divergence (most interpretable output)** - after checking `degraded_sources`, identify a supplied apex whose observed `email_security_score` count differs materially from the set or whose DMARC policy differs (`p=none` while others publish `p=reject`). Report it as a review candidate, not an overall security ranking; collection gaps and non-public controls can explain the difference.
   - Per-brand notable findings - one line each, only when a brand has something its siblings don't.
5. **Keep the voice hedged.** *"Five domains share a Microsoft 365 tenant"* is observable. *"Acquired in 2024 and still on the same tenant"* is firmographic enrichment - out of scope. Surface per-brand `confidence` honestly; do not average it across the family.

Tracking change over time:

1. `recon delta <domain>` (CLI) compares the current resolution against the cached snapshot at `~/.recon/cache/`. The output is a `DeltaReport` (see `$defs/DeltaReport` in [`docs/recon-schema.json`](https://github.com/pueo-labs/recon/blob/v2.27.1/docs/recon-schema.json)) with explicit `added_*` / `removed_*` / `changed_*` fields. Report the deltas; do not narrate causes.
2. **First-run case.** A domain that has never been resolved on this machine has no baseline. `recon delta` reports "No cached snapshot," asks the operator to run the ordinary lookup first, and exits with code 3 without emitting a delta. Surface that no-baseline state rather than reporting "no changes."

## Picking a profile

Profiles are posture lenses, not scores. They bias category emphasis. Pick based on what the *target* is, not what the user is:

- `fintech` - banks, payment processors, fintech.
- `healthcare` - hospitals, payers, health-tech.
- `saas-b2b` - B2B SaaS vendors.
- `high-value-target` - Fortune 500, defense contractors, large enterprises.
- `public-sector` - `.gov`, municipalities, agencies.
- `higher-ed` - universities, `.edu`.

If unsure, omit the profile. Don't guess from a thin hint. Custom profiles can live in `~/.recon/profiles/*.yaml`; check `recon://profiles` to enumerate.

Invocation:

- CLI: `recon <domain> --profile <name>` (also accepted by `recon <domain> --full --profile <name>`).
- MCP: `analyze_posture(domain, profile="<name>")` - profile is the second argument.

## How to talk about the output

recon's voice is **hedged observation**, not verdict. Mirror that voice when reporting back.

- Say "DMARC policy is `p=none`" or "no DMARC record observed" - not "this domain is vulnerable."
- Say "Microsoft 365 tenant observed; identity is federated" - not "they use Okta" unless the IdP is explicitly named in the output (`google_idp_name` or evidence-backed insight).
- Say "passive observation only - there may be additional controls not visible in DNS" when summarizing posture, especially on sparse results.
- Surface the `confidence` field. `low` confidence with thin sources means "public evidence is sparse for this queried namespace," not that the domain or any organization behind it is suspicious.
- Cite the evidence type when stating a fingerprint - MX, TXT, CNAME, NS, SRV, CAA, SPF, certificate SAN. Don't just assert.
- Never claim a vulnerability is *confirmed*. recon does not test exploitability. A missing DMARC record is a missing record; what it implies is a separate conversation.

When summarizing a `lookup_tenant` response, lead with what carries signal:

1. Tenant identity (`tenant_id`, `provider`, `auth_type`, `region`, `cloud_instance` if non-default).
2. Email configuration (`email_security_score` is a count of publicly observed controls; also report `dmarc_policy`, `mta_sts_mode`, and `email_gateway` when present).
3. Services grouped by category, not as a flat list.
4. Related domains only if the user asked for them.
5. Confidence and any `degraded_sources`.

Don't paste the raw JSON unless asked. Offer it.

## Sparse results

recon will sometimes return very little - a domain behind heavy proxies, with minimal published records, or one that doesn't expose SaaS verification tokens. This is expected. When it happens:

- Report what *was* observed, name the empty fields explicitly, and explain that passive collection has a ceiling for this kind of target.
- Check `degraded_sources` and `partial` - if a source failed transiently, suggest a re-run.
- Don't synthesize confidence that isn't there.

## Cache awareness

Ordinary lookups may reuse a result from the default 24-hour cache. The public
lookup JSON does not expose `resolved_at` or `cached_at`; those timestamps are
internal cache metadata. Do not invent a collection time or describe a normal
lookup as fresh merely because it just returned. When current collection is
requested, use `build_review_bundle(domain)` for a fresh, lookup-cache-bypassed
MCP handoff, or `recon "<validated-domain>" --no-cache` through the CLI. Check
source status and degraded-source notes as well: a fresh lookup attempt does
not guarantee every upstream observation is current or available.

## Ephemeral fingerprints

If the user wants to test a hypothesis about a custom or internal SaaS - "does Synthetic Alpha publish a Synthetic Delta Platform verification token?" - use the ephemeral fingerprint workflow:

1. `inject_ephemeral_fingerprint(name, slug, category, confidence, detections=[...])`.
2. `reevaluate_domain(domain)` - uses cached data, no new network calls.
3. `clear_ephemeral_fingerprints()` when done.

Cache-only re-evaluation supports `txt`, `spf`, `mx`, `ns`, and apex/root
`cname` rules. Owner-qualified `cname_target`, `subdomain_txt`, `caa`, `srv`,
and `dmarc_rua` rules cannot be reconstructed from retained observations. For
one of those types, call `reload_data` to clear the lookup-result cache while
retaining the server process's ephemeral catalog, then run `lookup_tenant` again;
that fresh lookup uses the normal documented network boundary.

Ephemeral fingerprints are process-wide within the current MCP server process,
not conversation-scoped, and are quota-bounded. They disappear when that
server process exits.

## Gotchas

The sharp edges that have actually bitten this workflow. Skim before a session;
the detail for each lives in the section above.

- **`recon delta` on a never-seen domain exits with code 3.** It reports "No cached snapshot" and asks for an ordinary lookup to establish the baseline; it does not emit a delta.
- **A sub-host is analyzed as its apex unless you pass `--exact`.** `mail.delta.invalid` returns facts for `delta.invalid`; the `queried_domain` field tells you what was actually analyzed. Reporting apex tenancy as the sub-host's is wrong.
- **`--full --json` can be large; never dump it inline.** Its size depends on collected certificate-transparency and evidence data. Save it to a file and reply with the 3-line headline. Inline JSON burns context for no benefit.
- **Do not test MCP connectivity by calling a tool.** Inspect the client's actual recon tool names and server identity; a speculative call to "check" is a wasted, confusing round-trip.
- **`--exposure` / `assess_exposure` is cache first and may resolve on a miss.** The index calculation adds no network calls after the ordinary base lookup. Do not imply that the 0-100 value comes from a separate scan or measures overall security.
- **Low confidence means sparse public evidence, not a suspicious domain or organization.** Sparse output marks limited evidence for the queried namespace, not a finding or calibrated uncertainty level. Do not manufacture confidence or insinuation.
- **Do not guess a profile from a thin hint.** A wrong posture lens skews emphasis; omit `--profile` when the target type is unclear.
- **Serve cache honestly.** Public lookup JSON omits internal timestamps. For current collection, use `build_review_bundle` or CLI `--no-cache`, and retain source freshness and failure caveats.

## Hard rules

- recon is **passive in scope**: it does not scan ports, crawl target applications, use credentials, or test exploitability. Default DNS can be visible to authoritative infrastructure, MTA-STS is the one default target-owned HTTP/application request, and the documented CSE / BIMI direct probes require explicit opt-in. Never claim recon confirmed an active service, a running version, or an exploitable vulnerability.
- Fingerprints are **probabilistic**. Detection scores (`low` / `medium` / `high`) reflect evidence corroboration, not ground truth.
- recon does **not require authorization** to query - every endpoint it touches is one anyone can hit with `dig` or a browser. Do not ask the user whether they have authorization to query a domain unless the user's stated intent suggests something other than legitimate research, due diligence, or defensive review.
- Output uses **neutral language**. No takeover hints, maturity verdicts, or offensive guidance. Mirror this in your reply.
