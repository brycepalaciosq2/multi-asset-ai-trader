from AlgorithmImports import *


class HardLimitsRiskModel(RiskManagementModel):
    """Max notional / max open + daily-loss (day reset) + max-DD halt until HWM recovery."""

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
        self._daily_halted = False
        self._dd_halted = False

    @property
    def halted(self):
        return self._daily_halted or self._dd_halted

    def ManageRisk(self, algorithm, targets):
        day = algorithm.Time.date()
        portfolio_value = float(algorithm.Portfolio.TotalPortfolioValue)

        # New day: only clear daily-loss halt + baseline. MaxDD halt persists.
        if self._day != day:
            self._day = day
            self._day_start = portfolio_value
            self._daily_halted = False
            if self._peak is None:
                self._peak = portfolio_value

        # Running high-water mark (frozen while DD-halted).
        if not self._dd_halted and (self._peak is None or portfolio_value > self._peak):
            self._peak = portfolio_value

        # Trip daily-loss (clears next calendar day).
        if (
            not self._daily_halted
            and self._day_start is not None
            and self._day_start > 0
            and portfolio_value < self._day_start * (1 - self.daily_loss_pct)
        ):
            self._daily_halted = True

        # Trip max DD from running peak (sticks until recovery above HWM).
        if (
            not self._dd_halted
            and self._peak is not None
            and self._peak > 0
            and portfolio_value < self._peak * (1 - self.max_drawdown_pct)
        ):
            self._dd_halted = True

        # Clear DD halt only after full recovery to high-water mark.
        if self._dd_halted and self._peak is not None and portfolio_value >= self._peak:
            self._dd_halted = False

        if self.halted:
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
