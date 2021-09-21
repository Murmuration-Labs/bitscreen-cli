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

def authenticate(signature):
    global provider, accessToken
    payload = {'signature': signature}
    response = requests.post(host + '/provider/auth/' + wallet, json=payload)
    provider = response.json()

    accessToken = provider['accessToken']

def getConfigDirectory():
    userHome = os.path.expanduser('~')
    return userHome + '/.bitscreen'

def getConfigFile():
    configDir = getConfigDirectory()
    return configDir + '/.cli_config'

def getConfigFromFile(configKey):
    cf = open(getConfigFile())
    config = json.load(cf)
    cf.close()

    return config[configKey]

@app.command()
def login():
    global wallet, privateKey, accessToken
    configDir = getConfigDirectory()

    if not os.path.isdir(configDir):
        os.mkdir(configDir)
        typer.secho("Created bitscreen config directory.")

    configFile = getConfigFile()
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

    authenticate(signedNonce)
    typer.secho(f"Authenticated as " + provider['businessName'], fg=typer.colors.GREEN)

    saveCredentials = typer.confirm("Do you want to save credentials for future logins?")

    toSave = {
        'access_token': accessToken,
        'provider_id': provider['id']
    }

    if saveCredentials:
        toSave['eth_private_key'] = privateKey
        toSave['eth_wallet'] = wallet

    with open(configFile, 'w') as f:
        f.write(json.dumps(toSave))

@app.command()
def logout():
    configDir = getConfigDirectory()
    configFile = getConfigFile()

    if not os.path.isdir(configDir) or not os.path.isfile(configFile):
        typer.secho("Not logged in.")
        raise typer.Exit()

    with open(configFile, 'w') as f:
        f.write(json.dumps({}))

if __name__ == "__main__":
    app()
