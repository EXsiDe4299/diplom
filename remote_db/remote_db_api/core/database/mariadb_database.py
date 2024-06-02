from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from core.config import MARIADB_DB_USER, MARIADB_DB_NAME, MARIADB_DB_PASSWORD
from core.database.database_helper import get_connection_string

MARIADB_DATABASE_URL = get_connection_string(dbms_name='mariadb', user=MARIADB_DB_USER,
                                             password=MARIADB_DB_PASSWORD, db_name=MARIADB_DB_NAME)

mariadb_engine = create_async_engine(MARIADB_DATABASE_URL)
autocommit_mariadb_engine = mariadb_engine.execution_options(isolation_level="AUTOCOMMIT")
mariadb_async_session = async_sessionmaker(mariadb_engine, class_=AsyncSession, expire_on_commit=False)

autocommit_mariadb_async_session = async_sessionmaker(autocommit_mariadb_engine, class_=AsyncSession,
                                                      expire_on_commit=False)
