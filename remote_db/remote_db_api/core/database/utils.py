from typing import AsyncGenerator
from fastapi import Body
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.mariadb_database import mariadb_async_session, autocommit_mariadb_async_session
from core.database.mssql_database import mssql_async_session, autocommit_mssql_async_session
from core.database.postgres_database import postgres_async_session, autocommit_postgres_async_session


async def get_session(dbms_name: str = Body(...)) -> AsyncGenerator[AsyncSession, None]:
    match dbms_name:
        case 'mssql':
            async with mssql_async_session() as mssql_session:
                yield mssql_session
        case 'postgresql':
            async with postgres_async_session() as postgres_session:
                yield postgres_session
        case 'mariadb' | 'mysql':
            async with mariadb_async_session() as mariadb_session:
                yield mariadb_session
        case _:
            yield


async def get_autocommit_session(dbms_name: str = Body(...)) -> AsyncGenerator[AsyncSession, None]:
    match dbms_name:
        case 'mssql':
            async with autocommit_mssql_async_session() as autocommit_mssql_session:
                yield autocommit_mssql_session
        case 'postgresql':
            async with autocommit_postgres_async_session() as autocommit_postgres_session:
                yield autocommit_postgres_session
        case 'mariadb' | 'mysql':
            async with autocommit_mariadb_async_session() as autocommit_mariadb_session:
                yield autocommit_mariadb_session
        case _:
            yield
