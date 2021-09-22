import json
import requests
import typer
import os
from tabulate import tabulate
from .auth import host, getConfigFromFile

app = typer.Typer()

state = {
    'accessToken': None,
    'providerId': None
}

def getFilters(params = {}):
    params['providerId'] = state['providerId'];

    response = requests.get(host + '/filter', params=params, headers={'Authorization': 'Bearer ' + state['accessToken']})
    filters = response.json()

    return filters

def getFilterDetails(filterId, params = {}):
    params['providerId'] = state['providerId'];

    response = requests.get(host + '/filter/' + filterId, params=params, headers={'Authorization': 'Bearer ' + state['accessToken']})
    filters = response.json()

    return filters

def getReadableVisibility(visibilityId):
    return {
        1: 'Private',
        2: 'Public',
        3: 'Shareable'
    }[visibilityId]

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
    typer.secho(f"Filter name:  {filter['name']}")
    typer.secho(f"Description: {filter['description']}")
    typer.secho(f"ID: {filter['shareId']}")
    typer.secho(f"Visibility: {getReadableVisibility(filter['visibility'])}")
    typer.secho(f"Subscribers: {len(filter['provider_Filters'])}")
    typer.secho(f"Override: {('Yes' if filter['override'] else 'No')}")
    typer.secho(f"Owner: {filter['provider']['businessName']}")
    typer.secho(f"CID count: {len(filter['cids'])}")

    printCidLists(filter['cids'])

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
def add():
    print("Not implemented yet.")

@app.callback()
def getAuthData():
    state['accessToken'] = getConfigFromFile('access_token')
    state['providerId'] = getConfigFromFile('provider_id')

if __name__ == "__main__":
    app()
