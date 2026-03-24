"""
Server-side Yahoo Finance fetcher.

This eliminates the CORS proxy hack on the frontend.
Results are cached in-memory for 60 seconds to avoid rate limits.
"""

import time
from typing import Optional

import httpx

# Simple in-memory cache: { key: (timestamp, data) }
_cache: dict[str, tuple[float, dict]] = {}
CACHE_TTL = 60  # seconds


def _get_cached(key: str) -> Optional[dict]:
    entry = _cache.get(key)
    if entry and (time.time() - entry[0]) < CACHE_TTL:
        return entry[1]
    return None


def _set_cached(key: str, data: dict):
    _cache[key] = (time.time(), data)


async def fetch_quote(ticker: str) -> dict | None:
    """Fetch current price + change for a ticker."""
    key = f"quote:{ticker}"
    cached = _get_cached(key)
    if cached:
        return cached

    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        f"?range=1d&interval=1m&includePrePost=false"
    )
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        meta = data.get("chart", {}).get("result", [{}])[0].get("meta", {})
        price = meta.get("regularMarketPrice")
        prev = meta.get("chartPreviousClose") or meta.get("previousClose")
        change_pct = ((price - prev) / prev * 100) if (price and prev) else 0

        result = {
            "ticker": ticker,
            "name": meta.get("shortName", ticker),
            "price": price,
            "changePct": round(change_pct, 4),
            "exchange": meta.get("exchangeName"),
            "quoteType": meta.get("instrumentType"),
        }
        _set_cached(key, result)
        return result
    except Exception:
        return None


async def fetch_chart(ticker: str, range_str: str, interval: str) -> list[dict] | None:
    """Fetch OHLC chart data."""
    key = f"chart:{ticker}:{range_str}:{interval}"
    cached = _get_cached(key)
    if cached:
        return cached

    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        f"?range={range_str}&interval={interval}&includePrePost=false"
    )
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        result_data = data.get("chart", {}).get("result", [{}])[0]
        timestamps = result_data.get("timestamp", [])
        quotes = result_data.get("indicators", {}).get("quote", [{}])[0]

        points = []
        for i, ts in enumerate(timestamps):
            o = quotes.get("open", [None])[i] if i < len(quotes.get("open", [])) else None
            h = quotes.get("high", [None])[i] if i < len(quotes.get("high", [])) else None
            l = quotes.get("low", [None])[i] if i < len(quotes.get("low", [])) else None
            c = quotes.get("close", [None])[i] if i < len(quotes.get("close", [])) else None
            if c is not None:
                points.append({
                    "timestamp": ts * 1000,
                    "open": o, "high": h, "low": l, "close": c,
                })

        _set_cached(key, points)
        return points
    except Exception:
        return None


async def search_tickers(query: str) -> list[dict]:
    """Search for ticker symbols."""
    key = f"search:{query}"
    cached = _get_cached(key)
    if cached:
        return cached

    url = (
        f"https://query1.finance.yahoo.com/v1/finance/search"
        f"?q={query}&quotesCount=8&newsCount=0"
    )
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        results = [
            {
                "symbol": q.get("symbol"),
                "name": q.get("longname") or q.get("shortname", ""),
                "exchange": q.get("exchange"),
                "quoteType": q.get("quoteType"),
            }
            for q in data.get("quotes", [])
            if q.get("quoteType") in ("EQUITY", "ETF", "MUTUALFUND")
        ]
        _set_cached(key, results)
        return results
    except Exception:
        return []