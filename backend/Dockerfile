# Multi-stage build for optimal size
FROM python:3.13-alpine

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /api

# First stage: sync dependencies *without* project code (fast layer cache)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

ADD . /api

# Second stage: install project into managed environment
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen


EXPOSE 8000

# Healthcheck optional
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health/', timeout=5)" || exit 1

CMD ["uv", "run", "uvicorn", "api:app", "--workers", "5", "--host", "0.0.0.0", "--port", "8000"]