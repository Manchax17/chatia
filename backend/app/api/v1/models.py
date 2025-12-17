"""Modelos Pydantic para la API"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class Message(BaseModel):
    """Mensaje en el chat"""
    role: str = Field(..., description="Rol: 'user' o 'assistant'")
    content: str = Field(..., description="Contenido del mensaje")

class ChatRequest(BaseModel):
    """Request para el endpoint de chat"""
    model_config = {"protected_namespaces": ()}
    message: str = Field(..., description="Mensaje del usuario")
    chat_history: Optional[List[Message]] = Field(default=[], description="Historial de conversación")
    include_wearable: bool = Field(default=True, description="Incluir datos del wearable")
    llm_provider: Optional[str] = Field(default=None, description="Proveedor LLM (openai, ollama, huggingface)")
    model_name: Optional[str] = Field(default=None, description="Nombre del modelo específico")

class ChatResponse(BaseModel):
    """Response del endpoint de chat"""
    model_config = {"protected_namespaces": ()}
    response: str = Field(..., description="Respuesta del asistente")
    tools_used: List[Dict] = Field(default=[], description="Herramientas utilizadas")
    wearable_data: Optional[Dict] = Field(default=None, description="Datos del wearable usados")
    model_info: Dict = Field(default={}, description="Información del modelo usado")
    success: bool = Field(..., description="Si la operación fue exitosa")
    error: Optional[str] = Field(default=None, description="Mensaje de error si hubo")

class ChatResponse(BaseModel):
    """Response del endpoint de chat"""
    response: str = Field(..., description="Respuesta del asistente")
    tools_used: List[Dict] = Field(default=[], description="Herramientas utilizadas")
    wearable_data: Optional[Dict] = Field(default=None, description="Datos del wearable usados")
    model_info: Dict = Field(default={}, description="Información del modelo usado")
    success: bool = Field(..., description="Si la operación fue exitosa")
    error: Optional[str] = Field(default=None, description="Mensaje de error si hubo")

class WearableDataResponse(BaseModel):
    """Response con datos del wearable"""
    data: Dict = Field(..., description="Datos del dispositivo")
    success: bool = Field(..., description="Si la operación fue exitosa")
    error: Optional[str] = Field(default=None, description="Mensaje de error si hubo")
    message: Optional[str] = Field(default=None, description="Mensaje informativo")

class SyncResponse(BaseModel):
    """Response de sincronización"""
    message: str = Field(..., description="Mensaje de resultado")
    data: Optional[Dict] = Field(default=None, description="Datos sincronizados")
    success: bool = Field(..., description="Si la operación fue exitosa")

class ModelListResponse(BaseModel):
    """Lista de modelos disponibles"""
    provider: str
    models: List[str] = Field(default=[])
    current_model: str = Field(default="")
    available: bool

class ConnectionInfoResponse(BaseModel):
    """Información de conexión del wearable"""
    method: str
    using_mock: bool
    available_methods: List[str]
    mi_fitness_configured: bool
    bluetooth_configured: bool