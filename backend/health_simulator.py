from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import random
import math
import time
from typing import Dict, List, Optional

class HealthMetrics:
    def __init__(self, user_id: str):
        # Core user information
        self.user_id = user_id
        self.last_update = time.time()
        
        # Essential vital signs
        self.heart_rate = 65
        self.spo2 = 98
        self.respiratory_rate = 14
        self.blood_pressure = {"systolic": 120, "diastolic": 80}
        
        # Movement and position data
        self.acceleration = {"x": 0.0, "y": 0.0, "z": 9.81}  # m/s²
        self.device_orientation = "upright"  # upright, face_down, horizontal
        self.activity_state = "active"  # active, stationary, fallen
        self.last_movement_timestamp = time.time()
        
        # Location context
        self.location_type = "indoor"  # indoor, outdoor, vehicle
        self.gps_coordinates = {"latitude": 0.0, "longitude": 0.0}
        
        # Time tracking
        self.day_started = datetime.now().replace(hour=0, minute=0, second=0)

    def _get_time_factor(self) -> float:
        """Returns a factor (0-1) based on time of day to simulate daily patterns."""
        current_time = datetime.now()
        hour = current_time.hour + current_time.minute / 60
        time_factor = math.sin((hour - 3) * math.pi / 12)
        return (time_factor + 1) / 2

    def _add_noise(self, value: float, noise_level: float = 0.02) -> float:
        """Add random noise to a value."""
        noise = random.uniform(-noise_level, noise_level) * value
        return value + noise

    def update(self):
        """Update health metrics with realistic variations."""
        current_time = time.time()
        elapsed_minutes = (current_time - self.last_update) / 60
        time_factor = self._get_time_factor()
        
        # Update vital signs with realistic patterns
        self.heart_rate = self._add_noise(60 + (40 * time_factor), 0.05)
        self.spo2 = min(100, self._add_noise(97 + (2 * time_factor), 0.01))
        self.respiratory_rate = self._add_noise(14 + (4 * time_factor))
        
        # Update blood pressure with daily pattern
        bp_factor = time_factor * 0.15
        self.blood_pressure["systolic"] = self._add_noise(120 + (20 * bp_factor))
        self.blood_pressure["diastolic"] = self._add_noise(80 + (10 * bp_factor))
        
        # Simulate basic movement and orientation changes
        if random.random() < 0.01:  # 1% chance of position change
            self.device_orientation = random.choice(["upright", "face_down", "horizontal"])
            
        if random.random() < 0.05:  # 5% chance of activity change
            self.activity_state = random.choice(["active", "stationary", "fallen"])
            self.last_movement_timestamp = current_time if self.activity_state != "fallen" else self.last_movement_timestamp
            
        # Update acceleration with some random movement
        self.acceleration = {
            "x": self._add_noise(0.0, 0.5),
            "y": self._add_noise(0.0, 0.5),
            "z": self._add_noise(9.81, 0.1)  # Earth's gravity + noise
        }
        
        self.last_update = current_time

    def get_metrics(self) -> Dict:
        """Return current health metrics in a format suitable for LLM analysis."""
        self.update()
        
        time_since_last_movement = time.time() - self.last_movement_timestamp
        
        return {
            "timestamp": datetime.now().isoformat(),
            "user_id": self.user_id,
            "vital_signs": {
                "heart_rate": round(self.heart_rate, 1),
                "spo2": round(self.spo2, 1),
                "respiratory_rate": round(self.respiratory_rate, 1),
                "blood_pressure": {
                    "systolic": round(self.blood_pressure["systolic"]),
                    "diastolic": round(self.blood_pressure["diastolic"])
                }
            },
            "movement_data": {
                "acceleration": self.acceleration,
                "device_orientation": self.device_orientation,
                "activity_state": self.activity_state,
                "minutes_since_last_movement": round(time_since_last_movement / 60, 1)
            },
            "context": {
                "location_type": self.location_type,
                "gps_coordinates": self.gps_coordinates,
                "time_of_day": datetime.now().strftime("%H:%M")
            }
        }
        

app = FastAPI(title="Health Metrics Simulator")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store user metrics
user_metrics: Dict[str, HealthMetrics] = {}

@app.get("/health/{user_id}")
async def get_health_metrics(user_id: str):
    """Get current health metrics for a user."""
    if user_id not in user_metrics:
        user_metrics[user_id] = HealthMetrics(user_id)
    return user_metrics[user_id].get_metrics()

@app.get("/health/{user_id}/history")
async def get_health_history(user_id: str, hours: int = 24):
    """Get historical health metrics for a user."""
    if user_id not in user_metrics:
        user_metrics[user_id] = HealthMetrics(user_id)
        
    history = []
    current_time = datetime.now()
    
    # Generate historical data points
    for hour in range(hours, 0, -1):
        timestamp = current_time - timedelta(hours=hour)
        metrics = user_metrics[user_id].get_metrics()
        metrics["timestamp"] = timestamp.isoformat()
        history.append(metrics)
        
    return history