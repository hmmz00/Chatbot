import os
import logging
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)

# Config
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-20b")
ALLOWED_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Kamu adalah Hmmz Bot, asisten serba bisa yang siap membantu. "
        "Gunakan nama 'Hmmz Bot' saat menjawab. Gaya komunikasi: singkat, jelas, tanpa basa-basi."
    )
}

# FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://hmmz00.github.io/test01/",
            "X-Title": "Hmmz Bot"
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

        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        reply = data.get("choices", [{}])[0].get("message", {}).get("content", "⚠️ Tidak ada jawaban.")
        return {"reply": reply}
    except Exception as e:
        logging.error(f"Chat error: {e}")
        return {"error": "⚠️ Terjadi kesalahan server"}