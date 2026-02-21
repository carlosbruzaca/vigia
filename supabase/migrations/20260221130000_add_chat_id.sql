-- Add chat_id to companies for sending reports
ALTER TABLE public.vigia_companies ADD COLUMN IF NOT EXISTS chat_id BIGINT;

-- Add last_report_sent_at to companies
ALTER TABLE public.vigia_companies ADD COLUMN IF NOT EXISTS last_report_sent_at TIMESTAMPTZ;

-- Create index for chat_id lookup
CREATE INDEX IF NOT EXISTS idx_vigia_companies_chat_id ON public.vigia_companies(chat_id);

-- Grant permissions
GRANT UPDATE ON public.vigia_companies TO anon, authenticated, service_role;

NOTIFY pgrst, 'reload schema';
