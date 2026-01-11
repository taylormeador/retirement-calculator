from fastapi import APIRouter, Query
from typing import Optional, List
from api.models.historical import (
    HistoricalReturnsResponse,
    YearRangeResponse,
    HistoricalSummaryResponse,
    AssetClass,
)
from api.services.historical_service import historical_service

router = APIRouter(prefix="/historical")


@router.get("/returns", response_model=HistoricalReturnsResponse)
async def get_historical_returns(
    start_year: Optional[int] = Query(
        None, ge=1871, le=2024, description="Start year for data"
    ),
    end_year: Optional[int] = Query(
        None, ge=1871, le=2024, description="End year for data"
    ),
    assets: Optional[List[AssetClass]] = Query(
        None, description="Filter to specific asset classes"
    ),
):
    """
    Get historical return data.

    Returns yearly returns for stocks, bonds, cash, and inflation.
    Data sourced from Robert Shiller's historical database.
    """
    return historical_service.get_returns(
        start_year=start_year, end_year=end_year, assets=assets
    )


@router.get("/years", response_model=YearRangeResponse)
async def get_year_range():
    """
    Get the available year range for historical data.

    Returns the minimum and maximum years available in the dataset.
    """
    return historical_service.get_year_range()


@router.get("/summary", response_model=HistoricalSummaryResponse)
async def get_historical_summary():
    """
    Get summary statistics calculated from historical data.

    Returns means, standard deviations, and correlations for all asset classes.
    """
    return historical_service.get_summary()
