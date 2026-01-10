from fastapi import APIRouter
from api.services import historical

router = APIRouter(prefix="/historical")


@router.get("/returns")
async def get_returns(start_year: int, end_year: int, assets: str):
    return historical.get_returns(start_year, end_year, assets)
