# Multi-stage build for Python FastAPI backend
# Stage 1: Builder — compile dependencies
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and pre-compile wheels
COPY requirements.txt .
RUN pip install --user --no-warn-script-location --compile -r requirements.txt


# Stage 2: Runtime — minimal production image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install only runtime dependencies (curl for healthcheck, psycopg2 libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy compiled Python packages from builder to /usr/local
COPY --from=builder /root/.local /usr/local

# Copy application source
COPY app/      ./app/
COPY alembic/  ./alembic/
COPY alembic.ini .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Create non-root user
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup --no-create-home appuser

# Change ownership of app directory to appuser
RUN chown -R appuser:appgroup /app

# /usr/local/bin is already in PATH and readable by all users
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
