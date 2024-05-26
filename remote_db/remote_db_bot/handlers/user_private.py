from aiogram import types, Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from common.api_urls import account_create_url
from common.something import user_dbms_dict, main_menu_buttons, api_dbms_dict
from common.texts import main_menu_text, choose_dbms_text, invent_login_text, choose_dbms_text2
from filters.chat_types import ChatTypeFilter
from keyboards.reply import create_reply_buttons
from utils.api_requests import register_user_request, get_accounts_request, create_account_request
from utils.middleware import format_accounts_response, remove_excess_dbms_buttons, get_dbms_id_by_name, get_dbms_buttons

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))


class AddAccountStates(StatesGroup):
    check_accounts = State()
    choice_dbms = State()
    input_login = State()


class EditAccountStates(StatesGroup):
    choice_dbms = State()
    input_new_login = State()
    input_new_password = State()


@user_private_router.message(StateFilter('*'), CommandStart())
@user_private_router.message(StateFilter('*'), F.text == '📚 Главное меню')
async def start_cmd(message: types.Message, state: FSMContext):
    if message.text == '/start':
        await register_user_request(message.from_user.id)
    await state.clear()
    await message.answer(main_menu_text, reply_markup=create_reply_buttons(*main_menu_buttons))


@user_private_router.message(StateFilter(None), F.text == '👤 Аккаунты')
async def accounts(message: types.Message, state: FSMContext):
    response = await get_accounts_request(user_telegram_id=message.from_user.id)
    await state.update_data(existing_accounts=response)
    answer_text, buttons = await format_accounts_response(response=response)
    await state.set_state(AddAccountStates.check_accounts)
    await message.answer(answer_text, reply_markup=create_reply_buttons(*buttons))


@user_private_router.message(StateFilter(AddAccountStates.check_accounts), F.text == '🔐 Создать')
async def choose_dbms(message: types.Message, state: FSMContext):
    data = await state.get_data()
    existing_accounts = data['existing_accounts']
    buttons = await remove_excess_dbms_buttons(existing_accounts)
    await message.answer(choose_dbms_text,
                         reply_markup=create_reply_buttons(*buttons))
    await state.set_state(AddAccountStates.choice_dbms)


@user_private_router.message(StateFilter(AddAccountStates.choice_dbms),
                             lambda message: message.text in user_dbms_dict.values())
async def invent_login(message: types.Message, state: FSMContext):
    dbms_id = await get_dbms_id_by_name(message.text)
    await state.update_data(dbms_id=dbms_id)
    await message.answer(invent_login_text, reply_markup=create_reply_buttons('📚 Главное меню'))
    await state.set_state(AddAccountStates.input_login)


@user_private_router.message(StateFilter(AddAccountStates.input_login))
async def create_account(message: types.Message, state: FSMContext):
    data = await state.get_data()
    dbms_id = data['dbms_id']
    response = await create_account_request(url=account_create_url, user_telegram_id=message.from_user.id,
                                            account_login=message.text,
                                            dbms_name=api_dbms_dict[dbms_id])
    await message.answer(f'гав 🐶\n\nЛогин: {response['account_login']}\nПароль: {response['account_password']}',
                         reply_markup=create_reply_buttons('📚 Главное меню'))
    await state.clear()

# @user_private_router.message(StateFilter(AddAccountStates.check_accounts), F.text == '🔄 Редактировать')
# async def qwer(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     existing_accounts = data['existing_accounts']
#     buttons = await get_dbms_buttons(existing_accounts)
#     await message.answer(choose_dbms_text2,
#                          reply_markup=create_reply_buttons(*buttons))
#     await state.set_state(EditAccountStates.choice_dbms)
#
#
# @user_private_router.message(StateFilter(EditAccountStates.choice_dbms),
#                              lambda message: message.text in user_dbms_dict.values())
# async def asdf(message: types.Message, state: FSMContext):
#     dbms_id = await get_dbms_id_by_name(message.text)
#     await state.update_data(dbms_id=dbms_id)
#     await message.answer(invent_login_text, reply_markup=create_reply_buttons('📚 Главное меню'))
#     await state.set_state(EditAccountStates.input_new_login)
#
#
# @user_private_router.message(StateFilter(EditAccountStates.input_new_login))
# async def zxcv(message: types.Message, state: FSMContext):
#     pass
