from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
logger.debug("Loading .env file...")
load_dotenv()
logger.debug(f"GROQ_API_KEY present: {'GROQ_API_KEY' in os.environ}")
logger.debug(f"GROQ_API_KEY value: {os.environ.get('GROQ_API_KEY', 'Not set')}")

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Restaurant Reservation Agent"
    
    # LLM Settings
    LLM_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"
    
    # JWT Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        case_sensitive = True

# Create settings instance
settings = Settings()
logger.debug(f"Settings LLM_API_KEY: {settings.LLM_API_KEY}")
logger.debug(f"Settings LLM_API_URL: {settings.LLM_API_URL}") 