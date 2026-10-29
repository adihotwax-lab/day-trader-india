"""Exact-match resolver for rows from the official Kite instrument master.

This module does not make network requests and never guesses token IDs. Pass rows
from a freshly downloaded instrument master and resolve exact exchange/symbol pairs.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Mapping, Any

@dataclass(frozen=True)
class Instrument:
    exchange: str
    tradingsymbol: str
    instrument_token: int
    instrument_type: str
    name: str = ""

    @classmethod
    def from_row(cls, row: Mapping[str, Any]) -> "Instrument":
        try:
            exchange = str(row["exchange"]).strip().upper()
            symbol = str(row["tradingsymbol"]).strip().upper()
            token = int(row["instrument_token"])
            kind = str(row.get("instrument_type", "")).strip().upper()
            name = str(row.get("name", "")).strip()
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Malformed instrument-master row") from exc
        if not exchange or not symbol or token <= 0:
            raise ValueError("Instrument row requires exchange, symbol, and positive token")
        return cls(exchange, symbol, token, kind, name)

def resolve_instrument(rows: Iterable[Mapping[str, Any]], exchange: str, tradingsymbol: str, instrument_type: str | None = None) -> Instrument:
    wanted_exchange = exchange.strip().upper()
    wanted_symbol = tradingsymbol.strip().upper()
    if not wanted_exchange or not wanted_symbol:
        raise ValueError("Exchange and trading symbol are required")
    matches = []
    for row in rows:
        item = Instrument.from_row(row)
        if item.exchange == wanted_exchange and item.tradingsymbol == wanted_symbol:
            if instrument_type is None or item.instrument_type == instrument_type.strip().upper():
                matches.append(item)
    if not matches:
        raise LookupError(f"No exact instrument match for {wanted_exchange}:{wanted_symbol}")
    if len(matches) > 1:
        raise LookupError(f"Ambiguous instrument match for {wanted_exchange}:{wanted_symbol}; specify instrument_type")
    return matches[0]
