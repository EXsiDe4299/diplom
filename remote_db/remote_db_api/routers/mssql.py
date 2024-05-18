import sqlalchemy
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.mssql_database import get_mssql_session, get_autocommit_mssql_session, get_mssql_db_url
from core.database.sqlite_database import get_sqlite_session
from core.schemas.database import DatabaseInteractionScheme
from core.schemas.account import CreatedAccountScheme, CreateAccountScheme
from middleware.middleware import verify_connection_string, create_or_get_user_id, \
    check_account_existing, create_new_account, create_database, add_new_account_database, user_authentication, \
    check_databases_quantity, delete_database, remind_password

mssql_router = APIRouter()

sqlite_db_dependency: AsyncSession = Depends(get_sqlite_session)

mssql_db_dependency: AsyncSession = Depends(get_mssql_session)
autocommit_mssql_db_dependency: AsyncSession = Depends(get_autocommit_mssql_session)


@mssql_router.post('/user/create', response_model=CreatedAccountScheme, status_code=201)
async def mssql_user_create(user_data: CreateAccountScheme, mssql_session=mssql_db_dependency,
                            sqlite_session=sqlite_db_dependency):
    user_id = await create_or_get_user_id(user_data=user_data, sqlite_session=sqlite_session)

    account_exists = await check_account_existing(user_data=user_data, sqlite_session=sqlite_session,
                                                  dbms_name=mssql_session.get_bind().name)

    if account_exists:
        raise HTTPException(400, detail="You're already registered")

    new_user = await create_new_account(user_id=user_id, user_data=user_data, sqlite_session=sqlite_session,
                                        session=mssql_session)
    await sqlite_session.commit()
    await mssql_session.commit()

    # async with aiohttp.ClientSession() as http_session:
    #     async with http_session.post('http://25.64.51.236:5132/createDbUser',
    #                                  json={'user_login': new_user.user_login, 'user_password': new_user.user_password,
    #                                        'telegram_id': user_data.user_telegram_id,
    #                                        'db_type': 'mssql'}, headers={'content-type': 'application/json'}):
    #         pass

    return new_user


@mssql_router.post('/user/remind-password')
async def mssql_remind_password(user_data: CreateAccountScheme, sqlite_session=sqlite_db_dependency):
    account_exists = await check_account_existing(user_data=user_data, sqlite_session=sqlite_session,
                                                  dbms_name="mssql")
    if not account_exists:
        raise HTTPException(400, detail="Unregistered")

    user_password = await remind_password(user_data=user_data, sqlite_session=sqlite_session, dbms_name='mssql')
    return user_password


@mssql_router.post('/database/create', status_code=201)
async def mssql_db_create(data: DatabaseInteractionScheme, autocommit_mssql_session=autocommit_mssql_db_dependency,
                          sqlite_session=sqlite_db_dependency):
    account_exists = await check_account_existing(user_data=data, sqlite_session=sqlite_session,
                                                  dbms_name=autocommit_mssql_session.get_bind().name)

    if not account_exists:
        raise HTTPException(400, detail="Unregistered")

    successful_authentication = await user_authentication(data=data, sqlite_session=sqlite_session, dbms_name='mssql')
    if not successful_authentication:
        raise HTTPException(401, detail="Incorrect login or password")

    acceptable_quantity = await check_databases_quantity(data=data, sqlite_session=sqlite_session, dbms_name='mssql')
    if not acceptable_quantity:
        raise HTTPException(400, detail='You have the maximum number of databases')

    try:
        await create_database(data=data, session=autocommit_mssql_session)
    except ProgrammingError:
        raise HTTPException(400, "The database exists")

    connection_string = get_mssql_db_url(mssql_db_user=data.account_login,
                                         mssql_db_password=data.account_password,
                                         mssql_db_name=data.database_name)
    await add_new_account_database(data=data, sqlite_session=sqlite_session, session=autocommit_mssql_session)

    await sqlite_session.commit()

    return connection_string


@mssql_router.delete('/database/delete')
async def mssql_db_delete(data: DatabaseInteractionScheme, autocommit_mssql_session=autocommit_mssql_db_dependency,
                          sqlite_session=sqlite_db_dependency):
    account_exists = await check_account_existing(user_data=data, sqlite_session=sqlite_session,
                                                  dbms_name=autocommit_mssql_session.get_bind().name)

    if not account_exists:
        raise HTTPException(400, detail="Unregistered")

    successful_authentication = await user_authentication(data=data, sqlite_session=sqlite_session, dbms_name='mssql')
    if not successful_authentication:
        raise HTTPException(401, detail="Incorrect login or password")

    try:
        await delete_database(data=data, sqlite_session=sqlite_session, session=autocommit_mssql_session)
    except TypeError:
        raise HTTPException(404, "The database doesn't exist")
    await sqlite_session.commit()


@mssql_router.post('/database/get-connection-string')
async def mssql_db_get_conn_str(data: DatabaseInteractionScheme, sqlite_session=sqlite_db_dependency):
    account_exists = await check_account_existing(user_data=data, sqlite_session=sqlite_session,
                                                  dbms_name='mssql')

    if not account_exists:
        raise HTTPException(400, detail="Unregistered")

    successful_authentication = await user_authentication(data=data, sqlite_session=sqlite_session, dbms_name='mssql')
    if not successful_authentication:
        raise HTTPException(401, detail="Incorrect login or password")

    connection_string = get_mssql_db_url(mssql_db_user=data.account_login,
                                         mssql_db_password=data.account_password,
                                         mssql_db_name=data.database_name)

    try:
        await verify_connection_string(connection_string)
        return connection_string
    except sqlalchemy.exc.InterfaceError:
        raise HTTPException(404, detail="Incorrect database name")
