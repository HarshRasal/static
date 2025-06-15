# AI Companion MVP - FastAPI Version (Python + ElevenLabs + OpenAI)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import openai
import requests
import os
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# === CONFIGURATION ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
voice_id = "Rachel"  # Choose your ElevenLabs voice name

# === INITIALIZE APP ===
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# === MEMORY ===
user_memory = {
    "name": "Harry",
    "likes": ["reading", "Vaidehi", "AI projects"]
}

class Message(BaseModel):
    message: str

def get_openai_response(user_input, memory):
    prompt = f"You are a warm, emotionally intelligent female AI assistant. Remember these facts: {memory}. Now respond empathetically to: {user_input}"

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful, caring female AI companion."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

def get_elevenlabs_voice(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": elevenlabs_api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        with open("response.mp3", "wb") as f:
            f.write(response.content)
        return "response.mp3"
    else:
        return None

@app.get("/")
async def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(message: Message):
    memory_str = ", ".join([f"{k}: {v}" for k, v in user_memory.items()])
    ai_response = get_openai_response(message.message, memory_str)
    voice_path = get_elevenlabs_voice(ai_response)
    return JSONResponse(content={"text": ai_response, "audio": voice_path})

@app.get("/audio")
async def get_audio():
    return FileResponse("response.mp3", media_type="audio/mpeg")
