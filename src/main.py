from contextlib import asynccontextmanager
import logging
import sys
from fastapi import FastAPI, Request, Response
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from src.config import settings
from src.services.scheduler import start_scheduler, shutdown_scheduler
from src.handlers.router import route_message
from src.handlers.daily_report import send_daily_reports

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

telegram_app: Application | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global telegram_app
    
    logger.info("Iniciando VigIA...")
    
    start_scheduler()
    from apscheduler.triggers.cron import CronTrigger
    from src.services.scheduler import scheduler
    scheduler.add_job(
        send_daily_reports,
        CronTrigger(hour=7, minute=0),
        id="daily_report",
        replace_existing=True
    )
    logger.info("Scheduler configurado - relatório diário às 7h")
    
    telegram_app = Application.builder().token(settings.telegram_bot_token).build()
    
    telegram_app.add_handler(CommandHandler("start", route_message))
    telegram_app.add_handler(CommandHandler("ajuda", route_message))
    telegram_app.add_handler(CommandHandler("help", route_message))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_message))
    
    await telegram_app.initialize()
    await telegram_app.start()
    logger.info("Telegram bot iniciado")
    
    yield
    
    await telegram_app.stop()
    shutdown_scheduler()
    logger.info("VigIA encerrado")


app = FastAPI(title="VigIA", lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "vigia"}


@app.post("/webhook")
async def telegram_webhook(request: Request) -> Response:
    if not telegram_app:
        return Response(status_code=503, content="Bot não inicializado")
    
    try:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        
        if update:
            await telegram_app.process_update(update)
        
        return Response(status_code=200, content="OK")
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return Response(status_code=500, content=str(e))


@app.get("/webhook-info")
async def webhook_info():
    return {
        "status": "ativo",
        "endpoint": "/webhook (POST)",
        "scheduler": "relatório diário às 7h"
    }
