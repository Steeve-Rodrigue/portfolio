import asyncpg

from app.models.profile import ProfileUpdate


async def get(pool: asyncpg.Pool) -> dict | None:
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM profile LIMIT 1")
    return dict(row) if row else None


async def update(pool: asyncpg.Pool, data: ProfileUpdate) -> dict | None:
    fields = data.model_dump(exclude_unset=True)
    if not fields:
        return await get(pool)

    keys = list(fields.keys())
    values = list(fields.values())
    set_clause = ", ".join(f"{key} = ${i + 1}" for i, key in enumerate(keys))
    set_clause += ", updated_at = now()"

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            f"UPDATE profile SET {set_clause} WHERE lock = true RETURNING *",
            *values,
        )
    return dict(row) if row else None
