import secrets
import string

from sqlalchemy import text, select, and_, delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from core.models.sqlite_models import User, Account, Database, AccountDatabase
from core.schemas.database import DatabaseInteractionScheme
from core.schemas.user import CreateUserScheme, CreatedUserScheme


# user
async def verify_connection_string(connection_string):
    test_engine = create_async_engine(connection_string)
    test_engine_name = test_engine.name
    test_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with test_session() as session:
        try:
            match test_engine_name:
                case 'mssql':
                    await session.execute(text("SELECT @@VERSION"))
                case 'postgresql':
                    await session.execute(text("SELECT version()"))
                case 'mysql':
                    await session.execute(text("SELECT @@version"))
        finally:
            await session.close()
            await test_engine.dispose()


async def create_or_get_user_id(user_data: CreateUserScheme, sqlite_session: AsyncSession):
    user = await sqlite_session.execute(select(User).filter(User.user_telegram_id == user_data.user_telegram_id))
    user = user.first()
    if not user:
        new_user = User(user_telegram_id=user_data.user_telegram_id)
        sqlite_session.add(new_user)
        await sqlite_session.flush()
        user_id = new_user.user_id
    else:
        user = user[0]
        user_id = user.user_id
    return user_id


async def check_account_existing(user_data: CreateUserScheme | DatabaseInteractionScheme, sqlite_session: AsyncSession,
                                 dbms_name: str):
    account_type_id = int()
    match dbms_name:
        case 'mssql':
            account_type_id = 1
        case 'postgresql':
            account_type_id = 2
        case 'mysql':
            account_type_id = 3
    has_account = await sqlite_session.execute(select(Account).join(User).
                                               filter(User.user_telegram_id == user_data.user_telegram_id).
                                               filter(Account.account_type_id == account_type_id))
    has_account = has_account.first()
    if has_account:
        return True
    else:
        return False


async def create_new_account(*, user_id: int, user_data: CreateUserScheme, sqlite_session: AsyncSession,
                             session: AsyncSession):
    dbms_name = session.get_bind().name
    alphabet = string.ascii_letters + string.digits
    user_password = ''.join(secrets.choice(alphabet) for _ in range(8))
    account_type_id = int()
    create_user_query = str()
    match dbms_name:
        case 'mssql':
            account_type_id = 1
            create_user_query = ("USE remote_db;\n" +
                                 f"CREATE LOGIN {user_data.user_login} WITH PASSWORD='{user_password}';\n\n" +
                                 f"ALTER SERVER ROLE dbcreator ADD MEMBER {user_data.user_login};\n" +
                                 "USE master;\n" +
                                 f"GRANT CREATE ANY DATABASE TO {user_data.user_login};")
        case 'postgresql':
            account_type_id = 2
            create_user_query = f"CREATE USER {user_data.user_login} WITH PASSWORD '{user_password}' CREATEDB;"
        case 'mysql':
            account_type_id = 3
            create_user_query = f"CREATE USER '{user_data.user_login}'@localhost IDENTIFIED BY '{user_password}';"

    new_account = Account(account_user_id=user_id, account_login=user_data.user_login, account_password=user_password,
                          account_type_id=account_type_id)
    sqlite_session.add(new_account)

    await session.execute(text(create_user_query))

    new_user = CreatedUserScheme(user_login=user_data.user_login, user_password=user_password)
    return new_user


async def remind_password(user_data: CreateUserScheme, sqlite_session: AsyncSession, dbms_name: str):
    account_type_id = int()
    match dbms_name:
        case 'mssql':
            account_type_id = 1
        case 'postgresql':
            account_type_id = 2
        case 'mysql':
            account_type_id = 3
    user_password = await sqlite_session.execute(
        select(Account.account_password).join(User).filter(User.user_telegram_id == user_data.user_telegram_id).filter(
            Account.account_login == user_data.user_login).filter(Account.account_type_id == account_type_id))
    user_password = user_password.first()[0]
    return user_password


# database
async def create_database(data: DatabaseInteractionScheme, session: AsyncSession):
    dbms_name = session.get_bind().name
    match dbms_name:
        case 'mssql':
            await session.execute(text(f"CREATE DATABASE {data.database_name}"))
            await session.execute(text(f"USE {data.database_name};\n" +
                                       f"CREATE USER {data.user_login} FOR LOGIN {data.user_login}"))
        case 'postgresql':
            await session.execute(
                text(f"CREATE DATABASE {data.database_name} OWNER {data.user_login};"))
        case 'mysql':
            await session.execute(text(f"CREATE DATABASE {data.database_name}"))
            await session.execute(
                text(f"GRANT ALL PRIVILEGES ON {data.database_name}.* TO {data.user_login}@localhost;"))


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


# connection string
async def user_authentication(data: DatabaseInteractionScheme, sqlite_session: AsyncSession, dbms_name: str):
    account_type_id = int()
    match dbms_name:
        case 'mssql':
            account_type_id = 1
        case 'postgresql':
            account_type_id = 2
        case 'mysql':
            account_type_id = 3

    user = await sqlite_session.execute(
        select(Account).join(User).filter(and_(User.user_telegram_id == data.user_telegram_id,
                                               Account.account_type_id == account_type_id)))
    user = user.first()[0]

    if user.account_login != data.user_login or user.account_password != data.user_password:
        return False
    else:
        return True
