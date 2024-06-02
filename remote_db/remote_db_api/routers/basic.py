from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.database_helper import get_connection_string
from core.database.sqlite_database import get_sqlite_session
from core.schemas.user import UserScheme
from middleware.account_middleware import get_user_accounts
from middleware.database_middleware import get_user_databases
from middleware.db_toolkit import db_toolkit_data
from middleware.user_middleware import register_user

basic_router = APIRouter()

sqlite_db_dependency: AsyncSession = Depends(get_sqlite_session)


@basic_router.post('/registration', status_code=204)
async def registration(user_data: UserScheme, sqlite_session=sqlite_db_dependency):
    await register_user(user_data=user_data, sqlite_session=sqlite_session)
    await sqlite_session.commit()


@basic_router.post('/get-accounts')
async def get_accounts(user_data: UserScheme, sqlite_session=sqlite_db_dependency):
    accounts = await get_user_accounts(user_data=user_data, sqlite_session=sqlite_session)
    return accounts


@basic_router.post('/get-accounts-databases')
async def get_accounts_databases(data: UserScheme, sqlite_session=sqlite_db_dependency):
    user_databases = await get_user_databases(user_data=data, sqlite_session=sqlite_session)
    dbms_name = str()
    for user_database in user_databases:
        for key, value in db_toolkit_data.items():
            if value['database_type_id'] == user_database['database_type_id']:
                dbms_name = key
                break
        conn_str = get_connection_string(dbms_name=dbms_name,
                                         user=user_database['account_login'],
                                         password=user_database['account_password'],
                                         db_name=user_database['database_name'])
        user_database['connection_string'] = conn_str
    return user_databases
