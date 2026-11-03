# Agentic UX validation harness

**Audience:** recon maintainers running bridge-milestone validation for
the v1.9.x to v2.0 schema lock. End users running `recon example.com` do
not need this directory and do not need an LLM API key. The default
recon CLI never calls an LLM.

## What this exists for

The roadmap (`docs/roadmap.md` → v1.9.2) states that one of recon's
primary user personas *is* the AI agent: the MCP server is a real
production surface, and an agent reading recon JSON is a first-class
consumer. v1.9.2 is the bridge milestone that validates whether the
v1.9 fusion fields (`posterior_observations`, `slug_confidences`,
model-relative uncertainty bands, `sparse=true` flags) are actually used by
that audience, meaning whether agents read them, cite them, and let them
change a conclusion.

The harness drives three persona prompts (security analyst,
due-diligence researcher, ops engineer) across two committed fixtures
(`synthetic-dense.json` for a populated lookup; `synthetic-sparse.json`
for a deliberately-thin lookup) under fusion-on and fusion-off arms,
records transcripts, scores them against five binary checks, and
produces a self-contained markdown report under the gitignored
`validation/agentic_ux/local/` directory. The sanitized historical
aggregate at `validation/v1.9.2-agentic-ux.md` records the original
schema-lock disposition without retaining transcripts or target rows.

## Why it makes recon better

The harness produces *evidence* for or against design choices that
otherwise rely on intuition:

- Whether a posterior field is read or skipped under each persona's
  framing.
- Whether `sparse=true` actually causes an agent to hedge, or whether
  it gets parsed into the JSON tree and ignored.
- Whether the affordance to escalate (`--explain-dag`,
  `explain_dag` MCP tool) is discoverable from the JSON alone.

Each finding maps to a concrete v2.0 decision: keep the field as is,
rename, de-emphasize in the panel, expose a pointer field, or drop.
Without the harness, those decisions would be guesses. With it, they
are falsifiable.

## When to run it

- Before a v1.9.x bridge patch that proposes a schema-affecting
  change to fusion output. The harness baseline tells you which
  fields the change is moving.
- Before v2.0 schema lock, with at least two providers, so the
  finding pattern isn't single-vendor specific.
- When evaluating a new persona shape (e.g. when designing the v2.1
  closed-loop fingerprint-mining UX).

## What you need

1. Use the repository's locked `agentic-validation` dependency group. It pins
   `anthropic==0.120.2` and `openai==2.52.0` in `pyproject.toml`, with artifact
   hashes captured in `uv.lock`. These are not runtime dependencies of recon
   and are installed only when the group is selected.
2. The matching API key in your environment:
   - `ANTHROPIC_API_KEY` for Anthropic
   - `OPENAI_API_KEY` for OpenAI
   - `XAI_API_KEY` for xAI Grok
   - `OPENROUTER_API_KEY` for OpenRouter
   - `GEMINI_API_KEY` for Google Gemini
   - (No key required for local models via Ollama, vLLM, LM Studio)
3. The fixtures and personas in this directory (already committed).

## Running it

```bash
# Default provider and model, with provider charges
uv run --group agentic-validation python -m validation.agentic_ux.run

# Lower-cost model option
uv run --group agentic-validation python -m validation.agentic_ux.run --model claude-haiku-5-5

# OpenAI
uv run --group agentic-validation python -m validation.agentic_ux.run --provider openai --model gpt-5.6-sol

# xAI Grok
uv run --group agentic-validation python -m validation.agentic_ux.run --provider xai --model grok-4.7

# OpenRouter
uv run --group agentic-validation python -m validation.agentic_ux.run --provider openrouter --model anthropic/claude-sonnet-5-5

# Google Gemini
uv run --group agentic-validation python -m validation.agentic_ux.run --provider google --model gemini-3.5-flash-lite

# Local model
uv run --group agentic-validation python -m validation.agentic_ux.run --provider local --model llama3

# Subset of personas / fixtures
uv run --group agentic-validation python -m validation.agentic_ux.run --personas analyst,ops --fixtures synthetic-dense
```

Pricing was checked on 2026-11-03 against the provider pages linked in
`providers.py`. Each row records that date. The dollar amount multiplies
provider-reported token counts by the row, so a stale row mis-states the
estimate. Reports distinguish unknown prices from explicit zero prices.
Use `--input-price` and `--output-price` together for routed OpenRouter
IDs, cache or regional premiums, or prices outside the table. A one-sided
pair is rejected. `grok-4.7` and `grok-4.3` use their published long-context
rate once the prompt reaches 200,000 tokens, and `claude-haiku-5-5` uses
its higher rate once the prompt exceeds 100,000 tokens. Local provider runs
report zero API charges by default; hardware and hosting costs are outside
this estimate.
`--base-url` overrides any OpenAI-compatible provider endpoint. The same
provider names, key variables and endpoint overrides apply to
`validation/triage_llm.py`; its private report records the provider and model.

The runner writes the report to
`validation/agentic_ux/local/report.md` by default. `--output` and
`--records-json` accept paths outside the repository or under the
gitignored `validation/agentic_ux/local/` and
`validation/agentic_ux/runs/` directories. Other in-repository paths
are rejected before provider initialization.

## Privacy and data discipline

Everything in this directory respects the project's
no-real-company-data invariant (see `validation/README.md` →
Policy):

- Both fixtures use explicit synthetic identities under the reserved
  `.invalid` namespace.
- Persona prompts and neutral fixtures are committed. Transcripts,
  provider metadata, and raw run records stay local and gitignored.
- API keys never get committed or passed on the command line. The harness reads
  only provider-specific environment variables and does not log or embed them
  in the report.
- Keep every run output under `validation/agentic_ux/runs/` or
  `validation/agentic_ux/local/`, both of which are gitignored.

## What this is NOT

- **Not a runtime dependency of recon.** The default recon CLI does
  not call an LLM, does not require any API key, and does not
  import this directory.
- **Not a replacement for human operator interviews.** The roadmap
  v1.9.2 milestone keeps human interviews as a future option; the
  agentic harness is one persona class (the AI-agent persona),
  validated reproducibly. A SOC analyst clicking through the CLI
  is a different signal that this harness does not capture.
- **Not autonomous self-improvement.** The harness measures; humans
  decide. The findings are recommendations to a human curator, not
  auto-applied changes to recon's behavior.
