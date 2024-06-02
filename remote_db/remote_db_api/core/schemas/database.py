from pydantic import BaseModel


class DatabaseInteractionScheme(BaseModel):
    database_name: str
    user_telegram_id: str
    account_login: str
    account_password: str
