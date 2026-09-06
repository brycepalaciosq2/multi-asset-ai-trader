from AlgorithmImports import *


class HardLimitsRiskModel(RiskManagementModel):
    """Max notional / max open + hard daily-loss and max-drawdown halt (flatten + block)."""

    def __init__(
        self,
        max_notional=100_000,
        max_open=3,
        daily_loss_pct=0.02,
        max_drawdown_pct=0.15,
    ):
        self.max_notional = float(max_notional)
        self.max_open = int(max_open)
        self.daily_loss_pct = float(daily_loss_pct)
        self.max_drawdown_pct = float(max_drawdown_pct)
        self._day = None
        self._day_start = None
        self._peak = None
        self.halted = False

    def ManageRisk(self, algorithm, targets):
        day = algorithm.Time.date()
        portfolio_value = float(algorithm.Portfolio.TotalPortfolioValue)

        # Reset halt only on a new calendar day.
        if self._day != day:
            self._day = day
            self._day_start = portfolio_value
            self._peak = portfolio_value
            self.halted = False
        elif not self.halted and self._peak is not None and portfolio_value > self._peak:
            self._peak = portfolio_value

        if not self.halted:
            daily_loss_breached = (
                self._day_start is not None
                and self._day_start > 0
                and portfolio_value < self._day_start * (1 - self.daily_loss_pct)
            )
            drawdown_breached = (
                self._peak is not None
                and self._peak > 0
                and portfolio_value < self._peak * (1 - self.max_drawdown_pct)
            )
            if daily_loss_breached or drawdown_breached:
                self.halted = True

        if self.halted:
            # Flatten invested names and drop every non-zero incoming target (no same-day rebuy).
            return [
                PortfolioTarget(kvp.Key, 0)
                for kvp in algorithm.Portfolio
                if kvp.Value.Invested
            ]

        open_n = sum(1 for kvp in algorithm.Portfolio if kvp.Value.Invested)
        out = []
        for target in targets:
            if not algorithm.Securities.ContainsKey(target.Symbol):
                continue

            price = float(algorithm.Securities[target.Symbol].Price)
            if price <= 0:
                continue

            abs_notional = abs(float(target.Quantity)) * price
            if abs_notional > self.max_notional:
                continue

            is_new = (
                float(target.Quantity) != 0
                and not algorithm.Portfolio[target.Symbol].Invested
            )
            if is_new and open_n >= self.max_open:
                continue

            out.append(target)
            if is_new:
                open_n += 1
        return out
