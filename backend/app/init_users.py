import asyncio
import bcrypt
from datetime import datetime
from app.core.database import db

async def insert_test_user():
    # Admin users to create
    admin_users = [
        {
            "email": "admin@vitiscan.io",
            "phone": "+33612345678",
            "password": "Admin123!@#",
            "full_name": "Administrator VitiScan"
        },
        {
            "email": "admin2@vitiscan.io",
            "phone": "0033665017098",
            "password": "0234155787",
            "full_name": "Administrator VitiScan 2"
        }
    ]

    for admin_data in admin_users:
        admin_email = admin_data["email"]
        admin_phone = admin_data["phone"]
        admin_password = admin_data["password"]
        admin_full_name = admin_data["full_name"]

        # Hash the password
        hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())

        # Check if admin already exists
        existing_admin = await db["users"].find_one({
            "$or": [
                {"email": admin_email},
                {"phone": admin_phone}
            ]
        })

        if existing_admin:
            print(f"Admin user already exists: {admin_email} / {admin_phone}")
            continue

        # Create admin user
        admin_user = {
            "username": admin_phone,
            "phone": admin_phone,
            "email": admin_email,
            "full_name": admin_full_name,
            "password": hashed_password.decode('utf-8'),
            "role": "admin",
            "language": "ro",
            "is_verified": True,  # Admin is pre-verified
            "phone_verified": True,
            "email_verified": True,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "login_attempts": 0,
            "account_locked": False
        }

        result = await db["users"].insert_one(admin_user)
        print("✅ Admin user created successfully!")
        print(f"   Email: {admin_email}")
        print(f"   Phone: {admin_phone}")
        print(f"   Password: {admin_password}")
        print(f"   User ID: {result.inserted_id}")
        print()

if __name__ == "__main__":
    asyncio.run(insert_test_user())
