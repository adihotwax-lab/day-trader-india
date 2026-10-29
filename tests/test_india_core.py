import unittest
from datetime import date, datetime, timedelta
from india.market_calendar import IST, MarketCalendar
from india.candles import Candle, validate_candles
from india.strategies import opening_range_breakout
from paper.risk import RiskConfig, position_size
from paper.ledger import PaperLedger

class IndiaCoreTests(unittest.TestCase):
    def test_market_session_and_holiday(self):
        cal = MarketCalendar({date(2026, 11, 2)})
        self.assertTrue(cal.is_market_open(datetime(2026, 10, 30, 9, 15, tzinfo=IST)))
        self.assertFalse(cal.is_market_open(datetime(2026, 10, 30, 15, 30, tzinfo=IST)))
        self.assertFalse(cal.is_trading_day(date(2026, 11, 2)))
        self.assertFalse(cal.is_trading_day(date(2026, 10, 31)))

    def test_incomplete_and_stale_candles_rejected(self):
        now = datetime(2026, 10, 30, 10, 0, tzinfo=IST)
        incomplete = Candle(now - timedelta(minutes=1), 100, 101, 99, 100, 10, False)
        with self.assertRaises(ValueError): validate_candles([incomplete], now)
        stale = Candle(now - timedelta(minutes=10), 100, 101, 99, 100, 10)
        with self.assertRaises(ValueError): validate_candles([stale], now)
        future = Candle(now + timedelta(minutes=1), 100, 101, 99, 100, 10)
        with self.assertRaises(ValueError): validate_candles([future], now)

    def test_position_size_and_safe_config(self):
        self.assertEqual(position_size(100_000, 100, 98, 0.5), 250)
        RiskConfig().validate()
        with self.assertRaises(ValueError): RiskConfig(live_orders_enabled=True).validate()

    def test_paper_ledger_idempotency(self):
        ledger = PaperLedger(":memory:")
        self.assertTrue(ledger.record_fill("sig-1", "reliance", "BUY", 2, 1200))
        self.assertFalse(ledger.record_fill("sig-1", "reliance", "BUY", 2, 1200))
        self.assertEqual(len(ledger.events()), 1)

    def test_opening_range_signal_only_after_range(self):
        day = date(2026, 10, 30)
        def c(h, o, hi, lo, cl):
            return Candle(datetime(2026, 10, 30, h, o, tzinfo=IST), cl, hi, lo, cl, 100)
        bars = [c(9, 15, 101, 99, 100), c(9, 20, 102, 99, 101), c(9, 25, 102, 98, 100), c(9, 30, 103, 100, 102), c(9, 35, 104, 101, 103)]
        signal = opening_range_breakout("reliance", bars)
        self.assertIsNotNone(signal)
        self.assertEqual(signal.side, "LONG")

if __name__ == "__main__": unittest.main()
