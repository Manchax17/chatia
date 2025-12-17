"""Endpoints para gestión de chats e historial"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta, timezone
try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None
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
    model_config = {"protected_namespaces": ()}
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
    yesterday: List[ChatListItem] = []
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
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chats/create_sample", response_model=dict)
async def create_sample_chat(days_ago: int = 7, title: Optional[str] = None):
    """Crea un chat de ejemplo con una antigüedad determinada (en días).

    Útil para pruebas y demostraciones (por ejemplo crear un chat de hace una semana o de hace un día).
    """
    try:
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        created_at = (now - timedelta(days=days_ago)).isoformat()
        title = title or f"Chat de prueba - hace {days_ago} días"

        chat_id = ChatMemoryDB.create_chat(title)

        # Ajustar timestamps del chat
        chats = ChatMemoryDB._load_chats()
        if chat_id in chats:
            chat = chats[chat_id]
            chat.created_at = created_at
            chat.updated_at = created_at

            # Añadir mensajes de ejemplo con timestamps correspondientes
            msgs = [
                ("user", "Hola, ¿cómo estás?"),
                ("assistant", "¡Hola! Estoy listo para ayudarte con tus datos de actividad y salud."),
                ("user", "Calcula mi IMC"),
                ("assistant", "Tu IMC es 24.0. Esto es un ejemplo generico para el chat de prueba.")
            ]

            # Remover mensajes existentes y añadir con timestamp
            chat.messages = []
            for i, (role, content) in enumerate(msgs):
                ts = (now - timedelta(days=days_ago, minutes=(len(msgs)-i)*5)).isoformat()
                chat.messages.append({
                    "role": role,
                    "content": content,
                    "timestamp": ts,
                    "model_used": None,
                    "tools_used": []
                })

            # Guardar cambios
            ChatMemoryDB._save_chats(chats)

            return {"success": True, "chat_id": chat_id, "days_ago": days_ago}
        else:
            raise HTTPException(status_code=500, detail="No se pudo crear el chat de prueba")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chats/create_samples", response_model=dict)
async def create_sample_chats():
    """Crea varios chats de ejemplo (7 días, 30 días, 365 días) para pruebas."""
    try:
        results = []
        for days in (7, 30, 365):
            resp = await create_sample_chat(days_ago=days, title=f"Chat ejemplo - hace {days} días")
            results.append({"days_ago": days, "success": resp.get('success', False), "chat_id": resp.get('chat_id')})
        return {"success": True, "created": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chats", response_model=ChatGrouped)
async def list_chats_grouped(
    user_tz: Optional[str] = Query(None, description="IANA timezone (e.g. Europe/Madrid). If provided, grouping by days will use this timezone."),
    user_tz_offset: Optional[int] = Query(None, description="Timezone offset in minutes as returned by new Date().getTimezoneOffset() (e.g. 300 for UTC-5)")
):
    """
    Lista todos los chats agrupados por período

    - Hoy (según la hora local del usuario)
    - Esta semana (últimos 7 días)
    - Este mes (últimos 30 días)
    - Anterior (más de 30 días)
    """
    try:
        # Hora base en UTC y lista de chats
        now_utc = datetime.now(timezone.utc)
        chats = ChatMemoryDB.list_chats(limit=1000)

        # Preparar variables
        offset_minutes = None
        use_offset = False
        user_tzinfo = None

        # Preferimos IANA tz si viene; si no, usamos offset si viene
        if user_tz and ZoneInfo is not None:
            try:
                user_tzinfo = ZoneInfo(user_tz)
                now_user = now_utc.astimezone(user_tzinfo)
            except Exception:
                now_user = now_utc
                user_tzinfo = None
        elif user_tz_offset is not None:
            try:
                offset_minutes = int(user_tz_offset)
                now_user = now_utc - timedelta(minutes=offset_minutes)
                use_offset = True
            except Exception:
                now_user = now_utc
        else:
            now_user = now_utc

        today = []
        yesterday = []
        this_week = []
        this_month = []
        older = []

        for chat in chats:
            # Parse updated_at e interpretar como UTC si no tiene tz
            updated = datetime.fromisoformat(chat["updated_at"])
            if updated.tzinfo is None:
                updated = updated.replace(tzinfo=timezone.utc)

            # Calcular la hora "local" del usuario según la preferencia
            if use_offset and offset_minutes is not None:
                updated_user = (updated.astimezone(timezone.utc) - timedelta(minutes=offset_minutes))
            elif user_tzinfo is not None:
                updated_user = updated.astimezone(user_tzinfo)
            else:
                updated_user = updated.astimezone(timezone.utc)

            days_ago = (now_user.date() - updated_user.date()).days

            if days_ago == 0:
                today.append(chat)
            elif days_ago == 1:
                yesterday.append(chat)
            elif 1 < days_ago <= 7:
                this_week.append(chat)
            elif 7 < days_ago <= 30:
                this_month.append(chat)
            else:
                older.append(chat)

        return ChatGrouped(
            today=today,
            yesterday=yesterday,
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


# ==================== RAG / Vector Store ====================
@router.post("/rag/reindex", response_model=dict)
async def rag_reindex_all():
    """Resetea y reindexa la colección de RAG con los mensajes actuales"""
    try:
        from ..rag.vector_store import vector_store
        if not vector_store:
            raise HTTPException(status_code=500, detail="Vector store no inicializado")

        # Resetear (incluye re-poblar conocimiento inicial)
        vector_store.reset()

        chats = ChatMemoryDB._load_chats()
        added = 0
        for chat_id, chat in chats.items():
            for msg in chat.messages:
                try:
                    vector_store.add_documents(
                        texts=[msg.content],
                        metadatas=[{"chat_id": chat_id, "role": msg.role, "timestamp": msg.timestamp}]
                    )
                    added += 1
                except Exception as ie:
                    print(f"⚠️ No se pudo indexar mensaje {chat_id}: {ie}")

        return {"success": True, "added": added}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
