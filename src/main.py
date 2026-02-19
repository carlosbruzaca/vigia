from fastapi import FastAPI, Request
import logging
import sys

# Configurar logging para stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="VigIA API")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "vigia"}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"WEBHOOK RECEBIDO: {data}")
        
        # Extrair informações básicas
        if "message" in data:
            message = data["message"]
            chat_id = message.get("chat", {}).get("id")
            text = message.get("text", "")
            logger.info(f"Mensagem de {chat_id}: {text}")
        
        return {"ok": True}
    except Exception as e:
        logger.error(f"ERRO NO WEBHOOK: {str(e)}")
        return {"ok": False, "error": str(e)}

@app.get("/webhook-info")
async def webhook_info():
    """Endpoint de teste para verificar se a API está respondendo"""
    return {"status": "webhook ativo", "endpoint": "/webhook (POST)"}