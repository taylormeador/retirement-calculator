from fastapi import APIRouter

router = APIRouter(prefix="/simulations")


@router.get("/")
async def get_simulations():
    return {"TODO": "Implement simulations service"}
