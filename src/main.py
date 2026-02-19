from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="VigIA API")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "vigia"}

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    print(f"Mensagem recebida: {data}")
    
    # Por enquanto só retorna OK
    return {"ok": True}