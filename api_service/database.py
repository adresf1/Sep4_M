import psycopg2
from config import DB_CONFIG

# Opret forbindelse til PostgreSQL
def get_connection():
    return psycopg2.connect(
        dbname=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"]
    )

# Hent sensor-data fra databasen
def get_sensor_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT temperature, humidity, co2, light, soil_moisture FROM sensor_data;")
    data = cursor.fetchall()
    conn.close()
    
    # Konverter til liste af dictionaries
    return [
        {"temperature": d[0], "humidity": d[1], "co2": d[2], "light": d[3], "soil_moisture": d[4]} for d in data
    ]