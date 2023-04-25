import requests
import typer
from enum import Enum
import auth

countryCodes = ["AF", "AX", "AL", "DZ", "AS", "AD", "AO", "AI", "AQ", "AG", "AR", "AM", "AW", "AU", "AT", "AZ", "BS",
                "BH", "BD", "BB", "BY", "BE", "BZ", "BJ", "BM", "BT", "BO", "BQ", "BA", "BW", "BV", "BR", "IO", "BN",
                "BG", "BF", "BI", "CV", "KH", "CM", "CA", "KY", "CF", "TD", "CL", "CN", "CX", "CC", "CO", "KM", "CG",
                "CD", "CK", "CR", "HR", "CU", "CW", "CY", "CZ", "CI", "DK", "DJ", "DM", "DO", "EC", "EG", "SV", "GQ",
                "ER", "EE", "SZ", "ET", "FK", "FO", "FJ", "FI", "FR", "GF", "PF", "TF", "GA", "GM", "GE", "DE", "GH",
                "GI", "GR", "GL", "GD", "GP", "GU", "GT", "GG", "GN", "GW", "GY", "HT", "HM", "VA", "HN", "HK", "HU",
                "IS", "IN", "ID", "IR", "IQ", "IE", "IM", "IL", "IT", "JM", "JP", "JE", "JO", "KZ", "KE", "KI", "KP",
                "KR", "KW", "KG", "LA", "LV", "LB", "LS", "LR", "LY", "LI", "LT", "LU", "MO", "MG", "MW", "MY", "MV",
                "ML", "MT", "MH", "MQ", "MR", "MU", "YT", "MX", "FM", "MD", "MC", "MN", "ME", "MS", "MA", "MZ", "MM",
                "NA", "NR", "NP", "NL", "NC", "NZ", "NI", "NE", "NG", "NU", "NF", "MK", "MP", "NO", "OM", "PK", "PW",
                "PS", "PA", "PG", "PY", "PE", "PH", "PN", "PL", "PT", "PR", "QA", "RO", "RU", "RW", "RE", "BL", "SH",
                "KN", "LC", "MF", "PM", "VC", "WS", "SM", "ST", "SA", "SN", "RS", "SC", "SL", "SG", "SX", "SK", "SI",
                "SB", "SO", "ZA", "GS", "SS", "ES", "LK", "SD", "SR", "SJ", "SE", "CH", "SY", "TW", "TJ", "TZ", "TH",
                "TL", "TG", "TK", "TO", "TT", "TN", "TR", "TM", "TC", "TV", "UG", "UA", "AE", "GB", "UM", "US", "UY",
                "UZ", "VU", "VE", "VN", "VG", "VI", "WF", "EH", "YE", "ZM", "ZW"]
host = auth.host
getConfigFromFile = auth.getConfigFromFile
BearerAuth = auth.BearerAuth

app = typer.Typer()

state = {
    'accessToken': None,
    'providerId': None,
    'wallet': None
}


class Action(str, Enum):
    Filtering = "filtering",
    Sharing = "sharing",
    Importing = "importing",
    Safer = "Safer"


class ProviderDataKey(str, Enum):
    Country = "country",
    BusinessName = "name",
    Website = "website",
    Email = "email",
    ContactPerson = "contact-person",
    Address = "address",
    MinerId = "miner-id"


def mapProviderDataKey(key: ProviderDataKey):
    return {
        ProviderDataKey.Country: "country",
        ProviderDataKey.BusinessName: "businessName",
        ProviderDataKey.Website: "website",
        ProviderDataKey.Email: "email",
        ProviderDataKey.ContactPerson: "contactPerson",
        ProviderDataKey.Address: "address",
        ProviderDataKey.MinerId: "minerId",
    }[key]


def setValue(action: Action, value: bool):
    response = requests.get(f"{host}/config", auth=BearerAuth(state['accessToken']))
    if response.status_code != 200:
        typer.secho("Error: ", bg=typer.colors.RED)
        typer.secho(response.json())
        raise typer.Exit()

    config = response.json()

    typer.secho(config);

    key = None
    if action is Action.Filtering:
        key = 'bitscreen'
    if action is Action.Sharing:
        key = 'share'
    if action is Action.Importing:
        key = 'import'
    if action is Action.Safer:
        key = 'safer'

    if key is None:
        raise typer.Exit("Invalid action")

    if config[key] == value:
        raise typer.Exit("Value already set.")

    config[key] = value
    response = requests.patch(f"{host}/provider", json={
        "config": config
    }, auth=BearerAuth(state['accessToken']))
    if response.status_code == 200:
        typer.secho("Done.", bg=typer.colors.GREEN, fg=typer.colors.BLACK)
    else:
        typer.secho("Error: ", bg=typer.colors.RED)
        print(response.json())


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


@app.command(name="set")
def setProviderData(
        key: ProviderDataKey = typer.Argument(..., case_sensitive=False),
        value: str = typer.Argument(...)
):
    if key == ProviderDataKey.Country and value not in countryCodes:
        typer.secho("Error: Country code is invalid. Please use the Alpha-2 code of the country you want. Codes can "
                    "be found here: https://www.iso.org/obp/ui.", bg=typer.colors.RED)
        exit()

    response = requests.patch(f"{host}/provider", json={
        "provider": {
            mapProviderDataKey(key): value
        }
    }, auth=BearerAuth(state['accessToken']))
    if response.status_code == 200:
        typer.secho("Done.", bg=typer.colors.GREEN, fg=typer.colors.BLACK)
    else:
        typer.secho("Error: ", bg=typer.colors.RED)
        print(response.json())


@app.command()
def get():
    response = requests.get(f"{host}/provider", auth=BearerAuth(state['accessToken']))
    provider = response.json()

    typer.secho(f"Provider Id: {provider['id']}")
    typer.secho(f"Business Name: {provider['businessName']}")
    typer.secho(f"Country: {provider['country']}")
    typer.secho(f"Website: {provider['website']}")
    typer.secho(f"Email: {provider['email']}")
    typer.secho(f"Contact Person: {provider['contactPerson']}")
    typer.secho(f"Address: {provider['address']}")


@app.callback()
def getAuthData():
    state['accessToken'] = getConfigFromFile('access_token')
    state['providerId'] = getConfigFromFile('provider_id')
    state['wallet'] = getConfigFromFile('eth_wallet')

    if state['accessToken'] is None or state['providerId'] is None:
        raise typer.Exit("Not logged in.")


if __name__ == "__main__":
    app()
