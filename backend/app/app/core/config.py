from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8080",
        "http://0.0.0.0",
        "http://0.0.0.0:80",
    ]


settings = Settings()
