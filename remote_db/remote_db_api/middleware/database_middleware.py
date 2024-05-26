from sqlalchemy import text, select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from core.models.sqlite_models import User, Account, Database, AccountDatabase
from core.schemas.database import DatabaseInteractionScheme
from middleware.i_will_call_it_later import db_stuff


async def create_database(data: DatabaseInteractionScheme, session: AsyncSession):
    dbms_name = session.get_bind().name
    for query in db_stuff[dbms_name]['create_database_query'](database_name=data.database_name,
                                                              account_login=data.account_login):
        await session.execute(text(query))


async def verify_connection_string(connection_string):
    test_engine = create_async_engine(connection_string)
    test_engine_name = test_engine.name
    test_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with test_session() as session:
        try:
            await session.execute(text(db_stuff[test_engine_name]['select_version_query']))
        finally:
            await session.close()
            await test_engine.dispose()


async def add_new_account_database(data: DatabaseInteractionScheme, sqlite_session: AsyncSession,
                                   session: AsyncSession):
    dbms_name = session.get_bind().name
    account_type_id = db_stuff[dbms_name]['account_type_id']
    database_type_id = db_stuff[dbms_name]['database_type_id']

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
    account_type_id = db_stuff[dbms_name]['account_type_id']
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
    database_type_id = db_stuff[dbms_name]['database_type_id']

    database = await sqlite_session.execute(select(Database).filter(
        and_(Database.database_name == data.database_name, Database.database_type_id == database_type_id)))
    database = database.first()[0]
    database_id: int = database.database_id
    database_name = database.database_name
    await session.execute(text(db_stuff[dbms_name]['delete_database_query'](database_name)))
    await sqlite_session.execute(delete(AccountDatabase).filter(AccountDatabase.database_id == database_id))
    await sqlite_session.execute(delete(Database).filter(Database.database_id == database_id))
