import os
import shutil
import subprocess

from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()


def onerror(func, path, exc_info):
    import stat
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


@app.get("/clone", response_class=FileResponse)
async def clone_repository(repository_url: str):
    repository_name = repository_url.split('/')[-1].split('.')[0]
    try:
        subprocess.run(f"git clone {repository_url}", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        return {"message": f"Ошибка при клонировании репозитория: {e}"}

    shutil.make_archive(repository_name, 'zip', repository_name)
    shutil.rmtree(path=repository_name, onexc=onerror)

    return f'{repository_name}.zip'
