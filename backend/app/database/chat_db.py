"""Sistema de almacenamiento de chats y memoria"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass, asdict, field

# Directorio de datos
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "chats"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CHATS_FILE = DATA_DIR / "chats.json"
MEMORY_FILE = DATA_DIR / "memory.json"


@dataclass
class Message:
    """Mensaje individual en el chat"""
    role: str  # "user" o "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    model_used: Optional[str] = None
    tools_used: List[Dict] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data):
        return Message(**data)


@dataclass
class Chat:
    """Registro de un chat completo"""
    chat_id: str
    title: str  # Título generado o personalizado
    created_at: str
    updated_at: str
    messages: List[Message] = field(default_factory=list)
    wearable_data_snapshot: Optional[Dict] = None  # Snapshot de datos wearable al crear
    summary: Optional[str] = None  # Resumen del chat

    def to_dict(self):
        return {
            "chat_id": self.chat_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": [msg.to_dict() if isinstance(msg, Message) else msg for msg in self.messages],
            "wearable_data_snapshot": self.wearable_data_snapshot,
            "summary": self.summary
        }

    @staticmethod
    def from_dict(data):
        messages = [
            Message.from_dict(msg) if isinstance(msg, dict) else msg
            for msg in data.get("messages", [])
        ]
        return Chat(
            chat_id=data["chat_id"],
            title=data["title"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            messages=messages,
            wearable_data_snapshot=data.get("wearable_data_snapshot"),
            summary=data.get("summary")
        )


class ChatMemoryDB:
    """Base de datos de chats y memoria conversacional"""

    @staticmethod
    def _load_chats() -> Dict[str, Chat]:
        """Carga todos los chats desde archivo"""
        if not CHATS_FILE.exists():
            return {}
        
        try:
            with open(CHATS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {chat_id: Chat.from_dict(chat) for chat_id, chat in data.items()}
        except Exception as e:
            print(f"⚠️ Error cargando chats: {e}")
            return {}

    @staticmethod
    def _save_chats(chats: Dict[str, Chat]):
        """Guarda todos los chats en archivo"""
        try:
            with open(CHATS_FILE, 'w', encoding='utf-8') as f:
                data = {chat_id: chat.to_dict() for chat_id, chat in chats.items()}
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error guardando chats: {e}")

    @staticmethod
    def _load_memory() -> Dict:
        """Carga memoria global y por sesión"""
        if not MEMORY_FILE.exists():
            return {
                "global": {"user_preferences": {}, "learned_habits": []},
                "sessions": {}
            }
        
        try:
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error cargando memoria: {e}")
            return {"global": {}, "sessions": {}}

    @staticmethod
    def _save_memory(memory: Dict):
        """Guarda memoria en archivo"""
        try:
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Error guardando memoria: {e}")

    @staticmethod
    def create_chat(title: str, wearable_data: Optional[Dict] = None) -> str:
        """Crea nuevo chat y retorna su ID"""
        import uuid
        chat_id = str(uuid.uuid4())[:8]
        
        now = datetime.now().isoformat()
        chat = Chat(
            chat_id=chat_id,
            title=title,
            created_at=now,
            updated_at=now,
            wearable_data_snapshot=wearable_data
        )
        
        chats = ChatMemoryDB._load_chats()
        chats[chat_id] = chat
        ChatMemoryDB._save_chats(chats)
        
        print(f"✅ Chat creado: {chat_id}")
        return chat_id

    @staticmethod
    def add_message(chat_id: str, role: str, content: str, model_used: Optional[str] = None, tools_used: Optional[List[Dict]] = None) -> bool:
        """Añade mensaje a un chat"""
        chats = ChatMemoryDB._load_chats()
        
        if chat_id not in chats:
            print(f"❌ Chat {chat_id} no encontrado")
            return False
        
        message = Message(
            role=role,
            content=content,
            model_used=model_used,
            tools_used=tools_used or []
        )
        
        chats[chat_id].messages.append(message)
        chats[chat_id].updated_at = datetime.now().isoformat()
        
        ChatMemoryDB._save_chats(chats)
        return True

    @staticmethod
    def get_chat(chat_id: str) -> Optional[Chat]:
        """Obtiene un chat completo"""
        chats = ChatMemoryDB._load_chats()
        return chats.get(chat_id)

    @staticmethod
    def get_chat_history(chat_id: str) -> List[Dict]:
        """Obtiene historial de mensajes de un chat"""
        chat = ChatMemoryDB.get_chat(chat_id)
        if not chat:
            return []
        
        return [msg.to_dict() for msg in chat.messages]

    @staticmethod
    def list_chats(limit: int = 100) -> List[Dict]:
        """Lista todos los chats ordenados por fecha (más recientes primero)"""
        chats = ChatMemoryDB._load_chats()
        sorted_chats = sorted(
            chats.values(),
            key=lambda x: x.updated_at,
            reverse=True
        )[:limit]
        
        return [
            {
                "chat_id": chat.chat_id,
                "title": chat.title,
                "created_at": chat.created_at,
                "updated_at": chat.updated_at,
                "message_count": len(chat.messages),
                "preview": chat.messages[0].content[:100] if chat.messages else ""
            }
            for chat in sorted_chats
        ]

    @staticmethod
    def delete_chat(chat_id: str) -> bool:
        """Elimina un chat"""
        chats = ChatMemoryDB._load_chats()
        
        if chat_id in chats:
            del chats[chat_id]
            ChatMemoryDB._save_chats(chats)
            print(f"✅ Chat {chat_id} eliminado")
            return True
        
        return False

    @staticmethod
    def update_chat_title(chat_id: str, new_title: str) -> bool:
        """Actualiza título del chat"""
        chats = ChatMemoryDB._load_chats()
        
        if chat_id not in chats:
            return False
        
        chats[chat_id].title = new_title
        chats[chat_id].updated_at = datetime.now().isoformat()
        ChatMemoryDB._save_chats(chats)
        return True

    @staticmethod
    def update_chat_summary(chat_id: str, summary: str) -> bool:
        """Actualiza resumen del chat"""
        chats = ChatMemoryDB._load_chats()
        
        if chat_id not in chats:
            return False
        
        chats[chat_id].summary = summary
        ChatMemoryDB._save_chats(chats)
        return True

    # ==================== MEMORIA ====================

    @staticmethod
    def save_global_memory(key: str, value):
        """Guarda valor en memoria global"""
        memory = ChatMemoryDB._load_memory()
        memory["global"][key] = value
        ChatMemoryDB._save_memory(memory)

    @staticmethod
    def get_global_memory(key: str, default=None):
        """Obtiene valor de memoria global"""
        memory = ChatMemoryDB._load_memory()
        return memory["global"].get(key, default)

    @staticmethod
    def save_session_memory(session_id: str, key: str, value):
        """Guarda valor en memoria de sesión"""
        memory = ChatMemoryDB._load_memory()
        if session_id not in memory["sessions"]:
            memory["sessions"][session_id] = {}
        memory["sessions"][session_id][key] = value
        ChatMemoryDB._save_memory(memory)

    @staticmethod
    def get_session_memory(session_id: str, key: str, default=None):
        """Obtiene valor de memoria de sesión"""
        memory = ChatMemoryDB._load_memory()
        if session_id not in memory["sessions"]:
            return default
        return memory["sessions"][session_id].get(key, default)

    @staticmethod
    def get_all_session_memory(session_id: str) -> Dict:
        """Obtiene toda la memoria de una sesión"""
        memory = ChatMemoryDB._load_memory()
        return memory["sessions"].get(session_id, {})

    @staticmethod
    def clear_session_memory(session_id: str) -> bool:
        """Limpia memoria de una sesión"""
        memory = ChatMemoryDB._load_memory()
        if session_id in memory["sessions"]:
            del memory["sessions"][session_id]
            ChatMemoryDB._save_memory(memory)
            return True
        return False
