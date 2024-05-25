from common.api_urls import mssql_account_create_url, pg_account_create_url, mariadb_account_create_url
from common.something import dbms_dict


async def format_accounts_response(response):
    answer_text = 'гав 🐶\n\nАккаунты:'
    buttons = ['📚 Главное меню']

    if len(response) < 3:
        buttons.insert(0, '🔐 Создать')
    if len(response) > 0:
        for i in response:
            answer_text += f'\n{dbms_dict[i["account_type_id"]]}\nЛогин: {i["account_login"]}\nПароль: <span class="tg-spoiler">{i["account_password"]}</span>\n'
        buttons.insert(1, '🔄 Редактировать')

    return answer_text, buttons


async def remove_excess_dbms_buttons(existing_accounts):
    buttons = list(dbms_dict.values())
    for existing_account in existing_accounts:
        buttons.remove(dbms_dict[existing_account['account_type_id']])
    return buttons


async def get_dbms_id_by_name(dbms_name):
    for key, value in dbms_dict.items():
        if value == dbms_name:
            return key


async def get_create_account_url(dbms_id):
    url_dict = {1: mssql_account_create_url, 2: pg_account_create_url, 3: mariadb_account_create_url}
    return url_dict[dbms_id]
