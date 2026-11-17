"""Shared HTTP client context manager for lookup sources.

Includes SSRF protection with DNS rebinding defense: both literal IP addresses
and resolved hostnames are validated against a public-unicast policy before
connecting.

Includes retry logic for transient failures (429, 503) with exponential backoff.

The connection backend separately validates and pins numeric destinations at
socket creation. TLS verification and connection pooling retain the original
hostname, while DNS changes cannot redirect a validated connection internally.
"""

from __future__ import annotations

import asyncio
import ipaddress
import logging
import math
import socket
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any, Literal

import httpx

from recon_tool.http_backend import CoreHTTPTransport
from recon_tool.source_status import PUBLIC_ENDPOINT_PRIVATE_ADDRESS

logger = logging.getLogger("recon")

DEFAULT_TIMEOUT = 10.0
MAX_REDIRECTS = 5

# Retry configuration for transient HTTP errors (429 Too Many Requests, 503 Service Unavailable).
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 1.0  # seconds — doubles each retry (1s, 2s, 4s)
RETRYABLE_STATUS_CODES = frozenset({429, 503})

# Cumulative cap on retry sleeping for a single request. The per-attempt
# Retry-After is capped at 30s, but three attempts could otherwise stack
# to ~90s and consume most of the 120s aggregate resolve budget when an
# attacker-influenced endpoint returns 429 repeatedly. Bound the total.
_MAX_TOTAL_RETRY_SLEEP = 30.0

# Hard ceiling on a single HTTP response body. Several endpoints recon
# fetches have a host influenced by the looked-up domain owner
# (cse.<domain>, mta-sts.<domain>, the BIMI a= VMC URL, autodiscover
# redirects), and CT providers are third parties. resp.json() / resp.text
# buffer the whole body into memory, so without a cap a multi-GB response
# could OOM the process (or the MCP server). 10 MB is far above any
# legitimate response recon reads (CT JSON pages are bounded by their own
# entry caps; policy/config files are tiny).
#
# _MaxBytesStream counts the bytes recon reads off the wire, which are the
# COMPRESSED transfer bytes: httpx decodes Content-Encoding downstream of
# the transport stream, so the byte cap alone does NOT bound a gzip
# decompression bomb (a few MB of gzip expand to many GB after decode).
# recon defends that separately: it requests ``Accept-Encoding: identity``
# so a cooperating server sends the body uncompressed (making the raw cap
# the decoded cap), and refuses any response that still carries a
# compressing Content-Encoding via _RefusingStream, since an attacker-
# controlled host that ignores the identity request is the bomb vector.
_MAX_RESPONSE_BYTES = 10 * 1024 * 1024

# Content-Encoding values whose decoded body can be far larger than the
# transfer. recon requests identity and refuses a response carrying any of
# these rather than let httpx decode an attacker-sized payload past the cap.
_COMPRESSING_ENCODINGS = frozenset({"gzip", "x-gzip", "deflate", "br", "compress", "zstd"})

# IP networks that must never be reached via redirects (SSRF protection).
# Kept for explicit high-signal ranges and as a readability anchor; the
# predicate below also blocks all non-global or special-use IP literals.
# Covers loopback, private RFC1918, link-local, and cloud metadata ranges.
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),  # link-local / cloud metadata
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),  # IPv6 unique local
    ipaddress.ip_network("fe80::/10"),  # IPv6 link-local
    ipaddress.ip_network("fec0::/10"),  # deprecated IPv6 site-local
]


def _addr_is_blocked(addr: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Return True for any IP that is not globally routable unicast."""
    mapped = getattr(addr, "ipv4_mapped", None)
    if mapped is not None:
        return _addr_is_blocked(mapped)
    return (
        any(addr in net for net in _BLOCKED_NETWORKS)
        or not addr.is_global
        or addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_reserved
        or addr.is_multicast
        or addr.is_unspecified
    )


def _is_blocked_ip(addr_str: str) -> bool:
    """Check if an IP address string is private, internal, or special-use."""
    addr = _parse_ip_address(addr_str)
    if addr is None:
        return False
    return _addr_is_blocked(addr)


def _parse_ip_address(host: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    """Return a parsed IP literal, or None when *host* is a hostname."""
    try:
        return ipaddress.ip_address(host)
    except ValueError:
        return None


@dataclass(frozen=True, slots=True)
class DestinationRefusal:
    """Why destination validation refused a host, in operator wording.

    ``condition`` is ``unresolved_host`` (the name did not resolve, an
    availability failure) or ``private_address`` / ``no_hostname`` (a real
    policy refusal). The CLI groups these by condition into one summary line;
    see ``cli/collection_warnings.py``.
    """

    condition: Literal["unresolved_host", "private_address", "no_hostname"]
    host: str
    address: str | None = None

    def describe(self) -> str:
        """Return the one-line explanation used in logs and connect errors."""
        if self.condition == "unresolved_host":
            return f"could not resolve {self.host}"
        if self.condition == "no_hostname":
            return "skipped: request has no hostname"
        if self.address == self.host:
            return f"{self.host} skipped: a private address"
        return f"{self.host} skipped: resolves to a private address ({self.address})"


# Only fixed public collection endpoints can qualify the resolver view. A
# private target-owned address is a normal destination refusal.
_PUBLIC_COLLECTION_HOSTS = frozenset(
    {"login.microsoftonline.com", "accounts.google.com", "crt.sh", "api.certspotter.com"}
)
_REFUSAL_MARKERS: ContextVar[set[str] | None] = ContextVar("recon_refusal_markers", default=None)


@contextmanager
def collect_refusal_markers() -> Generator[set[str]]:
    """Collect transport observations from a single source and its child tasks."""
    markers: set[str] = set()
    token = _REFUSAL_MARKERS.set(markers)
    try:
        yield markers
    finally:
        _REFUSAL_MARKERS.reset(token)


def _log_refusal(refusal: DestinationRefusal) -> None:
    """Log a refusal once, with structured fields the CLI summary groups on."""
    markers = _REFUSAL_MARKERS.get()
    if markers is not None and refusal.condition == "private_address" and refusal.host in _PUBLIC_COLLECTION_HOSTS:
        markers.add(PUBLIC_ENDPOINT_PRIVATE_ADDRESS)
    logger.warning(
        "%s",
        refusal.describe(),
        extra={
            "recon_condition": refusal.condition,
            "recon_host": refusal.host,
            "recon_address": refusal.address,
        },
    )


def _refusal_for_answers(host: str, addrinfos: list[Any]) -> DestinationRefusal | None:
    """Admit a resolved answer only when every address is public unicast."""
    if not addrinfos:
        return DestinationRefusal("unresolved_host", host)
    for _family, _type, _proto, _canonname, sockaddr in addrinfos:
        ip_str = str(sockaddr[0])
        if _parse_ip_address(ip_str) is None or _is_blocked_ip(ip_str):
            return DestinationRefusal("private_address", host, ip_str)
    return None


async def _destination_refusal_async(host: str) -> DestinationRefusal | None:
    """Async destination validation; returns the refusal, or None to admit.

    Two-layer defense against SSRF and DNS rebinding:
    1. If the host is a literal IP address, check it directly.
    2. Resolve hostnames in the bound caller-safe DNS view, or via non-blocking
       OS resolution for trusted operator collection, and check every address.

    A host that is non-public, or that cannot be resolved and therefore cannot
    be validated safely, is refused. Hostname refusals are logged once.
    """
    from recon_tool.network_policy import selected_addresses

    selected = await selected_addresses(host)
    if selected is not None:
        refusal = _refusal_for_answers(host, [(0, 0, 0, "", (address, 0)) for address in selected])
        if refusal is not None:
            _log_refusal(refusal)
        return refusal

    # Layer 1: literal IP check (fast path, no I/O)
    addr = _parse_ip_address(host)
    if addr is not None:
        return DestinationRefusal("private_address", host, host) if _addr_is_blocked(addr) else None

    # Layer 2: resolve hostname in thread pool and check all returned IPs
    if not host:
        refusal: DestinationRefusal | None = DestinationRefusal("no_hostname", host)
    else:
        try:
            loop = asyncio.get_running_loop()
            addrinfos = await loop.getaddrinfo(host, None, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM)
        except (socket.gaierror, OSError):
            refusal = DestinationRefusal("unresolved_host", host)
        else:
            refusal = _refusal_for_answers(host, list(addrinfos))
    if refusal is not None:
        _log_refusal(refusal)
    return refusal


async def _is_private_ip_async(host: str) -> bool:  # pyright: ignore[reportUnusedFunction]
    """Return True when destination validation refuses *host* (async).

    The boolean form of ``_destination_refusal_async``, kept for callers and
    tests that need only the decision; the transport uses the refusal itself
    so its error names the condition.
    """
    return await _destination_refusal_async(host) is not None


async def _public_addresses_async(host: str) -> tuple[str, ...]:
    """Resolve once and admit the complete answer before any socket is opened."""
    from recon_tool.network_policy import selected_addresses

    selected = await selected_addresses(host)
    if selected is not None:
        return (
            ()
            if any(_parse_ip_address(address) is None or _is_blocked_ip(address) for address in selected)
            else selected
        )
    address = _parse_ip_address(host)
    if address is not None:
        return () if _addr_is_blocked(address) else (str(address),)
    if not host:
        return ()
    try:
        answers = await asyncio.get_running_loop().getaddrinfo(
            host, None, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM
        )
    except OSError:
        return ()
    addresses: list[str] = []
    for _family, _type, _proto, _canonname, sockaddr in answers:
        address = _parse_ip_address(str(sockaddr[0]))
        if address is None or _addr_is_blocked(address):
            return ()
        normalized = str(address)
        if normalized not in addresses:
            addresses.append(normalized)
    return tuple(addresses)


def _is_private_ip(host: str) -> bool:  # pyright: ignore[reportUnusedFunction]
    """Synchronous check if a host must be refused by destination validation.

    Called only by tests/test_http.py (which is why pyright flags it unused
    from the production scan). Production uses the async variant via
    _SSRFSafeTransport; tests need a sync form to exercise the blocklist
    without an event loop. Kept colocated with _BLOCKED_NETWORKS so the two
    can't drift apart.
    """
    # Layer 1: literal IP check (fast path)
    addr = _parse_ip_address(host)
    if addr is not None:
        return _addr_is_blocked(addr)

    # Layer 2: resolve hostname and check all returned IPs
    if not host:
        refusal: DestinationRefusal | None = DestinationRefusal("no_hostname", host)
    else:
        try:
            addrinfos = socket.getaddrinfo(host, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        except (socket.gaierror, OSError):
            refusal = DestinationRefusal("unresolved_host", host)
        else:
            refusal = _refusal_for_answers(host, list(addrinfos))
    if refusal is not None:
        _log_refusal(refusal)
    return refusal is not None


class _MaxBytesStream(httpx.AsyncByteStream):
    """Wrap a response byte stream and abort once it exceeds *max_bytes*.

    Counts bytes as the client reads the body (resp.json() / resp.text /
    resp.aread() all iterate this stream) and raises once the cap is
    exceeded, so a hostile endpoint cannot force recon to buffer an
    unbounded body into memory. Closing delegates to the wrapped stream.
    """

    def __init__(self, stream: httpx.AsyncByteStream, max_bytes: int) -> None:
        self._stream = stream
        self._max_bytes = max_bytes

    async def __aiter__(self) -> AsyncGenerator[bytes]:
        total = 0
        async for chunk in self._stream:
            total += len(chunk)
            if total > self._max_bytes:
                raise httpx.ReadError(f"response body exceeded {self._max_bytes}-byte cap")
            yield chunk

    async def aclose(self) -> None:
        await self._stream.aclose()


class _RefusingStream(httpx.AsyncByteStream):
    """A response stream that refuses to yield a body, raising on first read.

    Installed when a response carries a compressing Content-Encoding despite
    recon's ``Accept-Encoding: identity`` request. Reading the body would let
    httpx decode an attacker-controlled payload whose decoded size the transfer
    cap does not bound (a decompression bomb), so we refuse before any decode.
    The caller's body read raises httpx.ReadError and the source degrades
    cleanly, exactly like any other transport failure.
    """

    def __init__(self, encoding: str) -> None:
        self._encoding = encoding

    async def __aiter__(self) -> AsyncGenerator[bytes]:
        msg = f"refusing {self._encoding!r}-encoded response (identity requested; possible decompression bomb)"
        raise httpx.ReadError(msg)
        yield b""  # pragma: no cover - unreachable; makes this an async generator

    async def aclose(self) -> None:
        return None


class _SSRFSafeTransport(CoreHTTPTransport):
    """Transport wrapper that blocks requests to private/internal IPs.

    Intercepts each request before it hits the network and rejects any
    whose host resolves to a blocked IP range. This prevents SSRF via
    open redirects on upstream endpoints, including DNS rebinding attacks
    where a hostname resolves to an internal IP.

    It also bounds the response body two ways: an oversized identity body is
    aborted mid-read by _MaxBytesStream, and a response that carries a
    compressing Content-Encoding (despite recon's ``Accept-Encoding: identity``
    request) is refused outright by _RefusingStream, since the byte cap counts
    compressed transfer bytes and cannot bound a decompression bomb. Uses async
    DNS resolution to avoid blocking the event loop. Socket creation repeats
    destination admission and pins the accepted numeric address.
    """

    def __init__(self) -> None:
        super().__init__(_public_addresses_async)

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        host = request.url.host or ""
        timeout = request.extensions.get("timeout", {}).get("connect", DEFAULT_TIMEOUT)
        try:
            async with asyncio.timeout(timeout):
                refusal = await _destination_refusal_async(host)
        except TimeoutError as exc:
            raise httpx.ConnectTimeout("Timed out validating destination", request=request) from exc
        if refusal is not None:
            # A name that does not resolve is an availability failure, not a
            # policy event; only a non-public destination is an SSRF refusal.
            reason = (
                f"{refusal.describe()}, so the destination could not be validated"
                if refusal.condition == "unresolved_host"
                else f"SSRF blocked, {refusal.describe()}"
            )
            raise httpx.ConnectError(reason, request=request)
        response = await super().handle_async_request(request)
        if isinstance(response.stream, httpx.AsyncByteStream):
            stream = response.stream
            encodings = {e.strip() for e in response.headers.get("content-encoding", "").lower().split(",")}
            compressing = encodings & _COMPRESSING_ENCODINGS
            if compressing:
                # Server compressed despite our identity request. Decoding could
                # be a decompression bomb (the byte cap counts compressed bytes),
                # so release the original transport stream immediately and
                # refuse the body instead of buffering the decode.
                await stream.aclose()
                response.stream = _RefusingStream(", ".join(sorted(compressing)))
            else:
                response.stream = _MaxBytesStream(stream, _MAX_RESPONSE_BYTES)
        return response


class _RetryTransport(httpx.AsyncBaseTransport):
    """Transport wrapper that retries on 429/503 with exponential backoff.

    Wraps another transport (typically _SSRFSafeTransport) and adds retry
    logic for transient server errors. Respects Retry-After headers when present.

    NOTE: Only safe for requests with non-streaming bodies (bytes content).
    Streaming request bodies would be consumed on the first attempt and empty
    on retry. All current callers use content= (bytes), not stream=.
    """

    def __init__(self, wrapped: httpx.AsyncBaseTransport) -> None:
        super().__init__()
        self._wrapped = wrapped

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        last_response: httpx.Response | None = None
        total_slept = 0.0
        for attempt in range(MAX_RETRIES + 1):
            response = await self._wrapped.handle_async_request(request)
            if response.status_code not in RETRYABLE_STATUS_CODES:
                return response
            last_response = response
            if attempt < MAX_RETRIES:
                # Respect Retry-After header if present, otherwise exponential backoff.
                # Retry-After can be seconds (numeric) or HTTP-date (string).
                # We only parse numeric values; date-format falls through to backoff.
                # Headers are buffered, so reading them before any aclose() is safe.
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    try:
                        parsed_delay = float(retry_after)
                        if not math.isfinite(parsed_delay) or parsed_delay < 0.0:
                            raise ValueError("Retry-After must be finite and non-negative")
                        delay = min(parsed_delay, 30.0)
                    except ValueError:
                        delay = RETRY_BACKOFF_BASE * (2**attempt)
                else:
                    delay = RETRY_BACKOFF_BASE * (2**attempt)
                # Bound cumulative sleeping so repeated 429s on an
                # attacker-influenced endpoint cannot stack toward the
                # aggregate resolve budget. Once the total cap is reached,
                # stop retrying and return this response with its body still
                # readable: do not close the response we are about to return.
                remaining_sleep = max(0.0, _MAX_TOTAL_RETRY_SLEEP - total_slept)
                if remaining_sleep <= 0.0:
                    break
                delay = min(delay, remaining_sleep)
                # A retry will follow, so close this intermediate response's
                # stream to avoid a resource leak before fetching the next one.
                await response.aclose()
                total_slept += delay
                logger.debug(
                    "HTTP %d from %s, retrying in %.1fs (attempt %d/%d)",
                    response.status_code,
                    request.url.host,
                    delay,
                    attempt + 1,
                    MAX_RETRIES,
                )
                if delay > 0.0:
                    await asyncio.sleep(delay)
        # Exhausted retries — return the last response so caller sees the status code.
        # last_response is guaranteed non-None here because MAX_RETRIES >= 1 means
        # the loop body executes at least twice, and last_response is set on every
        # iteration that reaches the retryable branch.
        if last_response is None:  # pragma: no cover — defensive, should never happen
            raise httpx.ConnectError("Retry loop completed without a response")
        return last_response

    async def aclose(self) -> None:
        await self._wrapped.aclose()


def _user_agent() -> str:
    """Build User-Agent string with the actual package version."""
    from recon_tool import __version__

    return f"recon-tool/{__version__} (domain-intelligence; +https://github.com/recon-tool)"


@asynccontextmanager
async def http_client(
    provided: httpx.AsyncClient | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    retry_transient: bool = True,
) -> AsyncGenerator[httpx.AsyncClient]:
    """Yield an httpx.AsyncClient — reuses the provided one or creates a new one.

    If a client is provided, it is yielded as-is (caller owns lifecycle).
    If no client is provided, a new one is created with SSRF-safe defaults and closed on exit.

    When ``retry_transient`` is False, the _RetryTransport wrapper is skipped.
    Use this for callers whose own application code handles 429 / 503 — the
    CT providers (CertSpotter) are the primary example: they break the
    pagination loop on 429 and return partial data, so the transport-level
    retry (3 × 30s backoff = 90s) only adds pure latency and burns the
    aggregate resolve budget on rate-limited targets.
    """
    if provided is not None:
        yield provided
    else:
        base_transport: httpx.AsyncBaseTransport = _SSRFSafeTransport()
        transport: httpx.AsyncBaseTransport = (
            _RetryTransport(wrapped=base_transport) if retry_transient else base_transport
        )
        client = httpx.AsyncClient(
            transport=transport,
            timeout=timeout,
            # Request identity (uncompressed) so a cooperating server's body is
            # bounded by the same _MAX_RESPONSE_BYTES cap that counts wire bytes.
            # A host that ignores this and compresses anyway is refused by the
            # transport (decompression-bomb guard); see _SSRFSafeTransport.
            headers={"User-Agent": _user_agent(), "Accept-Encoding": "identity"},
            follow_redirects=True,
            max_redirects=MAX_REDIRECTS,
        )
        try:
            yield client
        finally:
            await client.aclose()
