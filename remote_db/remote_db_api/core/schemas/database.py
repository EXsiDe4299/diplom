from pydantic import BaseModel


class DatabaseInteractionScheme(BaseModel):
    database_name: str
    user_telegram_id: str
    user_login: str
    user_password: str
