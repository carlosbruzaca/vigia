import logging
from datetime import date, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from src.database import get_supabase

logger = logging.getLogger(__name__)


def get_company_by_id(company_id: str) -> dict | None:
    supabase = get_supabase()
    result = supabase.table("vigia_companies").select("*").eq("id", company_id).execute()
    if result.data:
        return result.data[0]
    return None


def get_entries_by_company(company_id: str) -> list[dict]:
    supabase = get_supabase()
    result = supabase.table("vigia_entries").select("*").eq("company_id", company_id).execute()
    return result.data


def get_yesterday_revenue(company_id: str) -> float:
    supabase = get_supabase()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    result = supabase.table("vigia_entries").select("amount").eq("company_id", company_id).eq("type", "revenue").eq("entry_date", yesterday).execute()
    return sum(r["amount"] for r in result.data)


def get_avg_revenue_7days(company_id: str) -> float:
    supabase = get_supabase()
    start_date = (date.today() - timedelta(days=7)).isoformat()
    result = supabase.table("vigia_entries").select("amount").eq("company_id", company_id).eq("type", "revenue").gte("entry_date", start_date).execute()
    revenues = [r["amount"] for r in result.data]
    return sum(revenues) / 7 if revenues else 0


def get_cash_balance(company_id: str) -> float:
    supabase = get_supabase()
    result = supabase.table("vigia_entries").select("amount", "type").eq("company_id", company_id).execute()
    cash = 0
    for r in result.data:
        if r["type"] == "revenue":
            cash += r["amount"]
        else:
            cash -= r["amount"]
    return cash


def get_overdue_receivables(company_id: str) -> tuple[int, float]:
    supabase = get_supabase()
    result = supabase.table("vigia_receivables").select("amount").eq("company_id", company_id).eq("status", "pending").execute()
    count = len(result.data)
    total = sum(r["amount"] for r in result.data)
    return count, total


def calculate_daily_burn(fixed_cost_avg: float, avg_daily_revenue: float, variable_percent: float) -> float:
    return (fixed_cost_avg / 30) + (avg_daily_revenue * variable_percent / 100)


def calculate_runway(cash_balance: float, daily_burn: float) -> int:
    if daily_burn <= 0:
        return 999
    return int(cash_balance / daily_burn)


def create_entry(data: dict) -> dict:
    supabase = get_supabase()
    result = supabase.table("vigia_entries").insert(data).execute()
    return result.data[0]


def update_company(company_id: str, data: dict) -> dict | None:
    supabase = get_supabase()
    result = supabase.table("vigia_companies").update(data).eq("id", company_id).execute()
    if result.data:
        return result.data[0]
    return None


def format_currency(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


async def process_operation(update: Update, context: ContextTypes.DEFAULT_TYPE, user: dict, message_text: str | None) -> None:
    chat_id = update.effective_chat.id
    company_id = user.get("company_id")
    first_name = user.get("first_name", "Usuário")
    
    if not company_id:
        await context.bot.send_message(chat_id=chat_id, text="❌ Erro: empresa não encontrada")
        return
    
    company = get_company_by_id(company_id)
    if not company:
        await context.bot.send_message(chat_id=chat_id, text="❌ Erro: empresa não encontrada")
        return
    
    if not message_text:
        await context.bot.send_message(chat_id=chat_id, text="❌ Mensagem vazia")
        return
    
    text = message_text.lower().strip()
    
    if text.startswith("/start"):
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Olá, {first_name}! Bem-vindo de volta.\n\n"
                 "Comandos disponíveis:\n"
                 "/receita - Registrar faturamento do dia\n"
                 "/despesa - Registrar despesa do dia\n"
                 "/relatorio - Ver situação atual\n"
                 "/ajuda - Ver todos os comandos"
        )
    elif text.startswith("/receita"):
        await _handle_revenue(context, chat_id, company, text)
    elif text.startswith("/despesa"):
        await _handle_expense(context, chat_id, company, text)
    elif text.startswith("/relatorio"):
        await _handle_report(context, chat_id, company, first_name)
    elif text.startswith("/ajuda") or text.startswith("/help"):
        await _handle_help(context, chat_id)
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="❓ Comando não reconhecido.\n\n"
                 "Use /ajuda para ver os comandos disponíveis."
        )


async def _handle_revenue(context: ContextTypes.DEFAULT_TYPE, chat_id: int, company: dict, text: str) -> None:
    parts = text.split()
    if len(parts) < 2:
        await context.bot.send_message(
            chat_id=chat_id,
            text="📝 Para registrar uma receita, digite:\n/receita 1500"
        )
        return
    
    try:
        value_str = parts[1].replace(",", ".")
        amount = float(value_str)
        if amount <= 0:
            raise ValueError()
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="❌ Valor inválido. Use: /receita 1500")
        return
    
    create_entry({
        "company_id": company["id"],
        "entry_date": date.today().isoformat(),
        "amount": amount,
        "type": "revenue",
        "source": "manual"
    })
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ Receita de {format_currency(amount)} registrada!"
    )


async def _handle_expense(context: ContextTypes.DEFAULT_TYPE, chat_id: int, company: dict, text: str) -> None:
    parts = text.split()
    if len(parts) < 2:
        await context.bot.send_message(
            chat_id=chat_id,
            text="📝 Para registrar uma despesa, digite:\n/despesa 500"
        )
        return
    
    try:
        value_str = parts[1].replace(",", ".")
        amount = float(value_str)
        if amount <= 0:
            raise ValueError()
    except ValueError:
        await context.bot.send_message(chat_id=chat_id, text="❌ Valor inválido. Use: /despesa 500")
        return
    
    create_entry({
        "company_id": company["id"],
        "entry_date": date.today().isoformat(),
        "amount": amount,
        "type": "expense",
        "source": "manual"
    })
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ Despesa de {format_currency(amount)} registrada!"
    )


async def _handle_report(context: ContextTypes.DEFAULT_TYPE, chat_id: int, company: dict, user_name: str = "Cliente") -> None:
    company_id = company["id"]
    
    yesterday_revenue = get_yesterday_revenue(company_id)
    avg_revenue = get_avg_revenue_7days(company_id)
    cash_balance = get_cash_balance(company_id)
    overdue_count, overdue_total = get_overdue_receivables(company_id)
    
    fixed_cost = company.get("fixed_cost_avg", 0) or 0
    variable_percent = company.get("variable_cost_percent", 30) or 30
    
    daily_burn = calculate_daily_burn(fixed_cost, avg_revenue, variable_percent)
    runway_days = calculate_runway(cash_balance, daily_burn)
    
    if avg_revenue > 0:
        variation = ((yesterday_revenue - avg_revenue) / avg_revenue) * 100
        variation_str = f"{variation:+.0f}%"
    else:
        variation_str = "N/A"
    
    message = f"📊 Bom dia, {user_name}!\n\n"
    
    if yesterday_revenue > 0:
        message += f"Ontem você faturou {format_currency(yesterday_revenue)} ({variation_str} vs média da semana).\n"
    else:
        message += "Ontem não houve faturamento registrado.\n"
    
    if overdue_count > 0:
        message += f"{overdue_count} cliente(s) em atraso somando {format_currency(overdue_total)}.\n"
    
    message += f"Seu caixa atual é {format_currency(cash_balance)}.\n\n"
    
    if runway_days <= 10:
        message += f"🔴 Atenção: em {runway_days} dias você entra no vermelho se nada mudar."
    elif runway_days <= 20:
        message += f"⚠️ Atenção: em {runway_days} dias você fica abaixo do mínimo."
    else:
        message += f"✅ Tudo OK! Você tem {runway_days} dias de caixa."
    
    await context.bot.send_message(chat_id=chat_id, text=message)


async def _handle_help(context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> None:
    message = """📋 *Ajuda - VigIA*

💰 *Receitas*
/receita 1500
→ Registra o faturamento do dia

📤 *Despesas*
/despesa 500
→ Registra uma despesa do dia

📊 *Relatório*
/relatorio
→ Envia relatório detalhado do momento

📑 *Outros*
/receber - Cadastrar cliente em atraso (em breve)
/ajuda - Mostra esta mensagem

💡 *Dica:* Use /relatorio a qualquer momento para ver a situação do seu caixa!"""

    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
