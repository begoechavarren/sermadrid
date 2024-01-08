from fastapi import APIRouter

from app.app.api.v1.endpoints import items

api_router = APIRouter()
api_router.include_router(items.router, prefix="/api/v1/items", tags=["items"])
