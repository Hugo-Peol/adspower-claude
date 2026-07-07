"""Gerenciamento de conjuntos de anuncios (Ad Sets).

Permite criar ad sets padronizados com segmentacao predefinida.

SEGURANCA: Conjuntos sao criados PAUSADOS. Ative manualmente apos revisar.
"""

import json
from api_client import get, post
from config import AD_ACCOUNT_ID


TARGETING_TEMPLATES = {
    "brasil_amplo": {
        "geo_locations": {"countries": ["BR"]},
        "age_min": 18,
        "age_max": 65,
    },
    "brasil_jovem": {
        "geo_locations": {"countries": ["BR"]},
        "age_min": 18,
        "age_max": 35,
    },
    "brasil_adulto": {
        "geo_locations": {"countries": ["BR"]},
        "age_min": 25,
        "age_max": 55,
    },
    "sp_rj": {
        "geo_locations": {
            "regions": [
                {"key": "3847", "name": "Sao Paulo", "country": "BR"},
                {"key": "3846", "name": "Rio de Janeiro", "country": "BR"},
            ]
        },
        "age_min": 18,
        "age_max": 65,
    },
}


def list_adsets(campaign_id=None, status_filter=None, limit=25):
    """Lista conjuntos de anuncios."""
    endpoint = f"{campaign_id}/adsets" if campaign_id else f"{AD_ACCOUNT_ID}/adsets"
    params = {
        "fields": "id,name,status,daily_budget,lifetime_budget,targeting,optimization_goal,bid_amount",
        "limit": limit,
    }
    if status_filter:
        params["filtering"] = json.dumps([{
            "field": "effective_status",
            "operator": "IN",
            "value": [status_filter] if isinstance(status_filter, str) else status_filter,
        }])

    data = get(endpoint, params)
    adsets = data.get("data", [])

    print(f"\nConjuntos de anuncios: {len(adsets)}")
    for a in adsets:
        budget = a.get("daily_budget") or a.get("lifetime_budget") or "N/A"
        if budget != "N/A":
            budget = f"R$ {int(budget) / 100:.2f}"
        print(f"  [{a['status']:8s}] {a['name']} (ID: {a['id']}) | Orcamento: {budget}")
    return adsets


def create_adset(name, campaign_id, targeting_template, daily_budget_cents,
                 optimization_goal="LINK_CLICKS", billing_event="IMPRESSIONS"):
    """Cria um conjunto de anuncios padronizado.

    Args:
        name: Nome do ad set
        campaign_id: ID da campanha pai
        targeting_template: Nome do template de segmentacao (ver TARGETING_TEMPLATES)
        daily_budget_cents: Orcamento diario em centavos
        optimization_goal: LINK_CLICKS, IMPRESSIONS, REACH, CONVERSIONS, LANDING_PAGE_VIEWS
        billing_event: IMPRESSIONS ou LINK_CLICKS
    """
    if targeting_template not in TARGETING_TEMPLATES:
        available = ", ".join(TARGETING_TEMPLATES.keys())
        raise ValueError(f"Template '{targeting_template}' nao encontrado. Disponiveis: {available}")

    targeting = TARGETING_TEMPLATES[targeting_template]

    params = {
        "name": name,
        "campaign_id": campaign_id,
        "daily_budget": str(daily_budget_cents),
        "targeting": json.dumps(targeting),
        "optimization_goal": optimization_goal,
        "billing_event": billing_event,
        "status": "PAUSED",
    }

    print(f"\nCriando ad set: {name}")
    print(f"  Campanha: {campaign_id}")
    print(f"  Segmentacao: {targeting_template}")
    print(f"  Orcamento: R$ {daily_budget_cents / 100:.2f}/dia")
    print(f"  Status: PAUSADO (por seguranca)")

    data = post(f"{AD_ACCOUNT_ID}/adsets", params=params)
    print(f"  Ad set criado! ID: {data.get('id', '?')}")
    return data


def list_targeting_templates():
    """Mostra templates de segmentacao disponiveis."""
    print("\nTemplates de segmentacao:")
    print("-" * 60)
    for name, config in TARGETING_TEMPLATES.items():
        locations = config.get("geo_locations", {})
        countries = locations.get("countries", [])
        regions = [r["name"] for r in locations.get("regions", [])]
        loc_str = ", ".join(countries + regions)
        print(f"  {name}")
        print(f"    Local: {loc_str}")
        print(f"    Idade: {config.get('age_min', '?')}-{config.get('age_max', '?')}")
        print()
    return TARGETING_TEMPLATES


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gerenciador de Ad Sets")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("targeting", help="Listar templates de segmentacao")

    lp = sub.add_parser("list", help="Listar ad sets")
    lp.add_argument("--campaign-id", default=None)

    cp = sub.add_parser("create", help="Criar ad set")
    cp.add_argument("name")
    cp.add_argument("--campaign-id", required=True)
    cp.add_argument("--targeting", required=True, choices=list(TARGETING_TEMPLATES.keys()))
    cp.add_argument("--daily-budget", type=int, required=True, help="Centavos (5000 = R$50)")
    cp.add_argument("--goal", default="LINK_CLICKS",
                     choices=["LINK_CLICKS", "IMPRESSIONS", "REACH", "CONVERSIONS", "LANDING_PAGE_VIEWS"])

    args = parser.parse_args()

    if args.command == "targeting":
        list_targeting_templates()
    elif args.command == "list":
        list_adsets(campaign_id=args.campaign_id)
    elif args.command == "create":
        create_adset(args.name, args.campaign_id, args.targeting, args.daily_budget, args.goal)
    else:
        parser.print_help()
