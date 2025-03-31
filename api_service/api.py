from fastapi import FastAPI
from database import get_sensor_data
from models import SensorData

app = FastAPI()

# Endpoint til at hente sensor-data fra databasen
@app.get("/sensors", response_model=list[SensorData])
def read_sensors():
    data = get_sensor_data()
    return data