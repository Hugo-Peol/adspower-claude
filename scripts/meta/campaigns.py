"""v1.0 - Criacao de campanhas padronizadas multi-conta.

Cria campanhas PAUSADAS em uma ou mais contas usando templates
e o sistema de tags para nomenclatura padronizada.

Todas as campanhas sao criadas PAUSADAS por seguranca.
"""

import json
import os
import time
import requests
from datetime import datetime
from naming import build_name, validate_tags, list_tags

ACCOUNTS_FILE = os.path.join(os.path.dirname(__file__), "accounts.json")
API_VERSION = "v21.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"

DELAY_BETWEEN_ACCOUNTS_SEC = 3


def load_accounts(account_filter=None):
    """Carrega contas do accounts.json.

    Args:
        account_filter: Nome ou lista de nomes para filtrar (None = todas)
    """
    if not os.path.exists(ACCOUNTS_FILE):
        print(f"ERRO: Arquivo {ACCOUNTS_FILE} nao encontrado.")
        print(f"Copie accounts.json.example para accounts.json e preencha seus dados.")
        return []

    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    accounts = data.get("contas", [])

    if account_filter:
        if isinstance(account_filter, str):
            account_filter = [account_filter]
        accounts = [a for a in accounts if a["nome"] in account_filter]

    return accounts


def _api_post(access_token, endpoint, params):
    params["access_token"] = access_token
    url = f"{BASE_URL}/{endpoint}"
    resp = requests.post(url, data=params, timeout=30)
    data = resp.json()
    if "error" in data:
        err = data["error"]
        raise RuntimeError(
            f"Meta API error {err.get('code', '?')}: {err.get('message', 'Unknown')}"
        )
    return data


def _api_get(access_token, endpoint, params=None):
    if params is None:
        params = {}
    params["access_token"] = access_token
    url = f"{BASE_URL}/{endpoint}"
    resp = requests.get(url, params=params, timeout=30)
    data = resp.json()
    if "error" in data:
        err = data["error"]
        raise RuntimeError(
            f"Meta API error {err.get('code', '?')}: {err.get('message', 'Unknown')}"
        )
    return data


OBJECTIVE_MAP = {
    "ASC": "OUTCOME_SALES",
    "MANUAL": "OUTCOME_TRAFFIC",
    "DCT": "OUTCOME_TRAFFIC",
}


def create_campaign_on_account(account, campaign_name, objective="OUTCOME_TRAFFIC",
                                bid_strategy="LOWEST_COST_WITHOUT_CAP",
                                daily_budget_cents=None, lifetime_budget_cents=None,
                                special_ad_categories=None):
    """Cria uma campanha PAUSADA em uma conta especifica."""
    params = {
        "name": campaign_name,
        "objective": objective,
        "status": "PAUSED",
        "bid_strategy": bid_strategy,
        "special_ad_categories": json.dumps(special_ad_categories or []),
    }

    if daily_budget_cents:
        params["daily_budget"] = str(daily_budget_cents)
    if lifetime_budget_cents:
        params["lifetime_budget"] = str(lifetime_budget_cents)

    ad_account_id = account["ad_account_id"]
    data = _api_post(account["access_token"], f"{ad_account_id}/campaigns", params)
    return data


def deploy_campaign(tags_config, accounts=None, daily_budget_cents=None,
                    lifetime_budget_cents=None, special_ad_categories=None, dry_run=False):
    """Cria uma campanha padronizada em uma ou mais contas.

    Args:
        tags_config: Dict com as tags da campanha:
            produto, orcamento, estrutura, ad_name, segmentacao,
            tipo_campanha, data, gestor, variacao
        accounts: Lista de nomes de conta (None = todas)
        daily_budget_cents: Orcamento diario em centavos (5000 = R$50)
        lifetime_budget_cents: Orcamento vitalicio em centavos
        special_ad_categories: Lista de categorias especiais (ex: ["HOUSING"])
        dry_run: Se True, apenas mostra o que seria criado sem executar
    """
    errors = validate_tags(**tags_config)
    if errors:
        print("\nERRO - Tags invalidas:")
        for e in errors:
            print(f"  - {e}")
        return {"created": [], "errors": errors}

    account_list = load_accounts(accounts)
    if not account_list:
        print("Nenhuma conta encontrada.")
        return {"created": [], "errors": ["Nenhuma conta encontrada"]}

    tipo = tags_config.get("tipo_campanha", "MANUAL")
    objective = OBJECTIVE_MAP.get(tipo, "OUTCOME_TRAFFIC")

    created = []
    deploy_errors = []

    print(f"\n{'='*70}")
    print(f"  DEPLOY DE CAMPANHA {'(DRY RUN)' if dry_run else ''}")
    print(f"{'='*70}")

    for i, account in enumerate(account_list):
        conta_tag = tags_config.get("conta") or account.get("tag", account["nome"])
        current_tags = {**tags_config, "conta": conta_tag}
        campaign_name = build_name(**{
            k: v for k, v in current_tags.items()
            if k in ("produto", "orcamento", "estrutura", "ad_name",
                     "segmentacao", "tipo_campanha", "data", "conta", "gestor", "variacao")
        })

        print(f"\n  Conta: {account['nome']} ({account['ad_account_id']})")
        print(f"  Nome:  {campaign_name}")
        print(f"  Objetivo: {objective}")
        if daily_budget_cents:
            print(f"  Orcamento: R$ {daily_budget_cents / 100:.2f}/dia")
        print(f"  Status: PAUSADA")

        if dry_run:
            print(f"  >> Dry run - nao criada")
            created.append({"account": account["nome"], "name": campaign_name, "dry_run": True})
            continue

        try:
            result = create_campaign_on_account(
                account, campaign_name, objective,
                daily_budget_cents=daily_budget_cents,
                lifetime_budget_cents=lifetime_budget_cents,
                special_ad_categories=special_ad_categories,
            )
            campaign_id = result.get("id", "?")
            print(f"  >> Criada! ID: {campaign_id}")
            created.append({
                "account": account["nome"],
                "name": campaign_name,
                "id": campaign_id,
            })
        except Exception as e:
            print(f"  >> ERRO: {e}")
            deploy_errors.append({"account": account["nome"], "error": str(e)})

        if i < len(account_list) - 1:
            print(f"  (aguardando {DELAY_BETWEEN_ACCOUNTS_SEC}s antes da proxima conta...)")
            time.sleep(DELAY_BETWEEN_ACCOUNTS_SEC)

    print(f"\n{'='*70}")
    print(f"  RESULTADO: {len(created)} criadas, {len(deploy_errors)} erros")
    print(f"{'='*70}\n")

    return {"created": created, "errors": deploy_errors}


def list_campaigns_on_account(account, status_filter=None, limit=25):
    """Lista campanhas de uma conta."""
    params = {
        "fields": "id,name,objective,status,daily_budget,lifetime_budget,created_time",
        "limit": limit,
    }
    if status_filter:
        params["filtering"] = json.dumps([{
            "field": "effective_status",
            "operator": "IN",
            "value": status_filter if isinstance(status_filter, list) else [status_filter],
        }])

    data = _api_get(account["access_token"], f"{account['ad_account_id']}/campaigns", params)
    return data.get("data", [])


def list_all_campaigns(accounts=None, status_filter=None, limit=25):
    """Lista campanhas de todas as contas."""
    account_list = load_accounts(accounts)

    print(f"\n{'='*80}")
    for account in account_list:
        print(f"\n  {account['nome']} ({account['ad_account_id']})")
        print(f"  {'-'*60}")

        try:
            campaigns = list_campaigns_on_account(account, status_filter, limit)
            if not campaigns:
                print(f"    Nenhuma campanha encontrada.")
                continue
            for c in campaigns:
                budget = c.get("daily_budget") or c.get("lifetime_budget") or "N/A"
                if budget != "N/A":
                    budget = f"R$ {int(budget) / 100:.2f}"
                print(f"    [{c['status']:8s}] {c['name']}")
                print(f"              ID: {c['id']} | Orcamento: {budget}")
        except Exception as e:
            print(f"    ERRO: {e}")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="v1.0 - Campanhas Multi-Conta com Tags")
    sub = parser.add_subparsers(dest="command")

    # Tags
    sub.add_parser("tags", help="Listar todas as tags disponiveis")

    # List
    lp = sub.add_parser("list", help="Listar campanhas de todas as contas")
    lp.add_argument("--contas", nargs="*", default=None, help="Filtrar por nomes de conta")
    lp.add_argument("--status", default=None, choices=["ACTIVE", "PAUSED", "ARCHIVED"])

    # Deploy
    dp = sub.add_parser("deploy", help="Criar campanha em uma ou mais contas")
    dp.add_argument("--produto", required=True, help="Tag do produto (ex: DS)")
    dp.add_argument("--orcamento", required=True, help="Tag do orcamento (ex: CBO)")
    dp.add_argument("--estrutura", required=True, help="Estrutura (ex: 1-3-1)")
    dp.add_argument("--ad-name", required=True, help="Nome do anuncio (ex: ADLAT23)")
    dp.add_argument("--segmentacao", required=True, nargs="+", help="Tag(s) de segmentacao")
    dp.add_argument("--tipo", required=True, help="Tipo de campanha (ex: ASC)")
    dp.add_argument("--data", default=None, help="Data DD-MM-AA (default: hoje)")
    dp.add_argument("--gestor", default=None, help="Nome do gestor")
    dp.add_argument("--variacao", default=None, help="Variacao (ex: Copy 4)")
    dp.add_argument("--contas", nargs="*", default=None, help="Contas alvo (default: todas)")
    dp.add_argument("--daily-budget", type=int, default=None, help="Centavos (5000 = R$50)")
    dp.add_argument("--lifetime-budget", type=int, default=None, help="Centavos")
    dp.add_argument("--dry-run", action="store_true", help="Simular sem criar")

    # Parse name
    pp = sub.add_parser("parse", help="Decompor nome de campanha existente")
    pp.add_argument("name")

    args = parser.parse_args()

    if args.command == "tags":
        list_tags()

    elif args.command == "list":
        list_all_campaigns(accounts=args.contas, status_filter=args.status)

    elif args.command == "deploy":
        tags_config = {
            "produto": args.produto,
            "orcamento": args.orcamento,
            "estrutura": args.estrutura,
            "ad_name": args.ad_name,
            "segmentacao": args.segmentacao,
            "tipo_campanha": args.tipo,
            "data": args.data,
            "gestor": args.gestor,
            "variacao": args.variacao,
        }
        deploy_campaign(
            tags_config,
            accounts=args.contas,
            daily_budget_cents=args.daily_budget,
            lifetime_budget_cents=args.lifetime_budget,
            dry_run=args.dry_run,
        )

    elif args.command == "parse":
        from naming import parse_name
        result = parse_name(args.name)
        print("\nTags encontradas:")
        for k, v in result.items():
            print(f"  {k}: {v}")

    else:
        parser.print_help()
