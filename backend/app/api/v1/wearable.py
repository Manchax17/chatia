"""Endpoints relacionados con el wearable Xiaomi"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date

from ...iot.xiaomi_client import xiaomi_client
from .models import WearableDataResponse, SyncResponse, ConnectionInfoResponse

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
    distance_km: float = 0
    active_minutes: int = 0
    floors_climbed: int = 0
    resting_heart_rate: int = 0
    max_heart_rate: int = 0
    sleep_quality: str = "good"
    stress_level: int = 50
    battery_level: int = 100
    device_model: str = "Xiaomi Mi Band"

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
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo datos del wearable: {str(e)}"
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
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo frecuencia cardíaca: {str(e)}"
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
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo datos de sueño: {str(e)}"
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
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo actividades: {str(e)}"
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
        raise HTTPException(
            status_code=500,
            detail=f"Error sincronizando: {str(e)}"
        )

@router.get("/connection-info", response_model=ConnectionInfoResponse)
async def get_connection_info():
    """
    Obtiene información sobre la conexión actual del wearable
    """
    try:
        info = xiaomi_client.get_connection_info()
        return ConnectionInfoResponse(**info)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo información de conexión: {str(e)}"
        )

@router.post("/update-manual", response_model=WearableDataResponse)
async def update_manual_data(data: WearableUpdateRequest):
    """
    Actualiza datos del wearable manualmente
    Útil cuando no hay API disponible
    
    Este endpoint solo funciona cuando XIAOMI_CONNECTION_METHOD=manual
    """
    try:
        # Verificar que esté en modo manual
        if xiaomi_client.connection_method != "manual":
            raise HTTPException(
                status_code=400,
                detail=f"Este endpoint solo funciona en modo 'manual'. Actualmente: '{xiaomi_client.connection_method}'. Cambia XIAOMI_CONNECTION_METHOD=manual en .env y reinicia el servidor."
            )
        
        # Actualizar datos
        xiaomi_client.client.update_data(data.dict())
        
        # Retornar datos actualizados
        updated_data = await xiaomi_client.get_daily_summary()
        
        return WearableDataResponse(
            data=updated_data,
            success=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error actualizando datos: {str(e)}"
        )