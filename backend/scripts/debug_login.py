import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import asyncio
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient
from app.core import config
from app.main import app

async def main():
    # Drop test DB to start clean
    client = AsyncIOMotorClient(config.MONGODB_URL)
    await client.drop_database(config.MONGODB_DB_NAME)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        test_user = {
            "username": "test-ci@vitiscan.dev",
            "password": "Test123!@#",
            "language": "ro",
            "role": "user",
            "accept_terms": True,
            "accept_privacy": True,
            "marketing_consent": False,
            "phone": "+40700123456",
            "phone_verified": True,
        }
        print('Registering user...')
        r1 = await ac.post('/register', json=test_user)
        print('Register status:', r1.status_code)
        try:
            print('Register json:', r1.json())
        except Exception as e:
            print('Register body not JSON:', r1.text)

        # Inspect stored user in DB
        print('Config DB name:', config.MONGODB_DB_NAME)
        db = client[f"{config.MONGODB_DB_NAME}"]
        stored = await db['users'].find_one({"username": test_user["username"]})
        print('Stored user doc (by username):', stored)
        all_users = await db['users'].find().to_list(length=100)
        print('All users in DB:', all_users)
        dbs = await client.list_database_names()
        print('Databases on server:', dbs)
        # Count users collection documents for all DBs matching common names
        for candidate in dbs:
            try:
                c = client[candidate]
                count = await c['users'].count_documents({})
                if count:
                    print(f"DB {candidate} has {count} users")
            except Exception:
                pass

        print('Logging in...')
        r2 = await ac.post('/login', json={"username": test_user["username"], "password": test_user["password"]})
        print('Login status:', r2.status_code)
        try:
            print('Login json:', r2.json())
        except Exception as e:
            print('Login body not JSON:', r2.text)

if __name__ == '__main__':
    asyncio.run(main())
