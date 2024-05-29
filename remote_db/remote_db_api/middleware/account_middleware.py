import secrets
import string

from sqlalchemy import text, select, and_, update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import joinedload

from core.models.sqlite_models import User, Account, AccountTypes
from core.schemas.account import CreateAccountScheme, CreatedAccountScheme, EditAccountScheme
from core.schemas.database import DatabaseInteractionScheme
from core.schemas.user import UserScheme
from middleware.i_will_call_it_later import db_stuff


async def get_user_id(user_data: CreateAccountScheme | EditAccountScheme, sqlite_session: AsyncSession):
    user = await sqlite_session.execute(select(User).filter(User.user_telegram_id == user_data.user_telegram_id))
    user = user.first()[0]
    # user = user.scalars().first()
    user_id = user.user_id
    return user_id


async def get_user_accounts(user_data: UserScheme, sqlite_session: AsyncSession):
    accounts = await sqlite_session.execute(
        select(Account).join(User).filter(User.user_telegram_id == user_data.user_telegram_id))
    # accounts = await sqlite_session.execute(select(Account).join(Account.users).filter(User.user_telegram_id==user_data.user_telegram_id).options(joinedload(Account.account_types)))
    accounts = accounts.scalars().all()
    return accounts


async def check_account_existing(user_data: CreateAccountScheme | DatabaseInteractionScheme | EditAccountScheme,
                                 sqlite_session: AsyncSession,
                                 dbms_name: str):
    account_type_id = db_stuff[dbms_name]['account_type_id']
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
    account_type_id = db_stuff[dbms_name]['account_type_id']
    create_user_query = db_stuff[dbms_name]['create_user_query'](account_login=user_data.account_login,
                                                                 user_password=user_password)

    new_account = Account(account_user_id=user_id, account_login=user_data.account_login,
                          account_password=user_password,
                          account_type_id=account_type_id)
    sqlite_session.add(new_account)

    await session.execute(text(create_user_query))

    new_user = CreatedAccountScheme(account_login=user_data.account_login, account_password=user_password)
    return new_user


# async def remind_password(user_data: CreateAccountScheme, sqlite_session: AsyncSession, dbms_name: str):
#     account_type_id = int()
#     match dbms_name:
#         case 'mssql':
#             account_type_id = 1
#         case 'postgresql':
#             account_type_id = 2
#         case 'mysql':
#             account_type_id = 3
#     user_password = await sqlite_session.execute(
#         select(Account.account_password).join(User).filter(User.user_telegram_id == user_data.user_telegram_id).filter(
#             Account.account_login == user_data.account_login).filter(Account.account_type_id == account_type_id))
#     user_password = user_password.first()[0]
#     return user_password


async def account_authentication(data: DatabaseInteractionScheme | EditAccountScheme, sqlite_session: AsyncSession,
                                 dbms_name: str):
    account_type_id = db_stuff[dbms_name]['account_type_id']

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


async def change_account(user_id: int, user_data: EditAccountScheme, sqlite_session: AsyncSession,
                         session: AsyncSession):
    dbms_name = session.get_bind().name
    account_type_id: int = db_stuff[dbms_name]['account_type_id']
    if user_data.account_login != user_data.new_account_login:
        await session.execute(text(db_stuff[dbms_name]['edit_login_query'](user_login=user_data.account_login,
                                                                           new_account_login=user_data.new_account_login)))
    if user_data.account_password != user_data.new_account_password:
        await session.execute(
            text(db_stuff[dbms_name]['edit_password_query'](new_account_login=user_data.new_account_login,
                                                            new_account_password=user_data.new_account_password)))
    await sqlite_session.execute(
        update(Account).filter(
            and_(Account.account_user_id == user_id, Account.account_type_id == account_type_id)).values(
            account_login=user_data.new_account_login, account_password=user_data.new_account_password))

    updated_user = CreatedAccountScheme(account_login=user_data.new_account_login,
                                        account_password=user_data.new_account_password)
    return updated_user
