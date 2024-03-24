from aiogram.filters import CommandStart
from aiogram import types, Router, F

from filters.chat_types import ChatTypeFilter
from keyboards.inline import create_inline_buttons
from middleware.api_requests import get_groups, get_group

import pandas as pd

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))


@user_private_router.message(CommandStart())
async def start_cmd(message: types.Message):
    group_buttons = dict()
    groups = await get_groups()
    for group in groups:
        group_buttons[group['groupName']] = f'get_group_attendance_{group['groupName']}'

    await message.answer(text='Выберите группу:',
                         reply_markup=create_inline_buttons(buttons=group_buttons, sizes=(4,)))


@user_private_router.callback_query(F.data == 'back_to_groups')
async def start_cmd_callback(callback: types.CallbackQuery):
    group_buttons = dict()
    groups = await get_groups()
    for group in groups:
        group_buttons[group['groupName']] = f'get_group_attendance_{group['groupName']}'
    await callback.message.answer(text='Выберите группу:',
                                  reply_markup=create_inline_buttons(buttons=group_buttons, sizes=(4,)))


@user_private_router.callback_query(F.data.startswith('get_group_attendance'))
async def get_group_attendance(callback: types.CallbackQuery):
    group_name = callback.data.split('_')[-1]
    group_data = await get_group(group_name)
    pd.set_option('display.max_columns', None)
    df = pd.json_normalize(group_data)
    attendance_data = df['StudNumber'].value_counts().to_dict()
    response = str()
    back_button = {'Назад': 'back_to_groups'}
    for i, j in attendance_data.items():
        response += f'{i}: {j}\n'
    await callback.message.answer(text=response, reply_markup=create_inline_buttons(buttons=back_button, sizes=(1,)))
