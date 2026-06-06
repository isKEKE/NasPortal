import uvicorn
import typer
import subprocess
import os
from dotenv import load_dotenv
load_dotenv()

from app.commands import admin

app = typer.Typer()


@app.command()
def rundev(host: str = "127.0.0.1", port: int = 8000, reload: bool = True):
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


@app.command()
def runprd(host: str = "0.0.0.0", port: int = 8000, workers: int = 1):
    if os.name == "nt":
        uvicorn.run("app.main:app", host=host, port=port, reload=False)
        return

    command = [
        "gunicorn",
        "app.main:app",
        "--workers", str(workers),
        "--worker-class", "uvicorn.workers.UvicornWorker",
        "--bind", f"{host}:{port}"
    ]
    subprocess.run(command)


app.add_typer(admin.app, name="admin")


if __name__ == "__main__":
    app()
