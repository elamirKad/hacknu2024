from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

from audio import AsyncSpeechSynthesizer
from vtube_plugin.connector import VTubeConnector

app = FastAPI()


class TextRequest(BaseModel):
    text: str


connector = None
audio_generator = None


@app.on_event("startup")
async def startup_event():
    global connector, audio_generator
    connector = VTubeConnector()
    await connector.start()
    audio_generator = AsyncSpeechSynthesizer(connector)


@app.post("/synthesize/")
async def synthesize_text(request: TextRequest):
    print(f"Received request to synthesize text: {request.text}")
    global audio_generator

    await audio_generator.enqueue_text(request.text)

    await audio_generator.audio_generation_lock.acquire()
    audio_generator.audio_generation_lock.release()

    while audio_generator.is_playing or not audio_generator.playback_queue.empty():
        await asyncio.sleep(0.1)

    return {"message": "Synthesis complete for text", "text": request.text}
