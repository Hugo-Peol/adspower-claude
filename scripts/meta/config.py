"""Configuracao da Meta Marketing API.

Para obter seu Access Token:
1. Acesse https://developers.facebook.com
2. Crie um app do tipo "Business"
3. Adicione o produto "Marketing API"
4. Gere um token com as permissoes: ads_management, ads_read, read_insights

IMPORTANTE: Nunca commite seu token real. Use variaveis de ambiente.
"""

import os

ACCESS_TOKEN = os.environ.get("META_ACCESS_TOKEN", "")
AD_ACCOUNT_ID = os.environ.get("META_AD_ACCOUNT_ID", "")  # formato: act_123456789
API_VERSION = "v21.0"
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"

if not ACCESS_TOKEN:
    print("AVISO: META_ACCESS_TOKEN nao definido. Defina com:")
    print('  export META_ACCESS_TOKEN="seu-token-aqui"')

if not AD_ACCOUNT_ID:
    print("AVISO: META_AD_ACCOUNT_ID nao definido. Defina com:")
    print('  export META_AD_ACCOUNT_ID="act_123456789"')
