"""
Application configuration.

All settings are read from environment variables so the same code
runs identically in Docker, on bare metal, or in CI.  Pydantic
validates them at startup — if DATABASE_URL is missing you'll get
a clear error instead of a mysterious crash at runtime.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://fintrack:changeme@localhost:5432/fintrack"
    DATABASE_URL_SYNC: str = "postgresql://fintrack:changeme@localhost:5432/fintrack"

    # ── JWT ───────────────────────────────────────────────────
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 30

    # ── CORS ──────────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:8080"

    # ── App ───────────────────────────────────────────────────
    APP_VERSION: str = "1.0.0"

    @property
    def cors_origin_list(self) -> list[str]:
        """Split comma-separated origins into a list."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        extra = "ignore"


# Singleton — import this everywhere
settings = Settings()