from elevenlabs.client import ElevenLabs

client = ElevenLabs(
    api_key="sk_1660fb850f4b0a63910902b87535525ec3999835a5370faf"
)

VOICE_MAP = {
    "Friendly": "nPczCjzI2devNBz1zQrb",   # Brian
    "Formal": "JBFqnCBsd6RMkjVDRZzb",     # George
    "Strict": "pNInz6obpgDQGcFmaJgB",     # Adam
    "Casual": "iP95p4xoKVk53GoZ742B"      # Chris (لو موجود في Workspace)
}

def text_to_speech(
    text: str,
    personality: str = "Formal",
    lang: str = "en"
) -> bytes:

    if not text.strip():
        return b""

    voice_id = VOICE_MAP.get(
        personality,
        VOICE_MAP["Formal"]
    )

    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        text=text
    )

    return b"".join(audio)