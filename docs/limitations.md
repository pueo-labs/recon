# Known Limitations

recon is public-metadata-only and zero-credential. Its narrow collection
boundary limits target interaction, but it also means there are whole classes
of information the tool cannot see. DNS reads use the configured recursive
resolver, so authoritative DNS infrastructure may observe resulting resolver
traffic. The standard MTA-STS policy fetch is the only default target-owned HTTP
or application request, and opt-in direct probes add the documented CSE and
BIMI certificate requests. This document is the honest inventory, not a legal
opinion or a claim of invisibility.

If any of these matter for your use case, either pipe recon's output into a
complementary tool (active scanner, authenticated API consumer) or accept the
gap as a known unknown.

> **Surfaced in the panel (v1.9.9+).** When a default lookup returns a sparse
> classified surface alongside a multi-domain tenant-discovery response, the
> panel adds a compact "Passive-DNS ceiling" footer naming categories that
> public DNS cannot reach. The trigger does not estimate organization size.
> This page is the long-form inventory; the panel footer is the at-a-glance cue.

---

## What recon cannot see

### Bundled platform services with no DNS footprint

- **Microsoft Copilot, Microsoft Teams Phone, Microsoft Purview**: a public
  M365 tenant observation does not establish licensing, enablement, deployment,
  or use of these child products.
- **Google Gemini, Google Vault, Context-Aware Access**: a Google Workspace
  observation likewise does not establish child-product use.
- **Most GitHub features**: private repos, actions, code scanning have no
  public DNS footprint even when the org is detectable elsewhere.

### Heavily proxied or zero-DNS domains

- **Cloudflare Email Routing**: MX points to Cloudflare, the backend mailbox
  provider is invisible.
- **Email security gateways**: when MX is Proofpoint / Mimecast / Trend
  Micro / Symantec, the actual email platform behind the gateway is only
  visible when DKIM or other public records leak it.
- **Cloud-hosted landing pages**: when the apex is one A record pointing to a
  shared CDN and no SaaS verification tokens are published, the landing-page
  application or backend may remain unattributed. recon can still observe any
  available NS, CT, identity-discovery, and bounded subdomain evidence.

See [correlation.md](correlation.md) for the graph, temporal, and Bayesian
layers shipped across v1.7-v1.9 and stabilized in v2.0. Wildcard SAN siblings,
CT issuance bursts, and chain motifs describe structure that one record cannot,
but their incremental operator value over simple evidence plus abstention has
not yet passed the predeclared product benchmark.

### Internal-only services

By default recon does not probe hosts, ports, login pages, or application
endpoints on the target's own infrastructure. The exceptions are narrow and
documented: it may fetch the standards-compliant MTA-STS policy at
`mta-sts.<domain>`, and the CSE / BIMI VMC direct probes run only when
`--direct-probes` is explicitly enabled.

- **Private SSO** (on-prem ADFS without public autodiscover, internal CAS,
  self-hosted Authelia / Keycloak not exposed via public DNS)
- **Internal SaaS** (company-internal Jira / Confluence behind VPN with no
  public CNAME)
- **Corporate file shares, intranet portals, internal ticketing**: all
  zero public DNS footprint by design.

### Regional and domestic SaaS ecosystems

- **Domestic provider stacks**: some APAC and China-focused organizations use
  domestic mail, collaboration, cloud, and identity providers whose public DNS
  patterns are not as well represented in the built-in catalog.
- **Localized verification schemes**: regional SaaS products may publish TXT
  or CNAME proofs that are stable but not yet fingerprinted.

When this happens, recon may show a low-signal or unclassified result even
though a rich domestic stack exists behind the scenes. Treat those results as
coverage gaps unless the public evidence directly supports a stronger claim;
do not infer that the stack is self-hosted.

### Network-level and host-level facts

- **Open ports, running services, OS versions**: these are active-scanning
  outputs. recon does not port-scan.
- **Web server software versions**: these come from generic HTTP responses, not
  DNS. recon does not request those pages; its only target-owned HTTP fetches are
  the documented MTA-STS policy request and opt-in CSE / BIMI VMC probes.
- **TLS certificate chain details beyond CT metadata**: recon sees what CT
  logs contain (issuer, not_before/not_after, subject). For live certificate
  detail, use `openssl s_client` or an active TLS scanner.
- **IP-level infrastructure, ASN, BGP paths**: recon has no ASN / GeoIP /
  BGP datasets (see roadmap invariants).

---

## Where recon must remain conservative

These are cases where the evidence does not justify a stronger claim. Some are
deliberate abstentions.

### Tenant cardinality and public vendor indicators

**Current behavior:** A Microsoft tenant-domain response is reported as a
tenant-discovery count, not as organization size. Intune, Office ProPlus, Jamf,
Kandji, and security-vendor fingerprints remain public vendor indicators. They
do not establish a license tier, device enrollment, operating-system mix,
fleet composition, active security stack, or SASE / ZTNA deployment.

Email-gateway prose requires an MX-backed `email_gateway` observation. A
generic vendor slug does not establish mail routing, and a gateway MX record
does not by itself identify the downstream mailbox provider or establish DKIM.

**Why conservative:** Tenant cardinality is namespace metadata, while DNS and
administrative records can persist after trials, migrations, or
decommissioning. Those public observations do not expose contracts, endpoint
inventory, control-plane state, or live traffic.

### Bundled AI services

**Current behavior:** Microsoft 365 and Google Workspace observations do not
produce Microsoft Copilot or Google Gemini labels. A child product appears only
when recon has a direct fingerprint for that product. Public DNS and tenant
metadata do not establish a child product's license, enablement, deployment, or
use.

### Dual-provider organizations

**Current:** A domain with M365 tenant + MX through a Trend Micro gateway and
M365 DKIM reads as "Trend Micro gateway + Microsoft 365 (likely downstream)" on
the default view, and as "Trend Micro gateway (MX delivery path) + Microsoft 365
(possible downstream indicator)" under `--explain` / `--full` and in the JSON
record ([ADR-0012](adr/0012-default-view-evidence-role-visibility.md)). The
ordering does not assert priority. If M365
is the only detected slug and Google Workspace fires only from a TXT token
(no DKIM, no MX), Google Workspace remains an account signal and does not enter
the provider line. Use `--full` or structured output when account-only
detections matter.

**Why underclaimed:** An M365 tenant with a dormant Google Workspace
registration is wildly common and doesn't mean active dual-platform email.
Showing both on every lookup was noise.

### Sovereignty when OIDC metadata is absent

**Current:** Government cloud (GCC, GCC High, DoD) detection depends on the
Microsoft OIDC discovery endpoint returning `cloud_instance` and
`tenant_region_sub_scope`. When those fields are absent, recon preserves them
as unknown and emits no sovereignty conclusion.

**Why unresolved:** absent metadata cannot distinguish a commercial tenant from
suppressed or unavailable sovereignty metadata. This unknown-state behavior is
an invariant to preserve, not evidence of a commercial cloud.

### Federated IdP vendor identification

**Current:** A federated UserRealm result is reported as `Federated identity
observed; external IdP not identified` unless separate public fingerprints name
identity vendors. When those fingerprints exist, recon labels them as vendor
indicators rather than claiming that one operates the external IdP.

**Why conservative:** The federation state is observable; a DNS verification
marker or related vendor fingerprint does not establish the live federation
route or its operator.

---

## Calibration and the validation ceiling

The fusion point estimates are exact for one manually encoded, partly
development-corpus-informed Bayesian network,
not demonstrated real-world probabilities. `interval_low` and `interval_high`
form a post-inference, evidence-responsive uncertainty band. Its auxiliary Beta
distribution has the point estimate as its mean, and the emitted band is
required to contain that estimate, but equal-tail Beta quantiles are generally
asymmetric and are not centered on the mean. The band does not integrate CPT,
likelihood, dependence, or missingness uncertainty and is not a Bayesian
credible interval or frequentist confidence interval. Its width is not
generally monotone in added evidence because both the point estimate and
effective mass can change.

What is validated, what remains model-internal, and the predeclared independent
label ablation are in [correlation.md](correlation.md). The current synthetic
experiments and real-corpus consistency checks validate inference plumbing and
selected assumptions. They do not validate the CPT values. Brier or log score
is proper-score evidence only for an arm that supplies one frozen probability
forecast for every eligible row. An arbitrary evidence-strength score first
needs a development-disjoint fitted probability mapping. Otherwise report only
descriptive score diagnostics. Do not interpret a probability band as
containing a binary truth value.

---

## Known noise patterns

Times recon has been wrong in empirically verified ways:

- **crt.sh returning stale certs.** Cached certs for decommissioned subdomains
  can inflate the related-domain count. The per-domain CT cache bounds repeat
  exposure to flaky providers, but a single CT query can surface certs from
  years ago.
- **CertSpotter rate limits.** When crt.sh is down, CertSpotter is the
  fallback, but it rate-limits aggressively on larger domains. recon handles
  429 responses by returning partial data (documented in degraded-sources
  note) rather than crashing.
- **CT search is not complete inventory.** Public CT search APIs are indexed
  views over append-only logs and can be rate-limited, stale, partial, or
  missing an entry that another monitor sees. Treat CT evidence as passive
  certificate telemetry, not as an authoritative asset list.
- **A lookup is not an atomic snapshot.** DNS, CT, identity providers, and the
  MTA-STS policy can be read at different times and through different vantage
  points. Cross-source agreement can therefore mix current, historical, cached,
  and non-simultaneous observations.
- **Administrative tokens can be copied or stale.** Exact site-verification
  token reuse is observable, but it does not establish a shared account,
  operator, owner, or current product use. Copied configuration, managed
  service, and historical residue remain compatible explanations.
- **DNS answers can vary by vantage.** Split-horizon policy, geolocation,
  resolver cache state, DNSSEC validation behavior, and transient delegation
  conditions can make two clean lookups differ. recon currently records source
  degradation but does not yet serialize a complete resolver-vantage capsule.
- **DKIM selector blind spots.** recon probes common selectors such as `s1`,
  `s2`, `dkim`, `mail`, `k1`, `k2`, and `default`. Services using
  non-standard or per-account selectors (for example some Mailchimp, SendGrid,
  Salesforce Marketing Cloud, and regional providers) can still produce "No
  DKIM observed" false negatives.
- **Email declarations are not operational validation.** BIMI and TLS-RPT
  observations require one eligible record with valid declaration syntax.
  Conflicting records and BIMI's explicit opt-out do not create a positive
  control. This follows [RFC 8460 section 3](https://www.rfc-editor.org/rfc/rfc8460.html#section-3)
  and the [BIMI draft -14](https://datatracker.ietf.org/doc/html/draft-brand-indicators-for-message-identification-14),
  which remains an Internet-Draft. recon does not validate BIMI logo contents,
  message authentication or recipient display behavior, follow local-part
  selectors, or test TLS report delivery and receiver scheme support. Ordinary
  lookups can retain older cached observations until expiry; use `--no-cache`
  when checking current declaration admission.
- **Domain homograph / Punycode.** recon IDNA-encodes Unicode input and enforces
  a round-trip guard before analysis. This validation reduces ambiguous input;
  it does not make a Unicode display name safe from visual confusables or
  guarantee that it matches what a browser renders.
- **Wildcard DNS.** A domain with a catch-all wildcard A record at `*.domain`
  makes subdomain probing return a hit for every prefix, including ones that
  aren't actually distinct services. recon filters wildcard CT results but
  cannot fully neutralize wildcard A.

### Resolvers that answer names that should not exist

By default the CLI uses the system resolver. Some resolvers answer names that do not
exist: captive portals, filtering or content-blocking resolvers, and ISP
resolvers that rewrite NXDOMAIN into an advertising or search address. Behind
one of them, related-domain probing receives an answer for every candidate, so
artifact hosts can be listed as related domains and a nonexistent name can look
like it exists. An individual candidate answer cannot establish whether it was
synthesized. When an existing lookup request finds a fixed public identity or
certificate-transparency endpoint at a private or reserved address, the panel
warns that related domains may be artifacts. JSON records the condition as
`resolver:public_endpoint_private_address` in `degraded_sources`. This uses
the existing destination check without sending another probe.

`recon doctor` checks for the condition with one query for a random name under
the reserved `.invalid` top-level domain, where no name can exist
([RFC 6761 section 6.4](https://www.rfc-editor.org/rfc/rfc6761.html#section-6.4)).
Any answer other than NXDOMAIN is reported as
`warn  Nonexistent-name probe: Resolver answers names that should not exist`.
When it appears, treat related-domain results as unreliable and rerun the
lookup through a resolver that returns NXDOMAIN for nonexistent names. A
resolver that rewrites only some names can pass this check, so a clean probe
does not prove every answer is genuine.

---

## When to reach for something else

| If you need… | Use instead |
|---|---|
| Live port/service enumeration | `nmap`, `masscan`, Project Discovery's `naabu` |
| Vulnerability assessment | Nessus, OpenVAS, `nuclei` |
| Authenticated Microsoft 365 enumeration | ROADtools, AADInternals (requires credentials) |
| Continuous monitoring / alerting | Commercial ASM (Bit Discovery, RiskIQ, CyCognito, Randori) |
| Phishing-level OSINT | Maltego, SpiderFoot, Amass |
| Certificate chain deep-dive | `openssl s_client`, `testssl.sh` |
| Subdomain takeover scanning | `subjack`, `nuclei` takeover templates (requires HTTP probing) |
| IP / ASN intelligence | ipinfo.io, Shodan, Censys (requires API keys) |
| Historical DNS | SecurityTrails, PassiveTotal, DomainTools (requires API keys) |

recon is deliberately a narrow tool. If you are doing any of the above, use
the right tool for the job, or pipe recon's `--json` output into it as a
starting point.

---

## Signal coverage and false positives

The fingerprint database is rule-based. A fingerprint match means "evidence
fits this service's DNS signature", not "this service is in use".
Confident-looking output can still be wrong.

Best practices:

- Treat outputs marked **Confidence: Low** or supported by only one qualifying
  source as investigation leads, not conclusions. Under the current merged
  confidence rule, a one-source result cannot receive the overall High tier.
- `--explain` shows flat retained-evidence explanations with an explicit
  `exact`, `exact_rule_only`, `reconstructed`, or `unsupported` lineage label.
  `--json --explain` additionally emits `explanation_dag`. Use
  `exact_provenance_complete` and `lineage_disconnected_terminals` when an exact
  evidence-to-rule path matters.
- Built-in generated insights retain exact generation-time associations.
  Confidence, legacy insight, and proxy-matched posture associations can still
  be reconstructed. Schema-version-1 `provenance_complete=true` establishes
  reachability in the emitted graph, not exact generation-time lineage for
  every terminal.
- `inference_confidence` describes the strongest error-free, same-claim
  corroboration chain. Evidence from failed sources or unrelated provider and
  service claims is not pooled. `--explain` identifies the winning claim and
  its qualifying record types, source names, and evidence.
- `--confidence-mode strict` or `--strict` only drops hedging when ≥3 sources corroborate
  AND confidence is High. Sparse-data output stays hedged by design.
- If you spot a false positive, do not put a real domain or its output in a
  public issue or pull request. Use a fictionalized minimal reproduction, or
  report a load-bearing real-domain case through the private path in
  [SECURITY.md](../SECURITY.md). Fingerprint pull requests are welcome when
  their fixtures follow [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## Release & maintenance caveats

- **Solo maintainer.** The fingerprint database, signals, and profiles are
  maintained by one person. Fingerprint and signal PRs are the path to sharing
  that load; until then, coverage is constrained by one person's attention.
- **Upstream flakiness.** crt.sh, CertSpotter, and Microsoft / Google
  identity endpoints are not operated by the recon project. Outages
  propagate directly to recon output (documented via `degraded_sources`).
- **Point-in-time lookups.** recon reports a bounded observation window, or a
  recently cached result. `recon delta <domain>` is the supported run-over-run
  output diff. It suppresses additions when the previous endpoint was degraded,
  removals when the current endpoint was degraded, and dependent scalar changes
  unless both required observation opportunities existed. It cannot yet
  separate public-fact changes from catalog, model, version, normalizer,
  evaluation-time, option, cache, or vantage changes. Continuous monitoring
  needs a separate retention contract.
