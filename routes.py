import os
import tempfile
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from auth import user_tokens
from chat import chat

router = APIRouter()

@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    tmp_path = os.path.join(tempfile.gettempdir(), "recorded_audio.webm")
    with open(tmp_path, "wb") as f:
        f.write(await audio.read())
    with open(tmp_path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(tmp_path), f.read()),
            model="whisper-large-v3", language="en", response_format="text",
        )
    return JSONResponse({"transcript": transcription.strip()})

@router.post("/chat")
async def chat_endpoint(data: dict):
    if "default" not in user_tokens:
        return JSONResponse({"reply": "Please connect your Gmail first.", "auth": False})
    user_message = data.get("message", "")
    if not user_message:
        return JSONResponse({"reply": "I didn't catch that.", "auth": True})
    reply = chat(user_message, user_tokens["default"])
    return JSONResponse({"reply": reply, "auth": True})

@router.get("/", response_class=HTMLResponse)
async def serve_login():
    if "default" in user_tokens:
        return RedirectResponse("/app")
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@router.get("/app", response_class=HTMLResponse)
async def serve_app():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()