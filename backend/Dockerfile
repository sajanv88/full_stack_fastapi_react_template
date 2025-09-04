# Multi-stage build: Node.js for frontend, Python for backend
FROM node:22-alpine AS frontend-builder

# Set work directory for frontend
WORKDIR /frontend

# Install pnpm globally
RUN npm install -g pnpm

# Copy frontend package files
COPY frontend/app/package.json ./
COPY frontend/app/pnpm-lock.yaml ./

# Install frontend dependencies with pnpm
RUN pnpm install --frozen-lockfile --prod

# Copy frontend source code
COPY frontend/app/ .

# Build frontend for production
RUN pnpm run build

# Production stage: Python backend with built frontend
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ .

# Copy built frontend from the previous stage
COPY --from=frontend-builder /frontend/dist ./static

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/users/', timeout=10)"

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
