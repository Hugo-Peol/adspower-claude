# Setup do MCP Meta Ads + AdsPower

## O que voce precisa

1. **Node.js** instalado (para rodar o MCP via npx)
2. **Claude Code CLI** instalado na sua maquina (`npm install -g @anthropic-ai/claude-code`)
3. **Tokens** da Meta Marketing API para cada conta
4. **AdsPower** rodando (opcional, para isolamento de perfis)

## Passo a passo

### 1. Obter tokens da Meta

Para cada conta de anuncio:

1. Acesse https://developers.facebook.com
2. Crie/use um app do tipo "Business"
3. Adicione o produto "Marketing API"
4. Em Tools > Graph API Explorer, gere um token com permissoes:
   - `ads_management` (criar/editar campanhas)
   - `ads_read` (ler campanhas)
   - `read_insights` (metricas)
5. Anote o Ad Account ID (formato: `act_123456789`)

### 2. Configurar o Claude Code

Copie o arquivo de exemplo para a pasta de configuracao:

```bash
# Opcao A: configuracao do projeto
mkdir -p .claude
cp mcp-setup/claude-settings.json.example .claude/settings.json

# Opcao B: configuracao global
cp mcp-setup/claude-settings.json.example ~/.claude/settings.json
```

Edite o arquivo e substitua os tokens e IDs das suas contas.

### 3. Testar

```bash
# Abrir o Claude Code na pasta do projeto
claude

# Dentro do Claude, testar com linguagem natural:
> Liste as campanhas da conta 01
> Crie uma campanha pausada chamada "DS-CBO [1-3-1] | teste [ID] [ASC]" na conta 01
```

### 4. Usar com o sistema de tags

O sistema de tags (scripts/meta/naming.py) gera o nome da campanha.
Voce pode usar o MCP para criar a campanha com esse nome:

```bash
# Gerar o nome
cd scripts/meta
python naming.py build --produto DS --orcamento CBO --estrutura 1-3-1 \
  --ad-name "ADLAT23'" --segmentacao ID TOPM --tipo ASC \
  --gestor Hugo --variacao "Copy 4"

# Resultado: DS-CBO [1-3-1] | ADLAT23' [ID] [TOPM] [ASC] | 07-07-25 | Hugo - Copy 4

# Usar esse nome no Claude Code com MCP:
# > Crie uma campanha pausada com o nome "DS-CBO [1-3-1] | ADLAT23' [ID] [TOPM] [ASC] | 07-07-25 | Hugo - Copy 4" na conta 01
```

## Estrutura multi-conta

Cada conta Meta e configurada como um MCP server separado no Claude:

```
meta-ads-conta01  ->  Token A  ->  act_111
meta-ads-conta02  ->  Token B  ->  act_222
meta-ads-conta06  ->  Token C  ->  act_333
```

Quando voce pede algo ao Claude, especifique a conta:
- "Liste campanhas da **conta 01**"
- "Crie campanha X na **conta 06**"

## Com AdsPower (opcional)

Se voce usa AdsPower para isolamento de perfis, o MCP do AdsPower
tambem esta configurado. Use para:
- "Abra o perfil da conta 01" (abre navegador isolado)
- "Liste meus perfis do AdsPower"

O AdsPower NAO e necessario para a API. Use apenas quando precisar
acessar o Gerenciador de Anuncios manualmente.
