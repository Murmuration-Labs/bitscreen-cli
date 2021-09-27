import json
import requests
import typer
import os
from enum import Enum
from tabulate import tabulate
from .auth import host, getConfigFromFile, BearerAuth

app = typer.Typer()

state = {
    'accessToken': None,
    'providerId': None
}

class Action(str, Enum):
    Filtering = "filtering",
    Sharing = "sharing",
    Importing = "importing"

def setValue(action: Action, value: bool):
    response = requests.get(f"{host}/config/{state['providerId']}", auth=BearerAuth(state['accessToken']))
    if response.status_code != 200:
        typer.secho("Error: ", bg=typer.colors.RED)
        typer.secho(response.json())
        raise typer.Exit()

    config = response.json()

    key = None
    if action is Action.Filtering:
        key = 'bitscreen'
    if action is Action.Sharing:
        key = 'share'
    if action is Action.Importing:
        key = 'import'

    if key is None:
        raise typer.Exit("Invalid action")

    if config[key] == value:
        raise typer.Exit("Value already set.")

    config['providerId'] = state['providerId']
    config[key] = value;
    response = requests.put(f"{host}/config", json=config, auth=BearerAuth(state['accessToken']))
    if response.status_code == 200:
        typer.secho("Done.", bg=typer.colors.GREEN, fg=typer.colors.BLACK)
    else:
        typer.secho("Error: ", bg=typer.colors.RED)
        print(response)

@app.command()
def enable(
    action: Action = typer.Argument(..., case_sensitive=False)
):
    setValue(action, True)

@app.command()
def disable(
    action: Action = typer.Argument(..., case_sensitive=False)
):
    setValue(action, False)

@app.callback()
def getAuthData():
    state['accessToken'] = getConfigFromFile('access_token')
    state['providerId'] = getConfigFromFile('provider_id')

    if state['accessToken'] is None or state['providerId'] is None:
        raise typer.Exit("Not logged in.")

if __name__ == "__main__":
    app()
