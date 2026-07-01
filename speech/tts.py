import io
from gtts import gTTS

def text_to_speech(text: str, lang: str = "en") -> bytes:
    if not text.strip():
        return b""
    tts = gTTS(text=text, lang=lang, slow=False)
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return audio_bytes.getvalue()