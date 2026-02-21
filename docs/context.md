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

## Fluxo do Usuário

1. **new**: Usuário envia qualquer mensagem → recebe mensagem de boas-vindas
2. **new + /start**: Muda para onboarding e começa perguntas
3. **onboarding**: Coleta custo fixo → % variável → caixa mínimo
4. **active**: Usuário pode usar /receita, /despesa, /relatorio, /ajuda

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
- **Anon Key:** eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxhbGFtZWZjeGNjdHVya2dzc21rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE0MjM3ODUsImV4cCI6MjA4Njk5OTc4NX0.slZjfNC0jeUSnl7_DpB6PWtYi7P7gCy7ud5beoQoE7E
- **Service Role:** eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxhbGFtZWZjeGNjdHVya2dzc21rIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTQyMzc4NSwiZXhwIjoyMDg2OTk5Nzg1fQ.1NClJwvUoWbs_JZ32LFjwdwrTtDhgpVH_ZXYwI9GIuA

### Telegram
- **Bot Token:** 8578648583:AAEecREdgPw89RnUeOrMORZs73TfUsZCm00

### VPS
- **Host:** Hostinger (gerenciado pelo Coolify)

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
│   └── daily_report.py # Relatório diário 7h
├── services/
│   ├── supabase.py     # Queries Supabase
│   ├── telegram.py     # Envio de mensagens
│   └── scheduler.py    # Agendamento
└── utils/
    ├── burn_rate.py    # Cálculos financeiros
    └── formatters.py   # Formatação de mensagens
```

## Comandos do Bot

| Comando | Estado | Descrição |
|---------|--------|-----------|
| `/start` | new/onboarding | Iniciar cadastro |
| `/receita <valor>` | active | Registrar faturamento |
| `/despesa <valor>` | active | Registrar despesa |
| `/relatorio` | active | Ver situação atual |
| `/ajuda` | qualquer | Ver comandos |

## Mensagens do Bot

### Boas-vindas (state=new)
```
👋 Olá, {nome}! Bem-vindo ao VigIA!

🛡️ Sou seu guardião financeiro. Estou aqui para garantir que você saiba o que está acontecendo com o caixa da sua empresa - antes que o pior problema apareça: ficar sem dinheiro.

💡 Como funciona:
• Todo dia você me informa suas receitas e despesas
• Todo dia 7h eu te mando um relatório com a situação do caixa
• Se algo precisar de atenção, eu te aviso antes

🚀 Para começar, é rápido! Preciso só de 3 informações:
1. Seu custo fixo mensal
2. Quanto % do faturamento vira custo variável
3. Quanto você quer ter de caixa mínimo

Digite /start quando quiser começar!
```

### Ajuda
```
📋 AJUDA - VigIA

/receita <valor> - Registrar faturamento
/despesa <valor> - Registrar despesa
/relatorio - Ver situacao atual
/ajuda - Esta mensagem

Use /relatorio para ver a situacao do seu caixa!
```

## Status Atual

- ✅ Banco configurado e funcionando
- ✅ Onboarding completo
- ✅ /ajuda funcionando
- ✅ /start funcionando
- ⏳ /receita, /despesa, /relatorio em teste
