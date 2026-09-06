# multi-asset-ai-trader

Paper-first LEAN (QuantConnect) dual-momentum (GEM-style) bot.

## Scope (v0.3)

- Universe: `SPY`, `EFA`, `AGG` (cash sleeve = **true cash**, BIL dropped — never filled in sample data)
- Signal: 12-month absolute + relative momentum, **monthly** rebalance
- Portfolio: `SingleNamePortfolioConstructionModel` — 100% into GEM winner, explicit zeros elsewhere
- Risk: `HardLimitsRiskModel`
  - max notional 100k, max open 3
  - daily-loss 2% halt (clears next calendar day)
  - max drawdown 15% from running high-water mark
  - while halted: **always** emit zero targets for all symbols (never `[]`, blocks rebalance leaks)
  - resume when equity recovers to HWM **or** after `resume_after_halt_days=60` flat (peak resets to current)
- **Paper / backtest only** — no live brokers until helper sign-off
- Crypto / FX / IB / Alpaca / MT5: **off** until risk sign-off

## Not added yet (approved later)

- Qlib / FinRL signals, Freqtrade-style UX (reimplement), CCXT/Hummingbot crypto, MT5/cTrader bridges, IB/Alpaca paper wiring

## License notes

- Built to run on QuantConnect/Lean (Apache-2.0)
- Do **not** paste GPL code (Freqtrade, OctoBot, Backtrader, etc.)

## Run (LEAN CLI)

**Requires:** Docker (daemon running) + Lean CLI (`pip install lean`) + equity daily data for SPY/EFA/AGG.

```bash
pip install lean
lean init
# copy main.py + risk/ + portfolio/ into the Lean project
lean backtest .
```
