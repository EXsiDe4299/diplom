from database_connection import ConnectionDB
import datetime
import json


class Logger(ConnectionDB):
    def __init__(self, connection_string):
        super().__init__(connection_string)
        self._log_levels = {
            '10': 'DEBUG',
            '20': 'INFO',
            '30': 'WARN',
            '40': 'ERROR',
            '50': 'CRITICAL',
        }

    def send_log(self, log_level, log_message):
        """
            Коды уровней логов:
            CRITICAL = 50
            ERROR = 40
            WARNING = 30
            INFO = 20
            DEBUG = 10
        """
        self._execute_query(
            f"INSERT INTO Log VALUES ('{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}', '{self._log_levels[log_level]}', '{log_message}')")

    def get_logs(self):
        self._execute_query("SELECT * FROM Log")
        rows = self._cursor.fetchall()
        data = list()
        for row in rows:
            data.append({
                'LogId': row[0],
                'LogDateTime': row[1],
                'LogLevelName': row[2],
                'LogMessage': row[3],
            })
        return data
