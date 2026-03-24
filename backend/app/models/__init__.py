"""
Import all models here so Alembic can discover them.
"""

from app.models.user import User
from app.models.settings import UserSettings
from app.models.budget import BudgetYear, BudgetItem, SavingsBucket
from app.models.hysa import HysaAccount, HysaLog, HysaSnapshot
from app.models.stock import StockHolding, StockLot, StockPriceHistory, PortfolioSnapshot

__all__ = [
    "User",
    "UserSettings",
    "BudgetYear",
    "BudgetItem",
    "SavingsBucket",
    "HysaAccount",
    "HysaLog",
    "HysaSnapshot",
    "StockHolding",
    "StockLot",
    "StockPriceHistory",
    "PortfolioSnapshot",
]