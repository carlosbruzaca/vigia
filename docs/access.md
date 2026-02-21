# Instruções de Acesso - VigIA

## Supabase

### URL
```
https://lalamefcxccturkgssmk.supabase.co
```

### Chaves de API
- **Anon Key (pública):** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxhbGFtZWZjeGNjdHVya2dzc21rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE0MjM3ODUsImV4cCI6MjA4Njk5OTc4NX0.slZjfNC0jeUSnl7_DpB6PWtYi7P7gCy7ud5beoQoE7E`
- **Service Role (secreta):** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxhbGFtZWZjeGNjdHVya2dzc21rIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTQyMzc4NSwiZXhwIjoyMDg2OTk5Nzg1fQ.1NClJwvUoWbs_JZ32LFjwdwrTtDhgpVH_ZXYwI9GIuA`

### Como testar via curl
```bash
# Listar empresas
curl "https://lalamefcxccturkgssmk.supabase.co/rest/v1/vigia_companies?select=*" \
  -H "apikey:ON_KEY"

# SUA_AN Listar usuários
curl "https://lalamefcxccturkgssmk.supabase.co/rest/v1/vigia_users?select=*" \
  -H "apikey: SUA_ANON_KEY"
```

### Como acessar pelo Python
```python
from supabase import create_client

url = "https://lalamefcxccturkgssmk.supabase.co"
key = "SUA_ANON_KEY"  # ou service_role para admin

client = create_client(url, key)
result = client.table("vigia_companies").select("*").execute()
```

---

## Telegram Bot

### Bot Token
**Configurado no .env:** `your_telegram_bot_token_here`

Para criar um novo bot:
1. Abra o @BotFather no Telegram
2. Digite `/newbot`
3. Siga as instruções e pegue o token

### Como obter o token atual
O token está na variável `TELEGRAM_BOT_TOKEN` no arquivo `.env` da VPS.

### Webhook
O bot usa webhook na VPS:
- **Endpoint:** `https://[URL-VPS]/webhook`
- **Método:** POST

### Como verificar se o bot está funcionando
1. Envie uma mensagem para o bot
2. Verifique os logs no Coolify

---

## VPS / Coolify

### Acesso
- **Plataforma:** Coolify (gerenciado na Hostinger)
- **URL do Coolify:** A verificar
- **App:** VigIA

### Verificar logs
1. Acesse o painel do Coolify
2. Selecione o app VigIA
3. Vá em "Logs" ou "Deployments"

### Variáveis de ambiente (.env)
```
SUPABASE_URL=https://lalamefcxccturkgssmk.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
TELEGRAM_BOT_TOKEN=seu_token_aqui
ENVIRONMENT=production
LOG_LEVEL=INFO
```

---

## Debug de Problemas

### Erro no Telegram
1. Verificar se o token está configurado corretamente
2. Verificar se o webhook está configurado: `https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
3. Verificar logs no Coolify

### Erro no Supabase
1. Testar a API com curl
2. Verificar as chaves no .env
3. Verificar se as tabelas existem

### Deploy não funciona
1. Verificar se o Dockerfile está correto
2. Verificar os logs de build no Coolify
3. Verificar variáveis de ambiente

---

## Atualizações

| Data | Alteração | Responsável |
|------|-----------|-------------|
| 2026-02-21 | Contexto inicial criado | opencode |
| 2026-02-21 | URLs e chaves documentadas | opencode |
