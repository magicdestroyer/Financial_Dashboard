#!/bin/sh
# entrypoint.sh
#
# Runs Alembic migrations to head before starting the application.
# Keeping this separate from CMD means:
#   - Migrations run once on startup, not on every signal/restart
#   - You can override CMD in docker-compose (e.g. for a worker) without
#     accidentally skipping migrations
#   - The migration exit code will stop the container if something goes wrong,
#     rather than silently starting a broken app

set -e  # exit immediately if any command fails

echo "==> Running database migrations..."
alembic upgrade head

echo "==> Migrations complete. Starting server..."
exec "$@"
