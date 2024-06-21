main_menu_text = 'Это главное меню 📚\n\nЗдесь вы можете посмотреть ваши аккаунты и базы данных в трех СУБД: MSSQL, PostgreSQL и MariaDB'
choose_dbms_text = 'Выберите СУБД, в которой хотите создать аккаунт:'
choose_dbms_text2 = 'Выберите СУБД, в которой хотите редактировать аккаунт:'
choose_dbms_text3 = 'Выберите СУБД, в которой хотите создать базу данных:'
choose_dbms_text4 = 'Выберите СУБД, в которой хотите удалить базу данных:'
confirmation_of_deletion_text = '❓ Вы уверены, что хотите удалить?'
invent_db_name_text = 'Придумайте название для новой базы данных:'
input_db_name_text = 'Введите название базы данных:'
invent_login_text = 'Придумайте логин:'
invent_new_login_text = 'Придумайте новый логин:'
invent_new_password_text = 'Придумайте новый пароль:'
database_deleted_text = '🚮 База данных успешно удалена'
incorrect_dbms_name_text = '❗ Некорректное имя СУБД'
register_first_text = '❗ Сначала необходимо зарегистрироваться'
already_have_account_text = '❗ У вас уже есть аккаунт в этой СУБД'
incorrect_input_text = '❗ Некорректный ввод'
incorrect_login_or_pass_text = '❗ Неправильный логин или пароль'
too_many_databases_text = '❗ Достигнут лимит по количеству баз данных в этой СУБД'
db_already_exists_text = '❗ База данных с таким названием уже существует в этой СУБД'
someone_else_db_text = '❗ Такой базы данных не существует или вы не являетесь ее владельцем'
db_doesnt_exists_text = '❗ Базы данных с таким названием не существует в этой СУБД'


def account_created_text(response):
    return f'✅ Аккаунт успешно создан.\n\nЛогин: {response["account_login"]}\nПароль: {response["account_password"]}'


def account_edited_text(response):
    return f'✅ Аккаунт успешно изменен.\n\nЛогин: {response["account_login"]}\nПароль: {response["account_password"]}'


def database_created_text(database_name, response):
    return f'✅ База данных успешно создана.\n\nНазвание базы данных: {database_name}\nСтрока подключения: <code>{response}</code>'
