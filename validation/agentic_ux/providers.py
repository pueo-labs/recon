"""Multi-provider chat adapter for agentic UX validation.

The harness needs to drive identical persona prompts across multiple
LLM providers (Anthropic, OpenAI, xAI Grok) so the v1.9.2 rubric
findings are not Anthropic-specific. Each provider's SDK is imported
lazily so installing only one of them is enough; selecting an
unavailable provider raises a clear ``ProviderError`` instead of an
``ImportError``.

The price table is the pre-run estimate. Token counts in a finished
report come from the provider response, and the dollar amount
multiplies those counts by this table or by an explicit override. A
stale row mis-states that estimate. Pass both price overrides for a
model the table does not list, or when cache, batch, or regional
premiums should replace the list rate.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, Literal, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence


Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class ChatMessage:
    """Single turn in a chat conversation."""

    role: Role
    content: str


@dataclass(frozen=True)
class ChatResponse:
    """Result of a single chat call.

    ``cost_usd`` multiplies provider-reported token counts by the list
    price, or by an explicit override. It is an estimate, not an invoice.
    """

    text: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    model: str
    provider: str
    cost_known: bool = True


class ProviderError(RuntimeError):
    """Raised when a provider cannot be constructed or its call fails."""


class ChatProvider(Protocol):
    """Minimal chat-completion contract the runner depends on."""

    name: str
    model: str

    def chat(
        self,
        system: str,
        messages: Sequence[ChatMessage],
        *,
        max_tokens: int,
    ) -> ChatResponse:
        """Submit a single chat completion and return a normalized response."""
        ...


# --- Pricing -----------------------------------------------------------------

# Per-million-token standard list prices in USD, checked 2026-11-03.
# Each row records that check on ``ModelPrice.checked_on``.
# https://platform.claude.com/docs/en/about-claude/pricing
# https://developers.openai.com/api/docs/pricing
# https://developers.openai.com/api/docs/deprecations
# https://docs.x.ai/developers/pricing
# https://docs.x.ai/developers/migration/may-15-retirement
# https://aistudio.google.com/docs/pricing
# Rates omit caching, batch discounts, and regional premiums. A long-context
# threshold bills every token in the request at the long-context rate once
# the prompt reaches it. A successor date replaces the standard rate from
# that day. Overrides are a flat pair and do not apply either tier.
_ANTHROPIC_PRICING = "https://platform.claude.com/docs/en/about-claude/pricing"
_OPENAI_PRICING = "https://developers.openai.com/api/docs/pricing"
_XAI_PRICING = "https://docs.x.ai/developers/pricing"
_GOOGLE_PRICING = "https://aistudio.google.com/docs/pricing"
_PRICE_CHECKED_ON = date(2026, 11, 3)


@dataclass(frozen=True, slots=True)
class ModelPrice:
    """Public list price for one model id.

    ``shutdown_on`` is the provider's shutdown date. The guard fails on
    that date. ``long_context_at`` is the first input-token count that
    bills the whole request at the long-context rate. ``successor_on``
    is the first day the successor standard rate replaces this one.
    """

    provider: str
    input_usd_per_mtok: float
    output_usd_per_mtok: float
    checked_on: date
    source: str
    shutdown_on: date | None = None
    long_context_at: int | None = None
    long_context_input_usd_per_mtok: float | None = None
    long_context_output_usd_per_mtok: float | None = None
    successor_on: date | None = None
    successor_input_usd_per_mtok: float | None = None
    successor_output_usd_per_mtok: float | None = None

    def __post_init__(self) -> None:
        _require_rate("input", self.input_usd_per_mtok)
        _require_rate("output", self.output_usd_per_mtok)
        long_values = (
            self.long_context_at,
            self.long_context_input_usd_per_mtok,
            self.long_context_output_usd_per_mtok,
        )
        if any(value is not None for value in long_values) and any(value is None for value in long_values):
            raise ValueError("long-context pricing needs a token threshold and both rates")
        if self.long_context_at is not None and self.long_context_at <= 0:
            raise ValueError("long-context threshold must be positive")
        if self.long_context_input_usd_per_mtok is not None:
            _require_rate("long-context input", self.long_context_input_usd_per_mtok)
        if self.long_context_output_usd_per_mtok is not None:
            _require_rate("long-context output", self.long_context_output_usd_per_mtok)
        successor_values = (
            self.successor_on,
            self.successor_input_usd_per_mtok,
            self.successor_output_usd_per_mtok,
        )
        if any(value is not None for value in successor_values) and any(value is None for value in successor_values):
            raise ValueError("a successor rate needs a start date and both prices")
        if self.successor_input_usd_per_mtok is not None:
            _require_rate("successor input", self.successor_input_usd_per_mtok)
        if self.successor_output_usd_per_mtok is not None:
            _require_rate("successor output", self.successor_output_usd_per_mtok)
        if self.long_context_at is not None and self.successor_on is not None:
            raise ValueError("a row cannot combine a long-context tier with a successor rate")
        if not self.provider or not self.source:
            raise ValueError("a price row needs a provider and a source")

    def rates(self, input_tokens: int, *, on: date) -> tuple[float, float]:
        """Return the list rate that applies to this prompt size on ``on``."""
        in_price = self.input_usd_per_mtok
        out_price = self.output_usd_per_mtok
        if (
            self.successor_on is not None
            and on >= self.successor_on
            and self.successor_input_usd_per_mtok is not None
            and self.successor_output_usd_per_mtok is not None
        ):
            in_price = self.successor_input_usd_per_mtok
            out_price = self.successor_output_usd_per_mtok
        if (
            self.long_context_at is not None
            and input_tokens >= self.long_context_at
            and self.long_context_input_usd_per_mtok is not None
            and self.long_context_output_usd_per_mtok is not None
        ):
            return (self.long_context_input_usd_per_mtok, self.long_context_output_usd_per_mtok)
        return (in_price, out_price)


def _require_rate(label: str, value: float) -> None:
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{label} price must be a finite non-negative number")


def _price(
    provider: str,
    rates: tuple[float, float],
    source: str,
    *,
    long_context: tuple[int, float, float] | None = None,
    successor: tuple[date, float, float] | None = None,
) -> ModelPrice:
    """Build one checked row.

    ``long_context`` is ``(first input-token count, input rate, output rate)``.
    ``successor`` is ``(first day, input rate, output rate)``.
    """
    input_usd, output_usd = rates
    long_at: int | None = None
    long_in: float | None = None
    long_out: float | None = None
    if long_context is not None:
        long_at, long_in, long_out = long_context
    successor_on: date | None = None
    successor_in: float | None = None
    successor_out: float | None = None
    if successor is not None:
        successor_on, successor_in, successor_out = successor
    return ModelPrice(
        provider=provider,
        input_usd_per_mtok=input_usd,
        output_usd_per_mtok=output_usd,
        checked_on=_PRICE_CHECKED_ON,
        source=source,
        long_context_at=long_at,
        long_context_input_usd_per_mtok=long_in,
        long_context_output_usd_per_mtok=long_out,
        successor_on=successor_on,
        successor_input_usd_per_mtok=successor_in,
        successor_output_usd_per_mtok=successor_out,
    )


# Removed from the estimate, checked 2026-11-03:
# gpt-5-mini shuts down 2026-12-11 (replacement gpt-5.6-terra). Its listed
# output rate is $2, not $1. The cheap OpenAI example is gpt-6-luna.
# gemini-2.5-flash is closed to new projects and routes to
# gemini-3.5-flash-lite on 2026-12-01.
# grok-4-0709 retired 2026-05-15 and is served as grok-4.3. The bare grok-4
# slug was not confirmed, and grok-4-mini is not on the xAI price page.
PRICING_USD_PER_MTOK: dict[str, ModelPrice] = {
    "claude-opus-5-5": _price("anthropic", (4.0, 20.0), _ANTHROPIC_PRICING),
    "claude-opus-4-7": _price("anthropic", (5.0, 25.0), _ANTHROPIC_PRICING),
    "claude-sonnet-5-5": _price("anthropic", (2.0, 10.0), _ANTHROPIC_PRICING),
    "claude-sonnet-4-6": _price("anthropic", (3.0, 15.0), _ANTHROPIC_PRICING),
    "claude-haiku-5-5": _price(
        "anthropic",
        (0.10, 0.50),
        _ANTHROPIC_PRICING,
        long_context=(100_001, 0.50, 2.50),
    ),
    "claude-haiku-4-5": _price("anthropic", (1.0, 5.0), _ANTHROPIC_PRICING),
    "gpt-6.1-sol": _price("openai", (2.0, 10.0), _OPENAI_PRICING),
    "gpt-6.1-terra": _price("openai", (1.0, 5.0), _OPENAI_PRICING),
    "gpt-6-luna": _price("openai", (0.10, 0.50), _OPENAI_PRICING),
    # Promotional at least through 2026-11-21. The following rate is not published.
    "gpt-5.6-sol": _price("openai", (4.0, 20.0), _OPENAI_PRICING),
    "grok-4.7": _price(
        "xai",
        (2.0, 6.0),
        _XAI_PRICING,
        long_context=(200_000, 4.0, 12.0),
    ),
    "grok-4.3": _price(
        "xai",
        (1.25, 2.50),
        _XAI_PRICING,
        long_context=(200_000, 2.50, 5.0),
    ),
    "gemini-3.8-flash": _price(
        "google",
        (0.75, 3.75),
        _GOOGLE_PRICING,
        successor=(date(2027, 1, 1), 1.50, 7.50),
    ),
    "gemini-3.5-flash-lite": _price("google", (0.30, 2.50), _GOOGLE_PRICING),
}


def require_price_pair(input_price: float | None, output_price: float | None) -> None:
    """Reject a one-sided or non-finite override before it can mix with the table."""
    if (input_price is None) != (output_price is None):
        raise ValueError("input_price and output_price must both be set or both be omitted")
    if input_price is None or output_price is None:
        return
    _require_rate("input", input_price)
    _require_rate("output", output_price)


def models_shut_down(
    prices: dict[str, ModelPrice] | None = None,
    *,
    on: date | None = None,
) -> tuple[str, ...]:
    """Return priced model ids whose recorded shutdown date has arrived."""
    table = PRICING_USD_PER_MTOK if prices is None else prices
    day = datetime.now(UTC).date() if on is None else on
    return tuple(
        sorted(model for model, row in table.items() if row.shutdown_on is not None and row.shutdown_on <= day)
    )


def _override_pair(
    input_price: float | None,
    output_price: float | None,
) -> tuple[float, float] | None:
    """Return a validated flat pair, or ``None`` when the caller omitted both."""
    require_price_pair(input_price, output_price)
    if input_price is None or output_price is None:
        return None
    return (input_price, output_price)


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str,
    *,
    override: tuple[float, float] | None = None,
    on: date | None = None,
) -> float:
    """Compute USD cost for a call given token counts and a model name.

    When the model is not in the pricing table and no override is
    supplied the function returns ``0.0`` rather than raising. Callers
    that report a dollar amount also check whether the price is known.
    An explicit pair replaces the list rate for every token, including
    prompts past a long-context threshold. ``on`` selects a successor
    rate; the default is the current UTC date.
    """
    if override is not None:
        in_price, out_price = override
        require_price_pair(in_price, out_price)
    else:
        row = PRICING_USD_PER_MTOK.get(model)
        if row is None:
            in_price = 0.0
            out_price = 0.0
        else:
            in_price, out_price = row.rates(input_tokens, on=datetime.now(UTC).date() if on is None else on)
    return (input_tokens * in_price + output_tokens * out_price) / 1_000_000


# --- Anthropic ---------------------------------------------------------------


class AnthropicProvider:
    """Adapter over the official ``anthropic`` SDK."""

    name = "anthropic"

    def __init__(
        self,
        model: str,
        *,
        api_key: str | None = None,
        input_price: float | None = None,
        output_price: float | None = None,
    ) -> None:
        require_price_pair(input_price, output_price)
        try:
            import anthropic  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - exercised via mock in tests
            raise ProviderError(
                "anthropic SDK not installed. Use the locked agentic-validation dependency group documented in "
                "validation/agentic_ux/README.md.",
            ) from exc

        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise ProviderError(
                "ANTHROPIC_API_KEY is not set. Export it in the environment.",
            )

        self.model = model
        self._client = anthropic.Anthropic(api_key=key)
        self._input_price = input_price
        self._output_price = output_price

    def chat(
        self,
        system: str,
        messages: Sequence[ChatMessage],
        *,
        max_tokens: int,
    ) -> ChatResponse:
        payload = [{"role": m.role, "content": m.content} for m in messages if m.role != "system"]
        try:
            response = self._client.messages.create(
                model=self.model,
                system=system,
                messages=payload,
                max_tokens=max_tokens,
            )
        except Exception as exc:  # pragma: no cover - real network failure path
            raise ProviderError(f"anthropic call failed: {exc}") from exc

        text = "".join(block.text for block in response.content if getattr(block, "type", "") == "text")
        usage = response.usage
        in_tok = int(getattr(usage, "input_tokens", 0))
        out_tok = int(getattr(usage, "output_tokens", 0))
        cost = estimate_cost(
            in_tok,
            out_tok,
            self.model,
            override=_override_pair(self._input_price, self._output_price),
        )
        return ChatResponse(
            text=text,
            input_tokens=in_tok,
            output_tokens=out_tok,
            cost_usd=cost,
            model=self.model,
            provider=self.name,
            cost_known=self.model in PRICING_USD_PER_MTOK
            or (self._input_price is not None and self._output_price is not None),
        )


# --- OpenAI / xAI ------------------------------------------------------------


class _OpenAICompatibleProvider:
    """Shared adapter for OpenAI-compatible chat APIs.

    The xAI Grok API is OpenAI-compatible apart from its base URL and
    auth header, so subclassing here keeps the parsing logic in one
    place. The two concrete classes below differ only in defaults.
    """

    name = "openai"
    default_base_url: str | None = None
    api_key_env: str = "OPENAI_API_KEY"

    def __init__(
        self,
        model: str,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        input_price: float | None = None,
        output_price: float | None = None,
    ) -> None:
        require_price_pair(input_price, output_price)
        try:
            import openai  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - exercised via mock in tests
            raise ProviderError(
                "openai SDK not installed. Use the locked agentic-validation dependency group documented in "
                "validation/agentic_ux/README.md.",
            ) from exc

        key = api_key or os.environ.get(self.api_key_env)
        if not key:
            raise ProviderError(
                f"{self.api_key_env} is not set. Export it in the environment.",
            )

        self.model = model
        client_kwargs: dict[str, str] = {"api_key": key}
        url = base_url or self.default_base_url
        if url:
            client_kwargs["base_url"] = url
        self._client = openai.OpenAI(**client_kwargs)
        self._input_price = input_price
        self._output_price = output_price

    def chat(
        self,
        system: str,
        messages: Sequence[ChatMessage],
        *,
        max_tokens: int,
    ) -> ChatResponse:
        payload: list[dict[str, str]] = [{"role": "system", "content": system}]
        payload.extend({"role": m.role, "content": m.content} for m in messages if m.role != "system")

        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=payload,
                max_tokens=max_tokens,
            )
        except Exception as exc:  # pragma: no cover - real network failure path
            raise ProviderError(f"{self.name} call failed: {exc}") from exc

        choice = response.choices[0]
        if choice.finish_reason != "stop" or getattr(choice.message, "tool_calls", None):
            raise ProviderError("model response must complete normally with text only")
        text = choice.message.content or ""
        usage = response.usage
        in_tok = int(getattr(usage, "prompt_tokens", 0))
        out_tok = int(getattr(usage, "completion_tokens", 0))
        cost = estimate_cost(
            in_tok,
            out_tok,
            self.model,
            override=_override_pair(self._input_price, self._output_price),
        )
        return ChatResponse(
            text=text,
            input_tokens=in_tok,
            output_tokens=out_tok,
            cost_usd=cost,
            model=self.model,
            provider=self.name,
            cost_known=self.model in PRICING_USD_PER_MTOK
            or (self._input_price is not None and self._output_price is not None),
        )


class OpenAIProvider(_OpenAICompatibleProvider):
    """Adapter over the official ``openai`` SDK."""

    name = "openai"
    api_key_env = "OPENAI_API_KEY"


class XAIProvider(_OpenAICompatibleProvider):
    """Adapter over xAI's OpenAI-compatible Grok API."""

    name = "xai"
    default_base_url = "https://api.x.ai/v1"
    api_key_env = "XAI_API_KEY"


class OpenRouterProvider(_OpenAICompatibleProvider):
    """Adapter over OpenRouter's OpenAI-compatible API."""

    name = "openrouter"
    default_base_url = "https://openrouter.ai/api/v1"
    api_key_env = "OPENROUTER_API_KEY"


class GoogleProvider(_OpenAICompatibleProvider):
    """Adapter over Google Gemini's OpenAI-compatible API."""

    name = "google"
    default_base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
    api_key_env = "GEMINI_API_KEY"


class LocalProvider(_OpenAICompatibleProvider):
    """Adapter for local OpenAI-compatible endpoints (Ollama, vLLM, LM Studio)."""

    name = "local"
    default_base_url = "http://localhost:11434/v1"
    api_key_env = "LOCAL_API_KEY"

    def __init__(
        self,
        model: str,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        input_price: float | None = None,
        output_price: float | None = None,
    ) -> None:
        require_price_pair(input_price, output_price)
        key = api_key or os.environ.get(self.api_key_env) or "local"
        super().__init__(
            model,
            api_key=key,
            base_url=base_url,
            input_price=input_price if input_price is not None else 0.0,
            output_price=output_price if output_price is not None else 0.0,
        )


# --- Registry ----------------------------------------------------------------

PROVIDER_REGISTRY: dict[str, type[ChatProvider]] = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "xai": XAIProvider,
    "openrouter": OpenRouterProvider,
    "google": GoogleProvider,
    "local": LocalProvider,
}


def get_provider(
    name: str,
    model: str,
    **kwargs: object,
) -> ChatProvider:
    """Construct a provider by name. Raises ``ProviderError`` on misconfiguration."""
    cls = PROVIDER_REGISTRY.get(name)
    if cls is None:
        known = ", ".join(sorted(PROVIDER_REGISTRY))
        raise ProviderError(f"unknown provider {name!r}; expected one of: {known}")
    return cls(model=model, **kwargs)  # type: ignore[arg-type]
