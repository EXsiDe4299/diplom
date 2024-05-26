from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from core.config import MSSQL_DB_USER, MSSQL_DB_PASSWORD, MSSQL_DB_HOST, MSSQL_DB_NAME
from core.database.database_helper import get_connection_string

# MSSQL_DATABASE_URL = f"mssql+aioodbc://{MSSQL_DB_USER}:{MSSQL_DB_PASSWORD}@{MSSQL_DB_HOST}/{MSSQL_DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"


# def get_mssql_db_url(mssql_db_user: str = MSSQL_DB_USER, mssql_db_password: str = MSSQL_DB_PASSWORD,
#                      mssql_db_host: str = MSSQL_DB_HOST, mssql_db_name: str = MSSQL_DB_NAME):
#     connection_string = f"mssql+aioodbc://{mssql_db_user}:{mssql_db_password}@{mssql_db_host}/{mssql_db_name}?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
#     return connection_string


MSSQL_DATABASE_URL = get_connection_string(dbms_name='mssql', user=MSSQL_DB_USER, password=MSSQL_DB_PASSWORD,
                                           db_name=MSSQL_DB_NAME)

# MssqlBase = declarative_base()

mssql_engine = create_async_engine(MSSQL_DATABASE_URL)
autocommit_mssql_engine = mssql_engine.execution_options(isolation_level="AUTOCOMMIT")

mssql_async_session = async_sessionmaker(mssql_engine, class_=AsyncSession, expire_on_commit=False)
autocommit_mssql_async_session = async_sessionmaker(autocommit_mssql_engine, class_=AsyncSession,
                                                    expire_on_commit=False)

# async def get_mssql_session() -> AsyncGenerator[AsyncSession, None]:
#     async with mssql_async_session() as mssql_session:
#         yield mssql_session
#
#
# async def get_autocommit_mssql_session() -> AsyncGenerator[AsyncSession, None]:
#     async with autocommit_mssql_async_session() as autocommit_mssql_session:
#         yield autocommit_mssql_session
