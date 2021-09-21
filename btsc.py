#!/usr/bin/env python

import json
import requests
import typer
import os

from commands import auth, filter

app = typer.Typer()

app.add_typer(auth.app, name="auth")
app.add_typer(filter.app, name="filter")

if __name__ == "__main__":
    app()
