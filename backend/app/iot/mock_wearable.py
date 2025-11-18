"""Cliente mock para desarrollo sin dispositivo físico"""

from datetime import datetime, timedelta
from typing import Dict
import random

class MockWearableClient:
    """Simula datos realistas del wearable Xiaomi"""
    
    def __init__(self):
        self.base_steps = 8000
        self.base_hr = 72
        self.base_sleep = 7.5
        
    async def get_daily_summary(self) -> Dict:
        """Genera resumen diario simulado"""
        current_hour = datetime.now().hour
        steps_multiplier = min(current_hour / 24, 1.0)
        
        steps = int(self.base_steps * steps_multiplier + random.randint(-1000, 1500))
        distance = round(steps * 0.00075, 2)  # ~0.75m por paso
        calories = int(steps * 0.04 + 1200)  # Metabolismo basal + actividad
        
        return {
            "steps": steps,
            "calories": calories,
            "heart_rate": self.base_hr + random.randint(-5, 10),
            "sleep_hours": round(self.base_sleep + random.uniform(-0.5, 0.5), 1),
            "distance_km": distance,
            "active_minutes": int(45 + random.randint(-10, 30)),
            "floors_climbed": random.randint(5, 15),
            "resting_heart_rate": self.base_hr + random.randint(-3, 3),
            "max_heart_rate": 140 + random.randint(-10, 20),
            "sleep_quality": random.choice(["excellent", "good", "fair"]),
            "stress_level": random.randint(30, 70),
            "battery_level": random.randint(60, 100),
            "last_sync": datetime.now().isoformat(),
            "device_model": "Xiaomi Mi Band 7",
            "connection_method": "mock",
            "mock_data": True
        }
    
    async def get_heart_rate_realtime(self) -> Dict:
        """Simula HR en tiempo real"""
        return {
            "heart_rate": self.base_hr + random.randint(-8, 12),
            "timestamp": datetime.now().isoformat(),
            "quality": random.choice(["excellent", "good"]),
            "mock_data": True
        }
    
    async def get_sleep_data(self) -> Dict:
        """Simula datos de sueño detallados"""
        total_sleep = round(self.base_sleep + random.uniform(-1, 1), 1)
        
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
        
        return sessions
    
    async def sync(self) -> Dict:
        """Simula sincronización"""
        return {
            "status": "success",
            "last_sync": datetime.now().isoformat(),
            "data_points_synced": random.randint(50, 200),
            "mock_data": True
        }

mock_client = MockWearableClient()