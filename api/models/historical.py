from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class AssetClass(str, Enum):
    """Valid asset classes for historical data"""

    STOCKS = "stocks"
    BONDS = "bonds"
    CASH = "cash"
    INFLATION = "inflation"


class HistoricalReturnData(BaseModel):
    """Single year of historical return data"""

    year: int
    stocks: Optional[float] = None
    bonds: Optional[float] = None
    cash: Optional[float] = None
    inflation: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "year": 1926,
                "stocks": 0.1162,
                "bonds": -0.0079,
                "cash": 0.0327,
                "inflation": 0.0149,
            }
        }


class HistoricalReturnsRequest(BaseModel):
    """Query parameters for historical returns"""

    start_year: Optional[int] = Field(None, ge=1871, le=2024)
    end_year: Optional[int] = Field(None, ge=1871, le=2024)
    assets: Optional[List[AssetClass]] = Field(
        default=None, description="Filter to specific asset classes"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "start_year": 1926,
                "end_year": 2024,
                "assets": ["stocks", "bonds", "inflation"],
            }
        }


class HistoricalReturnsResponse(BaseModel):
    """Response containing historical return data"""

    data: List[HistoricalReturnData]
    count: int
    start_year: int
    end_year: int
    source: str = "shiller"


class YearRangeResponse(BaseModel):
    """Available year range for historical data"""

    min_year: int
    max_year: int
    total_years: int
    source: str = "shiller"
    last_updated: Optional[str] = None


class HistoricalSummaryStats(BaseModel):
    """Summary statistics for an asset class"""

    mean: float
    std_dev: float
    min: float
    max: float
    median: float


class CorrelationMatrix(BaseModel):
    """Correlation matrix between asset classes"""

    stocks_bonds: float
    stocks_cash: float
    stocks_inflation: float
    bonds_cash: float
    bonds_inflation: float
    cash_inflation: float


class HistoricalSummaryResponse(BaseModel):
    """Summary statistics from historical data"""

    stocks: HistoricalSummaryStats
    bonds: HistoricalSummaryStats
    cash: HistoricalSummaryStats
    inflation: HistoricalSummaryStats
    correlations: CorrelationMatrix
    period: str  # e.g., "1926-2024"
    n_years: int
