"""Simple, explicit opening-range breakout signal for completed candles only."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from .candles import Candle
from .market_calendar import IST

@dataclass(frozen=True)
class Signal:
    symbol: str
    side: str
    timestamp: datetime
    entry_reference: float
    opening_range_high: float
    opening_range_low: float
    reason: str

def opening_range_breakout(symbol: str, candles: list[Candle], opening_range_minutes: int = 15) -> Signal | None:
    if opening_range_minutes != 15:
        raise ValueError("This initial implementation supports a 15-minute opening range only")
    if not candles:
        return None
    rows = sorted(candles, key=lambda c: c.local_timestamp())
    for c in rows:
        c.validate()
    day = rows[-1].local_timestamp().date()
    same_day = [c for c in rows if c.local_timestamp().date() == day]
    start = datetime.combine(day, datetime.strptime("09:15", "%H:%M").time(), tzinfo=IST)
    end = datetime.combine(day, datetime.strptime("09:30", "%H:%M").time(), tzinfo=IST)
    opening = [c for c in same_day if start <= c.local_timestamp() < end]
    later = [c for c in same_day if c.local_timestamp() >= end]
    if len(opening) < 3 or not later:
        return None
    high = max(c.high for c in opening)
    low = min(c.low for c in opening)
    latest = later[-1]
    if latest.close > high:
        return Signal(symbol.upper(), "LONG", latest.local_timestamp(), latest.close, high, low, "Completed candle closed above 15-minute opening range")
    if latest.close < low:
        return Signal(symbol.upper(), "SHORT", latest.local_timestamp(), latest.close, high, low, "Completed candle closed below 15-minute opening range")
    return None
