from pydantic import BaseModel


class CreateAccountScheme(BaseModel):
    user_telegram_id: str
    account_login: str


class CreatedAccountScheme(BaseModel):
    account_login: str
    account_password: str


class EditAccountScheme(BaseModel):
    user_telegram_id: str
    account_login: str
    account_password: str
    new_account_login: str
    new_account_password: str
