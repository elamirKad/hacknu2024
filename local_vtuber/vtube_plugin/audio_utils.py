import asyncio
import wave
from concurrent.futures import ThreadPoolExecutor
import audioop
import pyaudio


class AudioProcessor:
    def __init__(self, communicator):
        print("Initializing AudioProcessor")
        self.communicator = communicator
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.current_rms = 0

    async def update_parameter(self, parameter_id, value, weight=None, mode="set", face_found=False):
        if not (-1000000 <= value <= 1000000):
            raise ValueError("Value must be a floating-point number between -1000000 and 1000000.")

        parameter_values = [{"id": parameter_id, "value": value}]

        msg = self.communicator.get_msg_template()
        msg["messageType"] = "InjectParameterDataRequest"
        msg["data"] = {
            "faceFound": face_found,
            "mode": mode,
            "parameterValues": parameter_values
        }
        # print(f"Sending parameter update: {msg}")
        result = await self.communicator.send(msg)

    async def translate_audio_to_mouth_movement(self, rms):
        max_rms = 32768
        scaled_value = min(max((rms / max_rms) * 100, 0), 100)
        scaled_value = int(scaled_value * 1.7)
        await self.update_parameter("CustomSoundTracker", scaled_value)

    def play_audio(self, audio_file_path):
        wf = wave.open(audio_file_path, 'rb')

        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        frames_per_buffer=1024)

        chunk_size = 1024
        data = wf.readframes(chunk_size)
        while data:
            stream.write(data)

            self.current_rms = audioop.rms(data, wf.getsampwidth())

            data = wf.readframes(chunk_size)

        stream.stop_stream()
        stream.close()
        p.terminate()
        self.current_rms = 0

    async def play_and_send_data(self, audio_file_path):
        future = self.executor.submit(self.play_audio, audio_file_path)
        try:
            while not future.done():
                await self.translate_audio_to_mouth_movement(int(self.current_rms))
                await asyncio.sleep(0.02)
        except Exception as e:
            print(f"Error during playback and parameter update: {str(e)}")
            raise e
