# Multi-stage build for optimal size
FROM python:3.13-alpine AS builder

# Install uv for dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install build dependencies (only needed during build)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev

# Set work directory
WORKDIR /api

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv sync in a virtual environment
RUN uv sync --frozen --no-dev

# Production stage - minimal runtime image
FROM python:3.13-alpine AS runtime

# Install only runtime dependencies
RUN apk add --no-cache \
    libffi \
    openssl \
    ca-certificates && \
    rm -rf /var/cache/apk/*

# Create non-root user
RUN addgroup -g 1000 appuser && \
    adduser -u 1000 -G appuser -s /bin/sh -D appuser

# Copy virtual environment from builder
COPY --from=builder /api/.venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/api"

# Set work directory
WORKDIR /api

# Copy only application code (exclude unnecessary files)
COPY --chown=appuser:appuser api/ ./api/
COPY --chown=appuser:appuser pyproject.toml ./

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Lightweight health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health/', timeout=5)" || exit 1

# Run the application
CMD ["python", "-m", "fastapi", "run", "api", "--port", "8000", "--host", "0.0.0.0"]
