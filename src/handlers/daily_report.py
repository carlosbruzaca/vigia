from datetime import date, timedelta
from src.services import supabase as supabase_service
from src.services.telegram import send_message
from src.utils.burn_rate import calculate_daily_burn, calculate_runway, get_alert_level
from src.utils.formatters import format_daily_report, format_currency


async def send_daily_reports() -> None:
    companies = supabase_service.get_all_active_companies()
    
    for company in companies:
        try:
            await _send_company_report(company)
        except Exception as e:
            print(f"Erro ao enviar relatório para {company.get('name')}: {e}")


async def _send_company_report(company: dict) -> None:
    company_id = company["id"]
    
    yesterday_revenue = _get_yesterday_revenue(company_id)
    avg_revenue = _get_avg_revenue(company_id)
    cash_balance = _get_cash_balance(company_id)
    overdue_total = _get_overdue_total(company_id)
    
    fixed_cost = company.get("fixed_cost_avg", 0) or 0
    variable_percent = company.get("variable_cost_percent", 30) or 30
    
    daily_burn = calculate_daily_burn(fixed_cost, avg_revenue / 7, variable_percent)
    days_of_cash = calculate_runway(cash_balance, daily_burn)
    
    alert_emoji, alert_level = get_alert_level(int(days_of_cash))
    
    message = format_daily_report(
        company_name=company.get("name", "Empresa"),
        revenue_yesterday=yesterday_revenue,
        revenue_avg=avg_revenue,
        cash_balance=cash_balance,
        days_of_cash=int(days_of_cash),
        overdue_total=overdue_total,
        alert_emoji=alert_emoji,
        alert_level=alert_level
    )
    
    chat_id = company.get("chat_id")
    if chat_id:
        await send_message(chat_id, message)


def _get_yesterday_revenue(company_id: str) -> float:
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    entries = supabase_service.get_entries_yesterday(company_id)
    return sum(e["amount"] for e in entries if e["type"] == "revenue")


def _get_avg_revenue(company_id: str) -> float:
    entries = supabase_service.get_entries_by_company(company_id, days=7)
    revenues = [e["amount"] for e in entries if e["type"] == "revenue"]
    return sum(revenues) / 7 if revenues else 0


def _get_cash_balance(company_id: str) -> float:
    entries = supabase_service.get_entries_by_company(company_id, days=90)
    cash = 0
    for e in entries:
        if e["type"] == "revenue":
            cash += e["amount"]
        elif e["type"] == "expense":
            cash -= e["amount"]
    return cash


def _get_overdue_total(company_id: str) -> float:
    receivables = supabase_service.get_receivables_pending(company_id)
    return sum(r["amount"] for r in receivables)
