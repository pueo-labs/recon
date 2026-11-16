# Draft Optional Google Cloud Run Reference

This Terraform root module is the first optional scale-to-zero reference for
recon. Google publishes specific guidance for hosting Streamable HTTP MCP
servers on Cloud Run, and Cloud Run matches recon's existing Python container
without a function-framework rewrite.

Nothing here is required for local use. Nothing deploys automatically. The
operator supplies a Google Cloud project, region, immutable image digest,
authentication choice, and billing approval, then owns the resulting service.

Status: draft intended to be directionally useful. Terraform formatting,
initialization, and schema validation pass, and the referenced container passes
local build and MCP smoke checks. This module has not yet been applied and
validated through a real Cloud Run project under this plan's promotion gate.
It is not production-ready or a claim that IAM, secret injection, quotas,
autoscaling, billing, logging, rollback, and deletion have been exercised end
to end.

## Maturity boundary

Locally checked:

- Terraform formatting and provider-schema validation with the lockfile
- Immutable image-reference input validation
- Linux container build, health response, authentication rejection, and MCP
  initialization
- Unit coverage for the application security boundary

Still required in a non-production Google Cloud project:

- Review and apply against the exact project, region, organization policy, and
  identities
- Verify both access modes through the managed ingress
- Measure cold and warm behavior, concurrency, quotas, and bounded cost
- Inspect query-bearing logs and set access and retention deliberately
- Rotate the secret version and roll back the immutable image
- Confirm a no-change second plan, deletion protection, and reviewed removal

Until those steps are recorded, keep calling this a draft reference.

## What it creates

- Required Google APIs
- One dedicated service account with no project roles
- One Cloud Run v2 service with minimum instances zero by default
- A bounded maximum of three instances and concurrency eight by default
- Startup and liveness probes against `/health`
- Optional Secret Manager access to one existing bearer-token secret
- Either a public Cloud Run invoker plus application bearer auth, or named
  Google IAM invokers plus trusted platform auth

The module does not create an Artifact Registry repository, a secret value, an
OAuth provider, a domain, a load balancer, or a monitoring project. Those are
organization-level choices and should not be silently inferred.

## Choose the access mode

`application-bearer` is the default interoperability mode. Cloud Run's network
invoker is public, but the application rejects every `/mcp` request without the
Secret Manager backed bearer. This mode works with remote AI clients that can
send a static authorization header. It is suitable for a trusted individual or
team, not a public multi-tenant service. Because an unauthenticated request can
still start an instance before the application rejects it, keep the maximum
instance bound, budgets, and alerts in place. Put a reviewed gateway and
identity-aware rate limit in front before broader exposure.

`google-iam` keeps the Cloud Run invoker private and grants only the members in
`invoker_members`. The container trusts that outer identity boundary. Use it
for Google-hosted agents, service-to-service calls, or a local Cloud Run proxy.
It is not directly usable by an AI service that cannot mint a Google ID token.

Per-user Claude or ChatGPT plugin access needs an OAuth 2.1 compatible gateway
and authorization server. That is a later, separately gated layer in the
[cross-platform plan](../../docs/optional-cloud-deployment-plan.md).

## Prerequisites

- Terraform 1.8 or newer. The Google provider constraint is `>= 8.0, < 9.0`.
- Google Cloud credentials authorized to enable APIs, create the service and
  service account, and manage the named IAM bindings
- An existing Artifact Registry repository and pushed `linux/amd64` image
- In `application-bearer` mode, an existing Secret Manager secret containing a
  random token of at least 32 bytes
- A selected region based on residency, latency, quota, and organization policy

Build and push the container from the repository root. Tag it for traceability,
then resolve and pass its immutable registry digest to Terraform:

```powershell
docker build --platform linux/amd64 --file deploy/container/Dockerfile --tag $ImageTag .
docker push $ImageTag
gcloud artifacts docker images describe $ImageTag --format="value(image_summary.digest)"
```

Create the secret outside Terraform so its value never enters Terraform state.
For example, after creating an empty secret named `recon-mcp-bearer`, add a
version through standard input:

```powershell
$token = [Convert]::ToBase64String([Security.Cryptography.RandomNumberGenerator]::GetBytes(48))
$token | gcloud secrets versions add recon-mcp-bearer --data-file=-
Remove-Variable token
```

Record the numeric version returned by Secret Manager. Do not use `latest` for
an environment-variable secret because a revision should resolve one reviewed
version consistently.

## Plan and apply

Create an untracked `terraform.tfvars` or pass variables through the operator's
normal automation. It contains identifiers, never the secret value:

```hcl
project_id            = "example-project"
region                = "us-central1"
container_image       = "us-central1-docker.pkg.dev/example-project/tools/recon@sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
access_mode           = "application-bearer"
bearer_secret_id      = "recon-mcp-bearer"
bearer_secret_version = "1"
max_instances         = 3
```

Then run:

```powershell
terraform -chdir=deploy/gcp-cloud-run init
terraform -chdir=deploy/gcp-cloud-run fmt -check
terraform -chdir=deploy/gcp-cloud-run validate
terraform -chdir=deploy/gcp-cloud-run plan -out=recon.tfplan
terraform -chdir=deploy/gcp-cloud-run apply recon.tfplan
```

Review the plan for the exact project, region, image digest, public IAM member,
secret ID and version, instance bounds, and service account before applying.
The output `mcp_url` is the endpoint for the chosen client.

For Google IAM mode, omit the secret variables and set explicit members:

```hcl
access_mode = "google-iam"
invoker_members = [
  "serviceAccount:agent@example-project.iam.gserviceaccount.com",
]
```

## Verification and rollback

After apply:

1. Confirm `/health` returns 200.
2. Confirm `/mcp` without the required identity returns 401 or 403.
3. Use MCP Inspector or the intended client to initialize, list tools, read one
   catalog resource, and call a reserved-domain lookup.
4. Confirm mutating tools such as `reload_data` and
   `inject_ephemeral_fingerprint` are absent.
5. Confirm max instances, request timeout, secret version, log retention, cost
   budget, and alerting in the deployed project.

Rollback by applying the previous immutable image digest and secret version.
Deletion protection defaults to true. A deliberate destroy requires first
setting it false and applying that change, then reviewing a separate destroy
plan.

## Source basis

This reference was checked on 2026-07-28 against Google's current
[Cloud Run MCP hosting guide](https://docs.cloud.google.com/run/docs/host-mcp-servers),
[concurrency guidance](https://docs.cloud.google.com/run/docs/about-concurrency),
[request timeout contract](https://docs.cloud.google.com/run/docs/configuring/request-timeout),
[Secret Manager integration](https://docs.cloud.google.com/run/docs/configuring/services/secrets),
and [health-check guidance](https://docs.cloud.google.com/run/docs/configuring/healthchecks).
