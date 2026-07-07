"""Gerador de nomes de campanha baseado em tags.

Formato padrao:
  {produto}-{orcamento} [{estrutura}] | {ad_name} [{segmentacao}] [{tipo_campanha}] | {data} | {conta} | {gestor} - {variacao}

Exemplo:
  DS-CBO [1-3-1] | ADLAT23' [ID] [TOPM] [ASC] | 02-09-25 | Conta06 | Hugo - Copy 4
"""

import json
import os
from datetime import datetime

TAGS_FILE = os.path.join(os.path.dirname(__file__), "tags.json")


def load_tags():
    with open(TAGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def list_tags(campo=None):
    """Mostra todas as tags ou as de um campo especifico."""
    tags = load_tags()

    campos = [campo] if campo else [k for k in tags if k != "_doc"]

    for c in campos:
        if c not in tags:
            print(f"Campo '{c}' nao encontrado.")
            continue
        info = tags[c]
        desc = info.get("_desc", "")
        print(f"\n  {c.upper()}" + (f" - {desc}" if desc else ""))
        print("  " + "-" * 50)
        for tag, significado in info.items():
            if tag == "_desc":
                continue
            print(f"    {tag:10s}  {significado}")

    return tags


def build_name(produto, orcamento, estrutura, ad_name, segmentacao, tipo_campanha,
               data=None, conta=None, gestor=None, variacao=None):
    """Monta o nome da campanha a partir das tags.

    Args:
        produto: Tag do produto (ex: "DS", "EC")
        orcamento: Tag do orcamento (ex: "CBO", "ABO")
        estrutura: Tag da estrutura (ex: "1-3-1")
        ad_name: Nome/codigo do anuncio (ex: "ADLAT23'")
        segmentacao: Tag(s) de segmentacao, string ou lista (ex: "ID" ou ["ID", "TOPM"])
        tipo_campanha: Tag do tipo (ex: "ASC", "MANUAL")
        data: Data no formato DD-MM-AA (default: hoje)
        conta: Tag da conta (ex: "Conta06")
        gestor: Nome do gestor (ex: "Hugo")
        variacao: Variacao do criativo (ex: "Copy 4")
    """
    if data is None:
        data = datetime.now().strftime("%d-%m-%y")

    if isinstance(segmentacao, list):
        seg_str = " ".join(f"[{s}]" for s in segmentacao)
    else:
        seg_str = f"[{segmentacao}]"

    parts = [
        f"{produto}-{orcamento} [{estrutura}]",
        f"{ad_name} {seg_str} [{tipo_campanha}]",
        data,
    ]

    if conta:
        parts.append(conta)
    if gestor:
        suffix = gestor
        if variacao:
            suffix += f" - {variacao}"
        parts.append(suffix)

    return " | ".join(parts)


def parse_name(name):
    """Decompoe um nome de campanha nas suas tags."""
    segments = [s.strip() for s in name.split("|")]
    result = {}

    if len(segments) >= 1:
        first = segments[0]
        if "-" in first.split("[")[0]:
            prefix = first.split("[")[0].strip()
            tag_parts = prefix.split("-")
            result["produto"] = tag_parts[0].strip()
            if len(tag_parts) > 1:
                result["orcamento"] = tag_parts[1].strip()

        import re
        brackets = re.findall(r'\[([^\]]+)\]', first)
        if brackets:
            result["estrutura"] = brackets[0]

    if len(segments) >= 2:
        second = segments[1].strip()
        import re
        brackets = re.findall(r'\[([^\]]+)\]', second)
        clean = re.sub(r'\[([^\]]+)\]', '', second).strip()
        if clean:
            result["ad_name"] = clean

        tags_data = load_tags()
        seg_tags = set(tags_data.get("segmentacao", {}).keys()) - {"_desc"}
        tipo_tags = set(tags_data.get("tipo_campanha", {}).keys()) - {"_desc"}

        result["segmentacao"] = [b for b in brackets if b in seg_tags]
        tipo = [b for b in brackets if b in tipo_tags]
        if tipo:
            result["tipo_campanha"] = tipo[0]

    if len(segments) >= 3:
        result["data"] = segments[2].strip()

    if len(segments) >= 4:
        result["conta"] = segments[3].strip()

    if len(segments) >= 5:
        last = segments[4].strip()
        if " - " in last:
            gestor, variacao = last.split(" - ", 1)
            result["gestor"] = gestor.strip()
            result["variacao"] = variacao.strip()
        else:
            result["gestor"] = last

    return result


def validate_tags(**kwargs):
    """Valida se as tags usadas existem no registro."""
    tags = load_tags()
    errors = []

    field_map = {
        "produto": "produto",
        "orcamento": "orcamento",
        "estrutura": "estrutura",
        "tipo_campanha": "tipo_campanha",
        "conta": "conta",
    }

    for param, campo in field_map.items():
        value = kwargs.get(param)
        if value and campo in tags:
            valid = set(tags[campo].keys()) - {"_desc"}
            if value not in valid:
                errors.append(f"Tag '{value}' nao encontrada em '{campo}'. Validas: {', '.join(sorted(valid))}")

    seg = kwargs.get("segmentacao", [])
    if isinstance(seg, str):
        seg = [seg]
    if seg and "segmentacao" in tags:
        valid_seg = set(tags["segmentacao"].keys()) - {"_desc"}
        for s in seg:
            if s not in valid_seg:
                errors.append(f"Segmentacao '{s}' invalida. Validas: {', '.join(sorted(valid_seg))}")

    return errors


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gerador de nomes de campanha")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("tags", help="Listar todas as tags")

    tp = sub.add_parser("tags-campo", help="Listar tags de um campo")
    tp.add_argument("campo")

    bp = sub.add_parser("build", help="Montar nome de campanha")
    bp.add_argument("--produto", required=True)
    bp.add_argument("--orcamento", required=True)
    bp.add_argument("--estrutura", required=True)
    bp.add_argument("--ad-name", required=True)
    bp.add_argument("--segmentacao", required=True, nargs="+")
    bp.add_argument("--tipo", required=True)
    bp.add_argument("--data", default=None)
    bp.add_argument("--conta", default=None)
    bp.add_argument("--gestor", default=None)
    bp.add_argument("--variacao", default=None)

    pp = sub.add_parser("parse", help="Decompor nome de campanha")
    pp.add_argument("name")

    args = parser.parse_args()

    if args.command == "tags":
        list_tags()
    elif args.command == "tags-campo":
        list_tags(args.campo)
    elif args.command == "build":
        errors = validate_tags(
            produto=args.produto, orcamento=args.orcamento,
            estrutura=args.estrutura, segmentacao=args.segmentacao,
            tipo_campanha=args.tipo, conta=args.conta,
        )
        if errors:
            print("ERROS:")
            for e in errors:
                print(f"  - {e}")
        else:
            name = build_name(
                args.produto, args.orcamento, args.estrutura, args.ad_name,
                args.segmentacao, args.tipo, args.data, args.conta,
                args.gestor, args.variacao,
            )
            print(f"\n  {name}\n")
    elif args.command == "parse":
        result = parse_name(args.name)
        print("\nTags encontradas:")
        for k, v in result.items():
            print(f"  {k}: {v}")
    else:
        parser.print_help()
