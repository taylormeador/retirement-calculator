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

    def calculate_portfolio_return(self, allocation):
        """
        Calculate portfolio return for given allocation.

        allocation: dict like {'stocks': 0.6, 'bonds': 0.3, 'cash': 0.1}

        Returns: tuple of (portfolio_nominal_return, inflation_rate)
        """
        annual_returns = self.generate_annual_returns(n_samples=1)[0]
        asset_returns = annual_returns[:3]
        inflation_rate = annual_returns[3]

        # Calculate weighted portfolio return
        weights = np.array(
            [allocation["stocks"], allocation["bonds"], allocation["cash"]]
        )
        portfolio_nominal_return = np.dot(asset_returns, weights)

        return portfolio_nominal_return, inflation_rate


def main():
    portfolio = Portfolio()

    allocation = {"stocks": 0.6, "bonds": 0.3, "cash": 0.1}

    # Test multiple years
    print("Sample portfolio returns over 10 years:\n")
    for year in range(1, 11):
        portfolio_return, inflation = portfolio.calculate_portfolio_return(allocation)
        print(
            f"Year {year}: Portfolio Return = {portfolio_return:.2%}, Inflation = {inflation:.2%}"
        )


if __name__ == "__main__":
    main()
