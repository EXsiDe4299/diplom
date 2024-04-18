from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from schemas import UserScheme

app = FastAPI()

db_dependency: AsyncSession = Depends(get_session)


@app.post('/test')
async def test(user: UserScheme, session=db_dependency):
    await session.execute(text(
        f"USE remote_db;CREATE LOGIN {user.user_login} WITH PASSWORD='{user.user_password}'; CREATE USER {user.user_login} FOR LOGIN {user.user_login}"))
    await session.commit()
