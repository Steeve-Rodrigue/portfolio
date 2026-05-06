import asyncio

import asyncpg

from app.core.config import settings

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        for attempt in range(5):
            try:
                _pool = await asyncpg.create_pool(
                    dsn=settings.database_url,
                    min_size=2,
                    max_size=10,
                )
                break
            except Exception:
                if attempt == 4:
                    raise
                await asyncio.sleep(2**attempt)
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
