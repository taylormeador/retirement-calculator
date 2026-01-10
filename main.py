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
            - parttime_max_age: int (e.g., 65 - don't work past this age)
            - parttime_withdrawal_rate_threshold: float (e.g., 0.075 - trigger if WR exceeds this)
            - parttime_annual_income: float (e.g., 25000)
            - ss_start_age: int (e.g., 67)
            - ss_annual_benefit: float (e.g., 30000 in today's dollars)
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
            "spending_need": [],
            "parttime_income": [],
            "ss_income": [],
            "net_withdrawals": [],
            "withdrawal_rates": [],
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

        for year in range(self.params["simulation_years"]):
            age = self.params["retirement_age"] + year
            current_portfolio = stocks_value + bonds_value + cash_value

            results["years"].append(year)
            results["ages"].append(age)
            results["portfolio_values_start"].append(current_portfolio)

            # 1. Calculate spending need (adjusted for cumulative inflation)
            inflation_adjusted_spending = (
                self.params["annual_spending"] * cumulative_inflation
            )
            results["spending_need"].append(inflation_adjusted_spending)

            # 2. Calculate Social Security income (starts at ss_start_age, inflation-adjusted)
            ss_income = 0
            if age >= self.params["ss_start_age"]:
                ss_income = self.params["ss_annual_benefit"] * cumulative_inflation
            results["ss_income"].append(ss_income)

            # 3. Calculate how much we'd need to withdraw before considering part-time work
            preliminary_withdrawal = max(0, inflation_adjusted_spending - ss_income)

            # 4. Check if part-time income is needed (withdrawal rate trigger + age cap)
            parttime_income = 0
            if (
                self.params["enable_parttime_income"]
                and age <= self.params["parttime_max_age"]
                and current_portfolio > 0
            ):

                # Calculate what withdrawal rate would be without part-time work
                projected_withdrawal_rate = preliminary_withdrawal / current_portfolio

                if (
                    projected_withdrawal_rate
                    > self.params["parttime_withdrawal_rate_threshold"]
                ):
                    parttime_income = (
                        self.params["parttime_annual_income"] * cumulative_inflation
                    )

            results["parttime_income"].append(parttime_income)

            # 5. Calculate actual net withdrawal from portfolio
            net_withdrawal = max(
                0, inflation_adjusted_spending - ss_income - parttime_income
            )
            results["net_withdrawals"].append(net_withdrawal)

            # Calculate actual withdrawal rate
            if current_portfolio > 0:
                actual_withdrawal_rate = net_withdrawal / current_portfolio
            else:
                actual_withdrawal_rate = 0
            results["withdrawal_rates"].append(actual_withdrawal_rate)

            # 6. Withdraw net amount from portfolio (proportionally from each asset)
            if current_portfolio > 0 and net_withdrawal > 0:
                withdrawal_fraction = net_withdrawal / current_portfolio
                stocks_value *= 1 - withdrawal_fraction
                bonds_value *= 1 - withdrawal_fraction
                cash_value *= 1 - withdrawal_fraction

            # 7. Generate returns for this year
            annual_returns = self.portfolio.generate_annual_returns(n_samples=1)[0]
            stock_return = annual_returns[0]
            bond_return = annual_returns[1]
            cash_return = annual_returns[2]
            inflation_rate = annual_returns[3]
            results["inflation_rates"].append(inflation_rate)

            # Update cumulative inflation
            cumulative_inflation *= 1 + inflation_rate

            # 8. Apply returns to each asset class independently
            stocks_value *= 1 + stock_return
            bonds_value *= 1 + bond_return
            cash_value *= 1 + cash_return

            # Portfolio value after returns, before rebalancing
            current_portfolio = stocks_value + bonds_value + cash_value

            # 9. Rebalance to target allocation
            stocks_value = (
                current_portfolio * self.params["target_allocation"]["stocks"]
            )
            bonds_value = current_portfolio * self.params["target_allocation"]["bonds"]
            cash_value = current_portfolio * self.params["target_allocation"]["cash"]

            results["stocks_values"].append(stocks_value)
            results["bonds_values"].append(bonds_value)
            results["cash_values"].append(cash_value)
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
        "parttime_max_age": 65,
        "parttime_withdrawal_rate_threshold": 0.075,  # 7.5%
        "parttime_annual_income": 25000,
        "ss_start_age": 67,
        "ss_annual_benefit": 15000,  # In today's dollars
    }

    sim = RetirementSimulation(portfolio, params)
    results = sim.simulate_single_retirement()

    # Print sample results
    print(
        f"Retirement simulation: Age {params['retirement_age']} to {params['retirement_age'] + params['simulation_years'] - 1}"
    )
    print(f"Starting portfolio: ${params['starting_portfolio']:,.0f}")
    print(f"Annual spending: ${params['annual_spending']:,.0f}")
    print(
        f"SS benefit (starts age {params['ss_start_age']}): ${params['ss_annual_benefit']:,.0f}\n"
    )

    print("Sample years:")
    for i in [0, 9, 16, 19, 29, 39]:  # Include year when SS starts (age 67 = year 17)
        if i < len(results["years"]):
            print(
                f"Age {results['ages'][i]}: "
                f"Portfolio=${results['portfolio_values_end'][i]:,.0f}, "
                f"Need=${results['spending_need'][i]:,.0f}, "
                f"SS=${results['ss_income'][i]:,.0f}, "
                f"Part-time=${results['parttime_income'][i]:,.0f}, "
                f"Withdrawal=${results['net_withdrawals'][i]:,.0f} "
                f"({results['withdrawal_rates'][i]:.1%})"
            )

    print(f"\nFinal portfolio: ${results['portfolio_values_end'][-1]:,.0f}")
    print(f"Success: {results['success']}")

    # Calculate total years of part-time work
    years_worked = sum(1 for income in results["parttime_income"] if income > 0)
    print(f"Years of part-time work needed: {years_worked}")


if __name__ == "__main__":
    main()
