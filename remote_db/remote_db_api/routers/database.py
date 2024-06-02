import asyncpg
import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import ProgrammingError

from core.database.database_helper import get_connection_string
from core.database.sqlite_database import get_sqlite_session
from core.database.utils import get_session, get_autocommit_session
from core.schemas.database import DatabaseInteractionScheme
from middleware.account_middleware import check_account_existing, account_authentication
from middleware.database_middleware import check_databases_quantity, create_database, add_new_account_database, \
    delete_database, verify_connection_string
from middleware.user_middleware import check_user_existing

database_router = APIRouter()
sqlite_db_dependency = Depends(get_sqlite_session)
db_dependency = Depends(get_session)
autocommit_db_dependency = Depends(get_autocommit_session)


@database_router.post('/create', status_code=201)
async def db_create(data: DatabaseInteractionScheme,
                    autocommit_session=autocommit_db_dependency,
                    sqlite_session=sqlite_db_dependency):
    if not autocommit_session:
        raise HTTPException(400, detail='Incorrect dbms name')

    user_exists = await check_user_existing(user_data=data, sqlite_session=sqlite_session)
    if not user_exists:
        raise HTTPException(400, detail="Unknown user")

    account_exists = await check_account_existing(user_data=data, sqlite_session=sqlite_session,
                                                  dbms_name=autocommit_session.get_bind().name)

    if not account_exists:
        raise HTTPException(400, detail="You don't have an account in this DBMS")

    successful_authentication = await account_authentication(data=data, sqlite_session=sqlite_session,
                                                             dbms_name=autocommit_session.get_bind().name)
    if not successful_authentication:
        raise HTTPException(401, detail="Incorrect login or password")

    acceptable_quantity = await check_databases_quantity(data=data, sqlite_session=sqlite_session,
                                                         dbms_name=autocommit_session.get_bind().name)
    if not acceptable_quantity:
        raise HTTPException(400, detail='You have the maximum number of databases')

    try:
        await create_database(data=data, session=autocommit_session)
    except (ProgrammingError, sqlalchemy.exc.OperationalError):
        raise HTTPException(400, "The database exists")

    connection_string = get_connection_string(dbms_name=autocommit_session.get_bind().name, user=data.account_login,
                                              password=data.account_password,
                                              db_name=data.database_name)
    await add_new_account_database(data=data, sqlite_session=sqlite_session, session=autocommit_session)

    await sqlite_session.commit()
    return connection_string


@database_router.delete('/delete')
async def db_delete(data: DatabaseInteractionScheme,
                    autocommit_session=autocommit_db_dependency,
                    sqlite_session=sqlite_db_dependency):
    if not autocommit_session:
        raise HTTPException(400, detail='Incorrect dbms name')

    user_exists = await check_user_existing(user_data=data, sqlite_session=sqlite_session)
    if not user_exists:
        raise HTTPException(400, detail="Unknown user")

    account_exists = await check_account_existing(user_data=data, sqlite_session=sqlite_session,
                                                  dbms_name=autocommit_session.get_bind().name)

    if not account_exists:
        raise HTTPException(400, detail="You don't have an account in this DBMS")

    successful_authentication = await account_authentication(data=data, sqlite_session=sqlite_session,
                                                             dbms_name=autocommit_session.get_bind().name)
    if not successful_authentication:
        raise HTTPException(401, detail="Incorrect login or password")

    try:
        await delete_database(data=data, sqlite_session=sqlite_session, session=autocommit_session)
    except TypeError:
        raise HTTPException(404, "The database doesn't exist")
    await sqlite_session.commit()


@database_router.post('/get-connection-string')
async def db_get_conn_str(data: DatabaseInteractionScheme, sqlite_session=sqlite_db_dependency,
                          session=db_dependency):
    if not session:
        raise HTTPException(400, detail='Incorrect dbms name')
    user_exists = await check_user_existing(user_data=data, sqlite_session=sqlite_session)
    if not user_exists:
        raise HTTPException(400, detail="Unknown user")

    account_exists = await check_account_existing(user_data=data, sqlite_session=sqlite_session,
                                                  dbms_name=session.get_bind().name)

    if not account_exists:
        raise HTTPException(400, detail="You don't have an account in this DBMS")

    successful_authentication = await account_authentication(data=data, sqlite_session=sqlite_session,
                                                             dbms_name=session.get_bind().name)
    if not successful_authentication:
        raise HTTPException(401, detail="Incorrect login or password")

    connection_string = get_connection_string(dbms_name=session.get_bind().name, user=data.account_login,
                                              password=data.account_password,
                                              db_name=data.database_name)

    try:
        await verify_connection_string(connection_string)
        return connection_string
    except (sqlalchemy.exc.InterfaceError, asyncpg.exceptions.ConnectionDoesNotExistError,
            sqlalchemy.exc.OperationalError):
        raise HTTPException(404, detail="Incorrect database name")
