import json
import requests
import typer
import os
from tabulate import tabulate
from .auth import host, getConfigFromFile, BearerAuth
from .filter import getReadableVisibility

app = typer.Typer()

state = {
    'accessToken': None,
    'providerId': None
}

def getPublicFilters(params = {}):
    params['providerId'] = state['providerId'];

    response = requests.get(host + '/filter/public', params=params, auth=BearerAuth(state['accessToken']))
    filters = response.json()

    return filters['data']

def printPublicFilterLists(filterList: list):
    headers = ["ID", "Name", "Visibility", "Status", "Subscribers", "CIDs", "Override", "Provider", "Description"]
    rows = [];
    for filter in filterList:
        status = typer.style("Not imported", fg=typer.colors.WHITE, bg=typer.colors.RED)
        if filter['isImported']:
            status = typer.style("Imported", fg=typer.colors.GREEN, bold=True)
        elif filter['provider']['id'] == state['providerId']:
            status = typer.style("Owned", fg=typer.colors.GREEN)

        rows.append([
            filter['shareId'],
            filter['name'],
            getReadableVisibility(filter['visibility']),
            status,
            filter['subs'],
            filter['cids'],
            'Yes' if filter['override'] else 'No',
            filter['provider']['businessName'],
            filter['description']
        ])
    print(tabulate(rows, headers, tablefmt="fancy_grid"))

@app.command()
def list(search: str = ""):
    params = {};
    if len(search) > 0:
        params['q'] = search
    filters = getPublicFilters(params)

    typer.secho(f"Found {len(filters)} filters.")
    printPublicFilterLists(filters)

@app.callback()
def getAuthData():
    state['accessToken'] = getConfigFromFile('access_token')
    state['providerId'] = getConfigFromFile('provider_id')

    if state['accessToken'] is None or state['providerId'] is None:
        raise typer.Exit("Not logged in.")

if __name__ == "__main__":
    app()
