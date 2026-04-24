'''
So this file holds all the Ai logic! including:
- Gemini
- Elevenlabs stt & tts
'''

import os
from typing import Iterator
from google import genai
from google.genai import types
import dotenv
from io import BytesIO
import yaml
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play as elevenlabs_play

dotenv.load_dotenv()

gemini_client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY")
)
elevenlabs_client = ElevenLabs(
    api_key=os.environ.get("ELEVENLABS_API_KEY")
)

with open("personas.yaml", "r") as f:
    BASE_SYSTEM_PROPMT = yaml.safe_load(f)["BASE_SYSTEM_PROMPT"]

class GenerationError(Exception):
    ...

class Character:
    def __init__(self, system_instruction: str, voice_id:str="JBFqnCBsd6RMkjVDRZzb", model: str = 'gemini-2.5-flash-lite', prepend_default: bool = True, history: list[dict] = None, base_prompt: str = BASE_SYSTEM_PROPMT):
        self._system_instruction = system_instruction
        self._base_prompt = base_prompt
        self._history = history
        self._model = model

        self.voice_id=voice_id

        if prepend_default:
            self._system_instruction = self._base_prompt + self._system_instruction

        config = types.GenerateContentConfig(
            system_instruction = self._system_instruction
        )

        self.chat = gemini_client.chats.create(model=self._model, config=config, history=self._history)

    def generate(self, message:str):
        for i in range(3):
            try:
                return self.chat.send_message(message).text
            except:
                time.sleep(1)
                continue
        raise GenerationError('llm error')
    
    def __call__(self, message: str):
        llm_response = self.generate(message)
        if not isinstance(llm_response, str):
            raise TypeError("Expected str got: {type(llm_response)}\n\nthis is in the __call__ function of sdk.Character")
        audio_bytes = self.tts(llm_response)
        self.play(audio_bytes)

    def tts(self, text: str):   
        for i in range(3):
            try:
                padded_text = f"... {text} ..."
                return elevenlabs_client.text_to_speech.convert(
                    text=padded_text,
                    voice_id=self.voice_id,
                    model_id="eleven_flash_v2_5",
                    output_format="mp3_44100_128"
                )
            except:
                time.sleep(1)
                continue
            raise GenerationError("tts error")

    def stt(self, audio: BytesIO):
        for i in range(3):
            try:
                return elevenlabs_client.speech_to_text.convert(
                    file=audio,
                    model_id="scribe_v2",
                    tag_audio_events=True,
                    language_code="eng",
                    diarize=True
                ).text
            except:
                time.sleep(1)
                continue
            raise GenerationError("stt error")

    def play(self, audio: bytes | Iterator[bytes]):
        elevenlabs_play(audio)

    @property
    def history(self):
        return self.chat.get_history()
    
    @history.setter
    def history(self, value):
        self.__init__(
            self._system_instruction,
            self._base_prompt,
            model=self._model,
            prepend_default=False,
            history=value
        )

    @history.deleter
    def history(self):
        self.__init__(
            self._system_instruction,
            self._base_prompt,
            model=self._model,
            prepend_default=False,
            history=[]
        )

    @property
    def system_instruction(self):
        return self._system_instruction

    @system_instruction.setter
    def system_instruction(self, value):
        self.__init__(
            value,
            self._base_prompt,
            model=self._model,
            prepend_default=False,
            history=self.history
        )
    
    @system_instruction.deleter
    def system_instruction(self):
        self.__init__(
            self._base_prompt,
            self._base_prompt,
            model=self._model,
            prepend_default=True,
            history=self.history
        )

    @property
    def model(self):
        return self._model
    
    @model.setter
    def model(self, value):
        self.__init__(
            self._system_instruction,
            self._base_prompt,
            prepend_default=False,
            model=value,
            history=self.history
        )

    @model.deleter
    def model(self):
        self.__init__(
            self._system_instruction,
            self._base_prompt,
            prepend_default=False,
            model='gemini-2.5-flash-lite',
            history=self.history
        )


