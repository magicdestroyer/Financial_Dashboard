FROM python:3.11-slim

# Prevent .pyc files and force stdout/stderr flush
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Keep pip quiet and don't write a cache inside the image
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System deps needed to compile psycopg2
# Kept in a single layer and cleaned up immediately to minimise image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        # curl is used by the HEALTHCHECK below
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps before copying source so this layer is cached as long
# as requirements.txt doesn't change
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application source
COPY app/      ./app/
COPY alembic/  ./alembic/
COPY alembic.ini .

# Copy the entrypoint script and make it executable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Run as a non-root user — principle of least privilege
RUN addgroup --system appgroup && \
    adduser  --system --ingroup appgroup --no-create-home appuser
USER appuser

EXPOSE 8000

# Liveness check — hits the /api/health endpoint we already have
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Entrypoint runs migrations first, then hands off to CMD
ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]