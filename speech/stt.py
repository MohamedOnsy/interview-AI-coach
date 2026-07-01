import io
import speech_recognition as sr

def speech_to_text(audio_bytes: bytes, language: str = "en-US") -> str:
    """
    Transcribe audio bytes (from st.audio_input) using Google Speech Recognition.
    """
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language=language)
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return ""