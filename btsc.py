#!/usr/bin/env python

import json
import requests
import typer
import os

from commands import auth, filter, directory

app = typer.Typer()

app.add_typer(auth.app, name="auth")
app.add_typer(filter.app, name="filter")
app.add_typer(directory.app, name="directory")

if __name__ == "__main__":
    app()
