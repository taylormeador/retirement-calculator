import numpy as np


class Portfolio:
    def __init__(self):
        # Nominal returns for each asset class and inflation
        self._mean_vector = np.array(
            [0.1, 0.04, 0.025, 0.025]
        )  # stocks, bonds, cash, inflation

        # Volatilities (standard deviations) for each
        self._volatilities = np.array(
            [0.18, 0.06, 0.005, 0.025]
        )  # stocks, bonds, cash, inflation

        # Correlation matrix
        self._correlations = np.array(
            [
                [1.0, -0.1, 0.0, 0.2],  # Stocks vs [Stocks, Bonds, Cash, Inflation]
                [-0.1, 1.0, 0.0, -0.3],  # Bonds vs [Stocks, Bonds, Cash, Inflation]
                [0.0, 0.0, 1.0, 0.9],  # Cash vs [Stocks, Bonds, Cash, Inflation]
                [0.2, -0.3, 0.9, 1.0],  # Inflation vs [Stocks, Bonds, Cash, Inflation]
            ]
        )

        # Construct covariance matrix from correlations and volatilities
        self._covariance_matrix = self._correlations * np.outer(
            self._volatilities, self._volatilities
        )

    def generate_annual_returns(self, n_samples=1):
        """
        Generate correlated returns for stocks, bonds, cash, and inflation.

        Returns: array of shape (n_samples, 4) where columns are [stocks, bonds, cash, inflation]
        """
        returns = np.random.multivariate_normal(
            mean=self._mean_vector,
            cov=self._covariance_matrix,
            size=n_samples,
        )
        return returns


class RetirementSimulation:
    def __init__(self, portfolio, params):
        """
        portfolio: Portfolio instance
        params: dict with keys:
            - starting_portfolio: float (e.g., 500000)
            - annual_spending: float (e.g., 50000)
            - target_allocation: dict (e.g., {'stocks': 0.6, 'bonds': 0.3, 'cash': 0.1})
            - retirement_age: int (e.g., 50)
            - simulation_years: int (e.g., 40)
            - enable_parttime_income: bool
            - parttime_trigger_type: str ('peak_percent' | 'starting_percent')
            - parttime_trigger_threshold: float (e.g., 0.80)
            - parttime_annual_income: float (e.g., 25000)
        """
        self.portfolio = portfolio
        self.params = params

    def simulate_single_retirement(self):
        """Run one complete retirement simulation"""
        results = {
            "years": [],
            "ages": [],
            "portfolio_values_start": [],
            "portfolio_values_end": [],
            "withdrawals": [],
            "parttime_income": [],
            "inflation_rates": [],
            "stocks_values": [],
            "bonds_values": [],
            "cash_values": [],
            "success": True,
        }

        # Initialize portfolio with target allocation
        total_portfolio = self.params["starting_portfolio"]
        stocks_value = total_portfolio * self.params["target_allocation"]["stocks"]
        bonds_value = total_portfolio * self.params["target_allocation"]["bonds"]
        cash_value = total_portfolio * self.params["target_allocation"]["cash"]

        cumulative_inflation = 1.0
        peak_portfolio_real = self.params[
            "starting_portfolio"
        ]  # For peak_percent trigger

        for year in range(self.params["simulation_years"]):
            age = self.params["retirement_age"] + year
            current_portfolio = stocks_value + bonds_value + cash_value

            results["years"].append(year)
            results["ages"].append(age)
            results["portfolio_values_start"].append(current_portfolio)

            # 1. Adjust spending for cumulative inflation
            inflation_adjusted_spending = (
                self.params["annual_spending"] * cumulative_inflation
            )

            # 2. Withdraw spending from portfolio (proportionally from each asset)
            if current_portfolio > 0:
                withdrawal_fraction = inflation_adjusted_spending / current_portfolio
                stocks_value *= 1 - withdrawal_fraction
                bonds_value *= 1 - withdrawal_fraction
                cash_value *= 1 - withdrawal_fraction

            results["withdrawals"].append(inflation_adjusted_spending)

            # 3. Generate returns for this year
            annual_returns = self.portfolio.generate_annual_returns(n_samples=1)[0]
            stock_return = annual_returns[0]
            bond_return = annual_returns[1]
            cash_return = annual_returns[2]
            inflation_rate = annual_returns[3]
            results["inflation_rates"].append(inflation_rate)

            # Update cumulative inflation
            cumulative_inflation *= 1 + inflation_rate

            # 4. Apply returns to each asset class independently
            stocks_value *= 1 + stock_return
            bonds_value *= 1 + bond_return
            cash_value *= 1 + cash_return

            # Portfolio value after returns, before rebalancing
            current_portfolio = stocks_value + bonds_value + cash_value

            # 5. Check if part-time income is needed
            parttime_income = 0
            if self.params["enable_parttime_income"]:
                trigger_threshold = self.params["parttime_trigger_threshold"]

                # Adjust peak for inflation to compare in real terms
                peak_portfolio_real_adjusted = (
                    peak_portfolio_real * cumulative_inflation
                )

                if self.params["parttime_trigger_type"] == "peak_percent":
                    if (
                        current_portfolio
                        < peak_portfolio_real_adjusted * trigger_threshold
                    ):
                        parttime_income = (
                            self.params["parttime_annual_income"] * cumulative_inflation
                        )
                elif self.params["parttime_trigger_type"] == "starting_percent":
                    starting_adjusted = (
                        self.params["starting_portfolio"] * cumulative_inflation
                    )
                    if current_portfolio < starting_adjusted * trigger_threshold:
                        parttime_income = (
                            self.params["parttime_annual_income"] * cumulative_inflation
                        )

            # Add part-time income proportionally to each asset class
            if current_portfolio > 0:
                income_fraction = parttime_income / current_portfolio
                stocks_value *= (
                    1 + income_fraction * self.params["target_allocation"]["stocks"]
                )
                bonds_value *= (
                    1 + income_fraction * self.params["target_allocation"]["bonds"]
                )
                cash_value *= (
                    1 + income_fraction * self.params["target_allocation"]["cash"]
                )
            else:
                # If portfolio is depleted, add income according to target allocation
                stocks_value += (
                    parttime_income * self.params["target_allocation"]["stocks"]
                )
                bonds_value += (
                    parttime_income * self.params["target_allocation"]["bonds"]
                )
                cash_value += parttime_income * self.params["target_allocation"]["cash"]

            results["parttime_income"].append(parttime_income)

            # Recalculate portfolio after part-time income
            current_portfolio = stocks_value + bonds_value + cash_value

            # 6. Rebalance to target allocation
            stocks_value = (
                current_portfolio * self.params["target_allocation"]["stocks"]
            )
            bonds_value = current_portfolio * self.params["target_allocation"]["bonds"]
            cash_value = current_portfolio * self.params["target_allocation"]["cash"]

            results["stocks_values"].append(stocks_value)
            results["bonds_values"].append(bonds_value)
            results["cash_values"].append(cash_value)

            # Update peak portfolio (in real terms)
            current_portfolio_real = current_portfolio / cumulative_inflation
            if current_portfolio_real > peak_portfolio_real:
                peak_portfolio_real = current_portfolio_real

            results["portfolio_values_end"].append(current_portfolio)

            # Check if we've run out of money
            if current_portfolio <= 0 and results["success"]:
                results["success"] = False

        return results


def main():
    portfolio = Portfolio()

    params = {
        "starting_portfolio": 750000,
        "annual_spending": 50000,
        "target_allocation": {"stocks": 0.6, "bonds": 0.3, "cash": 0.1},
        "retirement_age": 50,
        "simulation_years": 40,
        "enable_parttime_income": True,
        "parttime_trigger_type": "peak_percent",
        "parttime_trigger_threshold": 0.80,
        "parttime_annual_income": 25000,
    }

    sim = RetirementSimulation(portfolio, params)
    results = sim.simulate_single_retirement()

    # Print sample results
    print(
        f"Retirement simulation: Age {params['retirement_age']} to {params['retirement_age'] + params['simulation_years'] - 1}"
    )
    print(f"Starting portfolio: ${params['starting_portfolio']:,.0f}")
    print(f"Annual spending: ${params['annual_spending']:,.0f}\n")

    print("Sample years:")
    for i in [0, 9, 19, 29, 39]:  # Years 1, 10, 20, 30, 40
        if i < len(results["years"]):
            print(
                f"Age {results['ages'][i]}: "
                f"Total=${results['portfolio_values_end'][i]:,.0f} "
                f"(S=${results['stocks_values'][i]:,.0f}, "
                f"B=${results['bonds_values'][i]:,.0f}, "
                f"C=${results['cash_values'][i]:,.0f}), "
                f"Withdrawal=${results['withdrawals'][i]:,.0f}, "
                f"Part-time=${results['parttime_income'][i]:,.0f}"
            )

    print(f"\nFinal portfolio: ${results['portfolio_values_end'][-1]:,.0f}")
    print(f"Success: {results['success']}")


if __name__ == "__main__":
    main()
