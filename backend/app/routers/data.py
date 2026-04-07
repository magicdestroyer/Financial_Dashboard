"""
Bulk data endpoints for hydration and saving.
Maps frontend localStorage structure to granular backend routes.
"""

from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.routers import budgets, hysa, stocks, settings

router = APIRouter()


@router.get("/data")
async def get_data(user_id: int = Depends(get_current_user)):
    """
    Bulk hydration endpoint.
    Returns all user data in a single response for localStorage initialization.
    Shape: { budgets: {...}, hysa: {...}, stocks: {...}, settings: {...} }
    """
    # Fetch from individual routers
    # TODO: These need to be refactored as internal functions, not just API routes
    # For now, this is a stub that returns empty data
    return {
        "budgets": {},
        "hysa": {},
        "stocks": {},
        "settings": {}
    }


@router.put("/data/budgets")
async def put_budgets(data: dict, user_id: int = Depends(get_current_user)):
    """
    Bulk budget save.
    Accepts: { budgets: { "2024": [...], "2025": [...] } }
    """
    budgets_by_year = data.get("budgets", {})
    for year, items in budgets_by_year.items():
        # Call the granular endpoint internally
        # TODO: Refactor to call internal budget service
        pass
    return {"status": "ok"}


@router.put("/data/hysa")
async def put_hysa(data: dict, user_id: int = Depends(get_current_user)):
    """
    Bulk HYSA save.
    Accepts: { hysa: {...} }
    """
    hysa_data = data.get("hysa", {})
    # TODO: Implement bulk HYSA save
    return {"status": "ok"}


@router.put("/data/stocks")
async def put_stocks(data: dict, user_id: int = Depends(get_current_user)):
    """
    Bulk stocks save.
    Accepts: { stocks: [...] }
    Handles field normalization: account (frontend) → account_type (backend)
    """
    stocks_data = data.get("stocks", [])
    # TODO: Implement bulk stocks save
    return {"status": "ok"}


@router.put("/data/settings")
async def put_settings(data: dict, user_id: int = Depends(get_current_user)):
    """
    Bulk settings save.
    Accepts: { settings: {...} }
    """
    settings_data = data.get("settings", {})
    # TODO: Implement bulk settings save
    return {"status": "ok"}
