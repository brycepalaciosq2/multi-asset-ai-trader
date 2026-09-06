# multi-asset-ai-trader

Paper-first LEAN (QuantConnect) dual-momentum (GEM-style) bot.

## Scope (v0.1)

- Universe: `SPY`, `EFA`, `AGG`, `BIL` (cash proxy)
- Signal: 12-month absolute + relative momentum, **monthly** rebalance
- Portfolio: **InsightWeighting** — GEM winner gets weight 1.0; all other names get **Flat** (single-name flips)
- Risk: `HardLimitsRiskModel` — max notional 100k, max open 3, daily-loss 2% + max drawdown 15% **hard halt** (flatten + **no rebuy until next calendar day**)
- **Paper / backtest only** — no live brokers until helper sign-off
- Crypto / FX: **off** until risk is proven
- **BIL:** needs equity daily data; if BIL is missing/unpriced when cash is selected, bot flattens to cash and logs a Debug line

## License notes

- Built to run on QuantConnect/Lean (Apache-2.0)
- Do **not** paste GPL code (Freqtrade, OctoBot, Backtrader, etc.)

## Run (LEAN CLI)

**Requires:** Docker (daemon running) + Lean CLI (`pip install lean`) + equity daily data for SPY/EFA/AGG/BIL (via `lean data download` after `lean login`, or local data folders). Without these, `lean backtest` will not run.

```bash
pip install lean
lean init
# copy main.py + risk/ into the Lean project
lean backtest .
# later: lean live deploy "..." --brokerage "Paper Trading"
```
