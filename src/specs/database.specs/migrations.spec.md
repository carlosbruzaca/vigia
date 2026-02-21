# Spec: Database Migrations
## Evolução Controlada do Schema VigIA

---

## Princípios

1. **Nunca altere migrations aplicadas** - Crie novas sempre
2. **Versionamento:** `YYYYMMDD_HHMMSS_nome_descritivo.sql`
3. **Idempotência:** Scripts devem poder rodar múltiplas vezes sem erro (IF NOT EXISTS)
4. **Rollback:** Documente como reverter (para emergências)

---

## Migration Inicial: 20260221_000000_schema_inicial.sql

**Arquivo:** `generated/supabase/migrations/20260221_000000_schema_inicial.sql`

```sql
-- ==========================================
-- VIGIA - Migration Inicial
-- Cria todas as tabelas do MVP
-- ==========================================

-- 1. COMPANIES
CREATE TABLE IF NOT EXISTS vigia_companies (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    cnpj text UNIQUE,
    email text,
    fixed_cost_avg decimal(12,2) DEFAULT 0,
    variable_cost_percent decimal(5,2) DEFAULT 30,
    cash_minimum decimal(12,2) DEFAULT 5000,
    alert_days_threshold int DEFAULT 10,
    status text DEFAULT 'trial' CHECK (status IN ('active', 'paused', 'cancelled', 'trial')),
    plan text DEFAULT 'early_adopter' CHECK (plan IN ('basic', 'pro', 'early_adopter')),
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- 2. USERS
CREATE TABLE IF NOT EXISTS vigia_users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id uuid REFERENCES vigia_companies(id) ON DELETE CASCADE,
    chat_id bigint UNIQUE NOT NULL,
    telegram_id bigint,
    first_name text,
    last_name text,
    username text,
    state text DEFAULT 'new' CHECK (state IN ('new', 'onboarding', 'active', 'paused', 'blocked')),
    current_action text CHECK (current_action IN (null, 'awaiting_fixed_cost', 'awaiting_variable_cost', 'awaiting_cash_minimum', 'awaiting_revenue_value', 'awaiting_expense_value', 'awaiting_receivable_name', 'awaiting_receivable_amount')),
    onboarding_step int DEFAULT 0 CHECK (onboarding_step BETWEEN 0 AND 4),
    last_interaction_at timestamptz DEFAULT now(),
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- 3. ENTRIES
CREATE TABLE IF NOT EXISTS vigia_entries (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id uuid REFERENCES vigia_companies(id) ON DELETE CASCADE,
    user_id uuid REFERENCES vigia_users(id) ON DELETE SET NULL,
    entry_date date NOT NULL,
    amount decimal(12,2) NOT NULL CHECK (amount > 0),
    type text NOT NULL CHECK (type IN ('revenue', 'expense')),
    source text DEFAULT 'manual' CHECK (source IN ('manual', 'import', 'projection')),
    description text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    CONSTRAINT unique_entry UNIQUE (company_id, entry_date, amount, type, source)
);

-- 4. RECEIVABLES
CREATE TABLE IF NOT EXISTS vigia_receivables (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id uuid REFERENCES vigia_companies(id) ON DELETE CASCADE,
    client_name text NOT NULL,
    amount decimal(12,2) NOT NULL CHECK (amount > 0),
    due_date date NOT NULL,
    status text DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'overdue', 'cancelled')),
    description text,
    notified_at timestamptz,
    paid_at timestamptz,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- 5. SUBSCRIPTIONS
CREATE TABLE IF NOT EXISTS vigia_subscriptions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id uuid REFERENCES vigia_companies(id) ON DELETE CASCADE,
    amount decimal(12,2) NOT NULL,
    status text DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'overdue', 'cancelled', 'trial')),
    gateway text,
    gateway_payment_id text,
    invoice_url text,
    due_date date NOT NULL,
    paid_at timestamptz,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- 6. MESSAGE LOGS
CREATE TABLE IF NOT EXISTS vigia_message_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id uuid REFERENCES vigia_companies(id) ON DELETE CASCADE,
    user_id uuid REFERENCES vigia_users(id) ON DELETE SET NULL,
    direction text NOT NULL CHECK (direction IN ('in', 'out')),
    message_text text,
    telegram_message_id bigint,
    payload jsonb,
    created_at timestamptz DEFAULT now()
);

-- 7. ALERTS
CREATE TABLE IF NOT EXISTS vigia_alerts (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id uuid REFERENCES vigia_companies(id) ON DELETE CASCADE,
    alert_type text NOT NULL CHECK (alert_type IN ('cash_critical', 'burn_rate_high', 'no_data', 'overdue_receivables', 'revenue_drop')),
    severity text NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    message text NOT NULL,
    data jsonb,
    sent_at timestamptz DEFAULT now(),
    read_at timestamptz,
    resolved_at timestamptz
);

-- ==========================================
-- ÍNDICES
-- ==========================================

-- Companies
CREATE INDEX IF NOT EXISTS idx_vigia_companies_status ON vigia_companies(status);
CREATE INDEX IF NOT EXISTS idx_vigia_companies_plan ON vigia_companies(plan);

-- Users
CREATE INDEX IF NOT EXISTS idx_vigia_users_chat_id ON vigia_users(chat_id);
CREATE INDEX IF NOT EXISTS idx_vigia_users_state ON vigia_users(state);
CREATE INDEX IF NOT EXISTS idx_vigia_users_company ON vigia_users(company_id);
CREATE INDEX IF NOT EXISTS idx_vigia_users_action ON vigia_users(current_action) WHERE current_action IS NOT NULL;

-- Entries
CREATE INDEX IF NOT EXISTS idx_vigia_entries_company_date ON vigia_entries(company_id, entry_date DESC);
CREATE INDEX IF NOT EXISTS idx_vigia_entries_type ON vigia_entries(company_id, type, entry_date);
CREATE INDEX IF NOT EXISTS idx_vigia_entries_created ON vigia_entries(created_at DESC);

-- Receivables
CREATE INDEX IF NOT EXISTS idx_vigia_receivables_company_status ON vigia_receivables(company_id, status) WHERE status IN ('pending', 'overdue');
CREATE INDEX IF NOT EXISTS idx_vigia_receivables_due_date ON vigia_receivables(due_date);

-- Subscriptions
CREATE INDEX IF NOT EXISTS idx_vigia_subscriptions_company ON vigia_subscriptions(company_id);
CREATE INDEX IF NOT EXISTS idx_vigia_subscriptions_status ON vigia_subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_vigia_subscriptions_due ON vigia_subscriptions(due_date);

-- Logs
CREATE INDEX IF NOT EXISTS idx_vigia_logs_company_created ON vigia_message_logs(company_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_vigia_logs_user ON vigia_message_logs(user_id);

-- Alerts
CREATE INDEX IF NOT EXISTS idx_vigia_alerts_company_sent ON vigia_alerts(company_id, sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_vigia_alerts_unread ON vigia_alerts(company_id, read_at) WHERE read_at IS NULL;

-- ==========================================
-- TRIGGERS updated_at
-- ==========================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

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

-- ==========================================
-- COMENTÁRIOS
-- ==========================================

COMMENT ON TABLE vigia_companies IS 'Empresas/clientes do VigIA';
COMMENT ON TABLE vigia_users IS 'Usuários que interagem com o bot Telegram';
COMMENT ON TABLE vigia_entries IS 'Lançamentos financeiros diários (receitas e despesas)';
COMMENT ON TABLE vigia_receivables IS 'Contas a receber/clientes em atraso';
COMMENT ON TABLE vigia_subscriptions IS 'Controle de pagamentos mensais do VigIA';
COMMENT ON TABLE vigia_message_logs IS 'Auditoria de todas as mensagens trocadas';
COMMENT ON TABLE vigia_alerts IS 'Histórico de alertas de caixa gerados pelo sistema';

Migration Futura Exemplo: Adicionar campo

Quando precisar adicionar campo:

-- 20260301_120000_add_phone_to_companies.sql
-- Adiciona telefone para notificações SMS futuras

ALTER TABLE vigia_companies 
ADD COLUMN IF NOT EXISTS phone text;

COMMENT ON COLUMN vigia_companies.phone IS 'Telefone para notificações SMS (futuro)';

Rollback (Emergência)

Se precisar desfazer migration inicial:

-- ATENÇÃO: Apaga todos os dados!
DROP TABLE IF EXISTS vigia_alerts CASCADE;
DROP TABLE IF EXISTS vigia_message_logs CASCADE;
DROP TABLE IF EXISTS vigia_subscriptions CASCADE;
DROP TABLE IF EXISTS vigia_receivables CASCADE;
DROP TABLE IF EXISTS vigia_entries CASCADE;
DROP TABLE IF EXISTS vigia_users CASCADE;
DROP TABLE IF EXISTS vigia_companies CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column();