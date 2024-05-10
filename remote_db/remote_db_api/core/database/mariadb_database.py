from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from core.config import MARIADB_DB_USER, MARIADB_DB_HOST, MARIADB_DB_NAME, MARIADB_DB_PORT, MARIADB_DB_PASSWORD


def get_mariadb_db_url(mariadb_db_user: str = MARIADB_DB_USER, mariadb_db_password: str = MARIADB_DB_PASSWORD,
                       mariadb_db_host: str = MARIADB_DB_HOST, mariadb_db_port: str = MARIADB_DB_PORT,
                       mariadb_db_name: str = MARIADB_DB_NAME):
    connection_string = f"mysql+asyncmy://{mariadb_db_user}:{mariadb_db_password}@{mariadb_db_host}:{mariadb_db_port}/{mariadb_db_name}"
    return connection_string


MARIADB_DATABASE_URL = get_mariadb_db_url()

MariadbBase = declarative_base()

mariadb_engine = create_async_engine(MARIADB_DATABASE_URL)
autocommit_mariadb_engine = mariadb_engine.execution_options(isolation_level="AUTOCOMMIT")
mariadb_async_session = async_sessionmaker(mariadb_engine, class_=AsyncSession, expire_on_commit=False)

autocommit_mariadb_async_session = async_sessionmaker(autocommit_mariadb_engine, class_=AsyncSession,
                                                      expire_on_commit=False)


async def get_mariadb_session() -> AsyncGenerator[AsyncSession, None]:
    async with mariadb_async_session() as mariadb_session:
        yield mariadb_session


async def get_autocommit_mariadb_session() -> AsyncGenerator[AsyncSession, None]:
    async with autocommit_mariadb_async_session() as autocommit_mariadb_session:
        yield autocommit_mariadb_session
