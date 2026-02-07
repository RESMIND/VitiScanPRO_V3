import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

# Rezultate teste
results = []

def test_step(name, method, url, **kwargs):
    """Execută un test și înregistrează rezultatul"""
    try:
        response = requests.request(method, url, **kwargs)
        success = response.status_code < 400
        results.append({
            "Test": name,
            "Status": "✅" if success else "❌",
            "HTTP": response.status_code,
            "Response": response.json() if response.headers.get('content-type') == 'application/json' else "Binary/File"
        })
        return response
    except Exception as e:
        results.append({
            "Test": name,
            "Status": "❌",
            "HTTP": "Error",
            "Response": str(e)
        })
        return None

# Test 1: Register
print("🧪 Test 1: Creare utilizator testuser...")
response = test_step(
    "Register User",
    "POST",
    f"{BASE_URL}/register",
    json={"username": "testuser", "password": "testpass123", "language": "ro", "role": "user"}
)
print(f"   Rezultat: {response.status_code if response else 'ERROR'}\n")

# Test 2: Login
print("🧪 Test 2: Login cu testuser...")
response = test_step(
    "Login",
    "POST",
    f"{BASE_URL}/login",
    json={"username": "testuser", "password": "testpass123"}
)

if response and response.status_code == 200:
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print(f"   Token JWT obținut: {token[:50]}...\n")
else:
    print("   ❌ Login failed!\n")
    headers = {}

# Test 3: Get /me
print("🧪 Test 3: Get current user profile...")
response = test_step(
    "Get /me",
    "GET",
    f"{BASE_URL}/me",
    headers=headers
)
print(f"   Rezultat: {response.json() if response and response.status_code == 200 else 'ERROR'}\n")

# Test 4: Create Establishment
print("🧪 Test 4: Creare establishment 'Ferma Verde'...")
response = test_step(
    "Create Establishment",
    "POST",
    f"{BASE_URL}/establishments",
    headers=headers,
    json={"name": "Ferma Verde", "siret": "123456789", "address": "Str. Agricola 1", "surface_ha": 50.5}
)

if response and response.status_code == 200:
    establishment_id = response.json().get("id")
    print(f"   Establishment ID: {establishment_id}\n")
else:
    print("   ❌ Create establishment failed!\n")
    establishment_id = None

# Test 5: Create Parcel
if establishment_id:
    print("🧪 Test 5: Creare parcelă 'Parcela A'...")
    response = test_step(
        "Create Parcel",
        "POST",
        f"{BASE_URL}/parcels",
        headers=headers,
        json={"name": "Parcela A", "crop_type": "wheat", "area_ha": 10.0, "establishment_id": establishment_id}
    )
    
    if response and response.status_code == 200:
        parcel_id = response.json().get("id")
        print(f"   Parcel ID: {parcel_id}\n")
    else:
        print("   ❌ Create parcel failed!\n")
        parcel_id = None
else:
    parcel_id = None
    results.append({"Test": "Create Parcel", "Status": "⏭️", "HTTP": "Skipped", "Response": "No establishment ID"})

# Test 6: Create Crop
if parcel_id:
    print("🧪 Test 6: Creare cultură 'Grau'...")
    response = test_step(
        "Create Crop",
        "POST",
        f"{BASE_URL}/crops",
        headers=headers,
        json={"name": "Grau", "variety": "Winter", "year": 2026, "parcel_id": parcel_id}
    )
    print(f"   Rezultat: {response.json() if response and response.status_code == 200 else 'ERROR'}\n")
else:
    results.append({"Test": "Create Crop", "Status": "⏭️", "HTTP": "Skipped", "Response": "No parcel ID"})

# Test 7: Upload Scan
if parcel_id:
    print("🧪 Test 7: Upload fișier scan dummy...")
    files = {"file": ("test_scan.txt", b"This is a test scan file content", "text/plain")}
    
    try:
        response = requests.post(f"{BASE_URL}/scans?parcel_id={parcel_id}", headers=headers, files=files)
        success = response.status_code < 400
        results.append({
            "Test": "Upload Scan",
            "Status": "✅" if success else "❌",
            "HTTP": response.status_code,
            "Response": response.json() if response.status_code == 200 else response.text[:100]
        })
        
        if response.status_code == 200:
            scan_id = response.json().get("scan_id")
            print(f"   Scan ID: {scan_id}\n")
        else:
            print(f"   ❌ Upload failed: {response.text}\n")
            scan_id = None
    except Exception as e:
        print(f"   ❌ Upload error: {str(e)}\n")
        scan_id = None
        results.append({"Test": "Upload Scan", "Status": "❌", "HTTP": "Error", "Response": str(e)})
else:
    scan_id = None
    results.append({"Test": "Upload Scan", "Status": "⏭️", "HTTP": "Skipped", "Response": "No parcel ID"})

# Test 8: List Scans by Parcel
if parcel_id:
    print("🧪 Test 8: Listare scanări pentru parcelă...")
    response = test_step(
        "List Scans",
        "GET",
        f"{BASE_URL}/scans/by-parcel/{parcel_id}",
        headers=headers
    )
    print(f"   Număr scanări: {len(response.json()) if response and response.status_code == 200 else 0}\n")
else:
    results.append({"Test": "List Scans", "Status": "⏭️", "HTTP": "Skipped", "Response": "No parcel ID"})

# Test 9: Download Scan
if scan_id:
    print("🧪 Test 9: Download scanare...")
    try:
        response = requests.get(f"{BASE_URL}/scans/{scan_id}", headers=headers)
        success = response.status_code == 200
        results.append({
            "Test": "Download Scan",
            "Status": "✅" if success else "❌",
            "HTTP": response.status_code,
            "Response": f"File size: {len(response.content)} bytes" if success else response.text[:100]
        })
        print(f"   Fișier descărcat: {len(response.content)} bytes\n")
    except Exception as e:
        print(f"   ❌ Download error: {str(e)}\n")
        results.append({"Test": "Download Scan", "Status": "❌", "HTTP": "Error", "Response": str(e)})
else:
    results.append({"Test": "Download Scan", "Status": "⏭️", "HTTP": "Skipped", "Response": "No scan ID"})

# Print results table
print("\n" + "="*100)
print("📊 REZULTATE TESTE CAP-COADĂ")
print("="*100)
print(f"{'Test':<25} {'Status':<8} {'HTTP':<10} {'Response':<50}")
print("-"*100)
for result in results:
    response_str = str(result['Response'])[:47] + "..." if len(str(result['Response'])) > 50 else str(result['Response'])
    print(f"{result['Test']:<25} {result['Status']:<8} {str(result['HTTP']):<10} {response_str:<50}")
print("="*100)

# Summary
total = len(results)
passed = sum(1 for r in results if r['Status'] == '✅')
print(f"\n✨ Rezumat: {passed}/{total} teste reușite ({passed*100//total if total > 0 else 0}%)")
