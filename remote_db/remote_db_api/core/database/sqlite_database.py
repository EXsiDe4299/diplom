from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLITE_DB_URL = "sqlite+aiosqlite:///remote_db.db"

SqliteBase = declarative_base()
sqlite_engine = create_async_engine(SQLITE_DB_URL)
sqlite_async_session = async_sessionmaker(sqlite_engine, expire_on_commit=False)


async def get_sqlite_session() -> AsyncGenerator[AsyncSession, None]:
    async with sqlite_async_session() as sqlite_session:
        yield sqlite_session
