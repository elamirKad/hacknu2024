import asyncio
import queue
import concurrent.futures
import os
import uuid
from datetime import datetime

import azure.cognitiveservices.speech as speechsdk
import websockets.exceptions
from dotenv import load_dotenv
from pydub import AudioSegment
from pydub.playback import play

from vtube_plugin.connector import VTubeConnector


class AsyncSpeechSynthesizer:
    def __init__(self, connector: VTubeConnector = None):
        load_dotenv()
        self.speech_key = os.getenv("AZURE_API")
        self.service_region = os.getenv("AZURE_REGION")
        self.speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.service_region)
        self.speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm)
        # self.speech_config.speech_synthesis_voice_name = "en-US-AshleyNeural"
        self.speech_config.speech_synthesis_voice_name = "en-US-JaneNeural"
        self.is_playing = False
        self.playback_queue = queue.Queue()
        self.audio_generation_lock = asyncio.Lock()
        self.connector = connector
        print(self.connector, self.connector.audio_processor)

    async def enqueue_text(self, text: str):
        async with self.audio_generation_lock:
            unique_filename = f"{uuid.uuid4().hex}.wav"
            await self.speech_synthesis_to_wav_file(text, unique_filename)
            self.playback_queue.put(unique_filename)
        if not self.is_playing:
            asyncio.create_task(self.play_audio_from_queue())

    async def play_audio_from_queue(self):
        try:
            while True:
                self.is_playing = True
                file_path = self.playback_queue.get()
                if file_path is None:
                    break
                await self.connector.audio_processor.play_and_send_data(file_path)
                self.playback_queue.task_done()
                # os.remove(file_path)
            self.is_playing = False
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")
            await self.connector.reauthenticate()
            await self.play_audio_from_queue()

    async def speech_synthesis_to_wav_file(self, text: str, file_name: str) -> None:
        """Performs speech synthesis to a WAV file with adjustable pitch."""

        file_config = speechsdk.audio.AudioOutputConfig(filename=file_name)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=file_config)

        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
            <voice name="{self.speech_config.speech_synthesis_voice_name}">
                <prosody>
                    {text}
                </prosody>
            </voice>
        </speak>
        """

        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, lambda: speech_synthesizer.speak_ssml_async(ssml).get())
