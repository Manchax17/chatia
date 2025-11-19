"""Endpoints del chat"""

from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime
from typing import Optional

from ...llm.agent import ChatFitAgent
from ...llm.llm_factory import LLMFactory
from ...iot.xiaomi_client import xiaomi_client
from .models import ChatRequest, ChatResponse, ModelListResponse

router = APIRouter()

# Cache de datos del wearable
_wearable_cache = {"data": None, "timestamp": None}

# Cache de modelos por sesión
_session_models = {}

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, request_obj: Request):
    """
    Endpoint principal del chat
    
    - Recibe mensaje del usuario
    - Incluye datos del reloj Xiaomi si está disponible
    - Usa agente LLM con herramientas
    - Retorna respuesta enriquecida
    """
    try:
        # Obtener ID de sesión (puedes usar IP o un token si lo tienes)
        session_id = request_obj.client.host if request_obj.client else "default"
        
        # Si se especifica un proveedor o modelo, actualizar la sesión
        llm_provider = request.llm_provider or _session_models.get(session_id, {}).get("provider", "ollama")
        model_name = request.model_name or _session_models.get(session_id, {}).get("model", "gemma3:1b")
        
        # Guardar en caché de sesión
        _session_models[session_id] = {
            "provider": llm_provider,
            "model": model_name
        }
        
        # Obtener datos del wearable si se solicita
        wearable_data = None
        if request.include_wearable:
            # Usar cache si es reciente (< 5 minutos)
            from datetime import timedelta
            now = datetime.now()
            
            if (_wearable_cache["data"] is None or 
                _wearable_cache["timestamp"] is None or
                now - _wearable_cache["timestamp"] > timedelta(minutes=5)):
                
                wearable_data = await xiaomi_client.get_daily_summary()
                _wearable_cache["data"] = wearable_data
                _wearable_cache["timestamp"] = now
            else:
                wearable_data = _wearable_cache["data"]
        
        # Crear agente con configuración
        agent = ChatFitAgent(
            wearable_data=wearable_data,
            llm_provider=llm_provider,
            model_name=model_name
        )
        
        # Convertir historial a formato dict
        chat_history = [msg.dict() for msg in request.chat_history]
        
        # Procesar mensaje
        result = agent.chat(
            message=request.message,
            chat_history=chat_history
        )
        
        return ChatResponse(
            response=result["response"],
            tools_used=result.get("tools_used", []),
            wearable_data=wearable_data,
            model_info=result.get("model_info", {}),
            success=result["success"],
            error=result.get("error")
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Error en el chat: {str(e)}"
        )

@router.get("/models", response_model=list)
async def list_available_models():
    """
    Lista todos los modelos disponibles por proveedor
    """
    try:
        from ...config import settings
        
        available_models = LLMFactory.get_available_models()
        
        response = []
        
        for provider, models in available_models.items():
            is_available = LLMFactory.validate_provider(provider)
            
            # Asegurar que current_model sea siempre una cadena
            current_model = ""
            if provider == 'ollama':
                current_model = settings.ollama_model or ""
            elif provider == 'huggingface':
                current_model = settings.huggingface_model or ""
            elif provider == 'openai':
                current_model = settings.openai_model or ""
            elif provider == 'groq':  # Si agregaste Groq
                current_model = settings.groq_model or ""
            
            # Asegurar que models sea siempre una lista de cadenas
            if not isinstance(models, list):
                models = []
            
            # Filtrar solo cadenas válidas
            filtered_models = []
            for model in models:
                if isinstance(model, str) and model.strip():
                    filtered_models.append(model)
            
            # Crear respuesta segura
            model_list_response = {
                "provider": provider,
                "models": filtered_models,
                "current_model": current_model,
                "available": is_available
            }
            
            response.append(model_list_response)
        
        return response
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Error listando modelos: {str(e)}"
        )

@router.post("/clear-cache")
async def clear_wearable_cache():
    """
    Limpia el cache de datos del wearable
    """
    global _wearable_cache
    _wearable_cache = {"data": None, "timestamp": None}
    return {"message": "Cache limpiado", "success": True}