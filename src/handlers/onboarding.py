from telegram import Update
from telegram.ext import ContextTypes
from src.services import supabase as supabase_service
from src.models.user import UserCreate


async def start_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    telegram_id = update.effective_user.id
    name = update.effective_user.first_name
    
    user = UserCreate(telegram_id=telegram_id, name=name, state="onboarding_name")
    supabase_service.create_user(user)
    
    await update.message.reply_text("Qual é o seu nome completo?")


async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE, user) -> None:
    name = update.message.text
    supabase_service.update_user(user.telegram_id, {"name": name, "state": "onboarding_company"})
    
    await update.message.reply_text(f"Prazer, {name}! Qual é o nome da sua empresa?")


async def handle_company(update: Update, context: ContextTypes.DEFAULT_TYPE, user) -> None:
    company_name = update.message.text
    
    company = supabase_service.create_company({"name": company_name, "burn_rate": 0.0, "cash": 0.0})
    supabase_service.update_user(user.telegram_id, {"company_id": company.id, "state": "operation"})
    
    await update.message.reply_text(
        f"Empresa '{company_name}' criada com sucesso!\n\n"
        "Agora você pode:\n"
        "- Adicionar entradas/saídas\n"
        "- Ver o status da empresa\n"
        "- Receber relatórios diários"
    )
