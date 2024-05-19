import sqlalchemy
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.mariadb_database import get_mariadb_db_url, get_mariadb_session, get_autocommit_mariadb_session
from core.database.sqlite_database import get_sqlite_session
from core.schemas.database import DatabaseInteractionScheme
from core.schemas.account import CreatedAccountScheme, CreateAccountScheme
from middleware.account_middleware import get_user_id, check_account_existing, create_new_account, \
    remind_password, account_authentication, verify_connection_string
from middleware.database_middleware import check_databases_quantity, create_database, add_new_account_database, \
    delete_database
from middleware.user_middleware import check_user_existing

mariadb_router = APIRouter()

sqlite_db_dependency: AsyncSession = Depends(get_sqlite_session)

mariadb_db_dependency: AsyncSession = Depends(get_mariadb_session)
autocommit_mariadb_db_dependency: AsyncSession = Depends(get_autocommit_mariadb_session)


@mariadb_router.post("/user/create", response_model=CreatedAccountScheme, status_code=201)
async def mariadb_user_create(user_data: CreateAccountScheme, sqlite_session=sqlite_db_dependency,
                              mariadb_session=mariadb_db_dependency):
    user_exists = await check_user_existing(user_data=user_data, sqlite_session=sqlite_session)
    if not user_exists:
        raise HTTPException(400, detail="Unknown user")

    user_id = await get_user_id(user_data=user_data, sqlite_session=sqlite_session)

    account_exists = await check_account_existing(user_data=user_data, sqlite_session=sqlite_session,
                                                  dbms_name=mariadb_session.get_bind().name)

    if account_exists:
        raise HTTPException(400, detail="You already have an account")

    new_user = await create_new_account(user_id=user_id, user_data=user_data, sqlite_session=sqlite_session,
                                        session=mariadb_session)
    await sqlite_session.commit()
    await mariadb_session.commit()

    # async with aiohttp.ClientSession() as http_session:
    #     async with http_session.post('http://25.64.51.236:5132/createDbUser',
    #                                  json={'user_login': new_user.user_login, 'user_password': new_user.user_password,
    #                                        'telegram_id': user_data.user_telegram_id,
    #                                        'db_type': 'mariadb'}, headers={'content-type': 'application/json'}):
    #         pass

    return new_user


@mariadb_router.post('/user/remind-password')
async def mssql_remind_password(user_data: CreateAccountScheme, sqlite_session=sqlite_db_dependency):
    user_exists = await check_user_existing(user_data=user_data, sqlite_session=sqlite_session)
    if not user_exists:
        raise HTTPException(400, detail="Unknown user")

    account_exists = await check_account_existing(user_data=user_data, sqlite_session=sqlite_session,
                                                  dbms_name="mysql")
    if not account_exists:
        raise HTTPException(400, detail="You don't have an account in this DBMS")

    user_password = await remind_password(user_data=user_data, sqlite_session=sqlite_session, dbms_name='mysql')
    return user_password


@mariadb_router.post('/database/create', status_code=201)
async def mariadb_db_create(data: DatabaseInteractionScheme,
                            autocommit_mariadb_session=autocommit_mariadb_db_dependency,
                            sqlite_session=sqlite_db_dependency):
    user_exists = await check_user_existing(user_data=data, sqlite_session=sqlite_session)
    if not user_exists:
        raise HTTPException(400, detail="Unknown user")

    account_exists = await check_account_existing(user_data=data, sqlite_session=sqlite_session,
                                                  dbms_name=autocommit_mariadb_session.get_bind().name)

    if not account_exists:
        raise HTTPException(400, detail="You don't have an account in this DBMS")

    successful_authentication = await account_authentication(data=data, sqlite_session=sqlite_session,
                                                             dbms_name='mysql')
    if not successful_authentication:
        raise HTTPException(401, detail="Incorrect login or password")

    acceptable_quantity = await check_databases_quantity(data=data, sqlite_session=sqlite_session, dbms_name='mysql')
    if not acceptable_quantity:
        raise HTTPException(400, detail='You have the maximum number of databases')

    try:
        await create_database(data=data, session=autocommit_mariadb_session)
    except ProgrammingError:
        raise HTTPException(400, "The database exists")

    connection_string = get_mariadb_db_url(mariadb_db_user=data.account_login,
                                           mariadb_db_password=data.account_password,
                                           mariadb_db_name=data.database_name)
    await add_new_account_database(data=data, sqlite_session=sqlite_session, session=autocommit_mariadb_session)

    await sqlite_session.commit()
    return connection_string


@mariadb_router.delete('/database/delete')
async def mariadb_db_delete(data: DatabaseInteractionScheme,
                            autocommit_mariadb_session=autocommit_mariadb_db_dependency,
                            sqlite_session=sqlite_db_dependency):
    user_exists = await check_user_existing(user_data=data, sqlite_session=sqlite_session)
    if not user_exists:
        raise HTTPException(400, detail="Unknown user")

    account_exists = await check_account_existing(user_data=data, sqlite_session=sqlite_session,
                                                  dbms_name=autocommit_mariadb_session.get_bind().name)

    if not account_exists:
        raise HTTPException(400, detail="You don't have an account in this DBMS")

    successful_authentication = await account_authentication(data=data, sqlite_session=sqlite_session,
                                                             dbms_name='mysql')
    if not successful_authentication:
        raise HTTPException(401, detail="Incorrect login or password")

    try:
        await delete_database(data=data, sqlite_session=sqlite_session, session=autocommit_mariadb_session)
    except TypeError:
        raise HTTPException(404, "The database doesn't exist")
    await sqlite_session.commit()


@mariadb_router.post('/database/get-connection-string')
async def mariadb_db_get_conn_str(data: DatabaseInteractionScheme, sqlite_session=sqlite_db_dependency):
    user_exists = await check_user_existing(user_data=data, sqlite_session=sqlite_session)
    if not user_exists:
        raise HTTPException(400, detail="Unknown user")

    account_exists = await check_account_existing(user_data=data, sqlite_session=sqlite_session,
                                                  dbms_name='mysql')

    if not account_exists:
        raise HTTPException(400, detail="You don't have an account in this DBMS")

    successful_authentication = await account_authentication(data=data, sqlite_session=sqlite_session,
                                                             dbms_name='mysql')
    if not successful_authentication:
        raise HTTPException(401, detail="Incorrect login or password")

    connection_string = get_mariadb_db_url(mariadb_db_user=data.account_login,
                                           mariadb_db_password=data.account_password,
                                           mariadb_db_name=data.database_name)

    try:
        await verify_connection_string(connection_string)
        return connection_string
    except (sqlalchemy.exc.InterfaceError, sqlalchemy.exc.OperationalError):
        raise HTTPException(404, detail="Incorrect database name")
