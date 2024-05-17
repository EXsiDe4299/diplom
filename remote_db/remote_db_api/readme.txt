Нужен python версии 3.12.0

python -m venv venv
venv\scripts\activate
pip install -r requirements.txt

Создать файл .env
В .env поместить следующие поля:

MSSQL_DB_USER=
MSSQL_DB_PASSWORD=
MSSQL_DB_HOST=
MSSQL_DB_NAME=

POSTGRES_DB_USER=
POSTGRES_DB_PASSWORD=
POSTGRES_DB_HOST=
POSTGRES_DB_PORT=
POSTGRES_DB_NAME=

MARIADB_DB_USER=
MARIADB_DB_PASSWORD=
MARIADB_DB_HOST=
MARIADB_DB_PORT=
MARIADB_DB_NAME=

