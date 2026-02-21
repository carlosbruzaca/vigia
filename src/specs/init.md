# VigIA - Perfil do Projeto (Stack Python + Supabase)

## Visão
Sistema de vigilância financeira automatizada para PMEs via Telegram.
Entrega: relatórios diários de caixa com previsão de quebra (burn rate) e alertas proativos.

## Stack Técnica
- **Backend:** Python 3.11+ (FastAPI/Flask opcional, ou puro com webhooks)
- **Banco de Dados:** Supabase (PostgreSQL)
- **Mensageria:** Telegram Bot API (python-telegram-bot)
- **Agendamento:** APScheduler ou cron com Python
- **Deploy:** VPS com Docker (opcional) ou PM2

## Arquitetura de Estados

new → onboarding → active → paused → blocked


- **new:** Usuário criado, aguardando configuração inicial
- **onboarding:** Coletando custo fixo, % variável e caixa mínimo
- **active:** Operação normal (receitas/despesas diárias)
- **paused:** Pagamento atrasado ou solicitação do cliente
- **blocked:** Cancelado ou inadimplente grave

## Padrões de Código

### Python
- **Estilo:** PEP 8, type hints obrigatórios
- **Estrutura:** Serviços separados por domínio (router, onboarding, operation, daily_report)
- **Banco:** postgrest-py ou supabase-py para queries
- **Logs:** logging padrão Python, nível INFO para produção

### Nomenclatura de Arquivos
- `router.py` = Roteamento principal
- `onboarding.py` = Coleta de dados iniciais
- `operation.py` = Comandos diários (/receita, /despesa)
- `daily_report.py` = Relatório agendado
- `models.py` = Schemas Pydantic (opcional) ou dataclasses

### Supabase
- Tabelas: prefixo `vigia_` (ex: vigia_companies, vigia_users)
- Campos: snake_case
- Índices: todo foreign key e campo de busca frequente

## Regras de Negócio Críticas

1. **Cálculo Burn Rate:** `daily_burn = (fixed_cost_avg / 30) + (avg_daily_revenue * variable_cost_percent / 100)`
2. **Alertas de Caixa:**
   - 🔴 Crítico: <= 10 dias de caixa restante
   - ⚠️ Atenção: <= 20 dias de caixa restante
3. **Cobrança de Dados:** 2 dias sem input do usuário = notificação
4. **Preços:** Early Adopter R$ 79 | Local R$ 119 | Pro R$ 179 (mensal)

## MCPs Disponíveis

### supabase-mcp
- Execução de SQL (schema, migrations)
- CRUD em tabelas
- Queries complexas

## Comandos do OpenCode

Quando eu disser "gerar", você deve:

1. Ler a spec correspondente em `specs/`
2. Gerar o código Python em `src/` (nunca edite specs)
3. Validar sintaxe Python (imports, indentação, tipos)
4. Reportar o que foi criado e pendências

Quando eu disser "deploy", você deve:

1. Verificar se há requirements.txt atualizado
2. Sugerir comando de execução (python main.py ou similar)
3. Reportar dependências pendentes

## Contexto de Negócio

- **Região Inicial:** São Luís, Maranhão
- **Público-Alvo:** PMEs com faturamento recorrente
- **Meta Financeira:** R$ 7.000/mês (R$ 5.000 lucro + R$ 2.000 custos)
- **Meta de Clientes:** 40-50 clientes pagos no primeiro trimestre

## Restrições Técnicas

- MVP sem RLS (simplifica desenvolvimento)
- MVP sem integração bancária (dados manuais)
- MVP sem app web (só Telegram)
- PostgreSQL 15+ (Supabase)
- Python 3.11+