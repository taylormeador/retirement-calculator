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
            "success": True,
        }

        current_portfolio = self.params["starting_portfolio"]
        cumulative_inflation = 1.0
        peak_portfolio_real = self.params[
            "starting_portfolio"
        ]  # For peak_percent trigger

        for year in range(self.params["simulation_years"]):
            age = self.params["retirement_age"] + year
            results["years"].append(year)
            results["ages"].append(age)
            results["portfolio_values_start"].append(current_portfolio)

            # 1. Adjust spending for cumulative inflation
            inflation_adjusted_spending = (
                self.params["annual_spending"] * cumulative_inflation
            )

            # 2. Withdraw spending from portfolio
            current_portfolio -= inflation_adjusted_spending
            results["withdrawals"].append(inflation_adjusted_spending)

            # 3. Generate returns for this year
            annual_returns = self.portfolio.generate_annual_returns(n_samples=1)[0]
            asset_returns = annual_returns[:3]  # stocks, bonds, cash
            inflation_rate = annual_returns[3]
            results["inflation_rates"].append(inflation_rate)

            # Update cumulative inflation
            cumulative_inflation *= 1 + inflation_rate

            # 4. Apply returns to post-withdrawal portfolio
            # Calculate weighted return based on current allocation
            weights = np.array(
                [
                    self.params["target_allocation"]["stocks"],
                    self.params["target_allocation"]["bonds"],
                    self.params["target_allocation"]["cash"],
                ]
            )
            portfolio_return = np.dot(asset_returns, weights)
            current_portfolio *= 1 + portfolio_return

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

            current_portfolio += parttime_income
            results["parttime_income"].append(parttime_income)

            # 6. Rebalancing happens automatically by using target allocation for next year's returns
            # (In reality, this is implicitly handled by always using target_allocation weights)

            # Update peak portfolio (in real terms)
            current_portfolio_real = current_portfolio / cumulative_inflation
            if current_portfolio_real > peak_portfolio_real:
                peak_portfolio_real = current_portfolio_real

            results["portfolio_values_end"].append(current_portfolio)

            # Check if we've run out of money (though we continue simulation even if negative)
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
                f"Portfolio=${results['portfolio_values_end'][i]:,.0f}, "
                f"Withdrawal=${results['withdrawals'][i]:,.0f}, "
                f"Part-time=${results['parttime_income'][i]:,.0f}, "
                f"Inflation={results['inflation_rates'][i]:.1%}"
            )

    print(f"\nFinal portfolio: ${results['portfolio_values_end'][-1]:,.0f}")
    print(f"Success: {results['success']}")


if __name__ == "__main__":
    main()
