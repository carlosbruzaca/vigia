from fastapi import FastAPI, Request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="VigIA API")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "vigia"}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    logger.info(f"MENSAGEM RECEBIDA: {data}")
    return {"ok": True}