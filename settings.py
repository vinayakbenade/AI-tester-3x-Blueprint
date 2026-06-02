from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    base_url: str
    timeout: int = 30
    retries: int = 3
    backoff_seconds: float = 0.5
    env: str = "local"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
