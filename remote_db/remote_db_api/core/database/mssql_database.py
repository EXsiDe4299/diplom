from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from core.config import MSSQL_DB_USER, MSSQL_DB_PASSWORD, MSSQL_DB_NAME
from core.database.database_helper import get_connection_string

MSSQL_DATABASE_URL = get_connection_string(dbms_name='mssql', user=MSSQL_DB_USER, password=MSSQL_DB_PASSWORD,
                                           db_name=MSSQL_DB_NAME)


mssql_engine = create_async_engine(MSSQL_DATABASE_URL)
autocommit_mssql_engine = mssql_engine.execution_options(isolation_level="AUTOCOMMIT")

mssql_async_session = async_sessionmaker(mssql_engine, class_=AsyncSession, expire_on_commit=False)
autocommit_mssql_async_session = async_sessionmaker(autocommit_mssql_engine, class_=AsyncSession,
                                                    expire_on_commit=False)

