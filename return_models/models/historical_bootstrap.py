import numpy as np
import pandas as pd


def load_historical_data():
    """
    Load historical stock and bond returns.
    """
    data_path = "return_models/shiller.csv"
    df = pd.read_csv(
        data_path,
        usecols=[
            "year",
            "return_on_s_and_p_composite",
            "long_government_bond_yield",
            "consumer_price_index",
        ],
    )

    # Rename columns and trim to years with data.
    map_columns = {
        "return_on_s_and_p_composite": "stocks",
        "long_government_bond_yield": "bonds",
    }
    df = df.rename(columns=map_columns)
    df = df[df.year <= 2012]

    # Calculate inflation rate from CPI index
    df["inflation"] = df["consumer_price_index"].pct_change().fillna(0)
    df.bonds = df.bonds / 100 - df.inflation
    df.stocks = df.stocks - df.inflation

    return df[["stocks", "bonds"]]


def bootstrap_returns():
    """
    Generate returns by randomly sampling from historical data.

    This method:
    - Preserves the correlation structure (sample paired returns)
    - Captures fat tails, skewness, any patterns in historical data
    - No distributional assumptions
    """
    n_years = 30
    historical_data = load_historical_data()

    # Randomly sample n_years from historical data with replacement
    # Using .sample() preserves the paired structure (stocks + bonds together)
    sampled_data = historical_data.sample(n=n_years, replace=True, random_state=None)

    # Return as numpy array (n_years, 2)
    return sampled_data.values
