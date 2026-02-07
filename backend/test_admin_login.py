import requests
import json
import asyncio
from app.core.database import db

async def debug_login():
    print("🔍 Debugging login process...")

    # Check user in database
    user = await db["users"].find_one({"$or": [{"phone": "+40700123456"}, {"username": "+40700123456"}]})
    if user:
        print("✅ User found in database")
        print(f"   ID: {user['_id']}")
        print(f"   Has password: {'password' in user}")
        print(f"   Role: {user.get('role')}")

        # Test password
        import bcrypt
        if bcrypt.checkpw("Admin123!@#".encode('utf-8'), user["password"].encode('utf-8')):
            print("✅ Password verification successful")
        else:
            print("❌ Password verification failed")
    else:
        print("❌ User not found in database")

# Run debug first
asyncio.run(debug_login())

# Admin credentials
admin_credentials = {
    "phone": "+40700123456",
    "password": "Admin123!@#"
}

# Login endpoint
login_url = "http://localhost:8000/login"

print("\n🔐 Testing admin login...")

try:
    response = requests.post(login_url, data=admin_credentials)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")

        print("✅ Login successful!")
        print(f"Access Token: {access_token[:50]}...")
        print(f"Refresh Token: {refresh_token[:50]}...")

        # Test admin endpoint
        admin_url = "http://localhost:8000/admin-area"
        headers = {"Authorization": f"Bearer {access_token}"}

        admin_response = requests.get(admin_url, headers=headers)
        print(f"\nAdmin Area Status: {admin_response.status_code}")
        if admin_response.status_code == 200:
            print("✅ Admin access confirmed!")
            print(f"Response: {admin_response.json()}")
        else:
            print(f"❌ Admin access failed: {admin_response.text}")

        # Test /me endpoint
        me_url = "http://localhost:8000/me"
        me_response = requests.get(me_url, headers=headers)
        print(f"\nProfile Status: {me_response.status_code}")
        if me_response.status_code == 200:
            profile = me_response.json()
            print("✅ Profile retrieved!")
            print(f"User: {profile.get('full_name')} ({profile.get('role')})")
            print(f"Phone: {profile.get('phone')}")
            print(f"Email: {profile.get('username')}")
        else:
            print(f"❌ Profile retrieval failed: {me_response.text}")

    else:
        print(f"❌ Login failed: {response.text}")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n🔐 SECURITY RECOMMENDATIONS:")
print("1. Change the default admin password immediately")
print("2. Enable 2FA/SMS verification for admin account")
print("3. Set up email verification")
print("4. Configure rate limiting and monitoring")
print("5. Use HTTPS in production")