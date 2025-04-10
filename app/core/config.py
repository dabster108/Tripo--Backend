import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Basic settings
    APP_NAME: str = "Tripo API"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS settings
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Groq AI Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-8b-8192")  # Default model
    GROQ_MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", "1024"))
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", "1.0"))

    @property
    def groq_config(self) -> dict:
        """Returns Groq configuration as a dictionary"""
        return {
            "api_key": self.GROQ_API_KEY,
            "model": self.GROQ_MODEL,
            "max_tokens": self.GROQ_MAX_TOKENS,
            "temperature": self.GROQ_TEMPERATURE
        }

# Create settings instance
settings = Settings()

# Validation checks
if not settings.GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is required in environment variables")

# Debug logging
print(f"ALLOWED_ORIGINS: {settings.ALLOWED_ORIGINS}")
print(f"ENVIRONMENT: {settings.ENVIRONMENT}")
print(f"Groq Model: {settings.GROQ_MODEL}")
print(f"DATABASE_URL: {settings.DATABASE_URL}")  # Added database URL logging