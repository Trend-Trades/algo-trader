"""Pattern detection for CANSLIM + Leif Soreide style setups.

Each module in this package detects a specific pattern type:
- htf.py — High Tight Flags (Leif Soreide criteria)
- breakout.py — Cup & handle, flat base breakouts
- earnings_momentum.py — Post-earnings relative strength
- rs_weak_tape.py — Relative strength during market drawdowns
"""

from . import htf
from . import breakout