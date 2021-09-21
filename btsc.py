import json
import requests
import typer
import os

from commands import auth

app = typer.Typer()

app.add_typer(auth.app, name="auth")

if __name__ == "__main__":
    app()
