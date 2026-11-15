"""Lookup / discover command implementation: resolve, fuse, emit (panel/json/markdown/explain).

Extracted from cli.py (docs/roadmap.md god-file track). Plain command-logic
helpers; the Typer app and the thin @app.command wrappers stay in cli.py, which
imports this module and references the orchestrators through a small assignment
facade. Imports the shared cli helpers / formatter; never imports cli.py.
"""

from __future__ import annotations

import json
from typing import Any

import typer

from recon_tool.cli.options import LookupOperationMode, LookupOptions
from recon_tool.cli.shared import fmt_exc as _fmt_exc
from recon_tool.cli.shared import lookup_validate, raise_lookup_error
from recon_tool.exit_codes import (
    EXIT_INTERNAL,
    EXIT_VALIDATION,
)
from recon_tool.formatter import get_console, get_err_console
from recon_tool.formatter.theme import spinner_kwargs

_CHAIN_STATUS_MESSAGE = "Following related-domain evidence..."


def _build_explanations(
    info: Any,
    results: list[Any],
    observations: tuple[Any, ...] | None = None,
) -> list[Any]:
    """Build ExplanationRecords for a TenantInfo using the explanation engine.

    Generates explanations for signals, insights, confidence, and observations.
    """
    from recon_tool.absence import evaluate_absence_signals, evaluate_positive_absence
    from recon_tool.collection_view import (
        collection_observable_evidence,
        collection_observable_info,
        collection_observable_results,
    )
    from recon_tool.email_security import signal_context_from_tenant_info, signal_context_metadata
    from recon_tool.explanation import (
        explain_confidence,
        explain_insights,
        explain_observations,
        explain_signals,
    )
    from recon_tool.insight_explanation import InsightExplanationContext
    from recon_tool.models import ExplanationRecord
    from recon_tool.posture import analyze_posture, load_posture_rules
    from recon_tool.signals import evaluate_signals, load_signals

    info = collection_observable_info(info)
    observable_evidence = collection_observable_evidence(info)
    explanations: list[ExplanationRecord] = []

    context = signal_context_from_tenant_info(info)
    context_metadata = signal_context_metadata(context)
    signals = load_signals()
    signal_matches = evaluate_signals(context)

    # Third pass: absence signals + positive hardening observations
    absence_matches = evaluate_absence_signals(signal_matches, signals, frozenset(info.slugs))
    positive_matches = evaluate_positive_absence(signal_matches, signals, frozenset(info.slugs))
    all_signal_matches = signal_matches + absence_matches + positive_matches

    # Signal explanations
    signal_recs = explain_signals(
        all_signal_matches,
        signals,
        frozenset(info.slugs),
        context_metadata,
        observable_evidence,
        info.detection_scores,
    )
    explanations.extend(signal_recs)

    # Insight explanations
    insight_recs = explain_insights(
        list(info.insights),
        frozenset(info.slugs),
        frozenset(info.services),
        observable_evidence,
        InsightExplanationContext(info.detection_scores, info.insight_claims),
    )
    explanations.extend(insight_recs)

    # Confidence explanation uses the stored dimensions. Recomputing them from
    # live SourceResults made cache hits omit this record, and a tenant-ID
    # conflict made the text claim a minimum that was not the stored final.
    observable_results = collection_observable_results(results) if results else []
    identity_conflict = bool(info.merge_conflicts and info.merge_conflicts.tenant_id)
    conf_rec = explain_confidence(
        observable_results,
        info.evidence_confidence,
        info.inference_confidence,
        info.confidence,
        identity_conflict=identity_conflict,
    )
    explanations.append(conf_rec)

    # Observation explanations
    observations = analyze_posture(info) if observations is None else observations
    posture_rules = load_posture_rules()
    obs_recs = explain_observations(observations, posture_rules, observable_evidence, info.detection_scores)
    explanations.extend(obs_recs)

    return explanations


async def _resolve_with_spinner(
    console: Any, validated: str, *, timeout: float, skip_ct: bool, quiet: bool, active_probes: bool = False
) -> tuple[Any, list[Any]]:
    """Resolve a tenant under the source ladder unless output is machine-readable.

    The ladder, its source-health line and the collection-warning summary all
    go to stderr, so they never contaminate the stdout data stream. Machine
    output (``--json``, ``--md``) gets no ladder and no health line; the
    warning summary still replaces the raw warning lines on stderr.
    """
    from recon_tool.cli.collection_warnings import capture_collection_warnings, print_collection_warnings
    from recon_tool.cli.source_ladder import run_with_source_ladder
    from recon_tool.resolver import resolve_tenant

    err_console = get_err_console()
    coro = resolve_tenant(validated, timeout=timeout, skip_ct=skip_ct, active_probes=active_probes)
    with capture_collection_warnings() as warnings:
        try:
            if quiet:
                return await coro
            return await run_with_source_ladder(err_console, coro, skip_ct=skip_ct, active_probes=active_probes)
        finally:
            print_collection_warnings(warnings, err_console)


async def _resolve_cached(
    console: Any,
    validated: str,
    *,
    no_cache: bool,
    cache_ttl: int,
    timeout: float,
    skip_ct: bool,
    quiet: bool,
    active_probes: bool = False,
) -> Any:
    """Return a cached TenantInfo if present, else resolve fresh and cache it.

    Applies the same scope rule as ``_lookup_resolve_standard``: the cache key is
    the domain alone, so a CT-degraded (``--skip-ct``) or probe-derived
    (``--direct-probes``) result must never enter or be served from the shared
    default-scope cache. The exposure and gaps reports reached this helper
    without that guard, which reopened the sharing defect on a second path.
    """
    info: Any = None
    shareable_scope = not skip_ct and not active_probes
    if not no_cache and shareable_scope:
        from recon_tool.cache import cache_get

        cached = cache_get(validated, ttl=cache_ttl)
        if cached is not None:
            info = cached
    if info is None:
        info, _results = await _resolve_with_spinner(
            console, validated, timeout=timeout, skip_ct=skip_ct, quiet=quiet, active_probes=active_probes
        )
        if not no_cache and shareable_scope:
            from recon_tool.cache import cache_put

            cache_put(validated, info)
    return info


def _print_cache_reuse_note(console: Any, info: Any, *, spacer: bool = True) -> None:
    """Print the shared muted reuse line under a panel built from a cached result.

    The panel, ``--exposure``, and ``--gaps`` views print it after their own
    content; ``--plain`` and ``--md`` carry the same sentence in their formatter,
    and lookup JSON keeps the cache timestamps out of its stable contract.
    The tenant panel already ends on a blank line, so it passes ``spacer=False``.
    """
    from recon_tool.formatter.panel_status import render_cache_reuse_note

    note = render_cache_reuse_note(info)
    if note is not None:
        if spacer:
            console.print()
        console.print(note)


async def _lookup_compare(
    console: Any,
    validated: str,
    domain: str,
    options: LookupOptions,
) -> None:
    """Resolve and diff against a saved snapshot (`--compare`)."""
    from pathlib import Path as _Path

    from recon_tool.delta import compute_delta, load_previous, validate_snapshot_domain
    from recon_tool.formatter import format_delta_json, render_delta_panel, render_error
    from recon_tool.models import ReconLookupError

    compare_file = options.compare_file
    if compare_file is None or not compare_file.strip():
        render_error("--compare requires a snapshot path")
        raise typer.Exit(code=EXIT_VALIDATION) from None

    try:
        previous = load_previous(_Path(compare_file))
        validate_snapshot_domain(previous, validated)
    except (OSError, ValueError) as exc:
        # Any unreadable path is operator input, not an internal fault. A bare
        # FileNotFoundError missed a directory or a permission failure, which
        # reached the crash handler and exited 4 instead of the documented 2.
        render_error(_fmt_exc(exc))
        raise typer.Exit(code=EXIT_VALIDATION) from None

    try:
        info, _results = await _resolve_with_spinner(
            console,
            validated,
            timeout=options.timeout,
            skip_ct=options.skip_ct,
            quiet=options.quiet,
            active_probes=options.active_probes,
        )
    except ReconLookupError as exc:
        raise_lookup_error(exc, domain=domain)
    except Exception as exc:
        render_error(_fmt_exc(exc))
        raise typer.Exit(code=EXIT_INTERNAL) from None

    delta = compute_delta(previous, info)
    if options.json_output:
        typer.echo(format_delta_json(delta))
    else:
        console.print(render_delta_panel(delta), crop=False)


async def _lookup_chain(
    console: Any,
    validated: str,
    options: LookupOptions,
) -> None:
    """Follow related-domain breadcrumbs (`--chain`)."""
    from recon_tool.chain import ChainOptions, resolve_chain
    from recon_tool.formatter import format_chain_json, render_chain_panel, render_error
    from recon_tool.models import ReconLookupError

    chain_options = ChainOptions(
        depth=options.chain_depth,
        timeout=options.timeout,
        skip_ct=options.skip_ct,
        active_probes=options.active_probes,
    )
    try:
        from recon_tool.cli.collection_warnings import capture_collection_warnings, print_collection_warnings

        with capture_collection_warnings() as warnings:
            try:
                if not options.quiet:
                    with get_err_console().status(_CHAIN_STATUS_MESSAGE, **spinner_kwargs()):
                        report = await resolve_chain(validated, chain_options)
                else:
                    report = await resolve_chain(validated, chain_options)
            finally:
                print_collection_warnings(warnings, get_err_console())
    except ReconLookupError as exc:
        raise_lookup_error(exc, domain=validated)
    except Exception as exc:
        render_error(_fmt_exc(exc))
        raise typer.Exit(code=EXIT_INTERNAL) from None

    if options.json_output:
        chain_dict = json.loads(format_chain_json(report))
        if options.show_explain:
            from recon_tool.formatter import format_explanations_list

            for i, domain_entry in enumerate(chain_dict.get("domains", [])):
                if i < len(report.results):
                    chain_info = report.results[i].info
                    explanations = _build_explanations(chain_info, [])
                    domain_entry["explanations"] = format_explanations_list(explanations)
                    if chain_info.merge_conflicts and chain_info.merge_conflicts.has_conflicts:
                        from recon_tool.models import serialize_conflicts

                        domain_entry["conflicts"] = serialize_conflicts(chain_info.merge_conflicts)
        typer.echo(json.dumps(chain_dict, indent=2))
    else:
        console.print(render_chain_panel(report), crop=False)
        if options.show_explain:
            from recon_tool.formatter import render_explanations_panel

            for r in report.results:
                explanations = _build_explanations(r.info, [])
                if explanations:
                    console.print(render_explanations_panel(explanations), crop=False)


async def _lookup_exposure(
    console: Any,
    validated: str,
    domain: str,
    options: LookupOptions,
) -> None:
    """Resolve (cache-aware) and render the exposure score (`--exposure`)."""
    from recon_tool.exposure import assess_exposure_from_info
    from recon_tool.formatter import format_exposure_json, render_error, render_exposure_panel
    from recon_tool.models import ReconLookupError

    try:
        info_exp = await _resolve_cached(
            console,
            validated,
            no_cache=options.no_cache,
            cache_ttl=options.cache_ttl,
            timeout=options.timeout,
            skip_ct=options.skip_ct,
            quiet=options.quiet,
            active_probes=options.active_probes,
        )
        assessment = assess_exposure_from_info(info_exp)
        if options.json_output:
            typer.echo(format_exposure_json(assessment))
        else:
            console.print(render_exposure_panel(assessment), crop=False)
            _print_cache_reuse_note(console, info_exp)
    except ReconLookupError as exc:
        raise_lookup_error(exc, domain=domain)
    except Exception as exc:
        render_error(_fmt_exc(exc))
        raise typer.Exit(code=EXIT_INTERNAL) from None


async def _lookup_gaps(
    console: Any,
    validated: str,
    domain: str,
    options: LookupOptions,
) -> None:
    """Resolve (cache-aware) and render the detection-gap report (`--gaps`)."""
    from recon_tool.exposure import find_gaps_from_info
    from recon_tool.formatter import format_gaps_json, render_error, render_gaps_panel
    from recon_tool.models import ReconLookupError

    try:
        info_gaps = await _resolve_cached(
            console,
            validated,
            no_cache=options.no_cache,
            cache_ttl=options.cache_ttl,
            timeout=options.timeout,
            skip_ct=options.skip_ct,
            quiet=options.quiet,
            active_probes=options.active_probes,
        )
        report = find_gaps_from_info(info_gaps)
        if options.json_output:
            typer.echo(format_gaps_json(report))
        else:
            console.print(render_gaps_panel(report), crop=False)
            _print_cache_reuse_note(console, info_gaps)
    except ReconLookupError as exc:
        raise_lookup_error(exc, domain=domain)
    except Exception as exc:
        render_error(_fmt_exc(exc))
        raise typer.Exit(code=EXIT_INTERNAL) from None


def _lookup_apply_fusion(info: Any) -> Any:
    """Apply the shared fusion layer. Kept as a thin alias so the ``--explain-dag``
    call site and any patch target here still resolve; the body moved to
    ``recon_tool.fusion_apply`` so the MCP JSON path can populate the same fields.
    """
    from recon_tool.fusion_apply import apply_fusion

    return apply_fusion(info)


async def _lookup_resolve_standard(
    console: Any,
    validated: str,
    options: LookupOptions,
) -> tuple[Any, list[Any]]:
    """Cache read, resolve on miss, apply fusion, write back. Returns (info, results)."""
    info: Any = None
    results: list[Any] = []
    # The cache key is the domain alone, so it cannot distinguish results
    # collected under different scopes. Only the default scope is shared.
    # --skip-ct produces a CT-degraded result, and --direct-probes produces one
    # containing opt-in probe data. Sharing either would answer a full lookup
    # from a degraded entry, or hand probe-derived data to a run that never
    # opted in. The MCP server applies the same rule to its shared cache; see
    # the note above its cache_set call in server/introspection.py.
    shareable_scope = not options.skip_ct and not options.active_probes
    if not options.no_cache and shareable_scope:
        from recon_tool.cache import cache_get

        cached = cache_get(validated, ttl=options.cache_ttl)
        if cached is not None:
            info = cached

    cache_miss = info is None
    if cache_miss:
        info, results = await _resolve_with_spinner(
            console,
            validated,
            timeout=options.timeout,
            skip_ct=options.skip_ct,
            quiet=options.quiet or options.explain_dag,
            active_probes=options.active_probes,
        )
    else:
        results = _synthetic_source_results(info)

    if options.fusion or options.explain_dag:
        info = _lookup_apply_fusion(info)
    else:
        # --no-fusion: a cache hit may carry fusion fields written by an earlier
        # run. Clear them so the opt-out is honored (fusion_enabled is derived
        # from posterior_observations downstream).
        from dataclasses import replace as _replace

        info = _replace(info, slug_confidences={}, posterior_observations=())

    # Cache hits don't write back: the entry hasn't changed except for fusion
    # output, which is recomputed on read anyway. A collection with a recorded
    # collector failure is still written: `recon delta` uses it as a baseline
    # and `recon cache show` reports it, but cache_get never serves it to an
    # ordinary lookup, so the next default lookup collects again. --no-cache
    # bypasses both the read and this write.
    if cache_miss and not options.no_cache and shareable_scope:
        from recon_tool.cache import cache_put

        cache_put(validated, info)
    return info, results


def _lookup_compute_observations(info: Any, profile_name: str | None, show_posture: bool) -> tuple[Any, ...]:
    """Resolve the requested posture profile and compute posture observations."""
    from recon_tool.formatter import render_error

    profile = None
    if profile_name:
        from recon_tool.profiles import load_profile

        profile = load_profile(profile_name)
        if profile is None:
            from recon_tool.profiles import list_profiles

            names = ", ".join(p.name for p in list_profiles())
            render_error(f"Unknown profile {profile_name!r}. Available profiles: {names or '(none)'}")
            raise typer.Exit(code=EXIT_VALIDATION) from None

    observations: tuple[Any, ...] = ()
    if show_posture:
        from recon_tool.collection_view import collection_claim_info
        from recon_tool.posture import analyze_posture
        from recon_tool.profiles import apply_profile, compute_baseline_anomalies

        claim_info = collection_claim_info(info)
        raw_observations = analyze_posture(claim_info)
        # Append vertical-baseline anomalies before profile reweighting so
        # profile boosts apply uniformly. Empty tuple when no profile or when the
        # profile has no expectations.
        anomalies = (
            ()
            if claim_info.degraded_sources
            else compute_baseline_anomalies(
                profile,
                claim_info.slugs,
                tuple(motif.motif_name for motif in claim_info.chain_motifs),
            )
        )
        combined_obs = tuple(raw_observations) + anomalies
        observations = apply_profile(combined_obs, profile)
    return observations


def _lookup_emit_explain_dag(validated: str, info: Any, explain_dag_format: str) -> None:
    """Render the Bayesian evidence DAG in the requested format (`--explain-dag`)."""
    from recon_tool.bayesian import collection_masked_units, infer_from_tenant_info, load_network
    from recon_tool.bayesian_dag import render_dag_dot, render_dag_mermaid, render_dag_text
    from recon_tool.formatter import render_error

    network = load_network()
    inference = infer_from_tenant_info(info, network=network)
    fmt = (explain_dag_format or "text").lower()
    degraded = sorted(set(getattr(info, "degraded_sources", ()) or ()))
    masked = sorted(collection_masked_units(degraded, network=network))
    if degraded:
        degraded_text = ", ".join(degraded)
        masked_text = ", ".join(masked) if masked else "none"
        if fmt == "dot":
            provenance_prefix = f"// degraded_sources: {degraded_text}\n// collection_masked_units: {masked_text}\n"
        elif fmt == "mermaid":
            provenance_prefix = f"%% degraded_sources: {degraded_text}\n%% collection_masked_units: {masked_text}\n"
        else:
            provenance_prefix = (
                "Collection provenance:\n"
                f"- degraded_sources: {degraded_text}\n"
                f"- collection-masked units: {masked_text}\n\n"
            )
    else:
        provenance_prefix = ""
    if fmt == "dot":
        typer.echo(provenance_prefix + render_dag_dot(network, inference, domain=validated))
    elif fmt == "mermaid":
        typer.echo(provenance_prefix + render_dag_mermaid(network, inference, domain=validated))
    elif fmt == "text":
        typer.echo(provenance_prefix + render_dag_text(network, inference, domain=validated))
    else:
        render_error(f"--explain-dag-format must be 'text', 'dot', or 'mermaid', got {explain_dag_format!r}")
        raise typer.Exit(code=EXIT_VALIDATION) from None


def _lookup_emit_json(
    info: Any,
    results: list[Any],
    observations: tuple[Any, ...],
    *,
    show_posture: bool,
    show_explain: bool,
    include_unclassified: bool,
) -> None:
    """Emit the tenant dict as JSON, with optional posture and explanation blocks."""
    from recon_tool.formatter import format_tenant_dict

    tenant_dict = format_tenant_dict(info, include_unclassified=include_unclassified)
    tenant_dict.update(
        _lookup_optional_sections(info, results, observations, show_posture=show_posture, show_explain=show_explain)
    )
    typer.echo(json.dumps(tenant_dict, indent=2))


def _lookup_optional_sections(
    info: Any,
    results: list[Any],
    observations: tuple[Any, ...],
    *,
    show_posture: bool,
    show_explain: bool,
) -> dict[str, Any]:
    """Build the `--posture` and `--explain` blocks shared by JSON and plain output.

    Extracted so the linear `--plain` view carries the same optional sections.
    It previously took neither flag, so `--plain --explain` and
    `--plain --posture` exited 0 having silently dropped the requested content,
    which made the screen-reader path the only one that could not show evidence.
    """
    from recon_tool.formatter import format_posture_observations

    sections: dict[str, Any] = {}
    if show_posture:
        sections["posture"] = format_posture_observations(observations)
    if show_explain:
        from recon_tool.collection_view import collection_observable_evidence
        from recon_tool.explanation import build_explanation_dag
        from recon_tool.formatter import format_explanations_list
        from recon_tool.models import serialize_conflicts

        explanations = _build_explanations(info, results, observations)
        sections["explanations"] = format_explanations_list(explanations)
        # Structured provenance DAG for programmatic consumers. Lives
        # alongside the flat list; both are emitted so existing tooling doesn't
        # break.
        sections["explanation_dag"] = build_explanation_dag(explanations, collection_observable_evidence(info))
        if info.merge_conflicts and info.merge_conflicts.has_conflicts:
            sections["conflicts"] = serialize_conflicts(info.merge_conflicts)
    return sections


def _lookup_emit_markdown(
    info: Any,
    results: list[Any],
    observations: tuple[Any, ...],
    *,
    display: Any,
) -> None:
    """Emit the tenant report as Markdown, with optional posture and explanations.

    Takes the display options rather than three booleans off them: the report
    needs the posture flag, the explain flag, and the evidence-role detail
    level, and threading each one separately put this function over the
    argument ratchet for no readability gain.
    """
    from recon_tool.formatter import format_tenant_markdown
    from recon_tool.formatter.markdown import markdown_escape

    show_posture = display.show_posture
    show_explain = display.show_explain
    md = format_tenant_markdown(
        info,
        detailed=display.verbose or show_explain,
        full=display.full,
        confidence_mode=display.confidence_mode,
    )
    if show_posture and observations:
        md += "\n## Posture Analysis\n\n"
        for obs in observations:
            indicator = {"high": "●", "medium": "◐", "low": "○"}.get(obs.salience, "○")
            category = markdown_escape(obs.category)
            statement = markdown_escape(obs.statement)
            md += f"- {indicator} **[{category}]** {statement}\n"
        md += "\n"
    if show_explain:
        from recon_tool.formatter import format_explanations_markdown

        explanations = _build_explanations(info, results, observations)
        md += "\n" + format_explanations_markdown(explanations)
    typer.echo(md)


def _lookup_emit_plain(
    info: Any,
    sections: dict[str, Any],
    *,
    detailed: bool,
    options: LookupOptions,
) -> None:
    """Emit the tenant report as plain, linear, greppable text (no panel).

    Takes the already-built optional sections rather than the flags that select
    them, so the linear view shares one definition of those blocks with the JSON
    view without growing another wide flag signature. The remaining renderer
    flags come off ``options`` for the same reason.

    ``--full`` selects the complete structured record (ADR-0016); the default is
    the panel's own rows, with the panel's own cuts.
    """
    from recon_tool.formatter import format_tenant_plain
    from recon_tool.formatter.serialize import plain_lines

    lines = [
        format_tenant_plain(
            info,
            include_unclassified=options.include_unclassified,
            detailed=detailed,
            full=options.display.full,
            confidence_mode=options.confidence_mode,
        )
    ]
    for key, value in sections.items():
        lines.extend(plain_lines(value, key, 0))
    typer.echo("\n".join(lines))


def _synthetic_source_results(info: Any) -> list[Any]:
    """Reconstruct minimal SourceResults from a cached TenantInfo.

    On a cache hit the raw SourceResult list isn't available (the cache stores
    TenantInfo, not source results), so the `--explain` status panel rebuilds
    what it can from ``info.sources`` (successes) and ``info.degraded_sources``
    (failures).
    """
    from recon_tool.models import SourceResult

    _m365_sources = {"oidc_discovery", "user_realm", "dns_records"}
    synthetic: list[SourceResult] = []
    for src_name in info.sources:
        synthetic.append(
            SourceResult(
                source_name=src_name,
                tenant_id=info.tenant_id if src_name == "oidc_discovery" else None,
                display_name=info.display_name if src_name == "user_realm" else None,
                auth_type=info.auth_type if src_name == "user_realm" else None,
                m365_detected=bool(info.tenant_id) and src_name in _m365_sources,
                dmarc_policy=info.dmarc_policy if src_name == "dns_records" else None,
            )
        )
    for deg in info.degraded_sources:
        synthetic.append(
            SourceResult(
                source_name=deg,
                error="unavailable during original lookup",
            )
        )
    return synthetic


def _lookup_emit_panel(
    console: Any,
    info: Any,
    results: list[Any],
    observations: tuple[Any, ...],
    *,
    show_services: bool,
    show_domains: bool,
    verbose: bool,
    show_explain: bool,
    show_sources: bool,
    show_posture: bool,
    confidence_mode: str,
) -> None:
    """Render the default human-readable panel, plus optional sources/posture/explain."""
    from recon_tool.collection_view import collection_observable_results
    from recon_tool.formatter import render_sources_detail, render_tenant_panel

    visible_results = collection_observable_results(results)

    console.print(
        render_tenant_panel(
            info,
            show_services=show_services,
            show_domains=show_domains,
            verbose=verbose,
            explain=show_explain,
            confidence_mode=confidence_mode,
        ),
        # An identifier wider than a narrow console runs past the edge on its
        # own line instead of being cropped (formatter/layout.py width rule).
        crop=False,
    )
    _print_cache_reuse_note(console, info, spacer=False)

    if show_sources:
        console.print(render_sources_detail(visible_results))

    # Posture panel after main output
    if show_posture and observations:
        from recon_tool.formatter import render_posture_panel

        posture_panel = render_posture_panel(observations)
        if posture_panel:
            console.print(posture_panel, crop=False)

    # Explanations panel after posture
    if show_explain:
        from recon_tool.formatter import render_explanations_panel, render_source_status_panel

        # U1: always render per-source status under --explain so users
        # can see which sources succeeded, which failed, and why. Previously this
        # was only available via --verbose.
        status_results: list[Any] = visible_results
        if not status_results and info is not None:
            status_results = _synthetic_source_results(info)

        status_panel = render_source_status_panel(status_results)
        if status_panel:
            console.print(status_panel, crop=False)

        explanations = _build_explanations(info, visible_results, observations)
        if explanations:
            console.print(render_explanations_panel(explanations), crop=False)


async def _lookup_standard(
    console: Any,
    validated: str,
    domain: str,
    options: LookupOptions,
) -> None:
    """The default lookup path: resolve, fuse, then emit DAG / JSON / Markdown / panel."""
    from recon_tool.formatter import render_error, render_verbose_sources
    from recon_tool.models import ReconLookupError

    try:
        info, results = await _lookup_resolve_standard(
            console,
            validated,
            options=options,
        )

        if options.verbose:
            from recon_tool.collection_view import collection_observable_results

            render_verbose_sources(
                collection_observable_results(results),
                console=get_err_console(),
                skip_ct=options.skip_ct,
                active_probes=options.active_probes,
            )

        observations = _lookup_compute_observations(
            info,
            options.profile_name,
            options.show_posture or options.show_explain,
        )

        if options.explain_dag:
            _lookup_emit_explain_dag(validated, info, options.explain_dag_format)
            return
        if options.json_output:
            _lookup_emit_json(
                info,
                results,
                observations,
                show_posture=options.show_posture,
                show_explain=options.show_explain,
                include_unclassified=options.include_unclassified,
            )
            return
        # The evidence-role detail level tracks the panel's (ADR-0012): the
        # non-panel human surfaces are the same default view in another shape.
        detailed_roles = options.verbose or options.show_explain
        if options.markdown:
            _lookup_emit_markdown(info, results, observations, display=options)
            return
        if options.plain:
            _lookup_emit_plain(
                info,
                _lookup_optional_sections(
                    info,
                    results,
                    observations,
                    show_posture=options.show_posture,
                    show_explain=options.show_explain,
                ),
                detailed=detailed_roles,
                options=options,
            )
            return

        _lookup_emit_panel(
            console,
            info,
            results,
            observations,
            show_services=options.show_services,
            show_domains=options.show_domains,
            verbose=options.verbose,
            show_explain=options.show_explain,
            show_sources=options.show_sources,
            show_posture=options.show_posture,
            confidence_mode=options.confidence_mode,
        )
    except typer.Exit:
        # Deliberate control-flow exits (an unknown --profile or a bad
        # --explain-dag-format raise typer.Exit(EXIT_VALIDATION) from inside the
        # try). typer.Exit subclasses Exception, so without this it would be
        # caught below, reclassified to EXIT_INTERNAL, and print a bare "Exit".
        raise
    except ReconLookupError as exc:
        raise_lookup_error(exc, domain=domain)
    except Exception as exc:
        render_error(_fmt_exc(exc))
        raise typer.Exit(code=EXIT_INTERNAL) from None


async def lookup(
    domain: str,
    options: LookupOptions,
) -> None:
    """Async lookup implementation.

    A thin dispatcher: validate the domain and normalized option set, then hand
    off to the mode helper for compare / chain / exposure / gaps, or to the
    standard panel path.
    """
    console = get_console()

    validated = lookup_validate(domain, options=options)

    if options.operation_mode is LookupOperationMode.COMPARE:
        await _lookup_compare(console, validated, domain, options)
        return

    if options.operation_mode is LookupOperationMode.CHAIN:
        await _lookup_chain(console, validated, options)
        return

    if options.operation_mode is LookupOperationMode.EXPOSURE:
        await _lookup_exposure(console, validated, domain, options)
        return

    if options.operation_mode is LookupOperationMode.GAPS:
        await _lookup_gaps(console, validated, domain, options)
        return

    await _lookup_standard(console, validated, domain, options)
