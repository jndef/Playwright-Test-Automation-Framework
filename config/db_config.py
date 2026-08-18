import os
from dotenv import load_dotenv

load_dotenv()


class MyLocalDBConfig:
    db_name = os.getenv("DB_NAME")
    server = "localhost"
    database = os.getenv("DB_BASE")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    port = os.getenv("DB_PORT")
