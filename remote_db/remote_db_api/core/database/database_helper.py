from core.config import MSSQL_DB_HOST, POSTGRES_DB_HOST, POSTGRES_DB_PORT, MARIADB_DB_HOST, MARIADB_DB_PORT


def get_connection_string(dbms_name: str, user: str | None = None, password: str | None = None,
                          db_name: str | None = None):
    match dbms_name:
        case 'mssql':
            connection_string = f"mssql+aioodbc://{user}:{password}@{MSSQL_DB_HOST}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
            return connection_string
        case 'postgresql':
            connection_string = f"postgresql+asyncpg://{user}:{password}@{POSTGRES_DB_HOST}:{POSTGRES_DB_PORT}/{db_name}"
            return connection_string
        case 'mariadb' | 'mysql':
            connection_string = f"mysql+asyncmy://{user}:{password}@{MARIADB_DB_HOST}:{MARIADB_DB_PORT}/{db_name}"
            return connection_string
