"""Yahoo Finance v8 chart API — data fetching for stock analysis.

Reliable free data source. No API key required. Uses the v8 chart endpoint
which is not officially documented but consistently available.

Endpoints:
  /v8/finance/chart/{ticker}?range={range}&interval={interval}

Works for: equities, indices (^GSPC, ^IXIC, ^VIX), ETFs.
Does NOT work for: fundamentals (v7/v10 endpoints are dead as of Aug 2026).

Usage:
  from data.yahoo import get_quote, get_history, scan_tickers
"""

import json
import time
import urllib.request
from typing import Optional

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"


def _fetch(url: str) -> Optional[dict]:
    """Fetch JSON from Yahoo Finance API."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def get_quote(ticker: str) -> Optional[dict]:
    """Get current price, 52-week high/low, and meta for a ticker.

    Returns dict with keys: price, hi52, lo52, symbol, currency
    """
    url = f"{BASE_URL}/{ticker}?range=5d&interval=1d"
    data = _fetch(url)
    if not data or "chart" not in data or "result" not in data["chart"]:
        return None

    result = data["chart"]["result"]
    if not result:
        return None

    meta = result[0].get("meta", {})
    return {
        "symbol": meta.get("symbol", ticker),
        "price": meta.get("regularMarketPrice"),
        "hi52": meta.get("fiftyTwoWeekHigh"),
        "lo52": meta.get("fiftyTwoWeekLow"),
        "currency": meta.get("currency", "USD"),
    }


def get_history(ticker: str, range: str = "6mo", interval: str = "1d") -> Optional[dict]:
    """Get full OHLCV history for a ticker.

    Args:
        ticker: Stock symbol (e.g. 'AAPL', '^GSPC')
        range: Time range ('5d', '1mo', '3mo', '6mo', '1y', '5y')
        interval: Bar interval ('1d', '1wk', '1mo')

    Returns dict with keys: timestamps, opens, highs, lows, closes, volumes
    """
    url = f"{BASE_URL}/{ticker}?range={range}&interval={interval}"
    data = _fetch(url)
    if not data or "chart" not in data:
        return None

    result = data["chart"].get("result")
    if not result:
        return None

    r = result[0]
    meta = r.get("meta", {})
    indicators = r.get("indicators", {})
    quote = (indicators.get("quote") or [{}])[0]

    timestamps = r.get("timestamp", [])
    opens = quote.get("open", [])
    highs = quote.get("high", [])
    lows = quote.get("low", [])
    closes = quote.get("close", [])
    volumes = quote.get("volume", [])

    # Filter out None values
    valid = []
    for i in range(len(closes)):
        if closes[i] is not None:
            valid.append({
                "timestamp": timestamps[i] if i < len(timestamps) else None,
                "open": opens[i] if i < len(opens) else None,
                "high": highs[i] if i < len(highs) else None,
                "low": lows[i] if i < len(lows) else None,
                "close": closes[i],
                "volume": volumes[i] if i < len(volumes) else 0,
            })

    return {
        "symbol": meta.get("symbol", ticker),
        "price": meta.get("regularMarketPrice"),
        "hi52": meta.get("fiftyTwoWeekHigh"),
        "lo52": meta.get("fiftyTwoWeekLow"),
        "bars": valid,
    }


def scan_tickers(tickers: list[str], max_range: str = "6mo") -> list[dict]:
    """Batch screen a list of tickers for basic CANSLIM metrics.

    Returns list of dicts sorted by proximity to 52-week high (tightest first).
    Each result: symbol, price, hi52, fromhi%, range_10d%, vol_shrink, 
    sma20, sma50, above_sma20, above_sma50, avg_vol
    """
    results = []
    for ticker in tickers:
        hist = get_history(ticker, range=max_range)
        if not hist or not hist.get("bars"):
            continue

        bars = hist["bars"]
        closes = [b["close"] for b in bars]
        highs = [b["high"] for b in bars]
        lows = [b["low"] for b in bars]
        volumes = [b["volume"] for b in bars]

        price = hist["price"]
        hi52 = hist["hi52"] or max(highs)

        # Moving averages
        sma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else None
        sma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else None

        # Range tightness (10-day)
        if len(highs) >= 10 and len(lows) >= 10:
            lo10 = min(lows[-10:])
            range_10d = ((max(highs[-10:]) - lo10) / lo10) * 100 if lo10 else None
        else:
            range_10d = None

        # Volume trend
        if len(volumes) >= 20:
            vol5 = sum(volumes[-5:]) / 5
            vol20 = sum(volumes[-20:]) / 20
            vol_shrink = vol5 / vol20 if vol20 else 1.0
        else:
            vol_shrink = None

        # Distance from 52-week high
        fromhi = ((price - hi52) / hi52) * 100 if hi52 else None

        # Average volume
        avg_vol = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else None

        results.append({
            "symbol": ticker,
            "price": price,
            "hi52": hi52,
            "fromhi": round(fromhi, 1) if fromhi is not None else None,
            "range_10d": round(range_10d, 1) if range_10d is not None else None,
            "vol_shrink": round(vol_shrink, 2) if vol_shrink is not None else None,
            "sma20": round(sma20, 2) if sma20 else None,
            "sma50": round(sma50, 2) if sma50 else None,
            "above_sma20": price > sma20 if sma20 else None,
            "above_sma50": price > sma50 if sma50 else None,
            "avg_vol": int(avg_vol) if avg_vol else 0,
        })

        time.sleep(0.15)  # Rate limiting

    # Sort by proximity to 52-week high
    results.sort(key=lambda x: x.get("fromhi") if x.get("fromhi") is not None else 999)
    return results