# India NSE Paper-Trading Integration Plan

## Status
- Personal repository: `adihotwax-lab/day-trader-india`.
- Working branch: `india-nse-paper`.
- GitHub connector write access was verified and the temporary check file was removed.
- This plan is not a claim that market data, credentials, alerts, deployment, or strategy execution have been implemented.

## Non-negotiable safety scope
- Paper trading only.
- Never call a live broker order-placement endpoint.
- Enforce `PAPER_MODE=true` and `LIVE_ORDERS_ENABLED=false` at runtime.
- Stale, incomplete, or inconsistent market data must fail closed: no new signal or simulated entry.
- The paper ledger is simulated and is not a broker account.

## Initial market scope
- NSE cash equities and the NIFTY 50 / NIFTY BANK indices.
- Use timezone-aware timestamps in `Asia/Kolkata`.
- Normal NSE equity session is 09:15–15:30 IST; derivatives generally run until 15:40 IST. Use a maintained exchange calendar and account for holidays and special sessions.
- Options contracts are out of scope until expiry, strike, lot-size, liquidity, and options-risk requirements are defined.

## Proposed components
- `india/market_calendar.py`: sessions and holidays.
- `india/instruments.py`: instrument-master cache and token resolution.
- `india/kite_feed.py`: market-data-only Kite WebSocket adapter; no order APIs.
- `india/candles.py`: completed candles, gap/duplicate/staleness checks.
- `india/strategies.py`: India-specific strategy rules.
- `paper/ledger.py`: persistent SQLite simulated positions and fills.
- `paper/risk.py`: INR sizing, exposure, per-trade and daily-loss limits.
- `alerts/telegram.py`, `alerts/email.py`, `alerts/dispatcher.py`: delivery, retries, and deduplication.
- `service/runner.py`, `service/health.py`: market loop, heartbeat, reconnects, and health.
- `tests/`: fixture-based tests that need no live credentials.

## Implementation sequence
1. Run and record the upstream test baseline.
2. Add safe configuration and a placeholder-only `.env.example`.
3. Implement and test India calendar and instrument resolution.
4. Add a Kite adapter limited to quotes and historical candles, with reconnect/backoff.
5. Build candles and reject stale, missing, duplicate, or incomplete data.
6. Port candidate strategies and test with historical/synthetic replay; do not assume US rules transfer unchanged.
7. Add SQLite paper ledger, INR risk controls, simulated costs/slippage, stops/targets, and trade caps.
8. Add Telegram/email notifications with retries and idempotency.
9. Add health monitoring, replay mode, and operational logging.
10. Complete acceptance tests before a supervised paper session.

## Secrets
Keep Kite API secret/access token, Telegram bot token, and email credentials in environment variables or a secret store. Never commit `.env`, tokens, or session files, and never paste credentials into chat.

## Acceptance checklist
- [ ] Upstream tests run and baseline recorded.
- [ ] IST session/holiday and instrument-token resolution tested.
- [ ] Only completed candles can create signals.
- [ ] Stale/missing data blocks new entries.
- [ ] No live order-placement path is called.
- [ ] Paper ledger persists across restart without duplicate positions.
- [ ] INR risk limits and simulated costs are tested.
- [ ] Telegram and email tested independently.
- [ ] Duplicate alerts suppressed across restarts.
- [ ] Reconnects, session expiry, and service failure are observable.
- [ ] Historical replay and supervised paper session completed.

## Configuration requirements
The final configuration must explicitly provide paper mode and live-order disable switches, virtual INR capital, risk and daily-loss caps, max positions/trades, allowed instruments and strategies, data freshness threshold, reconnect policy, alert settings, logging level, and persistent state path.

Do not reuse the upstream sample's USD amounts, Alpaca broker setting, New York timezone, or US-market cutoffs.
