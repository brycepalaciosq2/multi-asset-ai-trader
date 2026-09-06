from AlgorithmImports import *
from risk.HardLimitsRiskModel import HardLimitsRiskModel


class MultiAssetAiTrader(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2015, 1, 1)
        self.SetCash(100_000)
        self.UniverseSettings.Resolution = Resolution.Daily
        self.SetBenchmark("SPY")

        tickers = ["SPY", "EFA", "AGG", "BIL"]
        self._symbols = [self.AddEquity(t, Resolution.Daily).Symbol for t in tickers]
        self.SetWarmUp(252, Resolution.Daily)

        self.SetAlpha(GemDualMomentumAlphaModel(
            risk_on=["SPY", "EFA"], risk_off="AGG", cash="BIL",
            lookback_days=252, rebalance_days=21,
        ))
        self.SetPortfolioConstruction(EqualWeightingPortfolioConstructionModel(Resolution.Daily))
        self.SetExecution(ImmediateExecutionModel())
        self.SetRiskManagement(HardLimitsRiskModel(max_notional=50_000, max_open=3, daily_loss_pct=0.02))
        self.AddRiskManagement(MaximumDrawdownPercentPortfolio(0.15))
        self.Debug("PAPER/BACKTEST ONLY — no live brokerage until helper sign-off")


class GemDualMomentumAlphaModel(AlphaModel):
    def __init__(self, risk_on, risk_off, cash, lookback_days=252, rebalance_days=21):
        self.risk_on, self.risk_off, self.cash = list(risk_on), risk_off, cash
        self.lookback, self.rebalance_days = int(lookback_days), int(rebalance_days)
        self._last, self._symbols = None, {}

    def OnSecuritiesChanged(self, algorithm, changes):
        for s in changes.AddedSecurities:
            self._symbols[s.Symbol.Value] = s.Symbol
        for s in changes.RemovedSecurities:
            self._symbols.pop(s.Symbol.Value, None)

    def Update(self, algorithm, data):
        if algorithm.IsWarmingUp:
            return []
        if self._last is not None and (algorithm.Time - self._last).days < self.rebalance_days:
            return []

        needed = self.risk_on + [self.risk_off, self.cash]
        symbols = []
        for t in needed:
            if t in self._symbols:
                symbols.append(self._symbols[t])
            else:
                for kvp in algorithm.Securities:
                    if kvp.Key.Value == t:
                        symbols.append(kvp.Key)
                        self._symbols[t] = kvp.Key
                        break
        if len(symbols) < 3:
            return []

        hist = algorithm.History(symbols, self.lookback + 1, Resolution.Daily)
        if hist is None or hist.empty:
            return []

        def ret_12m(sym):
            try:
                px = hist.loc[sym].close
                if len(px) < self.lookback:
                    return None
                a, b = float(px.iloc[-1]), float(px.iloc[-self.lookback])
                return None if b <= 0 else a / b - 1.0
            except Exception:
                return None

        best_t, best_r = None, None
        for t in self.risk_on:
            sym = self._symbols.get(t)
            if not sym:
                continue
            r = ret_12m(sym)
            if r is not None and (best_r is None or r > best_r):
                best_t, best_r = t, r
        if best_t is None:
            return []

        if best_r > 0:
            pick = best_t
        else:
            off_r = ret_12m(self._symbols.get(self.risk_off))
            pick = self.risk_off if (off_r is not None and off_r > 0) else self.cash

        pick_sym = self._symbols.get(pick)
        if not pick_sym:
            return []
        self._last = algorithm.Time
        return [Insight.Price(pick_sym, timedelta(days=self.rebalance_days), InsightDirection.Up, weight=1.0)]
