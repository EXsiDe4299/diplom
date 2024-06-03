from aiohttp import ClientSession

from common.api_urls import registration_url, get_accounts_url, account_create_url, account_edit_url, \
    get_accounts_databases_url, create_database_url, delete_database_url, createdbuser_url


async def register_user_request(user_telegram_id):
    async with ClientSession() as client_session:
        async with client_session.post(url=registration_url,
                                       json={'user_telegram_id': str(user_telegram_id)}):
            pass


async def get_accounts_request(user_telegram_id):
    async with ClientSession() as client_session:
        async with client_session.post(url=get_accounts_url,
                                       json={'user_telegram_id': str(user_telegram_id)}) as response:
            status_code = response.status
            response = await response.json()
            return response, status_code


async def create_account_request(user_telegram_id, account_login, dbms_name):
    async with ClientSession() as client_session:
        async with client_session.post(url=account_create_url,
                                       json={'user_data': {'user_telegram_id': str(user_telegram_id),
                                                           'account_login': account_login},
                                             'dbms_name': dbms_name}) as response:
            status_code = response.status
            response = await response.json()
            return response, status_code


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
            status_code = response.status
            response = await response.json()
            return response, status_code


async def get_accounts_databases_request(user_telegram_id):
    async with ClientSession() as client_session:
        async with client_session.post(url=get_accounts_databases_url,
                                       json={"user_telegram_id": user_telegram_id}) as response:
            status_code = response.status
            response = await response.json()
            return response, status_code


async def create_database_request(database_name, user_telegram_id, account_login, account_password, dbms_name):
    async with ClientSession() as client_session:
        async with client_session.post(url=create_database_url,
                                       json={
                                           "data": {
                                               "database_name": database_name,
                                               "user_telegram_id": str(user_telegram_id),
                                               "account_login": account_login,
                                               "account_password": account_password
                                           },
                                           "dbms_name": dbms_name
                                       }) as response:
            status_code = response.status
            response = await response.json()
            return response, status_code


async def delete_database_request(database_name, user_telegram_id, account_login, account_password, dbms_name):
    async with ClientSession() as client_session:
        async with client_session.delete(url=delete_database_url,
                                         json={
                                             "data": {
                                                 "database_name": database_name,
                                                 "user_telegram_id": str(user_telegram_id),
                                                 "account_login": account_login,
                                                 "account_password": account_password
                                             },
                                             "dbms_name": dbms_name
                                         }) as response:
            status_code = response.status
            response = await response.json()
            return response, status_code


async def createdbuser_request(user_login, user_password, telegram_id, db_type):
    async with ClientSession() as client_session:
        async with client_session.post(url=createdbuser_url, json={
            'user_login': user_login,
            'user_password': user_password,
            'telegram_id': str(telegram_id),
            'db_type': db_type
        }):
            pass
