"""Cliente mock para desarrollo sin dispositivo físico"""

from datetime import datetime, timedelta, date
from typing import Dict
import random

class MockWearableClient:
    """Simula datos realistas del wearable Xiaomi con consistencia diaria"""
    
    def __init__(self):
        self._cached_data = {}
        self._last_cache_date = None
        
    def _generate_daily_data(self) -> Dict:
        """Genera datos consistentes para el día actual"""
        current_hour = datetime.now().hour
        steps_multiplier = min(current_hour / 24, 1.0)
        
        # Usar la fecha actual como semilla para consistencia
        today_seed = hash(date.today().isoformat()) % 10000
        random.seed(today_seed)
        
        base_steps = 8000
        base_hr = 72
        base_sleep = 7.5
        
        steps = int(base_steps * steps_multiplier + random.randint(-1000, 1500))
        distance = round(steps * 0.00075, 2)
        calories = int(steps * 0.04 + 1200)
        
        data = {
            "steps": steps,
            "calories": calories,
            "heart_rate": base_hr + random.randint(-5, 10),
            "sleep_hours": round(base_sleep + random.uniform(-0.5, 0.5), 1),
            "distance_km": distance,
            "active_minutes": int(45 + random.randint(-10, 30)),
            "floors_climbed": random.randint(5, 15),
            "resting_heart_rate": base_hr + random.randint(-3, 3),
            "max_heart_rate": 140 + random.randint(-10, 20),
            "sleep_quality": random.choice(["excellent", "good", "fair"]),
            "stress_level": random.randint(30, 70),
            "battery_level": random.randint(60, 100),
            "last_sync": datetime.now().isoformat(),
            "device_model": "Xiaomi Mi Band 7",
            "connection_method": "mock",
            "mock_data": True
        }
        
        # Resetear la semilla para no afectar otras partes del código
        random.seed()
        
        return data
    
    def _get_cached_data(self) -> Dict:
        """Obtiene datos cacheados para el día actual"""
        today = date.today()
        
        if self._last_cache_date != today:
            self._cached_data = self._generate_daily_data()
            self._last_cache_date = today
            
        return self._cached_data.copy()
    
    async def get_daily_summary(self) -> Dict:
        """Genera resumen diario simulado (consistente por día)"""
        return self._get_cached_data()
    
    async def get_heart_rate_realtime(self) -> Dict:
        """Simula HR en tiempo real (más variable)"""
        cached_data = self._get_cached_data()
        
        # Permitir variabilidad en HR en tiempo real
        base_hr = cached_data.get("heart_rate", 72)
        
        return {
            "heart_rate": base_hr + random.randint(-8, 12),
            "timestamp": datetime.now().isoformat(),
            "quality": random.choice(["excellent", "good"]),
            "mock_data": True
        }
    
    async def get_sleep_data(self) -> Dict:
        """Simula datos de sueño detallados (basado en datos cacheados)"""
        cached_data = self._get_cached_data()
        total_sleep = cached_data.get("sleep_hours", 7.5)
        
        return {
            "total_sleep_hours": total_sleep,
            "deep_sleep_hours": round(total_sleep * 0.25, 1),
            "light_sleep_hours": round(total_sleep * 0.55, 1),
            "rem_sleep_hours": round(total_sleep * 0.15, 1),
            "awake_time_hours": round(total_sleep * 0.05, 1),
            "sleep_score": random.randint(75, 95),
            "bedtime": "23:30",
            "wake_time": "07:00",
            "interruptions": random.randint(1, 4),
            "mock_data": True
        }
    
    async def get_activity_sessions(self) -> list:
        """Simula sesiones de actividad"""
        # Usar semilla consistente para actividades del día
        today_seed = hash(date.today().isoformat()) % 10000
        random.seed(today_seed + 1)  # Semilla diferente para actividades
        
        activities = ["walk", "run", "cycle", "workout"]
        sessions = []
        
        for _ in range(random.randint(1, 3)):
            activity = random.choice(activities)
            duration = random.randint(15, 60)
            
            sessions.append({
                "type": activity,
                "start_time": (datetime.now() - timedelta(hours=random.randint(1, 10))).isoformat(),
                "duration_minutes": duration,
                "distance_km": round(duration * random.uniform(0.05, 0.15), 2),
                "calories": int(duration * random.uniform(8, 12)),
                "avg_heart_rate": 120 + random.randint(-10, 20),
                "max_heart_rate": 160 + random.randint(-10, 15),
                "mock_data": True
            })
        
        # Resetear semilla
        random.seed()
        
        return sessions
    
    async def sync(self) -> Dict:
        """Simula sincronización"""
        return {
            "status": "success",
            "last_sync": datetime.now().isoformat(),
            "data_points_synced": random.randint(50, 200),
            "mock_data": True
        }

# Instancia global
mock_client = MockWearableClient()