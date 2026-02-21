from src.database import get_supabase, get_supabase_admin


def get_user_by_chat_id(chat_id: int) -> dict | None:
    supabase = get_supabase()
    result = supabase.table("vigia_users").select("*").eq("chat_id", chat_id).execute()
    if result.data:
        return result.data[0]
    return None


def get_user_by_id(user_id: str) -> dict | None:
    supabase = get_supabase()
    result = supabase.table("vigia_users").select("*").eq("id", user_id).execute()
    if result.data:
        return result.data[0]
    return None


def create_user(data: dict) -> dict:
    supabase = get_supabase_admin()
    result = supabase.table("vigia_users").insert(data).execute()
    return result.data[0]


def update_user(user_id: str, data: dict) -> dict | None:
    supabase = get_supabase_admin()
    result = supabase.table("vigia_users").update(data).eq("id", user_id).execute()
    if result.data:
        return result.data[0]
    return None


def get_company_by_id(company_id: str) -> dict | None:
    supabase = get_supabase()
    result = supabase.table("vigia_companies").select("*").eq("id", company_id).execute()
    if result.data:
        return result.data[0]
    return None


def get_all_active_companies() -> list[dict]:
    supabase = get_supabase()
    result = supabase.table("vigia_companies").select("*").eq("status", "active").execute()
    return result.data


def create_company(data: dict) -> dict:
    supabase = get_supabase_admin()
    result = supabase.table("vigia_companies").insert(data).execute()
    return result.data[0]


def update_company(company_id: str, data: dict) -> dict | None:
    supabase = get_supabase_admin()
    result = supabase.table("vigia_companies").update(data).eq("id", company_id).execute()
    if result.data:
        return result.data[0]
    return None


def create_entry(data: dict) -> dict:
    supabase = get_supabase_admin()
    result = supabase.table("vigia_entries").insert(data).execute()
    return result.data[0]


def get_entries_by_company(company_id: str, days: int = 30) -> list[dict]:
    supabase = get_supabase()
    from datetime import date, timedelta
    start_date = (date.today() - timedelta(days=days)).isoformat()
    result = supabase.table("vigia_entries").select("*").eq("company_id", company_id).gte("entry_date", start_date).execute()
    return result.data


def get_entries_yesterday(company_id: str) -> list[dict]:
    supabase = get_supabase()
    from datetime import date, timedelta
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    result = supabase.table("vigia_entries").select("*").eq("company_id", company_id).eq("entry_date", yesterday).execute()
    return result.data


def get_receivables_pending(company_id: str) -> list[dict]:
    supabase = get_supabase()
    result = supabase.table("vigia_receivables").select("*").eq("company_id", company_id).in_("status", ["pending", "overdue"]).execute()
    return result.data


def create_receivable(data: dict) -> dict:
    supabase = get_supabase_admin()
    result = supabase.table("vigia_receivables").insert(data).execute()
    return result.data[0]


def update_receivable(receivable_id: str, data: dict) -> dict | None:
    supabase = get_supabase_admin()
    result = supabase.table("vigia_receivables").update(data).eq("id", receivable_id).execute()
    if result.data:
        return result.data[0]
    return None


def log_message(data: dict) -> dict:
    supabase = get_supabase_admin()
    result = supabase.table("vigia_message_logs").insert(data).execute()
    return result.data[0]


def create_alert(data: dict) -> dict:
    supabase = get_supabase_admin()
    result = supabase.table("vigia_alerts").insert(data).execute()
    return result.data[0]
