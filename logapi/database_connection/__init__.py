import pyodbc
from pyodbc import Error


class ConnectionDB:
    """
        Пример строки подключения:
        Driver={SQL Server};Server=server;Database=database;UID=userid;PWD=password;Trusted_Connection=yes
    """
    def __init__(self, connection_string):
        try:
            self._connection = pyodbc.connect(connection_string)
            self._cursor = self._connection.cursor()
        except Error as err:
            print(f"Cannot connect to the database {err}")

    def _execute_query(self, sql_query):
        self._cursor.execute(sql_query)

    def _close_connection(self):
        self._connection.commit()
        self._cursor.close()
        self._connection.close()

    def __del__(self):
        self._close_connection()
