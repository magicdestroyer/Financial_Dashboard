# Financial Dashboard

A containerized full-stack financial portfolio tracking application. Built with FastAPI (Python), PostgreSQL, and a static frontend served by Nginx.

## Features

- **User Authentication** — JWT-based login with secure password hashing (bcrypt)
- **Portfolio Management** — Track multiple investment accounts and holdings
- **Transaction History** — Record and analyze buy/sell transactions
- **Price Tracking** — Real-time price updates via Yahoo Finance proxy
- **Audit Logging** — Complete audit trail for compliance
- **Responsive UI** — Web frontend with security headers and SPA fallback

## Prerequisites

- Docker and Docker Compose 2.20+
- 2+ GB available disk space
- 512 MB RAM minimum (1+ GB recommended)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd Financial_Dashboard
cp .env.example .env
```

Edit `.env` with secure values:
```env
DB_PASSWORD=your-strong-db-password
JWT_SECRET=your-random-jwt-secret
CORS_ORIGINS=http://localhost:8080,http://localhost:3000
```

### 2. Start Services

```bash
# Build and start all services
docker compose up -d --build

# Check service health
docker compose ps

# View logs
docker compose logs -f backend
```

### 3. Access the Application

- **Frontend**: http://localhost:8080
- **API Docs**: http://localhost:8080/api/docs
- **Database**: `psql -h 127.0.0.1 -U fintrack -d fintrack`

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Nginx (port 8080)              │
│              Static SPA + API Proxy             │
└──────────────────────┬──────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
   ┌─────────────┐          ┌──────────────────┐
   │  Frontend   │          │  FastAPI Backend │
   │  (static)   │          │  (uvicorn)       │
   └─────────────┘          └────────┬─────────┘
                                     │
                            ┌────────▼────────┐
                            │   PostgreSQL    │
                            │  (port 5432)    │
                            └─────────────────┘
```

### Service Topology

- **Frontend (fintrack-web)**: Serves static assets, proxies `/api/*` to backend, enforces SPA routing
- **Backend (fintrack-api)**: Uvicorn server on port 8000, handles API requests, runs Alembic migrations on startup
- **Database (fintrack-db)**: PostgreSQL 16 Alpine, persists data to named volume `pgdata`
- **Network**: All services communicate via bridge network `fintrack-net`

## Development

### Run with Live Reload

Uncomment the volumes section in `compose.yaml` under the `backend` service:

```yaml
volumes:
  - ./backend/app:/app/app
```

Then restart:
```bash
docker compose up backend --build
```

Changes to `backend/app/**/*.py` will trigger Uvicorn to reload.

### Run Tests

```bash
# Install dev dependencies
pip install -r backend/requirements-dev.txt

# Run pytest
pytest backend/tests -v --cov=backend/app

# Or run inside container
docker compose run --rm backend pytest -v
```

### Database Migrations

Migrations run automatically on backend startup via `entrypoint.sh`. To create a new migration:

```bash
# Inside container
docker compose exec backend alembic revision --autogenerate -m "Add new_column to users"

# Review the generated migration in backend/alembic/versions/
# Then restart the backend to apply
docker compose restart backend
```

### Linting

```bash
# Format code
black backend/app

# Lint
ruff check backend/app --fix

# Type check
mypy backend/app
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_PASSWORD` | `107692_CBarson` | PostgreSQL password (CHANGE THIS!) |
| `JWT_SECRET` | `107692_CBarson_ETTS_arson_2268_` | JWT signing secret (CHANGE THIS!) |
| `JWT_ACCESS_EXPIRE_MINUTES` | `30` | JWT access token TTL in minutes |
| `JWT_REFRESH_EXPIRE_DAYS` | `30` | JWT refresh token TTL in days |
| `CORS_ORIGINS` | `http://localhost:8080,http://localhost:3000` | Allowed CORS origins |

## Database Schema

### Tables

- **users** — User accounts with auth credentials
- **accounts** — Investment accounts (brokerage, 401k, IRA, etc.)
- **holdings** — Current positions in securities
- **transactions** — Historical buy/sell trades
- **price_history** — Daily OHLCV data for charting
- **audit_logs** — Security and compliance audit trail

See `backend/alembic/versions/` for full schema definitions.

## Security

- Non-root containers (FastAPI and Nginx run as unprivileged users)
- Secrets via environment variables (never committed)
- JWT-based authentication
- CORS restrictions to frontend domain
- Database accessible only on localhost
- Audit logging for compliance
- Security headers (X-Frame-Options, X-Content-Type-Options, CSP ready)

## Troubleshooting

### Backend fails to start

```bash
docker compose logs backend
```

Common issues:
- Database not ready: Check `docker compose ps` — wait for `postgres` to be healthy
- Migration failed: Review logs, check `backend/alembic/versions/`
- Port 8000 already in use: Change compose port binding or kill conflicting process

### Database connection issues

```bash
# Test connection from host
psql -h 127.0.0.1 -U fintrack -d fintrack

# Test from container
docker compose exec backend psql -h postgres -U fintrack -d fintrack
```

### Nginx returns 502 Bad Gateway

- Backend container has crashed: `docker compose logs backend`
- Network issue: Verify `fintrack-net` exists: `docker network ls | grep fintrack`

## Production Deployment

For production, override these settings:

```yaml
# compose.override.yml
services:
  backend:
    environment:
      JWT_SECRET: ${JWT_SECRET:?Error: JWT_SECRET required}
      DB_PASSWORD: ${DB_PASSWORD:?Error: DB_PASSWORD required}
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
  postgres:
    environment:
      POSTGRES_PASSWORD: ${DB_PASSWORD:?Error: DB_PASSWORD required}
    restart: always
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
```

Then deploy with:
```bash
docker compose -f compose.yaml -f compose.override.yml up -d
```

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test: `pytest backend/tests`
3. Format and lint: `black . && ruff check . --fix`
4. Commit: `git commit -m "feat: description"`
5. Push and open a PR

## License

MIT — See LICENSE file for details

## Support

For issues or questions, open a GitHub issue or contact the team.
