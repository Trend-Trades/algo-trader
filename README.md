# algo-trader

## Daily CANSLIM + Leif Soreide Style Scan

The daily scan cron job runs at 5:00 AM PT (8:00 AM EST) M-F and delivers a formatted market scan report to Discord channel 1531474112239767713.

### Methodology

- **CANSLIM fundamentals** (EPS acceleration, ROE, institutional sponsorship)
- **Leif Soreide High Tight Flags** (90%+ pole in ≤8 weeks, 10-25% pullback above 50DMA, volume dry-up)
- **Breakout patterns** (cup & handle, flat base press-outs)
- **Post-earnings RS leaders**
- **Relative strength in weak tape** (stocks holding near ATHs while broad market pulls back)

## Project Structure

```
algo-trader/
├── scans/            # Pattern detection & daily scan logic
├── data/             # Data fetching (Yahoo Finance v8 API)
├── backtests/        # Historical pattern validation
├── risk/             # Position sizing & portfolio risk
├── broker/           # schwab-py paper/live execution
├── tradingview/      # Pine Script patterns (branch)
├── config/           # Parameters
└── scripts/          # Cron job wrappers & utilities
```

## Phases

- **Phase 0** — ✅ Daily Discord scan (existing cron)
- **Phase 1** — Pattern encoding into Python + backtesting
- **Phase 2** — Paper trading via schwab-py
- **Phase 3** — Live execution

## Data Source

Yahoo Finance v8 chart API (free, no key required).  
Cron job pulls data programmatically using the v8 endpoint.

## Branches

- `main` — Core Python algo (backtesting, execution)
- `tradingview` — Pine Script experiments for visual charting & alerts