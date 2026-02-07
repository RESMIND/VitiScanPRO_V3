import asyncio
from app.core.database import db

async def update_admin_username():
    # Update admin user to have username set
    result = await db["users"].update_one(
        {"email": "admin@vitiscan.io"},
        {"$set": {"username": "+40700123456"}}
    )

    if result.modified_count > 0:
        print("✅ Admin username updated")
    else:
        print("❌ Failed to update username")

    # Check the user
    user = await db["users"].find_one({"email": "admin@vitiscan.io"})
    print(f"Username: {user.get('username')}")
    print(f"Phone: {user.get('phone')}")

if __name__ == "__main__":
    asyncio.run(update_admin_username())