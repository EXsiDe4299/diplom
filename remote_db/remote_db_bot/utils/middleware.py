from common.something import user_dbms_dict


def format_accounts_response(response):
    answer_text = 'гав 🐶\n\nАккаунты:'
    buttons = ['📚 Главное меню']

    if len(response) < 3:
        buttons.insert(0, '🔐 Создать')
    if len(response) > 0:
        for i in response:
            answer_text += f'\n{user_dbms_dict[i["account_type_id"]]}\nЛогин: {i["account_login"]}\nПароль: <span class="tg-spoiler">{i["account_password"]}</span>\n'
        buttons.insert(1, '🔄 Редактировать')

    return answer_text, buttons


def format_databases_response(accounts_databases):
    answer_text = 'гав 🐶\n\nБазы данных:\n'
    buttons = ['📚 Главное меню']

    if len(accounts_databases) < 9:
        buttons.append('🔐 Создать')
    if len(accounts_databases) > 0:
        buttons.append('❌ Удалить')

    for account_database in accounts_databases:
        dbms_name = user_dbms_dict[account_database["database_type_id"]]
        if dbms_name not in answer_text:
            answer_text += f'{dbms_name}\n'
        answer_text += f'Название: {account_database["database_name"]}\n'
        answer_text += f'Строка подключения: <code>{account_database["connection_string"]}</code>\n\n'

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
