import logging
from datetime import date
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


def calculate_cash_balance(company_id: str) -> float:
    entries = get_entries_by_company(company_id)
    cash = 0
    for entry in entries:
        if entry["type"] == "revenue":
            cash += entry["amount"]
        elif entry["type"] == "expense":
            cash -= entry["amount"]
    return cash


def calculate_monthly_burn(company_id: str) -> float:
    from datetime import date, timedelta
    supabase = get_supabase()
    start_date = (date.today() - timedelta(days=30)).isoformat()
    result = supabase.table("vigia_entries").select("amount").eq("company_id", company_id).eq("type", "expense").gte("entry_date", start_date).execute()
    total = sum(entry["amount"] for entry in result.data)
    return total


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
        await _handle_report(context, chat_id, company)
    elif text.startswith("/ajuda"):
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


async def _handle_report(context: ContextTypes.DEFAULT_TYPE, chat_id: int, company: dict) -> None:
    cash_balance = calculate_cash_balance(company["id"])
    monthly_burn = calculate_monthly_burn(company["id"])
    fixed_cost = company.get("fixed_cost_avg", 0)
    cash_minimum = company.get("cash_minimum", 5000)
    
    days_of_cash = monthly_burn / 30 if monthly_burn > 0 else 999
    runway_days = cash_balance / (monthly_burn / 30) if monthly_burn > 0 else 999
    
    message = f"📊 *Relatório - {company.get('name', 'Empresa')}*\n\n"
    message += f"💰 Caixa atual: {format_currency(cash_balance)}\n"
    message += f"🔥 Burn rate mensal: {format_currency(monthly_burn)}\n"
    message += f"📅 Custos fixos: {format_currency(fixed_cost)}/mês\n"
    message += f"🛡️ Caixa mínimo: {format_currency(cash_minimum)}\n"
    
    if cash_balance < cash_minimum:
        message += f"\n⚠️ *Atenção: Caixa abaixo do mínimo!*"
    
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")


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
