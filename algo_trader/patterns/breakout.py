"""
patterns/breakout.py — Breakout detection (cup & handle, flat base)

Detects stocks pressing out of consolidation bases on volume.
"""

from data.yahoo import get_history
from typing import Optional


def detect_breakout(ticker: str) -> Optional[dict]:
    """Check if a ticker is breaking out or pressing out of a base.

    Looks for: price near 52-week high, tight recent range,
    expanding volume, above key moving averages.
    """
    hist = get_history(ticker, range="6mo", interval="1d")
    if not hist or not hist.get("bars") or len(hist["bars"]) < 50:
        return None

    bars = hist["bars"]
    closes = [b["close"] for b in bars]
    highs = [b["high"] for b in bars]
    lows = [b["low"] for b in bars]
    volumes = [b["volume"] for b in bars]
    price = hist["price"]
    hi52 = hist["hi52"]

    if not hi52 or not price:
        return None

    # Near 52-week high (within 15%)
    from_hi = ((price - hi52) / hi52) * 100

    # Tight range on pullback
    if len(highs) >= 10:
        range_10d = ((max(highs[-10:]) - min(lows[-10:])) / min(lows[-10:])) * 100
    else:
        range_10d = 999

    # Volume expanding (recent vs 50-day avg)
    if len(volumes) >= 50:
        vol_50d = sum(volumes[-50:]) / 50
        vol_recent = sum(volumes[-5:]) / 5
        vol_ratio = vol_recent / vol_50d if vol_50d else 1.0
    else:
        vol_ratio = 1.0

    # Above moving averages
    sma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else 0
    sma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else 0

    if from_hi > -15 and range_10d < 12 and price > sma20 > sma50:
        return {
            "ticker": ticker,
            "price": price,
            "pattern": "Breakout / Base Press",
            "from_hi_pct": round(from_hi, 1),
            "range_10d": round(range_10d, 1),
            "vol_ratio": round(vol_ratio, 2),
            "sma20": round(sma20, 2),
            "sma50": round(sma50, 2),
            "entry_zone": round(hi52, 2),
            "stop": round(sma50, 2),
        }

    return None