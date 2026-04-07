"""
Yahoo Finance proxy — avoids CORS issues on the frontend.
All results are cached server-side for 60 seconds.
Requires authentication to prevent quota abuse.
"""

from fastapi import APIRouter, Query, Depends
from app.dependencies import get_current_user
from app.utils.yahoo_finance import fetch_quote, fetch_chart, search_tickers

router = APIRouter()


@router.get("/quote")
async def proxy_quote(ticker: str = Query(..., description="Stock ticker"), _=Depends(get_current_user)):
    result = await fetch_quote(ticker.upper())
    if not result:
        return {"error": "Could not fetch quote", "ticker": ticker}
    return result


@router.get("/chart")
async def proxy_chart(
    ticker: str = Query(...),
    range: str = Query("1d", alias="range"),
    interval: str = Query("5m"),
    _=Depends(get_current_user)
):
    points = await fetch_chart(ticker.upper(), range, interval)
    if points is None:
        return {"points": [], "error": "Could not fetch chart data"}
    return {"points": points}


@router.get("/search")
async def proxy_search(q: str = Query(..., min_length=1), _=Depends(get_current_user)):
    results = await search_tickers(q.upper())
    return results


@router.get("/ticker/lookup")
async def ticker_lookup(q: str = Query(..., description="Stock ticker or company name"), _=Depends(get_current_user)):
    """
    Lookup a ticker by symbol or company name. Returns quote data.
    Alias for /proxy/quote with frontend-friendly response shape.
    """
    quote = await fetch_quote(q.upper())
    if not quote:
        return {"error": "Ticker not found", "q": q}
    # Wrap quote in result field for frontend compatibility
    return {"result": quote}
