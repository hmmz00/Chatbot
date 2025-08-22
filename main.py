from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os

# Inisialisasi FastAPI
app = FastAPI()

# Ambil API Key dari environment di Vercel
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Model fix sesuai permintaan
MODEL_NAME = "openai/gpt-oss-20b"

# Prompt sistem
SYSTEM_PROMPT = {
    "role": "system",
    "content": "Kamu adalah Hmmz Bot, jawab singkat, jelas, dan langsung ke poin."
}

# Schema untuk request
class ChatRequest(BaseModel):
    message: str

# Root endpoint (biar tidak 404)
@app.get("/")
async def root():
    return {
        "name": "Hmmz Bot API",
        "status": "ok",
        "endpoints": ["/ping", "/chat"]
    }

# Endpoint health check
@app.get("/ping")
async def ping():
    return {"status": "alive"}

# Endpoint chat
@app.post("/chat")
async def chat(req: ChatRequest):
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY belum diset di environment.")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            SYSTEM_PROMPT,
            {"role": "user", "content": req.message}
        ],
        "max_tokens": 1000,
        "temperature": 0.7,
    }

    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        reply = data.get("choices", [{}])[0].get("message", {}).get("content")
        if not reply:
            reply = "⚠️ Model tidak memberikan jawaban."

        return {"reply": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")