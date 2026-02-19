from src.database import get_supabase
from src.models.user import User, UserCreate
from src.models.company import Company, CompanyCreate
from src.models.entries import Entry, EntryCreate


def get_user_by_telegram_id(telegram_id: int) -> User | None:
    supabase = get_supabase()
    result = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
    if result.data:
        return User(**result.data[0])
    return None


def create_user(user: UserCreate) -> User:
    supabase = get_supabase()
    result = supabase.table("users").insert(user.model_dump()).execute()
    return User(**result.data[0])


def update_user(telegram_id: int, data: dict) -> User | None:
    supabase = get_supabase()
    result = supabase.table("users").update(data).eq("telegram_id", telegram_id).execute()
    if result.data:
        return User(**result.data[0])
    return None


def get_company(company_id: str) -> Company | None:
    supabase = get_supabase()
    result = supabase.table("companies").select("*").eq("id", company_id).execute()
    if result.data:
        return Company(**result.data[0])
    return None


def create_company(company: CompanyCreate) -> Company:
    supabase = get_supabase()
    result = supabase.table("companies").insert(company.model_dump()).execute()
    return Company(**result.data[0])


def update_company(company_id: str, data: dict) -> Company | None:
    supabase = get_supabase()
    result = supabase.table("companies").update(data).eq("id", company_id).execute()
    if result.data:
        return Company(**result.data[0])
    return None


def create_entry(entry: EntryCreate) -> Entry:
    supabase = get_supabase()
    result = supabase.table("entries").insert(entry.model_dump()).execute()
    return Entry(**result.data[0])


def get_entries_by_company(company_id: str) -> list[Entry]:
    supabase = get_supabase()
    result = supabase.table("entries").select("*").eq("company_id", company_id).execute()
    return [Entry(**item) for item in result.data]
