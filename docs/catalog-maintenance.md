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
reference check. It is a bounded
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
