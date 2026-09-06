from AlgorithmImports import *


class HardLimitsRiskModel(RiskManagementModel):
    """Max notional/open + daily-loss + max-DD halt until HWM recovery (or N flat days)."""

    def __init__(
        self,
        max_notional=100_000,
        max_open=3,
        daily_loss_pct=0.02,
        max_drawdown_pct=0.15,
        resume_after_halt_days=60,
    ):
        self.max_notional = float(max_notional)
        self.max_open = int(max_open)
        self.daily_loss_pct = float(daily_loss_pct)
        self.max_drawdown_pct = float(max_drawdown_pct)
        # After this many calendar days continuously DD-halted, reset peak to current and resume.
        # Set to None/0 to disable (stay flat until full HWM recovery only).
        self.resume_after_halt_days = (
            None if resume_after_halt_days in (None, 0) else int(resume_after_halt_days)
        )
        self._day = None
        self._day_start = None
        self._peak = None
        self._daily_halted = False
        self._dd_halted = False
        self._dd_halt_since = None

    @property
    def halted(self):
        return self._daily_halted or self._dd_halted

    def _zero_all(self, algorithm):
        # Always emit explicit zeros for every known symbol — never return [].
        symbols = set()
        for kvp in algorithm.Securities:
            symbols.add(kvp.Key)
        for kvp in algorithm.Portfolio:
            symbols.add(kvp.Key)
        return [PortfolioTarget(symbol, 0) for symbol in symbols]

    def ManageRisk(self, algorithm, targets):
        day = algorithm.Time.date()
        portfolio_value = float(algorithm.Portfolio.TotalPortfolioValue)

        if self._day != day:
            self._day = day
            self._day_start = portfolio_value
            self._daily_halted = False
            if self._peak is None:
                self._peak = portfolio_value

        if not self._dd_halted and (self._peak is None or portfolio_value > self._peak):
            self._peak = portfolio_value

        if (
            not self._daily_halted
            and self._day_start is not None
            and self._day_start > 0
            and portfolio_value < self._day_start * (1 - self.daily_loss_pct)
        ):
            self._daily_halted = True

        if (
            not self._dd_halted
            and self._peak is not None
            and self._peak > 0
            and portfolio_value < self._peak * (1 - self.max_drawdown_pct)
        ):
            self._dd_halted = True
            self._dd_halt_since = day
            algorithm.Debug(
                f"MaxDD halt ON — peak={self._peak:.2f} pv={portfolio_value:.2f}"
            )

        # Resume: full HWM recovery OR optional N flat days (reset peak to current).
        if self._dd_halted:
            if self._peak is not None and portfolio_value >= self._peak:
                self._dd_halted = False
                self._dd_halt_since = None
                algorithm.Debug("MaxDD halt OFF — recovered to HWM")
            elif (
                self.resume_after_halt_days is not None
                and self._dd_halt_since is not None
                and (day - self._dd_halt_since).days >= self.resume_after_halt_days
            ):
                self._peak = portfolio_value
                self._dd_halted = False
                self._dd_halt_since = None
                algorithm.Debug(
                    f"MaxDD halt OFF — {self.resume_after_halt_days}d flat, peak reset to {portfolio_value:.2f}"
                )

        if self.halted:
            return self._zero_all(algorithm)

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
