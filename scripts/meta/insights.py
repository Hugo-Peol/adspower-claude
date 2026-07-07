"""Analise de campanhas Meta Ads.

Consulta metricas de performance das campanhas usando a Marketing API.
Gera relatorios em CSV e resumos no terminal.

SEGURANCA: Apenas leitura de dados. Nenhuma acao e executada nas contas.
"""

import csv
import json
from datetime import datetime, timedelta
from api_client import get
from config import AD_ACCOUNT_ID


DEFAULT_FIELDS = [
    "campaign_name",
    "campaign_id",
    "impressions",
    "reach",
    "clicks",
    "cpc",
    "cpm",
    "ctr",
    "spend",
    "actions",
    "cost_per_action_type",
    "frequency",
]


def get_campaign_insights(campaign_id=None, date_preset="last_7d", fields=None, breakdowns=None):
    """Obtem metricas de uma campanha ou de toda a conta.

    Args:
        campaign_id: ID da campanha (None = toda a conta)
        date_preset: Periodo (last_7d, last_30d, last_90d, today, yesterday, this_month, last_month)
        fields: Lista de campos (None = campos padrao)
        breakdowns: Segmentacao (age, gender, country, publisher_platform, device_platform)
    """
    if fields is None:
        fields = DEFAULT_FIELDS

    endpoint = f"{campaign_id}/insights" if campaign_id else f"{AD_ACCOUNT_ID}/insights"
    params = {
        "fields": ",".join(fields),
        "date_preset": date_preset,
        "level": "campaign",
    }
    if breakdowns:
        params["breakdowns"] = ",".join(breakdowns) if isinstance(breakdowns, list) else breakdowns

    data = get(endpoint, params)
    results = data.get("data", [])

    if not results:
        print("Nenhum dado encontrado para o periodo selecionado.")
        return results

    print(f"\nRelatorio de Performance ({date_preset})")
    print("=" * 100)

    for r in results:
        spend = float(r.get("spend", 0))
        impressions = int(r.get("impressions", 0))
        clicks = int(r.get("clicks", 0))
        ctr = float(r.get("ctr", 0))
        cpc = float(r.get("cpc", 0))
        cpm = float(r.get("cpm", 0))
        reach = int(r.get("reach", 0))
        frequency = float(r.get("frequency", 0))

        print(f"\n  Campanha: {r.get('campaign_name', 'N/A')}")
        print(f"  ID: {r.get('campaign_id', 'N/A')}")
        print(f"  Gasto: R$ {spend:.2f}")
        print(f"  Impressoes: {impressions:,} | Alcance: {reach:,} | Frequencia: {frequency:.1f}")
        print(f"  Cliques: {clicks:,} | CTR: {ctr:.2f}% | CPC: R$ {cpc:.2f} | CPM: R$ {cpm:.2f}")

        actions = r.get("actions", [])
        costs = r.get("cost_per_action_type", [])
        cost_map = {c["action_type"]: float(c["value"]) for c in costs} if costs else {}

        if actions:
            print(f"  Acoes:")
            for a in actions:
                action_type = a["action_type"]
                value = int(a["value"])
                cost = cost_map.get(action_type)
                cost_str = f" | Custo: R$ {cost:.2f}" if cost else ""
                print(f"    - {action_type}: {value}{cost_str}")

    print("\n" + "=" * 100)
    return results


def get_account_summary(date_preset="last_7d"):
    """Resumo geral da conta."""
    fields = ["impressions", "reach", "clicks", "spend", "cpc", "cpm", "ctr", "actions"]
    data = get(f"{AD_ACCOUNT_ID}/insights", {
        "fields": ",".join(fields),
        "date_preset": date_preset,
    })
    results = data.get("data", [])

    if not results:
        print("Nenhum dado encontrado.")
        return None

    r = results[0]
    spend = float(r.get("spend", 0))
    impressions = int(r.get("impressions", 0))
    clicks = int(r.get("clicks", 0))

    print(f"\nResumo da Conta ({date_preset})")
    print("=" * 60)
    print(f"  Gasto total: R$ {spend:.2f}")
    print(f"  Impressoes: {impressions:,}")
    print(f"  Cliques: {clicks:,}")
    print(f"  CTR: {float(r.get('ctr', 0)):.2f}%")
    print(f"  CPC medio: R$ {float(r.get('cpc', 0)):.2f}")
    print(f"  CPM medio: R$ {float(r.get('cpm', 0)):.2f}")
    print("=" * 60)
    return r


def compare_campaigns(date_preset="last_7d", sort_by="spend", limit=10):
    """Compara todas as campanhas ativas lado a lado."""
    fields = [
        "campaign_name", "campaign_id",
        "spend", "impressions", "clicks", "ctr", "cpc", "cpm",
        "reach", "frequency", "actions", "cost_per_action_type",
    ]
    data = get(f"{AD_ACCOUNT_ID}/insights", {
        "fields": ",".join(fields),
        "date_preset": date_preset,
        "level": "campaign",
        "sort": f"{sort_by}_descending",
        "limit": limit,
    })
    results = data.get("data", [])

    if not results:
        print("Nenhum dado encontrado.")
        return results

    print(f"\nComparativo de Campanhas ({date_preset}) - Top {limit} por {sort_by}")
    print("=" * 120)
    print(f"  {'Campanha':<40} {'Gasto':>10} {'Impress.':>10} {'Cliques':>8} {'CTR':>7} {'CPC':>8} {'CPM':>8}")
    print("-" * 120)

    for r in results:
        name = r.get("campaign_name", "N/A")[:38]
        print(
            f"  {name:<40} "
            f"R${float(r.get('spend', 0)):>8.2f} "
            f"{int(r.get('impressions', 0)):>10,} "
            f"{int(r.get('clicks', 0)):>8,} "
            f"{float(r.get('ctr', 0)):>6.2f}% "
            f"R${float(r.get('cpc', 0)):>6.2f} "
            f"R${float(r.get('cpm', 0)):>6.2f}"
        )

    print("=" * 120)
    return results


def export_csv(date_preset="last_30d", output_file="relatorio_campanhas.csv"):
    """Exporta relatorio de campanhas para CSV."""
    fields = [
        "campaign_name", "campaign_id",
        "spend", "impressions", "reach", "clicks",
        "ctr", "cpc", "cpm", "frequency",
    ]
    data = get(f"{AD_ACCOUNT_ID}/insights", {
        "fields": ",".join(fields),
        "date_preset": date_preset,
        "level": "campaign",
        "limit": 500,
    })
    results = data.get("data", [])

    if not results:
        print("Nenhum dado para exportar.")
        return None

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields + ["date_start", "date_stop"])
        writer.writeheader()
        for r in results:
            row = {k: r.get(k, "") for k in fields + ["date_start", "date_stop"]}
            writer.writerow(row)

    print(f"Relatorio exportado: {output_file} ({len(results)} campanhas)")
    return output_file


def alert_high_spend(daily_limit_cents=10000, date_preset="today"):
    """Alerta campanhas que ultrapassaram um limite de gasto diario.

    Args:
        daily_limit_cents: Limite em centavos (10000 = R$100)
    """
    fields = ["campaign_name", "campaign_id", "spend"]
    data = get(f"{AD_ACCOUNT_ID}/insights", {
        "fields": ",".join(fields),
        "date_preset": date_preset,
        "level": "campaign",
        "limit": 100,
    })
    results = data.get("data", [])
    limit_reais = daily_limit_cents / 100

    alerts = []
    for r in results:
        spend = float(r.get("spend", 0))
        if spend >= limit_reais:
            alerts.append(r)
            print(f"  ALERTA: {r['campaign_name']} gastou R$ {spend:.2f} (limite: R$ {limit_reais:.2f})")

    if not alerts:
        print(f"Nenhuma campanha ultrapassou R$ {limit_reais:.2f} hoje.")

    return alerts


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analise de Campanhas Meta")
    sub = parser.add_subparsers(dest="command")

    sp = sub.add_parser("summary", help="Resumo geral da conta")
    sp.add_argument("--period", default="last_7d")

    ip = sub.add_parser("insights", help="Metricas de campanha")
    ip.add_argument("--campaign-id", default=None)
    ip.add_argument("--period", default="last_7d")
    ip.add_argument("--breakdown", default=None)

    cp = sub.add_parser("compare", help="Comparar campanhas")
    cp.add_argument("--period", default="last_7d")
    cp.add_argument("--sort", default="spend")
    cp.add_argument("--limit", type=int, default=10)

    ep = sub.add_parser("export", help="Exportar CSV")
    ep.add_argument("--period", default="last_30d")
    ep.add_argument("--output", default="relatorio_campanhas.csv")

    ap = sub.add_parser("alerts", help="Alertas de gasto")
    ap.add_argument("--limit", type=int, default=10000, help="Limite em centavos (10000 = R$100)")

    args = parser.parse_args()

    if args.command == "summary":
        get_account_summary(args.period)
    elif args.command == "insights":
        get_campaign_insights(args.campaign_id, args.period,
                              breakdowns=args.breakdown.split(",") if args.breakdown else None)
    elif args.command == "compare":
        compare_campaigns(args.period, args.sort, args.limit)
    elif args.command == "export":
        export_csv(args.period, args.output)
    elif args.command == "alerts":
        alert_high_spend(args.limit)
    else:
        parser.print_help()
