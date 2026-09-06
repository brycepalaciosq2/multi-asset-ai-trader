from AlgorithmImports import *


class SingleNamePortfolioConstructionModel(PortfolioConstructionModel):
    """100% into the single Up insight; explicit zero for every other invested name."""

    def CreateTargets(self, algorithm, insights):
        pick = None
        for insight in insights:
            if insight.Direction == InsightDirection.Up:
                pick = insight.Symbol
                break

        targets = []
        for kvp in algorithm.Portfolio:
            if kvp.Value.Invested and (pick is None or kvp.Key != pick):
                targets.append(PortfolioTarget(kvp.Key, 0))

        if pick is not None and algorithm.Securities.ContainsKey(pick):
            price = float(algorithm.Securities[pick].Price)
            if price > 0:
                targets.append(PortfolioTarget.Percent(algorithm, pick, 1.0))

        return targets
