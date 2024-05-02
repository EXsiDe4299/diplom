from pydantic import BaseModel


class CreateUserScheme(BaseModel):
    user_telegram_id: str
    user_login: str


class CreatedUserScheme(BaseModel):
    user_login: str
    user_password: str
