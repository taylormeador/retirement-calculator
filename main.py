import numpy as np


class Portfolio:
    def __init__(self):
        self._mean_vector = [0.1, 0.04, 0.025]
        self._correlations = [
            [1.0, -0.1, 0.0],  # Stocks vs [Stocks, Bonds, Cash]
            [-0.1, 1.0, 0.0],  # Bonds vs [Stocks, Bonds, Cash]
            [0.0, 0.0, 1.0],  # Cash vs [Stocks, Bonds, Cash]
        ]
        self._covariance_matrix = self._correlations * np.outer(
            self._mean_vector, self._mean_vector
        )

    def generate_annual_return(self, n_samples=1):
        """Generate correlated returns for stocks, bonds, and cash."""
        returns = np.random.multivariate_normal(
            mean=self._mean_vector,
            cov=self._covariance_matrix,
            size=n_samples,
        )
        return returns

    def calculate_portfolio_return(self, allocation):
        """
        asset_returns: array of [stock_return, bond_return, cash_return]
        allocation: dict like {'stocks': 0.6, 'bonds': 0.3, 'cash': 0.1}

        Returns: weighted portfolio return
        """
        asset_returns = self.generate_annual_return()
        weights = np.array(
            [allocation["stocks"], allocation["bonds"], allocation["cash"]]
        )
        portfolio_return = np.dot(asset_returns, weights)
        return portfolio_return


def main():
    portfolio = Portfolio()

    allocation = {"stocks": 0.6, "bonds": 0.3, "cash": 0.1}
    returns = portfolio.calculate_portfolio_return(allocation)
    print(returns)


if __name__ == "__main__":
    main()
