import pandas as pd

from historical_bootstrap import bootstrap_returns


class Simulation:
    def __init__(self):
        self.initial_portfolio_value = 750000
        self.inflation_rate = 0.03
        self.allocation = {"stocks": 0.6, "bonds": 0.4}
        self.withdrawal_rate = 0.04
        self.n_samples = 10000
        self.failures = 0

    def run(self):
        all_simulation_data = []
        for sample in range(self.n_samples):
            all_returns = bootstrap_returns()
            withdrawal = self.initial_portfolio_value * self.withdrawal_rate
            portfolio_value = self.initial_portfolio_value
            simulation_data = []
            success = True
            for i, returns in enumerate(all_returns):
                portfolio_value -= withdrawal

                stock_gains = portfolio_value * self.allocation["stocks"] * returns[0]
                bond_gains = portfolio_value * self.allocation["bonds"] * returns[1]

                portfolio_value = portfolio_value + stock_gains + bond_gains
                if portfolio_value <= 0:
                    success = False

                year_data = {
                    "year": i,
                    "end_portfolio_value": portfolio_value,
                    "stock_return": returns[0],
                    "bond_return": returns[1],
                    "withdrawal": withdrawal,
                }
                simulation_data.append(year_data)

            final_portfolio_value = simulation_data[-1]["end_portolio_value"]


if __name__ == "__main__":
    simulation = Simulation()
    simulation.run()
