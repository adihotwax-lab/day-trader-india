"""NSE session helpers. Holiday dates must be supplied from a maintained exchange calendar."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date, datetime, time
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

@dataclass(frozen=True)
class MarketSession:
    open_time: time = time(9, 15)
    close_time: time = time(15, 30)

class MarketCalendar:
    def __init__(self, holidays: set[date] | None = None, session: MarketSession | None = None):
        self.holidays = set(holidays or set())
        self.session = session or MarketSession()

    def is_trading_day(self, day: date) -> bool:
        return day.weekday() < 5 and day not in self.holidays

    def session_bounds(self, day: date) -> tuple[datetime, datetime] | None:
        if not self.is_trading_day(day):
            return None
        return (datetime.combine(day, self.session.open_time, tzinfo=IST),
                datetime.combine(day, self.session.close_time, tzinfo=IST))

    def is_market_open(self, moment: datetime) -> bool:
        local = moment.replace(tzinfo=IST) if moment.tzinfo is None else moment.astimezone(IST)
        bounds = self.session_bounds(local.date())
        return bool(bounds and bounds[0] <= local < bounds[1])
