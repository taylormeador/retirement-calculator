"""Simulation object."""


class Simulation:
    def __init__(self, return_model, withdrawal_rate):
        self.return_model = return_model
        self.withdrawal_rate = withdrawal_rate
        self.inflation_rate = 0.03
        self.allocation = {"stocks": 0.6, "bonds": 0.4}

    def run(self):
        all_returns = self.return_model()
        portfolio_value = 1000000
        withdrawal = portfolio_value * self.withdrawal_rate

        portfolio_values = [portfolio_value]
        success = True
        year_failed = None
        for i, returns in enumerate(all_returns):
            portfolio_value -= withdrawal

            stock_gains = portfolio_value * self.allocation["stocks"] * returns[0]
            bond_gains = portfolio_value * self.allocation["bonds"] * returns[1]

            portfolio_value = portfolio_value + stock_gains + bond_gains
            if portfolio_value <= 0:
                if success:
                    success = False
                    year_failed = i + 1
                portfolio_value = 0
                portfolio_values.append(0)
                continue

            portfolio_values.append(portfolio_value)

        return {
            "portfolio_values": portfolio_values,
            "success": success,
            "failure_year": year_failed,
        }
