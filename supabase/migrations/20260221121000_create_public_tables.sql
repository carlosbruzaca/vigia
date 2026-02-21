-- Recreate tables in public schema (Supabase default)

-- 1. companies
CREATE TABLE IF NOT EXISTS public.vigia_companies (
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

CREATE INDEX IF NOT EXISTS idx_vigia_companies_status ON public.vigia_companies(status);
CREATE INDEX IF NOT EXISTS idx_vigia_companies_plan ON public.vigia_companies(plan);

-- 2. users
CREATE TABLE IF NOT EXISTS public.vigia_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES public.vigia_companies(id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_vigia_users_chat_id ON public.vigia_users(chat_id);
CREATE INDEX IF NOT EXISTS idx_vigia_users_state ON public.vigia_users(state);
CREATE INDEX IF NOT EXISTS idx_vigia_users_company ON public.vigia_users(company_id);
CREATE INDEX IF NOT EXISTS idx_vigia_users_action ON public.vigia_users(current_action) WHERE current_action IS NOT NULL;

-- 3. entries
CREATE TABLE IF NOT EXISTS public.vigia_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES public.vigia_companies(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.vigia_users(id) ON DELETE SET NULL,
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

CREATE INDEX IF NOT EXISTS idx_vigia_entries_company_date ON public.vigia_entries(company_id, entry_date DESC);
CREATE INDEX IF NOT EXISTS idx_vigia_entries_type ON public.vigia_entries(company_id, type, entry_date);
CREATE INDEX IF NOT EXISTS idx_vigia_entries_created ON public.vigia_entries(created_at DESC);

-- 4. receivables
CREATE TABLE IF NOT EXISTS public.vigia_receivables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES public.vigia_companies(id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_vigia_receivables_company_status ON public.vigia_receivables(company_id, status) WHERE status IN ('pending', 'overdue');
CREATE INDEX IF NOT EXISTS idx_vigia_receivables_due_date ON public.vigia_receivables(due_date);

-- 5. subscriptions
CREATE TABLE IF NOT EXISTS public.vigia_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES public.vigia_companies(id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_vigia_subscriptions_company ON public.vigia_subscriptions(company_id);
CREATE INDEX IF NOT EXISTS idx_vigia_subscriptions_status ON public.vigia_subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_vigia_subscriptions_due ON public.vigia_subscriptions(due_date);

-- 6. message_logs
CREATE TABLE IF NOT EXISTS public.vigia_message_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES public.vigia_companies(id) ON DELETE SET NULL,
    user_id UUID REFERENCES public.vigia_users(id) ON DELETE SET NULL,
    direction TEXT NOT NULL,
    message_text TEXT,
    telegram_message_id BIGINT,
    payload JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_vigia_logs_company_created ON public.vigia_message_logs(company_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_vigia_logs_user ON public.vigia_message_logs(user_id);

-- 7. alerts
CREATE TABLE IF NOT EXISTS public.vigia_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES public.vigia_companies(id) ON DELETE CASCADE,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    data JSONB,
    sent_at TIMESTAMPTZ DEFAULT now(),
    read_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_vigia_alerts_company_sent ON public.vigia_alerts(company_id, sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_vigia_alerts_unread ON public.vigia_alerts(company_id, read_at) WHERE read_at IS NULL;

-- Grant permissions
GRANT ALL ON public.vigia_companies TO anon, authenticated, service_role;
GRANT ALL ON public.vigia_users TO anon, authenticated, service_role;
GRANT ALL ON public.vigia_entries TO anon, authenticated, service_role;
GRANT ALL ON public.vigia_receivables TO anon, authenticated, service_role;
GRANT ALL ON public.vigia_subscriptions TO anon, authenticated, service_role;
GRANT ALL ON public.vigia_message_logs TO anon, authenticated, service_role;
GRANT ALL ON public.vigia_alerts TO anon, authenticated, service_role;

-- Notify PostgREST to reload
NOTIFY pgrst, 'reload schema';
