import uvicorn
from fastapi import FastAPI

from routers.basic import basic_router
from routers.mariadb import mariadb_router
from routers.mssql import mssql_router
from routers.postgresql import postgresql_router

# TODO: оптимизировать sql-запросы

# TODO: *сделать нормальный нейминг

# TODO: *сделать JWT-Auth

app = FastAPI()

app.include_router(mssql_router, prefix='/mssql', tags=['mssql'])
app.include_router(postgresql_router, prefix='/postgresql', tags=['postgresql'])
app.include_router(mariadb_router, prefix='/mariadb', tags=['mariadb'])
app.include_router(basic_router, tags=['basic'])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
