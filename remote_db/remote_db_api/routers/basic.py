from fastapi import Depends, APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.sqlite_database import get_sqlite_session
from core.schemas.user import UserScheme
from middleware.account_middleware import get_user_accounts
from middleware.user_middleware import register_user

basic_router = APIRouter()

sqlite_db_dependency: AsyncSession = Depends(get_sqlite_session)


@basic_router.post('/registration')
async def registration(user_data: UserScheme, sqlite_session=sqlite_db_dependency):
    await register_user(user_data=user_data, sqlite_session=sqlite_session)
    await sqlite_session.commit()


@basic_router.post('/get-accounts')
async def get_accounts(user_data: UserScheme, sqlite_session=sqlite_db_dependency):
    accounts = await get_user_accounts(user_data=user_data, sqlite_session=sqlite_session)
    return accounts

# @basic_router.post('/backdoor')
# async def backdoor(query: str, sqlite_session=sqlite_db_dependency):
#     data = await sqlite_session.execute(text(query))
#     data = data.scalars().all()
#     return response
