import json
import requests
import typer
import os
from web3.auto import w3
from eth_account.messages import encode_defunct

app = typer.Typer()

host = "http://172.30.1.3:3030"
wallet = None
privateKey = None
accessToken = None
provider = None

def getNonce():
    response = requests.get(host + '/provider/' + wallet)

    return response.json()['nonce']

def signMessage(msg):
    message = encode_defunct(text=msg)
    signedMessage = w3.eth.account.sign_message(message, private_key=privateKey)

    return signedMessage.signature.hex()

def getAccessToken(signature):
    global provider
    payload = {'signature': signature}
    response = requests.post(host + '/provider/auth/' + wallet, json=payload)
    provider = response.json()

    return provider['accessToken']

@app.command()
def login():
    global wallet, privateKey, accessToken
    userHome = os.path.expanduser('~')
    configDir = userHome + '/.bitscreen'

    if not os.path.isdir(configDir):
        os.mkdir(configDir)
        typer.secho("Created bitscreen config directory.")

    configFile = configDir + '/.cli_config'
    if not os.path.isfile(configFile):
        with open(configFile, 'w') as fp:
            fp.write('{}')
        typer.secho("Created bitscreen config file.")

    typer.echo(f"Checking credentials.")

    cf = open(configFile)
    config = json.load(cf)
    cf.close()

    if 'eth_wallet' in config:
        wallet = config['eth_wallet'].lower()
    else:
        wallet = typer.prompt("What's you Ethereum wallet address?").lower()

    if 'eth_private_key' in config:
        privateKey = config['eth_private_key']
    else:
        privateKey = typer.prompt("What's your private key?")

    nonce = getNonce()
    signedNonce = signMessage(nonce)

    accessToken = getAccessToken(signedNonce)
    typer.secho(f"Authenticated as " + provider['businessName'], fg=typer.colors.GREEN)

    saveCredentials = typer.confirm("Do you want to save credentials for future logins?")

    toSave = {
        'access_token': accessToken
    }

    if saveCredentials:
        toSave['eth_private_key'] = privateKey
        toSave['eth_wallet'] = wallet

    with open(configFile, 'w') as f:
        f.write(json.dumps(toSave))

@app.command()
def logout():
    userHome = os.path.expanduser('~')
    configDir = userHome + '/.bitscreen'
    configFile = configDir + '/.cli_config'

    if not os.path.isdir(configDir) or not os.path.isfile(configFile):
        typer.secho("Not logged in.")
        raise typer.Exit()

    with open(configFile, 'w') as f:
        f.write(json.dumps({}))

if __name__ == "__main__":
    app()
