from supabase import create_client, Client
from src.config import settings

_client: Client | None = None
_service_client: Client | None = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        _client = create_client(settings.supabase_url, settings.supabase_key)
    return _client


def get_supabase_admin() -> Client:
    global _service_client
    if _service_client is None:
        key = settings.supabase_service_role_key or settings.supabase_key
        _service_client = create_client(settings.supabase_url, key)
    return _service_client
