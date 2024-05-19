from pydantic import BaseModel


class CreateUserScheme(BaseModel):
    user_telegram_id: str
