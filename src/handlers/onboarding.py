import logging
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


def update_company(company_id: str, data: dict) -> dict | None:
    supabase = get_supabase()
    result = supabase.table("vigia_companies").update(data).eq("id", company_id).execute()
    if result.data:
        return result.data[0]
    return None


def update_user(user_id: str, data: dict) -> dict | None:
    supabase = get_supabase()
    result = supabase.table("vigia_users").update(data).eq("id", user_id).execute()
    if result.data:
        return result.data[0]
    return None


def get_current_step(company: dict, onboarding_step: int) -> int:
    if onboarding_step > 0 and onboarding_step <= 4:
        return onboarding_step
    
    if company.get("fixed_cost_avg") is None or company.get("fixed_cost_avg") == 0:
        return 1
    if company.get("variable_cost_percent") is None or company.get("variable_cost_percent") == 30:
        return 2
    if company.get("cash_minimum") is None or company.get("cash_minimum") == 5000:
        return 3
    return 4


def parse_number(value: str) -> tuple[bool, float | None, str]:
    cleaned = value.replace("R", "").replace("r", "").replace("$", "").replace(" ", "").replace(".", "")
    cleaned = cleaned.replace(",", ".")
    try:
        return True, float(cleaned), ""
    except ValueError:
        return False, None, "Por favor, digite apenas números (ex: 5000)"


def validate_input(value: float, step: int) -> tuple[bool, str]:
    if step == 1:
        if value <= 0:
            return False, "O custo fixo deve ser maior que zero"
    elif step == 2:
        if not (0 <= value <= 100):
            return False, "A porcentagem deve estar entre 0 e 100"
    elif step == 3:
        if value < 0:
            return False, "O caixa mínimo não pode ser negativo"
    return True, ""


def format_currency(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


async def process_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE, user: dict, message_text: str | None) -> None:
    chat_id = update.effective_chat.id
    company_id = user.get("company_id")
    
    if not company_id:
        await context.bot.send_message(chat_id=chat_id, text="❌ Erro: empresa não encontrada")
        return
    
    company = get_company_by_id(company_id)
    if not company:
        await context.bot.send_message(chat_id=chat_id, text="❌ Erro: empresa não encontrada")
        return
    
    current_step = get_current_step(company, user.get("onboarding_step", 0))
    
    if not message_text or message_text.startswith("/"):
        await _send_onboarding_question(context, chat_id, current_step, company)
        return
    
    valid, value, error_msg = parse_number(message_text)
    if not valid:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Não entendi esse valor.\n\n{error_msg}")
        return
    
    valid, error_msg = validate_input(value, current_step)
    if not valid:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ {error_msg}\n\nTente novamente:")
        return
    
    if current_step == 1:
        update_company(company_id, {"fixed_cost_avg": value})
        update_user(user["id"], {"onboarding_step": 2, "current_action": "awaiting_variable_cost"})
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Custo fixo registrado: {format_currency(value)}\n\n"
                 f"📊 Agora, qual porcentagem do seu faturamento vira custo variável?\n"
                 f"(impostos, comissões, matéria-prima)\n\n"
                 f"Digite um número de 0 a 100:"
        )
    elif current_step == 2:
        update_company(company_id, {"variable_cost_percent": value})
        update_user(user["id"], {"onboarding_step": 3, "current_action": "awaiting_cash_minimum"})
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Custo variável: {value}%\n\n"
                 f"🛡️ Por último: qual valor mínimo de caixa você quer manter para se sentir seguro?\n"
                 f"(ex: 10000 para cobrir 2 meses de custo fixo)\n\n"
                 f"Digite o valor:"
        )
    elif current_step == 3:
        update_company(company_id, {"cash_minimum": value})
        update_user(user["id"], {"onboarding_step": 4, "state": "active", "current_action": None})
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ Caixa mínimo: {format_currency(value)}\n\n"
                 f"🎉 Configuração completa!\n\n"
                 f"Amanhã cedo você recebe seu primeiro relatório.\n\n"
                 f"Comandos disponíveis:\n"
                 f"/receita - Registrar faturamento do dia\n"
                 f"/despesa - Registrar despesa do dia\n"
                 f"/relatorio - Ver situação atual agora\n"
                 f"/ajuda - Ver todos os comandos"
        )


async def _send_onboarding_question(context: ContextTypes.DEFAULT_TYPE, chat_id: int, step: int, company: dict) -> None:
    if step == 1:
        await context.bot.send_message(
            chat_id=chat_id,
            text="💰 Vamos configurar sua vigilância financeira!\n\n"
                 "Qual seu custo fixo mensal médio?\n"
                 "(Inclua aluguel, salários, internet, etc.)\n\n"
                 "Digite só o número em reais (ex: 5000)"
        )
    elif step == 2:
        await context.bot.send_message(
            chat_id=chat_id,
            text="📊 Agora, qual porcentagem do seu faturamento vira custo variável?\n"
                 "(impostos, comissões, matéria-prima)\n\n"
                 "Digite um número de 0 a 100:"
        )
    elif step == 3:
        await context.bot.send_message(
            chat_id=chat_id,
            text="🛡️ Por último: qual valor mínimo de caixa você quer manter para se sentir seguro?\n"
                 "(ex: 10000 para cobrir 2 meses de custo fixo)\n\n"
                 "Digite o valor:"
        )
    elif step == 4:
        await context.bot.send_message(
            chat_id=chat_id,
            text="🎉 Configuração completa!\n\n"
                 "Amanhã cedo você recebe seu primeiro relatório.\n\n"
                 "Comandos disponíveis:\n"
                 "/receita - Registrar faturamento do dia\n"
                 "/despesa - Registrar despesa do dia\n"
                 "/relatorio - Ver situação atual agora\n"
                 "/ajuda - Ver todos os comandos"
        )
