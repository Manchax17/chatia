"""
Cliente para cargar datos manualmente desde Mi Fitness
El usuario exporta los datos de la app y los carga aquí
"""

from typing import Dict, Optional
from datetime import datetime

class ManualDataClient:
    """Cliente que permite cargar datos manualmente"""
    
    def __init__(self):
        self.cached_data: Optional[Dict] = None
        self.last_update: Optional[datetime] = None
    
    async def get_daily_summary(self) -> Dict:
        """Retorna datos cargados manualmente"""
        if self.cached_data:
            return {
                **self.cached_data,
                "connection_method": "manual",
                "mock_data": False,
                "last_sync": self.last_update.isoformat() if self.last_update else datetime.now().isoformat()
            }
        
        # Si no hay datos, retornar estructura vacía
        return {
            "steps": 0,
            "calories": 0,
            "heart_rate": 0,
            "sleep_hours": 0,
            "distance_km": 0,
            "active_minutes": 0,
            "floors_climbed": 0,
            "resting_heart_rate": 0,
            "max_heart_rate": 0,
            "sleep_quality": "unknown",
            "stress_level": 0,
            "battery_level": 100,
            "device_model": "Xiaomi Mi Band (Manual)",
            "connection_method": "manual",
            "mock_data": False,
            "last_sync": "Esperando datos manuales..."
        }
    
    def update_data(self, data: Dict):
        """Actualiza datos manualmente"""
        # Asegurar que todos los campos necesarios existan
        self.cached_data = {
            "steps": data.get("steps", 0),
            "calories": data.get("calories", 0),
            "heart_rate": data.get("heart_rate", 0),
            "sleep_hours": data.get("sleep_hours", 0),
            "distance_km": data.get("distance_km", 0),
            "active_minutes": data.get("active_minutes", 0),
            "floors_climbed": data.get("floors_climbed", 0),
            "resting_heart_rate": data.get("resting_heart_rate", data.get("heart_rate", 0)),
            "max_heart_rate": data.get("max_heart_rate", 0),
            "sleep_quality": data.get("sleep_quality", "good"),
            "stress_level": data.get("stress_level", 50),
            "battery_level": data.get("battery_level", 100),
            "device_model": data.get("device_model", "Xiaomi Mi Band (Manual)")
        }
        self.last_update = datetime.now()
        print(f"✅ Datos actualizados manualmente: {self.cached_data}")
    
    async def get_heart_rate_realtime(self) -> Dict:
        """HR desde datos manuales"""
        if self.cached_data:
            return {
                "heart_rate": self.cached_data.get("heart_rate", 0),
                "timestamp": datetime.now().isoformat(),
                "quality": "good",
                "mock_data": False
            }
        return {
            "heart_rate": 0,
            "timestamp": datetime.now().isoformat(),
            "quality": "unknown",
            "mock_data": False
        }
    
    async def get_sleep_data(self) -> Dict:
        """Sueño desde datos manuales"""
        if self.cached_data:
            sleep_hours = self.cached_data.get("sleep_hours", 0)
            return {
                "total_sleep_hours": sleep_hours,
                "deep_sleep_hours": round(sleep_hours * 0.25, 1),
                "light_sleep_hours": round(sleep_hours * 0.55, 1),
                "rem_sleep_hours": round(sleep_hours * 0.15, 1),
                "awake_time_hours": round(sleep_hours * 0.05, 1),
                "sleep_score": 0,
                "bedtime": "Unknown",
                "wake_time": "Unknown",
                "interruptions": 0,
                "mock_data": False
            }
        return {
            "total_sleep_hours": 0,
            "deep_sleep_hours": 0,
            "light_sleep_hours": 0,
            "rem_sleep_hours": 0,
            "awake_time_hours": 0,
            "sleep_score": 0,
            "bedtime": "Unknown",
            "wake_time": "Unknown",
            "interruptions": 0,
            "mock_data": False
        }
    
    async def get_activity_sessions(self) -> list:
        """Retorna lista vacía para datos manuales"""
        return []
    
    async def sync(self) -> Dict:
        """Mensaje de sincronización manual"""
        return {
            "status": "manual",
            "message": "Datos cargados manualmente. Usa el endpoint /update-manual para actualizarlos.",
            "last_sync": self.last_update.isoformat() if self.last_update else "Nunca",
            "mock_data": False
        }

# Instancia global
manual_client = ManualDataClient()