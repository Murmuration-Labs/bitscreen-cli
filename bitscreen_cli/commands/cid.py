import json
import requests
import typer
import os
from .auth import host, getConfigFromFile, BearerAuth
from typing import Optional

state = {
    'accessToken': None,
    'providerId': None
}

app = typer.Typer()

def getCids(download = False):
    query = {
        download: download
    }

    response = requests.get(host + '/cid/blocked', params=query, auth=BearerAuth(state['accessToken']))

    if download:
        return response.content

    cids = response.json()

    return cids

@app.command()
def list(
    outputFile: str = typer.Option(None, "--outputfile", "-o")
):
    if outputFile:
        cids = getCids(True)
        open(outputFile, 'wb').write(cids)
        raise typer.Exit("CID list written at: " + outputFile)

    cids = getCids(False)

    print("Found " + str(len(cids)) + " blocked CIDs:")

    for cid in cids:
        typer.secho(cid)

@app.command()
def add(
    cid: str,
    cidFile: str = typer.Option("~/.murmuration/bitscreen", "--file", "-f")
):
    filePath = os.getenv("BITSCREEN_CIDS_FILE", cidFile)
    if not os.path.isfile(os.path.expanduser(filePath)):
        typer.secho("File not found: " + cidFile)
        typer.Exit()
    f = open(os.path.expanduser(filePath));
    data = json.load(f)
    print(data)
    f.close()

    data.append(cid)

    with open(os.path.expanduser(filePath), 'w') as f:
        json.dump(data, f)


@app.callback()
def getAuthData():
    state['accessToken'] = getConfigFromFile('access_token')
    state['providerId'] = getConfigFromFile('provider_id')

    if state['accessToken'] is None or state['providerId'] is None:
        raise typer.Exit("Not logged in.")

if __name__ == "__main__":
    app()
