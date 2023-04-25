import typer
from auth import getConfigFromFile
from dashing import *
import requests
from auth import host, getConfigFromFile, BearerAuth

app = typer.Typer()

state = {
    'accessToken': None,
    'providerId': None
}

def get_dashboard_data():
    response = requests.get(host + '/filter/dashboard', auth=BearerAuth(state['accessToken']))
    dashboard_data = response.json()

    return dashboard_data

@app.command()
def show():
    dashboard_data = get_dashboard_data()
    typer.secho(dashboard_data)
    textColor = 2
    borderColor = 3
    ui = VSplit(
        HSplit(
            Text(f"Currently Filtering CIDs\n{dashboard_data['currentlyFiltering']}", color=textColor, border_color=borderColor),
            Text(f"List subscriberss\n{dashboard_data['listSubscribers']}", color=textColor, border_color=borderColor),
            Text(f"Deals declined\n{dashboard_data['dealsDeclined']}", color=textColor, border_color=borderColor),
        ),
        HSplit(
            Text(f"Active lists\n{dashboard_data['activeLists']}", color=textColor, border_color=borderColor),
            Text(f"Inactive lists\n{dashboard_data['inactiveLists']}", color=textColor, border_color=borderColor),
            Text(f"Imported lists\n{dashboard_data['importedLists']}", color=textColor, border_color=borderColor),
            Text(f"Private lists\n{dashboard_data['privateLists']}", color=textColor, border_color=borderColor),
            Text(f"Public lists\n{dashboard_data['publicLists']}", color=textColor, border_color=borderColor),
        ),
        HSplit(),
        HSplit()
    )

    ui.display()


@app.callback()
def getAuthData():
    state['accessToken'] = getConfigFromFile('access_token')
    state['providerId'] = getConfigFromFile('provider_id')

    if state['accessToken'] is None or state['providerId'] is None:
        raise typer.Exit("Not logged in.")

if __name__ == "__main__":
    app()
