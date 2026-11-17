# Catalog Growth and Quality Strategy

Status: measurement-first maintenance plan
Review date: 2026-09-05 UTC

This document is the plan for growing and maintaining the fingerprint catalog
(`src/recon_tool/data/fingerprints/*.yaml`) so coverage, precision, and
freshness improve deliberately rather than by accretion. It sets direction; it
does not change runtime behavior. All corpora and per-domain scan outputs stay
private and off GitHub per [data-handling-policy.md](data-handling-policy.md).
New review artifacts use aggregate patterns, generic tooling, and explicit
synthetic examples under reserved namespaces. The release gate rejects the
retired fictional target vocabulary across current public text artifacts.
Real vendor and product names, plus provider-controlled domains used in generic
fingerprint rules, may be committed. The evaluated target names, target-owned
records, and per-domain results may not.
This plan implements the catalog-quality track in the canonical
[roadmap](roadmap.md). Catalog size is not a success metric; classified public
surface and independently supported precision are.

The [maintainer workflow](catalog-maintenance.md) turns this strategy into
corpus-planning, collection/evaluation, and rule-triage skills using the existing
harnesses. It also records evaluator limits and research-backed sampling
caveats. No evaluation holdout becomes a development queue.

## How the catalog grows today

The catalog carries 873 entries and 1,123 detection rules across nine populated
types: `cname_target`, `cname`, `txt`, `spf`, `dmarc_rua`, `mx`, `ns`, `caa`,
and `subdomain_txt`. The grammar and runtime also support `srv`, but the built-in
catalog currently has no `srv` rules. New rules come from a corpus-mining loop:

1. A private domain corpus is run through `recon batch --include-unclassified`
   (`validation/scan.py` or `validation/run_corpus.py`), with output written to
   gitignored private directories (`validation/runs-private/`, `live_runs/`).
2. `validation/find_gaps.py` retains the established CNAME-chain queue, while
   `validation/catalog_baseline.py` separately aggregates every bounded catalog
   path, ranks private recurrence buckets, and emits a target-free count report.
3. `validation/triage_candidates.py` drops already-covered and
   intra-organizational suffixes and applies both occurrence and distinct-
   namespace floors.
4. Each surviving candidate is verified against public vendor documentation and
   promoted with a scoped pattern, a `reference`, a category mapping, a
   regression test, and hedged wording.

The loop is disciplined and effective, but the available corpus remains a
convenience sample with selection bias. The first frozen typed baseline is
recorded in
[the 2026-07-17 aggregate memo](../validation/2026-07-17-typed-catalog-baseline.md);
the independent rank, regional, and vendor-seed rounds are complete. The
vendor-seed result records 29 corroborated and 4 observed-silent HubSpot rows,
no unavailable, unmeasured, or error outcome, and no catalog promotion from the
evaluation holdout. The final 5,199-row prior-sample drift round is also
complete. Its [aggregate result](../validation/2026-08-14-catalog-drift-round.md)
reports complete measurement, no decline beyond the frozen review threshold,
no catalog promotion, and the exact catalog-driven `subdomain_txt`
measurement-surface change. Most legacy detections still lack a freshness
date: 293 of 1,123 detections carry a `verified` date (26.1 percent)
after the 2026-11-17 survey-include check.
That share is the dated floor, not a reason to stamp today's date on the
undated backlog.

Current round status:

| Round | Status |
|---|---|
| Convenience-sample baseline | Complete, aggregate-only memo published |
| Unseen vertical holdout | Complete, 366 normalized namespaces, no post-holdout tuning |
| Rank bands | Complete; four-band aggregate, dispositions, and zero-regression decision published |
| Regional / ccTLD | Complete; baseline, fixed-observation decision, and clean-main replay published |
| Vendor seed | Complete; 33-row HubSpot result published with 29 corroborated, 4 observed-silent, no error or unmeasured outcome, and no rule promotion |
| Drift | Complete; 5,199 rows measured, aggregate result published, measurement-surface change disclosed, no threshold breach or rule promotion |

## 1. A stratified, reproducible sampling frame

The catalog can only recognize vendors the corpus exposes, so one list biases
the catalog toward that list's population. Replace the single corpus with
purpose-built strata, each curated and stored privately:

- **Rank-stratified backbone.** Use Tranco (a research-grade, manipulation-
  resistant top-sites list) in rank bands (1-1k, 1k-10k, 10k-100k, 100k-1M).
  Head and tail run different stacks, and Tranco is reproducible and citable for
  the write-up.
- **Vertical lists.** Fintech, healthcare, public sector, higher education,
  retail, legal, media. Each vertical has its own vendor ecosystem. Many source
  directories are public (the `.gov` zone, accreditation registries, regulator
  member lists).
- **Regional / ccTLD lists.** The current catalog skews toward US and English
  vendors; this is the largest blind spot. The first round groups only exact
  ASCII two-letter IANA country-code TLDs through their matching UN M49
  ISO-alpha2 entries in the five canonical M49 regions, then samples equal
  discovery quotas from several ccTLDs per region. Archive and digest both raw
  official pages before deriving the mapping; count and exclude regionless M49
  entries explicitly. A ccTLD is a namespace attribute, not evidence of
  registrant location, organizational presence, or service geography.
  Globally marketed ccTLDs remain in their delegated grouping, so the result is
  descriptive for the frozen namespace frame and is not a regional prevalence
  estimate.
- **Vendor-seed lists (reverse direction).** For a target vendor, archive
  provider-controlled customer evidence, observe a development-disjoint
  holdout, and measure independent relationship corroboration. Search-result
  and "powered by" discovery can suggest private development rows, but cannot
  label the holdout.
- **TLD-scale mining.** ICANN CZDS zone files are free and give every domain in
  a TLD for aggregate pattern mining. Mine patterns only; never persist
  per-domain data (the no-aggregate-database invariant).

"More rounds" should mean more diverse lists, not re-scanning the same corpus,
which mostly re-finds known vendors.

### Round protocol

A round evaluates domain query coordinates, not websites. It does not crawl
pages or infer the company behind an apex. Each round has one predeclared
sampling purpose and a private, frozen input manifest:

| Round | Private input stratum | Primary question |
|---|---|---|
| 0. Baseline | Deduplicated current corpus | What is measured, unmeasured, classified, and unresolved at the current catalog revision? |
| 1. Rank bands | Independent samples from several popularity bands | Do head and tail namespaces expose different high-frequency gaps? |
| 2. Region | Country-code and regional samples | Which provider patterns are missing outside the current geographic concentration? |
| 3. Vertical | Separately sampled public-sector, education, finance, healthcare, retail, legal, and media sets | Which gaps recur within a domain class without being pooled into a population claim? |
| 4. Vendor seed | Provider-controlled customer evidence disjoint from development and earlier observation rows | How often does the frozen provider slug independently corroborate the relationship label on measurable rows? |
| 5. Drift | A frozen prior sample observed again later | Which rules or public record shapes changed, appeared, or disappeared? |

Before collection, normalize each input through the same apex reducer used by
the product, reject malformed rows, and deduplicate within the round. When
reporting a pooled descriptive count across overlapping strata, count each apex
once. Keep stratum membership, source list revisions, and every domain row only
in the ignored private workspace. A corpus used to develop a rule cannot also
serve as its independent precision or provider-relationship corroboration
holdout.

Every round records the catalog digest, collection options, source-success
counts, observation-opportunity counts, unresolved counts, and gap counts by
record type. Re-run the frozen round after a candidate patch and report only
aggregate before-and-after deltas. Do not publish a target sample to explain a
rule. The rule itself, a provider-controlled public reference, reserved
synthetic fixtures, and aggregate counts are sufficient for review.

Stop adding inputs when a round does not answer a new sampling question. Stop a
promotion pass when the highest-frequency survivors lack an independent public
basis, fail a lookalike negative, or exceed the predeclared precision regression
budget. Two scans of the same list are a drift check, not two coverage rounds.

The first rank-round selection and completed observation pass are recorded in
the [catalog rank-round declaration](catalog-rank-round-declaration.md). Its
four equal discovery quotas are not population weights. The membership-bound
stratified aggregate, candidate dispositions, and fixed-observation
zero-regression decision are published in the aggregate-only
[rank-round result](../validation/2026-08-13-catalog-rank-round.md). The official
source mapping and independent five-stratum frame are frozen in the
[regional declaration](catalog-regional-round-declaration.md). The
aggregate-only
[result](../validation/2026-08-13-catalog-regional-round.md) records the
complete baseline, accepted fixed-observation decision, and clean protected-main
replay. The rank result does not substitute for it.

## 2. Measurement: coverage, relationship corroboration, precision

Growth without measurement cannot tell 40% coverage from 90%. Three metrics
close the loop:

- **Coverage / unclassified rate.** `find_gaps.py` retains the historical
  frequency-ranked CNAME-terminal list. The opt-in discovery envelope now also
  emits typed, bounded accounting for every direct catalog path, and
  `catalog_baseline.py` writes separate private recurrence queues plus one
  aggregate-only report. Track "share of observed DNS surface classified" by
  type. TXT tokens, mail routes, issuers, and hostnames are never forced into
  one suffix metric.
- **Provider-relationship corroboration, via vendor-seed lists.** On a
  provider-controlled customer holdout, how often does recon independently
  observe that provider's frozen slug when an eligible catalog path is
  measurable? Report this separately by provider with unavailable, unmeasured,
  and error counts. A customer relationship does not guarantee publication of
  a specific DNS record, so silence is not a false negative and the measure is
  not recall. The frozen protocol is in the
  [vendor-seed declaration](catalog-vendor-seed-round-declaration.md).
- **Precision, only with independent labels.** Measure false attribution only
  where a provider-owned endpoint, standards-defined record, or other
  predeclared authoritative source supplies a label that the matcher did not
  consume. Apply the product-quality plan's minimum sample and uncertainty
  rule; otherwise report no precision estimate.
- **Corroboration diagnostic.** Signal disagreement and single-signal matches
  are useful review queues, but they are not false-positive denominators or
  independent correctness labels.

All measurement outputs are aggregate and disclosure-controlled; no apexes,
organization names, or per-domain rows leave the maintainer machine.

The first dated record-type baseline reports availability, observed and
unclassified values, partial collection, truncation, and the exact catalog
revision. Later strata must retain that accounting and add the unresolved,
freshness, and corroboration measures relevant to their question. Every
promotion should name the aggregate gap it is intended to reduce and a
precision regression budget.

The record-type accounting target is:

| Catalog type | Bounded observation surface | Current corpus-wide gap queue |
|---|---|---|
| `cname_target` | Related-subdomain CNAME chains found by bounded probes or CT | Implemented and frequency-ranked |
| `cname` | Apex and `www` CNAME targets | Typed accounting and private recurrence queue implemented |
| `txt` | Non-SPF apex TXT values | Typed accounting and private prefix or exact-repeat queue implemented |
| `spf` | Apex SPF include and redirect targets | Typed accounting and private hostname queue implemented |
| `mx` | Apex MX routing hosts | Typed accounting and private hostname queue implemented |
| `ns` | Apex NS hosts | Typed accounting and private hostname queue implemented |
| `caa` | Apex CAA issuer values | Typed accounting and private issuer queue implemented |
| `dmarc_rua` | Valid aggregate-report destination domains | Typed accounting and private hostname queue implemented |
| `subdomain_txt` | TXT owners explicitly named by catalog rules | Typed accounting implemented; unknown owner names remain non-enumerable and outside the denominator |
| `srv` | The bounded common SRV owner list queried by recon | Typed accounting implemented; the built-in catalog still has no `srv` rules |

An empty queue means no recurrent candidate crossed the frozen thresholds, not
that the catalog is complete. "All records" means all bounded observation
opportunities recon actually attempted.
It cannot mean every record in a DNS zone: unknown TXT owners, DKIM selectors,
and SRV owner names are not generally enumerable through passive DNS queries.

## 3. Freshness

Vendors change domains, get acquired, and sunset products, so a rule with no
re-check is a slow source of false positives and negatives. Each detection now
supports an optional `verified` date (`YYYY-MM-DD`) recording when its pattern
was last confirmed against a public source or corpus observation. It is advisory
and does not affect matching.

Run the no-network auditor:

```bash
python -m validation.audit_fingerprints --freshness
```

It defaults to the canonical built-in catalog and reports verified-date
coverage and detections older than a staleness threshold. As of 2026-09-05 the
catalog had 162 dated detections of 1,109 (14.6 percent), after the
[claim and retirement review](../validation/2026-09-05-catalog-claim-review.md)
and the [documented CNAME round](../validation/2026-09-05-documented-cname-review.md).
As of 2026-09-08 it has 166 dated detections of 1,113 (14.9 percent) after
adding documented Tailscale, PostHog, and Resend rules
([review](../validation/2026-09-08-documented-fingerprint-review.md)).
An explicit `--effective-catalog` audit includes local additions and is not a
canonical baseline. The diff-aware `scripts/check_fingerprint_freshness.py`
gate permits the legacy undated backlog but requires every new detection to
carry a valid, non-future `verified` date. Backfill only independently reviewed
families, and only after the vendor's current public page still names the
pattern. The first named pass is the mail-routing and identity families that
already have claim-contract, quality-baseline, or regional-round review:
Microsoft 365, Google Workspace, Cloudflare, Okta, and Proofpoint. The 2026-08-19
MX pass dated Google Workspace and Microsoft 365. Cloudflare Email Service was
already dated. The later 2026-08-19 Okta pass dated the custom-domain family
from current developer and allowlist pages. The 2026-08-20 Mimecast pass dated
inbound MX and `_netblocks` SPF from current support articles. The later
2026-08-20 pass dated current TrendAI regional MX and SPF values, Barracuda
inbound MX, Cisco Cloud Gateway `iphmx.com`, all 22 current AWS SES
email-receiving regions, and current AWS SES, Google Workspace, and Microsoft
365 SPF values. Current `akamaiedge.net`, `akamaized.net`, `edgekey.net`, and
`edgesuite.net` CNAME rules are dated from Akamai's Property Manager guide.
Proofpoint stays
in the queue: current public product pages do not name `pphosted.com` /
`ppe-hosted.com` MX or SPF hosts, and the Essentials connection-details article
is login-walled. Once coverage is high enough, raise the gate to reject dates
older than the chosen threshold. A dead-reference URL check remains an opt-in
local tool, not a CI gate, because the committed gates run at zero network and
zero paid-API cost.

A freshness pass can change wording without adding a rule. The 2026-08-18
vendor-doc check found two of those cases, both already matched, and the
2026-08-19 pass closed the remaining wording and dates:

- Google's current MX setup page (updated 2026-08-14) names `smtp.google.com`
  as the default and labels the `aspmx.*` series as the still-supported
  pre-2023 form. The catalog already matched both (the current host lives as a
  same-slug EXTEND). The family now calls `aspmx.*` the documented pre-2023
  series, points `reference` at the current page, and dates both detections.
- Microsoft's current Learn DNS-records page still names
  `*.mail.protection.outlook.com`. New accepted domains can also be provisioned
  under `mx.microsoft`, which the catalog already matches as an EXTEND. Both
  hosts are dated from their respective public bases. The older host is not
  retired, and the newer one is not promoted as the only current form.

Neither finding is a missing-pattern promotion. Both are why the freshness
loop exists: the vendor page moved, and the family prose has to move with it.

The same loop also retires dead references and corrects directionality. The
2026-08-19 Okta pass found
that `help.okta.com` custom-url-domain and preview-orgs articles 404, and
that `okta.com/okta-for-government/` 404s. The live bases are the developer
custom-domain guide (`_oktaverification`, `okta.com`, `oktapreview.com`,
`okta-dnssec.com`) and the IP-allowlist article (`*.okta-gov.com`). The
current guide does not name `okta-domain-verification`, so that prefix
stays undated. The 2026-08-20 Mimecast pass replaced generic product-page
and `community.mimecast.com/` roots with current support articles that name
`us-smtp-inbound-1.mimecast.com`, `za-smtp-inbound-1.mimecast.co.za`, and
`include:_netblocks.mimecast.com`. The `^mimecast` TXT prefix is not named
on the current domain-validation article and stays undated. Proofpoint is
the remaining named queue family: public product pages do not name gateway
MX/SPF hosts, and the Essentials connection-details article is login-walled,
so those detections stay undated. TrendAI documentation names current regional
MX and site-specific SPF values while retaining the older shared US SPF value;
the catalog now represents that distinction and adds the documented regional
SPF suffixes. Barracuda's current Email Gateway Defense page still names
`ess.barracudanetworks.com` for inbound MX. Cisco's current hostname page names
`iphmx.com` for Cloud Gateway allocations, so `iphmx.com` is current and
`ess.cisco.com` remains an undated earlier observation rather than the current
default.

AWS's current General Reference names 22 SES email-receiving endpoints. The
catalog previously carried six; the 2026-08-20 pass dates those six and adds the
other 16 with exact regional suffixes. The same pass dates
`include:amazonses.com` from the custom MAIL FROM guide,
`include:_spf.google.com` from Google Workspace Admin Help, and
`include:spf.protection.outlook.com` from Microsoft Learn. The earlier observed
`amazonses:` TXT value remains undated because current AWS identity guidance
does not name that apex value form.

Akamai's current Property Manager guide names `edgesuite.net` for Standard TLS,
`edgekey.net` for Enhanced TLS, `akamaized.net` for shared certificates, and
shows the subsequent `akamaiedge.net` chain. Those exact CNAME and
`cname_target` rules are dated. The broader Edge DNS NS rules,
`akamaiedge-staging.net`, and `akadns.net` remain undated until a current public
page names each exact pattern and role.

The bounded HubSpot review uses its closed v2.14 vendor-seed context and dates
only three rules named by current first-party pages: the account-qualified
`hubspotemail.net` SPF suffix plus the `hubspot.net` CNAME and discovered-target
forms. Its other seven TXT and CNAME-target patterns remain undated because the
reviewed current pages do not name their exact pattern and role.

The bounded Marketo review dates `include:mktomail.com`, the CNAME and
discovered-target forms of `[MunchkinID].mktoweb.com`, and the exact
`mkto-[letter][four digits].com` tracking-link form. The last rule replaces the
broader `mkto-` fragment and uses the shared validated-regex path in runtime and
discovery matching. Five other Marketo patterns remain undated because current
Adobe pages do not name their exact pattern and role.

The bounded Salesforce Marketing Cloud review dates eight CNAME and
discovered-target rules. Current first-party pages name `exacttarget.com`
application hosts, `sfmc-content.com` CloudPages and Content Builder assets,
`sfmc-marketing.com` web-view URLs, `marketingcloudapis.com` tenant-specific API
endpoints, and `exct.net` Subscription Center link tracking. The
`exacttarget.com` SPF and `SFMC-` TXT observations remain undated because the
reviewed pages do not support those exact DNS roles.

The AWS load-balancer correction replaces seven undated, partial regional
`aws-nlb` CNAME-target rules with one dated validated regex for the current
ELBv2 form across commercial, GovCloud, and China partitions. The stable slug
is retained for compatibility, while the display name and description now say
that the shared DNS form cannot distinguish Application from Network Load
Balancers. Fictional partition positives, a Classic ELB negative boundary, and
deceptive suffix lookalikes are blocking tests.

The AWS API Gateway correction replaces five undated, partial regional rules
with one dated validated regex for documented regional targets across
commercial, GovCloud, and China partitions. Tests keep edge-optimized
CloudFront targets, private VPC endpoint names, the bare regional service
endpoint, and deceptive suffix lookalikes outside the API Gateway claim.

The Microsoft residual pass corrects service and role boundaries before adding
dates. Microsoft 365 retains the current `MS=ms########` tenant-domain token;
`ms-domain-verification=` moves to a distinct Azure Communication Services
Email fingerprint because that is the exact service named by current Microsoft
documentation. The broad `outlook.com` CNAME target narrows to
`autodiscover.outlook.com`, GCC High MX narrows from `office365.us` to
`mail.protection.office365.us`, and supported GCC High SPF,
`usgovcloud.microsoft`, and SharePoint roles are dated from current first-party
pages.

The follow-up Microsoft residual review closes the named queue without stamping
the family as a unit. Current Microsoft 365 endpoint guidance supports bounded
`tm-3.office.com`, `svc.cloud.microsoft`, and `svc.sovcloud.cn` routing
observations. Current Exchange guidance supports narrowing `eo.outlook.com` to
the documented legacy `mail.eo.outlook.com` MX family. Those four rules gain
review dates and explicit abstentions from
workload, tenant, activity, location, subscription, recommended-state, and DANE
inferences as applicable. `msv1.invalid` remains undated because no current
first-party product page documents its exact role; the old migration-state
claim is removed and the rule now describes non-routable verification residue
only. Proofpoint remains blocked for the same evidence reason. The detailed
source and disposition matrix is
[the 2026-08-20 Microsoft residual review](../validation/2026-08-20-microsoft-residual-review.md).

The 2026-08-21 Statuspage review replaces a dead shared reference and checks
all seven cataloged rules against Atlassian's current DNS and custom-domain
guidance. The exact `status-page-domain-verification=` custom-email TXT,
`stspg-customer.com` SPF include, and `<PAGE_CODE>.stspg-customer.com`
CNAME-target family gain review dates and role-specific boundaries. The
no-hyphen TXT variant, `statuspage.io` CNAME forms, and `statuspageio.com`
CNAME-target form remain undated because current first-party pages do not name
those exact DNS roles. Detail:
[the 2026-08-21 Statuspage fingerprint review](../validation/2026-08-21-statuspage-fingerprint-review.md).

The follow-up 2026-08-21 Zendesk review replaces another unusable shared
reference and checks all six cataloged rules against current Zendesk email and
host-mapping guidance. The TXT observation moves from an unsupported apex
`zendeskverification=` value to the documented
`zendeskverification.<domain>` owner-qualified form. That rule, the exact
`mail.zendesk.com` SPF include, and both `zendesk.com` CNAME roles gain review
dates and explicit claim boundaries. The apex
`zendesk-domain-verification=` value and broad `zendesk.com` SPF family remain
undated because current first-party pages do not name those exact roles.
Detail:
[the 2026-08-21 Zendesk fingerprint review](../validation/2026-08-21-zendesk-fingerprint-review.md).

The next 2026-08-21 Tencent EdgeOne review checks all five undated
`eo.dnse*.com` CNAME-target rules. Current first-party API examples exactly
support shards 0, 2, 3, and 5, so the review adds the missing shard 0 rule and
dates those four forms. Shards 1 and 4 remain undated because no current page
reviewed in the pass names those exact forms. The family now reports an
observed routing relationship without inferring traffic, enabled CDN or WAF
features, or current configuration state. Detail:
[the 2026-08-21 Tencent EdgeOne fingerprint review](../validation/2026-08-21-tencent-edgeone-fingerprint-review.md).

The 2026-08-30 Cloudflare review corrects the catalog before increasing dated
coverage. The unsupported apex `cloudflare-verify=` value becomes the current
owner-qualified `cloudflare-verify.<domain>` observation. A generic CNAME
string match and broad `cloudflare.net` target narrow to the documented
`cdn.cloudflare.net` partial-zone family. Cloudflare standard and secondary
nameservers, Pages, and the current `cdn.cloudflareanycast.net` and
`cdn.cloudflarecn.net` China Network families gain exact references and review
dates. `pacloudflare.com` remains undated because current first-party guidance
does not name it. Detail:
[the 2026-08-30 Cloudflare fingerprint review](../validation/2026-08-30-cloudflare-fingerprint-review.md).

## 4. Higher-order signals

Beyond listing vendors:

- **Stack archetypes.** Recognizable combinations (enterprise M365 + gateway +
  federated SSO; modern edge + managed database + hosted auth) are higher-signal
  and more memorable than a flat vendor list, and fit the existing motif layer.
- **Typed overlap characterization.** Shared declarative values such as SPF
  includes, provider-attested tenant IDs, DMARC `rua` destinations, and exact
  verification tokens can group domains by the observed overlap type. Each
  grouping must retain stale, copied, delegated, and broad-provider explanations
  and must not become entity resolution, ownership, or control inference. Its
  value is descriptive comparison, especially within an operator-supplied
  portfolio.

## 5. Boundaries

The invariants are the moat and constrain this plan: passive in collection
scope, zero credentials, zero paid feeds, and no active scanning. Specifically
out of scope for catalog work: ASN / GeoIP / IP-based fingerprinting, generic
target-owned HTTP-header probing or crawling, and ingesting a third-party
technology
database. The frontier stays in DNS-name, certificate-transparency, and
declarative-token space.

## 5b. What collection already yields that the catalog does not read

Catalog growth has been mined in one direction: run a corpus, collect the
strings no rule matched, triage them. That direction is close to exhausted at
the current catalog size. The 2026-07-17 round produced 780 candidate buckets,
and the promotion pass two hours later closed the queue's verifiable entries in
a single commit. What remains is unnamed prefixes and target-owned
infrastructure, neither of which is promotable.

A second direction is available and cheaper, because the records are already
being collected and simply are not read. Each row below is evidence recon
already holds at the end of a normal lookup.

| Surface | Current state | Why it matters |
|---|---|---|
| MTA-STS policy body | Fetched over HTTPS, only `mode:` parsed; the `mx:` lines are discarded | An operator-published, authoritative list of the domain's mail hosts, arriving over a different channel than the MX lookup. It corroborates mail attribution without a second DNS query. |
| TLS-RPT `rua=` | Presence only | The reporting destination names the vendor exactly as DMARC `rua` does, and that path already carries 42 rules. |
| CAA parameters | `issue` and `issuewild` values are matched; `iodef`, `accounturi`, and `validationmethods` are not parsed | `accounturi` identifies the issuing account and ACME client; `iodef` names a security-contact destination. |
| SRV | Five owners probed, zero catalog rules; attribution runs through a hardcoded table | The record type carries service, target, port, priority, and weight. Standards-defined mail autoconfiguration owners under RFC 6186 name the mail host directly. |
| DKIM selectors | About thirteen probed, attributed by CNAME target | Selector names are themselves vendor-assigned, so a selector that resolves is evidence even when its target does not match a known hint. |
| MX preference and SRV priority | Discarded after matching | A primary and backup split across two vendors is a topology observation that a flat vendor list cannot express. |
| Certificate transparency | Disabled in the 2026-07-17 round | Chain discovery ran on the common-subdomain probe alone. CT is where the existing `cname_target` rules came from. |

These are ranked deliberately. The first three add an evidence path to slugs
that already exist, which is worth more than a new vendor: 569 of 679 slugs
define exactly one detection type, so no amount of new single-path vendors
improves the share of claims that can be corroborated. See
[the 2026-07-25 base-rate memo](../validation/2026-07-25-pattern-base-rates.md).

## 5c. Inverting the discovery direction

Corpus mining finds a vendor only after some sampled namespace already uses it,
so it systematically misses the long tail and cannot anticipate a vendor at
all. The inverse is to enumerate vendors and read each vendor's own published
DNS requirements, deriving the pattern before it appears in any corpus.

This stays inside the invariants. Vendor documentation is provider-owned public
text, no target is queried, and the resulting candidate carries a reference by
construction rather than needing one found afterwards. It also produces the
disclosure-safe artifact the promotion gate wants: a vendor, a record type, a
pattern, and a citation, with the corpus supplying only an aggregate
observation count if the pattern is present at all.

A vendor-looking prefix and a documentation index are not independent support
for an exact record pattern. Legacy entries with such references remain an
unresolved review backlog; their presence is not precedent for promotion or a
fresh `verified` date. Check a current provider-owned page that names the exact
record role and reusable form, or document an independent disclosure-safe
basis. If neither is available, leave the candidate pending or deferred. A
vendor name in a string is a search lead, not proof of attribution; an opaque
prefix can still qualify if its exact independent basis is established.

## 6. Prioritized backlog

The canonical release order controls execution. Runtime evidence-path
expansion below is a separate feature track because it changes collection,
claim, schema, or network semantics and cannot silently enter a catalog
measurement round.

1. Preserve the completed rank-stratified aggregate, candidate dispositions,
   and fixed-observation zero-regression decision.
2. Preserve the completed regional baseline, accepted fixed-observation
   decision, and clean-main replay from the
   [regional result](../validation/2026-08-13-catalog-regional-round.md).
3. Preserve the closed vendor-seed contract and aggregate-only
   [result](../validation/2026-08-14-catalog-vendor-seed-round.md): 29 of 33
   rows corroborated the provider relationship, 4 were observed silent, and no
   catalog rule was promoted from the evaluation holdout. Do not call this
   measure recall or use holdout outcomes to tune the evaluated rules.
4. Preserve the completed 5,199-row
   [drift result](../validation/2026-08-14-catalog-drift-round.md), including
   its aggregate changed, unavailable, unmeasured, and no-change outcomes,
   measurement-surface disposition, classification-comparison abstention, and
   zero-promotion decision. Do not describe the repeated frame as independent
   coverage or universal external DNS drift.
5. Backfill `verified` dates only in independently reviewed families after a
   current vendor-page confirmation, starting with the mail-routing families
   named in [Freshness](#3-freshness). Raise the freshness ratchet only when
   observed coverage supports a new threshold. Do not stamp today's date on
   an undated rule whose public page was not re-read.
6. Keep the opt-in unmatched-observation envelope and private ranking tool
   covered by per-type bounds, reserved synthetic fixtures, and default-output
   absence tests.
7. Evaluate vertical rounds only if they answer a question not already covered
   by the completed unseen-vertical holdout; never pool them into population
   rates.

Separately gated future feature work, after the shipped v2.14 evidence baseline:

1. Read already collected MTA-STS `mx:` lines, TLS-RPT `rua=` destinations,
   and CAA `accounturi` or `iodef` parameters only under a new claim and schema
   contract.
2. Replace hardcoded SRV attribution with a catalog-driven path and consider
   additional standards-defined owners only with an explicit collection and
   compatibility review.
3. Reopen CT-enabled catalog discovery only through a separately frozen round;
   it cannot be compared to the CT-off regional contract as if collection were
   unchanged.

No promotion is complete without a current public reference or
disclosure-safe aggregate basis, a `verified` date, a positive fixture, a
lookalike-negative fixture, a sparse-result fixture, and provenance assertions.
