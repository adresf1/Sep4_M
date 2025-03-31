import os

DB_CONFIG = {
    "dbname": os.getenv("DBNAME", "b4miactrrxbtqyg0obdl"),
    "user": os.getenv("DBUSER", "ujmpoinam3senrd9at7f"),
    "password": os.getenv("DBPASSWORD", "FZHjl5BLPSkZWlFJ6rXQqDfUK4Ekwz"),
    "host": os.getenv("DBHOST", "b4miactrrxbtqyg0obdl-postgresql.services.clever-cloud.com"),
    "port": os.getenv("DBPORT", "50013"),
}
