import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    OUTPUT_DIR: str = "outputs"
    IMAGES_DIR: str = "outputs/images"

settings = Settings()
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
os.makedirs(settings.IMAGES_DIR, exist_ok=True)
