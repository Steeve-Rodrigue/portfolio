from fastapi import APIRouter

from app.core.database import get_pool

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/health_db")
async def health_db():
    try:
        pool = await get_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {"status": "ok", "database": "connected"}
    
    except Exception:
        return {"status": "degraded"}