# Dockerfile optimized for Google Cloud Run
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

# Create model cache folder
RUN mkdir -p /app/models /tmp

# Copy application code
COPY services/fastapi/app /app/app

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PORT=8080

# Expose port (Cloud Run will override this)
EXPOSE 8080

# Run application with PORT from environment
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}