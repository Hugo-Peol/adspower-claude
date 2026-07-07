# Meta Ads Campaign Manager v1.0

Sistema de criacao padronizada de campanhas Meta Ads com tags e suporte multi-conta.

## SEGURANCA

- Campanhas sao SEMPRE criadas **PAUSADAS**
- Delay automatico entre contas para evitar padroes suspeitos
- Use `--dry-run` para simular antes de criar
- **Nunca** commite `accounts.json` com tokens reais

## Setup

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar contas

```bash
cd scripts/meta
cp accounts.json.example accounts.json
```

Edite `accounts.json` com os dados das suas contas:

```json
{
  "contas": [
    {
      "nome": "Conta Principal",
      "tag": "Conta01",
      "ad_account_id": "act_111111111",
      "access_token": "seu-token-aqui"
    }
  ]
}
```

Cada conta precisa de um token da Meta Marketing API com permissao `ads_management`.

## Uso

### Ver tags disponiveis

```bash
python campaigns.py tags
```

### Simular criacao (dry run)

```bash
python campaigns.py deploy \
  --produto DS \
  --orcamento CBO \
  --estrutura 1-3-1 \
  --ad-name "ADLAT23'" \
  --segmentacao ID TOPM \
  --tipo ASC \
  --gestor Hugo \
  --variacao "Copy 4" \
  --daily-budget 5000 \
  --dry-run
```

Resultado: `DS-CBO [1-3-1] | ADLAT23' [ID] [TOPM] [ASC] | 07-07-25 | Conta01 | Hugo - Copy 4`

### Criar campanha em todas as contas

```bash
python campaigns.py deploy \
  --produto DS \
  --orcamento CBO \
  --estrutura 1-3-1 \
  --ad-name "ADLAT23'" \
  --segmentacao ID TOPM \
  --tipo ASC \
  --gestor Hugo \
  --variacao "Copy 4" \
  --daily-budget 5000
```

### Criar em contas especificas

```bash
python campaigns.py deploy \
  --produto DS \
  --orcamento CBO \
  --estrutura 1-3-1 \
  --ad-name "ADLAT23'" \
  --segmentacao BROAD \
  --tipo MANUAL \
  --gestor Hugo \
  --contas "Conta Principal" "Conta Reserva" \
  --daily-budget 3000
```

### Decompor nome de campanha existente

```bash
python campaigns.py parse "DS-CBO [1-3-1] | ADLAT23' [ID] [TOPM] [ASC] | 02-09-25 | Conta06 | Hugo - Copy 4"
```

### Listar campanhas de todas as contas

```bash
python campaigns.py list
python campaigns.py list --status PAUSED
python campaigns.py list --contas "Conta Principal"
```

## Tags

As tags ficam em `tags.json`. Edite para adicionar novas:

| Campo | Exemplo | Descricao |
|-------|---------|-----------|
| produto | DS, EC, IF | Produto sendo anunciado |
| orcamento | CBO, ABO | Tipo de orcamento |
| estrutura | 1-3-1, 1-5-1 | Campanhas-conjuntos-anuncios |
| segmentacao | ID, LAL, TOPM, BROAD | Tipo de publico |
| tipo_campanha | ASC, MANUAL, DCT | Modo da campanha |
| conta | Conta01, Conta06 | Identificador da conta |
| gestor | Hugo | Responsavel |

## Formato do nome

```
{produto}-{orcamento} [{estrutura}] | {ad_name} [{segmentacao}] [{tipo}] | {data} | {conta} | {gestor} - {variacao}
```

## Estrutura

```
scripts/
  adspower_client.py             # Cliente AdsPower (gerenciamento de perfis)
  meta/
    accounts.json.example        # Modelo de configuracao de contas
    accounts.json                # Suas contas (NAO commitar)
    tags.json                    # Registro de tags
    naming.py                    # Gerador de nomes com tags
    campaigns.py                 # CLI principal - deploy multi-conta
    api_client.py                # Cliente base da API (uso futuro)
    config.py                    # Config via env vars (uso futuro)
    adsets.py                    # Ad sets (uso futuro)
    insights.py                  # Relatorios (uso futuro)
```

## Roadmap

- v1.0: Tags + criacao de campanhas pausadas multi-conta (atual)
- v1.1: Dashboard de relatorios multi-conta
- v1.2: Templates completos (campanha + ad sets + ads com uma tag)
- v1.3: Integracao com AdsPower para abrir perfil e revisar
