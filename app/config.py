from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import List
import json

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Lanceraa API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    ALLOWED_ORIGINS: str  # Changed to str to handle raw string from env

    @property
    def origins(self) -> List[str]:
        try:
            # Try to parse as JSON first
            return json.loads(self.ALLOWED_ORIGINS)
        except json.JSONDecodeError:
            # Fallback to comma-separated string
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()