"""Environment-backed configuration with safe paper-only defaults."""
from __future__ import annotations
import os
from .risk import RiskConfig

def _bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise ValueError(f"Invalid boolean value: {value!r}")

def load_risk_config(env: dict[str, str] | None = None) -> RiskConfig:
    source = os.environ if env is None else env
    cfg = RiskConfig(
        starting_capital_inr=float(source.get("STARTING_CAPITAL_INR", "100000")),
        risk_per_trade_pct=float(source.get("RISK_PER_TRADE_PCT", "0.5")),
        max_daily_loss_pct=float(source.get("MAX_DAILY_LOSS_PCT", "2.0")),
        max_positions=int(source.get("MAX_POSITIONS", "3")),
        max_trades_per_day=int(source.get("MAX_TRADES_PER_DAY", "5")),
        paper_mode=_bool(source.get("PAPER_MODE"), True),
        live_orders_enabled=_bool(source.get("LIVE_ORDERS_ENABLED"), False),
    )
    cfg.validate()
    return cfg
