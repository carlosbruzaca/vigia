from src.services import supabase as supabase_service
from src.services.telegram import send_message
from src.utils.burn_rate import calculate_runway, calculate_monthly_burn
from src.utils.formatters import format_company_status


async def send_daily_reports() -> None:
    supabase = supabase_service.get_supabase()
    result = supabase.table("users").select("*").eq("state", "operation").execute()
    
    for user_data in result.data:
        if not user_data.get("company_id"):
            continue
        
        company = supabase_service.get_company(user_data["company_id"])
        if not company:
            continue
        
        entries = supabase_service.get_entries_by_company(company.id)
        entries_dict = [{"amount": e.amount, "entry_type": e.entry_type} for e in entries]
        burn_rate = calculate_monthly_burn(entries_dict)
        runway = calculate_runway(company.cash, burn_rate)
        
        message = format_company_status(company.model_dump(), burn_rate, runway)
        await send_message(user_data["telegram_id"], message)
