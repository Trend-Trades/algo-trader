"""
scan_runner.py — Daily scan: find setups, format report, deliver to Discord.

This is the main entry point for the daily CANSLIM + Leif Soreide scan.
Ported from the cron prompt into executable Python.
"""

from data.yahoo import get_quote, scan_tickers
from patterns.htf import detect_htf
from patterns.breakout import detect_breakout
from data.tickers import WATCH_LIST


def get_market_health() -> dict:
    """Fetch current market index data for report header."""
    spx = get_quote("^GSPC")
    ixic = get_quote("^IXIC")
    vix = get_quote("^VIX")

    return {
        "spx": round(spx["price"], 0) if spx else "N/A",
        "ixic": round(ixic["price"], 0) if ixic else "N/A",
        "vix": round(vix["price"], 1) if vix else "N/A",
    }


def run_daily_scan() -> dict:
    """Run the full daily scan. Returns dict with market health, setups, watches."""
    market = get_market_health()
    strong_setups = []
    stocks_to_watch = []

    for ticker in WATCH_LIST:
        try:
            # Check HTF first
            htf = detect_htf(ticker)
            if htf and htf.get("is_breakout"):
                strong_setups.append(htf)
                continue

            # Check breakout
            breakout = detect_breakout(ticker)
            if breakout:
                if breakout.get("from_hi_pct", 0) > -5:
                    strong_setups.append(breakout)
                else:
                    stocks_to_watch.append(breakout)
                continue

            # Store for watching if not already caught
            if htf:
                stocks_to_watch.append(htf)
            elif breakout:
                pass  # already handled
        except Exception:
            pass

    return {
        "market": market,
        "strong_setups": strong_setups[:4],  # Max 4
        "stocks_to_watch": stocks_to_watch[:3],  # Max 3
    }


def format_discord_report(scan_result: dict) -> str:
    """Format the scan result into a Discord-ready markdown post."""
    market = scan_result["market"]
    setups = scan_result["strong_setups"]
    watches = scan_result["stocks_to_watch"]

    lines = []
    lines.append(f"**Daily CANSLIM + Leif Soreide Scan**\n")

    # Market Health
    lines.append("**Market Health**")
    lines.append(f"S&P 500: {market['spx']}  |  Nasdaq: {market['ixic']}  |  VIX: {market['vix']}")
    lines.append("")

    # Strong Setups
    lines.append("**Strong Setups**")
    if not setups:
        lines.append("No setups fully met criteria today.")
    else:
        for s in setups:
            lines.append(f"**{s['ticker']}** — {s.get('pattern', 'Setup')}")
            lines.append(f"Price: ${s['price']:.2f}")

            if 'pole_pct' in s:
                lines.append(f"Pole: {s['pole_pct']}% in {s['pole_duration_days']} days")
                lines.append(f"Pullback: {s['pullback_pct']}%")
                lines.append(f"Consolidation: {s['consolidation_pct']}% (tight)")

            if 'from_hi_pct' in s:
                lines.append(f"From 52W High: {s['from_hi_pct']}%")
                lines.append(f"10d Range: {s['range_10d']}% | Vol Ratio: {s['vol_ratio']}x")

            if 'suggested_entry' in s:
                lines.append(f"Entry: ${s['suggested_entry']:.2f}")
            if 'stop_loss' in s:
                lines.append(f"Stop: ${s['stop_loss']:.2f}")
            if 'target_1' in s:
                lines.append(f"Targets: ${s['target_1']:.2f} / ${s['target_2']:.2f}")

            lines.append("")

    # Stocks to Watch
    lines.append("**Stocks to Watch**")
    if not watches:
        lines.append("No additional names on watch today.")
    else:
        for w in watches:
            info = f"**{w['ticker']}** — ${w['price']:.2f}"
            if 'from_hi_pct' in w:
                info += f" [{w['from_hi_pct']}% from high]"
            if 'pullback_pct' in w:
                info += f" [pullback: {w['pullback_pct']}%]"
            lines.append(info)
    lines.append("")

    # Notes
    lines.append("**Notes**")
    lines.append("Volume confirmation key on any breakout. Risk per trade: 1-2%.")
    lines.append("")

    # Disclaimers
    lines.append("**Disclaimers**")
    lines.append("For informational purposes only. Not financial advice. Do your own research. Trading involves risk.")

    return "\n".join(lines)