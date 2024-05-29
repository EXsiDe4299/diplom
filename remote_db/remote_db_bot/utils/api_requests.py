from aiohttp import ClientSession

from common.api_urls import registration_url, get_accounts_url, account_create_url, account_edit_url


async def register_user_request(user_telegram_id):
    async with ClientSession() as client_session:
        async with client_session.post(url=registration_url,
                                       json={'user_telegram_id': str(user_telegram_id)}):
            pass


async def get_accounts_request(user_telegram_id):
    async with ClientSession() as client_session:
        async with client_session.post(url=get_accounts_url,
                                       json={'user_telegram_id': str(user_telegram_id)}) as response:
            response = await response.json()
            return response


async def create_account_request(user_telegram_id, account_login, dbms_name):
    async with ClientSession() as client_session:
        async with client_session.post(url=account_create_url,
                                       json={'user_data': {'user_telegram_id': str(user_telegram_id),
                                                           'account_login': account_login},
                                             'dbms_name': dbms_name}) as response:
            response = await response.json()
            return response


async def edit_account_request(user_telegram_id, account_login, account_password, new_account_login,
                               new_account_password, dbms_name):
    async with ClientSession() as client_session:
        async with client_session.post(url=account_edit_url,
                                       json={"account_data": {
                                           "user_telegram_id": user_telegram_id,
                                           "account_login": account_login,
                                           "account_password": account_password,
                                           "new_account_login": new_account_login,
                                           "new_account_password": new_account_password
                                       },
                                           "dbms_name": dbms_name}) as response:
            response = await response.json()
            return response
