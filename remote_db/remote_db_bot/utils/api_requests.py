from aiohttp import ClientSession

from common.api_urls import registration_url, get_accounts_url


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


async def create_account_request(url, user_telegram_id, account_login):
    async with ClientSession() as client_session:
        async with client_session.post(url=url,
                                       json={'user_telegram_id': str(user_telegram_id),
                                             'account_login': account_login}) as response:
            response = await response.json()
            return response
