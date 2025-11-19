"""Cliente unificado para dispositivos Xiaomi"""

from typing import Dict
from datetime import datetime, date
from ..config import settings

class XiaomiClient:
    """Cliente principal que selecciona el método de conexión"""
    
    def __init__(self):
        self.connection_method = settings.xiaomi_connection_method
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa el cliente según configuración"""
        print(f"🔧 Inicializando Xiaomi Client: {self.connection_method}")
        
        if self.connection_method == "manual":
            from .manual_data_client import manual_client
            self.client = manual_client
            print("✅ Usando carga manual de datos")
            
        elif self.connection_method == "mock" or settings.use_mock_wearable:
            from .mock_wearable import mock_client
            self.client = mock_client
            print("✅ Usando datos simulados (MOCK)")
            
        elif self.connection_method == "mi_fitness":
            if settings.mi_fitness_email and settings.mi_fitness_password:
                from .mi_fitness_client import mi_fitness_client
                self.client = mi_fitness_client
                print("✅ Usando Mi Fitness API")
            else:
                print("⚠️ Credenciales Mi Fitness no configuradas, usando MOCK")
                from .mock_wearable import mock_client
                self.client = mock_client
                
        elif self.connection_method == "bluetooth":
            if settings.bluetooth_enabled and settings.xiaomi_mac_address:
                from .bluetooth_client import bluetooth_client
                self.client = bluetooth_client
                print("✅ Usando Bluetooth directo")
            else:
                print("⚠️ Bluetooth no configurado, usando MOCK")
                from .mock_wearable import mock_client
                self.client = mock_client
        else:
            print(f"⚠️ Método desconocido: {self.connection_method}, usando MOCK")
            from .mock_wearable import mock_client
            self.client = mock_client
    
    async def get_daily_summary(self, target_date: date = None) -> Dict:
        """Obtiene resumen diario"""
        try:
            data = await self.client.get_daily_summary()
            data["connection_method"] = self.connection_method
            data["timestamp"] = datetime.now().isoformat()
            return data
        except Exception as e:
            print(f"❌ Error: {e}, fallback a mock")
            from .mock_wearable import mock_client
            return await mock_client.get_daily_summary()
    
    async def get_heart_rate_realtime(self) -> Dict:
        """Obtiene HR en tiempo real"""
        try:
            return await self.client.get_heart_rate_realtime()
        except Exception as e:
            print(f"❌ Error: {e}")
            from .mock_wearable import mock_client
            return await mock_client.get_heart_rate_realtime()
    
    async def get_sleep_data(self) -> Dict:
        """Obtiene datos de sueño"""
        if hasattr(self.client, 'get_sleep_data'):
            try:
                return await self.client.get_sleep_data()
            except:
                pass
        
        from .mock_wearable import mock_client
        return await mock_client.get_sleep_data()
    
    async def get_activity_sessions(self) -> list:
        """Obtiene sesiones de actividad"""
        if hasattr(self.client, 'get_activity_sessions'):
            try:
                return await self.client.get_activity_sessions()
            except:
                pass
        
        from .mock_wearable import mock_client
        return await mock_client.get_activity_sessions()
    
    async def sync(self) -> Dict:
        """Fuerza sincronización"""
        if hasattr(self.client, 'sync'):
            return await self.client.sync()
        
        return {
            "status": "success",
            "message": "Sincronización simulada",
            "last_sync": datetime.now().isoformat()
        }
    
    def get_connection_info(self) -> Dict:
        """Información sobre la conexión actual"""
        return {
            "method": self.connection_method,
            "using_mock": settings.use_mock_wearable,
            "available_methods": ["mi_fitness", "bluetooth", "manual", "mock"],
            "mi_fitness_configured": bool(settings.mi_fitness_email),
            "bluetooth_configured": bool(settings.xiaomi_mac_address),
            "manual_mode_available": True
        }

# Instancia global
xiaomi_client = XiaomiClient()