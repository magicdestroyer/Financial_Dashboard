FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies needed for psycopg2
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Create setup.py to make app importable as a package
RUN cat > setup.py << 'EOF'
from setuptools import setup, find_packages
setup(
    name="fintrack",
    version="0.1.0",
    packages=find_packages(),
)
EOF

# Install app in editable mode for proper import resolution
RUN pip install -e .

EXPOSE 8000

# Run Alembic migrations first, then start the server
# PYTHONPATH set as fallback for module discovery
CMD ["sh", "-c", "PYTHONPATH=/app alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2"]
