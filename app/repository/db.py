from __future__ import annotations
import logging
from typing import Optional
import asyncio

try:
    from psycopg_pool import AsyncConnectionPool
except Exception:  # pragma: no cover
    AsyncConnectionPool = None  # type: ignore

log = logging.getLogger(__name__)

class Database:
    def __init__(self, dsn: Optional[str]):
        self.dsn = dsn
        self.pool: Optional[AsyncConnectionPool] = None

    async def connect(self):
        if not self.dsn or not AsyncConnectionPool:
            log.info("DB disabled (no DATABASE_URL or psycopg_pool missing).")
            return
        self.pool = AsyncConnectionPool(self.dsn, max_size=10, kwargs={"autocommit": True})
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        chat_id BIGINT PRIMARY KEY,
                        first_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        last_seen  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        messages_count BIGINT NOT NULL DEFAULT 0
                    );
                    """
                )
        log.info("DB connected and schema ensured.")

    async def close(self):
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def bump_user(self, chat_id: int) -> None:
        if not self.pool:
            return
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO users (chat_id, messages_count)
                    VALUES (%s, 1)
                    ON CONFLICT (chat_id)
                    DO UPDATE SET
                      last_seen = NOW(),
                      messages_count = users.messages_count + 1;
                    """,
                    (chat_id,),
                )

    async def stats(self) -> tuple[int, int]:
        if not self.pool:
            return (0, 0)
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT COUNT(*), COALESCE(SUM(messages_count),0) FROM users;")
                row = await cur.fetchone()
                return (int(row[0]), int(row[1]))
