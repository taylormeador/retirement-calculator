from fastapi import FastAPI, APIRouter
from api.routers import simulations, historical

app = FastAPI()

# Add routes
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(simulations.router, tags=["simulations"])
api_router.include_router(historical.router, tags=["historical"])
app.include_router(api_router)


@app.get("/")
async def root():
    return {"hello": "world"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
