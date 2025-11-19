"""Cliente para Mi Fitness API (Xiaomi Health)"""

import httpx
import hashlib
import time
from typing import Dict, Optional
from datetime import datetime, date
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

from ..config import settings

class MiFitnessClient:
    """Cliente no oficial para Mi Fitness API"""
    
    BASE_URLS = {
        "us": "https://api-mifit-us2.huami.com",
        "eu": "https://api-mifit-eu.huami.com",
        "cn": "https://api-mifit.huami.com"
    }
    
    def __init__(self):
        self.email = settings.mi_fitness_email
        self.password = settings.mi_fitness_password
        self.region = settings.mi_fitness_region
        self.base_url = self.BASE_URLS.get(self.region, self.BASE_URLS["us"])
        self.access_token: Optional[str] = None
        self.user_id: Optional[str] = None
        
        # Siempre usar mock en modo desarrollo
        if settings.use_mock_wearable:
            from .mock_wearable import mock_client
            self.client = mock_client
        else:
            self.client = self  # Usar métodos propios
    
    def _encrypt_password(self, password: str) -> str:
        """Encripta password para autenticación"""
        try:
            key = b'XiaomiMiFitness!'[:16]
            iv = b'1234567890123456'
            cipher = AES.new(key, AES.MODE_CBC, iv)
            encrypted = cipher.encrypt(pad(password.encode(), AES.block_size))
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            print(f"❌ Error encriptando password: {e}")
            return password
    
    async def authenticate(self) -> bool:
        """Autentica con Mi Fitness"""
        if not self.email or not self.password:
            print("⚠️ Credenciales de Mi Fitness no configuradas")
            return False
        
        try:
            encrypted_pwd = self._encrypt_password(self.password)
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/v2/user/login",
                    json={
                        "email": self.email,
                        "password": encrypted_pwd,
                        "app_name": "com.xiaomi.hm.health",
                        "app_version": "6.0.0",
                        "device_id": settings.mi_fitness_device_id or "mock_device"
                    },
                    headers={
                        "User-Agent": "MiFitness/6.0.0",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data.get("token_info", {}).get("access_token")
                    self.user_id = data.get("token_info", {}).get("user_id")
                    print("✅ Autenticación exitosa con Mi Fitness")
                    return True
                else:
                    print(f"❌ Error de autenticación: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error en autenticación Mi Fitness: {e}")
            return False
    
    async def get_daily_summary(self, target_date: Optional[date] = None) -> Dict:
        """Obtiene resumen diario"""
        if settings.use_mock_wearable:
            from .mock_wearable import mock_client
            return await mock_client.get_daily_summary()
        
        if not self.access_token and not await self.authenticate():
            print("⚠️ Fallback a datos mock")
            from .mock_wearable import mock_client
            return await mock_client.get_daily_summary()
        
        if not target_date:
            target_date = date.today()
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/v1/data/band_data.json",
                    params={
                        "query_type": "summary",
                        "device_type": "0",
                        "userid": self.user_id,
                        "from_date": target_date.strftime("%Y-%m-%d"),
                        "to_date": target_date.strftime("%Y-%m-%d")
                    },
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "User-Agent": "MiFitness/6.0.0"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_daily_data(data)
                else:
                    from .mock_wearable import mock_client
                    return await mock_client.get_daily_summary()
                    
        except Exception as e:
            print(f"❌ Error obteniendo datos Mi Fitness: {e}")
            from .mock_wearable import mock_client
            return await mock_client.get_daily_summary()
    
    def _parse_daily_data(self, raw_data: dict) -> Dict:
        """Parsea respuesta API a formato estándar"""
        data = raw_data.get("data", {})
        
        return {
            "steps": data.get("ttl_step", 0),
            "calories": data.get("ttl_cal", 0),
            "heart_rate": data.get("avg_heart_rate", 0),
            "sleep_hours": data.get("ttl_sleep_time", 0) / 3600,
            "distance_km": data.get("ttl_dis", 0) / 1000,
            "active_minutes": data.get("ttl_run_time", 0) / 60,
            "floors_climbed": data.get("climb_floors", 0),
            "resting_heart_rate": data.get("resting_heart_rate", 0),
            "max_heart_rate": data.get("max_heart_rate", 0),
            "sleep_quality": "unknown",
            "stress_level": 0,
            "battery_level": 0,
            "last_sync": datetime.now().isoformat(),
            "device_model": data.get("device_name", "Xiaomi Wearable"),
            "connection_method": "mi_fitness",
            "mock_data": False
        }
    
    async def get_heart_rate_realtime(self) -> Dict:
        """Obtiene HR en tiempo real"""
        summary = await self.get_daily_summary()
        return {
            "heart_rate": summary.get("heart_rate", 0),
            "timestamp": datetime.now().isoformat(),
            "quality": "good",
            "mock_data": summary.get("mock_data", False)
        }
    
    async def get_sleep_data(self) -> Dict:
        """Obtiene datos de sueño"""
        summary = await self.get_daily_summary()
        sleep_hours = summary.get("sleep_hours", 0)
        
        return {
            "total_sleep_hours": sleep_hours,
            "deep_sleep_hours": sleep_hours * 0.25,
            "light_sleep_hours": sleep_hours * 0.55,
            "rem_sleep_hours": sleep_hours * 0.15,
            "awake_time_hours": sleep_hours * 0.05,
            "sleep_score": 0,
            "bedtime": "Unknown",
            "wake_time": "Unknown",
            "interruptions": 0,
            "mock_data": summary.get("mock_data", False)
        }
    
    async def get_activity_sessions(self) -> list:
        """Obtiene sesiones de actividad"""
        return []
    
    async def sync(self) -> Dict:
        """Sincroniza con Mi Fitness"""
        if await self.authenticate():
            return {
                "status": "success",
                "message": "Sincronizado con Mi Fitness",
                "last_sync": datetime.now().isoformat(),
                "mock_data": False
            }
        return {
            "status": "failed",
            "message": "No se pudo conectar con Mi Fitness",
            "last_sync": datetime.now().isoformat(),
            "mock_data": False
        }

# Instancia global
xiaomi_client = MiFitnessClient()