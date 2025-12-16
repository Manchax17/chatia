"""Endpoints para gestión de chats e historial"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

from ...database.chat_db import ChatMemoryDB

router = APIRouter()

# ==================== MODELOS ====================

class ChatCreateRequest(BaseModel):
    """Request para crear un nuevo chat"""
    title: Optional[str] = None
    wearable_data: Optional[dict] = None


class ChatMessageRequest(BaseModel):
    """Request para añadir un mensaje"""
    role: str  # "user" o "assistant"
    content: str
    model_used: Optional[str] = None
    tools_used: Optional[list] = None


class ChatListItem(BaseModel):
    """Item en lista de chats"""
    chat_id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int
    preview: str


class ChatGrouped(BaseModel):
    """Chats agrupados por período"""
    today: List[ChatListItem] = []
    this_week: List[ChatListItem] = []
    this_month: List[ChatListItem] = []
    older: List[ChatListItem] = []


class ChatDetailResponse(BaseModel):
    """Detalle completo de un chat"""
    chat_id: str
    title: str
    created_at: str
    updated_at: str
    messages: list
    wearable_data_snapshot: Optional[dict] = None
    summary: Optional[str] = None


class ChatHistoryResponse(BaseModel):
    """Historial de mensajes"""
    chat_id: str
    history: list


# ==================== ENDPOINTS ====================

@router.post("/chats/create", response_model=dict)
async def create_chat(request: ChatCreateRequest):
    """
    Crea un nuevo chat
    
    - Si no se proporciona título, se genera uno genérico
    - Guarda snapshot de datos wearable
    """
    try:
        title = request.title or f"Chat {datetime.now().strftime('%d/%m %H:%M')}"
        chat_id = ChatMemoryDB.create_chat(title, request.wearable_data)
        
        return {
            "success": True,
            "chat_id": chat_id,
            "title": title,
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chats", response_model=ChatGrouped)
async def list_chats_grouped():
    """
    Lista todos los chats agrupados por período
    
    - Hoy (últimas 24 horas)
    - Esta semana (últimos 7 días)
    - Este mes (últimos 30 días)
    - Anterior (más de 30 días)
    """
    try:
        now = datetime.now()
        chats = ChatMemoryDB.list_chats(limit=1000)
        
        today = []
        this_week = []
        this_month = []
        older = []
        
        for chat in chats:
            updated = datetime.fromisoformat(chat["updated_at"])
            days_ago = (now - updated).days
            
            if days_ago == 0:
                today.append(chat)
            elif days_ago <= 7:
                this_week.append(chat)
            elif days_ago <= 30:
                this_month.append(chat)
            else:
                older.append(chat)
        
        return ChatGrouped(
            today=today,
            this_week=this_week,
            this_month=this_month,
            older=older
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chats/{chat_id}", response_model=ChatDetailResponse)
async def get_chat(chat_id: str):
    """Obtiene detalle completo de un chat"""
    try:
        chat = ChatMemoryDB.get_chat(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat no encontrado")
        
        return ChatDetailResponse(
            chat_id=chat.chat_id,
            title=chat.title,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            messages=[msg.to_dict() for msg in chat.messages],
            wearable_data_snapshot=chat.wearable_data_snapshot,
            summary=chat.summary
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chats/{chat_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(chat_id: str):
    """Obtiene solo el historial de mensajes de un chat"""
    try:
        history = ChatMemoryDB.get_chat_history(chat_id)
        if history is None:
            raise HTTPException(status_code=404, detail="Chat no encontrado")
        
        return ChatHistoryResponse(
            chat_id=chat_id,
            history=history
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chats/{chat_id}/message", response_model=dict)
async def add_message(
    chat_id: str,
    request: Optional[ChatMessageRequest] = None,
    role: str = Query(None),
    content: str = Query(None),
    model_used: Optional[str] = Query(None),
    tools_used: Optional[list] = Query(None)
):
    """
    Añade un mensaje a un chat
    Acepta: body JSON o parámetros de query
    """
    try:
        # Extraer datos del body o de los query params
        if request:
            role = request.role
            content = request.content
            model_used = request.model_used
            tools_used = request.tools_used or []
        
        if not role or not content:
            raise HTTPException(status_code=400, detail="role y content son requeridos")
        
        success = ChatMemoryDB.add_message(chat_id, role, content, model_used, tools_used)
        
        if not success:
            raise HTTPException(status_code=404, detail="Chat no encontrado")
        
        return {
            "success": True,
            "message": f"Mensaje añadido a {chat_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/chats/{chat_id}/title", response_model=dict)
async def update_chat_title(chat_id: str, title: str):
    """Actualiza el título de un chat"""
    try:
        success = ChatMemoryDB.update_chat_title(chat_id, title)
        
        if not success:
            raise HTTPException(status_code=404, detail="Chat no encontrado")
        
        return {
            "success": True,
            "chat_id": chat_id,
            "new_title": title
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/chats/{chat_id}/summary", response_model=dict)
async def update_chat_summary(chat_id: str, summary: str):
    """Actualiza el resumen de un chat"""
    try:
        success = ChatMemoryDB.update_chat_summary(chat_id, summary)
        
        if not success:
            raise HTTPException(status_code=404, detail="Chat no encontrado")
        
        return {
            "success": True,
            "chat_id": chat_id,
            "summary": summary
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chats/{chat_id}", response_model=dict)
async def delete_chat(chat_id: str):
    """Elimina un chat"""
    try:
        success = ChatMemoryDB.delete_chat(chat_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Chat no encontrado")
        
        return {
            "success": True,
            "message": f"Chat {chat_id} eliminado"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MEMORIA ====================

@router.post("/memory/global/{key}", response_model=dict)
async def save_global_memory(key: str, value: dict):
    """Guarda valor en memoria global"""
    try:
        ChatMemoryDB.save_global_memory(key, value)
        return {"success": True, "key": key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/global/{key}")
async def get_global_memory(key: str, default: Optional[str] = None):
    """Obtiene valor de memoria global"""
    try:
        value = ChatMemoryDB.get_global_memory(key, default)
        return {"key": key, "value": value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/memory/session/{session_id}/{key}", response_model=dict)
async def save_session_memory(session_id: str, key: str, value: dict):
    """Guarda valor en memoria de sesión"""
    try:
        ChatMemoryDB.save_session_memory(session_id, key, value)
        return {"success": True, "session_id": session_id, "key": key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/session/{session_id}/{key}")
async def get_session_memory(session_id: str, key: str, default: Optional[str] = None):
    """Obtiene valor de memoria de sesión"""
    try:
        value = ChatMemoryDB.get_session_memory(session_id, key, default)
        return {"session_id": session_id, "key": key, "value": value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/session/{session_id}")
async def get_all_session_memory(session_id: str):
    """Obtiene toda la memoria de una sesión"""
    try:
        memory = ChatMemoryDB.get_all_session_memory(session_id)
        return {"session_id": session_id, "memory": memory}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
