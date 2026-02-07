import asyncio
import bcrypt
from app.core.database import db

async def fix_admin_password():
    # Find admin user
    admin_user = await db["users"].find_one({"email": "admin@vitiscan.io"})
    if not admin_user:
        print("❌ Admin user not found")
        return

    # Hash the correct password
    admin_password = "Admin123!@#"
    hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())

    # Update the user with proper hash
    result = await db["users"].update_one(
        {"_id": admin_user["_id"]},
        {"$set": {"password": hashed_password.decode('utf-8')}}
    )

    if result.modified_count > 0:
        print("✅ Admin password updated successfully")
        print(f"   New password: {admin_password}")

        # Verify the new password
        updated_user = await db["users"].find_one({"email": "admin@vitiscan.io"})
        if bcrypt.checkpw(admin_password.encode('utf-8'), updated_user["password"].encode('utf-8')):
            print("✅ Password verification successful")
        else:
            print("❌ Password verification failed")
    else:
        print("❌ Failed to update password")

if __name__ == "__main__":
    asyncio.run(fix_admin_password())