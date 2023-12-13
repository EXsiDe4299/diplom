"""
http://127.0.0.1:8000/docs - открывает Swagger UI
"""
from logger import Logger
from fastapi import FastAPI

myLogger = Logger('Driver={SQL Server};Server=computer;Database=xixixixixi;UID=sa;PWD=111;Trusted_Connection=yes')
app = FastAPI()
myLogger.get_logs()


@app.get('/log')
def get_all_logs():
    logs = myLogger.get_logs()
    return logs


@app.post('/log')
def add_log(log_level, log_message):
    myLogger.send_log(log_level=log_level, log_message=log_message)
