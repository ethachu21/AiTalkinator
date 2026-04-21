'''
Huge thanks to my guy gemini for making this file possible! (im not an audio nerd)
'''
import sounddevice as sd
import numpy as np
import soundfile as sf
import io
from typing import Optional

class Recorder:
    def __init__(self, samplerate: int = 44100, channels: int = 1):
        self.samplerate = samplerate
        self.channels = channels
        self.stream: Optional[sd.InputStream] = None
        self._audio_data = []

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"Error in recording: {status}")
        self._audio_data.append(indata.copy())

    def start(self):
        self._audio_data = []
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            callback=self._callback
        )
        self.stream.start()

    def stop(self) -> io.BytesIO:
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if not self._audio_data:
            return io.BytesIO()

        audio_np = np.concatenate(self._audio_data, axis=0)
        
        buffer = io.BytesIO()
        sf.write(buffer, audio_np, self.samplerate, format='WAV')
        buffer.seek(0)
        return buffer

_global_recorder = Recorder()

def record():
    """Starts recording from the default microphone."""
    _global_recorder.start()

def stop_recording() -> io.BytesIO:
    """Stops recording and returns a BytesIO object containing the WAV data."""
    return _global_recorder.stop()
