"""
FastAPI application entry point.

This file wires together:
  - CORS (so the browser can call /api from a different port)
  - All routers (auth, budgets, hysa, stocks, etc.)
  - The health check endpoint
  - Lifespan events (startup/shutdown)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine

# Import routers
from app.routers import auth, settings as settings_router
from app.routers import budgets, hysa, stocks, snapshots, proxy, export, data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once on startup and once on shutdown.
    Good place for connection pool warmup or cleanup.
    """
    # Startup
    yield
    # Shutdown — dispose of the connection pool cleanly
    await engine.dispose()


app = FastAPI(
    title="FinTrack API",
    version=settings.APP_VERSION,
    docs_url="/api/docs",       # Swagger UI at /api/docs
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────
# This lets the Nginx-served frontend (port 8080) call the API
# (port 8000) without the browser blocking it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── ROUTERS ───────────────────────────────────────────────────
app.include_router(auth.router,              prefix="/api/auth",     tags=["Auth"])
app.include_router(settings_router.router,   prefix="/api/settings", tags=["Settings"])
app.include_router(budgets.router,           prefix="/api/budgets",  tags=["Budgets"])
app.include_router(hysa.router,              prefix="/api/hysa",     tags=["HYSA"])
app.include_router(stocks.router,            prefix="/api/stocks",   tags=["Stocks"])
app.include_router(snapshots.router,         prefix="/api/snapshots",tags=["Snapshots"])
app.include_router(proxy.router,             prefix="/api/proxy",    tags=["Proxy"])
app.include_router(data.router,              prefix="/api",          tags=["Data"])
app.include_router(export.router,            prefix="/api",          tags=["Export"])


# ── HEALTH CHECK ──────────────────────────────────────────────
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Quick check that the API and database are alive."""
    from sqlalchemy import text
    from app.database import async_session

    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"

    return {
        "status": "ok" if db_status == "connected" else "degraded",
        "db": db_status,
        "version": settings.APP_VERSION,
    }
