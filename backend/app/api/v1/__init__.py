from fastapi import APIRouter
from . import chat, wearable, models

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(wearable.router, prefix="/wearable", tags=["wearable"])

__all__ = ['api_router']