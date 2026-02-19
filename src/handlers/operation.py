from telegram import Update
from telegram.ext import ContextTypes
from src.services import supabase as supabase_service
from src.models.entries import EntryCreate
from src.utils.burn_rate import calculate_runway, calculate_monthly_burn
from src.utils.formatters import format_company_status


async def handle_operation(update: Update, context: ContextTypes.DEFAULT_TYPE, user) -> None:
    text = update.message.text.lower()
    company = supabase_service.get_company(user.company_id)
    
    if not company:
        await update.message.reply_text("Empresa não encontrada.")
        return
    
    if text.startswith("/status"):
        entries = supabase_service.get_entries_by_company(company.id)
        entries_dict = [{"amount": e.amount, "entry_type": e.entry_type} for e in entries]
        burn_rate = calculate_monthly_burn(entries_dict)
        runway = calculate_runway(company.cash, burn_rate)
        
        await update.message.reply_text(
            format_company_status(company.model_dump(), burn_rate, runway),
            parse_mode="Markdown"
        )
    elif text.startswith("/entrada"):
        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text("Uso: /entrada <valor>")
            return
        try:
            amount = float(parts[1].replace(",", "."))
            entry = EntryCreate(
                company_id=company.id,
                entry_type="income",
                amount=amount
            )
            supabase_service.create_entry(entry)
            supabase_service.update_company(company.id, {"cash": company.cash + amount})
            await update.message.reply_text(f"Entrada de R$ {amount} registrada!")
        except ValueError:
            await update.message.reply_text("Valor inválido.")
    elif text.startswith("/saida") or text.startswith("/despesa"):
        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text("Uso: /saida <valor>")
            return
        try:
            amount = float(parts[1].replace(",", "."))
            entry = EntryCreate(
                company_id=company.id,
                entry_type="expense",
                amount=amount
            )
            supabase_service.create_entry(entry)
            supabase_service.update_company(company.id, {"cash": company.cash - amount})
            await update.message.reply_text(f"Saída de R$ {amount} registrada!")
        except ValueError:
            await update.message.reply_text("Valor inválido.")
    else:
        await update.message.reply_text(
            "Comandos disponíveis:\n"
            "/status - Ver status da empresa\n"
            "/entrada <valor> - Adicionar entrada\n"
            "/saida <valor> - Adicionar despesa"
        )
