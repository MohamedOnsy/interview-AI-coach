import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. Make sure you have a .env file "
        "with GEMINI_API_KEY=your_key_here in the project root."
    )

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"