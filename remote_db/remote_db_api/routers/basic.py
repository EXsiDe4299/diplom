from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.sqlite_database import get_sqlite_session
from core.schemas.user import CreateUserScheme
from middleware.user_middleware import register_user

basic_router = APIRouter()

sqlite_db_dependency: AsyncSession = Depends(get_sqlite_session)


@basic_router.post('/registration')
async def registration(user_data: CreateUserScheme, sqlite_session=sqlite_db_dependency):
    await register_user(user_data=user_data, sqlite_session=sqlite_session)
    await sqlite_session.commit()
