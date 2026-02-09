from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import MONGODB_URL, MONGODB_DB_NAME

# Create client lazily and only if MongoDB appears reachable. This avoids
# long blocking errors in local dev environments that don't have Mongo running.
from urllib.parse import urlparse
import socket

_client = None
_db = None

try:
    parsed = urlparse(MONGODB_URL)
    host = parsed.hostname or "localhost"
    port = parsed.port or 27017
    sock = socket.create_connection((host, port), timeout=0.5)
    sock.close()
    _client = AsyncIOMotorClient(MONGODB_URL)
    _db = _client[MONGODB_DB_NAME]
except Exception:
    # Mongo not reachable locally; leave client/db as None. Tests or app
    # startup will set these explicitly when a real DB is available.
    _client = None
    _db = None

client = _client
db = _db

# FastAPI dependency helper
def get_db():
    return db
