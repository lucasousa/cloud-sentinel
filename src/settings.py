import os

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_URL = "sqlite://" + os.path.join(BASE_DIR, "db.sqlite3")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
