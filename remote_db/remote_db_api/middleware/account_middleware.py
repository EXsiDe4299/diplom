import secrets
import string

from sqlalchemy import text, select, and_
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from core.models.sqlite_models import User, Account
from core.schemas.account import CreateAccountScheme, CreatedAccountScheme
from core.schemas.database import DatabaseInteractionScheme


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
            # pass
            await session.close()
            await test_engine.dispose()


async def get_user_id(user_data: CreateAccountScheme, sqlite_session: AsyncSession):
    user = await sqlite_session.execute(select(User).filter(User.user_telegram_id == user_data.user_telegram_id))
    user = user.first()[0]
    user_id = user.user_id
    return user_id


async def check_account_existing(user_data: CreateAccountScheme | DatabaseInteractionScheme,
                                 sqlite_session: AsyncSession,
                                 dbms_name: str):
    account_type_id = int()
    match dbms_name:
        case 'mssql':
            account_type_id = 1
        case 'postgresql':
            account_type_id = 2
        case 'mysql':
            account_type_id = 3
    has_account = await sqlite_session.execute(select(Account).join(User).filter(
        and_(User.user_telegram_id == user_data.user_telegram_id,
             Account.account_type_id == account_type_id)))
    has_account = has_account.first()
    if has_account:
        return True
    else:
        return False


async def create_new_account(*, user_id: int, user_data: CreateAccountScheme, sqlite_session: AsyncSession,
                             session: AsyncSession):
    dbms_name = session.get_bind().name
    alphabet = string.ascii_letters + string.digits
    user_password = ''.join(secrets.choice(alphabet) for _ in range(8))
    account_type_id = int()
    create_user_query = str()
    match dbms_name:
        case 'mssql':
            account_type_id = 1
            create_user_query = ("USE master;\n" +
                                 f"CREATE LOGIN {user_data.account_login} WITH PASSWORD='{user_password}';\n\n" +
                                 f"ALTER SERVER ROLE dbcreator ADD MEMBER {user_data.account_login};\n" +
                                 "USE master;\n" +
                                 f"GRANT CREATE ANY DATABASE TO {user_data.account_login};")
        case 'postgresql':
            account_type_id = 2
            create_user_query = f"CREATE USER {user_data.account_login} WITH PASSWORD '{user_password}' CREATEDB;"
        case 'mysql':
            account_type_id = 3
            create_user_query = f"CREATE USER '{user_data.account_login}'@localhost IDENTIFIED BY '{user_password}';"

    new_account = Account(account_user_id=user_id, account_login=user_data.account_login,
                          account_password=user_password,
                          account_type_id=account_type_id)
    sqlite_session.add(new_account)

    await session.execute(text(create_user_query))

    new_user = CreatedAccountScheme(account_login=user_data.account_login, account_password=user_password)
    return new_user


async def remind_password(user_data: CreateAccountScheme, sqlite_session: AsyncSession, dbms_name: str):
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
            Account.account_login == user_data.account_login).filter(Account.account_type_id == account_type_id))
    user_password = user_password.first()[0]
    return user_password


async def account_authentication(data: DatabaseInteractionScheme, sqlite_session: AsyncSession, dbms_name: str):
    account_type_id = int()
    match dbms_name:
        case 'mssql':
            account_type_id = 1
        case 'postgresql':
            account_type_id = 2
        case 'mysql':
            account_type_id = 3

    account = await sqlite_session.execute(
        select(Account).join(User).filter(
            and_(User.user_telegram_id == data.user_telegram_id,
                 Account.account_login == data.account_login,
                 Account.account_password == data.account_password,
                 Account.account_type_id == account_type_id)))
    account = account.first()
    if account:
        account = account[0]
    else:
        return False

    if account.account_login != data.account_login or account.account_password != data.account_password:
        return False
    else:
        return True
