"""
Yahoo Finance proxy — avoids CORS issues on the frontend.
All results are cached server-side for 60 seconds.
"""

from fastapi import APIRouter, Query

from app.utils.yahoo_finance import fetch_quote, fetch_chart, search_tickers

router = APIRouter()


@router.get("/quote")
async def proxy_quote(ticker: str = Query(..., description="Stock ticker")):
    result = await fetch_quote(ticker.upper())
    if not result:
        return {"error": "Could not fetch quote", "ticker": ticker}
    return result


@router.get("/chart")
async def proxy_chart(
    ticker: str = Query(...),
    range: str = Query("1d", alias="range"),
    interval: str = Query("5m"),
):
    points = await fetch_chart(ticker.upper(), range, interval)
    if points is None:
        return {"points": [], "error": "Could not fetch chart data"}
    return {"points": points}


@router.get("/search")
async def proxy_search(q: str = Query(..., min_length=1)):
    results = await search_tickers(q.upper())
    return results