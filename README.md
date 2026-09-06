# multi-asset-ai-trader

Paper-first LEAN (QuantConnect) dual-momentum (GEM-style) bot.

## Scope (v0)

- Universe: `SPY`, `EFA`, `AGG`, `BIL` (cash proxy)
- Signal: 12-month absolute + relative momentum, **monthly** rebalance
- Risk: `HardLimitsRiskModel` (max notional / max open / daily-loss kill-switch) + `MaximumDrawdownPercentPortfolio`
- **Paper / backtest only** — no live brokers until helper sign-off
- Crypto / FX: **off** until risk is proven

## License notes

- Built to run on QuantConnect/Lean (Apache-2.0)
- Do **not** paste GPL code (Freqtrade, OctoBot, Backtrader, etc.)

## Run (LEAN CLI)

**Requires:** Docker (daemon running) + Lean CLI (`pip install lean`) + equity daily data for SPY/EFA/AGG/BIL (via `lean data download` after `lean login`, or local data folders). Without these, `lean backtest` will not run.

pip install lean
lean init
# copy main.py + risk/ into the Lean project
lean backtest .
# later: lean live deploy "..." --brokerage "Paper Trading"
