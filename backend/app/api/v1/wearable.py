"""Endpoints relacionados con el wearable Xiaomi"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import date

from ...iot.xiaomi_client import xiaomi_client
from .models import WearableDataResponse, SyncResponse, ConnectionInfoResponse

router = APIRouter()

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