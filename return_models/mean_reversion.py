import numpy as np


def ar1_returns():
    """
    Generate returns using AR(1) mean reversion model.

    Model: r_t = μ + φ(r_{t-1} - μ) + ε_t
    where ε_t ~ N(0, σ²)

    φ = autocorrelation parameter
    - φ = 0: no persistence (iid normal)
    - 0 < φ < 1: positive autocorrelation (momentum)
    - -1 < φ < 0: negative autocorrelation (mean reversion)

    For mean reversion: use φ = -0.3
    - Negative φ means bad years tend to be followed by good years
    - Literature on equity returns shows weak evidence for mean reversion
    - Pfau and others test this assumption

    Note: treating stocks and bonds independently (no correlation)
    """

    # Parameters
    n_years = 30

    # Stock parameters - mild mean reversion
    stock_mu = 0.10
    stock_phi = -0.3
    stock_historical_std = 0.20
    # Innovation std adjusted so unconditional variance matches historical
    # Unconditional variance = σ²/(1-φ²), so σ = historical_std * sqrt(1-φ²)
    stock_sigma = stock_historical_std * np.sqrt(1 - stock_phi**2)

    # Bond parameters - mild mean reversion
    bond_mu = 0.05
    bond_phi = -0.3
    bond_historical_std = 0.06
    bond_sigma = bond_historical_std * np.sqrt(1 - bond_phi**2)

    # Initialize returns arrays
    stock_returns = np.zeros(n_years)
    bond_returns = np.zeros(n_years)

    # Set initial values to long-run means
    stock_returns[0] = stock_mu
    bond_returns[0] = bond_mu

    # Generate AR(1) process
    for t in range(1, n_years):
        # Stock return
        epsilon_stock = np.random.normal(0, stock_sigma)
        stock_returns[t] = (
            stock_mu + stock_phi * (stock_returns[t - 1] - stock_mu) + epsilon_stock
        )

        # Bond return
        epsilon_bond = np.random.normal(0, bond_sigma)
        bond_returns[t] = (
            bond_mu + bond_phi * (bond_returns[t - 1] - bond_mu) + epsilon_bond
        )

    # Combine into single array (n_years, 2)
    returns = np.column_stack([stock_returns, bond_returns])

    return returns


result = ar1_returns()
breakpoint()
