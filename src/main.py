from contextlib import asynccontextmanager
from fastapi import FastAPI
from telegram.ext import Application
from apscheduler.triggers.cron import CronTrigger
from src.config import settings
from src.services.scheduler import start_scheduler, shutdown_scheduler
from src.handlers.daily_report import send_daily_reports


telegram_app: Application | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global telegram_app
    
    start_scheduler()
    
    from src.services.scheduler import scheduler
    scheduler.add_job(
        send_daily_reports,
        CronTrigger(hour=9, minute=0),
        id="daily_report",
        replace_existing=True
    )
    
    telegram_app = Application.builder().token(settings.telegram_bot_token).build()
    
    from src.handlers.router import handle_start, handle_message
    from telegram.ext import CommandHandler, MessageHandler, filters
    
    telegram_app.add_handler(CommandHandler("start", handle_start))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    await telegram_app.initialize()
    await telegram_app.start()
    
    yield
    
    await telegram_app.stop()
    shutdown_scheduler()


app = FastAPI(title="Vigia", lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
