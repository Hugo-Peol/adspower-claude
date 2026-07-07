# AdsPower + Meta Ads - Gerenciamento de Campanhas

Ferramentas para gerenciar perfis AdsPower e campanhas Meta Ads de forma padronizada e segura.

## IMPORTANTE - Seguranca das Contas

- Campanhas sao SEMPRE criadas **PAUSADAS** - ative manualmente apos revisar
- Scripts de analise sao **somente leitura** - nao modificam nada nas contas
- Use a **Marketing API oficial** da Meta (nao automacao de UI)
- **Nunca** automatize acoes dentro do Facebook/Instagram (curtir, postar, etc.)
- **Nunca** commite tokens ou API keys - use variaveis de ambiente

## Pre-requisitos

- AdsPower instalado com API Local ativada (para gerenciamento de perfis)
- Python 3.8+
- Token da Meta Marketing API (ver setup abaixo)
- `pip install -r requirements.txt`

## Setup

### 1. Variaveis de ambiente

```bash
# AdsPower
export ADSPOWER_API_URL="http://127.0.0.1:50325"
export ADSPOWER_API_KEY="sua-api-key"

# Meta Marketing API
export META_ACCESS_TOKEN="seu-token-aqui"
export META_AD_ACCOUNT_ID="act_123456789"
```

### 2. Obter token da Meta Marketing API

1. Acesse https://developers.facebook.com
2. Crie um app do tipo "Business"
3. Adicione o produto "Marketing API"
4. Gere um token com permissoes: `ads_management`, `ads_read`, `read_insights`

## Uso - Campanhas Meta

### Listar campanhas

```bash
cd scripts/meta
python campaigns.py list
python campaigns.py list --status ACTIVE
```

### Templates de campanha disponiveis

```bash
python campaigns.py templates
```

Templates: `conversao_trafego`, `conversao_vendas`, `engajamento`, `leads`, `awareness`

### Criar campanha padronizada

```bash
# Campanha criada PAUSADA por seguranca
python campaigns.py create "Vendas - Produto X" --template conversao_vendas --daily-budget 5000
```

### Conjuntos de anuncios (Ad Sets)

```bash
python adsets.py targeting           # Ver templates de segmentacao
python adsets.py list                # Listar ad sets
python adsets.py create "Publico BR" --campaign-id 123 --targeting brasil_amplo --daily-budget 3000
```

## Uso - Analise de Campanhas

### Resumo da conta

```bash
cd scripts/meta
python insights.py summary --period last_7d
```

### Comparar campanhas

```bash
python insights.py compare --period last_30d --sort spend
```

### Exportar relatorio CSV

```bash
python insights.py export --period last_30d --output relatorio.csv
```

### Alertas de gasto

```bash
python insights.py alerts --limit 10000  # Alerta acima de R$100/dia
```

### Insights detalhados

```bash
python insights.py insights --period last_7d
python insights.py insights --campaign-id 123456 --breakdown age,gender
```

## Uso - Perfis AdsPower

```bash
python scripts/adspower_client.py status
python scripts/adspower_client.py list
python scripts/adspower_client.py open <user_id>
python scripts/adspower_client.py close <user_id>
```

## Conectar via MCP Server (Claude Code local)

O AdsPower oferece um MCP Server para controle por linguagem natural.
**Requer Claude Code CLI rodando na sua maquina local.**

Adicione ao `.claude/settings.json` ou `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "adspower-local-api": {
      "command": "npx",
      "args": ["-y", "local-api-mcp-typescript", "--base-url", "http://127.0.0.1:50325"]
    }
  }
}
```

## Estrutura

```
scripts/
  adspower_client.py        # Cliente AdsPower Local API
  meta/
    config.py               # Configuracao da Meta API
    api_client.py            # Cliente base da Marketing API
    campaigns.py             # Criar/listar campanhas com templates
    adsets.py                # Criar/listar ad sets com segmentacao
    insights.py              # Analise e relatorios de performance
```
