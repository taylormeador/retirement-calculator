import pandas as pd
import numpy as np
from typing import List, Optional
from api.models.historical import (
    HistoricalReturnData,
    HistoricalReturnsResponse,
    YearRangeResponse,
    HistoricalSummaryResponse,
    HistoricalSummaryStats,
    CorrelationMatrix,
    AssetClass,
)


class HistoricalDataService:
    """Service for loading and querying historical return data"""

    def __init__(self, data_path: str = "api/data/shiller.csv"):
        """
        Initialize with historical data.
        """
        self.data_path = data_path
        self.df = self._load_data()

    def _load_data(self):
        """Load historical data from CSV and calculate returns"""
        try:
            df = pd.read_csv(self.data_path)
            df["year"] = df["year"].astype(int)
            df["stocks"] = df["return_on_s_and_p_composite"]
            df["bonds"] = df["long_government_bond_yield"] / 100
            df["cash"] = df["one_year_interest_rate"] / 100

            # Calculate inflation rate from CPI index
            df["inflation"] = df["consumer_price_index"].pct_change(fill_method=None)

            # Drop rows with NaN in any of our calculated columns
            df = df.dropna(subset=["year", "stocks", "bonds", "cash", "inflation"])

            # Reset index after dropping rows
            df = df.reset_index(drop=True)

            return df

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Historical data file not found at {self.data_path}"
            )

    def get_returns(
        self,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        assets: Optional[List[AssetClass]] = None,
    ) -> HistoricalReturnsResponse:
        """Get historical returns filtered by year range and asset classes"""

        df = self.df.copy()

        # Filter by year range
        if start_year:
            df = df[df["year"] >= start_year]
        if end_year:
            df = df[df["year"] <= end_year]

        # Get actual year range in filtered data
        actual_start = int(df["year"].min())
        actual_end = int(df["year"].max())

        # Select columns based on requested assets
        columns = ["year"]
        if assets:
            columns.extend([asset.value for asset in assets])
        else:
            columns.extend(["stocks", "bonds", "cash", "inflation"])

        df_subset = df[columns].copy()

        # Convert to response model
        data = [HistoricalReturnData(**row) for row in df_subset.to_dict("records")]

        return HistoricalReturnsResponse(
            data=data,
            count=len(data),
            start_year=actual_start,
            end_year=actual_end,
            source="shiller",
        )

    def get_year_range(self) -> YearRangeResponse:
        """Get available year range"""
        return YearRangeResponse(
            min_year=int(self.df["year"].min()),
            max_year=int(self.df["year"].max()),
            total_years=len(self.df),
            source="shiller",
            last_updated="2024-12-31",
        )

    def get_summary(self) -> HistoricalSummaryResponse:
        """Calculate summary statistics from historical data"""

        def calc_stats(series: pd.Series) -> HistoricalSummaryStats:
            return HistoricalSummaryStats(
                mean=float(series.mean()),
                std_dev=float(series.std()),
                min=float(series.min()),
                max=float(series.max()),
                median=float(series.median()),
            )

        # Use the calculated return columns
        stocks_data = self.df["stocks"]
        bonds_data = self.df["bonds"]
        cash_data = self.df["cash"]
        inflation_data = self.df["inflation"]

        # Create a temp dataframe for correlation calculation
        corr_df = pd.DataFrame(
            {
                "stocks": stocks_data,
                "bonds": bonds_data,
                "cash": cash_data,
                "inflation": inflation_data,
            }
        )

        corr_matrix = corr_df.corr()

        correlations = CorrelationMatrix(
            stocks_bonds=float(corr_matrix.loc["stocks", "bonds"]),
            stocks_cash=float(corr_matrix.loc["stocks", "cash"]),
            stocks_inflation=float(corr_matrix.loc["stocks", "inflation"]),
            bonds_cash=float(corr_matrix.loc["bonds", "cash"]),
            bonds_inflation=float(corr_matrix.loc["bonds", "inflation"]),
            cash_inflation=float(corr_matrix.loc["cash", "inflation"]),
        )

        return HistoricalSummaryResponse(
            stocks=calc_stats(stocks_data),
            bonds=calc_stats(bonds_data),
            cash=calc_stats(cash_data),
            inflation=calc_stats(inflation_data),
            correlations=correlations,
            period=f"{int(self.df['year'].min())}-{int(self.df['year'].max())}",
            n_years=len(self.df),
        )


# Global instance (loaded once at startup)
historical_service = HistoricalDataService()
