import psycopg2
import pandas as pd

DB_CONFIG = {
    "host": "b4miactrrxbtqyg0obdl-postgresql.services.clever-cloud.com",
    "port": "50013",
    "dbname": "b4miactrrxbtqyg0obdl",
    "user": "ujmpoinam3senrd9at7f",
    "password": "FZHjl5BLPSkZWlFJ6rXQqDfUK4Ekwz",
}

def fetch():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        query = "SELECT * FROM sensordata_data;"  
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Database error: {e}")
        return None
    

    