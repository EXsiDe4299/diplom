from sqlalchemy import text, select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.sqlite_models import User, Account, Database, AccountDatabase
from core.schemas.database import DatabaseInteractionScheme


async def create_database(data: DatabaseInteractionScheme, session: AsyncSession):
    dbms_name = session.get_bind().name
    match dbms_name:
        case 'mssql':
            await session.execute(text(f"CREATE DATABASE {data.database_name}"))
            await session.execute(text(f"USE {data.database_name};\n" +
                                       f"CREATE USER {data.account_login} FOR LOGIN {data.account_login}"))
        case 'postgresql':
            await session.execute(
                text(f"CREATE DATABASE {data.database_name} OWNER {data.account_login};"))
        case 'mysql':
            await session.execute(text(f"CREATE DATABASE {data.database_name}"))
            await session.execute(
                text(f"GRANT ALL PRIVILEGES ON {data.database_name}.* TO {data.account_login}@localhost;"))


async def add_new_account_database(data: DatabaseInteractionScheme, sqlite_session: AsyncSession,
                                   session: AsyncSession):
    account_type_id = int()
    database_type_id = int()
    dbms_name = session.get_bind().name
    match dbms_name:
        case 'mssql':
            account_type_id = 1
            database_type_id = 1
        case 'postgresql':
            account_type_id = 2
            database_type_id = 2
        case 'mysql':
            account_type_id = 3
            database_type_id = 3

    new_database = Database(database_name=data.database_name, database_type_id=database_type_id)
    sqlite_session.add(new_database)
    await sqlite_session.flush()
    database_id = new_database.database_id

    account = await sqlite_session.execute(select(Account.account_id).
                                           join(User).filter(and_(User.user_telegram_id == data.user_telegram_id,
                                                                  Account.account_type_id == account_type_id)))
    account = account.first()
    account_id = account[0]

    new_account_database = AccountDatabase(database_id=database_id, account_id=account_id)
    sqlite_session.add(new_account_database)


async def check_databases_quantity(data: DatabaseInteractionScheme, sqlite_session: AsyncSession, dbms_name: str):
    account_type_id = int()
    match dbms_name:
        case 'mssql':
            account_type_id = 1
        case 'postgresql':
            account_type_id = 2
        case 'mysql':
            account_type_id = 3
    account = await sqlite_session.execute(select(Account.account_id).
                                           join(User).filter(and_(User.user_telegram_id == data.user_telegram_id,
                                                                  Account.account_type_id == account_type_id)))
    account = account.first()
    account_id: int = account[0]
    accounts_databases = await sqlite_session.execute(
        select(AccountDatabase).filter(AccountDatabase.account_id == account_id))
    accounts_databases = accounts_databases.fetchall()
    if len(accounts_databases) >= 3:
        return False
    else:
        return True


async def delete_database(data: DatabaseInteractionScheme, sqlite_session: AsyncSession, session: AsyncSession):
    dbms_name = session.get_bind().name
    database_type_id = int()
    match dbms_name:
        case 'mssql':
            database_type_id = 1
        case 'postgresql':
            database_type_id = 2
        case 'mysql':
            database_type_id = 3
    database = await sqlite_session.execute(select(Database).filter(
        and_(Database.database_name == data.database_name, Database.database_type_id == database_type_id)))
    database = database.first()[0]
    database_id: int = database.database_id
    database_name = database.database_name
    match database_type_id:
        case 1:
            await session.execute(text(f"USE master;\n" +
                                       f"ALTER DATABASE {database_name} SET SINGLE_USER WITH ROLLBACK IMMEDIATE;\n" +
                                       f"DROP DATABASE {database_name};"))
        case 2:
            await session.execute(text(f"DROP DATABASE {database_name} WITH (FORCE);"))
        case 3:
            await session.execute(text(f"DROP DATABASE {database_name};"))
    await sqlite_session.execute(delete(AccountDatabase).filter(AccountDatabase.database_id == database_id))
    await sqlite_session.execute(delete(Database).filter(Database.database_id == database_id))
