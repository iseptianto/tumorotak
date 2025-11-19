# Dockerfile optimized for Google Cloud Run - Backend (FastAPI)
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY services/fastapi/requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --ignore-installed blinker==1.7.0 \
    && pip install --no-cache-dir -r /app/requirements.txt

# Create cache directories
RUN mkdir -p /tmp /app/models

# Copy application code
COPY services/fastapi/app /app/app

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PORT=8080
ENV PYTHONDONTWRITEBYTECODE=1

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app /tmp
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Run with uvicorn (production-ready ASGI server)
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1 --log-level info