import asyncio
from app.core.database import db

async def test_user_id():
    user = await db["users"].find_one({"phone": "+40700123456"})
    if user:
        print(f"User _id type: {type(user['_id'])}")
        print(f"User _id str: {str(user['_id'])}")
        print(f"User _id repr: {repr(user['_id'])}")

asyncio.run(test_user_id())