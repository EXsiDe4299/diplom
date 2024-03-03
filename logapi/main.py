from fastapi import FastAPI, status, Query
from pydantic import BaseModel
from datetime import datetime
from typing import Annotated
import pyodbc
from pyodbc import Error

app = FastAPI()


class LogOutput(BaseModel):
    LogId: int
    LogDateTime: datetime
    LogLevelName: str
    LogMessage: str


class LogInput(BaseModel):
    LogDateTime: datetime
    LogLevelName: str
    LogMessage: str


class DBConnection:
    def __init__(self, connection_string):
        try:
            self._connection = pyodbc.connect(connection_string)
            self.cursor = self._connection.cursor()
        except Error as err:
            print(f"Cannot connect to the database {err}")

    def __del__(self):
        self._connection.commit()
        self.cursor.close()
        self._connection.close()


class Logger(DBConnection):
    def __init__(self, connection_string):
        super().__init__(connection_string=connection_string)

    def get_logs(self):
        self.cursor.execute('SELECT * FROM Log')
        rows = self.cursor.fetchall()
        data = list()
        for row in rows:
            data.append(LogOutput(LogId=row[0], LogDateTime=row[1], LogLevelName=row[2], LogMessage=row[3]))
        return data

    def get_logs_by_level(self, log_level_name: str):
        self.cursor.execute(f"SELECT * FROM Log WHERE LogLevelName='{log_level_name}'")
        rows = self.cursor.fetchall()
        data = list()
        for row in rows:
            data.append(LogOutput(LogId=row[0], LogDateTime=row[1], LogLevelName=row[2], LogMessage=row[3]))
        return data

    def add_log(self, log: LogInput):
        self.cursor.execute(
            f"INSERT INTO Log VALUES ('{log.LogDateTime.strftime('%Y-%m-%d %H:%M:%S')}', '{log.LogLevelName}', '{log.LogMessage}')")

    def clear_all_logs(self):
        self.cursor.execute('TRUNCATE TABLE Log')

    def delete_logs_by_level(self, log_level):
        self.cursor.execute(f"DELETE FROM Log WHERE LogLevelName='{log_level}'")


logger = Logger(
    'Driver={SQL Server};Server=;Database=;UID=;PWD=;Trusted_Connection=yes')


@app.get('/get-logs/', response_model=list[LogOutput])
async def get_logs():
    received_logs = logger.get_logs()
    return received_logs


@app.get('/get-logs-by-level/', response_model=list[LogOutput])
async def get_logs_by_level(log_level_name: Annotated[str, Query(max_length=50)]):
    received_logs = logger.get_logs_by_level(log_level_name=log_level_name.strip())
    return received_logs


@app.post('/add-log/', status_code=status.HTTP_201_CREATED)
async def create_log(log_level_name: Annotated[str, Query(max_length=50)],
                     log_message: Annotated[str, Query(max_length=150)]):
    new_log = LogInput(
        LogDateTime=datetime.now(),
        LogLevelName=log_level_name.strip(),
        LogMessage=log_message.strip()
    )
    logger.add_log(log=new_log)


@app.delete('/delete-logs/', status_code=status.HTTP_200_OK)
async def clear_all_logs():
    logger.clear_all_logs()


@app.delete('/delete-logs-by-level/', status_code=status.HTTP_200_OK)
async def delete_logs_by_level(log_level: Annotated[str, Query(max_length=50)]):
    logger.delete_logs_by_level(log_level)
