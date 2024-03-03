from aiogram.filters import CommandStart
from aiogram import types, Router, F

from filters.chat_types import ChatTypeFilter
from keyboards.inline import create_inline_buttons
from middleware.api_requests import get_groups

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    groups = await get_groups()
    buttons = dict()
    for group in groups:
        # TODO: придумать че сделать с айдишниками для коллбэков
        buttons[group['groupName']] = group['groupName']

    await message.answer(text='Выберите группу:',
                         reply_markup=create_inline_buttons(buttons=buttons, sizes=(4,)))
