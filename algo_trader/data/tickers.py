"""
data/tickers.py — Stock watch list for daily scanning.

The cron scans these tickers each day for HTF, breakout, 
and relative strength patterns. Update this list to expand 
or focus the universe.
"""

# Core watch list — US equities, avg vol >400k, price >$10
# Add/edit as needed. The scanner checks each ticker for patterns.
WATCH_LIST = [
    # Software / Cloud / AI
    "NVDA", "MSFT", "CRM", "NOW", "DDOG", "MDB", "NET", "SNOW",
    "CRWD", "ZS", "PANW", "PLTR", "SHOP", "SPOT",
    # Fintech / Payments
    "SOFI", "PYPL", "AFRM", "SQ",
    # Healthcare / Biotech
    "LLY", "LQDA", "UNH", "HUM",
    # Financial / Insurance
    "ENVA", "CPRT",
    # Consumer / Retail
    "AMZN", "CHWY", "DECK",
    # Industrials / Energy
    "CEG", "LMT", "GE",
    # Semiconductors
    "AMD", "MU", "LRCX", "KLAC",
]

# Expanded scan (for deeper market sweeps)
EXPANDED_LIST = WATCH_LIST + [
    "AAPL", "GOOGL", "META", "TSLA", "AVGO",
    "ANET", "ALGN", "NVR", "PHM", "DHI",
    "MEDP", "IDXX", "ISRG", "TTD",
    "TOST", "GTLB", "FROG", "MNDY",
]