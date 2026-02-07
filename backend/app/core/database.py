from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import MONGODB_URL, MONGODB_DB_NAME

client = AsyncIOMotorClient(MONGODB_URL)
db = client[MONGODB_DB_NAME]

# FastAPI dependency helper
def get_db():
	return db
