import asyncio
from app.core.database import db

async def test_connection():
    collections = await db.list_collection_names()
    print("MongoDB connection successful! Existing collections:", collections)

if __name__ == "__main__":
    asyncio.run(test_connection())
