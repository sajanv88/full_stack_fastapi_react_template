FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /api

COPY . /api/
RUN uv sync --frozen --no-cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*



# Copy backend application code
COPY api/ .


# Change ownership to non-root user
RUN chown -R appuser:appuser /api

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health/', timeout=10)"

# Run the application
CMD ["/api/.venv/bin/fastapi", "run", "api", "--port", "8000", "--host", "0.0.0.0"]
