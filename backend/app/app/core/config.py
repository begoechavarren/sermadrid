# TODO: remove
import os
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings

print("BACKEND_CORS_ORIGINS from env:", os.getenv("BACKEND_CORS_ORIGINS"))


class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: List[str] = Field(..., env="BACKEND_CORS_ORIGINS")


settings = Settings()
