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
        self.gps_coordinates = {"latitude": 40.756870, "longitude": -74.001762}
        
        # Accident simulation
        self.in_accident = False
        self.accident_type = None
        self.accident_start_time = None
        self.accident_phase = None  # impact, immediate_post, recovery
        
        # Time tracking
        self.day_started = datetime.now().replace(hour=0, minute=0, second=0)

    def simulate_accident(self, accident_type: str = None):
        """
        Initiate an accident simulation.
        Types: 'car_crash', 'fall', 'sports_injury'
        """
        if not accident_type:
            accident_type = random.choice(['car_crash', 'fall', 'sports_injury'])
            
        self.in_accident = True
        self.accident_type = accident_type
        self.accident_start_time = time.time()
        self.accident_phase = "impact"
        self.location_type = "vehicle" if accident_type == "car_crash" else "outdoor"

    def _add_noise(self, value: float, noise_level: float = 0.02) -> float:
        """Add random noise to a value."""
        noise = random.uniform(-noise_level, noise_level) * value
        return value + noise

    def _get_time_factor(self) -> float:
        """Returns a factor (0-1) based on time of day to simulate daily patterns."""
        current_time = datetime.now()
        hour = current_time.hour + current_time.minute / 60
        time_factor = math.sin((hour - 3) * math.pi / 12)
        return (time_factor + 1) / 2

    def _update_accident_metrics(self):
        """Update metrics based on accident type and phase"""
        elapsed_time = time.time() - self.accident_start_time
        
        # Phase transitions
        if self.accident_phase == "impact" and elapsed_time > 10:
            self.accident_phase = "immediate_post"
        elif self.accident_phase == "immediate_post" and elapsed_time > 60:  # 1 minutes
            self.accident_phase = "recovery"
        elif self.accident_phase == "recovery" and elapsed_time > 300:  # 5 minutes
            self.in_accident = False
            return

        if self.accident_type == "car_crash":
            if self.accident_phase == "impact":
                # Simulate sudden deceleration and chaos
                self.acceleration = {
                    "x": random.uniform(-20, 20),
                    "y": random.uniform(-20, 20),
                    "z": random.uniform(-20, 20)
                }
                self.device_orientation = random.choice(["face_down", "horizontal"])
                self.heart_rate = random.uniform(120, 150)
                self.respiratory_rate = random.uniform(25, 30)
                
            elif self.accident_phase == "immediate_post":
                # Post-impact trauma response
                self.activity_state = "fallen"
                self.heart_rate = random.uniform(100, 130)
                self.respiratory_rate = random.uniform(20, 25)
                self.blood_pressure["systolic"] = random.uniform(140, 160)
                
            else:  # recovery
                # Gradual stabilization
                self.heart_rate = random.uniform(80, 100)
                self.respiratory_rate = random.uniform(16, 20)

        elif self.accident_type == "fall":
            if self.accident_phase == "impact":
                self.acceleration["z"] = random.uniform(-15, -10)
                self.device_orientation = "face_down"
                self.activity_state = "fallen"
                
            elif self.accident_phase == "immediate_post":
                self.heart_rate = random.uniform(90, 110)
                self.activity_state = "fallen"
                
            else:  # recovery
                self.heart_rate = random.uniform(75, 85)

        elif self.accident_type == "sports_injury":
            if self.accident_phase == "impact":
                self.acceleration = {
                    "x": random.uniform(-10, 10),
                    "y": random.uniform(-10, 10),
                    "z": random.uniform(-10, 10)
                }
                self.heart_rate = random.uniform(110, 130)
                
            elif self.accident_phase == "immediate_post":
                self.activity_state = "stationary"
                self.heart_rate = random.uniform(100, 120)
                
            else:  # recovery
                self.heart_rate = random.uniform(80, 90)

    def update(self):
        """Update health metrics with realistic variations."""
        current_time = time.time()
        elapsed_minutes = (current_time - self.last_update) / 60
        
        # Randomly trigger accidents (0.1% chance per update)
        if not self.in_accident and random.random() < 0.001:
            self.simulate_accident()
            
        if self.in_accident:
            self._update_accident_metrics()
        else:
            # Normal updates
            time_factor = self._get_time_factor()
            self.heart_rate = self._add_noise(60 + (40 * time_factor), 0.05)
            self.spo2 = min(100, self._add_noise(97 + (2 * time_factor), 0.01))
            self.respiratory_rate = self._add_noise(14 + (4 * time_factor))
            
            bp_factor = time_factor * 0.15
            self.blood_pressure["systolic"] = self._add_noise(120 + (20 * bp_factor))
            self.blood_pressure["diastolic"] = self._add_noise(80 + (10 * bp_factor))
            
            if random.random() < 0.01:
                self.device_orientation = random.choice(["upright", "face_down", "horizontal"])
                
            if random.random() < 0.05:
                self.activity_state = random.choice(["active", "stationary"])
                self.last_movement_timestamp = current_time
                
            self.acceleration = {
                "x": self._add_noise(0.0, 0.5),
                "y": self._add_noise(0.0, 0.5),
                "z": self._add_noise(9.81, 0.1)
            }
        
        self.last_update = current_time

    def get_metrics(self) -> Dict:
        """Return current health metrics in a format suitable for LLM analysis."""
        self.update()
        
        time_since_last_movement = time.time() - self.last_movement_timestamp
        
        metrics = {
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
        
        if self.in_accident:
            metrics["accident_data"] = {
                "accident_type": self.accident_type,
                "accident_phase": self.accident_phase,
                "elapsed_time": round(time.time() - self.accident_start_time, 1)
            }
            
        return metrics

class AccidentSimulation(BaseModel):
    accident_type: str

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

@app.post("/health/{user_id}/simulate")
async def simulate_accident(user_id: str, simulation: AccidentSimulation):
    """Simulate an accident for a specific user."""
    if user_id not in user_metrics:
        user_metrics[user_id] = HealthMetrics(user_id)
        
    if simulation.accident_type not in ['car_crash', 'fall', 'sports_injury']:
        raise HTTPException(status_code=400, detail="Invalid accident type")
        
    user_metrics[user_id].simulate_accident(simulation.accident_type)
    return {"status": "success", "message": f"Simulating {simulation.accident_type}"}