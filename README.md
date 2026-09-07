# algo-trader

## What This Is

The systematic version of my daily CANSLIM + Leif Soreide style scan.

Every day I scan the market, find stocks matching my edge, and tell you:
- **What I found** — tickers that fit the criteria
- **Where I'd buy** — entry/pivot, stop, targets
- **Why** — fundamentals + pattern setup + volume characteristics

This repo is the foundation. Everything branches from here.

## The Scan

Runs M-F at 5:00 AM PT (8:00 AM EST) and posts to Discord.

**Patterns I scan for:**
- High Tight Flags (90%+ pole in ≤8 weeks, 10-25% pullback above 50DMA, volume dry-up)
- Breakouts / pressing out of bases (cup & handle, flat base)
- Post-earnings relative strength leaders
- Stocks holding near ATHs while broad market pulls back (RS in weak tape)

## Branches

| Branch | What's on it |
|---|---|
| `main` | The core Python scan — what posts to Discord daily |
| `tradingview` | Pine Script experiments (visual charts, real-time alerts) |

## Project Structure

```
algo_trader/
├── __init__.py
├── data/           # Fetching market data (Yahoo Finance v8 API)
├── patterns/       # Pattern detection (HTF, breakout, RS, etc.)
└── scans/          # Daily scan runner + Discord posting
```

## Phases

- **Phase 0** — ✅ Daily Discord scan (live)

This is where we start. Will update as we build.

---

*Built for Trend_Trades by Hermione*