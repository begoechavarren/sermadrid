from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: List[str] = Field(..., env="BACKEND_CORS_ORIGINS")


settings = Settings()
