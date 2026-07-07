"""Gerenciamento de campanhas Meta Ads.

Permite criar campanhas padronizadas a partir de templates,
listar campanhas existentes e duplicar campanhas.

SEGURANCA: Este script usa a Marketing API oficial da Meta.
Nao viola termos de uso e nao causa risco para suas contas.
"""

import json
from api_client import get, post, delete
from config import AD_ACCOUNT_ID


CAMPAIGN_TEMPLATES = {
    "conversao_trafego": {
        "objective": "OUTCOME_TRAFFIC",
        "status": "PAUSED",
        "special_ad_categories": [],
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
    },
    "conversao_vendas": {
        "objective": "OUTCOME_SALES",
        "status": "PAUSED",
        "special_ad_categories": [],
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
    },
    "engajamento": {
        "objective": "OUTCOME_ENGAGEMENT",
        "status": "PAUSED",
        "special_ad_categories": [],
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
    },
    "leads": {
        "objective": "OUTCOME_LEADS",
        "status": "PAUSED",
        "special_ad_categories": [],
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
    },
    "awareness": {
        "objective": "OUTCOME_AWARENESS",
        "status": "PAUSED",
        "special_ad_categories": [],
        "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
    },
}


def list_campaigns(status_filter=None, limit=25):
    """Lista campanhas da conta."""
    params = {
        "fields": "id,name,objective,status,daily_budget,lifetime_budget,bid_strategy,created_time",
        "limit": limit,
    }
    if status_filter:
        params["filtering"] = json.dumps([{
            "field": "effective_status",
            "operator": "IN",
            "value": status_filter if isinstance(status_filter, list) else [status_filter],
        }])

    data = get(f"{AD_ACCOUNT_ID}/campaigns", params)
    campaigns = data.get("data", [])

    print(f"\nCampanhas encontradas: {len(campaigns)}")
    print("-" * 80)
    for c in campaigns:
        budget = c.get("daily_budget") or c.get("lifetime_budget") or "N/A"
        if budget != "N/A":
            budget = f"R$ {int(budget) / 100:.2f}"
        print(f"  [{c['status']:8s}] {c['name']}")
        print(f"            ID: {c['id']} | Objetivo: {c['objective']} | Orcamento: {budget}")
    print("-" * 80)
    return campaigns


def create_campaign(name, template_name, daily_budget_cents=None, lifetime_budget_cents=None):
    """Cria uma campanha a partir de um template padronizado.

    IMPORTANTE: Campanhas sao criadas PAUSADAS por seguranca.
    Ative manualmente apos revisar no Gerenciador de Anuncios.

    Args:
        name: Nome da campanha
        template_name: Nome do template (ver CAMPAIGN_TEMPLATES)
        daily_budget_cents: Orcamento diario em centavos (ex: 5000 = R$50)
        lifetime_budget_cents: Orcamento vitalicio em centavos
    """
    if template_name not in CAMPAIGN_TEMPLATES:
        available = ", ".join(CAMPAIGN_TEMPLATES.keys())
        raise ValueError(f"Template '{template_name}' nao encontrado. Disponiveis: {available}")

    template = CAMPAIGN_TEMPLATES[template_name].copy()
    template["name"] = name

    if daily_budget_cents:
        template["daily_budget"] = str(daily_budget_cents)
    if lifetime_budget_cents:
        template["lifetime_budget"] = str(lifetime_budget_cents)

    print(f"\nCriando campanha: {name}")
    print(f"  Template: {template_name}")
    print(f"  Objetivo: {template['objective']}")
    print(f"  Status: PAUSADA (por seguranca)")

    data = post(f"{AD_ACCOUNT_ID}/campaigns", params=template)
    campaign_id = data.get("id", "")
    print(f"  Campanha criada com sucesso! ID: {campaign_id}")
    print(f"  AVISO: Campanha criada PAUSADA. Ative no Gerenciador de Anuncios apos revisar.")
    return data


def create_campaigns_batch(campaigns_config):
    """Cria varias campanhas de uma vez.

    Args:
        campaigns_config: Lista de dicts com keys: name, template, daily_budget_cents

    Exemplo:
        create_campaigns_batch([
            {"name": "Vendas - Produto A", "template": "conversao_vendas", "daily_budget_cents": 5000},
            {"name": "Vendas - Produto B", "template": "conversao_vendas", "daily_budget_cents": 3000},
            {"name": "Leads - Landing Page", "template": "leads", "daily_budget_cents": 2000},
        ])
    """
    print(f"\nCriando {len(campaigns_config)} campanhas em lote...")
    print("=" * 80)

    created = []
    errors = []

    for i, config in enumerate(campaigns_config, 1):
        try:
            result = create_campaign(
                name=config["name"],
                template_name=config["template"],
                daily_budget_cents=config.get("daily_budget_cents"),
                lifetime_budget_cents=config.get("lifetime_budget_cents"),
            )
            created.append(result)
        except Exception as e:
            print(f"  ERRO na campanha '{config.get('name', '?')}': {e}")
            errors.append({"config": config, "error": str(e)})

    print("=" * 80)
    print(f"Resultado: {len(created)} criadas, {len(errors)} erros")
    if errors:
        print("Campanhas com erro:")
        for e in errors:
            print(f"  - {e['config'].get('name', '?')}: {e['error']}")

    return {"created": created, "errors": errors}


def pause_campaign(campaign_id):
    """Pausa uma campanha."""
    data = post(campaign_id, params={"status": "PAUSED"})
    print(f"Campanha {campaign_id} pausada.")
    return data


def list_templates():
    """Mostra os templates disponiveis."""
    print("\nTemplates de campanha disponiveis:")
    print("-" * 60)
    for name, config in CAMPAIGN_TEMPLATES.items():
        print(f"  {name}")
        print(f"    Objetivo: {config['objective']}")
        print(f"    Estrategia de lance: {config['bid_strategy']}")
        print()
    return CAMPAIGN_TEMPLATES


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gerenciador de Campanhas Meta")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("templates", help="Listar templates disponiveis")

    lp = sub.add_parser("list", help="Listar campanhas")
    lp.add_argument("--status", choices=["ACTIVE", "PAUSED", "ARCHIVED"], default=None)
    lp.add_argument("--limit", type=int, default=25)

    cp = sub.add_parser("create", help="Criar campanha")
    cp.add_argument("name", help="Nome da campanha")
    cp.add_argument("--template", required=True, choices=list(CAMPAIGN_TEMPLATES.keys()))
    cp.add_argument("--daily-budget", type=int, help="Orcamento diario em centavos (5000 = R$50)")

    pp = sub.add_parser("pause", help="Pausar campanha")
    pp.add_argument("campaign_id")

    args = parser.parse_args()

    if args.command == "templates":
        list_templates()
    elif args.command == "list":
        list_campaigns(status_filter=args.status, limit=args.limit)
    elif args.command == "create":
        create_campaign(args.name, args.template, daily_budget_cents=args.daily_budget)
    elif args.command == "pause":
        pause_campaign(args.campaign_id)
    else:
        parser.print_help()
