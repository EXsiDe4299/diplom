from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from core.config import POSTGRES_DB_USER, POSTGRES_DB_PASSWORD, POSTGRES_DB_NAME
from core.database.database_helper import get_connection_string

POSTGRES_DATABASE_URL = get_connection_string(dbms_name='postgresql', user=POSTGRES_DB_USER,
                                              password=POSTGRES_DB_PASSWORD, db_name=POSTGRES_DB_NAME)


postgres_engine = create_async_engine(POSTGRES_DATABASE_URL)
autocommit_postgres_engine = postgres_engine.execution_options(isolation_level="AUTOCOMMIT")

postgres_async_session = async_sessionmaker(postgres_engine, class_=AsyncSession, expire_on_commit=False)
autocommit_postgres_async_session = async_sessionmaker(autocommit_postgres_engine, class_=AsyncSession,
                                                       expire_on_commit=False)

