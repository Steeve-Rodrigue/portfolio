from fastapi import APIRouter

from app.database import get_pool

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.fetchval("SELECT 1")
    return {"status": "ok", "database": "connected"}
