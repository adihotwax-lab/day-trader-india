"""Validation helpers for completed OHLCV candles."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable
from .market_calendar import IST

@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    complete: bool = True

    def validate(self) -> None:
        vals = (self.open, self.high, self.low, self.close, self.volume)
        if any(v != v or abs(v) == float("inf") for v in vals):
            raise ValueError("Candle contains non-finite values")
        if min(self.open, self.high, self.low, self.close) <= 0 or self.volume < 0:
            raise ValueError("Prices must be positive and volume non-negative")
        if self.high < max(self.open, self.close, self.low) or self.low > min(self.open, self.close, self.high):
            raise ValueError("Invalid OHLC relationship")
        if not self.complete:
            raise ValueError("Incomplete candle is not eligible for signals")

    def local_timestamp(self) -> datetime:
        return self.timestamp.replace(tzinfo=IST) if self.timestamp.tzinfo is None else self.timestamp.astimezone(IST)

def validate_candles(candles: Iterable[Candle], now: datetime, max_age: timedelta = timedelta(minutes=3)) -> list[Candle]:
    rows = list(candles)
    if not rows:
        raise ValueError("No candles supplied")
    normalized = []
    for candle in rows:
        candle.validate()
        normalized.append((candle.local_timestamp(), candle))
    stamps = [x[0] for x in normalized]
    if len(stamps) != len(set(stamps)):
        raise ValueError("Duplicate candle timestamps")
    if stamps != sorted(stamps):
        raise ValueError("Candles must be in chronological order")
    local_now = now.replace(tzinfo=IST) if now.tzinfo is None else now.astimezone(IST)
    if local_now - stamps[-1] > max_age:
        raise ValueError("Latest candle is stale")
    return [x[1] for x in normalized]
