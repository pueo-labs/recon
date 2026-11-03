# Legacy typing exceptions are owned in docs/typing-exceptions.json.
# pyright: reportPrivateUsage=none
"""Tests for the v1.9.2 agentic UX validation harness.

These tests cover three things:

1. The provider adapter shape - that ``get_provider`` constructs each
   adapter with mocked SDK clients without ever calling the network.
2. The rubric scoring - that the binary regex/keyword scans correctly
   classify both positive and negative synthetic transcripts.
3. The runner / report writer - that ``run_matrix`` orchestrates the
   3 x 2 x 2 = 12 sessions, that fusion-stripping removes only the
   v1.9 fields, and that the markdown report is well-formed.

The tests inject a fake provider (no SDK imports, no network) so the
suite stays deterministic and runs in the default ``-m 'not integration'``
selection.
"""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, ClassVar

import pytest

# Add repo root to path so we can import ``validation.agentic_ux`` without
# a packaging install. Keep this localized to the test module so other
# tests are not affected.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from validation.agentic_ux import providers, run, score  # noqa: I001 - sys.path bootstrap above


# --- Provider adapter --------------------------------------------------------


def test_estimate_cost_known_model() -> None:
    cost = providers.estimate_cost(1_000_000, 500_000, "claude-sonnet-4-6")
    # 1M * 3 + 0.5M * 15 = 3 + 7.5 = 10.5
    assert cost == pytest.approx(10.5)


def test_estimate_cost_unknown_model_returns_zero() -> None:
    assert providers.estimate_cost(1_000, 1_000, "no-such-model") == 0.0


def test_estimate_cost_overrides_take_precedence() -> None:
    cost = providers.estimate_cost(200_000, 0, "grok-4.7", override=(2.0, 4.0))
    # A flat override replaces the 200k long-context tier.
    assert cost == pytest.approx(0.4)


def test_require_price_pair_rejects_one_sided_override() -> None:
    with pytest.raises(ValueError, match="both be set or both be omitted"):
        providers.require_price_pair(1.0, None)


def test_estimate_cost_rejects_negative_override() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        providers.estimate_cost(1_000, 1_000, "gpt-6-luna", override=(-1.0, 1.0))


def test_estimate_cost_rejects_non_finite_override() -> None:
    with pytest.raises(ValueError, match="finite"):
        providers.estimate_cost(1_000, 1_000, "gpt-6-luna", override=(float("nan"), 1.0))


def test_price_row_rejects_incomplete_or_combined_tiers() -> None:
    checked = date(2026, 11, 3)
    source = "https://example.invalid/pricing"
    with pytest.raises(ValueError, match="long-context pricing"):
        providers.ModelPrice(
            provider="example",
            input_usd_per_mtok=1.0,
            output_usd_per_mtok=2.0,
            checked_on=checked,
            source=source,
            long_context_at=200_000,
        )
    with pytest.raises(ValueError, match="cannot combine"):
        providers.ModelPrice(
            provider="example",
            input_usd_per_mtok=1.0,
            output_usd_per_mtok=2.0,
            checked_on=checked,
            source=source,
            long_context_at=200_000,
            long_context_input_usd_per_mtok=2.0,
            long_context_output_usd_per_mtok=4.0,
            successor_on=date(2027, 1, 1),
            successor_input_usd_per_mtok=2.0,
            successor_output_usd_per_mtok=4.0,
        )
    with pytest.raises(ValueError, match="non-negative"):
        providers.ModelPrice(
            provider="example",
            input_usd_per_mtok=-1.0,
            output_usd_per_mtok=2.0,
            checked_on=checked,
            source=source,
        )


def test_provider_rejects_one_sided_price_before_sdk_import() -> None:
    with pytest.raises(ValueError, match="both be set or both be omitted"):
        providers.OpenAIProvider("gpt-6-luna", input_price=1.0)


@pytest.mark.parametrize(
    ("model", "input_rate", "output_rate"),
    [
        ("claude-opus-4-7", 5.0, 25.0),
        ("claude-opus-5-5", 4.0, 20.0),
        ("claude-sonnet-5-5", 2.0, 10.0),
        ("claude-sonnet-4-6", 3.0, 15.0),
        ("claude-haiku-5-5", 0.10, 0.50),
        ("claude-haiku-4-5", 1.0, 5.0),
        ("gpt-6.1-sol", 2.0, 10.0),
        ("gpt-6.1-terra", 1.0, 5.0),
        ("gpt-6-luna", 0.10, 0.50),
        ("gpt-5.6-sol", 4.0, 20.0),
        ("grok-4.7", 2.0, 6.0),
        ("grok-4.3", 1.25, 2.50),
        ("gemini-3.8-flash", 0.75, 3.75),
        ("gemini-3.5-flash-lite", 0.30, 2.50),
    ],
)
def test_checked_list_prices(model: str, input_rate: float, output_rate: float) -> None:
    row = providers.PRICING_USD_PER_MTOK[model]
    assert row.checked_on == date(2026, 11, 3)
    assert row.source.startswith("https://")
    assert row.input_usd_per_mtok == input_rate
    assert row.output_usd_per_mtok == output_rate
    assert providers.estimate_cost(1_000, 1_000, model, on=date(2026, 11, 3)) == pytest.approx(
        (input_rate + output_rate) / 1_000
    )


@pytest.mark.parametrize("model", ["gpt-5-mini", "gemini-2.5-flash", "grok-4", "grok-4-mini"])
def test_retired_or_unverified_model_is_not_priced(model: str) -> None:
    assert model not in providers.PRICING_USD_PER_MTOK


def test_long_context_rate_applies_to_the_whole_request() -> None:
    below = providers.estimate_cost(199_999, 1_000, "grok-4.7", on=date(2026, 11, 3))
    at_threshold = providers.estimate_cost(200_000, 1_000, "grok-4.7", on=date(2026, 11, 3))
    assert below == pytest.approx((199_999 * 2.0 + 1_000 * 6.0) / 1_000_000)
    assert at_threshold == pytest.approx((200_000 * 4.0 + 1_000 * 12.0) / 1_000_000)
    haiku_short = providers.estimate_cost(100_000, 1_000, "claude-haiku-5-5", on=date(2026, 11, 3))
    haiku_long = providers.estimate_cost(100_001, 1_000, "claude-haiku-5-5", on=date(2026, 11, 3))
    assert haiku_short == pytest.approx((100_000 * 0.10 + 1_000 * 0.50) / 1_000_000)
    assert haiku_long == pytest.approx((100_001 * 0.50 + 1_000 * 2.50) / 1_000_000)


def test_successor_rate_starts_on_its_published_date() -> None:
    introductory = providers.estimate_cost(1_000_000, 1_000_000, "gemini-3.8-flash", on=date(2026, 12, 31))
    standard = providers.estimate_cost(1_000_000, 1_000_000, "gemini-3.8-flash", on=date(2027, 1, 1))
    assert introductory == pytest.approx(0.75 + 3.75)
    assert standard == pytest.approx(1.50 + 7.50)


def test_price_table_has_no_model_past_its_shutdown_date() -> None:
    assert providers.models_shut_down() == ()


def test_shutdown_guard_reports_a_row_on_its_shutdown_date() -> None:
    row = providers.PRICING_USD_PER_MTOK["gpt-6-luna"]
    priced = {"gpt-6-luna": replace(row, shutdown_on=date(2026, 12, 11))}
    assert providers.models_shut_down(priced, on=date(2026, 12, 10)) == ()
    assert providers.models_shut_down(priced, on=date(2026, 12, 11)) == ("gpt-6-luna",)


def test_get_provider_unknown_raises() -> None:
    with pytest.raises(providers.ProviderError, match="unknown provider"):
        providers.get_provider("nope", "x")


def test_anthropic_provider_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    fake_module = type(sys)("anthropic")
    fake_module.Anthropic = lambda **kwargs: object()  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "anthropic", fake_module)
    with pytest.raises(providers.ProviderError, match="ANTHROPIC_API_KEY"):
        providers.AnthropicProvider("claude-sonnet-4-6")


def test_anthropic_provider_normalizes_response(monkeypatch: pytest.MonkeyPatch) -> None:
    """A mocked anthropic SDK client returns a normalized ChatResponse."""

    class _Block:
        type = "text"

        def __init__(self, text: str) -> None:
            self.text = text

    class _Usage:
        input_tokens = 100
        output_tokens = 50

    class _Response:
        content: ClassVar[list[_Block]] = [_Block("hello world")]
        usage: ClassVar[_Usage] = _Usage()

    class _Messages:
        def create(self, **_kwargs: object) -> _Response:
            return _Response()

    class _Client:
        def __init__(self, **_kwargs: object) -> None:
            self.messages = _Messages()

    fake_module = type(sys)("anthropic")
    fake_module.Anthropic = _Client  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "anthropic", fake_module)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")

    provider = providers.AnthropicProvider("claude-sonnet-4-6")
    response = provider.chat(
        system="be brief",
        messages=[providers.ChatMessage(role="user", content="hi")],
        max_tokens=64,
    )
    assert response.text == "hello world"
    assert response.input_tokens == 100
    assert response.output_tokens == 50
    assert response.provider == "anthropic"
    # 100 in @ $3/M + 50 out @ $15/M = 0.0003 + 0.00075 = 0.00105
    assert response.cost_usd == pytest.approx(0.00105)


def test_openai_provider_normalizes_response(monkeypatch: pytest.MonkeyPatch) -> None:
    """A mocked openai SDK client returns a normalized ChatResponse."""

    class _Message:
        content = "ok"

    class _Choice:
        finish_reason = "stop"
        message: ClassVar[_Message] = _Message()

    class _Usage:
        prompt_tokens = 200
        completion_tokens = 100

    class _Response:
        choices: ClassVar[list[_Choice]] = [_Choice()]
        usage: ClassVar[_Usage] = _Usage()

    class _Completions:
        def create(self, **_kwargs: object) -> _Response:
            return _Response()

    class _Chat:
        completions: ClassVar[_Completions] = _Completions()

    class _Client:
        def __init__(self, **_kwargs: object) -> None:
            self.chat = _Chat()

    fake_module = type(sys)("openai")
    fake_module.OpenAI = _Client  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "openai", fake_module)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    provider = providers.OpenAIProvider("gpt-6-luna")
    response = provider.chat(
        system="terse",
        messages=[providers.ChatMessage(role="user", content="hi")],
        max_tokens=64,
    )
    assert response.text == "ok"
    assert response.input_tokens == 200
    assert response.output_tokens == 100
    assert response.provider == "openai"
    # 200 in @ $0.10/M + 100 out @ $0.50/M
    assert response.cost_usd == pytest.approx(0.00007)
    assert response.cost_known is True


def test_xai_provider_uses_xai_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """The xAI adapter passes the xAI base URL into the openai SDK client."""
    captured: dict[str, object] = {}

    class _Client:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)
            self.chat: object = None

    fake_module = type(sys)("openai")
    fake_module.OpenAI = _Client  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "openai", fake_module)
    monkeypatch.setenv("XAI_API_KEY", "sk-grok")

    providers.XAIProvider("grok-4.3")
    assert captured.get("base_url") == "https://api.x.ai/v1"
    assert captured.get("api_key") == "sk-grok"


def test_openrouter_provider_uses_openrouter_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class _Client:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)
            self.chat: object = None

    fake_module = type(sys)("openai")
    fake_module.__dict__["OpenAI"] = _Client
    monkeypatch.setitem(sys.modules, "openai", fake_module)
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")

    providers.OpenRouterProvider("anthropic/claude-sonnet-5-5")
    assert captured.get("base_url") == "https://openrouter.ai/api/v1"
    assert captured.get("api_key") == "sk-or-test"


def test_google_provider_uses_gemini_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class _Client:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)
            self.chat: object = None

    fake_module = type(sys)("openai")
    fake_module.__dict__["OpenAI"] = _Client
    monkeypatch.setitem(sys.modules, "openai", fake_module)
    monkeypatch.setenv("GEMINI_API_KEY", "sk-gemini-test")

    providers.GoogleProvider("gemini-3.5-flash-lite")
    assert captured.get("base_url") == "https://generativelanguage.googleapis.com/v1beta/openai/"
    assert captured.get("api_key") == "sk-gemini-test"


def test_local_provider_defaults_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class _Client:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)
            self.chat: object = None

    fake_module = type(sys)("openai")
    fake_module.__dict__["OpenAI"] = _Client
    monkeypatch.setitem(sys.modules, "openai", fake_module)
    monkeypatch.delenv("LOCAL_API_KEY", raising=False)

    provider = providers.LocalProvider("llama3")
    assert captured.get("base_url") == "http://localhost:11434/v1"
    assert captured.get("api_key") == "local"
    assert provider.name == "local"


# --- Rubric scoring ----------------------------------------------------------


def test_score_session_negative_baseline() -> None:
    text = "This domain runs Microsoft 365. Email security looks normal."
    s = score.score_session("analyst", "synthetic-dense", True, text)
    assert s.read_posterior_block is False
    assert s.cited_credible_interval is False
    assert s.mentioned_explain_dag is False
    assert s.hedge_count == 0


def test_score_session_detects_posterior_reference() -> None:
    text = "The posterior_observations entry for m365_tenant has n_eff = 5.0."
    s = score.score_session("analyst", "synthetic-dense", True, text)
    assert s.read_posterior_block is True


def test_score_session_rejects_credible_interval_mislabel() -> None:
    text = "The credible interval [0.83, 1.0] suggests high confidence."
    s = score.score_session("ops", "synthetic-dense", True, text)
    assert s.cited_credible_interval is False


def test_score_session_detects_uncertainty_band_phrase() -> None:
    text = "The 80% uncertainty band [0.83, 1.0] is model-relative."
    s = score.score_session("ops", "synthetic-dense", True, text)
    assert s.cited_credible_interval is True


def test_score_session_detects_numeric_interval() -> None:
    text = "Range looks like 0.21 to 0.95 which is wide."
    s = score.score_session("ops", "synthetic-sparse", True, text)
    assert s.cited_credible_interval is True


def test_score_session_detects_explain_dag_invocation() -> None:
    text = "I would run recon example.com --explain-dag for the evidence DAG."
    s = score.score_session("researcher", "synthetic-dense", True, text)
    assert s.mentioned_explain_dag is True


def test_score_session_counts_hedge_phrases() -> None:
    text = "Limited evidence. Cannot confirm the email provider. The signal is sparse and the target appears hardened."
    s = score.score_session("analyst", "synthetic-sparse", True, text)
    assert s.hedge_count >= 3


def test_diff_sparse_vs_dense_positive() -> None:
    dense = score.score_session("analyst", "synthetic-dense", True, "All clear, normal stack.")
    sparse = score.score_session(
        "analyst",
        "synthetic-sparse",
        True,
        "Limited evidence; cannot confirm. The target looks hardened with sparse signals.",
    )
    diff = score.diff_sparse_vs_dense(
        dense,
        sparse,
        dense_text="All clear, normal stack.",
        sparse_text="Limited evidence; cannot confirm. The target looks hardened with sparse signals.",
    )
    assert diff.differed is True


def test_diff_sparse_vs_dense_negative_when_identical_tone() -> None:
    text = "Microsoft 365 with normal posture."
    dense = score.score_session("ops", "synthetic-dense", True, text)
    sparse = score.score_session("ops", "synthetic-sparse", True, text)
    diff = score.diff_sparse_vs_dense(dense, sparse, dense_text=text, sparse_text=text)
    assert diff.differed is False


def test_diff_fusion_on_vs_off_positive() -> None:
    on_text = "Posterior 0.95 for m365_tenant, uncertainty band [0.83, 1.0]."
    off_text = "Microsoft 365 detected from the tenant ID."
    on_score = score.score_session("analyst", "synthetic-dense", True, on_text)
    off_score = score.score_session("analyst", "synthetic-dense", False, off_text)
    diff = score.diff_fusion_on_vs_off(on_score, off_score, on_text=on_text, off_text=off_text)
    assert diff.differed is True


def test_diff_fusion_on_vs_off_negative_when_neither_engages() -> None:
    text = "Microsoft 365 detected. Email looks fine."
    on_score = score.score_session("ops", "synthetic-dense", True, text)
    off_score = score.score_session("ops", "synthetic-dense", False, text)
    diff = score.diff_fusion_on_vs_off(on_score, off_score, on_text=text, off_text=text)
    assert diff.differed is False
    assert "did not engage" in diff.reason


# --- Runner orchestration ----------------------------------------------------


class _FakeProvider:
    """In-process provider that returns canned text without network."""

    name = "fake"
    model = "fake-model"

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def chat(
        self,
        system: str,
        messages: Any,
        *,
        max_tokens: int,
    ) -> providers.ChatResponse:
        msg_list = list(messages)
        user_text = msg_list[0].content if msg_list else ""
        self.calls.append({"system": system, "user": user_text, "max_tokens": max_tokens})
        # Synthesize a response that varies with whether the input has
        # the fusion fields, so the rubric exercises both arms.
        has_fusion = "posterior_observations" in user_text
        is_sparse = "sparse.example.invalid" in user_text
        if has_fusion and not is_sparse:
            text = (
                "Reading posterior_observations: m365_tenant has a credible "
                "interval near 0.83 to 1.0. The evidence DAG (--explain-dag) "
                "would corroborate."
            )
        elif has_fusion and is_sparse:
            text = (
                "Limited evidence; the target looks hardened. The posterior is "
                "wide (interval 0.21 to 0.95) so I cannot confirm. Sparse signals."
            )
        elif is_sparse:
            text = "Limited evidence. Cannot confirm the email provider. Hardened target."
        else:
            text = "Microsoft 365 detected from the tenant ID. Normal stack."
        return providers.ChatResponse(
            text=text,
            input_tokens=200,
            output_tokens=80,
            cost_usd=0.001,
            model=self.model,
            provider=self.name,
        )


def test_run_session_strips_fusion_fields_when_off() -> None:
    fake = _FakeProvider()
    record = run.run_session(
        fake,
        "analyst",
        "synthetic-dense",
        fusion=False,
        max_tokens=512,
    )
    assert record.fusion is False
    assert "posterior_observations" not in fake.calls[-1]["user"]
    assert "slug_confidences" not in fake.calls[-1]["user"]


def test_run_session_includes_fusion_fields_when_on() -> None:
    fake = _FakeProvider()
    record = run.run_session(
        fake,
        "analyst",
        "synthetic-dense",
        fusion=True,
        max_tokens=512,
    )
    assert record.fusion is True
    assert "posterior_observations" in fake.calls[-1]["user"]


def test_run_matrix_produces_12_sessions() -> None:
    fake = _FakeProvider()
    records = run.run_matrix(fake, max_tokens=256)
    assert len(records) == 12
    keys = {(r.persona, r.fixture, r.fusion) for r in records}
    assert len(keys) == 12


def test_score_records_emits_both_diff_kinds() -> None:
    fake = _FakeProvider()
    records = run.run_matrix(fake, max_tokens=256)
    summary = run.score_records(records)
    # Three personas, two diff kinds each = six diffs.
    assert len(summary.diffs) == 6
    labels = {d.label for d in summary.diffs}
    assert labels == {"sparse_vs_dense", "fusion_on_vs_off"}


def test_render_report_contains_required_sections(tmp_path: Path) -> None:
    fake = _FakeProvider()
    records = run.run_matrix(fake, max_tokens=256)
    summary = run.score_records(records)
    started = datetime(2026, 5, 8, 12, 0, 0, tzinfo=UTC)
    finished = datetime(2026, 5, 8, 12, 5, 0, tzinfo=UTC)
    body = run.render_report(records, summary, started_at=started, finished_at=finished)
    assert "# Agentic UX Validation - v1.9.2" in body
    assert "## Methodology" in body
    assert "## Rubric - per-session" in body
    assert "## Rubric - cross-session diffs" in body
    assert "## Transcripts" in body
    assert "fusion=on" in body
    assert "fusion=off" in body
    assert "uv run --group agentic-validation python -m validation.agentic_ux.run" in body
    # Cost line uses 4-decimal precision so a $0.001 fake call is visible.
    assert "$0.0120" in body  # 12 sessions x $0.001 fake cost
    out = tmp_path / "out.md"
    out.write_text(body, encoding="utf-8")
    assert out.read_text(encoding="utf-8") == body


def test_main_writes_output_with_fake_provider(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The main entrypoint should write a report when given a fake provider."""

    def _fake_get_provider(*args: object, **kwargs: object) -> _FakeProvider:
        return _FakeProvider()

    monkeypatch.setattr(run, "get_provider", _fake_get_provider)
    output = tmp_path / "out.md"
    records_json = tmp_path / "records.json"
    rc = run.main(
        [
            "--provider",
            "anthropic",
            "--model",
            "fake",
            "--output",
            str(output),
            "--records-json",
            str(records_json),
        ],
    )
    assert rc == 0
    assert output.exists()
    body = output.read_text(encoding="utf-8")
    assert "# Agentic UX Validation - v1.9.2" in body
    payload = json.loads(records_json.read_text(encoding="utf-8"))
    assert len(payload) == 12
    assert all("response_text" in entry for entry in payload)
    stderr = capsys.readouterr().err
    assert "wrote agentic validation report" in stderr
    assert str(output) not in stderr
    assert str(records_json) not in stderr


def test_main_returns_nonzero_on_provider_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    def _raises(*args: object, **kwargs: object) -> None:
        raise providers.ProviderError("missing key")

    monkeypatch.setattr(run, "get_provider", _raises)
    rc = run.main(
        [
            "--provider",
            "anthropic",
            "--model",
            "x",
            "--output",
            str(tmp_path / "x.md"),
        ],
    )
    assert rc == 2


def test_main_rejects_one_sided_price_before_provider(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    provider_initialized = False

    def _unexpected_provider(*args: object, **kwargs: object) -> _FakeProvider:
        nonlocal provider_initialized
        provider_initialized = True
        return _FakeProvider()

    monkeypatch.setattr(run, "get_provider", _unexpected_provider)
    rc = run.main(
        [
            "--provider",
            "openai",
            "--model",
            "gpt-6-luna",
            "--input-price",
            "0.10",
            "--output",
            str(tmp_path / "report.md"),
        ]
    )
    assert rc == 2
    assert provider_initialized is False
    assert "both be set or both be omitted" in capsys.readouterr().err


@pytest.mark.parametrize(
    "arguments",
    [
        ["--api-key", "super-secret-cli-value"],
        ["--api-key=super-secret-cli-value"],
    ],
)
def test_main_rejects_cli_api_key_without_echoing_secret(
    arguments: list[str],
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = run.main(arguments)

    assert rc == 2
    stderr = capsys.readouterr().err
    assert "--api-key is not supported" in stderr
    assert "ANTHROPIC_API_KEY" in stderr
    assert "GEMINI_API_KEY" in stderr
    assert "OPENROUTER_API_KEY" in stderr
    assert "super-secret-cli-value" not in stderr


@pytest.mark.parametrize(
    "arguments",
    [
        ["--output", str(run._REPO_ROOT / "docs" / "agentic-report.md")],
        [
            "--output",
            str(run._LOCAL_OUTPUT_DIR / "report.md"),
            "--records-json",
            str(run._REPO_ROOT / "validation" / "public-records.json"),
        ],
    ],
)
def test_main_rejects_trackable_output_paths_before_provider_initialization(
    arguments: list[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider_initialized = False

    def _unexpected_provider(*args: object, **kwargs: object) -> _FakeProvider:
        nonlocal provider_initialized
        provider_initialized = True
        return _FakeProvider()

    monkeypatch.setattr(run, "get_provider", _unexpected_provider)

    rc = run.main(["--provider", "anthropic", "--model", "fake", *arguments])

    assert rc == 2
    assert provider_initialized is False


@pytest.mark.parametrize("directory", [run._LOCAL_OUTPUT_DIR, run._RUNS_OUTPUT_DIR])
def test_output_path_guard_accepts_gitignored_agentic_directories(directory: Path) -> None:
    candidate = directory / "nested" / "report.md"

    assert run._validate_output_path(candidate) == candidate.resolve()


@pytest.mark.parametrize("directory", [run._LOCAL_OUTPUT_DIR, run._RUNS_OUTPUT_DIR])
def test_output_path_guard_rejects_allowed_directory_roots(directory: Path) -> None:
    with pytest.raises(ValueError, match="must name a file"):
        run._validate_output_path(directory)


def test_output_path_guard_rejects_existing_external_directory(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="must name a file"):
        run._validate_output_path(tmp_path)


def test_main_rejects_overlapping_report_and_record_paths_before_provider(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    provider_initialized = False

    def _unexpected_provider(*args: object, **kwargs: object) -> _FakeProvider:
        nonlocal provider_initialized
        provider_initialized = True
        return _FakeProvider()

    monkeypatch.setattr(run, "get_provider", _unexpected_provider)
    output = tmp_path / "shared-output.json"

    rc = run.main(
        [
            "--provider",
            "anthropic",
            "--model",
            "fake",
            "--output",
            str(output),
            "--records-json",
            str(output),
        ]
    )

    assert rc == 2
    assert provider_initialized is False


# --- Fixture sanity ----------------------------------------------------------


def test_committed_fixtures_have_expected_shape() -> None:
    """The committed fixtures must round-trip through the runner's loader."""
    dense = run._load_fixture("synthetic-dense")
    sparse = run._load_fixture("synthetic-sparse")
    assert dense["queried_domain"] == "dense.example.invalid"
    assert sparse["queried_domain"] == "sparse.example.invalid"
    # Explicit synthetic sentinels only; see validation/README.md.
    assert "posterior_observations" in dense
    assert "posterior_observations" in sparse
    # Sparse fixture should report sparse=true on at least one node, by design.
    assert any(p.get("sparse") for p in sparse["posterior_observations"])


@pytest.mark.parametrize("known", [False, True])
def test_zero_cost_report_distinguishes_unknown_from_explicit_free(known: bool) -> None:
    records = [
        replace(record, model="llama-remote", cost_usd=0.0, cost_known=known)
        for record in run.run_matrix(_FakeProvider(), max_tokens=64)
    ]
    now = datetime(2026, 10, 26, tzinfo=UTC)
    body = run.render_report(records, run.score_records(records), started_at=now, finished_at=now)
    assert ("cost unknown" in body) is not known
    assert ("$0.0000" in body) is known
