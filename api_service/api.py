from fastapi import FastAPI
from database import get_sensor_data
from models import SensorData
from database import insert_sensor_data


app = FastAPI()

# Endpoint til at hente sensor-data fra databasen
@app.get("/sensors", response_model=list[SensorData])
def read_sensors():
    data = get_sensor_data()
    return data

# Endpoint til at modtage sensor-data via POST
@app.post("/sensors")
def create_sensor_data(sensor: SensorData):
    # Gem data i databasen
    insert_sensor_data(sensor)
    return {"message": "Sensor data successfully added", "data": sensor.dict()}