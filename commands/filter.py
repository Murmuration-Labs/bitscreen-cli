import json
import requests
import typer
import os
from tabulate import tabulate
from .auth import host, getConfigFromFile, BearerAuth
from typing import Optional

VISIBILITY_TYPES = {
    1: 'Private',
    2: 'Public',
    3: 'Shareable'
}

app = typer.Typer()

state = {
    'accessToken': None,
    'providerId': None
}

def getFilters(params = {}):
    params['providerId'] = state['providerId'];

    response = requests.get(host + '/filter', params=params, auth=BearerAuth(state['accessToken']))
    filters = response.json()

    return filters

def getFilterDetails(filterId, params = {}):
    params['providerId'] = state['providerId'];

    response = requests.get(host + '/filter/' + filterId, params=params, auth=BearerAuth(state['accessToken']))
    filters = response.json()

    return filters

def getReadableVisibility(visibilityId):
    return VISIBILITY_TYPES[visibilityId]

def parseVisibilityCallback(value: str):
    if value is None:
        return None

    for key in VISIBILITY_TYPES:
        if VISIBILITY_TYPES[key].lower() == value.lower():
            return key
    raise typer.BadParameter("Invalid visibility type. Allowed types are: Private, Public, Shareable")

def parseOverrideCallback(value: int):
    if value is None:
        return None

    if value >= 0 and value <= 1:
        return value
    raise typer.BadParameter("Invalid override value. Allowed types are: 0, 1")

def printFilterLists(filterList):
    headers = ["ID", "Name", "Visibility", "Status", "Subscribers", "CIDs", "Override", "Provider", "Description"]
    rows = [];
    for filter in filterList:
        rows.append([
            filter['shareId'],
            filter['name'],
            getReadableVisibility(filter['visibility']),
            'Enabled' if filter['enabled'] else 'Disabled',
            len(filter['provider_Filters']),
            filter['cidsCount'],
            'Yes' if filter['override'] else 'No',
            filter['provider']['businessName'],
            filter['description']
        ])
    print(tabulate(rows, headers, tablefmt="fancy_grid"))

def printCidLists(cidList):
    headers = ["CID", "Reference URL", "Created", "Updated"]
    rows = []

    for cid in cidList:
        rows.append([
            cid['cid'],
            cid['refUrl'],
            cid['created'],
            cid['updated']
        ])

    print(tabulate(rows, headers, tablefmt="fancy_grid"))

def printFilterDetails(filter):
    if filter['enabled']:
        typer.secho("Enabled", bg=typer.colors.GREEN, fg=typer.colors.BLACK)
    else:
        typer.secho("Disabled", bg=typer.colors.RED)
    typer.secho(f"Filter name:  {filter['name']}")
    typer.secho(f"Description: {filter['description']}")
    typer.secho(f"ID: {filter['shareId']}")
    typer.secho(f"Visibility: {getReadableVisibility(filter['visibility'])}")
    typer.secho(f"Subscribers: {len(filter['provider_Filters'])}")
    typer.secho(f"Override: {('Yes' if filter['override'] else 'No')}")
    typer.secho(f"Owner: {filter['provider']['businessName']}")
    typer.secho(f"CID count: {len(filter['cids'])}")

    printCidLists(filter['cids'])

def setFilterStatus(filter: str, status: bool):
    filterDetails = getFilterDetails(filter)

    allowed = False
    for providerFilter in filterDetails['provider_Filters']:
        if providerFilter['provider']['id'] == state['providerId']:
            allowed = True
            if providerFilter['active'] == status:
                raise typer.Exit("Status already set.")

    if allowed:
        params = {'active': status}
        response = requests.put(f"{host}/provider-filter/{state['providerId']}/{filterDetails['id']}", json=params, auth=BearerAuth(state['accessToken']))
        if response.status_code == 200:
            typer.secho("Done.", bg=typer.colors.GREEN, fg=typer.colors.BLACK)
        else:
            typer.secho("Error: ", bg=typer.colors.RED)
            typer.secho(response.json())

@app.command()
def list(search: str = ""):
    params = {};
    if len(search) > 0:
        params['q'] = search
    filters = getFilters(params)

    print("Found " + str(filters['count']) + " filters:")

    printFilterLists(filters['filters'])

@app.command()
def details(filter: str):
    filterDetails = getFilterDetails(filter)
    printFilterDetails(filterDetails)

@app.command()
def enable(filter: str):
    setFilterStatus(filter, True)

@app.command()
def disable(filter: str):
    setFilterStatus(filter, False)

@app.command()
def edit(
    filter: str,
    name: str = None,
    description: str = None,
    override: int = typer.Option(None, callback=parseOverrideCallback),
    visibility: str = typer.Option(None, callback=parseVisibilityCallback)
):
    filter = getFilterDetails(filter)
    if name is not None:
        filter['name'] = name

    if description is not None:
        filter['description'] = description

    if override is not None:
        filter['override'] = (override == 1)

    if visibility is not None:
        filter['visibility'] = visibility

    response = requests.put(f"{host}/filter/{filter['id']}", json=filter, auth=BearerAuth(state['accessToken']))
    if response.status_code == 200:
        typer.secho("Done.", bg=typer.colors.GREEN, fg=typer.colors.BLACK)
    else:
        typer.secho("Error: ", bg=typer.colors.RED)
        typer.secho(response.json())

@app.command()
def add():
    print("Not implemented yet.")

@app.callback()
def getAuthData():
    state['accessToken'] = getConfigFromFile('access_token')
    state['providerId'] = getConfigFromFile('provider_id')

if __name__ == "__main__":
    app()
