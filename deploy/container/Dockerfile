ARG PYTHON_IMAGE=python:3.15.2-slim-trixie@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928

FROM ${PYTHON_IMAGE} AS builder

COPY --from=ghcr.io/astral-sh/uv:0.13.9@sha256:d3b601f0c7b118bc1753febf7c41cc80981df678445e0254284eecf84db79a7d /uv /uvx /bin/

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src ./src

RUN uv sync --frozen --no-dev --no-editable

FROM ${PYTHON_IMAGE} AS runtime

LABEL org.opencontainers.image.source="https://github.com/pueo-labs/recon" \
      org.opencontainers.image.licenses="Apache-2.0"

RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin recon \
    && mkdir -p /home/recon/.recon \
    && chown -R 10001:10001 /home/recon

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RECON_REMOTE_HOST=0.0.0.0 \
    RECON_REMOTE_PORT=8080

USER 10001:10001
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('RECON_REMOTE_PORT', '8080') + '/health', timeout=2).read()"

ENTRYPOINT ["python", "-m", "recon_tool.remote_server"]
