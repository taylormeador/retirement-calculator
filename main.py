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


class MonteCarloSimulation:
    def __init__(self, portfolio, params):
        """
        portfolio: Portfolio instance
        params: same as RetirementSimulation params
        """
        self.portfolio = portfolio
        self.params = params

    def run(self, n_simulations=10000):
        """
        Run Monte Carlo simulation with n_simulations independent trials.

        Returns:
            all_simulations: list of individual simulation results
            summary: dict of aggregated statistics
        """
        all_simulations = []

        print(f"Running {n_simulations} Monte Carlo simulations...")

        for i in range(n_simulations):
            if (i + 1) % 1000 == 0:
                print(f"  Completed {i + 1}/{n_simulations} simulations")

            sim = RetirementSimulation(self.portfolio, self.params)
            results = sim.simulate_single_retirement()
            all_simulations.append(results)

        print(
            f"Completed all {n_simulations} simulations. Computing summary statistics...\n"
        )

        # Compute summary statistics
        summary = self._compute_summary(all_simulations)

        return all_simulations, summary

    def _compute_summary(self, all_simulations):
        """Compute aggregate statistics across all simulations"""
        n_sims = len(all_simulations)

        # Success rate
        successes = sum(1 for sim in all_simulations if sim["success"])
        success_rate = successes / n_sims

        # Final portfolio values
        final_portfolios = [sim["portfolio_values_end"][-1] for sim in all_simulations]
        final_portfolios_sorted = sorted(final_portfolios)

        # Years of part-time work
        years_working = [
            sum(1 for income in sim["parttime_income"] if income > 0)
            for sim in all_simulations
        ]

        # Probability of working at all
        prob_any_work = sum(1 for years in years_working if years > 0) / n_sims

        # Portfolio value over time (median and percentiles for each year)
        n_years = self.params["simulation_years"]
        portfolio_over_time = {
            "median": [],
            "p10": [],  # 10th percentile (bad outcomes)
            "p25": [],
            "p75": [],
            "p90": [],  # 90th percentile (good outcomes)
        }

        for year in range(n_years):
            values_this_year = [
                sim["portfolio_values_end"][year] for sim in all_simulations
            ]
            portfolio_over_time["median"].append(np.median(values_this_year))
            portfolio_over_time["p10"].append(np.percentile(values_this_year, 10))
            portfolio_over_time["p25"].append(np.percentile(values_this_year, 25))
            portfolio_over_time["p75"].append(np.percentile(values_this_year, 75))
            portfolio_over_time["p90"].append(np.percentile(values_this_year, 90))

        # Age at portfolio depletion (for failed scenarios)
        depletion_ages = []
        for sim in all_simulations:
            if not sim["success"]:
                # Find first year where portfolio hit 0
                for i, value in enumerate(sim["portfolio_values_end"]):
                    if value <= 0:
                        depletion_ages.append(sim["ages"][i])
                        break

        summary = {
            "n_simulations": n_sims,
            "success_rate": success_rate,
            "failure_rate": 1 - success_rate,
            # Final portfolio statistics
            "final_portfolio": {
                "median": np.median(final_portfolios),
                "mean": np.mean(final_portfolios),
                "p10": np.percentile(final_portfolios, 10),
                "p25": np.percentile(final_portfolios, 25),
                "p75": np.percentile(final_portfolios, 75),
                "p90": np.percentile(final_portfolios, 90),
                "min": min(final_portfolios),
                "max": max(final_portfolios),
            },
            # Part-time work statistics
            "years_working": {
                "median": np.median(years_working),
                "mean": np.mean(years_working),
                "max": max(years_working),
                "p90": np.percentile(years_working, 90),
            },
            "prob_any_parttime_work": prob_any_work,
            # Portfolio trajectory over time
            "portfolio_over_time": portfolio_over_time,
            # Failure statistics
            "depletion_age": {
                "median": np.median(depletion_ages) if depletion_ages else None,
                "mean": np.mean(depletion_ages) if depletion_ages else None,
                "earliest": min(depletion_ages) if depletion_ages else None,
            },
        }

        return summary


def print_summary(summary, params):
    """Pretty print the Monte Carlo summary statistics"""
    print("=" * 70)
    print("MONTE CARLO SIMULATION SUMMARY")
    print("=" * 70)
    print(f"Number of simulations: {summary['n_simulations']:,}")
    print(f"Retirement age: {params['retirement_age']}")
    print(f"Starting portfolio: ${params['starting_portfolio']:,.0f}")
    print(f"Annual spending: ${params['annual_spending']:,.0f}")
    print(f"Target allocation: {params['target_allocation']}")
    print()

    print("-" * 70)
    print("SUCCESS METRICS")
    print("-" * 70)
    print(f"Success rate: {summary['success_rate']:.1%}")
    print(f"Failure rate: {summary['failure_rate']:.1%}")
    print()

    print("-" * 70)
    print("FINAL PORTFOLIO VALUE")
    print("-" * 70)
    fp = summary["final_portfolio"]
    print(f"Median:  ${fp['median']:,.0f}")
    print(f"Mean:    ${fp['mean']:,.0f}")
    print(f"10th %:  ${fp['p10']:,.0f}")
    print(f"90th %:  ${fp['p90']:,.0f}")
    print(f"Min:     ${fp['min']:,.0f}")
    print(f"Max:     ${fp['max']:,.0f}")
    print()

    print("-" * 70)
    print("PART-TIME WORK")
    print("-" * 70)
    print(
        f"Probability of needing part-time work: {summary['prob_any_parttime_work']:.1%}"
    )
    yw = summary["years_working"]
    print(f"Years of work (median): {yw['median']:.1f}")
    print(f"Years of work (mean):   {yw['mean']:.1f}")
    print(f"Years of work (max):    {yw['max']:.0f}")
    print(f"Years of work (90th%):  {yw['p90']:.1f}")
    print()

    if summary["depletion_age"]["median"]:
        print("-" * 70)
        print("FAILURE SCENARIOS (Portfolio Depletion)")
        print("-" * 70)
        da = summary["depletion_age"]
        print(f"Median depletion age: {da['median']:.0f}")
        print(f"Earliest depletion:   {da['earliest']:.0f}")
        print()

    print("=" * 70)


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

    # Run Monte Carlo simulation
    mc = MonteCarloSimulation(portfolio, params)
    all_simulations, summary = mc.run(n_simulations=10000)

    # Print summary
    print_summary(summary, params)

    # Example: Show portfolio trajectory over time
    print("\nPORTFOLIO VALUE TRAJECTORY (selected years)")
    print("-" * 70)
    print(f"{'Age':<6} {'Year':<6} {'10th %':<15} {'Median':<15} {'90th %':<15}")
    print("-" * 70)

    years_to_show = [0, 5, 10, 15, 17, 20, 30, 39]  # Include year 17 (when SS starts)
    for year in years_to_show:
        if year < len(summary["portfolio_over_time"]["median"]):
            age = params["retirement_age"] + year
            p10 = summary["portfolio_over_time"]["p10"][year]
            median = summary["portfolio_over_time"]["median"][year]
            p90 = summary["portfolio_over_time"]["p90"][year]
            print(f"{age:<6} {year:<6} ${p10:<14,.0f} ${median:<14,.0f} ${p90:<14,.0f}")


if __name__ == "__main__":
    main()
