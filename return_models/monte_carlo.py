import numpy as np

import models
from embed_charts import generate_analysis_page


class Simulation:
    def __init__(self, return_model):
        self.initial_portfolio_value = 750000
        self.inflation_rate = 0.03
        self.allocation = {"stocks": 0.6, "bonds": 0.4}
        self.withdrawal_rate = 0.04
        self.n_samples = 10000
        self.failures = 0
        self.return_model = return_model

    def run(self):
        all_returns = self.return_model()
        withdrawal = self.initial_portfolio_value * self.withdrawal_rate
        portfolio_value = self.initial_portfolio_value
        portfolio_values = []
        success = True
        year_failed = None
        for i, returns in enumerate(all_returns):
            portfolio_value -= withdrawal

            stock_gains = portfolio_value * self.allocation["stocks"] * returns[0]
            bond_gains = portfolio_value * self.allocation["bonds"] * returns[1]

            portfolio_value = portfolio_value + stock_gains + bond_gains
            if success and portfolio_value <= 0:
                success = False
                year_failed = i + 1

            portfolio_values.append(portfolio_value)

        return {
            "portfolio_values": portfolio_values,
            "success": success,
            "failure_year": year_failed,
        }


if __name__ == "__main__":
    simulation = Simulation(models.bootstrap_returns)
    all_trajectories = []
    failures = 0
    for _ in range(10000):
        result = simulation.run()
        all_trajectories.append(result["portfolio_values"])
        if not result["success"]:
            failures += 1

    # Calculate stats
    trajectories_array = np.array(all_trajectories)
    p10 = np.percentile(trajectories_array, 10, axis=0)
    p25 = np.percentile(trajectories_array, 25, axis=0)
    p50 = np.percentile(trajectories_array, 50, axis=0)
    p75 = np.percentile(trajectories_array, 75, axis=0)
    p90 = np.percentile(trajectories_array, 90, axis=0)

    failure_rate = failures / 10000 * 100
    print(f"Failure rate: {failure_rate}%")

    generate_analysis_page(trajectories_array, "Historical Returns", 4, {})
