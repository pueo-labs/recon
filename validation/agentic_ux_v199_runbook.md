# Agentic UX runbook for v1.9.9 surfaces

The v1.9.2 agentic UX harness at `validation/agentic_ux/run.py`
validates that AI agents read the panel correctly. v1.9.9 added two
new panel surfaces (Multi-cloud rollup, Passive-DNS ceiling) that
the v1.9.2 evidence does not cover. This runbook is the
maintainer's recipe for re-running the harness against v1.9.9
panels with the smallest LLM footprint and clearest output.

The harness needs an LLM API key; recon itself does not. Keep the
operational boundary clean. This is optional paid validation and must not run
without explicit budget approval.

## Smallest-cost invocation

The default harness runs 3 personas × 2 fixtures × 2 fusion modes
= 12 sessions × ~2K tokens each. To minimize cost while still
covering the v1.9.9 surfaces, run a focused subset:

```bash
# Set AGENTIC_UX_PROVIDER and AGENTIC_UX_MODEL to a currently available
# low-cost instruction-following model before running.
# One persona against the dense compatibility fixture
uv run --group agentic-validation python -m validation.agentic_ux.run \
    --provider "$AGENTIC_UX_PROVIDER" \
    --model "$AGENTIC_UX_MODEL" \
    --personas analyst \
    --fixtures synthetic-dense \
    --max-tokens 1024 \
    --output validation/agentic_ux/local/v1.9.9-update.md
```

Rough cost envelope at `claude-haiku-5-5` standard rates for prompts up to
100,000 tokens, checked 2026-11-03, omitting cache and regional premiums:
- 1 persona x 1 fixture x 2 modes = 2 sessions
- ~3K input tokens + ~1K output tokens per session
- Total ~6K input + 2K output = ~$0.0016 per run

Compared to the full default matrix, the focused subset is materially
cheaper and easier to review.

## What to look for in the output

The harness produces transcripts and a per-persona scoring table.
The v1.9.9-specific questions to add to the rubric:

1. **Does the agent avoid inventing a Multi-cloud claim?** The dense
   compatibility fixture has one unresolved DNS-provider indicator and one
   endpoint-bound surface provider. The renderer correctly suppresses the
   rollup because those observations do not establish two workload providers.
2. **Does the agent preserve the role qualifier?** The unresolved DNS role
   remains visible in Services below Confidence and must not be promoted into a
   stronger key fact.
3. **Does the agent distinguish sparse evidence from a tool failure?** The
   deliberately incomplete sparse fixture pins a loader error. It is not a
   successful low-confidence lookup and should not be narrated as one.

The synthetic-sparse fixture has `display_name: null` and does not
load via the cache deserializer; skip it for the v1.9.9 update or
fix the loader contract first.

## Expanding the matrix later

When explicit paid-validation approval is available, expand to:

```bash
# All three personas, both fixtures, both modes: full v1.9.2
# methodology re-run on v1.9.9 panels.
uv run --group agentic-validation python -m validation.agentic_ux.run \
    --provider "$AGENTIC_UX_PROVIDER" \
    --model "$AGENTIC_UX_MODEL" \
    --output validation/agentic_ux/local/v1.9.9-full.md
```

Rough cost envelope: confirm against the selected provider's current
public price sheet before running.

## Why this is not run automatically

- LLM calls cost money and require API keys.
- The harness is a *human-supervised* validation step. Automated
  scoring is provided but a human should read at least one
  transcript per run to sanity-check the rubric output.
- The harness is the v1.9.2 contract; v1.9.9 surfaces are an
  additive enrichment, not a redesign. The risk that v1.9.9
  silently regresses agent UX is bounded by the existing
  agentic-UX fixture compatibility tests
  (`tests/test_agentic_ux_compatibility.py`), which already pin
  that v1.9.2 fixtures continue to load and render through v1.9.9.

## Related artifacts

- `validation/agentic_ux/README.md`: full harness documentation.
- `validation/synthetic_corpus/render_snapshots.md`: current aggregate panel
  review; detailed local output is gitignored.
- `validation/v1.9.2-agentic-ux.md`: sanitized historical aggregate.
