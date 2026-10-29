"""INR-denominated risk sizing and hard paper-trading guardrails."""
from dataclasses import dataclass

@dataclass(frozen=True)
class RiskConfig:
    starting_capital_inr: float = 100_000.0
    risk_per_trade_pct: float = 0.5
    max_daily_loss_pct: float = 2.0
    max_positions: int = 3
    max_trades_per_day: int = 5
    paper_mode: bool = True
    live_orders_enabled: bool = False

    def validate(self) -> None:
        if not self.paper_mode or self.live_orders_enabled:
            raise ValueError("Unsafe configuration: paper mode must be on and live orders disabled")
        if self.starting_capital_inr <= 0 or not 0 < self.risk_per_trade_pct <= 1:
            raise ValueError("Invalid capital or per-trade risk percentage")
        if not 0 < self.max_daily_loss_pct <= 10 or self.max_positions < 1 or self.max_trades_per_day < 1:
            raise ValueError("Invalid daily loss, position, or trade limit")

def position_size(capital_inr: float, entry_price: float, stop_price: float, risk_pct: float = 0.5) -> int:
    if capital_inr <= 0 or entry_price <= 0 or stop_price <= 0 or entry_price == stop_price:
        raise ValueError("Capital and prices must be positive; stop must differ from entry")
    if not 0 < risk_pct <= 1:
        raise ValueError("risk_pct must be in (0, 1]")
    risk_budget = capital_inr * risk_pct / 100.0
    per_share_risk = abs(entry_price - stop_price)
    return max(0, min(int(risk_budget // per_share_risk), int(capital_inr // entry_price)))
