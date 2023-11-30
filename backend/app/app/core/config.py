from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost", "http://localhost:8080"]


settings = Settings()
