import secrets
import string

import pyodbc
import sqlalchemy
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from core.database.mssql_database import get_mssql_session, get_autocommit_mssql_session, get_mssql_db_url
from core.database.sqlite_database import get_sqlite_session
from core.schemas.database import DatabaseInteractionScheme
from core.schemas.user import CreatedUserScheme, CreateUserScheme

app = FastAPI()

sqlite_db_dependency: AsyncSession = Depends(get_sqlite_session)
mssql_db_dependency: AsyncSession = Depends(get_mssql_session)
autocommit_mssql_db_dependency: AsyncSession = Depends(get_autocommit_mssql_session)


# TODO: ограничить число баз данных для каждого пользователя до 3,
#  добавить обработку эндпоинтов,
#  информацию о пользователях и их БД хранить в sqllite.

# TODO: *сделать JWT-Auth

@app.post('/mssql/user/create', response_model=CreatedUserScheme)
async def mssql_user_create(user: CreateUserScheme, mssql_session=mssql_db_dependency,
                            sqlite_session=sqlite_db_dependency):
    alphabet = string.ascii_letters + string.digits
    user_password = ''.join(secrets.choice(alphabet) for _ in range(8))

    has_account = await sqlite_session.execute(
        text(f"SELECT * FROM accounts WHERE user_id='{user.user_telegram_id}' AND account_type_id=1"))

    if has_account.scalar_one_or_none():
        raise HTTPException(404, detail="You're already registered")

    await sqlite_session.execute(text("INSERT INTO users (user_telegram_id, user_login, user_password)" +
                                      f"VALUES ('{user.user_telegram_id}', '{user.user_login}', '{user_password}');"))

    await sqlite_session.execute(text("INSERT INTO accounts (user_id, account_type_id)" +
                                      f"VALUES ('{user.user_telegram_id}', 1);"))

    await mssql_session.execute(text("USE remote_db;\n" +
                                     f"CREATE LOGIN {user.user_login} WITH PASSWORD='{user_password}';\n\n" +
                                     f"ALTER SERVER ROLE dbcreator ADD MEMBER {user.user_login};\n" +
                                     "USE master;\n" +
                                     f"GRANT CREATE ANY DATABASE TO {user.user_login};"))

    await sqlite_session.commit()
    await mssql_session.commit()
    new_user = CreatedUserScheme(user_login=user.user_login, user_password=user_password)
    return new_user


@app.post('/mssql/database/create')
async def mssql_db_create(data: DatabaseInteractionScheme, autocommit_mssql_session=autocommit_mssql_db_dependency,
                          sqlite_session=sqlite_db_dependency):
    await autocommit_mssql_session.execute(text(f"CREATE DATABASE {data.database_name}"))
    await autocommit_mssql_session.execute(text(f"USE {data.database_name};\n" +
                                                f"CREATE USER {data.user_login} FOR LOGIN {data.user_login}"))
    autocommit_mssql_session.connection().close()
    connection_string = get_mssql_db_url(mssql_db_user=data.user_login,
                                         mssql_db_password=data.user_password,
                                         mssql_db_name=data.database_name)

    await sqlite_session.execute(text("INSERT INTO databases (database_name, database_type_id)" +
                                      f"VALUES ('{data.database_name}', 1)"))

    database_id = await sqlite_session.execute(
        text(f"SELECT database_id FROM databases WHERE database_name='{data.database_name}'"))

    await sqlite_session.execute(text("INSERT INTO accounts_databases (account_id, database_id)" +
                                      f"VALUES ('{data.user_telegram_id}', {database_id.scalar_one()})"))
    await sqlite_session.commit()

    return connection_string


@app.post('/mssql/database/get-connection-string')
async def mssql_db_get_conn_str(data: DatabaseInteractionScheme, sqlite_session=sqlite_db_dependency):
    connection_string = get_mssql_db_url(mssql_db_user=data.user_login,
                                         mssql_db_password=data.user_password,
                                         mssql_db_name=data.database_name)
    user = await sqlite_session.execute(text(f"SELECT * FROM users WHERE user_telegram_id='{data.user_telegram_id}'"))
    user_data = {}

    for row in user.fetchall():
        user_data['user_telegram_id'] = row[0]
        user_data['user_login'] = row[1]
        user_data['user_password'] = row[2]

    if user_data['user_login'] != data.user_login or user_data['user_password'] != data.user_password:
        raise HTTPException(401, detail="Incorrect login or password")

    engine = create_async_engine(connection_string)
    session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session() as s:
        try:
            await s.execute(text("SELECT @@VERSION"))
            return connection_string
        except pyodbc.InterfaceError:
            raise HTTPException(404, detail="The database doesn't exist")
        except sqlalchemy.exc.InterfaceError:
            raise HTTPException(403, detail="Access is denied")


@app.post("/postgresql/user/create", include_in_schema=False)
async def pg_user_create(user: CreateUserScheme, session=sqlite_db_dependency):  # не работает
    await session.execute(text(
        f"""CREATE USER {user.user_login} WITH PASSWORD '{user.user_password}' CREATEDB;"""
    ))
    await session.commit()


@app.post('/postgresql/database/create', include_in_schema=False)
async def pg_db_create():
    pass


@app.post('/postgresql/database/get-connection-string', include_in_schema=False)
async def pg_db_get_conn_str():
    pass


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
