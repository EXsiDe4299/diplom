from aiogram import types, Router, F
from aiogram.filters import CommandStart
from aiohttp import ClientSession

from filters.chat_types import ChatTypeFilter
from keyboards.reply import create_reply_buttons

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))


@user_private_router.message(CommandStart())
@user_private_router.message(F.text == '📚 Главное меню')
async def start_cmd(message: types.Message):
    buttons = ['👤 Аккаунты', '🗄️ Базы данных']
    if message.text == '/start':
        async with ClientSession() as client_session:
            async with client_session.post(url='http://127.0.0.1:8000/registration',
                                           json={'user_telegram_id': str(message.from_user.id)}):
                pass
    await message.answer(
        'гав 🐶\n\nЭто главное меню 📚\n\nЗдесь ты можешь посмотреть аккаунты и базы данных (базы пока что не сделал, не обессудь) в трех СУБД: MSSQL, PostgreSQL и MariaDB',
        reply_markup=create_reply_buttons(*buttons))


@user_private_router.message(F.text == '👤 Аккаунты')
async def accounts(message: types.Message):
    dbms_dict = {1: '🌐 MSSQL', 2: '🐘 PostgreSQL', 3: '🦭 MariaDB'}
    answer_text = 'гав 🐶\n\nАккаунты:'
    buttons = ['📚 Главное меню']
    async with ClientSession() as client_session:
        async with client_session.post(url='http://127.0.0.1:8000/get-accounts',
                                       json={'user_telegram_id': str(message.from_user.id)}) as response:
            response = await response.json()
            if len(response) < 3:
                buttons.insert(0, '🔐 Создать')
            if len(response) > 0:
                for i in response:
                    answer_text += f'\n{dbms_dict[i["account_type_id"]]}\nЛогин: {i["account_login"]}\nПароль: <span class="tg-spoiler">{i["account_password"]}</span>\n'
                buttons.insert(1, '🔄 Редактировать')

    # buttons = ['🔐 Создать', '🔄 Редактировать', '📚 Главное меню']
    await message.answer(answer_text, reply_markup=create_reply_buttons(*buttons))
