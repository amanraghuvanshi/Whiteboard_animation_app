# utils/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Gemini API for text generation
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    # Google Cloud settings for Imagen v4
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    # Application settings
    OUTPUT_DIR: str = "outputs"
    IMAGES_DIR: str = "outputs/images"
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    
    # Imagen v4 specific settings
    IMAGEN_MODEL: str = "imagen-3.0-generate-001"  # Latest available model
    MAX_IMAGE_RETRIES: int = 3
    IMAGE_GENERATION_TIMEOUT: int = 30

settings = Settings()

# Create directories
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
os.makedirs(settings.IMAGES_DIR, exist_ok=True)

# Debug logging setup
import logging
if settings.DEBUG_MODE:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
