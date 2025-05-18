import uvicorn
import typer
from dotenv import load_dotenv
load_dotenv()

from app.commands import admin


app = typer.Typer()

@app.command()
def runserver(host: str = "127.0.0.1", port: int = 8001, reload: bool = True):
    """
    启动 FastAPI 服务器
    """
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


app.add_typer(admin.app, name="admin")


if __name__ == "__main__":
    app()
