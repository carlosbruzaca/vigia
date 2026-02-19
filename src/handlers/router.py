from telegram import Update
from telegram.ext import ContextTypes
from src.services import supabase as supabase_service
from src.services.telegram import send_message


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    user = supabase_service.get_user_by_telegram_id(telegram_id)
    
    if user is None:
        await update.message.reply_text("Bem-vindo! Vou guiar você pelo cadastro.")
        from src.handlers.onboarding import start_onboarding
        await start_onboarding(update, context)
    else:
        await update.message.reply_text(f"Olá, {user.name}! Como posso ajudar?")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    user = supabase_service.get_user_by_telegram_id(telegram_id)
    
    if user is None:
        await handle_start(update, context)
        return
    
    state = user.state
    
    if state == "onboarding_name":
        from src.handlers.onboarding import handle_name
        await handle_name(update, context, user)
    elif state == "onboarding_company":
        from src.handlers.onboarding import handle_company
        await handle_company(update, context, user)
    elif state == "operation":
        from src.handlers.operation import handle_operation
        await handle_operation(update, context, user)
    else:
        await update.message.reply_text("Use /start para começar.")
