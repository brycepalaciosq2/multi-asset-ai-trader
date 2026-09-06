# multi-asset-ai-trader

Paper-first LEAN (QuantConnect) dual-momentum (GEM-style) bot.

## Scope (v0.2)

- Universe: `SPY`, `EFA`, `AGG`, `BIL` (cash proxy)
- Signal: 12-month absolute + relative momentum, **monthly** rebalance
- Portfolio: `SingleNamePortfolioConstructionModel` — 100% into GEM winner, **explicit zero** on all other holdings
- Risk: `HardLimitsRiskModel`
  - max notional 100k, max open 3
  - daily-loss 2% halt (clears next calendar day)
  - max drawdown 15% from **running high-water mark** — stays flat until equity **recovers above HWM**
- **Paper / backtest only** — no live brokers until helper sign-off
- Crypto / FX: **off** until risk is proven
- **BIL:** cash sleeve buys BIL when priced; if missing/unpriced → flatten to cash + Debug

## Not added yet (approved later)

- Qlib / FinRL signals, Freqtrade-style UX (reimplement), CCXT/Hummingbot crypto, MT5/cTrader bridges, IB/Alpaca paper wiring

## License notes

- Built to run on QuantConnect/Lean (Apache-2.0)
- Do **not** paste GPL code (Freqtrade, OctoBot, Backtrader, etc.)

## Run (LEAN CLI)

**Requires:** Docker (daemon running) + Lean CLI (`pip install lean`) + equity daily data for SPY/EFA/AGG/BIL (via `lean data download` after `lean login`, or local data folders). Without these, `lean backtest` will not run.

```bash
pip install lean
lean init
# copy main.py + risk/ + portfolio/ into the Lean project
lean backtest .
# later: lean live deploy "..." --brokerage "Paper Trading"
```
