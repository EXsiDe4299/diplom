import re

from common.buttons import edit_button, create_button, main_menu_button, delete_button
from common.something import user_dbms_dict


def format_accounts_response(existing_accounts):
    answer_text = 'Аккаунты:'
    buttons = [main_menu_button]
    if len(existing_accounts) < 3:
        buttons.insert(0, create_button)
    if len(existing_accounts) > 0:
        for i in existing_accounts:
            answer_text += f'\n{user_dbms_dict[i["account_type_id"]]}\nЛогин: {i["account_login"]}\nПароль: <span class="tg-spoiler">{i["account_password"]}</span>\n'
        buttons.insert(1, edit_button)
    else:
        answer_text = 'У вас еще нет аккаунта ни в одной из СУБД'

    return answer_text, buttons


def format_databases_response(accounts_databases):
    answer_text = 'Базы данных:\n'
    buttons = [main_menu_button]

    if len(accounts_databases) < 9:
        buttons.append(create_button)
    if len(accounts_databases) > 0:
        buttons.append(delete_button)

        for account_database in accounts_databases:
            dbms_name = user_dbms_dict[account_database["database_type_id"]]
            if dbms_name not in answer_text:
                answer_text += f'{dbms_name}\n'
            answer_text += f'Название: {account_database["database_name"]}\n'
            answer_text += f'Строка подключения: <code>{account_database["connection_string"]}</code>\n\n'
    else:
        answer_text = 'У вас еще нет ни одной базы данных'

    return answer_text, buttons


def remove_excess_dbms_buttons(existing_accounts):
    buttons = list(user_dbms_dict.values())
    for existing_account in existing_accounts:
        buttons.remove(user_dbms_dict[existing_account['account_type_id']])
    return buttons


def get_dbms_buttons(existing_accounts):
    buttons = []
    for existing_account in existing_accounts:
        buttons.append(user_dbms_dict[existing_account['account_type_id']])
    return buttons


def get_dbms_id_by_name(dbms_name):
    return next((key for key, value in user_dbms_dict.items() if value == dbms_name))


def checking_text_correctness(text):
    return bool(re.search('^[a-zA-Z_]{1,75}$', text))


def checking_password_correctness(text):
    return bool(re.search('^[a-zA-Z0-9!@#$%^&*()-_+=]{1,75}$', text))
