import logging
from telegram import Update
from telegram.ext import ContextTypes, Application
from src.database import get_supabase, get_supabase_admin

logger = logging.getLogger(__name__)


def get_user_by_chat_id(chat_id: int) -> dict | None:
    supabase = get_supabase()
    result = supabase.table("vigia_users").select("*").eq("chat_id", chat_id).execute()
    if result.data:
        return result.data[0]
    return None


def get_company_by_id(company_id: str) -> dict | None:
    supabase = get_supabase()
    result = supabase.table("vigia_companies").select("*").eq("id", company_id).execute()
    if result.data:
        return result.data[0]
    return None


def create_company(first_name: str, chat_id: int) -> dict:
    supabase = get_supabase_admin()
    company_name = f"{first_name} - Empresa"
    result = supabase.table("vigia_companies").insert({
        "name": company_name,
        "status": "trial",
        "plan": "early_adopter",
        "fixed_cost_avg": 0,
        "variable_cost_percent": 30,
        "cash_minimum": 5000,
        "chat_id": chat_id
    }).execute()
    return result.data[0]


def create_user(chat_id: int, telegram_id: int, first_name: str, company_id: str) -> dict:
    supabase = get_supabase_admin()
    result = supabase.table("vigia_users").insert({
        "chat_id": chat_id,
        "telegram_id": telegram_id,
        "first_name": first_name,
        "state": "new",
        "onboarding_step": 0,
        "company_id": company_id
    }).execute()
    return result.data[0]


def update_last_interaction(user_id: str) -> None:
    supabase = get_supabase()
    supabase.table("vigia_users").update({
        "last_interaction_at": "now()"
    }).eq("id", user_id).execute()


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Bem-vindo! Vou guiar você pelo cadastro.")


async def route_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    telegram_user_id = update.effective_user.id
    first_name = update.effective_user.first_name or "Usuário"
    last_name = update.effective_user.last_name
    username = update.effective_user.username
    message_text = update.message.text if update.message else None
    message_id = update.message.message_id if update.message else None
    date = update.message.date.timestamp() if update.message else None

    if not chat_id:
        logger.warning(f"chat_id ausente na mensagem de {telegram_user_id}")
        return

    user = get_user_by_chat_id(chat_id)

    if user is None:
        try:
            company = create_company(first_name, chat_id)
            user = create_user(chat_id, telegram_user_id, first_name, company["id"])
            logger.info(f"Novo usuário criado: {user['id']}, empresa: {company['id']}")
        except Exception as e:
            logger.error(f"Erro ao criar usuário/empresa: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Erro técnico. Tente novamente em alguns minutos."
            )
            return

    try:
        update_last_interaction(user["id"])
    except Exception:
        pass

    state = user.get("state", "new")
    message_text_lower = message_text.lower().strip() if message_text else ""
    
    if message_text_lower.startswith("/ajuda") or message_text_lower.startswith("/help"):
        await context.bot.send_message(
            chat_id=chat_id,
            text="📋 *Ajuda - VigIA*\n\n"
                 "💰 /receita <valor> - Registrar faturamento\n"
                 "📤 /despesa <valor> - Registrar despesa\n"
                 "📊 /relatorio - Ver situação atual\n"
                 "📑 /ajuda - Esta mensagem\n\n"
                 "💡 Use /relatorio para ver a situação do seu caixa!",
            parse_mode="Markdown"
        )
        return

    if state == "new":
        if message_text_lower.startswith("/start"):
            from src.database import get_supabase
            get_supabase().table("vigia_users").update({"state": "onboarding"}).eq("id", user["id"]).execute()
            await _delegate_to_onboarding(update, context, user, message_text)
        else:
            await _send_welcome_message(update, context, user)
    elif state == "onboarding":
        await _delegate_to_onboarding(update, context, user, message_text)
    elif state == "active":
        await _delegate_to_operation(update, context, user, message_text)
    elif state == "paused":
        await context.bot.send_message(
            chat_id=chat_id,
            text="⏸️ Sua conta está temporariamente suspensa. Entre em contato com o suporte."
        )
    elif state == "blocked":
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Sua conta foi cancelada. Para mais informações, entre em contato."
        )
    else:
        logger.warning(f"Estado desconhecido: {state}, tratando como new")
        await _delegate_to_onboarding(update, context, user, message_text)


async def _send_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE, user: dict) -> None:
    chat_id = update.effective_chat.id
    first_name = update.effective_user.first_name or "Usuário"
    
    message = f"""👋 Olá, {first_name}! Bem-vindo ao VigIA!

🛡️ Sou seu guardião financeiro. Estou aqui para garantir que você saiba o que está acontecendo com o caixa da sua empresa - antes que o pior problema apareça: ficar sem dinheiro.

💡 Como funciona:
• Todo dia você me informa suas receitas e despesas
• Todo dia 7h eu te mando um relatório com a situação do caixa
• Se algo precisar de atenção, eu te aviso antes

🚀 Para começar, é rápido! Preciso só de 3 informações:
1. Seu custo fixo mensal
2. Quanto % do faturamento vira custo variável
3. Quanto você quer ter de caixa mínimo

Digite /start quando quiser começar!"""
    
    await context.bot.send_message(chat_id=chat_id, text=message)


async def _delegate_to_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE, user: dict, message_text: str | None) -> None:
    from src.handlers.onboarding import process_onboarding
    await process_onboarding(update, context, user, message_text)


async def _delegate_to_operation(update: Update, context: ContextTypes.DEFAULT_TYPE, user: dict, message_text: str | None) -> None:
    from src.handlers.operation import process_operation
    await process_operation(update, context, user, message_text)
