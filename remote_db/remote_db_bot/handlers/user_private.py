from aiogram import types, Router
from aiogram.filters import CommandStart
from aiohttp import ClientSession

from filters.chat_types import ChatTypeFilter
from keyboards.inline import create_inline_buttons
from keyboards.reply import create_reply_buttons

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))


@user_private_router.message(lambda message: message.text in ['/start', '📚 Главное меню'])
async def start_cmd(message: types.Message):
    buttons = ['👤 Аккаунты', '🗄️ Базы данных']
    if message.text == '/start':
        async with ClientSession() as client_session:
            async with client_session.post(url='http://127.0.0.1:8000/registration',
                                           json={'user_telegram_id': str(message.from_user.id)}):
                pass
    await message.answer(
        'гав 🐶\n\nЭто главное меню 📚\n\nЗдесь ты можешь (пока что не можешь) посмотреть аккаунты и базы данных в трех СУБД: MSSQL, PostgreSQL и MariaDB',
        reply_markup=create_reply_buttons(*buttons))
