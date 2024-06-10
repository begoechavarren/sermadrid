# backend/app/app/main.py

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.app.api.v1.router import api_router
from app.app.core.config import settings

app = FastAPI()

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)
