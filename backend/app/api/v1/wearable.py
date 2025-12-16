"""Endpoints relacionados con el wearable Xiaomi"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
import logging

from ...iot.xiaomi_client import xiaomi_client
from .models import WearableDataResponse, SyncResponse, ConnectionInfoResponse

# Importar logger
logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================
# MODELOS PYDANTIC
# ============================================

class WearableUpdateRequest(BaseModel):
    """Modelo para actualizar datos manualmente"""
    steps: int
    calories: int
    heart_rate: int
    sleep_hours: float
    distance_km: Optional[float] = 0
    active_minutes: Optional[int] = 0
    floors_climbed: Optional[int] = 0
    resting_heart_rate: Optional[int] = 0
    max_heart_rate: Optional[int] = 0
    sleep_quality: Optional[str] = "good"
    stress_level: Optional[int] = 50
    battery_level: Optional[int] = 100
    device_model: Optional[str] = "Xiaomi Mi Band"

# ============================================
# ENDPOINTS
# ============================================

@router.get("/latest", response_model=WearableDataResponse)
async def get_latest_wearable_data():
    """
    Obtiene los datos más recientes del dispositivo Xiaomi
    """
    try:
        data = await xiaomi_client.get_daily_summary()
        return WearableDataResponse(
            data=data,
            success=True
        )
    except Exception as e:
        # Devolver datos simulados en caso de error
        logger.error(f"Error obteniendo datos del wearable: {e}")
        return WearableDataResponse(
            data={
                "steps": 0,
                "calories": 0,
                "heart_rate": 0,
                "sleep_hours": 0.0,
                "distance_km": 0.0,
                "active_minutes": 0,
                "floors_climbed": 0,
                "resting_heart_rate": 0,
                "max_heart_rate": 0,
                "sleep_quality": "good",
                "stress_level": 50,
                "battery_level": 100,
                "device_model": "Xiaomi Mi Band",
                "timestamp": datetime.now(),
                "connection_method": xiaomi_client.connection_method,
                "mock_data": True
            },
            success=False,
            error=str(e)
        )

@router.get("/heart-rate", response_model=WearableDataResponse)
async def get_heart_rate():
    """
    Obtiene frecuencia cardíaca en tiempo real
    """
    try:
        data = await xiaomi_client.get_heart_rate_realtime()
        return WearableDataResponse(
            data=data,
            success=True
        )
    except Exception as e:
        logger.error(f"Error obteniendo frecuencia cardíaca: {e}")
        return WearableDataResponse(
            data={"heart_rate": 0, "timestamp": datetime.now()},
            success=False,
            error=str(e)
        )

@router.get("/sleep", response_model=WearableDataResponse)
async def get_sleep_data():
    """
    Obtiene datos de sueño detallados
    """
    try:
        data = await xiaomi_client.get_sleep_data()
        return WearableDataResponse(
            data=data,
            success=True
        )
    except Exception as e:
        logger.error(f"Error obteniendo datos de sueño: {e}")
        return WearableDataResponse(
            data={
                "sleep_hours": 0.0,
                "sleep_quality": "good",
                "deep_sleep": 0.0,
                "light_sleep": 0.0,
                "rem_sleep": 0.0,
                "timestamp": datetime.now()
            },
            success=False,
            error=str(e)
        )

@router.get("/activities", response_model=WearableDataResponse)
async def get_activities():
    """
    Obtiene sesiones de actividad física
    """
    try:
        data = await xiaomi_client.get_activity_sessions()
        return WearableDataResponse(
            data={"activities": data},
            success=True
        )
    except Exception as e:
        logger.error(f"Error obteniendo actividades: {e}")
        return WearableDataResponse(
            data={"activities": []},
            success=False,
            error=str(e)
        )

@router.post("/sync", response_model=SyncResponse)
async def sync_wearable():
    """
    Fuerza sincronización con el dispositivo
    """
    try:
        result = await xiaomi_client.sync()
        return SyncResponse(
            message="Sincronización completada",
            data=result,
            success=True
        )
    except Exception as e:
        logger.error(f"Error sincronizando: {e}")
        return SyncResponse(
            message="Error al sincronizar",
            data={},
            success=False,
            error=str(e)
        )

@router.get("/connection-info", response_model=ConnectionInfoResponse)
async def get_connection_info():
    """
    Obtiene información sobre la conexión actual del wearable
    """
    try:
        info = xiaomi_client.get_connection_info()
        # Mapear los campos que devuelve xiaomi_client a los que espera ConnectionInfoResponse
        return ConnectionInfoResponse(
            method=info.get("method", "unknown"),
            available_methods=info.get("available_methods", ["mi_fitness", "bluetooth", "mock", "manual"]),
            using_mock=info.get("mock_enabled", False),  # Mapear mock_enabled a using_mock
            mi_fitness_configured=info.get("method") == "mi_fitness",  # Inferir configuración
            bluetooth_configured=info.get("method") == "bluetooth",   # Inferir configuración
            status=info.get("status", "unknown"),
            device_model=info.get("device_model", "Unknown")
        )
    except Exception as e:
        logger.error(f"Error obteniendo información de conexión: {e}") # Usar logger aquí
        # Devolver una respuesta válida incluso si falla
        return ConnectionInfoResponse(
            method=xiaomi_client.connection_method,
            available_methods=["mi_fitness", "bluetooth", "mock", "manual"],
            using_mock=xiaomi_client.use_mock,
            mi_fitness_configured=False,
            bluetooth_configured=False,
            status="error",
            device_model="Unknown"
        )

@router.post("/update-manual", response_model=WearableDataResponse)
async def update_manual_data(data: WearableUpdateRequest):
    """
    Actualiza datos del wearable manualmente
    Útil cuando no hay API disponible o para testing
    
    IMPORTANTE:
    - Si XIAOMI_CONNECTION_METHOD=manual: Actualiza los datos manualmente
    - Si XIAOMI_CONNECTION_METHOD=mock: Actualiza los datos mock para testing
    - Si otro método: Falla con error informativo
    """
    try:
        # Permitir actualización manual en estos modos
        if xiaomi_client.connection_method == "manual":
            # Modo manual - actualizar directamente
            xiaomi_client.update_data(data.dict())
            updated_data = await xiaomi_client.get_daily_summary()
            
            return WearableDataResponse(
                data=updated_data,
                success=True
            )
        
        elif xiaomi_client.connection_method == "mock":
            # Modo mock - actualizar datos mock para testing
            mock_data_dict = data.dict()
            mock_data_dict['timestamp'] = datetime.now()
            mock_data_dict['mock_data'] = True
            mock_data_dict['connection_method'] = 'mock'
            
            # Actualizar el diccionario mock_data del cliente
            xiaomi_client.mock_data.update(mock_data_dict)
            
            updated_data = await xiaomi_client.get_daily_summary()
            
            return WearableDataResponse(
                data=updated_data,
                success=True,
                message="Datos mock actualizados para testing"
            )
        
        else:
            # Otros métodos (mi_fitness, bluetooth) no permiten actualización manual
            raise HTTPException(
                status_code=400,
                detail=f"Actualización manual no disponible en modo '{xiaomi_client.connection_method}'. Use XIAOMI_CONNECTION_METHOD=manual o mock en .env"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando datos: {e}")
        current_data = await xiaomi_client.get_daily_summary()
        return WearableDataResponse(
            data=current_data,
            success=False,
            error=str(e)
        )