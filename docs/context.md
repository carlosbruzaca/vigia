# VigIA - Contexto do Projeto

## Visão Geral

**VigIA** é um bot do Telegram para vigilância financeira de PMEs brasileiras (especialmente em São Luís/MA).

- **Problema:** PMEs descobrem problemas de caixa tarde demais
- **Solução:** Bot que pergunta diariamente entrada/saída e alerta quando caixa vai acabar

## Stack Técnica

| Componente | Tecnologia |
|------------|------------|
| Backend | Python 3.11+ |
| API | FastAPI |
| Bot | python-telegram-bot |
| Banco | Supabase (PostgreSQL) |
| Agendamento | APScheduler |
| Deploy | Docker + Coolify (Hostinger VPS) |

## Arquitetura de Estados

```
new → onboarding → active → paused → blocked
```

## Tabelas do Banco (Supabase)

- `vigia_companies` - Empresas/clientes
- `vigia_users` - Usuários do Telegram
- `vigia_entries` - Lançamentos financeiros
- `vigia_receivables` - Contas a receber
- `vigia_subscriptions` - Assinaturas
- `vigia_message_logs` - Logs de mensagens
- `vigia_alerts` - Alertas enviados

## Credenciais Atuais

### Supabase
- **URL:** https://lalamefcxccturkgssmk.supabase.co
- **Chave anon:** eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxhbGFtZWZjeGNjdHVya2dzc21rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE0MjM3ODUsImV4cCI6MjA4Njk5OTc4NX0.slZjfNC0jeUSnl7_DpB6PWtYi7P7gCy7ud5beoQoE7E
- **Service role:** eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxhbGFtZWZjeGNjdHVya2dzc21rIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTQyMzc4NSwiZXhwIjoyMDg2OTk5Nzg1fQ.1NClJwvUoWbs_JZ32LFjwdwrTtDhgpVH_ZXYwI9GIuA

### Telegram
- **Bot Token:** your_telegram_bot_token_here (precisa ser configurado)

### VPS
- **Host:** Hostinger (gerenciado pelo Coolify)
- **URL do app:** A definir

## Estrutura de Arquivos

```
src/
├── main.py              # FastAPI + Telegram webhook
├── config.py            # Configurações
├── database.py          # Cliente Supabase
├── handlers/
│   ├── router.py        # Roteamento por estado
│   ├── onboarding.py    # Coleta dados iniciais
│   ├── operation.py     # Comandos /receita, /despesa
│   └── daily_report.py  # Relatório diário 7h
├── services/
│   ├── supabase.py      # Queries Supabase
│   ├── telegram.py      # Envio de mensagens
│   └── scheduler.py     # Agendamento
└── utils/
    ├── burn_rate.py     # Cálculos financeiros
    └── formatters.py    # Formatação de mensagens
```

## Comandos do Bot

- `/start` - Iniciar/cadastro
- `/receita <valor>` - Registrar faturamento
- `/despesa <valor>` - Registrar despesa
- `/relatorio` - Ver situação atual
- `/ajuda` - Ver comandos

## Status Atual

- Banco configurado (tabelas criadas, vazio)
- Código implementado
- Deploy em andamento (Coolify/Hostinger)
- Telegram erro precisa debugar
