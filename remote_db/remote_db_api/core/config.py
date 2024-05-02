import os
from dotenv import load_dotenv

load_dotenv()

MSSQL_DB_USER = os.getenv("MSSQL_DB_USER")
MSSQL_DB_PASSWORD = os.getenv("MSSQL_DB_PASSWORD")
MSSQL_DB_HOST = os.getenv("MSSQL_DB_HOST")
MSSQL_DB_NAME = os.getenv("MSSQL_DB_NAME")

POSTGRES_DB_USER = os.getenv('POSTGRES_DB_USER')
POSTGRES_DB_PASSWORD = os.getenv('POSTGRES_DB_PASSWORD')
POSTGRES_DB_HOST = os.getenv('POSTGRES_DB_HOST')
POSTGRES_DB_PORT = os.getenv('POSTGRES_DB_PORT')
POSTGRES_DB_NAME = os.getenv('POSTGRES_DB_NAME')


