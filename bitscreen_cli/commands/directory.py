import requests
import typer
from tabulate import tabulate
from auth import host, getConfigFromFile, BearerAuth
from filter import getReadableVisibility

app = typer.Typer()

state = {
    'accessToken': None,
    'providerId': None
}


def get_public_filters(params={}):
    response = requests.get(host + '/filter/public', params=params, auth=BearerAuth(state['accessToken']))
    filters = response.json()

    return filters['data']


def get_public_filter_details(filter_id):
    response = requests.get(host + '/filter/public/details/' + filter_id,
                            auth=BearerAuth(state['accessToken']))

    if response.status_code == 200:
        data = response.json()
        data['filter']['isImported'] = data['isImported']
        data['filter']['provider'] = data['provider']
        return data['filter']

    raise typer.Exit("Filter not found or is not public / shareable.")


def get_status_from_filter(public_filter):
    status = typer.style("Not imported", fg=typer.colors.WHITE, bg=typer.colors.RED)
    if public_filter['isImported']:
        status = typer.style("Imported", fg=typer.colors.GREEN, bold=True)
    elif public_filter['provider']['id'] == state['providerId']:
        status = typer.style("Owned", fg=typer.colors.GREEN)

    return status


def print_public_filter_lists(filter_list: list):
    headers = ["ID", "Name", "Visibility", "Status", "Subscribers", "CIDs", "Provider", "Description"]
    rows = []
    typer.secho(filter_list)
    for public_filter in filter_list:
        status = get_status_from_filter(public_filter)

        rows.append([
            public_filter['shareId'],
            public_filter['name'],
            getReadableVisibility(public_filter['visibility']),
            status,
            public_filter['subs'],
            public_filter['cids'],
            public_filter['provider']['businessName'],
            public_filter['description']
        ])
    print(tabulate(rows, headers, tablefmt="fancy_grid"))


def print_public_filter_details(public_filter):
    typer.echo(get_status_from_filter(public_filter))
    typer.secho(f"Filter name:  {public_filter['name']}")
    typer.secho(f"Description: {public_filter['description']}")
    typer.secho(f"ID: {public_filter['shareId']}")
    typer.secho(f"Subscribers: {len(public_filter['provider_Filters'])}")
    typer.secho(f"CID count: {len(public_filter['cids'])}")
    typer.secho(f"Business name: {public_filter['provider']['businessName']}")
    typer.secho(f"Contact person: {public_filter['provider']['contactPerson']}")
    typer.secho(f"Website: {public_filter['provider']['website']}")
    typer.secho(f"Email: {public_filter['provider']['businessName']}")
    typer.secho(f"Address: {public_filter['provider']['businessName']}")
    typer.secho(f"City & Country: {public_filter['provider']['businessName']}")


@app.command(name="list")
def list_filters(search: str = ""):
    params = {}
    if len(search) > 0:
        params['q'] = search
    filters = get_public_filters(params)

    typer.secho(f"Found {len(filters)} filters.")
    print_public_filter_lists(filters)


@app.command()
def details(filter_share_id: str):
    public_filter = get_public_filter_details(filter_share_id)

    print_public_filter_details(public_filter)


@app.command(name="import")
def import_filter(filter_share_id: str):
    public_filter = get_public_filter_details(filter_share_id)
    if public_filter['isImported']:
        raise typer.Exit("Filter already imported.")

    provider_filter = {
        'active': True,
        'filterId': public_filter['id']
    }

    response = requests.post(f"{host}/provider-filter", json=provider_filter, auth=BearerAuth(state['accessToken']))
    if response.status_code == 200:
        typer.secho("Imported.", bg=typer.colors.GREEN, fg=typer.colors.BLACK)
    else:
        typer.secho("Error: ", bg=typer.colors.RED)
        typer.secho(response.json())


@app.command(name="discard")
def discard_filter(filter_share_id: str):
    public_filter = get_public_filter_details(filter_share_id)

    if not public_filter['isImported']:
        raise typer.Exit("This filter is not imported.")

    response = requests.delete(f"{host}/provider-filter/{public_filter['id']}",
                               auth=BearerAuth(state['accessToken']))
    if response.status_code == 200:
        typer.secho("Discarded.", bg=typer.colors.GREEN, fg=typer.colors.BLACK)
    else:
        typer.secho("Error: ", bg=typer.colors.RED)
        typer.secho(response.json())


@app.callback()
def get_auth_data():
    state['accessToken'] = getConfigFromFile('access_token')
    state['providerId'] = getConfigFromFile('provider_id')

    if state['accessToken'] is None or state['providerId'] is None:
        raise typer.Exit("Not logged in.")


if __name__ == "__main__":
    app()
