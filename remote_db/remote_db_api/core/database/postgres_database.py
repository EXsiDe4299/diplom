from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import POSTGRES_DB_USER, POSTGRES_DB_PASSWORD, POSTGRES_DB_HOST, POSTGRES_DB_PORT, POSTGRES_DB_NAME

POSTGRES_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_DB_USER}:{POSTGRES_DB_PASSWORD}@{POSTGRES_DB_HOST}:{POSTGRES_DB_PORT}/{POSTGRES_DB_NAME}"

PostgresBase = declarative_base()
postgres_engine = create_async_engine(POSTGRES_DATABASE_URL)
postgres_async_session = sessionmaker(postgres_engine, class_=AsyncSession, expire_on_commit=False)


async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
    async with postgres_async_session() as postgres_session:
        yield postgres_session
