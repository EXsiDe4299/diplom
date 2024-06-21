import uvicorn
from fastapi import FastAPI

from routers.account import account_router
from routers.basic import basic_router
from routers.database import database_router

app = FastAPI()

app.include_router(account_router, prefix='/account', tags=['account'])
app.include_router(database_router, prefix='/database', tags=['database'])
app.include_router(basic_router, tags=['basic'])

if __name__ == "__main__":
    uvicorn.run(app, host="25.47.119.26", port=8000)
