-- Enable vigia schema in PostgREST
GRANT USAGE ON SCHEMA vigia TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA vigia TO anon, authenticated, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA vigia TO anon, authenticated, service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA vigia TO anon, authenticated, service_role;

-- Alter schema cache (requires superuser)
NOTIFY pgrst, 'reload schema';
