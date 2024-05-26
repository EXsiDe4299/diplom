from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import POSTGRES_DB_USER, POSTGRES_DB_PASSWORD, POSTGRES_DB_HOST, POSTGRES_DB_PORT, POSTGRES_DB_NAME
from core.database.database_helper import get_connection_string

# POSTGRES_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_DB_USER}:{POSTGRES_DB_PASSWORD}@{POSTGRES_DB_HOST}:{POSTGRES_DB_PORT}/{POSTGRES_DB_NAME}"

# def get_postgres_db_url(postgres_db_user: str = POSTGRES_DB_USER, postgres_db_password: str = POSTGRES_DB_PASSWORD,
#                         postgres_db_host: str = POSTGRES_DB_HOST, postgres_db_name: str = POSTGRES_DB_NAME,
#                         postgres_db_port: str = POSTGRES_DB_PORT):
#     connection_string = f"postgresql+asyncpg://{postgres_db_user}:{postgres_db_password}@{postgres_db_host}:{postgres_db_port}/{postgres_db_name}"
#     return connection_string


POSTGRES_DATABASE_URL = get_connection_string(dbms_name='postgresql', user=POSTGRES_DB_USER,
                                              password=POSTGRES_DB_PASSWORD, db_name=POSTGRES_DB_NAME)

# PostgresBase = declarative_base()

postgres_engine = create_async_engine(POSTGRES_DATABASE_URL)
autocommit_postgres_engine = postgres_engine.execution_options(isolation_level="AUTOCOMMIT")

postgres_async_session = async_sessionmaker(postgres_engine, class_=AsyncSession, expire_on_commit=False)
autocommit_postgres_async_session = async_sessionmaker(autocommit_postgres_engine, class_=AsyncSession,
                                                       expire_on_commit=False)

# async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
#     async with postgres_async_session() as postgres_session:
#         yield postgres_session
#
#
# async def get_autocommit_postgres_session() -> AsyncGenerator[AsyncSession, None]:
#     async with autocommit_postgres_async_session() as postgres_session:
#         yield postgres_session
