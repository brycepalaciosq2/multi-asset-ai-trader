from AlgorithmImports import *


class HardLimitsRiskModel(RiskManagementModel):
    """Max notional, max open positions, daily-loss kill-switch (flatten + block)."""

    def __init__(self, max_notional=50_000, max_open=5, daily_loss_pct=0.02):
        self.max_notional = float(max_notional)
        self.max_open = int(max_open)
        self.daily_loss_pct = float(daily_loss_pct)
        self._day = None
        self._day_start = None
        self.halted = False

    def ManageRisk(self, algorithm, targets):
        d = algorithm.Time.date()
        if self._day != d:
            self._day = d
            self._day_start = algorithm.Portfolio.TotalPortfolioValue
            self.halted = False

        pv = algorithm.Portfolio.TotalPortfolioValue
        if self._day_start and self._day_start > 0 and pv < self._day_start * (1 - self.daily_loss_pct):
            self.halted = True

        if self.halted:
            out = []
            for kvp in algorithm.Portfolio:
                if kvp.Value.Invested:
                    out.append(PortfolioTarget(kvp.Key, 0))
            return out

        open_n = sum(1 for kvp in algorithm.Portfolio if kvp.Value.Invested)
        out = []
        for t in targets:
            if not algorithm.Securities.ContainsKey(t.Symbol):
                continue
            price = float(algorithm.Securities[t.Symbol].Price)
            if price <= 0:
                continue

            abs_notional = abs(float(t.Quantity)) * price
            if abs_notional > self.max_notional:
                continue

            is_new = float(t.Quantity) != 0 and not algorithm.Portfolio[t.Symbol].Invested
            if is_new and open_n >= self.max_open:
                continue

            out.append(t)
            if is_new:
                open_n += 1
        return out
