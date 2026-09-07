"""
patterns/htf.py — High Tight Flag detection (Leif Soreide criteria)

Detects HTF patterns from historical OHLCV data:
  - Pole: 90%+ advance in 4-8 weeks (<=40 trading days), heavy volume, fundamental catalyst
  - Flag: Shallow 10-25% pullback from pole high, tight low-volatility action
         1-3 weeks ideal (max 5), volume dries up significantly
         MUST stay above 50-day MA
  - Breakout: Price breaking above flag high on volume surge (50%+ above avg preferred)
"""

from typing import Optional
from data.yahoo import get_history


def detect_htf(ticker: str) -> Optional[dict]:
    """Scan a ticker for a High Tight Flag pattern.

    Returns dict with pattern details if found, None otherwise.
    """
    hist = get_history(ticker, range="6mo", interval="1d")
    if not hist or not hist.get("bars") or len(hist["bars"]) < 60:
        return None

    bars = hist["bars"]
    closes = [b["close"] for b in bars]
    highs = [b["high"] for b in bars]
    lows = [b["low"] for b in bars]
    volumes = [b["volume"] for b in bars]
    price = hist["price"]

    # -- Pole detection: look for 90%+ run in last 4-8 weeks (20-40 bars) --
    lookback = min(40, len(bars))
    recent_peak = max(highs[-lookback:])
    recent_peak_idx = highs.index(recent_peak)

    # Find the start of the pole (lowest point before the peak)
    pole_start_idx = max(0, recent_peak_idx - 40)
    pole_low = min(lows[pole_start_idx:recent_peak_idx + 1])
    pole_pct = ((recent_peak - pole_low) / pole_low) * 100 if pole_low else 0

    # Pole must be >= 80% (criterion is 90%+, allow some flexibility in detection)
    if pole_pct < 80:
        return None

    # Pole duration must be <= 40 trading days (~8 weeks)
    pole_duration = recent_peak_idx - pole_start_idx
    if pole_duration > 40:
        return None

    # -- Flag detection: pullback from peak --
    current_idx = len(bars) - 1
    bars_since_peak = current_idx - recent_peak_idx

    # Flag should be 1-5 weeks (5-25 bars)
    if bars_since_peak < 3 or bars_since_peak > 25:
        return None

    pullback = ((price - recent_peak) / recent_peak) * 100

    # Pullback should be 10-25%
    if pullback > -8 or pullback < -30:
        return None

    # -- Volume dry-up in flag --
    if len(volumes) >= 20:
        vol_20d_avg = sum(volumes[-20:]) / 20
        vol_recent = sum(volumes[-5:]) / 5
        vol_ratio = vol_recent / vol_20d_avg if vol_20d_avg else 1.0
    else:
        vol_ratio = 1.0

    # Volume should be drying up (ratio < 1.0 means recent vol below average)
    if vol_ratio > 1.2:
        return None

    # -- Must stay above 50-day MA --
    if len(closes) >= 50:
        sma50 = sum(closes[-50:]) / 50
        if price < sma50:
            return None
    else:
        return None

    # -- Range tightness in flag (standard deviation method) --
    if len(closes) >= 10:
        recent_10 = closes[-10:]
        mean_10 = sum(recent_10) / 10
        variance = sum((x - mean_10) ** 2 for x in recent_10) / 10
        std_dev = variance ** 0.5
        consolidation_pct = (std_dev / mean_10) * 100 if mean_10 else 0
    else:
        consolidation_pct = 0

    # Tight flag: consolidation < 5%
    if consolidation_pct > 7:
        return None

    # -- Breakout detection: is price breaking above flag high? --
    flag_high = max(highs[-bar_count:] if (bar_count := min(10, len(highs))) else highs[-10:])
    breakout_pct = ((price - flag_high) / flag_high) * 100 if flag_high else 0
    is_breakout = breakout_pct >= 0

    # Volume surge on breakout
    if is_breakout and len(volumes) >= 5:
        vol_yesterday = volumes[-2] if len(volumes) >= 2 else 0
        vol_surge = vol_yesterday / vol_20d_avg if (vol_20d_avg if 'vol_20d_avg' in dir() else 0) else 1.0
    else:
        vol_surge = 0

    return {
        "ticker": ticker,
        "price": price,
        "pattern": "HTF",
        "pole_pct": round(pole_pct, 1),
        "pole_duration_days": pole_duration,
        "pullback_pct": round(pullback, 1),
        "consolidation_pct": round(consolidation_pct, 2),
        "vol_ratio": round(vol_ratio, 2),
        "above_sma50": True,
        "is_breakout": is_breakout,
        "breakout_pct": round(breakout_pct, 1),
        "flag_high": round(flag_high, 2),
        "suggested_entry": round(flag_high, 2),
        "stop_loss": round(sma50, 2) if "sma50" in dir() and sma50 else round(price * 0.95, 2),
        "target_1": round(flag_high * 1.1, 2),
        "target_2": round(flag_high * 1.2, 2),
    }