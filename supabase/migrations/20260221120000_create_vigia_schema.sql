-- Create vigia schema
CREATE SCHEMA IF NOT EXISTS vigia;

-- 1. vigia_companies
CREATE TABLE IF NOT EXISTS vigia.companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    cnpj TEXT,
    email TEXT,
    fixed_cost_avg DECIMAL(12,2) DEFAULT 0,
    variable_cost_percent DECIMAL(5,2) DEFAULT 30,
    cash_minimum DECIMAL(12,2) DEFAULT 5000,
    alert_days_threshold INT DEFAULT 10,
    status TEXT DEFAULT 'trial',
    plan TEXT DEFAULT 'early_adopter',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT chk_variable_cost CHECK (variable_cost_percent BETWEEN 0 AND 100),
    CONSTRAINT chk_fixed_cost CHECK (fixed_cost_avg >= 0),
    CONSTRAINT chk_cash_minimum CHECK (cash_minimum >= 0)
);

CREATE INDEX IF NOT EXISTS idx_vigia_companies_status ON vigia.companies(status);
CREATE INDEX IF NOT EXISTS idx_vigia_companies_plan ON vigia.companies(plan);

-- 2. vigia_users
CREATE TABLE IF NOT EXISTS vigia.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES vigia.companies(id) ON DELETE CASCADE,
    chat_id BIGINT NOT NULL,
    telegram_id BIGINT,
    first_name TEXT,
    last_name TEXT,
    username TEXT,
    state TEXT DEFAULT 'new',
    current_action TEXT,
    onboarding_step INT DEFAULT 0,
    last_interaction_at TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT chk_onboarding CHECK (onboarding_step BETWEEN 0 AND 4),
    CONSTRAINT uniq_chat_id UNIQUE (chat_id)
);

CREATE INDEX IF NOT EXISTS idx_vigia_users_chat_id ON vigia.users(chat_id);
CREATE INDEX IF NOT EXISTS idx_vigia_users_state ON vigia.users(state);
CREATE INDEX IF NOT EXISTS idx_vigia_users_company ON vigia.users(company_id);
CREATE INDEX IF NOT EXISTS idx_vigia_users_action ON vigia.users(current_action) WHERE current_action IS NOT NULL;

-- 3. vigia_entries
CREATE TABLE IF NOT EXISTS vigia.entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES vigia.companies(id) ON DELETE CASCADE,
    user_id UUID REFERENCES vigia.users(id) ON DELETE SET NULL,
    entry_date DATE NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    type TEXT NOT NULL,
    source TEXT DEFAULT 'manual',
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT chk_amount CHECK (amount > 0),
    CONSTRAINT chk_type CHECK (type IN ('revenue', 'expense'))
);

CREATE INDEX IF NOT EXISTS idx_vigia_entries_company_date ON vigia.entries(company_id, entry_date DESC);
CREATE INDEX IF NOT EXISTS idx_vigia_entries_type ON vigia.entries(company_id, type, entry_date);
CREATE INDEX IF NOT EXISTS idx_vigia_entries_created ON vigia.entries(created_at DESC);

-- 4. vigia_receivables
CREATE TABLE IF NOT EXISTS vigia.receivables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES vigia.companies(id) ON DELETE CASCADE,
    client_name TEXT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    due_date DATE NOT NULL,
    status TEXT DEFAULT 'pending',
    description TEXT,
    notified_at TIMESTAMPTZ,
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT chk_receivable_amount CHECK (amount > 0)
);

CREATE INDEX IF NOT EXISTS idx_vigia_receivables_company_status ON vigia.receivables(company_id, status) WHERE status IN ('pending', 'overdue');
CREATE INDEX IF NOT EXISTS idx_vigia_receivables_due_date ON vigia.receivables(due_date);

-- 5. vigia_subscriptions
CREATE TABLE IF NOT EXISTS vigia.subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES vigia.companies(id) ON DELETE CASCADE,
    amount DECIMAL(12,2) NOT NULL,
    status TEXT DEFAULT 'pending',
    gateway TEXT,
    gateway_payment_id TEXT,
    invoice_url TEXT,
    due_date DATE NOT NULL,
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_vigia_subscriptions_company ON vigia.subscriptions(company_id);
CREATE INDEX IF NOT EXISTS idx_vigia_subscriptions_status ON vigia.subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_vigia_subscriptions_due ON vigia.subscriptions(due_date);

-- 6. vigia_message_logs
CREATE TABLE IF NOT EXISTS vigia.message_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES vigia.companies(id) ON DELETE SET NULL,
    user_id UUID REFERENCES vigia.users(id) ON DELETE SET NULL,
    direction TEXT NOT NULL,
    message_text TEXT,
    telegram_message_id BIGINT,
    payload JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_vigia_logs_company_created ON vigia.message_logs(company_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_vigia_logs_user ON vigia.message_logs(user_id);

-- 7. vigia_alerts
CREATE TABLE IF NOT EXISTS vigia.alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES vigia.companies(id) ON DELETE CASCADE,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    data JSONB,
    sent_at TIMESTAMPTZ DEFAULT now(),
    read_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_vigia_alerts_company_sent ON vigia.alerts(company_id, sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_vigia_alerts_unread ON vigia.alerts(company_id, read_at) WHERE read_at IS NULL;

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION vigia.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_vigia_companies_updated_at BEFORE UPDATE ON vigia.companies 
    FOR EACH ROW EXECUTE FUNCTION vigia.update_updated_at_column();

CREATE TRIGGER update_vigia_users_updated_at BEFORE UPDATE ON vigia.users 
    FOR EACH ROW EXECUTE FUNCTION vigia.update_updated_at_column();

CREATE TRIGGER update_vigia_entries_updated_at BEFORE UPDATE ON vigia.entries 
    FOR EACH ROW EXECUTE FUNCTION vigia.update_updated_at_column();

CREATE TRIGGER update_vigia_receivables_updated_at BEFORE UPDATE ON vigia.receivables 
    FOR EACH ROW EXECUTE FUNCTION vigia.update_updated_at_column();

CREATE TRIGGER update_vigia_subscriptions_updated_at BEFORE UPDATE ON vigia.subscriptions 
    FOR EACH ROW EXECUTE FUNCTION vigia.update_updated_at_column();
