import secrets
import string

import pyodbc
import sqlalchemy
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text, select, and_
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from core.database.mssql_database import get_mssql_session, get_autocommit_mssql_session, get_mssql_db_url
from core.database.postgres_database import get_postgres_session, get_postgres_db_url, get_autocommit_postgres_session
from core.database.sqlite_database import get_sqlite_session
from core.models.sqlite_models import Account, User, Database, AccountDatabase
from core.schemas.database import DatabaseInteractionScheme
from core.schemas.user import CreatedUserScheme, CreateUserScheme

app = FastAPI()

sqlite_db_dependency: AsyncSession = Depends(get_sqlite_session)
mssql_db_dependency: AsyncSession = Depends(get_mssql_session)
autocommit_mssql_db_dependency: AsyncSession = Depends(get_autocommit_mssql_session)
postgres_db_dependency: AsyncSession = Depends(get_postgres_session)
autocommit_postgres_db_dependency: AsyncSession = Depends(get_autocommit_postgres_session)


# TODO: ограничить число баз данных для каждого пользователя до 3

# TODO: *сделать JWT-Auth

@app.post('/mssql/user/create', response_model=CreatedUserScheme, status_code=201, include_in_schema=False)
async def mssql_user_create(user_data: CreateUserScheme, mssql_session=mssql_db_dependency,
                            sqlite_session=sqlite_db_dependency):
    alphabet = string.ascii_letters + string.digits
    user_password = ''.join(secrets.choice(alphabet) for _ in range(8))

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

    has_account = await sqlite_session.execute(select(Account).join(User).
                                               filter(User.user_telegram_id == user_data.user_telegram_id).
                                               filter(Account.account_type_id == 1))
    has_account = has_account.first()

    if has_account:
        raise HTTPException(400, detail="You're already registered")

    new_account = Account(account_user_id=user_id, account_login=user_data.user_login, account_password=user_password,
                          account_type_id=1)
    sqlite_session.add(new_account)

    await mssql_session.execute(text("USE remote_db;\n" +
                                     f"CREATE LOGIN {user_data.user_login} WITH PASSWORD='{user_password}';\n\n" +
                                     f"ALTER SERVER ROLE dbcreator ADD MEMBER {user_data.user_login};\n" +
                                     "USE master;\n" +
                                     f"GRANT CREATE ANY DATABASE TO {user_data.user_login};"))

    await sqlite_session.commit()
    await mssql_session.commit()
    new_user = CreatedUserScheme(user_login=user_data.user_login, user_password=user_password)
    return new_user


@app.post('/mssql/database/create', status_code=201, include_in_schema=False)
async def mssql_db_create(data: DatabaseInteractionScheme, autocommit_mssql_session=autocommit_mssql_db_dependency,
                          sqlite_session=sqlite_db_dependency):
    try:
        await autocommit_mssql_session.execute(text(f"CREATE DATABASE {data.database_name}"))
        await autocommit_mssql_session.execute(text(f"USE {data.database_name};\n" +
                                                    f"CREATE USER {data.user_login} FOR LOGIN {data.user_login}"))
    except ProgrammingError:
        raise HTTPException(400, "The database exists")

    connection_string = get_mssql_db_url(mssql_db_user=data.user_login,
                                         mssql_db_password=data.user_password,
                                         mssql_db_name=data.database_name)
    new_database = Database(database_name=data.database_name, database_type_id=1)
    sqlite_session.add(new_database)
    await sqlite_session.flush()
    database_id = new_database.database_id

    account = await sqlite_session.execute(select(Account.account_id).
                                           join(User).filter(and_(User.user_telegram_id == data.user_telegram_id,
                                                                  Account.account_type_id == 1)))
    account = account.first()
    account_id = account[0]

    new_account_database = AccountDatabase(database_id=database_id, account_id=account_id)
    sqlite_session.add(new_account_database)

    await sqlite_session.commit()

    return connection_string


@app.get('/mssql/database/get-connection-string', include_in_schema=False)
async def mssql_db_get_conn_str(data: DatabaseInteractionScheme, sqlite_session=sqlite_db_dependency):
    connection_string = get_mssql_db_url(mssql_db_user=data.user_login,
                                         mssql_db_password=data.user_password,
                                         mssql_db_name=data.database_name)
    user = await sqlite_session.execute(
        select(Account).join(User).filter(and_(User.user_telegram_id == data.user_telegram_id,
                                               Account.account_type_id == 1)))
    user = user.first()[0]

    if user.account_login != data.user_login or user.account_password != data.user_password:
        raise HTTPException(401, detail="Incorrect login or password")

    test_engine = create_async_engine(connection_string)
    test_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with test_session() as session:
        try:
            await session.execute(text("SELECT @@VERSION"))
            return connection_string
        except pyodbc.InterfaceError:
            raise HTTPException(404, detail="The database doesn't exist")
        except sqlalchemy.exc.InterfaceError:
            raise HTTPException(403, detail="Access is denied")


@app.post("/postgresql/user/create", response_model=CreatedUserScheme, status_code=201)
async def pg_user_create(user_data: CreateUserScheme, sqlite_session=sqlite_db_dependency,
                         postgres_session=postgres_db_dependency):
    alphabet = string.ascii_letters + string.digits
    user_password = ''.join(secrets.choice(alphabet) for _ in range(8))

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

    has_account = await sqlite_session.execute(select(Account).join(User).
                                               filter(User.user_telegram_id == user_data.user_telegram_id).
                                               filter(Account.account_type_id == 2))
    has_account = has_account.first()

    if has_account:
        raise HTTPException(400, detail="You're already registered")

    new_account = Account(account_user_id=user_id, account_login=user_data.user_login, account_password=user_password,
                          account_type_id=2)
    sqlite_session.add(new_account)

    await postgres_session.execute(text(
        f"""CREATE USER {user_data.user_login} WITH PASSWORD '{user_password}' CREATEDB;"""
    ))
    await sqlite_session.commit()
    await postgres_session.commit()
    new_user = CreatedUserScheme(user_login=user_data.user_login, user_password=user_password)
    return new_user


@app.post('/postgresql/database/create', status_code=201)
async def pg_db_create(data: DatabaseInteractionScheme, autocommit_postgres_session=autocommit_postgres_db_dependency,
                       sqlite_session=sqlite_db_dependency):
    try:
        await autocommit_postgres_session.execute(
            text(f"CREATE DATABASE {data.database_name} OWNER {data.user_login};"))
    except ProgrammingError:
        raise HTTPException(400, "The database exists")

    connection_string = get_postgres_db_url(postgres_db_user=data.user_login,
                                            postgres_db_password=data.user_password,
                                            postgres_db_name=data.database_name)
    new_database = Database(database_name=data.database_name, database_type_id=2)
    sqlite_session.add(new_database)
    await sqlite_session.flush()
    database_id = new_database.database_id

    account = await sqlite_session.execute(select(Account.account_id).
                                           join(User).filter(and_(User.user_telegram_id == data.user_telegram_id,
                                                                  Account.account_type_id == 2)))
    account = account.first()
    account_id = account[0]

    new_account_database = AccountDatabase(database_id=database_id, account_id=account_id)
    sqlite_session.add(new_account_database)

    await sqlite_session.commit()

    return connection_string


@app.post('/postgresql/database/get-connection-string')
async def pg_db_get_conn_str(data: DatabaseInteractionScheme, sqlite_session=sqlite_db_dependency):
    connection_string = get_postgres_db_url(postgres_db_user=data.user_login,
                                            postgres_db_password=data.user_password,
                                            postgres_db_name=data.database_name)
    user = await sqlite_session.execute(
        select(Account).join(User).filter(and_(User.user_telegram_id == data.user_telegram_id,
                                               Account.account_type_id == 2)))
    user = user.first()[0]

    if user.account_login != data.user_login or user.account_password != data.user_password:
        raise HTTPException(401, detail="Incorrect login or password")

    test_engine = create_async_engine(connection_string)
    test_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
    async with test_session() as session:
        try:
            await session.execute(text("SELECT version()"))
            return connection_string
        except pyodbc.InterfaceError:
            raise HTTPException(404, detail="The database doesn't exist")
        except sqlalchemy.exc.InterfaceError:
            raise HTTPException(403, detail="Access is denied")


@app.post("/mariadb/user/create", include_in_schema=False)
async def mariadb_user_create():
    pass


@app.post('/mariadb/database/create', include_in_schema=False)
async def mariadb_db_create():
    pass


@app.post('/mariadb/database/get-connection-string', include_in_schema=False)
async def mariadb_db_get_conn_str():
    pass


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
