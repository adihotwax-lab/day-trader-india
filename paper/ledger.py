"""SQLite ledger for simulated fills only. No broker integration or order API."""
from __future__ import annotations
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

class PaperLedger:
    def __init__(self, path: str = "data/paper_ledger.sqlite3"):
        self.path = path
        self._memory_connection = sqlite3.connect(":memory:", timeout=10) if path == ":memory:" else None
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS paper_events (id INTEGER PRIMARY KEY AUTOINCREMENT, event_key TEXT UNIQUE NOT NULL, symbol TEXT NOT NULL, side TEXT NOT NULL, quantity INTEGER NOT NULL CHECK(quantity > 0), price REAL NOT NULL CHECK(price > 0), created_at TEXT NOT NULL)")

    def _connect(self):
        if self._memory_connection is not None:
            return self._memory_connection
        return sqlite3.connect(self.path, timeout=10)

    def record_fill(self, event_key: str, symbol: str, side: str, quantity: int, price: float, created_at: datetime | None = None) -> bool:
        if not event_key.strip() or not symbol.strip() or side.upper() not in {"BUY", "SELL"}:
            raise ValueError("Invalid event key, symbol, or side")
        if quantity <= 0 or price <= 0:
            raise ValueError("Quantity and price must be positive")
        stamp = (created_at or datetime.now(timezone.utc)).isoformat()
        try:
            with self._connect() as db:
                db.execute("INSERT INTO paper_events(event_key,symbol,side,quantity,price,created_at) VALUES(?,?,?,?,?,?)", (event_key, symbol.upper(), side.upper(), quantity, price, stamp))
            return True
        except sqlite3.IntegrityError as exc:
            if "event_key" in str(exc):
                return False
            raise

    def events(self) -> list[dict]:
        with self._connect() as db:
            db.row_factory = sqlite3.Row
            return [dict(row) for row in db.execute("SELECT * FROM paper_events ORDER BY id")]
