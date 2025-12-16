from fastapi import APIRouter
from . import chat, wearable, chats, models

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(wearable.router, prefix="/wearable", tags=["wearable"])
api_router.include_router(chats.router, prefix="", tags=["chats"])

__all__ = ['api_router']