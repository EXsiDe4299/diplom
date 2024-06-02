import uvicorn
from fastapi import FastAPI

from routers.account import account_router
from routers.basic import basic_router
from routers.database import database_router

# TODO: оптимизировать sql-запросы, убрать повторы кода проверок в эндпоинтах

# TODO: *сделать нормальный нейминг

# TODO: *сделать JWT-Auth

app = FastAPI()

app.include_router(account_router, prefix='/account', tags=['account'])
app.include_router(database_router, prefix='/database', tags=['database'])
app.include_router(basic_router, tags=['basic'])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
