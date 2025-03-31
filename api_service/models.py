from pydantic import BaseModel

class SensorData(BaseModel):
    temperature: float
    humidity: float
    co2: float
    light: float
    soil_moisture: float