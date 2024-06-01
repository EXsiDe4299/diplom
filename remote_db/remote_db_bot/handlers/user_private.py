from aiogram import types, Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from common.api_urls import account_create_url
from common.something import user_dbms_dict, main_menu_buttons, api_dbms_dict
from common.texts import main_menu_text, choose_dbms_text, invent_login_text, choose_dbms_text2, invent_password_text, \
    choose_dbms_text3, invent_db_name_text, choose_dbms_text4, input_db_name_text
from filters.chat_types import ChatTypeFilter
from keyboards.reply import create_reply_buttons
from utils.api_requests import register_user_request, get_accounts_request, create_account_request, \
    edit_account_request, get_accounts_databases_request, create_database_request
from utils.middleware import format_accounts_response, remove_excess_dbms_buttons, get_dbms_id_by_name, \
    get_dbms_buttons, format_databases_response

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


class AddDatabaseStates(StatesGroup):
    check_databases = State()
    choice_dbms = State()
    input_db_name = State()


class EditDatabaseStates(StatesGroup):
    choice_dbms = State()
    input_db_name = State()
    input_new_db_name = State()


@user_private_router.message(StateFilter('*'), CommandStart())
@user_private_router.message(StateFilter('*'), F.text == '📚 Главное меню')
async def main_menu(message: types.Message, state: FSMContext):
    await register_user_request(message.from_user.id)
    await state.clear()
    await message.answer(main_menu_text, reply_markup=create_reply_buttons(*main_menu_buttons))


@user_private_router.message(StateFilter(None), F.text == '👤 Аккаунты')
async def accounts(message: types.Message, state: FSMContext):
    response = await get_accounts_request(user_telegram_id=message.from_user.id)
    await state.update_data(existing_accounts=response)
    answer_text, buttons = format_accounts_response(response=response)
    await state.set_state(AddAccountStates.check_accounts)
    await message.answer(answer_text, reply_markup=create_reply_buttons(*buttons))


@user_private_router.message(StateFilter(AddAccountStates.check_accounts), F.text == '🔐 Создать')
async def create_account_btn_click(message: types.Message, state: FSMContext):
    data = await state.get_data()
    existing_accounts = data['existing_accounts']
    buttons = remove_excess_dbms_buttons(existing_accounts)
    await message.answer(choose_dbms_text,
                         reply_markup=create_reply_buttons(*buttons, '📚 Главное меню'))
    await state.set_state(AddAccountStates.choice_dbms)


@user_private_router.message(StateFilter(AddAccountStates.choice_dbms),
                             lambda message: message.text in user_dbms_dict.values())
async def invent_login(message: types.Message, state: FSMContext):
    dbms_id = get_dbms_id_by_name(message.text)
    await state.update_data(dbms_id=dbms_id)
    await message.answer(invent_login_text, reply_markup=create_reply_buttons('📚 Главное меню'))
    await state.set_state(AddAccountStates.input_login)


@user_private_router.message(StateFilter(AddAccountStates.input_login))
async def create_account(message: types.Message, state: FSMContext):
    data = await state.get_data()
    dbms_id = data['dbms_id']
    response = await create_account_request(user_telegram_id=message.from_user.id,
                                            account_login=message.text,
                                            dbms_name=api_dbms_dict[dbms_id])
    await message.answer(f'гав 🐶\n\nЛогин: {response['account_login']}\nПароль: {response['account_password']}',
                         reply_markup=create_reply_buttons('📚 Главное меню'))


@user_private_router.message(StateFilter(AddAccountStates.check_accounts), F.text == '🔄 Редактировать')
async def edit_account_btn_click(message: types.Message, state: FSMContext):
    data = await state.get_data()
    existing_accounts = data['existing_accounts']
    buttons = get_dbms_buttons(existing_accounts)
    await message.answer(choose_dbms_text2,
                         reply_markup=create_reply_buttons(*buttons))
    await state.set_state(EditAccountStates.choice_dbms)


@user_private_router.message(StateFilter(EditAccountStates.choice_dbms),
                             lambda message: message.text in user_dbms_dict.values())
async def edit_login(message: types.Message, state: FSMContext):
    dbms_id = get_dbms_id_by_name(message.text)
    await state.update_data(dbms_id=dbms_id)
    await message.answer(invent_login_text, reply_markup=create_reply_buttons('📚 Главное меню', '🚫 Оставить текущий'))
    await state.set_state(EditAccountStates.input_new_login)


@user_private_router.message(StateFilter(EditAccountStates.input_new_login))
async def edit_password(message: types.Message, state: FSMContext):
    data = await state.get_data()
    dbms_id = data['dbms_id']
    existing_accounts = data['existing_accounts']
    old_login = next(
        (account['account_login'] for account in existing_accounts if account['account_type_id'] == dbms_id))

    await state.update_data(old_login=old_login)
    if message.text != '🚫 Оставить текущий':
        await state.update_data(new_login=message.text)
    else:
        await state.update_data(new_login=old_login)

    await message.answer(invent_password_text,
                         reply_markup=create_reply_buttons('📚 Главное меню', '🚫 Оставить текущий'))
    await state.set_state(EditAccountStates.input_new_password)


@user_private_router.message(StateFilter(EditAccountStates.input_new_password))
async def edit_account(message: types.Message, state: FSMContext):
    data = await state.get_data()
    dbms_id = data['dbms_id']
    existing_accounts = data['existing_accounts']
    old_login = data['old_login']
    new_login = data['new_login']

    dbms_name = api_dbms_dict[dbms_id]
    old_password = next(
        (account['account_password'] for account in existing_accounts if account['account_type_id'] == dbms_id))

    if message.text != '🚫 Оставить текущий':
        new_password = message.text
    else:
        new_password = old_password

    response = await edit_account_request(user_telegram_id=str(message.from_user.id), account_login=old_login,
                                          account_password=old_password,
                                          new_account_login=new_login, new_account_password=new_password,
                                          dbms_name=dbms_name)
    await message.answer(f'гав 🐶\n\nЛогин: {response["account_login"]}\nПароль: {response["account_password"]}',
                         reply_markup=create_reply_buttons("📚 Главное меню"))


@user_private_router.message(StateFilter(None), F.text == '🗄️ Базы данных')
async def databases(message: types.Message, state: FSMContext):
    accounts_databases = await get_accounts_databases_request(user_telegram_id=str(message.from_user.id))
    await state.update_data(accounts_databases=accounts_databases)
    answer_text, buttons = format_databases_response(accounts_databases=accounts_databases)
    await message.answer(answer_text, reply_markup=create_reply_buttons(*buttons))
    await state.set_state(AddDatabaseStates.check_databases)


@user_private_router.message(StateFilter(AddDatabaseStates.check_databases), F.text == '🔐 Создать')
async def create_db_btn_click(message: types.Message, state: FSMContext):
    data = await state.get_data()
    accounts_databases = data['accounts_databases']
    user_accounts = await get_accounts_request(user_telegram_id=message.from_user.id)
    buttons = [user_dbms_dict[i['account_type_id']] for i in user_accounts]
    databases_quantity = {1: 0, 2: 0, 3: 0}
    for account_database in accounts_databases:
        databases_quantity[account_database['database_type_id']] += 1
        if databases_quantity[account_database['database_type_id']] >= 3:
            buttons.remove(user_dbms_dict[account_database['database_type_id']])

    await message.answer(choose_dbms_text3, reply_markup=create_reply_buttons(*buttons, "📚 Главное меню"))
    await state.set_state(AddDatabaseStates.choice_dbms)


@user_private_router.message(StateFilter(AddDatabaseStates.choice_dbms),
                             lambda message: message.text in user_dbms_dict.values())
async def input_db_name(message: types.Message, state: FSMContext):
    dbms_id = get_dbms_id_by_name(message.text)
    await state.update_data(dbms_id=dbms_id)
    await message.answer(invent_db_name_text, reply_markup=create_reply_buttons('📚 Главное меню'))
    await state.set_state(AddDatabaseStates.input_db_name)


@user_private_router.message(StateFilter(AddDatabaseStates.input_db_name))
async def create_database(message: types.Message, state: FSMContext):
    data = await state.get_data()
    dbms_id = data['dbms_id']
    dbms_name = api_dbms_dict[dbms_id]
    database_name = message.text
    accounts_response = await get_accounts_request(user_telegram_id=message.from_user.id)
    account_login = str()
    account_password = str()
    for account in accounts_response:
        if account['account_type_id'] == dbms_id:
            account_login = account['account_login']
            account_password = account['account_password']
    if account_login != '' and account_password != '':
        connection_string = await create_database_request(database_name=database_name,
                                                          user_telegram_id=message.from_user.id,
                                                          account_login=account_login,
                                                          account_password=account_password,
                                                          dbms_name=dbms_name)
        await message.answer(
            f'гав 🐶\n\nБаза данных успешно создана.\nНазвание базы данных: {database_name}\nСтрока подключения: <code>{connection_string}</code>',
            reply_markup=create_reply_buttons('📚 Главное меню'))
    else:
        await message.answer('Сначала создай аккаунт', reply_markup=create_reply_buttons('📚 Главное меню'))


@user_private_router.message(StateFilter(AddDatabaseStates.check_databases), F.text == '🔄 Редактировать')
async def edit_db_btn_click(message: types.Message, state: FSMContext):
    data = await state.get_data()
    accounts_databases = data['accounts_databases']
    buttons = []
    for account_database in accounts_databases:
        if user_dbms_dict[account_database['database_type_id']] not in buttons:
            buttons.append(user_dbms_dict[account_database['database_type_id']])
    # buttons = {user_dbms_dict[i['database_type_id']] for i in accounts_databases}
    await message.answer(choose_dbms_text4, reply_markup=create_reply_buttons(*buttons, "📚 Главное меню"))
    await state.set_state(EditDatabaseStates.choice_dbms)


@user_private_router.message(StateFilter(EditDatabaseStates.choice_dbms),
                             lambda message: message.text in user_dbms_dict.values())
async def input_existing_db_name(message: types.Message, state: FSMContext):
    dbms_id = get_dbms_id_by_name(message.text)
    await state.update_data(dbms_id=dbms_id)
    await message.answer(input_db_name_text, reply_markup=create_reply_buttons('📚 Главное меню'))
    await state.set_state(EditDatabaseStates.input_db_name)


@user_private_router.message(StateFilter(EditDatabaseStates.input_db_name))
async def input_new_db_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    dbms_id = data['dbms_id']
    accounts_databases = data['accounts_databases']
    old_db_name = next(
        (account_database['database_name'] for account_database in accounts_databases if
         account_database['database_name'] == message.text and account_database['database_type_id'] == dbms_id), None)

    if old_db_name:
        await state.update_data(old_db_name=old_db_name)

        await message.answer(invent_db_name_text,
                             reply_markup=create_reply_buttons('📚 Главное меню'))
        await state.set_state(EditDatabaseStates.input_new_db_name)
    else:
        await message.answer('Такой базы данных не существует',
                             reply_markup=create_reply_buttons('📚 Главное меню'))


@user_private_router.message(StateFilter(EditDatabaseStates.input_new_db_name))
async def edit_database(message: types.Message, state: FSMContext):
    await message.answer('база данных изменена (не изменена)')


@user_private_router.message(StateFilter(AddDatabaseStates.check_databases), F.text == '❌ Удалить')
async def asdf(message: types.Message, state: FSMContext):
    await message.answer('Ты в редактировании', reply_markup=create_reply_buttons("📚 Главное меню"))
    await state.set_state(EditDatabaseStates.choice_dbms)
