from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import close_pool
from app.routers import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_pool()


app = FastAPI(
    title="Portfolio API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(health.router)
