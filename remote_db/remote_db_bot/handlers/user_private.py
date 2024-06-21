from aiogram import types, Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from common.buttons import main_menu_button, no_button, accounts_button, databases_button, create_button, edit_button, \
    leave_current_button, delete_button, yes_button
from common.something import user_dbms_dict, api_dbms_dict
from common.texts import main_menu_text, choose_dbms_text, invent_login_text, choose_dbms_text2, \
    invent_new_password_text, \
    choose_dbms_text3, invent_db_name_text, choose_dbms_text4, input_db_name_text, confirmation_of_deletion_text, \
    invent_new_login_text, account_created_text, account_edited_text, database_created_text, database_deleted_text, \
    incorrect_dbms_name_text, register_first_text, already_have_account_text, incorrect_input_text, \
    incorrect_login_or_pass_text, too_many_databases_text, db_already_exists_text, someone_else_db_text, \
    db_doesnt_exists_text
from filters.chat_types import ChatTypeFilter
from keyboards.reply import create_reply_buttons
from utils.api_requests import register_user_request, get_accounts_request, create_account_request, \
    edit_account_request, get_accounts_databases_request, create_database_request, delete_database_request, \
    createdbuser_request, remote_edit_account_request, remote_create_database_request
from utils.middleware import format_accounts_response, remove_excess_dbms_buttons, get_dbms_id_by_name, \
    get_dbms_buttons, format_databases_response, checking_text_correctness, checking_password_correctness

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


class DeleteDatabaseStates(StatesGroup):
    choice_dbms = State()
    input_db_name = State()
    confirmation_of_deletion = State()


@user_private_router.message(StateFilter(DeleteDatabaseStates.confirmation_of_deletion), F.text == no_button)
@user_private_router.message(StateFilter('*'), CommandStart())
@user_private_router.message(StateFilter('*'), F.text == main_menu_button)
async def main_menu(message: types.Message, state: FSMContext):
    await register_user_request(message.from_user.id)
    await state.clear()
    await message.answer(main_menu_text, reply_markup=create_reply_buttons(accounts_button, databases_button))


@user_private_router.message(StateFilter(None), F.text == accounts_button)
async def accounts(message: types.Message, state: FSMContext):
    existing_accounts, status_code = await get_accounts_request(user_telegram_id=message.from_user.id)
    await state.update_data(existing_accounts=existing_accounts)
    answer_text, buttons = format_accounts_response(existing_accounts=existing_accounts)
    await state.set_state(AddAccountStates.check_accounts)
    await message.answer(answer_text, reply_markup=create_reply_buttons(*buttons))


@user_private_router.message(StateFilter(AddAccountStates.check_accounts), F.text == create_button)
async def create_account_btn_click(message: types.Message, state: FSMContext):
    data = await state.get_data()
    existing_accounts = data['existing_accounts']
    buttons = remove_excess_dbms_buttons(existing_accounts)
    await message.answer(choose_dbms_text,
                         reply_markup=create_reply_buttons(*buttons, main_menu_button))
    await state.set_state(AddAccountStates.choice_dbms)


@user_private_router.message(StateFilter(AddAccountStates.choice_dbms),
                             lambda message: message.text in user_dbms_dict.values())
async def invent_login(message: types.Message, state: FSMContext):
    dbms_id = get_dbms_id_by_name(message.text)
    await state.update_data(dbms_id=dbms_id)
    await message.answer(invent_login_text, reply_markup=create_reply_buttons(main_menu_button))
    await state.set_state(AddAccountStates.input_login)


@user_private_router.message(StateFilter(AddAccountStates.input_login))
async def create_account(message: types.Message, state: FSMContext):
    if checking_text_correctness(message.text):
        data = await state.get_data()
        dbms_id = data['dbms_id']
        response, status_code = await create_account_request(user_telegram_id=message.from_user.id,
                                                             account_login=message.text,
                                                             dbms_name=api_dbms_dict[dbms_id])

        match status_code:
            case 201:
                await createdbuser_request(user_login=response['account_login'],
                                           user_password=response['account_password'], telegram_id=message.from_user.id,
                                           db_type=api_dbms_dict[dbms_id])

                await message.answer(
                    account_created_text(response),
                    reply_markup=create_reply_buttons(main_menu_button))
            case 500:
                await message.answer(incorrect_dbms_name_text)
            case 404:
                await message.answer(register_first_text)
            case 409:
                await message.answer(already_have_account_text)
    else:
        await message.answer(incorrect_input_text)


@user_private_router.message(StateFilter(AddAccountStates.check_accounts), F.text == edit_button)
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
    await message.answer(invent_new_login_text,
                         reply_markup=create_reply_buttons(main_menu_button, leave_current_button))
    await state.set_state(EditAccountStates.input_new_login)


@user_private_router.message(StateFilter(EditAccountStates.input_new_login))
async def edit_password(message: types.Message, state: FSMContext):
    if checking_text_correctness(message.text) or message.text == leave_current_button:
        data = await state.get_data()
        dbms_id = data['dbms_id']
        existing_accounts = data['existing_accounts']
        old_login = next(
            (account['account_login'] for account in existing_accounts if account['account_type_id'] == dbms_id), '')

        await state.update_data(old_login=old_login)
        if message.text != leave_current_button:
            await state.update_data(new_login=message.text)
        else:
            await state.update_data(new_login=old_login)

        await message.answer(invent_new_password_text,
                             reply_markup=create_reply_buttons(main_menu_button, leave_current_button))
        await state.set_state(EditAccountStates.input_new_password)
    else:
        await message.answer(incorrect_input_text)


@user_private_router.message(StateFilter(EditAccountStates.input_new_password))
async def edit_account(message: types.Message, state: FSMContext):
    if checking_password_correctness(message.text) or message.text == leave_current_button:
        data = await state.get_data()
        dbms_id = data['dbms_id']
        existing_accounts = data['existing_accounts']
        old_login = data['old_login']
        new_login = data['new_login']

        dbms_name = api_dbms_dict[dbms_id]
        old_password = next(
            (account['account_password'] for account in existing_accounts if account['account_type_id'] == dbms_id), '')

        if message.text != leave_current_button:
            new_password = message.text
        else:
            new_password = old_password

        response, status_code = await edit_account_request(user_telegram_id=str(message.from_user.id),
                                                           account_login=old_login,
                                                           account_password=old_password,
                                                           new_account_login=new_login,
                                                           new_account_password=new_password,
                                                           dbms_name=dbms_name)
        match status_code:
            case 200:
                await remote_edit_account_request(user_telegram_id=str(message.from_user.id),
                                                  account_login=old_login,
                                                  account_password=old_password,
                                                  new_account_login=new_login,
                                                  new_account_password=new_password,
                                                  dbms_name=dbms_name)
                await message.answer(
                    account_edited_text(response),
                    reply_markup=create_reply_buttons(main_menu_button))
            case 500:
                await message.answer(incorrect_dbms_name_text,
                                     reply_markup=create_reply_buttons(main_menu_button))
            case 404:
                await message.answer(register_first_text,
                                     reply_markup=create_reply_buttons(main_menu_button))
            case 401:
                await message.answer(incorrect_login_or_pass_text,
                                     reply_markup=create_reply_buttons(main_menu_button))
    else:
        await message.answer(incorrect_input_text)


@user_private_router.message(StateFilter(None), F.text == databases_button)
async def databases(message: types.Message, state: FSMContext):
    accounts_databases, status_code = await get_accounts_databases_request(user_telegram_id=str(message.from_user.id))
    await state.update_data(accounts_databases=accounts_databases)
    answer_text, buttons = format_databases_response(accounts_databases=accounts_databases)
    await message.answer(answer_text, reply_markup=create_reply_buttons(*buttons))
    await state.set_state(AddDatabaseStates.check_databases)


@user_private_router.message(StateFilter(AddDatabaseStates.check_databases), F.text == create_button)
async def create_db_btn_click(message: types.Message, state: FSMContext):
    data = await state.get_data()
    accounts_databases = data['accounts_databases']
    user_accounts, status_code = await get_accounts_request(user_telegram_id=message.from_user.id)
    buttons = [user_dbms_dict[i['account_type_id']] for i in user_accounts]
    databases_quantity = {1: 0, 2: 0, 3: 0}
    for account_database in accounts_databases:
        databases_quantity[account_database['database_type_id']] += 1
        if databases_quantity[account_database['database_type_id']] >= 3:
            buttons.remove(user_dbms_dict[account_database['database_type_id']])

    await message.answer(choose_dbms_text3, reply_markup=create_reply_buttons(*buttons, main_menu_button))
    await state.set_state(AddDatabaseStates.choice_dbms)


@user_private_router.message(StateFilter(AddDatabaseStates.choice_dbms),
                             lambda message: message.text in user_dbms_dict.values())
async def input_db_name(message: types.Message, state: FSMContext):
    dbms_id = get_dbms_id_by_name(message.text)
    await state.update_data(dbms_id=dbms_id)
    await message.answer(invent_db_name_text, reply_markup=create_reply_buttons(main_menu_button))
    await state.set_state(AddDatabaseStates.input_db_name)


@user_private_router.message(StateFilter(AddDatabaseStates.input_db_name))
async def create_database(message: types.Message, state: FSMContext):
    if checking_text_correctness(message.text):
        data = await state.get_data()
        dbms_id = data['dbms_id']
        dbms_name = api_dbms_dict[dbms_id]
        database_name = message.text
        accounts_response, accounts_status_code = await get_accounts_request(user_telegram_id=message.from_user.id)
        account_login = str()
        account_password = str()
        for account in accounts_response:
            if account['account_type_id'] == dbms_id:
                account_login = account['account_login']
                account_password = account['account_password']
        response, status_code = await create_database_request(database_name=database_name,
                                                              user_telegram_id=message.from_user.id,
                                                              account_login=account_login,
                                                              account_password=account_password,
                                                              dbms_name=dbms_name)
        match status_code:
            case 201:
                await remote_create_database_request(database_name=database_name,
                                                     user_telegram_id=message.from_user.id,
                                                     account_login=account_login,
                                                     account_password=account_password,
                                                     dbms_name=dbms_name)
                await message.answer(
                    database_created_text(database_name, response),
                    reply_markup=create_reply_buttons(main_menu_button))
            case 500:
                await message.answer(incorrect_dbms_name_text)
            case 404:
                await message.answer(register_first_text)
            case 401:
                await message.answer(incorrect_login_or_pass_text)
            case 403:
                await message.answer(too_many_databases_text)
            case 400:
                await message.answer(db_already_exists_text)
    else:
        await message.answer(incorrect_input_text)


@user_private_router.message(StateFilter(AddDatabaseStates.check_databases), F.text == delete_button)
async def delete_btn_click(message: types.Message, state: FSMContext):
    data = await state.get_data()
    accounts_databases = data['accounts_databases']
    buttons = []
    for account_database in accounts_databases:
        if user_dbms_dict[account_database['database_type_id']] not in buttons:
            buttons.append(user_dbms_dict[account_database['database_type_id']])
    await message.answer(choose_dbms_text4, reply_markup=create_reply_buttons(*buttons, main_menu_button))
    await state.set_state(DeleteDatabaseStates.choice_dbms)


@user_private_router.message(StateFilter(DeleteDatabaseStates.choice_dbms),
                             lambda message: message.text in user_dbms_dict.values())
async def input_existing_db_name(message: types.Message, state: FSMContext):
    dbms_id = get_dbms_id_by_name(message.text)
    await state.update_data(dbms_id=dbms_id)
    await message.answer(input_db_name_text, reply_markup=create_reply_buttons(main_menu_button))
    await state.set_state(DeleteDatabaseStates.input_db_name)


@user_private_router.message(StateFilter(DeleteDatabaseStates.input_db_name))
async def confirm_deletion(message: types.Message, state: FSMContext):
    data = await state.get_data()
    dbms_id = data['dbms_id']
    accounts_databases = data['accounts_databases']
    db_name = next(
        (account_database['database_name'] for account_database in accounts_databases if
         account_database['database_name'] == message.text and account_database['database_type_id'] == dbms_id), None)
    account_login = next(
        (account_database['account_login'] for account_database in accounts_databases if
         account_database['database_name'] == message.text and account_database['database_type_id'] == dbms_id), None)
    account_password = next(
        (account_database['account_password'] for account_database in accounts_databases if
         account_database['database_name'] == message.text and account_database['database_type_id'] == dbms_id), None)

    if db_name:
        await state.update_data(database_name=db_name)
        await state.update_data(account_login=account_login)
        await state.update_data(account_password=account_password)

        await message.answer(confirmation_of_deletion_text,
                             reply_markup=create_reply_buttons(yes_button, no_button))
        await state.set_state(DeleteDatabaseStates.confirmation_of_deletion)
    else:
        await message.answer(someone_else_db_text,
                             reply_markup=create_reply_buttons(main_menu_button))


@user_private_router.message(StateFilter(DeleteDatabaseStates.confirmation_of_deletion), F.text == yes_button)
async def delete_db(message: types.Message, state: FSMContext):
    data = await state.get_data()
    dbms_id = data['dbms_id']
    dbms_name = api_dbms_dict[dbms_id]
    database_name = data['database_name']
    account_login = data['account_login']
    account_password = data['account_password']
    response, status_code = await delete_database_request(database_name=database_name,
                                                          user_telegram_id=message.from_user.id,
                                                          account_login=account_login,
                                                          account_password=account_password,
                                                          dbms_name=dbms_name)
    match status_code:
        case 200:
            await message.answer(database_deleted_text,
                                 reply_markup=create_reply_buttons(main_menu_button))
        case 500:
            await message.answer(incorrect_dbms_name_text)
        case 404:
            await message.answer(register_first_text)
        case 401:
            await message.answer(incorrect_login_or_pass_text)
        case 400:
            await message.answer(db_doesnt_exists_text)
