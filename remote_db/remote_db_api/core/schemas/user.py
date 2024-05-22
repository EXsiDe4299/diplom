from pydantic import BaseModel


class UserScheme(BaseModel):
    user_telegram_id: str
