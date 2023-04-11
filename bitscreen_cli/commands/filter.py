import requests
import typer
from tabulate import tabulate
from auth import host, getConfigFromFile, BearerAuth

VISIBILITY_TYPES = {
    1: 'Private',
    2: 'Public',
    3: 'Shareable',
    4: 'Exception'
}

app = typer.Typer()

state = {
    'accessToken': None,
    'providerId': None
}


def getFilters(params={}):
    response = requests.get(host + '/filter', params=params, auth=BearerAuth(state['accessToken']))
    filters = response.json()

    return filters


def getFilterDetails(filterId):
    response = requests.get(host + '/filter/' + filterId, auth=BearerAuth(state['accessToken']))
    if response.status_code == 200:
        filter_json = response.json()
        return filter_json

    raise typer.Exit(print(response.json()['message']))


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
    headers = ["ID", "Name", "Visibility", "Status", "Subscribers", "CIDs", "Provider", "Description"]
    rows = [];
    for filter in filterList:
        rows.append([
            filter['shareId'],
            filter['name'],
            getReadableVisibility(filter['visibility']),
            'Enabled' if filter['enabled'] else 'Disabled',
            len(filter['provider_Filters']),
            filter['cidsCount'],
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
    typer.secho(f"Owner: {filter['provider']['businessName']}")
    typer.secho(f"CID count: {len(filter['cids'])}")

    printCidLists(filter['cids'])


def setFilterStatus(filter: str, status: bool):
    filterDetails = getFilterDetails(filter)

    typer.secho(filterDetails)
    exit

    allowed = False
    for providerFilter in filterDetails['provider_Filters']:
        if providerFilter['provider']['id'] == state['providerId']:
            allowed = True
            if providerFilter['active'] == status:
                raise typer.Exit("Status already set.")

    if allowed:
        params = {'active': status}
        response = requests.put(f"{host}/provider-filter/{filterDetails['id']}", json=params,
                                auth=BearerAuth(state['accessToken']))
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
        filter_list: str,
        name: str = None,
        description: str = None,
        visibility: str = typer.Option(None, callback=parseVisibilityCallback)
):
    filter_json = getFilterDetails(filter_list)

    if name is None and description is None and visibility is None:
        return typer.secho("No changes were submitted.")

    if name is not None:
        filter_json['name'] = name

    if description is not None:
        filter_json['description'] = description

    if visibility is not None:
        filter_json['visibility'] = visibility

    response = requests.put(f"{host}/filter/{filter_json['id']}", json=filter_json, auth=BearerAuth(state['accessToken']))
    if response.status_code == 200:
        typer.secho("Done.", bg=typer.colors.GREEN, fg=typer.colors.BLACK)
    else:
        typer.secho("Error: ", bg=typer.colors.RED)
        typer.secho(response.json())


@app.command()
def add(
        name: str = typer.Option(..., prompt=True),
        description: str = typer.Option(..., prompt=True),
        visibility: str = typer.Option(..., prompt="What visibility should the filter have? [Private/Public/Shareable]"),
):
    parsed_visibility = parseVisibilityCallback(visibility)

    filter_json = {
        'cids': [],
        'enabled': True,
        'name': name,
        'description': description,
        'visibility': parsed_visibility,
    }

    response = requests.post(f"{host}/filter", json=filter_json, auth=BearerAuth(state['accessToken']))

    filter_list = response.json()

    if response.status_code == 200:
        typer.secho("Done.", bg=typer.colors.GREEN, fg=typer.colors.BLACK)
        filter_list['provider_Filters'] = []
        filter_list['cids'] = []
        printFilterDetails(filter_list)
    else:
        typer.secho("Error: ", bg=typer.colors.RED)
        typer.secho(response.json())


@app.command(name="add-cid")
def add_cid(filter: str, cid: str, refUrl: str = ""):
    filter = getFilterDetails(filter)
    cid = {
        'cid': cid,
        'filterId': filter['id'],
        'refUrl': refUrl
    }

    response = requests.post(f"{host}/cid", json=cid, auth=BearerAuth(state['accessToken']))
    if response.status_code == 200:
        typer.secho("Done.", bg=typer.colors.GREEN, fg=typer.colors.BLACK)
    else:
        typer.secho("Error: ", bg=typer.colors.RED)
        typer.secho(response.json())


@app.command(name="remove-cid")
def remove_cid(filter: str, cid: str):
    filter_json = getFilterDetails(filter)
    id = None
    for cidObj in filter_json['cids']:
        if cidObj['cid'] == cid:
            id = cidObj['id']
            break

    if id is None:
        raise typer.Exit("CID not found on provided filter.")

    response = requests.post(f"{host}/filter/remove-cids-from-filter", json={
        "filterId": filter_json['id'],
        "cids": [id]
    }, auth=BearerAuth(state['accessToken']))
    if response.status_code == 200:
        typer.secho("Done.", bg=typer.colors.GREEN, fg=typer.colors.BLACK)
    else:
        typer.secho("Error: ", bg=typer.colors.RED)
        typer.secho(response.json())


@app.command()
def delete(filter: str, confirm: bool = False):
    filter = getFilterDetails(filter)

    providerFilter = None
    for providerFilter in filter['provider_Filters']:
        if providerFilter['provider']['id'] == state['providerId']:
            providerFilter = providerFilter['id']
            break

    if providerFilter is None:
        raise typer.Exit("You do not own or import this filter.");

    if not confirm:
        confirm = typer.confirm(f"Are you sure you want to delete filter {filter['name']}?")

    if not confirm:
        raise typer.Exit("Aborting.");

    response = requests.delete(f"{host}/provider-filter/{filter['id']}", auth=BearerAuth(state['accessToken']))
    if response.status_code == 200:
        typer.secho("Deleted.", bg=typer.colors.GREEN, fg=typer.colors.BLACK)
    else:
        typer.secho("Error: ", bg=typer.colors.RED)
        typer.secho(response.json())


@app.callback()
def getAuthData():
    state['accessToken'] = getConfigFromFile('access_token')
    state['providerId'] = getConfigFromFile('provider_id')

    if state['accessToken'] is None or state['providerId'] is None:
        raise typer.Exit("Not logged in.")


if __name__ == "__main__":
    app()
