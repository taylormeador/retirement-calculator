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

    def __init__(self, data_path: str = "data/historical_returns.csv"):
        """
        Initialize with historical data.
        """
        self.data_path = data_path
        self.df = None
        self._load_data()

    def _load_data(self):
        """Load historical data from CSV"""
        try:
            # TODO: Replace with actual Shiller data
            # For now, create dummy data
            self.df = pd.DataFrame(
                {
                    "year": range(1926, 2025),
                    "stocks": np.random.normal(0.10, 0.18, 99),
                    "bonds": np.random.normal(0.04, 0.06, 99),
                    "cash": np.random.normal(0.025, 0.005, 99),
                    "inflation": np.random.normal(0.025, 0.025, 99),
                }
            )
        except FileNotFoundError:
            # TODO: Handle missing data file
            raise

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

        # Filter by asset classes if specified
        columns = ["year"]
        if assets:
            columns.extend([asset.value for asset in assets])
        else:
            columns.extend(["stocks", "bonds", "cash", "inflation"])

        df = df[columns]

        # Convert to response model
        data = [HistoricalReturnData(**row) for row in df.to_dict("records")]

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
            last_updated="2024-12-31",  # TODO: Make this dynamic
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

        # Calculate correlations
        corr_matrix = self.df[["stocks", "bonds", "cash", "inflation"]].corr()

        correlations = CorrelationMatrix(
            stocks_bonds=float(corr_matrix.loc["stocks", "bonds"]),
            stocks_cash=float(corr_matrix.loc["stocks", "cash"]),
            stocks_inflation=float(corr_matrix.loc["stocks", "inflation"]),
            bonds_cash=float(corr_matrix.loc["bonds", "cash"]),
            bonds_inflation=float(corr_matrix.loc["bonds", "inflation"]),
            cash_inflation=float(corr_matrix.loc["cash", "inflation"]),
        )

        return HistoricalSummaryResponse(
            stocks=calc_stats(self.df["stocks"]),
            bonds=calc_stats(self.df["bonds"]),
            cash=calc_stats(self.df["cash"]),
            inflation=calc_stats(self.df["inflation"]),
            correlations=correlations,
            period=f"{int(self.df['year'].min())}-{int(self.df['year'].max())}",
            n_years=len(self.df),
        )


# Global instance (loaded once at startup)
historical_service = HistoricalDataService()
