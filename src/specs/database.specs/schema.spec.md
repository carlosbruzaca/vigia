# Spec: Database Schema
## Modelo de Dados VigIA - Supabase PostgreSQL

---

## 1. Tabela: vigia_companies

**Propósito:** Empresas/clientes do sistema. Cada empresa tem uma configuração de negócio.

| Campo | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| id | uuid | gen_random_uuid() | PK |
| name | text | NOT NULL | Nome fantasia |
| cnpj | text | NULL | CNPJ (opcional no MVP) |
| email | text | NULL | Email para notificações |
| fixed_cost_avg | decimal(12,2) | 0 | Custo fixo mensal (aluguel, salários) |
| variable_cost_percent | decimal(5,2) | 30 | % do faturamento que é custo variável |
| cash_minimum | decimal(12,2) | 5000 | Caixa mínimo desejado (alerta) |
| alert_days_threshold | int | 10 | Avisar quando faltarem X dias |
| status | text | 'trial' | active, paused, cancelled, trial |
| plan | text | 'early_adopter' | basic, pro, early_adopter |
| created_at | timestamptz | now() | |
| updated_at | timestamptz | now() | |

**Constraints:**
- `CHECK (variable_cost_percent BETWEEN 0 AND 100)`
- `CHECK (fixed_cost_avg >= 0)`
- `CHECK (cash_minimum >= 0)`

**Índices:**
- `idx_vigia_companies_status ON (status)`
- `idx_vigia_companies_plan ON (plan)`

---

## 2. Tabela: vigia_users

**Propósito:** Usuários que interagem com o bot Telegram. Pode haver múltiplos por empresa (futuro).

| Campo | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| id | uuid | gen_random_uuid() | PK |
| company_id | uuid | NOT NULL | FK → vigia_companies.id |
| chat_id | bigint | NOT NULL | ID único do chat Telegram |
| telegram_id | bigint | NULL | ID do usuário no Telegram |
| first_name | text | NULL | Nome |
| last_name | text | NULL | Sobrenome |
| username | text | NULL | @username no Telegram |
| state | text | 'new' | new, onboarding, active, paused, blocked |
| current_action | text | NULL | Estado da conversa (ver enum abaixo) |
| onboarding_step | int | 0 | 0-4 (progresso do onboarding) |
| last_interaction_at | timestamptz | now() | Último contato |
| created_at | timestamptz | now() | |
| updated_at | timestamptz | now() | |

**Enum current_action:**
- `NULL` = idle (esperando comando)
- `awaiting_fixed_cost` = onboarding: esperando custo fixo
- `awaiting_variable_cost` = onboarding: esperando % variável
- `awaiting_cash_minimum` = onboarding: esperando caixa mínimo
- `awaiting_revenue_value` = operação: esperando valor de receita
- `awaiting_expense_value` = operação: esperando valor de despesa
- `awaiting_receivable_name` = operação: nome do cliente em atraso
- `awaiting_receivable_amount` = operação: valor do atraso

**Constraints:**
- `UNIQUE (chat_id)`
- `CHECK (onboarding_step BETWEEN 0 AND 4)`

**Índices:**
- `idx_vigia_users_chat_id ON (chat_id)` -- Busca principal
- `idx_vigia_users_state ON (state)` -- Roteamento
- `idx_vigia_users_company ON (company_id)` -- Joins
- `idx_vigia_users_action ON (current_action) WHERE current_action IS NOT NULL`

---

## 3. Tabela: vigia_entries

**Propósito:** Lançamentos financeiros diários (receitas e despesas).

| Campo | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| id | uuid | gen_random_uuid() | PK |
| company_id | uuid | NOT NULL | FK |
| user_id | uuid | NULL | FK → vigia_users (quem lançou) |
| entry_date | date | NOT NULL | Data do lançamento |
| amount | decimal(12,2) | NOT NULL | Valor (sempre positivo) |
| type | text | NOT NULL | revenue, expense |
| source | text | 'manual' | manual, import, projection |
| description | text | NULL | Ex: "Venda cliente X" |
| created_at | timestamptz | now() | |
| updated_at | timestamptz | now() | |

**Constraints:**
- `CHECK (amount > 0)`
- `CHECK (type IN ('revenue', 'expense'))`
- `UNIQUE (company_id, entry_date, amount, type, source)` -- Evita duplicidade exata

**Índices:**
- `idx_vigia_entries_company_date ON (company_id, entry_date DESC)` -- Relatório diário
- `idx_vigia_entries_type ON (company_id, type, entry_date)` -- Agregações
- `idx_vigia_entries_created ON (created_at DESC)` -- Auditoria

---

## 4. Tabela: vigia_receivables

**Propósito:** Contas a receber (clientes em atraso).

| Campo | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| id | uuid | gen_random_uuid() | PK |
| company_id | uuid | NOT NULL | FK |
| client_name | text | NOT NULL | Nome do cliente |
| amount | decimal(12,2) | NOT NULL | Valor a receber |
| due_date | date | NOT NULL | Data do vencimento |
| status | text | 'pending' | pending, paid, overdue, cancelled |
| description | text | NULL | Descrição do serviço |
| notified_at | timestamptz | NULL | Quando entrou no relatório |
| paid_at | timestamptz | NULL | Quando foi quitado |
| created_at | timestamptz | now() | |
| updated_at | timestamptz | now() | |

**Constraints:**
- `CHECK (amount > 0)`

**Índices:**
- `idx_vigia_receivables_company_status ON (company_id, status) WHERE status IN ('pending', 'overdue')`
- `idx_vigia_receivables_due_date ON (due_date)` -- Alertas de atraso

---

## 5. Tabela: vigia_subscriptions

**Propósito:** Controle de pagamentos mensais do VigIA (receita do sistema).

| Campo | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| id | uuid | gen_random_uuid() | PK |
| company_id | uuid | NOT NULL | FK |
| amount | decimal(12,2) | NOT NULL | Valor da mensalidade |
| status | text | 'pending' | pending, paid, overdue, cancelled, trial |
| gateway | text | NULL | asaas, stripe, manual |
| gateway_payment_id | text | NULL | ID externo do pagamento |
| invoice_url | text | NULL | Link da fatura |
| due_date | date | NOT NULL | Vencimento |
| paid_at | timestamptz | NULL | Data do pagamento |
| created_at | timestamptz | now() | |
| updated_at | timestamptz | now() | |

**Índices:**
- `idx_vigia_subscriptions_company ON (company_id)`
- `idx_vigia_subscriptions_status ON (status)`
- `idx_vigia_subscriptions_due ON (due_date)` -- Cobranças

---

## 6. Tabela: vigia_message_logs

**Propósito:** Auditoria de todas as mensagens trocadas (debug e compliance).

| Campo | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| id | uuid | gen_random_uuid() | PK |
| company_id | uuid | NULL | FK (pode ser NULL se usuário não identificado) |
| user_id | uuid | NULL | FK |
| direction | text | NOT NULL | in (usuário→bot), out (bot→usuário) |
| message_text | text | NULL | Conteúdo da mensagem |
| telegram_message_id | bigint | NULL | ID da msg no Telegram |
| payload | jsonb | NULL | Dados extras (estado, erro, etc) |
| created_at | timestamptz | now() | |

**Índices:**
- `idx_vigia_logs_company_created ON (company_id, created_at DESC)`
- `idx_vigia_logs_user ON (user_id)`

---

## 7. Tabela: vigia_alerts

**Propósito:** Histórico de alertas de caixa gerados pelo sistema.

| Campo | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| id | uuid | gen_random_uuid() | PK |
| company_id | uuid | NOT NULL | FK |
| alert_type | text | NOT NULL | cash_critical, burn_rate_high, no_data, overdue_receivables, revenue_drop |
| severity | text | NOT NULL | low, medium, high, critical |
| message | text | NOT NULL | Texto do alerta enviado |
| data | jsonb | NULL | Dados do momento (saldo, projeção, etc) |
| sent_at | timestamptz | now() | |
| read_at | timestamptz | NULL | Quando usuário viu |
| resolved_at | timestamptz | NULL | Quando foi resolvido |

**Índices:**
- `idx_vigia_alerts_company_sent ON (company_id, sent_at DESC)`
- `idx_vigia_alerts_unread ON (company_id, read_at) WHERE read_at IS NULL`

---

## 8. Triggers e Funções

### 8.1 Atualização automática de updated_at

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar em todas as tabelas com updated_at
CREATE TRIGGER update_vigia_companies_updated_at BEFORE UPDATE ON vigia_companies 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_vigia_users_updated_at BEFORE UPDATE ON vigia_users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_vigia_entries_updated_at BEFORE UPDATE ON vigia_entries 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_vigia_receivables_updated_at BEFORE UPDATE ON vigia_receivables 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_vigia_subscriptions_updated_at BEFORE UPDATE ON vigia_subscriptions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

9. Queries de Exemplo

9.1 Relatório Diário (Faturamento ontem vs média)

SELECT 
    c.id as company_id,
    c.name,
    -- Ontem
    COALESCE((
        SELECT SUM(amount) 
        FROM vigia_entries 
        WHERE company_id = c.id 
        AND type = 'revenue' 
        AND entry_date = CURRENT_DATE - 1
    ), 0) as revenue_yesterday,
    -- Média 7 dias
    COALESCE((
        SELECT SUM(amount) / 7.0
        FROM vigia_entries 
        WHERE company_id = c.id 
        AND type = 'revenue' 
        AND entry_date >= CURRENT_DATE - 7
    ), 0) as revenue_avg_7days,
    -- Variação percentual
    CASE 
        WHEN revenue_avg_7days > 0 
        THEN ROUND(((revenue_yesterday - revenue_avg_7days) / revenue_avg_7days * 100), 1)
        ELSE 0 
    END as variation_percent
FROM vigia_companies c
WHERE c.status = 'active';

9.2 Clientes em Atraso por Empresa

SELECT 
    company_id,
    COUNT(*) as overdue_count,
    SUM(amount) as overdue_total
FROM vigia_receivables
WHERE status IN ('pending', 'overdue')
    AND due_date < CURRENT_DATE
GROUP BY company_id;

9.3 Burn Rate e Dias de Caixa

WITH company_metrics AS (
    SELECT 
        c.id,
        c.fixed_cost_avg,
        c.variable_cost_percent,
        c.cash_minimum,
        -- Saldo atual (receitas - despesas)
        COALESCE((
            SELECT SUM(CASE WHEN type = 'revenue' THEN amount ELSE -amount END)
            FROM vigia_entries
            WHERE company_id = c.id
        ), 0) as cash_balance,
        -- Receita média diária (últimos 30 dias)
        COALESCE((
            SELECT SUM(amount) / 30.0
            FROM vigia_entries
            WHERE company_id = c.id
            AND type = 'revenue'
            AND entry_date >= CURRENT_DATE - 30
        ), 0) as avg_daily_revenue
    FROM vigia_companies c
    WHERE c.status = 'active'
)
SELECT 
    id as company_id,
    cash_balance,
    -- Burn rate diário
    ROUND((fixed_cost_avg / 30.0) + (avg_daily_revenue * variable_cost_percent / 100.0), 2) as daily_burn,
    -- Dias até quebrar
    CASE 
        WHEN daily_burn > 0 THEN ROUND(cash_balance / daily_burn, 0)
        ELSE 999 -- Infinito se não há queima
    END as days_to_zero
FROM company_metrics;

