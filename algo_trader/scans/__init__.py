"""
scans/market_health.py — Market health snapshot for daily scan.

Pulls S&P 500, Nasdaq, VIX from Yahoo Finance v8 API.
Returns structured data for the scan report header.
"""

from data.yahoo import get_quote


def get_market_health() -> dict:
    """Get current market health snapshot.

    Returns dict with SPX, IXIC, VIX prices and change percentages.
    """
    spx = get_quote("^GSPC")
    ixic = get_quote("^IXIC")
    vix = get_quote("^VIX")
    
    return {
        "spx": spx["price"] if spx else None,
        "ixic": ixic["price"] if ixic else None,
        "vix": vix["price"] if vix else None,
    }