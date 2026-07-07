"""Cliente base para a Meta Marketing API."""

import requests
from config import ACCESS_TOKEN, AD_ACCOUNT_ID, BASE_URL


def _request(method, endpoint, params=None, json_data=None):
    if params is None:
        params = {}
    params["access_token"] = ACCESS_TOKEN

    url = f"{BASE_URL}/{endpoint}"
    resp = requests.request(method, url, params=params, json=json_data, timeout=30)

    data = resp.json()
    if "error" in data:
        err = data["error"]
        raise RuntimeError(
            f"Meta API error {err.get('code', '?')}: {err.get('message', 'Unknown')} "
            f"(type: {err.get('type', '?')})"
        )
    return data


def get(endpoint, params=None):
    return _request("GET", endpoint, params=params)


def post(endpoint, params=None, json_data=None):
    return _request("POST", endpoint, params=params, json_data=json_data)


def delete(endpoint, params=None):
    return _request("DELETE", endpoint, params=params)


def get_ad_accounts():
    """Lista as contas de anuncio acessiveis."""
    data = get("me/adaccounts", {"fields": "id,name,account_status,currency,timezone_name"})
    accounts = data.get("data", [])
    print(f"Contas de anuncio encontradas: {len(accounts)}")
    for acc in accounts:
        status_map = {1: "ATIVA", 2: "DESATIVADA", 3: "NAO CONFIRMADA", 7: "PENDENTE"}
        status = status_map.get(acc.get("account_status"), "DESCONHECIDO")
        print(f"  - {acc.get('name', 'Sem nome')} ({acc['id']}) [{status}]")
    return accounts
