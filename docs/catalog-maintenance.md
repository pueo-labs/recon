# Reproducible catalog maintenance

The maintainer workflow has three distinct jobs: select a useful corpus,
collect and measure its bounded public observations, then review candidate
rules. It reuses the existing harnesses rather than adding a crawler, training
system, or automatic promotion service. Runtime collection and claim boundaries
remain unchanged. See [catalog strategy](catalog-strategy.md),
[rule grammar](fingerprints.md), and [data handling](data-handling-policy.md).

The [2026-10-23 hosting review](../validation/2026-10-23-hosting-rule-refinement.md)
is a worked documentation and offline regression round, including deferred
rules and the limits of its synthetic evidence.

## Agent entry points

Start with the harness-neutral
[recon-catalog-maintenance](../agents/maintainer/skills/recon-catalog-maintenance/SKILL.md)
entry point. It routes the six modes below to existing canonical helpers.

These skills are source-checkout maintenance instructions, not additional tools
in the public MCP server or changes to the frozen portable plugin evaluation:

| Job | Entry point | Completion artifact |
|---|---|---|
| Select and freeze a corpus | [recon-corpus-plan](../agents/maintainer/skills/recon-corpus-plan/SKILL.md) | Private frame and manifest, aggregate declaration, or explicit missing inputs; no collection |
| Collect or evaluate the frozen round | [recon-catalog-round](../agents/maintainer/skills/recon-catalog-round/SKILL.md) | Private retained observations, typed/stratified aggregates, completeness and decision ledger |
| Refine individual rules | [recon-fingerprint-triage](../agents/maintainer/skills/recon-fingerprint-triage/SKILL.md) | Evidence-backed disposition, scoped rule patch and synthetic regressions |

A harness can load these files directly or install them using its own skill
discovery mechanism. Paths inside them resolve against a recon checkout. They
do not install tooling, start a paid model session, or authorize network work.
An agent may prepare proposals autonomously within the requested task; rule
promotion and publication still require the repository's review and CI gates.
Within an authorized implementation task, that review can be automated through
source inspection, independently supported vendor grammar, and regression
checks. It does not add a human approval checkpoint before local catalog edits.
See the [maintainer acceptance rule](maintainer-loop-runbook.md#acceptance-rule).

## Start offline, without private context

Use a source checkout, Python 3.11-3.15 and the repository's pinned uv 0.13.5.
The installed PyPI CLI does not include `validation/` or `agents/`. From the
checkout root:

```text
uv sync --locked
uv run python -m validation.catalog_maintenance demo
```

This makes no DNS, HTTP, MCP or paid model calls. It freezes the public
[fictional plan](examples/catalog-maintenance-plan.json),
[round contract](examples/catalog-maintenance-round.json) and
[declared attributes](examples/catalog-maintenance-attributes.json) under
`validation/runs-private/catalog-maintenance/`. Repeated invocation preserves
the original artifacts. A changed example or implementation needs a fresh
private `--root`; old receipts remain historical evidence.

The example normalizes four supplied host rows into three namespaces, retains
two fictional strata, reports a missing commerce stratum and unknown scale and
geography, and counts one declared shared dependency group separately from
namespace count. It does not estimate an independent sample size. Finite
atomic and ordered-sequence controls exercise documented markers, deceptive
hosts, missing hops, reversed order, duplicate hops and subject provenance.
Cross-namespace graphs and CT are not evaluated. Existing dedicated suites
still own full human/JSON/MCP provenance, graph permutation and bounded-work
contracts; this small example does not replace them.

Its worked failed run has one timeout terminal and two unfinished items. With
no durable per-item starts, those two starts remain unknown, not unattempted.
Typed classification rates stay null and an empty proposal queue establishes
no catalog completeness. The existing 20-row public stratum minimum is kept;
the fictional example withholds subgroup publication rather than adding rows
to force eligibility.

## Choose the mode and freeze its authority

Documentation-only review, existing local artifact triage and planning are
offline. Read first-party configuration guidance, or use the neutral triage
skill and `validation.catalog_baseline` on retained local observations. For an
existing gap artifact, `validation.triage_candidates --gaps <private-path>
--output <private-path>` performs local filtering only. Recurrence and catalog
agreement do not establish precision or authorize promotion.

For new development or holdout work, copy the example documents into
`validation/corpus-private/`, replace only with operator-supplied inputs and
declare a question. The
[maintenance schema](catalog-maintenance-plan.schema.json) wraps the existing
round contract rather than replacing it. The attribute sub-schema is optional
at runtime; missing labels remain unknown. Include a private planning matrix:

| Dimension | Record and retain privately |
| --- | --- |
| Geography and language | Operator-declared basis, non-US/non-English coverage and unknowns; ccTLD, language and hosting location do not prove organizational geography |
| Scale or rank | Defensible small/medium/large basis or unknown; rank bands describe popularity, not company size |
| Sector and ownership | Commercial, nonprofit, public-sector, education or independent/community strata appropriate to the question |
| Website role | Informational presence, commerce, product/SaaS, content/community, public-service or institution |
| Provider mix and footprint | Diverse routing/hosting/email configurations and sparse/rich opportunities, without selecting only known catalog matches |
| Dependencies and exclusions | Explicitly known shared units, discovery inputs, prior consumed holdouts, duplicated hosts and actual exclusion files |

Use bounded quotas under one overall namespace budget, never an unbounded
Cartesian product. State source vintage, eligibility and missing or small
strata. A convenience/discovery frame is not a representative probability
sample. Do not publish tiny or unlabeled subgroup rates, infer ownership from
shared infrastructure, or silently count related namespaces as independent.

Freeze before collecting:

```text
uv run python -m validation.catalog_maintenance plan --plan validation/corpus-private/maintenance-plan.json
```

Admission archives source bytes and the original round plan, retains vintage,
normalizes/deduplicates through `prepare_catalog_round`, enforces actual
exclusion/development-frame disjointness and freezes the catalog/execution
digests. Existing local fingerprint, signal, motif and prior semantics receive
additional private digests; operator configuration, DNS and limiter state are
preserved. A local overlay is not the canonical built-in baseline. Changed
context blocks new collection and withholds comparable interpretation.
Interrupted preparation retains its reservation; reconcile it or declare a new
ID without deleting evidence. This wrapper supports non-drift contracts with
the existing runner's two-distinct-namespace recurrence floor. Drift keeps its
separate prior-result comparison contract.

Collection is a separate explicitly authorized action. The example below is a
template for a plan the operator has authorized; an automated due-work wake
does not provide that authority:

```text
uv run python -m validation.catalog_maintenance collect --admission validation/runs-private/catalog-maintenance/rounds/my-round/admission.json --attempt 1 --allow-network
```

The wrapper invokes the existing scan/batch path with frozen namespace,
logical DNS-query, concurrency, per-namespace timeout, overall runtime and
attempt budgets. A namespace can start once per attempt. DNS query reservations
include retries that revisit the safe-resolver boundary; transport-internal
packets and existing HTTP retry policies are not counted as DNS queries.
Those policies remain execution-digest bound. Budgets apply per attempt, with
an explicit maximum number of attempts. CT defaults off and must agree with the
round plan; direct probes remain off. Ordinary DNS and MTA-STS traffic is
target-visible. No user list is expanded through discovered related domains.
These source-checkout controls add no ordinary CLI setup or flags.

Durable namespace starts precede lookup IO. Query exhaustion stops the run
instead of becoming an empty source observation; streamed results remain
available for offline finalization. Admission, started-attempt and returned
receipts are immutable. A repeated attempt never recollects. A declared retry
uses the next numbered attempt and retains `retry_of`; reconcile an interrupted
or still-running attempt before starting another. Never run two attempts of
the same round concurrently.

For a holdout, freeze the exact candidate catalog and a nonempty development
frame, preserve disjointness and use the same private registry root. Consumption
is reserved by namespace before collection or first offline evaluation.
Renaming, reordering or taking a subset cannot recycle consumed names in that
registry. Failed collection still consumes it; no holdout retry is accepted.
The registry is local accounting, not a cross-machine secrecy or independence
guarantee. Do not inspect holdout outcomes while developing rules.

## Evaluate retained work and propose a patch

Run `validation.scan --finalize-existing <private-run>` with the original
corpus, manifest, collection choices and thresholds to finish an interrupted
scan offline. Preserve the original results; do not overwrite them or replace
failed namespaces. The wrapper's `resume` mode passes those frozen settings to
that exact offline path and records finalization before a development retry:

```text
uv run python -m validation.catalog_maintenance resume --admission validation/runs-private/catalog-maintenance/rounds/my-round/admission.json --attempt 1 --input validation/runs-private/catalog-maintenance/rounds/my-round/attempt-01/retained-run
```

Stop any surviving collection process before resuming offline. A retry is
refused until the previous attempt returned or has an offline finalization
receipt. Then reduce the specific retained run:

```text
uv run python -m validation.catalog_maintenance evaluate --admission validation/runs-private/catalog-maintenance/rounds/my-round/admission.json --input validation/runs-private/catalog-maintenance/rounds/my-round/attempt-01/retained-run
```

Evaluation freezes each result location and content digest separately, so a
new declared development attempt does not overwrite an earlier evaluation.
Holdouts get one evaluation reservation. Records must belong to the frozen
frame and fit its cap. Supplied evaluation inputs are limited to 8 MiB per
file, 64 MiB total, 1,024 candidate JSON/NDJSON files, 100,000 directory entries,
32 directory levels and 100 JSON nesting levels. Stable regular-file reads
reject symbolic links, growth and replacement. Hashing and decoding use the
same bounded bytes; invalid or oversized inputs fail without an evaluation or
holdout-consumption receipt. Split larger development cohorts into separately
admitted rounds rather than truncating observations. Receipts distinguish admitted, terminal success,
terminal error, unfinished, known-started lower bounds, unknown starts and
proven unattempted items. An unverifiable modern start receipt withholds start
accounting rather than inventing zeros. Source availability and classification
denominators remain the typed reducer's job. Review atomic and composite scope
separately: a requested layer is not proof it was successfully collected or
tested. CT-disabled and structural-not-evaluated states remain explicit.

Before a proposed PR, specify whether it changes a catalog rule, signal,
relation or inference claim. Require current first-party support or a
disclosure-safe basis, exact grammar/role, positive and counterexample fixtures,
sparse and failed-source cases, duplication and appropriate permutation checks,
bounds and retained namespace/provenance through human, JSON and MCP outputs.
An atomic addition alone supplies no stronger composite or inference claim.
Use the existing overlap, claim-disposition and full local/hosted gates; there
is no automatic promotion from classification uplift.

Inputs and all output artifacts are private by default. Before committing or
uploading any reviewed public proposal, give an explicit tracked file list to
`validation.catalog_maintenance check-publication`, then run the canonical
validation-hygiene gate. Private roots, untracked files, path escapes and broad
upload globs are refused. The existing gate also catches force-added private
artifacts. File-list checks do not anonymize content or replace disclosure
review; do not upload the private receipt directory. This workflow performs no
upload or GitHub write itself.

## Monthly due work and review receipts

The versioned [public ledger](catalog-freshness-ledger.json) starts with the
eight documented additions checked on 2026-10-23. Later rows record the
2026-10-28 checks, including a later CRM pass the same day, and the
2026-10-29 marketing reference check, and the 2026-10-30 Salesforce and
advertising reference check, and the 2026-11-02 CRM and advertising
reference check, a later 2026-11-02 data and analytics reference
check, and a later 2026-11-02 data, analytics, and infrastructure
reference check, and the 2026-11-16 email and cloud reference check,
and a later 2026-11-16 email reporting reference check,
and a later 2026-11-16 email, DNS, and event reference check,
and a later 2026-11-16 DNS and email reference check,
and a later 2026-11-16 DMARC reporting and DNS reference check,
and a later 2026-11-16 DNS provider reference check,
and a later 2026-11-16 email and DNS reference check,
and a later 2026-11-16 nameserver and mail reference check,
and a later 2026-11-16 nameserver, mail, and reporting reference
check, and a later 2026-11-16 mail, SPF, and custom-DNS reference
check, and a later 2026-11-16 mail and verification reference check.
It is a bounded
review record, not a claim that every rule was reviewed that month. Private monthly receipts
bind due rules to their exact claim/catalog digest, prior/new reference, actual
source check/review date, disposition, next review and bounded proposal queue.
The offline freshness auditor and weekly Provider drift smoke do not establish
that a documentation review occurred.

```text
uv run python -m validation.catalog_maintenance due --period 2026-10 --review-limit 8 --proposal-limit 8
uv run python -m validation.catalog_maintenance status --admission validation/runs-private/catalog-maintenance/freshness/2026-10/admission.json
uv run python -m validation.catalog_maintenance review-template --admission validation/runs-private/catalog-maintenance/freshness/2026-10/admission.json --output validation/corpus-private/reference-reviews.json
uv run python -m validation.catalog_maintenance review --admission validation/runs-private/catalog-maintenance/freshness/2026-10/admission.json --input validation/corpus-private/reference-reviews.json
```

The template starts explicitly unreviewed and deferred; edit it to record only
checks actually performed. Submitting it unchanged produces a blocked receipt.
Use the exact admitted rule IDs and the
[reference review schema](catalog-reference-review.schema.json). A checked row
needs actual source/review dates, supporting basis and a later `next_review`.
Use `unchanged`, `narrowed`, `added`, `retired` or `deferred`; source status is
`checked`, `unreachable` or `unreviewed`. Unknown sources cannot advance a
verification date. A URL edit alone is not a source check. A changed semantic
digest becomes due again even before its old next-review date.

Repeated wakes reuse one bounded admission; other active cycles reserve their
unfinished rule IDs. Immutable digest-named submissions can resume partial or
unknown work without rewriting checked decisions. Distinct receipts report
`completed`, `no_change`, `partial`, `blocked` and `skipped`; `status` also reports
whether the cycle is overdue. Record an intentional skip with `skip --admission
<private-path> --reason <explanation>`. No-change is successful completed review;
an inaccessible source remains unresolved. Neither state mechanically stamps
YAML `verified` values.

For an authorized external proposal, `catalog_freshness.claim_proposal` reserves
the queue item's content-bound identity and rule before a PR write. Different
intents for a rule stay serialized while a claim is outstanding. Reconcile
GitHub after interruption rather than creating a duplicate; record a checked
merged/closed PR with `resolve_proposal`. Identical completed intents do not
reopen. The next distinct checked intent can proceed. These helpers perform no
remote writes. A proposed patch still needs existing semantic dispositions,
synthetic fixtures and the full gate.

A future monthly scheduler may invoke offline `due` and record its result. It
may not silently collect, use paid models, upload inputs, push, open PRs or
promote rules. No recurring job is installed or activated by this workflow.

## One round, with explicit boundaries

1. State a question and estimand before selecting rows. Discovery yield,
   classified surface, documented-provider corroboration, and independently
   labeled precision answer different questions. Declare sample limits and
   what the frame cannot represent.
2. Freeze the dated source bytes, selection rule, exclusions, normalized apex
   membership, strata, and implementation/catalog digests. Use keyed rank or
   ccTLD preparers when those designs apply. Equal quotas are discovery budgets,
   not population weights. A ccTLD is a namespace attribute, not geolocation.
3. Separate development from holdout and forward-time drift. The generic round
   preparer deduplicates within the round, but its exclusion-policy text is not
   an exclusion algorithm. Use the actual exclusion files in the specialized
   preparers or a tested comparison before claiming a disjoint holdout. Record
   known duplicated observations or shared templates where independently
   established; apex deduplication alone does not prove independence. Shared
   providers do not establish common organizational ownership.
4. Freeze CT choice, direct probes off, concurrency, failure/retry disposition,
   recurrence thresholds, and the regression budget. Existing historical
   declarations remain immutable. A new question requires a new round, not an
   edited old result. Complete any declared protected-main gate before requests.
5. Collect only when requested. `validation.scan` contacts the supplied corpus;
   planning and reduction of existing results do not. DNS is observable and
   default collection can fetch MTA-STS. Preserve failures, unavailable sources,
   partial collection, truncation, and per-type opportunity denominators. Do
   not replace failed rows with convenient successful rows.
6. Refine candidates on development data. Require exact reusable rule grammar,
   independent provider support or a disclosure-safe basis, a genuine review
   date, synthetic positive/lookalike/sparse fixtures, and exact provenance.
   An independent reviewer can inspect the basis and negatives without seeing
   holdout outcomes. Rule agreement or agent agreement is not ground truth.
7. Freeze the candidate before a one-shot holdout. If evaluation reveals a
   defect, fix it, but do not report the reused holdout as independent proof of
   the revised rule. Declare a new untouched evaluation. Drift comparisons must
   disclose changed observation surfaces and withhold classification comparisons
   across unequal interpretation/catalog commitments.
8. Publish only a disclosure-reviewed aggregate decision and supported generic
   patterns. Per-domain rows, membership, opaque tokens, and keys stay private.
   A hash is an integrity commitment, not anonymization or collector attestation;
   small-cell suppression alone is not a general privacy guarantee.

## Matcher overlap and claim review gates

`uv run python -m scripts.check_catalog_overlaps` checks canonical YAML rules
against the shared
[synthetic witness corpus](../tests/fixtures/catalog-match-witnesses.json),
plus deterministic literal-host positives, child hosts and deceptive
prefix/suffix variants. Equal-pattern rules across different slugs are also
reported when no witness is available. Different regex spellings are tested
on the same values. This is finite candidate-match coverage before first-match
selection or AND gating, not a general regex-equivalence solver, a claim that
every rule has a positive witness, or evidence of real-world precision.

An overlap diagnostic includes both source/slug/type/pattern IDs and its
synthetic witness. Narrow or retire an accidental collision. An intentional
overlap belongs in
[catalog-overlap-reviews.json](catalog-overlap-reviews.json), with its reason,
expected retained rule IDs, record type and namespace scope. The gate replays
actual CNAME tier selection for those exceptions. A specificity exception must
retain one selected rule; a distinct-role exception must retain both roles.
Other record families need their own explicit selection proof before expanding
exception support. Stale exceptions fail. Oracle's existing overlap retains
Fusion as application and OCI as infrastructure, from one CNAME observation;
the old suppression comment was inaccurate. Multiple roles are not independent
corroboration.

The existing diff-aware
`uv run python scripts/check_fingerprint_freshness.py` now also compares claim
metadata under unchanged matching keys. Entry-level subject, category, role,
confidence and grouping context, plus rule descriptions, references, tier,
weight and other rule fields participate. Description whitespace is normalized.
Added/removed rules, meaningful edits and changes to `verified` require an
exact before/after disposition in
[catalog-rule-reviews.json](catalog-rule-reviews.json). The diagnostic prints
the required digests; an absent side is JSON `null`. Matching-key changes need
both retirement and addition dispositions. Historical dispositions remain as
review evidence and cannot authorize a different metadata revision.

Each disposition records `semantic` or `editorial`, a real `reviewed_on` date,
a reason with supporting basis, and `source_checked_on` or JSON `null` when the
source was not checked. Editorial dispositions permit description spelling or
layout corrections; structural, role and reference changes require semantic
review. Whitespace-only edits need no record. A review can narrow an unsupported
claim without pretending the vendor source was rechecked. Advancing `verified`
requires the actual declared source-check date, independently of the local
edit/review date. Removing an unsupported verification date is also reviewable.
A changed URL or description alone supplies no fresh verification evidence.
These offline gates validate the review record's consistency; they do not
prove that a reviewer read a source or that a vendor's configuration is current.

Both gates run locally in `scripts/check.py` and in blocking catalog CI. Keep
the original positive/lookalike/sparse/provenance tests as well: a passing finite
witness corpus does not replace claim-specific regression evidence.

### Documented family review, 2026-10-23

The [Convex abuse-protection guide](https://docs.convex.dev/production/abuse-protection)
documents the literal `convex.domains` custom-domain CNAME target. Its rule is
anchored to that target, including the optional DNS root dot. Attribution stays
with the queried related host and does not establish active deployment, traffic,
plan, ownership or security state. No `_convex_domains` TXT probes were added.

The [ImprovMX API reference](https://www.improvmx.com/api/v4/) and
[white-label guide](https://improvmx.com/guides/white-label-mx-records/) support
the `mx1.improvmx.com`, `mx2.improvmx.com` and `spf.improvmx.com` rules.
The [Forward Email FAQ](https://forwardemail.net/en/faq) supports its two
`mx1`/`mx2.forwardemail.net` MX targets, `spf.forwardemail.net`, and the anchored
nonempty `forward-email-site-verification=` marker. MX and SPF reuse existing
DNS-label suffix matching, including child hosts; this is not exact-host
enforcement. SPF is a parsed policy reference, not full sender authorization.
The TXT marker does not establish completed verification or active use.

All eight rules record the actual 2026-10-23 source-check date and an exact
addition disposition. The synthetic family tests preserve raw records and
namespace scope, cover lookalikes, duplicates, sparse/failed sources and cached
replay, and reject unsupported active-use/ownership/health wording. They do not
establish population precision. White-label mail routes can remain unobserved;
forwarding destinations, DKIM selector expansion, Domain Connect owners and
Cloudflare Tunnel remain outside this addition batch. No collection scope or
bare-domain invocation changed.

### Documented reference check, 2026-10-28

The [Claude SSO guide](https://support.claude.com/en/articles/13132885-set-up-single-sign-on-sso)
documents an apex TXT whose value begins with `anthropic-domain-verification-`
for Team plans, Enterprise plans, and Console organizations. Verification is
the domain-claim step. It does not by itself enforce SSO or prove active use.
The previous API getting-started reference does not document this record.

The [Mistral verify-domain guide](https://docs.mistral.ai/admin/set-up-organization/verify-domain)
documents an apex TXT using the `mistral-domain-verification=` prefix. The
guide requires that record before email-domain authentication, SAML SSO, and
other enterprise access features. The record does not prove those features
are enabled. A separate SSO quickstart documents a different TXT name and
value. That second shape is not part of this rule.

Six other undated AI rules were checked against their cited pages and stay
undated. Those pages do not print the catalog grammar. No new detection, DNS
record type, or collection path was added.

### Documented reference check, 2026-10-28, CRM and marketing

A later pass the same day checked eight undated CRM and marketing rules. None
of the cited pages print the catalog grammar, so none received a `verified`
date. No new detection, DNS record type, or collection path was added.

The Dynamics 365 Marketing rule cites the marketing index. The current
[Customer Insights - Journeys domain-authentication guide](https://learn.microsoft.com/en-us/dynamics365/customer-insights/journeys/domain-authentication),
updated 2026-10-13, tells the operator to copy an ownership TXT from the
product wizard and does not print `d365mktkey=`. The older authenticate-domains
article now redirects to the outbound-marketing removal notes, which also do
not print that prefix. A search-index copy of the retired article is not a
current basis. Separate DKIM and envelope-from records described only on that
retired article were not added.

The 6sense rules cite the support index. It does not document a customer CNAME
into `6sense.com` or `6sense.io`, or a TXT value that begins with `6sense`.
The Apollo rule cites the knowledge-base index. Current mailbox-authentication
articles cover SPF, DKIM, and DMARC and do not print
`apollo-domain-verification=`. The Braze rule cites the docs index. Current
email setup names records supplied in the dashboard and ESP or CDN targets,
not a CNAME into `braze.com`. The Clearbit rule cites the help-center index.
The content-security-policy article lists `clearbit.com` hosts for a browser
allowlist, not as a customer DNS CNAME target. The Customer.io rule cites the
docs index. Domain authentication places records on an account-specific
subdomain and names `customeriomail.com` for default tracked links. It does
not document a CNAME whose target is under `customer.io`.

### Documented reference check, 2026-10-28, later CRM pass

A later pass the same day checked eight more undated CRM rules. Two received
a `verified` date because the current vendor page prints the grammar. Six
stay undated. No new detection, DNS record type, or collection path was
added. This note does not cut a release.

The [Oracle Eloqua first-party cookie tracking guide](https://docs.oracle.com/en/cloud/saas/marketing/eloqua-user/Help/EloquaAsynchronousTrackingScripts/Tasks/BasicPageTrackingFirst.htm)
says the tracking domain CNAME points at `s[SiteID].t.eloqua.com`. The
existing suffix rule observes that documented target. It does not prove
landing pages, forms, or active campaigns. Pages that say to create a CNAME
without printing another target were not folded into this rule.

The [Emma DKIM setup guide](https://help.myemma.com/s/article/DomainKeys-Identified-Mail-DKIM)
shows an apex TXT whose value begins with `e2ma-verification=` and an
account-specific validation hash. The rule observes that record. It does not
prove sending is active. The same guide's DKIM CNAME targets and SPF include
are separate records and were not added.

Demandbase, Drift, Gong, both HubSpot TXT rules, and iContact stay undated.
Their cited pages do not print the catalog grammar. Separate shapes seen on
those pages were not added. Those include Drift MX hosts under
`driftmail.net`, a Gong branded-URL CNAME with no named target, and iContact
DKIM CNAME hosts. HubSpot content-domain CNAMEs remain the existing dated
`hubspot.net` rule.

### Documented reference check, 2026-10-29

This pass checked eight undated marketing rules. Three received a
`verified` date because the current vendor page prints the grammar. Five
stay undated. No new detection, DNS record type, or collection path was
added. This note does not cut a release.

The [Klaviyo branded-sending guide](https://help.klaviyo.com/hc/en-us/articles/115000357752)
prints an apex TXT whose value begins with `klaviyo-site-verification=`
and a public API key placeholder. The rule observes that record. It does
not prove NS delegation, static DKIM CNAMEs, SMS, or that sending is
active. The previously cited article now redirects to an integration
guide that does not print the prefix. Those other DNS shapes were not
added.

The [Kartra manual custom-domain article](https://support.kartra.com/support/solutions/articles/153000169884-manually-connect-a-custom-domain)
documents a CNAME from `www` or a subdomain to `username.kartra.com`.
The existing suffix rule observes that documented target. It does not
prove pages, funnels, checkout, or memberships, and it does not show
that the apex itself is hosted there. The cited support index does not
print the target.

The [Iterable shortlink guide](https://support.iterable.com/hc/en-us/articles/4403865896724-Link-Shortening-and-Click-Tracking-for-RCS-SMS-and-WhatsApp)
documents a CNAME to `links.iterable.com` or `links.eu.iterable.com`.
The existing suffix rule observes that documented target. It does not
prove email, SMS, RCS, or WhatsApp sends are active. A separate HTTPS
guide documents a CloudFront CNAME and was not added. The cited help
index does not print the target.

Both Intercom rules stay undated. Cited article 179 now serves a custom
data attributes article. It does not document a CNAME into `intercom.io`
or print `intercom-domain-verification=`. Current Help Center hosts
under `intercom.help` and `intercomhelpcenter.com` are a different
target and were not added.

LiveRamp, MailerLite, and the Marketo `mktosvc.com` rule stay undated.
The LiveRamp docs index and the current SSO guide do not print
`liveramp-site-verification=`. The MailerLite help index and the current
domain-authentication guide say to paste a domain-verification TXT from
the product and do not print `mailerlite-domain-verification=`. A DKIM
CNAME under `mlsend.com` is a separate shape and was not added. The
cited Marketo set-up-your-domain URL returned page not found, and a
current docs search did not find `mktosvc.com` printed as a customer
CNAME target. The already dated `mktoweb.com` rule was not reopened.

### Documented reference check, 2026-10-30

This pass checked eight undated advertising, sales, and Salesforce rules.
Two received a `verified` date because the current vendor page prints the
grammar. Six stay undated. No new detection, DNS record type, or
collection path was added. This note does not cut a release.

The [Salesforce SPF include guide](https://help.salesforce.com/s/articleView?id=xcloud.emailadmin_spf_include_salesforce.htm&language=en_US&type=5)
prints `include:_spf.salesforce.com` for mail sent from the Salesforce
application. The exact include rule observes that record. It does not
prove messages are being sent. The same guide says other `salesforce.com`
SPF records are not this include, so the broader `salesforce.com` suffix
stays undated.

The [Account Engagement tracker-domain guide](https://help.salesforce.com/s/articleView?id=mktg.pardot_admin_first_party_cookie_add_tracker_domain.htm&language=en_US&type=5)
documents a CNAME pointing at `go.pardot.com`. The existing suffix rule
observes that documented target. It does not prove landing pages,
campaigns, or first-party tracking. The cited older domain-management URL
is not the page that prints the target.

Meta, both Outreach rules, the broader Salesforce SPF suffix, the `00D`
TXT pattern, and `salesforce-domain-verification=` stay undated. The
current Meta domain guide says to add a TXT supplied by the product and
does not print `facebook-domain-verification=`. An HTML meta tag with
that name is a different record and was not added. The Outreach help
index does not print an `outreach.io` SPF include or a TXT value that
begins with `outreach`. Current Salesforce email-domain articles use
DKIM or an authorized-domain token and do not print either TXT grammar.
A token host under a Salesforce-owned name is a separate shape and was
not added.

### Documented reference check, 2026-11-02

This pass checked eight undated CRM, marketing, and advertising rules.
One received a `verified` date because the current vendor page prints the
grammar. Seven stay undated. No new detection, DNS record type, or
collection path was added. This note does not cut a release.

The [Yandex Webmaster rights-verification guide](https://yandex.ru/dev/webmaster/doc/en/concepts/verification)
prints a TXT value of `yandex-verification:` followed by a confirmation
code. The existing prefix rule observes that record. It does not prove
that rights were confirmed, and it does not identify Yandex Direct,
Metrica, or Connect. The same guide's meta tag and HTML file are separate
records and were not added. The previously cited Connect support URL
returns 404.

Salesloft, all three Segment rules, Salesforce Marketing Cloud, and
Unbounce stay undated. The cited Salesloft custom-email-domain article
returns 404. The current sending-records page is a client-rendered shell
whose extracted text says Salesloft sends through the customer's mailbox
and does not print `salesloft.com` or a TXT value that begins with
`salesloft`. A support-supplied tracking CNAME is a separate record and
was not added. The current Twilio copy of the Segment custom-domain guide
uses two domains Segment generates for that workspace. It does not print
a stable customer CNAME target under `segment.com` or `segment.io`, and
it does not print `segment-site-verification=`. Twilio organization
verification uses `twilio-domain-verification=` and was not added. The
cited Marketing Cloud overview and the current Register a Domain article
return the Salesforce Help shell. The retrieved Register a Domain steps
say to place a generated token in a TXT record and do not print a value
beginning with `SFMC-`. That token was not added. The cited Unbounce
article now serves a webhook guide and does not document a CNAME into
`unbounce.com`. The current domain article says the CNAME value is a
unique string copied from the product. Default hosts `unbouncepages.com`
and `ubpages.com` are a different shape and were not added.

### Documented reference check, 2026-11-02, data and analytics

This pass checked eight undated data and analytics rules. One received a
`verified` date because the current vendor page prints the grammar.
Seven stay undated. No new detection, DNS record type, or collection
path was added. This note does not cut a release.

The [Atlas federated-authentication domain-mapping guide](https://www.mongodb.com/docs/atlas/security/manage-domain-mapping/)
prints a TXT value of `mongodb-site-verification=` followed by a
32-character string. The existing prefix rule observes that record. It
does not prove that verification completed, that the domain is
associated with an identity provider, or that a cluster exists. The
same guide's HTML file is a separate record and was not added. The
previously cited docs root does not print the grammar.

Databricks, Datadog, Dynatrace, Heap, Hotjar, Mixpanel, and Amplitude
stay undated. The current Databricks email-domain sign-in guide, last
updated 2026-10-09, refers to a verified email domain for just-in-time
provisioning and does not print `databricks-domain-verification=`.
Account SSO pages document identity-provider metadata and do not print
that prefix. The current Datadog SAML guide does not print
`datadog-domain-verification=`. Docs searches returned DNS synthetic
tests, a Nifcloud `nifty-dns-verify=` rule, and Entra domain events.
None print this prefix. The current Dynatrace SAML guide, updated
2026-07-30, says to copy a TXT value from the product. It does not
print `dynatrace-site-verification=`, and it says the TXT resource
record can be removed after validation. That copied value was not
added. A direct fetch of `developers.heap.io` did not return a page
body. The indexed first-party collection guide says the customer CNAME
value is the CDN distribution domain, for example a CloudFront name,
and the CDN origin is `heapanalytics.com`. It does not print a stable
customer CNAME target under `heapanalytics.com`. Script hosts
`cdn.heapanalytics.com` and `heapanalytics.com` are a different shape
and were not added. A direct fetch of `help.hotjar.com` did not return
a page body. The indexed DNS TXT article says to add a TXT and points
at registrar guides. It does not print `hotjar-domain-verification=`.
A script host under `insights.hotjar.com` was not added. A direct fetch
of `docs.mixpanel.com` did not return a page body. The indexed
first-party domains guide, updated 2026-10-01, says the customer CNAME
value is the Mixpanel proxy host for that region. It does not print a
stable customer CNAME target under `mixpanel.com`. The SSO guide prints
`mixpanel-domain-verify=` as a TXT and was not added to this CNAME
rule. Default hosts `api.mixpanel.com`, `api-eu.mixpanel.com`,
`api-in.mixpanel.com`, and `cdn.mxpnl.com` are API or CDN hosts and
were not added. The current Amplitude SSO guide documents SAML entity
and ACS URLs and does not print `amplitude-domain-verification=`.

### Documented reference check, 2026-11-02, data, analytics, and infrastructure

This pass checked eight undated data, analytics, and infrastructure
rules. Two received a `verified` date because the current vendor page
prints the grammar. Six stay undated. No new detection, DNS record
type, or collection path was added. This note does not cut a release.

The [Pendo organization CNAME guide](https://support.pendo.io/hc/en-us/articles/4402594600589-Configure-organization-CNAME)
prints example customer CNAME targets that end in
`-content.example.pendo.io` and `-data.customer.pendo.io`. The
existing suffix rule observes a CNAME target under `pendo.io`. It
does not prove that guides are served, that events are collected, or
that setup is complete. Product-supplied prefixes and the
certificate-validation CNAMEs were not copied. The previously cited
help-center root does not print the grammar.

The [Afternic domain-parking page](https://www.afternic.com/domain-parking)
says to set the domain nameservers to `ns1.afternic.com` and
`ns2.afternic.com`. The existing suffix rule observes an NS host
under `afternic.com`. It does not establish a for-sale listing,
parking revenue, or that the namespace is unused. A direct fetch of
the parking help article returned a loading shell and was not used as
the basis.

New Relic, Optimizely, Snowflake, WalkMe, Adobe Experience Manager
Cloud Service, and the Alibaba Cloud `alibaba.com` CNAME stay undated.
A direct fetch of `docs.newrelic.com` did not return a page body. The
indexed domain-capture guide says to add the TXT record the product
provides. It does not print `newrelic-domain-verification=`. That
product-supplied value was not added. The cited Optimizely developer
host redirects to the current Performance Edge guide, which prints a
customer CNAME target of `cname.optimizely-edge.com`. It does not
print a customer CNAME target under `optimizely.com`. That target was
not added. The current Snowflake domain-verification guide prints an
apex TXT whose value is `snowflake-verification=` followed by a UUID.
That prefix is not `snowflake-domain-verification=`. The second prefix
was not added. The WalkMe EU access-requirements article, last updated
June 4, 2026, lists script and API hosts under `walkme.com`. Those are
allowlist hosts, not a customer CNAME target, and they were not added.
The current AEM as a Cloud Service custom-domain guide, last updated
September 29, 2026, prints a CNAME target of `cdn.adobeaemcloud.com`.
It does not print `adobecqms.net`. That cloud-service target was not
added. The current Alibaba Cloud ALB guide says to CNAME a custom
hostname to the instance DNS name, for example a host under
`alb.aliyuncsslb.com`. It does not print a customer CNAME target under
`alibaba.com`. That instance DNS name was not added.

### Documented reference check, 2026-11-16

This pass checked eight undated email and cloud rules. One received a
`verified` date because the current vendor page prints the grammar.
Seven stay undated. No new detection, DNS record type, or collection
path was added. This note does not cut a release.

The [Atlassian Cloud custom-domain email DNS checker](https://support.atlassian.com/jira/kb/why-dns-checker-for-setting-up-custom-domain-email-address-still-unverified-in-cloud/)
prints a TXT value that begins with
`atlassian-sending-domain-verification=`. The existing prefix rule
observes that record. It does not prove that the DNS check succeeded
or that mail is being sent. The same page prints
`include:_spf.atlassian.net` and a DKIM CNAME. Those are separate
records and were not added. The example token on the page was not
copied.

Alibaba Cloud `alibabadns.com`, `alibaba-inc.com`,
`service.alibaba.com`, and `aliyun-site-verification=`, the Amadeus
`amadeus.com` SPF suffix, the AppRiver `arsmtp.com` MX, and the
broader Atlassian `atlassian.net` SPF suffix stay undated. The
[Alibaba Mail MX, CNAME, and TXT guide](https://www.alibabacloud.com/help/en/alibaba-mail/latest/explanation-of-terms-for-mx-cname-and-txt-records)
prints regional CNAME targets `mail.sg.aliyun.com`,
`mail.hk.aliyun.com`, `mail.de.alibabacloud.com`, and
`mail.us.alibabacloud.com`. It does not print `alibabadns.com`. The
Alibaba Cloud DNS getting-started page reached from the CNAME
configuration URL prints `ns1.alidns.com` and does not print
`alibabadns.com`. Those regional mail hosts were not added. The same
Mail guide prints regional MX hosts `mx1.sg.aliyun.com`,
`mx1.hk.aliyun.com`, `mx1.de.alibabacloud.com`, and
`mx1.us.alibabacloud.com`, plus the `mx2` equivalents. It does not
print `alibaba-inc.com`. Those regional hosts were not added. It also
prints SPF includes `spf.sg.aliyun.com`, `spf.hk.aliyun.com`,
`spf.de.alibabacloud.com`, and `spf.us.alibabacloud.com`. Those
includes were not added. The [international Direct Mail DMARC
guide](https://www.alibabacloud.com/help/en/direct-mail/what-is-dmarc-and-how-to-configure-dmarc-records)
prints a placeholder `rua` of `dmarc_report@example.net`. The
[Aliyun Direct Mail DMARC guide](https://help.aliyun.com/en/direct-mail/what-is-dmarc-and-how-to-configure-dmarc-records)
prints `rua=mailto:dmarc_report@service.aliyun.com` and calls that
mailbox the default report mailbox. Neither prints
`service.alibaba.com`. The `service.aliyun.com` mailbox is a separate
shape and was not added. The [Aliyun site-verification
guide](https://help.aliyun.com/en/document_detail/3043313.html)
describes HTML tag and file checks for Baidu, 360, and Sogou, and a
TXT record copied from Google Search Console. It does not print
`aliyun-site-verification=`. The copied value was not added. A direct
fetch of the [Amadeus developer flight
guide](https://developers.amadeus.com/self-service/apis-docs/guides/developer-guides/resources/flights/)
returned an empty body and did not print an SPF include of
`amadeus.com`. The indexed guide uses `include=` as an API query
parameter, not an SPF include. A community thread is not a vendor
basis. No second SPF shape was added. The [OpenText support
portal](https://support.opentext.com/csm) returns a login page and
does not print `arsmtp.com`. DNS-lookup directories are not a vendor
basis. The Atlassian page's exact SPF include is narrower than the
existing `atlassian.net` suffix, so that suffix stays undated.

### Documented reference check, later on 2026-11-16

This pass checked eight undated email rules. One received a
`verified` date because the current vendor page prints the grammar.
Seven stay undated. No new detection, DNS record type, or collection
path was added. This note does not cut a release.

The [Brevo domain-setup article](https://help.brevo.com/hc/en-us/articles/35337929909778-Set-up-your-domain-in-Brevo)
prints an aggregate rua of `rua=mailto:rua@dmarc.brevo.com` and the
example record `v=DMARC1; p=none; rua=mailto:rua@dmarc.brevo.com`. The
[domain authentication article](https://help.brevo.com/hc/en-us/articles/12163873383186)
prints the same rua. The existing `dmarc.brevo.com` rule observes that
mailbox domain. It does not prove that reports are collected or that
mail is sent through Brevo. The `p=none` value is the page's example
policy.

The authentication article calls the ownership TXT a Brevo code and
says to copy its value from the product. It does not print
`sendinblue-site-verification=`. The domain-setup article also does
not print that prefix. The copied product value was not added. The
same authentication article says SPF and MX records are not required
to authenticate a domain and are provided only when setting up a
dedicated IP. The [dedicated-IP article](https://help.brevo.com/hc/en-us/articles/115000240344)
prints NS values `ns1.sendinblue.com` and `ns2.sendinblue.com` and
says to copy the SPF value from the product. It does not print an SPF
include of `sendinblue.com`. Those nameserver hosts were not added.

The [PayPal Braintree SPF guide](https://developer.paypal.com/braintree/articles/guides/configuring-spf-records/)
says configuring SPF records is no longer required for integration.
The retained steps print `include:spf.braintreegateway.com`. That
exact include is narrower than the existing `braintreegateway.com`
suffix, so that suffix stays undated. The exact include was not added.

The [Barracuda Domain Fraud Protection DMARC step](https://documentation.campus.barracuda.com/wiki/display/BDFP/Step+1+-+Configuring+DMARC+on+Your+Domain)
prints example aggregate rua and forensic ruf mailboxes on the host
`dmarc.barracudanetworks.com`. That host is narrower than the existing
`barracudanetworks.com` suffix, so that suffix stays undated. The
narrower host was not added. The example mailbox local-part was not
copied.

The [AutoSPF query-tracking article](https://support.autospf.com/support/solutions/articles/5000874728)
describes a host under `autospf.email` that AutoSPF uses to count DNS
queries. It does not print a customer SPF include of `autospf.email`.
The [manual setup article](https://support.autospf.com/support/solutions/articles/5000819575-manual-autospf-setup)
says the customer SPF record uses an include that points at AutoSPF
DNS space, and it does not print that include. The query-tracking
host label was not copied. No second SPF include was added.

The [AT&T Business DNS support article](https://www.att.com/support/smallbusiness/article/smb-internet/KM1188676/),
last updated December 7, 2022, tells the reader to list AT&T as
primary DNS with the registrar. It does not print an NS hostname
ending in `att.net`. DNS-lookup directories are not a vendor basis.

Campaign Monitor help articles for email authentication
troubleshooting and managing authentication returned the help center
CSS error shell and did not print an SPF record. The article body was
not available. A search index is not a vendor basis.

### Documented reference check, later on 2026-11-16, email, DNS, and events

This pass checked eight undated email, DNS, and event rules. None
received a `verified` date. No new detection, DNS record type, or
collection path was added. This note does not cut a release.

The [CISA BOD 18-01 page](https://www.cisa.gov/news-events/directives/bod-18-01-enhance-email-and-web-security)
prints an aggregate mailbox on the host `dmarc.cyber.dhs.gov`. That
host is narrower than the existing `dhs.gov` suffix, so that suffix
stays undated. The narrower host was not added. The page's other
example mailboxes were not copied.

The [Cloudflare DMARC Management enable page](https://developers.cloudflare.com/dmarc-management/enable/),
last updated May 5, 2026, says Cloudflare adds another rua using a
Cloudflare email address. It does not print that mailbox or a
reporting destination under `cloudflare.net`. The [email
authentication page](https://developers.cloudflare.com/email-service/concepts/email-authentication/),
last updated June 9, 2026, prints an example aggregate rua on the
reader's own domain and an SPF include of `_spf.mx.cloudflare.net`.
That include is not this `dmarc_rua` pattern and was not added. The
broader `cloudflare.net` suffix stays undated.

The [Cloudflare partial-setup page](https://developers.cloudflare.com/dns/zone-setups/partial-setup/setup/),
last updated July 29, 2026, prints a CNAME target of
`{your-hostname}.cdn.cloudflare.net`. It does not print
`pacloudflare.com`. The [China Network DNS page](https://developers.cloudflare.com/china-network/concepts/china-dns/),
last updated April 30, 2026, prints `cdn.cloudflareanycast.net` and
`cdn.cloudflarecn.net`, which are already dated sibling rules, and
does not print `pacloudflare.com`. A domain-directory page is not a
customer CNAME basis.

[Cisco document 223136](https://www.cisco.com/c/en/us/support/docs/security/cloud-email-security/223136-review-dmarc-reports-and-resolve.html),
updated June 23, 2025, describes Domain Protection hosting SPF, DKIM,
and DMARC records after the operator publishes TXT records that
delegate administration. It does not print the hostname
`dmp.cisco.com`. DNS-lookup directories are not a vendor basis.

The [Secure Email Threat Defense User Added Domains guide](https://docs.cmd.cisco.com/en/Content/secure-email-threat-defense-user-guide/Configuration%20Settings/Mail%20Flow%20Configuration/User%20Added%20Domains.htm)
says to copy the verification code from the product and create a TXT
record. It does not print `cisco-site-verification=`. It also names
regional hosts under `etd.cisco.com`. Those hosts are not this pattern
and were not added.

The Cvent community articles for the domains Cvent uses and for vanity
URL setup returned the community CSS error shell and did not print
`lwcal.com`. The article body was not available. A search index is
not a vendor basis.

The [Com Laude Managed DNS Service Terms](https://comlaude.com/app/uploads/2026/04/Com-Laude-Managed-DNS-Service-Terms-v1.4-2-April-2026.pdf),
version 1.4 dated 2 April 2026, say anycast DNS is subcontracted to
another provider. They do not print an NS hostname ending in
`comlaude-dns.com` or `comlaude-dns.co.uk`. The [Ask the Experts DNS
management page](https://comlaude.com/ask-the-experts-dns-management/)
also does not print those hosts. DNS-lookup directories are not a
vendor basis. The unadmitted `comlaude-dns.net` and `comlaude-dns.eu`
siblings were not dated.

### Documented reference check, later on 2026-11-16, DNS and email

This pass checked eight undated DNS and email rules. None received a
`verified` date. No new detection, DNS record type, or collection path
was added. This note does not cut a release.

The [Com Laude Managed DNS Service Terms](https://comlaude.com/app/uploads/2026/04/Com-Laude-Managed-DNS-Service-Terms-v1.4-2-April-2026.pdf),
version 1.4 dated 2 April 2026, say anycast DNS is subcontracted to
another provider. They do not print an NS hostname ending in
`comlaude-dns.eu` or `comlaude-dns.net`. The [Ask the Experts DNS
management page](https://comlaude.com/ask-the-experts-dns-management/)
also does not print those hosts. DNS-lookup directories are not a
vendor basis.

The Constant Contact article on adding addresses to an SPF record
returned a knowledge-base template shell and did not print an SPF
include. The article body was not available. A search index is not a
vendor basis. The broader `constantcontact.com` suffix stays undated.
A narrower include was not added.

The [Constellix registrar delegation guide](https://support.constellix.com/hc/en-us/articles/34573633265435-How-to-Point-Your-Registrar-to-a-New-DNS-Provider),
updated March 3, 2025, says to enter the nameservers assigned in the
product. It does not print an NS hostname ending in `constellix.com`
or `constellix.net`. The [SOA guide](https://support.constellix.com/hc/en-us/articles/34573686671259-Create-an-SOA-Record)
prints `dns.constellix.com` as the default administrator mailbox host.
That host is not an NS target and was not added. DNS-lookup
directories are not a vendor basis.

A documentation page for `cp-dmarc.com` was requested. The apex and
www host did not resolve, so no vendor page was available. Third-party
DMARC explainers are not a vendor basis.

The [CSC Domain Manager zone-management guide](https://www.cscglobal.com/cscglobal/pdfs/domains/Zone-Management-Process.pdf)
tells the operator to select a name server group and enter MX values.
It does not print `cscdns.net`. The [DNS Flag Day article](https://www.cscdbs.com/blog/dns-down-alert-for-dns-flag-day/)
says CSC DNS supports EDNS and does not print that host. DNS-lookup
directories are not a vendor basis.

### Documented reference check, later on 2026-11-16, DMARC reporting and DNS

This pass checked eight undated DMARC reporting and DNS rules. Two
received a `verified` date because the current vendor page prints the
grammar. Six stay undated. No new detection, DNS record type, or
collection path was added. This note does not cut a release.

The [DMARCLY rua article](https://www.dmarcly.com/blog/what-is-rua-in-dmarc-dmarc-rua-tag-explained),
dated 20 February 2024, prints an example aggregate rua whose mailbox
domain is `dmarcly.com`. The rule observes that mailbox domain. It
does not prove that reports are collected. The aggregate-reports
article prints a product mailbox on the narrower host `ag.dmarcly.com`.
That host was not added. Example and product local-parts were not
copied.

The [DNSimple name servers article](https://support.dnsimple.com/articles/dnsimple-nameservers/),
last updated October 26, 2026, says the name servers are
`ns1.dnsimple-edge.com`, `ns2.dnsimple-edge.net`,
`ns3.dnsimple-edge.io`, and `ns4.dnsimple-edge.org`. The rule observes
an NS host under `dnsimple-edge.com`. It does not prove that the zone
is delegated or that DNSimple is the only DNS provider. The sibling
suffixes were not dated in this pass. The specific `ns1` host was not
added as a separate rule.

The [Mimecast DMARC record guide](https://www.mimecast.com/content/how-to-create-a-dmarc-record/)
prints an aggregate rua on the host `for.dmarcanalyzer.com`. That host
is narrower than the existing `dmarcanalyzer.com` suffix, so that
suffix stays undated. The narrower host was not added. The placeholder
local-part was not copied.

The [DMARC Digests reporting-address article](https://support.dmarcdigests.com/article/1223-what-is-a-reporting-address),
last updated February 22, 2024, prints an aggregate rua on the host
`inbound.dmarcdigests.com`. That host is narrower than the existing
`dmarcdigests.com` suffix, so that suffix stays undated. The narrower
host was not added. The placeholder local-part was not copied.

The [DMARC/25 English product page](https://www.dmarc25.jp/index-en.html)
describes report analysis and does not print a DMARC record or an
aggregate rua. The site name is not the catalog grammar.

The `dmarc360.com` apex redirects to the [CTM360 email-intelligence page](https://www.ctm360.com/platform/email-intelligence-oversight).
That page uses DMARC360 as a product name and does not print the
hostname `dmarc360.com` or an aggregate rua. The contact mailbox is on
a different domain and was not used.

A documentation page for `dmarcinput.com` was requested. The apex and
www host did not resolve, so no vendor page was available. Third-party
explainers are not a vendor basis.

The [CSC managed DNS page](https://www.cscdbs.com/en/solutions/dns-services-ddos/)
describes managed DNS and does not print an NS hostname ending in
`cscdns.uk`. The zone-management guide also does not print that host.
DNS-lookup directories are not a vendor basis.

### Documented reference check, later on 2026-11-16, DNS providers

This pass checked eight undated DNS and SPF rules. All eight received
a `verified` date because the fetched vendor page prints the catalog
grammar. No new detection, DNS record type, or collection path was
added. This note does not cut a release.

The [DNSimple name servers article](https://support.dnsimple.com/articles/dnsimple-nameservers/)
lists `ns2.dnsimple-edge.net`, `ns3.dnsimple-edge.io`, and
`ns4.dnsimple-edge.org` beside the already dated `.com` suffix. Each
rule observes an NS host under its suffix. None proves that the zone
is delegated or that DNSimple is the only DNS provider. The specific
hosts were not added as separate rules.

The [DigiCert DNS nameserver transition article](https://support.dnsmadeeasy.com/hc/en-us/articles/34327239032603-DigiCert-DNS-Nameserver-Transition),
updated February 24, 2025, lists legacy DNS Made Easy name servers,
including `ns0.dnsmadeeasy.com` and `ns1.dnsmadeeasy.com`, and says
those legacy names continue to operate. The rule observes an NS host
under `dnsmadeeasy.com`. Addresses on the page were not copied. The
specific hosts were not added as separate rules.

The [DNSPod domain-change article](https://docs.dnspod.cn/dns/dns-domain-change/),
last updated August 25, 2025, lists `ns3.dnsv5.com` and
`ns4.dnsv5.com` for the premium plan. The rule observes an NS host
under `dnsv5.com`. The specific hosts were not added as separate
rules.

The [Docebo domain-management article](https://help.docebo.com/hc/en-us/articles/14651659200402-Domain-management-DNS-and-SSL-configuration-requirements),
last updated June 3, 2026, prints `include:docebosaas.com`. The rule
observes that include. It does not prove that Docebo sends mail for
the domain.

The [easyDNS nameserver page](https://easydns.com/our-nameservers/)
lists `DNS1.EASYDNS.COM` and `DNS3.EASYDNS.ORG` as current nameserver
constellations. Each rule observes an NS host under its suffix. The
specific hosts were not added as separate rules. `easydns.net` and
`easydns.info` on the same page were not dated in this pass.

### Documented reference check, later on 2026-11-16, email and DNS

This pass checked eight undated email and DNS rules. One received a
`verified` date because the fetched vendor page prints the catalog
grammar. Seven stayed undated. No new detection, DNS record type, or
collection path was added. This note does not cut a release.

The [easyDNS nameserver page](https://easydns.com/our-nameservers/)
lists `DNS2.EASYDNS.NET` as a current nameserver constellation. The
rule observes an NS host under `easydns.net`. It does not prove that
the zone is delegated or that easyDNS is the only DNS provider. The
specific host was not added as a separate rule. `easydns.info` on the
same page was not dated in this pass.

The [Elastic Email domain-verification article](https://help.elasticemail.com/en/articles/4934400-how-to-verify-your-domain)
prints `include:_spf.elasticemail.com`. That host is narrower than
the existing `elasticemail.com` suffix. The broader suffix stays
undated. The narrower host was not added.

The [Oracle Eloqua email-authentication page](https://docs.oracle.com/en/cloud/saas/marketing/eloqua-user/Help/Deliverability/EmailSendingDomainSubdomain.htm)
describes SPF and does not print an include for `eloqua.com`.
Third-party SPF guides are not a vendor basis. The Oracle knowledge
article is behind a sign-in.

The apex and `www` host for `emailanalyst.com` did not resolve, so
no vendor page was available. This is not a source check.
Third-party explainers and DNS-lookup directories are not a vendor
basis.

The [Emma SPF setup article](https://help.myemma.com/s/article/spf-authentication-setup)
was requested and the fetched page did not return the article body.
A search snippet is not a vendor basis.

The [Etisalat domain pages](https://www.nic.ae/) describe domain
registration and DNS management and do not print an NS hostname
ending in `etisalatdomains.ae`.

The [Everbridge custom-from article](https://supportcenter.everbridge.com/hc/en-us/articles/19141627397659-EBS-Emails-Not-Being-Received-From-Everbridge-Suite-When-Custom-From-Email-Address-Is-Configured)
was requested. The fetched page is a support sign-in wall and does
not print `include:everbridge.net`. A sign-in wall is not a vendor
basis.

The [Exclaimer SPF article](https://support.exclaimer.com/hc/en-gb/articles/4404775962641-How-to-update-the-Sender-Policy-Framework-SPF)
prints `include:spf.<region>.exclaimer.net`. It does not print
`emailsignatures365.com`. The regional host is a different suffix
and was not added.

### Documented reference check, later on 2026-11-16, nameservers and mail

This pass checked eight undated nameserver, MX, and SPF rules. Six
received a `verified` date because the fetched vendor page prints the
catalog grammar. Two stayed undated. No new detection, DNS record
type, or collection path was added. This note does not cut a release.

The [F5 Distributed Cloud DNS quickstart](https://docs.cloud.f5.com/docs-v2/dns-management/quickstart/dns-services)
says to add nameservers `ns1.f5clouddns.com` and `ns2.f5clouddns.com`.
The rule observes an NS host under `f5clouddns.com`. It does not prove
that the zone is delegated or that F5 is the only DNS provider. The
specific hosts were not added as separate rules.

The [Fastmail MX setup article](https://www.fastmail.help/hc/en-us/articles/1500000280261-Setting-up-your-domain-MX-only)
says to set MX records to `in1-smtp.messagingengine.com` and
`in2-smtp.messagingengine.com`. The rule observes an MX host under
`messagingengine.com`. It does not prove that mail is delivered or
that Fastmail is the only exchanger. The specific hosts were not
added. The SPF include `spf.messagingengine.com` on the same page
was not added.

The [FortiMail Cloud Microsoft 365 MX guide](https://fortinetweb.s3.amazonaws.com/docs.fortinet.com/v2/attachments/b35ad4f6-bef7-11ee-8673-fa163e15d75b/FortiMail_Cloud_Integration_with_Microsoft_365_Using_MX_Records.pdf),
last updated April 16, 2026, prints example MX targets under
`fortimailcloud.com`. The rule observes an MX host under that suffix.
It does not prove that mail is routed through FortiMail or that
FortiMail is the only exchanger. The example tenant labels were not
added. The SPF include `_spf.fortimailcloud.com` on the same page was
not added.

The [Cloudflare nameserver documentation](https://developers.cloudflare.com/dns/nameservers/),
last updated October 14, 2026, says advanced nameservers are hosted
on `foundationdns.com`, `foundationdns.net`, and `foundationdns.org`,
and that each zone is assigned a color host under each suffix. Each
rule observes an NS host under its suffix. None proves that the zone
is delegated or that Cloudflare is the only DNS provider. The color
host was not added as a separate rule.

The same [Exclaimer SPF article](https://support.exclaimer.com/hc/en-gb/articles/4404775962641-How-to-update-the-Sender-Policy-Framework-SPF)
prints `include:spf.<region>.exclaimer.net`. That host is narrower
than the existing `exclaimer.net` suffix, so that suffix stays
undated. The regional host was not added.

The [Freshservice SPF article](https://support.freshservice.com/support/solutions/articles/193639-creating-an-spf-record)
prints `include:email.freshservice.com`. That host is narrower than
the existing `freshservice.com` suffix, so that suffix stays undated.
The narrower host was not added.

### Documented reference check, later on 2026-11-16, nameservers, mail, and reporting

This pass checked eight undated nameserver, MX, SPF, DMARC, and TXT
rules. Five received a `verified` date because the fetched vendor page
prints the catalog grammar. Three stayed undated. No new detection,
DNS record type, or collection path was added. This note does not cut
a release.

The [Gandi secondary nameserver documentation](https://docs.gandi.net/en/domain_names/advanced_users/secondary_nameserver.html)
says Gandi's secondary DNS is `ns6.gandi.net` and that the operator
must declare `ns6.gandi.net` as an NS at the apex. The rule observes
an NS host under `gandi.net`. It does not prove that the zone is
delegated or that Gandi is the only DNS provider. The specific host
was not added. Glue addresses on the page were not copied.

The [GoDaddy Professional Email DNS article](https://www.godaddy.com/help/what-are-my-dns-settings-for-professional-email-powered-by-titan-42767)
says the MX records are the same for all users:
`smtp.secureserver.net` at priority 0 and
`mailstore1.secureserver.net` at priority 10. The rule observes an MX
host under `secureserver.net`. It does not prove that mail is
delivered or that GoDaddy is the only exchanger. The specific hosts
were not added.

The [GoDaddy SPF article](https://www.godaddy.com/help/add-an-spf-record-19218)
says the SPF value must be `v=spf1 include:secureserver.net -all` for
the listed GoDaddy mail products. The rule observes that include. It
does not prove that mail is sent or that GoDaddy is the only sender.
No second include was added.

The [GoDaddy DKIM, DMARC, and SPF article](https://www.godaddy.com/help/what-is-dkim-dmarc-and-spf-24605)
prints a default DMARC record whose rua mailbox is at
`onsecureserver.net`. The rule observes an aggregate rua host under
that suffix. It does not prove that reports are delivered or that
GoDaddy is the only reporting destination. The mailbox local-part was
not added.

The [Squarespace nameserver article](https://support.squarespace.com/hc/en-us/articles/4404183898125-Review-change-or-reset-your-domain-s-nameservers),
last updated September 17, 2026, says Squarespace default nameservers
may end in `.googledomains.com`. The rule observes an NS host under
that suffix. It does not prove that the zone is delegated, that
Google Domains is the registrar, or that Squarespace is the only DNS
provider. The other suffixes named on that page were not added.

The [GitHub organization domain verification documentation](https://docs.github.com/en/organizations/managing-organization-settings/verifying-or-approving-a-domain-for-your-organization)
tells the operator to follow on-screen TXT instructions and does not
print `github-verification=`. The Pages verification article prints a
different challenge name. That name was not added. The catalog TXT
stays undated.

The [GlockApps DMARC help article](https://help.glockapps.com/art/multiple-dmarc-records/),
updated March 5, 2025, prints a generated aggregate rua at
`ar.glockapps.com`. That host is narrower than the existing
`glockapps.com` suffix, and the local-part is account-specific. A tag
glossary uses a mailbox at `glockapps.com` as a syntax example. The
broader suffix stays undated. The narrower host and the account
local-part were not added.

The [GoDaddy nameserver help](https://www.godaddy.com/help/find-my-godaddy-nameservers-12318)
does not print `gdnsdef.com` or any nameserver hostname. Registry and
DNS-directory pages are not a vendor basis. The suffix stays undated.
No nameserver host was added.

### Documented reference check, later on 2026-11-16, mail, SPF, and custom DNS

This pass checked eight undated MX, TXT, SPF, and CNAME rules. Three
received a `verified` date because the fetched vendor page prints the
catalog grammar. Five stayed undated. No new detection, DNS record
type, or collection path was added. This note does not cut a release.

The [Help Scout SPF article](https://docs.helpscout.com/article/58-spf-records),
updated January 30, 2024, prints `include:helpscoutemail.com` as the
SPF entry that can be removed. The rule observes that include. It
does not prove that Help Scout sends mail or that the include is
still required.

The [Heroku TLS article](https://devcenter.heroku.com/articles/understanding-tls-on-heroku),
last updated September 30, 2024, says ACM DNS targets end with
`herokuspace.com` for Private Spaces apps. The custom domains article,
last updated June 7, 2026, says Cedar Private Spaces use a DNS target
ending in that suffix. The rule observes a CNAME target under
`herokuspace.com`. It does not prove that the app runs in a Private
Space or that this target is the only route. The example host was not
added.

The [Hornetsecurity Vade Cloud migration article](https://support.hornetsecurity.com/hc/en-us/articles/45997388779537-Migration-for-Vade-Cloud-Customers),
updated October 13, 2026, prints MX hosts under `hornetsecurity.com`.
The rule observes an MX host under that suffix. It does not prove
that mail is delivered or that Hornetsecurity is the only exchanger.
The specific hosts were not added.

The [Google Workspace MX article](https://knowledge.workspace.google.com/admin/domains/set-up-mx-records-for-google-workspace)
prints `smtp.google.com`. The legacy note says older values start
with `aspmx` and does not print `googlemail.com`. That different
suffix was not added. The catalog MX stays undated.

The [Google Workspace password-recovery article](https://knowledge.workspace.google.com/admin/domains/recover-your-google-workspace-password-with-a-cname-record)
tells the operator to add a unique CNAME whose destination is
`google.com`. It does not print
`google-gws-recovery-domain-verification=`. The domain TXT
verification article prints `google-site-verification=`, a different
prefix. The example label and token were not copied. The catalog TXT
stays undated.

The [Google Workspace business-email unlock article](https://knowledge.workspace.google.com/admin/domains/verify-your-domain-to-unlock-features-for-business-email-accounts)
says to follow the verification tool. It does not print
`work-accounts-domain-verification=`. The same TXT article prints a
different prefix. The example token was not copied. The catalog TXT
stays undated.

The [Greenhouse Mailgun update article](https://support.greenhouse.io/hc/en-us/articles/24674627688475-Greenhouse-Mailgun-Updates-April-2024),
last updated April 10, 2024, prints `include:mg-spf.greenhouse.io`.
That host is narrower than the existing `greenhouse.io` suffix, so
that suffix stays undated. The narrower host was not added.

The [Heroku custom domains article](https://devcenter.heroku.com/articles/custom-domains),
last updated June 7, 2026, says Heroku does not explicitly verify
domain ownership when a domain is added. It does not print
`heroku-domain-verification=`. The catalog TXT stays undated.

### Documented reference check, later on 2026-11-16, mail and verification

This pass checked eight undated MX, NS, SPF, DMARC, and TXT rules.
One received a `verified` date because the fetched vendor page prints
the catalog grammar. Seven stayed undated. No new detection, DNS
record type, or collection path was added. This note does not cut a
release.

The [Apple custom email domain article](https://support.apple.com/en-us/102374),
published November 3, 2026, prints MX hosts `mx01.mail.icloud.com` and
`mx02.mail.icloud.com`. The rule observes an MX host under
`icloud.com`. It does not prove that mail is delivered or that iCloud
Mail is the only exchanger. The specific hosts were not added. The
SPF include on the same page was not added.

The [Iberlayer Email Guardian page](https://www.iberlayer.com/es/email-guardian)
says to change the company MX records. The diagram prints
`mx1.emailguardian.` and `mx2.emailguardian.` beside a placeholder
customer name. It does not print an MX host under `iberlayer.com`.
The contact mailbox is not an MX record. Those diagram hosts were not
added. The catalog MX stays undated.

The [Thales Imperva basic managed DNS page](https://docs-cybersec.thalesgroup.com/bundle/cloud-application-security/page/dns-basic-managed.htm)
does not print `impervasecuredns.net`. The indexed article says to
update name servers supplied in the console. Registry and
DNS-directory observations are not a vendor basis. No nameserver host
was added. The catalog NS stays undated.

The [InboxMonster help center](https://inboxmonster.com/help-center)
discusses DMARC setup and says reports go to the specified email
addresses. It does not print an aggregate rua host under
`inboxmonster.com`. No mailbox was added. The catalog rua stays
undated.

The [Intercom email support article](https://www.intercom.com/help/en/articles/9744849-connect-your-email-support-channel)
says to add CNAME and TXT records supplied by the product. It does
not print `intercom-domain-validation=`. Help Center hosts under
`intercom.help` and `intercomhelpcenter.com` were not added. The
catalog TXT stays undated.

The [Ipreo terms of use](https://irm.ipreo.com/App_Themes/Login/TermsOfUse.html)
discuss email sent through the product and do not print
`include:ipreomail.com`. A third-party SPF guide is not the vendor
page. The include host was not added. The catalog SPF stays undated.

The [Lumen advanced domain setup article](https://docs.lumen.com/application-delivery-solutions/advanced-domain-setup/)
describes changing registrar name servers and does not print
`level3.net`. DNS-directory observations are not a vendor basis. No
nameserver host was added. The catalog NS stays undated.

The [Atlassian Loom TXT article](https://support.atlassian.com/loom/kb/add-a-dns-text-record/),
updated October 16, 2025, prints `loom-site-verification=` with an
example token. It does not print `loom-verification=`. That is a
different prefix. The example token was not copied, and the other
prefix was not dated in this pass. The catalog TXT stays undated.

## Executable path

Run from the checkout root. The strict plan schemas and specialized rank,
ccTLD, provider-seed, and drift examples live in
[validation/README.md](../validation/README.md). Inspect the selected command's
`--help`; do not apply one round's flags or schema to another.

The generic offline preparation step is:

```text
uv run python -m validation.prepare_catalog_round --plan validation/corpus-private/round-plan.json --output-corpus validation/corpus-private/round-frame.txt --output-manifest validation/corpus-private/round-manifest.json
```

Only after the corpus and collection are approved and frozen, use
`uv run python -m validation.scan` with `--corpus`, `--round-kind`, and
`--round-manifest`. Match `--ct` to the plan; the runner defaults to CT off.
Pass the frozen recurrence threshold as `--min-count` and declared parallelism
as `--concurrency`. Independent non-drift rounds use `--no-compare` unless an
exact prior comparison was declared; otherwise scan selects the latest local
run. Drift instead requires its explicit prior and comparison sidecar.
It creates the pooled typed baseline. Existing-result stratification uses
`validation.stratify_catalog_round` with the original `--round-plan`,
`--round-manifest`, `--input`, `--pooled-aggregate`, and private `--output-dir`.
Neither evaluation nor triage silently triggers another collection.
Candidate review alone can use an existing artifact without a full frozen
bundle, while explicitly withholding independent or contract-bound evaluation
claims. Review-only tasks produce findings and proposed patches, not catalog
mutations; unrun local gates and CI are `not checked`, never implicitly passed.

### What the promotion evaluator establishes

`validation.evaluate_catalog_promotions` is deliberately narrower than the
runtime detector. It reclassifies retained unmatched values using built-in
`match_mode: any` DNS-suffix rules in `cname_target`, `mx`, `ns`, and `spf`.
It rejects conjunctions and operator-local candidates. Reports retain the
canonical YAML digest and an additional digest of the exact normalized rules
evaluated. They do not bind a full service-selection counterfactual.

Its additive classified-count arithmetic cannot decrease by construction.
Therefore a zero-regression result does not establish absence of false
attribution, provider displacement, or misleading service claims. `accepted`
means that every requested candidate slug added a classification, each affected
pooled record type met the numeric minimum improvement, and every record type
met the numeric regression budget. Decisions use unrounded count ratios;
displayed rates remain rounded. The report and CLI identify this scope as
`pooled-classification-diagnostic` and mark policy text `not_evaluated`.
Private `metric` and `decision_rule` prose is digest-bound, not executed or
printed. Baseline recurrence thresholds do not become per-candidate acceptance
tests, and per-stratum policy still needs separate review. These checks do not
establish that every promotion gate passed. Other record types and conjunctions
need dedicated detector tests and a separately supported validation route.
Do not convert `all` to `any` merely to pass the evaluator.

Exclusion inputs accept a UTF-8 byte-order mark while commitments retain the
original bytes. Current execution digests include rank selection and its shared
sampling helpers. A changed implementation requires a new compatible collection
commitment; historical manifests and results retain their original digests.

Run focused tests, `uv run python scripts/generate_fingerprint_catalog.py --write`
when catalog source changes, and `uv run python -m validation.audit_fingerprints
--freshness`. Finish with `uv run --frozen python scripts/check.py` and the
hosted CI matrix for the exact proposed revision. Do not lower floors or
regenerate expected outcomes to conceal a regression.

The audit defaults to the canonical built-in catalog. Its explicit
`--effective-catalog` mode includes operator-local rules and is labeled as such;
do not publish that output without disclosure review or confuse it with a
reproducible built-in baseline.

## Optional model-assisted proposals

The existing `validation/triage_llm.py` helper is optional, developer-only and
not required by these skills or the recon runtime. Explicit invocation sends
the supplied private candidate data to the configured external model. Do not
run it without the operator's data-sharing and cost approval; environment-held
credentials are not approval. The normal recon runtime has no model dependency.

The helper reads the canonical built-in inventory and requires exactly one
valid response for each candidate before writing anything. It rejects missing,
duplicate, unexpected and malformed rows, inconsistent same-slug metadata, and
unsupported patterns. These are structural checks, not independent provider
verification or a precision estimate.

Its `--yaml` output is now a versioned `recon-private-fingerprint-proposals`
envelope marked `PENDING PRIVATE`, not directly loadable catalog YAML. It does
not assign confidence or a verification date. Same-slug detections are retained
without silently discarding later patterns. Existing destinations are never
overwritten. In-repository inputs and outputs must use ignored private roots;
the shared path policy also permits operator-local paths outside the checkout.
Reports, proposed patterns and optional validated-response files all require
disclosure review before sharing. A model-supplied reference is still unverified.

The separate [platform review](agent-platform-research.md) explains why strict
result validation and artifact-backed resumption are useful before introducing
another harness or model provider. No new platform adapter is required for this
correction, and all its regression tests are offline.

## Review claims before growing the catalog

A useful maintenance round can remove an unsupported rule, narrow a target,
or correct a product claim without adding any services. The
[September 2026 claim review](../validation/2026-09-05-catalog-claim-review.md)
records concrete owner/value confusion, overbroad routing attribution,
unsupported plan claims, and a retired hosting surface. The separate
[documented CNAME review](../validation/2026-09-05-documented-cname-review.md)
records the bounded Retool and Postmark follow-up, exact-target fixtures and
remaining integration gates. Synthetic contract checks are not accuracy gains.

For each candidate, keep separate answers for: what was published, where it
was published, which provider documents that grammar, what the route or token
can support, and what remains unobserved. A public verification token is not
proof that verification completed. A provider domain is not a product plan.
Retirement metadata is not evidence that a legacy endpoint still responds.
The strongest maintainable catalog is the one whose positive and withheld
claims are both testable.

## Research basis and limits

These are design implications for recon, not measured improvements to recon's
accuracy or permission to expand its collection surface:

- Top-list selection and date can materially change Internet measurements.
  Preserve the exact frame and report results for that frame. [A Long Way to
  the Top, IMC 2018](https://arxiv.org/abs/1805.11506).
- Reproducible, manipulation-hardened rankings improve repeatability but do not
  turn equal rank quotas into a representative population sample.
  [Tranco, NDSS 2019](https://arxiv.org/abs/1806.01156).
- Separation across development, evaluation, and time guards against optimistic
  evaluation. This is a methodological analogy from malware classification,
  not a recon accuracy result. [TESSERACT, USENIX Security
  2019](https://www.usenix.org/conference/usenixsecurity19/presentation/pendlebury).
- Heuristic evidence sources can overlap, conflict, and correlate. Preserve
  their derivation and do not count repeated evidence as independent labels.
  This motivates dependency-aware review, not adopting a learned label model.
  [Snorkel, 2017](https://arxiv.org/abs/1711.10160).
- Abstention should be visible beside coverage and errors on appropriately
  labeled cases. Statistical risk guarantees require a suitable labeled
  sampling setup; recon's confidence tiers do not supply it. [Selective
  Classification, NeurIPS 2017](https://arxiv.org/abs/1705.08500).

Learned weak supervision, retuned priors, and conformal guarantees remain
research proposals until a defined claim, independent labels, a frozen loss,
and defensible sampling/dependence assumptions exist. More matches alone do
not justify them. An unavailable observation, an unsupported pattern, or a
deferred promotion is often the most accurate result.
