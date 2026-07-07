# AdsPower + Claude - Automacao de Perfis

Ferramentas para conectar e automatizar o AdsPower usando a API Local e o MCP Server.

## Pre-requisitos

- AdsPower instalado e rodando com a API Local ativada
- Python 3.8+ (para scripts de automacao)
- `pip install requests selenium` (dependencias)

## Configuracao Rapida

### 1. Verificar conexao com o AdsPower

```bash
# Usar a URL e API Key do painel de configuracoes do AdsPower
export ADSPOWER_API_URL="http://127.0.0.1:50325"
export ADSPOWER_API_KEY="sua-api-key-aqui"

python scripts/adspower_client.py status
```

### 2. Listar e gerenciar perfis

```bash
python scripts/adspower_client.py list
python scripts/adspower_client.py open <user_id>
python scripts/adspower_client.py close <user_id>
python scripts/adspower_client.py create "Meu Perfil"
```

### 3. Automacao com Selenium

```bash
pip install selenium
python scripts/example_automation.py
```

## Conectar via MCP Server (Claude Code CLI / Claude Desktop)

O AdsPower oferece um MCP Server que permite controlar perfis diretamente pelo Claude usando linguagem natural.

### Claude Code CLI

Adicione ao `.claude/settings.json` do projeto ou `~/.claude/settings.json` global:

```json
{
  "mcpServers": {
    "adspower-local-api": {
      "command": "npx",
      "args": [
        "-y",
        "local-api-mcp-typescript",
        "--base-url", "http://127.0.0.1:50325"
      ]
    }
  }
}
```

### Claude Desktop

Adicione ao arquivo de configuracao (`claude_desktop_config.json`):

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "adspower-local-api": {
      "command": "npx",
      "args": [
        "-y",
        "local-api-mcp-typescript",
        "--base-url", "http://127.0.0.1:50325"
      ]
    }
  }
}
```

Apos configurar, reinicie o Claude e voce podera usar comandos como:
- "Liste meus perfis do AdsPower"
- "Abra o perfil X"
- "Crie um novo perfil chamado Y"

## Estrutura

```
scripts/
  adspower_client.py      # Cliente da API Local (CLI + biblioteca)
  example_automation.py   # Exemplo de automacao com Selenium
```

## Referencia da API

| Comando | Descricao |
|---------|-----------|
| `status` | Verifica conexao com a API |
| `list` | Lista perfis |
| `groups` | Lista grupos |
| `open <id>` | Abre perfil no navegador |
| `close <id>` | Fecha perfil |
| `check <id>` | Verifica se perfil esta ativo |
| `create <nome>` | Cria novo perfil |
| `delete <id>` | Deleta perfil(s) |
