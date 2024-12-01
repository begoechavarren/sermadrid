import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.app.api.v1.router import api_router
from app.app.core.config import settings
from app.app.core.dependencies import is_data_loaded, load_data


async def retry_load_data(duration_hours: int = 12, retry_delay: int = 10):
    end_time = time.time() + (duration_hours * 3600)
    attempt = 1

    while time.time() < end_time:
        if load_data(method="s3"):
            print("Data loaded successfully")
            return
        print(f"Attempt {attempt} failed. Retrying in {retry_delay} seconds...")
        await asyncio.sleep(retry_delay)
        attempt += 1

    print(f"Failed to load data after {duration_hours} hours")


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(retry_load_data())
    yield


app = FastAPI(lifespan=lifespan)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "data_loaded": is_data_loaded()}
