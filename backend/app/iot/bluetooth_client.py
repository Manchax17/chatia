"""Cliente Bluetooth para conexión directa (Linux/Raspberry Pi)"""

from typing import Dict, Optional
from datetime import datetime

try:
    from bleak import BleakClient
    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False

from ..config import settings

class XiaomiBluetoothClient:
    """Cliente Bluetooth BLE para Xiaomi Band"""
    
    # UUIDs de servicios Xiaomi
    HEART_RATE_UUID = "00002a37-0000-1000-8000-00805f9b34fb"
    BATTERY_UUID = "00002a19-0000-1000-8000-00805f9b34fb"
    
    def __init__(self):
        self.mac_address = settings.xiaomi_mac_address
        self.client: Optional[BleakClient] = None
        self.connected = False
        
    async def connect(self) -> bool:
        """Conecta al dispositivo via Bluetooth"""
        if not BLUETOOTH_AVAILABLE:
            print("⚠️ Bleak no instalado, Bluetooth no disponible")
            return False
        
        if not self.mac_address:
            print("❌ MAC address no configurada")
            return False
        
        try:
            self.client = BleakClient(self.mac_address)
            await self.client.connect()
            self.connected = self.client.is_connected
            
            if self.connected:
                print(f"✅ Conectado via Bluetooth: {self.mac_address}")
            
            return self.connected
            
        except Exception as e:
            print(f"❌ Error conectando Bluetooth: {e}")
            return False
    
    async def disconnect(self):
        """Desconecta del dispositivo"""
        if self.client and self.connected:
            await self.client.disconnect()
            self.connected = False
    
    async def get_daily_summary(self) -> Dict:
        """Obtiene datos via Bluetooth"""
        if not self.connected and not await self.connect():
            from .mock_wearable import mock_client
            return await mock_client.get_daily_summary()
        
        try:
            heart_rate = await self._read_heart_rate()
            battery = await self._read_battery()
            
            return {
                "steps": 0,  # No disponible via BLE estándar
                "calories": 0,
                "heart_rate": heart_rate,
                "sleep_hours": 0,
                "distance_km": 0,
                "active_minutes": 0,
                "battery_level": battery,
                "last_sync": datetime.now().isoformat(),
                "device_model": "Xiaomi Band (Bluetooth)",
                "connection_method": "bluetooth",
                "mock_data": False
            }
            
        except Exception as e:
            print(f"❌ Error leyendo Bluetooth: {e}")
            from .mock_wearable import mock_client
            return await mock_client.get_daily_summary()
    
    async def _read_heart_rate(self) -> int:
        """Lee frecuencia cardíaca"""
        try:
            data = await self.client.read_gatt_char(self.HEART_RATE_UUID)
            return int(data[1]) if len(data) > 1 else 0
        except:
            return 0
    
    async def _read_battery(self) -> int:
        """Lee nivel de batería"""
        try:
            data = await self.client.read_gatt_char(self.BATTERY_UUID)
            return int(data[0]) if len(data) > 0 else 0
        except:
            return 0
    
    async def get_heart_rate_realtime(self) -> Dict:
        """Lee HR en tiempo real"""
        if not self.connected:
            await self.connect()
        
        hr = await self._read_heart_rate()
        
        return {
            "heart_rate": hr,
            "timestamp": datetime.now().isoformat(),
            "quality": "good" if hr > 0 else "poor"
        }

bluetooth_client = XiaomiBluetoothClient()