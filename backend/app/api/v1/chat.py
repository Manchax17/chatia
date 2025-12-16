"""Endpoints del chat"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from datetime import datetime
from typing import Optional

from ...llm.agent import ChatFitAgent
from ...llm.llm_factory import LLMFactory
from ...iot.xiaomi_client import xiaomi_client
from ...database.chat_db import ChatMemoryDB
from .models import ChatRequest, ChatResponse, ModelListResponse

router = APIRouter()

# Cache de datos del wearable
_wearable_cache = {"data": None, "timestamp": None}

# Cache de modelos por sesión
_session_models = {}

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, request_obj: Request, chat_id: Optional[str] = Query(None)):
    """
    Endpoint principal del chat
    
    - Recibe mensaje del usuario
    - Incluye datos del reloj Xiaomi si está disponible
    - Usa agente LLM con herramientas
    - Retorna respuesta enriquecida
    - Guarda en historial de chats si se proporciona chat_id
    """
    try:
        session_id = request_obj.client.host if request_obj.client else "default"
        
        # ✅ CORREGIDO: Usar configuración real en lugar de valores hardcodeados
        from ...config import settings
        
        # Determinar proveedor y modelo
        llm_provider = request.llm_provider or _session_models.get(session_id, {}).get("provider", settings.llm_provider)
        
        # Obtener modelo por defecto del proveedor seleccionado
        default_model = getattr(settings, f"{llm_provider}_model", "")
        model_name = request.model_name or _session_models.get(session_id, {}).get("model", default_model)
        
        # ✅ AGREGAR: Logs de depuración
        print(f"🔧 PARÁMETROS RECIBIDOS:")
        print(f"   - llm_provider: {request.llm_provider}")
        print(f"   - model_name: {request.model_name}")
        print(f"   - message: {request.message[:50]}...")
        print(f"🔧 CONFIGURACIÓN FINAL:")
        print(f"   - llm_provider: {llm_provider}")
        print(f"   - model_name: {model_name}")
        
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
        
        response_data = ChatResponse(
            response=result["response"],
            tools_used=result.get("tools_used", []),
            wearable_data=wearable_data,
            model_info=result.get("model_info", {}),
            success=result["success"],
            error=result.get("error")
        )
        
        # ✅ AGREGAR: Guardar en historial si se proporciona chat_id
        if chat_id:
            try:
                # Guardar mensaje del usuario
                ChatMemoryDB.add_message(
                    chat_id,
                    role="user",
                    content=request.message
                )
                
                # Guardar respuesta del asistente
                ChatMemoryDB.add_message(
                    chat_id,
                    role="assistant",
                    content=result["response"],
                    model_used=model_name,
                    tools_used=result.get("tools_used", [])
                )
                
                print(f"✅ Mensajes guardados en chat {chat_id}")
            except Exception as e:
                print(f"⚠️ Error guardando mensajes: {e}")
        
        return response_data
        
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
        
        for provider in ['ollama', 'groq', 'openai', 'huggingface']:
            is_available = LLMFactory.validate_provider(provider)
            models_list = available_models.get(provider, [])
            
            # Obtener modelo actual del proveedor
            current_model = ""
            if provider == 'ollama':
                current_model = settings.ollama_model
            elif provider == 'groq':
                current_model = settings.groq_model
            elif provider == 'openai':
                current_model = settings.openai_model
            elif provider == 'huggingface':
                current_model = settings.huggingface_model
            
            # Filtrar modelos válidos
            filtered_models = [model for model in models_list if isinstance(model, str) and model.strip()]
            
            response.append({
                "provider": provider,
                "models": filtered_models,
                "current_model": current_model,
                "available": is_available
            })
        
        return response
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error listando modelos: {str(e)}")
    
@router.post("/clear-cache")
async def clear_wearable_cache():
    """
    Limpia el cache de datos del wearable
    """
    global _wearable_cache
    _wearable_cache = {"data": None, "timestamp": None}
    return {"message": "Cache limpiado", "success": True}