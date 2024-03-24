import aiohttp
from os import getenv
from dotenv import load_dotenv

load_dotenv()


async def authorize():
    login = getenv('API_LOGIN')
    password = getenv('API_PASSWORD')
    async with aiohttp.ClientSession() as session:
        # async with session.post('http://kgpkapi.somee.com/user/authorize',
        async with session.post('http://localhost:5132/user/authorize',
                                json={"login": login, "password": password}) as current_user_token:
            current_user_token = await current_user_token.json()
            return current_user_token


async def get_groups():
    current_user = await authorize()
    async with aiohttp.ClientSession() as session:
        # async with session.get('http://kgpkapi.somee.com/group/all', headers={
        async with session.get('http://localhost:5132/group/all', headers={
            'Authorization': f"Bearer {current_user['Item1']}"
        }) as all_groups:
            all_groups = await all_groups.json()
            return all_groups


async def get_group(group_name):
    current_user = await authorize()
    async with aiohttp.ClientSession() as session:
        # async with session.get(f'http://kgpkapi.somee.com/skippedClass/group?groupName={group_name}', headers={
        async with session.get(f'http://localhost:5132/skippedClass/group?groupName={group_name}', headers={
            'Authorization': f"Bearer {current_user['Item1']}"
        }) as group_data:
            group_data = await group_data.json()
            return group_data
