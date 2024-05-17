import aiohttp
import sqlalchemy
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.mariadb_database import get_mariadb_db_url, get_mariadb_session, get_autocommit_mariadb_session
from core.database.mssql_database import get_mssql_session, get_autocommit_mssql_session, get_mssql_db_url
from core.database.postgres_database import get_postgres_session, get_postgres_db_url, get_autocommit_postgres_session
from core.database.sqlite_database import get_sqlite_session
from core.schemas.database import DatabaseInteractionScheme
from core.schemas.user import CreatedUserScheme, CreateUserScheme
from middleware.middleware import verify_connection_string, create_or_get_user_id, \
    check_account_existing, create_new_account, create_database, add_new_account_database, user_authentication, \
    check_databases_quantity, delete_database

app = FastAPI()

sqlite_db_dependency: AsyncSession = Depends(get_sqlite_session)

mssql_db_dependency: AsyncSession = Depends(get_mssql_session)
autocommit_mssql_db_dependency: AsyncSession = Depends(get_autocommit_mssql_session)

postgres_db_dependency: AsyncSession = Depends(get_postgres_session)
autocommit_postgres_db_dependency: AsyncSession = Depends(get_autocommit_postgres_session)

mariadb_db_dependency: AsyncSession = Depends(get_mariadb_session)
autocommit_mariadb_db_dependency: AsyncSession = Depends(get_autocommit_mariadb_session)


# TODO: оптимизировать sql-запросы. Добавить эндпоинты для напоминания пароля

# TODO: *сделать нормальный нейминг

# TODO: *сделать JWT-Auth


@app.post('/mssql/user/create', response_model=CreatedUserScheme, status_code=201)
async def mssql_user_create(user_data: CreateUserScheme, mssql_session=mssql_db_dependency,
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


@app.post('/mssql/database/create', status_code=201)
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

    connection_string = get_mssql_db_url(mssql_db_user=data.user_login,
                                         mssql_db_password=data.user_password,
                                         mssql_db_name=data.database_name)
    await add_new_account_database(data=data, sqlite_session=sqlite_session, session=autocommit_mssql_session)

    await sqlite_session.commit()

    return connection_string


@app.delete('/mssql/database/delete')
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
    except ProgrammingError:
        raise HTTPException(400, "The database doesn't exist")
    await sqlite_session.commit()


@app.post('/mssql/database/get-connection-string')
async def mssql_db_get_conn_str(data: DatabaseInteractionScheme, sqlite_session=sqlite_db_dependency):
    account_exists = await check_account_existing(user_data=data, sqlite_session=sqlite_session,
                                                  dbms_name='mssql')

    if not account_exists:
        raise HTTPException(400, detail="Unregistered")

    successful_authentication = await user_authentication(data=data, sqlite_session=sqlite_session, dbms_name='mssql')
    if not successful_authentication:
        raise HTTPException(401, detail="Incorrect login or password")

    connection_string = get_mssql_db_url(mssql_db_user=data.user_login,
                                         mssql_db_password=data.user_password,
                                         mssql_db_name=data.database_name)

    try:
        await verify_connection_string(connection_string)
        return connection_string
    except sqlalchemy.exc.InterfaceError:
        raise HTTPException(404, detail="Incorrect database name")


@app.post("/postgresql/user/create", response_model=CreatedUserScheme, status_code=201)
async def pg_user_create(user_data: CreateUserScheme, sqlite_session=sqlite_db_dependency,
                         postgres_session=postgres_db_dependency):
    user_id = await create_or_get_user_id(user_data=user_data, sqlite_session=sqlite_session)

    account_exists = await check_account_existing(user_data=user_data, sqlite_session=sqlite_session,
                                                  dbms_name=postgres_session.get_bind().name)

    if account_exists:
        raise HTTPException(400, detail="You're already registered")

    new_user = await create_new_account(user_id=user_id, user_data=user_data, sqlite_session=sqlite_session,
                                        session=postgres_session)
    await sqlite_session.commit()
    await postgres_session.commit()

    # async with aiohttp.ClientSession() as http_session:
    #     async with http_session.post('http://25.64.51.236:5132/createDbUser',
    #                                  json={'user_login': new_user.user_login, 'user_password': new_user.user_password,
    #                                        'telegram_id': user_data.user_telegram_id,
    #                                        'db_type': 'postgresql'}, headers={'content-type': 'application/json'}):
    #         pass

    return new_user


@app.post('/postgresql/database/create', status_code=201)
async def pg_db_create(data: DatabaseInteractionScheme, autocommit_postgres_session=autocommit_postgres_db_dependency,
                       sqlite_session=sqlite_db_dependency):
    account_exists = await check_account_existing(user_data=data, sqlite_session=sqlite_session,
                                                  dbms_name=autocommit_postgres_session.get_bind().name)

    if not account_exists:
        raise HTTPException(400, detail="Unregistered")

    successful_authentication = await user_authentication(data=data, sqlite_session=sqlite_session,
                                                          dbms_name='postgresql')
    if not successful_authentication:
        raise HTTPException(401, detail="Incorrect login or password")

    acceptable_quantity = await check_databases_quantity(data=data, sqlite_session=sqlite_session,
                                                         dbms_name='postgresql')
    if not acceptable_quantity:
        raise HTTPException(400, detail='You have the maximum number of databases')

    try:
        await create_database(data=data, session=autocommit_postgres_session)

    except ProgrammingError:
        raise HTTPException(400, "The database exists")

    connection_string = get_postgres_db_url(postgres_db_user=data.user_login,
                                            postgres_db_password=data.user_password,
                                            postgres_db_name=data.database_name)
    await add_new_account_database(data=data, sqlite_session=sqlite_session, session=autocommit_postgres_session)

    await sqlite_session.commit()
    return connection_string


@app.delete('/postgresql/database/delete')
async def pg_db_delete(data: DatabaseInteractionScheme, autocommit_postgres_session=autocommit_postgres_db_dependency,
                       sqlite_session=sqlite_db_dependency):
    account_exists = await check_account_existing(user_data=data, sqlite_session=sqlite_session,
                                                  dbms_name=autocommit_postgres_session.get_bind().name)

    if not account_exists:
        raise HTTPException(400, detail="Unregistered")

    successful_authentication = await user_authentication(data=data, sqlite_session=sqlite_session, dbms_name='postgresql')
    if not successful_authentication:
        raise HTTPException(401, detail="Incorrect login or password")

    try:
        await delete_database(data=data, sqlite_session=sqlite_session, session=autocommit_postgres_session)
    except ProgrammingError:
        raise HTTPException(400, "The database doesn't exist")
    await sqlite_session.commit()


@app.post('/postgresql/database/get-connection-string')
async def pg_db_get_conn_str(data: DatabaseInteractionScheme, sqlite_session=sqlite_db_dependency):
    account_exists = await check_account_existing(user_data=data, sqlite_session=sqlite_session,
                                                  dbms_name='postgresql')

    if not account_exists:
        raise HTTPException(400, detail="Unregistered")

    successful_authentication = await user_authentication(data=data, sqlite_session=sqlite_session,
                                                          dbms_name='postgresql')
    if not successful_authentication:
        raise HTTPException(401, detail="Incorrect login or password")

    connection_string = get_postgres_db_url(postgres_db_user=data.user_login,
                                            postgres_db_password=data.user_password,
                                            postgres_db_name=data.database_name)

    try:
        await verify_connection_string(connection_string)
        return connection_string
    except sqlalchemy.exc.InterfaceError:
        raise HTTPException(404, detail="Incorrect database name")


@app.post("/mariadb/user/create", response_model=CreatedUserScheme, status_code=201)
async def mariadb_user_create(user_data: CreateUserScheme, sqlite_session=sqlite_db_dependency,
                              mariadb_session=mariadb_db_dependency):
    user_id = await create_or_get_user_id(user_data=user_data, sqlite_session=sqlite_session)

    account_exists = await check_account_existing(user_data=user_data, sqlite_session=sqlite_session,
                                                  dbms_name=mariadb_session.get_bind().name)

    if account_exists:
        raise HTTPException(400, detail="You're already registered")

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


@app.post('/mariadb/database/create', status_code=201)
async def mariadb_db_create(data: DatabaseInteractionScheme,
                            autocommit_mariadb_session=autocommit_mariadb_db_dependency,
                            sqlite_session=sqlite_db_dependency):
    account_exists = await check_account_existing(user_data=data, sqlite_session=sqlite_session,
                                                  dbms_name=autocommit_mariadb_session.get_bind().name)

    if not account_exists:
        raise HTTPException(400, detail="Unregistered")

    successful_authentication = await user_authentication(data=data, sqlite_session=sqlite_session, dbms_name='mysql')
    if not successful_authentication:
        raise HTTPException(401, detail="Incorrect login or password")

    acceptable_quantity = await check_databases_quantity(data=data, sqlite_session=sqlite_session, dbms_name='mysql')
    if not acceptable_quantity:
        raise HTTPException(400, detail='You have the maximum number of databases')

    try:
        await create_database(data=data, session=autocommit_mariadb_session)
    except ProgrammingError:
        raise HTTPException(400, "The database exists")

    connection_string = get_mariadb_db_url(mariadb_db_user=data.user_login,
                                           mariadb_db_password=data.user_password,
                                           mariadb_db_name=data.database_name)
    await add_new_account_database(data=data, sqlite_session=sqlite_session, session=autocommit_mariadb_session)

    await sqlite_session.commit()
    return connection_string


@app.delete('/mariadb/database/delete')
async def mariadb_db_delete(data: DatabaseInteractionScheme, autocommit_mariadb_session=autocommit_mariadb_db_dependency,
                            sqlite_session=sqlite_db_dependency):
    account_exists = await check_account_existing(user_data=data, sqlite_session=sqlite_session,
                                                  dbms_name=autocommit_mariadb_session.get_bind().name)

    if not account_exists:
        raise HTTPException(400, detail="Unregistered")

    successful_authentication = await user_authentication(data=data, sqlite_session=sqlite_session, dbms_name='mysql')
    if not successful_authentication:
        raise HTTPException(401, detail="Incorrect login or password")

    try:
        await delete_database(data=data, sqlite_session=sqlite_session, session=autocommit_mariadb_session)
    except ProgrammingError:
        raise HTTPException(400, "The database doesn't exist")
    await sqlite_session.commit()


@app.post('/mariadb/database/get-connection-string')
async def mariadb_db_get_conn_str(data: DatabaseInteractionScheme, sqlite_session=sqlite_db_dependency):
    account_exists = await check_account_existing(user_data=data, sqlite_session=sqlite_session,
                                                  dbms_name='mysql')

    if not account_exists:
        raise HTTPException(400, detail="Unregistered")

    successful_authentication = await user_authentication(data=data, sqlite_session=sqlite_session, dbms_name='mysql')
    if not successful_authentication:
        raise HTTPException(401, detail="Incorrect login or password")

    connection_string = get_mariadb_db_url(mariadb_db_user=data.user_login,
                                           mariadb_db_password=data.user_password,
                                           mariadb_db_name=data.database_name)

    try:
        await verify_connection_string(connection_string)
        return connection_string
    except sqlalchemy.exc.InterfaceError:
        raise HTTPException(404, detail="Incorrect database name")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
