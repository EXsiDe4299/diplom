from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.sqlite_models import User
from core.schemas.account import CreateAccountScheme, EditAccountScheme
from core.schemas.database import DatabaseInteractionScheme
from core.schemas.user import UserScheme


async def register_user(user_data: UserScheme, sqlite_session: AsyncSession):
    user = await sqlite_session.execute(select(User).filter(User.user_telegram_id == user_data.user_telegram_id))
    user = user.first()
    if not user:
        new_user = User(user_telegram_id=user_data.user_telegram_id)
        sqlite_session.add(new_user)


async def check_user_existing(
        user_data: UserScheme | CreateAccountScheme | DatabaseInteractionScheme | EditAccountScheme,
        sqlite_session: AsyncSession):
    user = await sqlite_session.execute(select(User).filter(User.user_telegram_id == user_data.user_telegram_id))
    user = user.first()
    if user:
        return True
    else:
        return False
