import asyncio
import json
import queue
import concurrent.futures
import os
import uuid
from datetime import datetime

import requests
import websockets.exceptions

from vtube_plugin.connector import VTubeConnector


class AsyncSpeechSynthesizer:
    def __init__(self, connector: VTubeConnector = None):
        self.api = ""
        self.is_playing = False
        self.playback_queue = asyncio.Queue()  # Changed to asyncio.Queue
        self.audio_generation_lock = asyncio.Lock()
        self.connector = connector
        print(self.connector, self.connector.audio_processor)

    async def enqueue_text(self, text: str):
        async with self.audio_generation_lock:
            unique_filename = f"{uuid.uuid4().hex}.wav"
            await self.speech_synthesis_to_wav_file(text, unique_filename)
            await self.playback_queue.put(unique_filename)  # Changed to async put
        if not self.is_playing:
            asyncio.create_task(self.play_audio_from_queue())

    async def play_audio_from_queue(self):
        try:
            self.is_playing = True
            while not self.playback_queue.empty():
                file_path = await self.playback_queue.get()  # Changed to async get
                await self.connector.audio_processor.play_and_send_data(file_path)
                self.playback_queue.task_done()
                os.remove(file_path)
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")
            await self.connector.reauthenticate()
        finally:
            self.is_playing = False

    async def speech_synthesis_to_wav_file(self, text: str, file_name: str, gender: str = "female", audio_format: str = "wav") -> None:
        """Performs speech synthesis to a WAV file with adjustable pitch."""

        if gender == "male":
            voice = "kk-KZ-DauletNeural"
        elif gender == "female":
            voice = "kk-KZ-AigulNeural"
        else:
            raise ValueError("Gender must be defined")

        headers = {
            "x-listnr-token": self.api,
            "Content-Type": "application/json"
        }

        base_url = "https://bff.listnr.tech/api/tts/v1/"
        endpoint = base_url + "convert-text"

        body = json.dumps({
            "voice": voice,
            "ssml": f"<speak><p>{text}</p></speak>",
            "audioFormat": audio_format
        })

        response = requests.post(endpoint, headers=headers, data=body)
        response_data = response.json()
        print(response_data)

        if 'url' in response_data:
            audio_url = response_data['url']
            audio_response = requests.get(audio_url)

            with open(file_name, "wb") as audio_file:
                audio_file.write(audio_response.content)
