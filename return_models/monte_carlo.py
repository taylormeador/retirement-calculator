from historical_bootstrap import bootstrap_returns


class Simulation:
    def __init__(self):
        self.initial_portfolio_value = 750000
        self.inflation_rate = 0.03
        self.allocation = {"stocks": 0.6, "bonds": 0.4}
        self.withdrawal_rate = 0.04

    def run(self):
        for _ in range(10000):
            all_returns = bootstrap_returns()
            withdrawal = self.initial_portfolio_value * self.withdrawal_rate
            portfolio_value = self.initial_portfolio_value
            for i, returns in enumerate(all_returns):
                portfolio_value -= withdrawal

                stock_gains = portfolio_value * self.allocation["stocks"] * returns[0]
                bond_gains = portfolio_value * self.allocation["bonds"] * returns[1]

                portfolio_value = portfolio_value + stock_gains + bond_gains
                print(
                    f"year #{i + 1}: portfolio_value=${portfolio_value} stocks={returns[0]}%, ${stock_gains} bonds={returns[1]}%, ${bond_gains}\n"
                )


if __name__ == "__main__":
    simulation = Simulation()
    simulation.run()
