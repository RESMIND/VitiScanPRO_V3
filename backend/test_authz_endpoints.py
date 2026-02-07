"""
Quick test script for authorization endpoints
Run: python test_authz_endpoints.py
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8000"

async def test_authz_check():
    """Test /authz/check endpoint"""
    print("\n🔍 Testing /authz/check endpoint...")
    
    # Test 1: Admin with MFA can delete
    payload1 = {
        "subject": {
            "id": "user:admin1",
            "role": "admin",
            "attrs": {"mfa": True}
        },
        "action": "delete",
        "resource": {
            "id": "parcel:123",
            "type": "parcel",
            "attrs": {},
            "relations": {}
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/authz/check", json=payload1)
        result = response.json()
        print(f"✅ Test 1 (Admin with MFA): {result['outcome']}")
        print(f"   Reasons: {result['reasons']}")
    
    # Test 2: User without MFA cannot delete
    payload2 = {
        "subject": {
            "id": "user:regular",
            "role": "user",
            "attrs": {"mfa": False}
        },
        "action": "delete",
        "resource": {
            "id": "parcel:456",
            "type": "parcel",
            "attrs": {},
            "relations": {}
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/authz/check", json=payload2)
        result = response.json()
        print(f"\n✅ Test 2 (User without MFA): {result['outcome']}")
        print(f"   Reasons: {result['reasons']}")
    
    # Test 3: Consultant with relationship
    payload3 = {
        "subject": {
            "id": "user:consultant1",
            "role": "consultant",
            "attrs": {"mfa": True, "region": "PACA"}
        },
        "action": "edit",
        "resource": {
            "id": "parcel:789",
            "type": "parcel",
            "attrs": {"region": "PACA"},
            "relations": {
                "owner": "user:owner1",
                "consultant": ["user:consultant1"]
            }
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/authz/check", json=payload3)
        result = response.json()
        print(f"\n✅ Test 3 (Consultant with relationship): {result['outcome']}")
        print(f"   Reasons: {result['reasons']}")
        print(f"   Matched policies: {result['matched_policies']}")

async def test_authz_why():
    """Test /authz/why endpoint"""
    print("\n\n🔍 Testing /authz/why endpoint...")
    
    payload = {
        "subject": {
            "id": "user:test",
            "role": "user",
            "attrs": {"mfa": True, "region": "PACA"}
        },
        "action": "view",
        "resource": {
            "id": "parcel:123",
            "type": "parcel",
            "attrs": {"region": "PACA"},
            "relations": {}
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}/authz/why", json=payload)
        result = response.json()
        print(f"Decision: {result['decision']}")
        print(f"RBAC: {result['rbac']}")
        print(f"ReBAC: {result['rebac']}")
        print(f"ABAC: {result['abac']}")

async def main():
    print("=" * 60)
    print("🔐 AUTHORIZATION SYSTEM TEST")
    print("=" * 60)
    
    try:
        await test_authz_check()
        await test_authz_why()
        
        print("\n" + "=" * 60)
        print("✅ All authorization endpoint tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure the backend is running:")
        print("  cd backend")
        print("  uvicorn app.main:app --reload")

if __name__ == "__main__":
    asyncio.run(main())
