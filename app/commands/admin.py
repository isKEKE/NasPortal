# app/commands/cli.py
import typer
from app.models.database import SessionLocal
from app.crud.user import create_user, ensure_user
from app.schemas.user import UserCreate

app = typer.Typer()

@app.command()
def init(username: str = "admin", password: str = "admin"):
    db = SessionLocal()
    try:
        user_data = UserCreate(username=username, password=password, is_superuser=True)
        user = create_user(db, user_data)
        typer.echo(f"Admin user created: {user.username}")
    except Exception as e:
        typer.echo(f"Error creating admin user: {e}")
    finally:
        db.close()


@app.command()
def ensure(username: str = "admin", password: str = "admin"):
    db = SessionLocal()
    try:
        user_data = UserCreate(username=username, password=password, is_superuser=True)
        user = ensure_user(db, user_data)
        typer.echo(f"Admin user ready: {user.username}")
    except Exception as e:
        typer.echo(f"Error ensuring admin user: {e}")
    finally:
        db.close()
