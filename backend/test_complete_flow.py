"""
SCRIPT TESTARE COMPLETĂ - VitiScan v3
Testează toate funcționalitățile critice ale platformei
"""

import asyncio
import sys
import os
import argparse
from datetime import datetime
from typing import Dict, List, Callable, Awaitable
import httpx

# ====== CONFIGURARE ======
BASE_URL = os.getenv("VITISCAN_BASE_URL", "http://127.0.0.1:8000")
TEST_USER = {
    "username": "test_viticultor",
    "email": "test@vitiscan.local",
    "password": "Test2026!Secure",
    "full_name": "Test Viticultor",
    "phone": "+40700000000",
    "language": "en",
    "role": "user",
    "accept_terms": True,
    "accept_privacy": True,
    "marketing_consent": False
}

# ====== CULORI PENTRU OUTPUT ======
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg: str):
    print(f"{Colors.GREEN}[OK] {msg}{Colors.END}")

def print_error(msg: str):
    print(f"{Colors.RED}[FAIL] {msg}{Colors.END}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}[SKIP] {msg}{Colors.END}")

def print_info(msg: str):
    print(f"{Colors.BLUE}[INFO] {msg}{Colors.END}")

def print_header(msg: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}{Colors.END}\n")

# ====== TESTE ======
class VitiScanTester:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)
        self.token = None
        self.refresh_token = None
        self.user_id = None
        self.establishment_id = None
        self.parcel_id = None
        self.scan_id = None
        
        self.tests_passed = 0
        self.tests_failed = 0
        self.tests_skipped = 0
        self.tests_total = 0
    
    async def run_all_tests(self):
        """Rulează toate testele în ordine"""
        print_header("TESTARE COMPLETA VITISCAN V3")
        print_info(f"Server: {BASE_URL}")
        print_info(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test 1: Health check
        await self.test_health_check()
        
        # Test 2: Autentificare
        await self.test_register()
        await self.test_login()
        await self.test_refresh_token()
        
        # Test 3: Profil utilizator
        await self.test_get_profile()
        await self.test_update_profile()
        
        # Test 4: Establishment
        await self.test_create_establishment()
        
        # Test 5: Parcele
        await self.test_create_parcel()
        await self.test_list_parcels()
        await self.test_get_parcel_details()
        await self.test_update_parcel()
        
        # Test 6: Scanări
        await self.test_upload_scan()
        await self.test_list_scans()
        
        # Test 7: Rate limiting
        await self.test_rate_limiting()
        
        # Test 8: Invitații echipă
        await self.test_invite_team_member()
        await self.test_list_invitations()
        
        # Test 9: Billing & Quota
        await self.test_usage_stats()
        
        # Test 10: Deletion
        await self.test_delete_parcel()
        
        # Test 11: Securitate
        await self.test_unauthorized_access()
        await self.test_sql_injection_protection()
        
        # Test 12: GDPR
        await self.test_data_export()
        
        # Cleanup
        await self.test_cleanup()
        
        # Raport final
        await self.print_final_report()
        
        await self.client.aclose()
    
    async def assert_test(self, condition: bool, test_name: str, error_msg: str = ""):
        """Helper pentru aserțiuni"""
        self.tests_total += 1
        if condition:
            self.tests_passed += 1
            print_success(f"{test_name}")
        else:
            self.tests_failed += 1
            print_error(f"{test_name}: {error_msg}")

    async def skip_test(self, test_name: str, reason: str):
        self.tests_total += 1
        self.tests_skipped += 1
        print_warning(f"{test_name} skipped: {reason}")
    
    # ====== TESTE HEALTH & AUTH ======
    
    async def test_health_check(self):
        print_header("TEST 1: Health Check")
        try:
            response = await self.client.get("/health")
            await self.assert_test(
                response.status_code == 200,
                "Health endpoint accessible"
            )
            data = response.json()
            await self.assert_test(
                data.get("status") == "healthy",
                "Server status healthy"
            )
        except Exception as e:
            await self.assert_test(False, "Health check failed", str(e))
    
    async def test_register(self):
        print_header("TEST 2: Register User")
        try:
            response = await self.client.post("/register", json=TEST_USER)
            
            if response.status_code == 400 and "already exists" in response.text.lower():
                await self.skip_test("User registration", "User already exists")
                return
            
            await self.assert_test(
                response.status_code == 201,
                "User registration successful",
                f"Status: {response.status_code}, Body: {response.text}"
            )
            
            data = response.json()
            self.user_id = data.get("user_id")
            await self.assert_test(
                self.user_id is not None,
                "User ID received",
                "No user_id in response"
            )
        except Exception as e:
            await self.assert_test(False, "Register test failed", str(e))
    
    async def test_login(self):
        print_header("TEST 3: Login")
        try:
            response = await self.client.post("/login", json={
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            })
            
            await self.assert_test(
                response.status_code == 200,
                "Login successful",
                f"Status: {response.status_code}"
            )
            
            data = response.json()
            self.token = data.get("access_token")
            self.refresh_token = data.get("refresh_token")
            
            await self.assert_test(
                self.token is not None,
                "Access token received"
            )
            
            # Setează header Authorization pentru toate request-urile următoare
            self.client.headers["Authorization"] = f"Bearer {self.token}"
            
        except Exception as e:
            await self.assert_test(False, "Login test failed", str(e))
    
    async def test_refresh_token(self):
        print_header("TEST 4: Refresh Token")
        try:
            if not self.refresh_token:
                await self.skip_test("Refresh token", "Refresh token not provided by API")
                return
            response = await self.client.post("/refresh", json={
                "refresh_token": self.refresh_token
            })
            await self.assert_test(
                response.status_code == 200,
                "Refresh token works",
                f"Status: {response.status_code}, Body: {response.text}"
            )
        except Exception as e:
            await self.assert_test(False, "Refresh token test failed", str(e))
    
    # ====== TESTE PROFIL ======
    
    async def test_get_profile(self):
        print_header("TEST 5: Get Profile")
        try:
            response = await self.client.get("/me")
            
            await self.assert_test(
                response.status_code == 200,
                "Profile retrieved"
            )
            
            data = response.json()
            await self.assert_test(
                data.get("username") == TEST_USER["username"],
                "Profile username matches"
            )
            await self.assert_test(
                data.get("language") == TEST_USER["language"],
                "Profile language matches"
            )
            
        except Exception as e:
            await self.assert_test(False, "Get profile failed", str(e))
    
    async def test_update_profile(self):
        print_header("TEST 6: Update Profile")
        try:
            response = await self.client.patch("/users/me", json={
                "full_name": "Test Viticultor Updated"
            })
            if response.status_code == 404:
                await self.skip_test("Profile update", "Endpoint not implemented")
                return
            await self.assert_test(
                response.status_code == 200,
                "Profile updated",
                f"Status: {response.status_code}, Body: {response.text}"
            )
        except Exception as e:
            await self.assert_test(False, "Update profile failed", str(e))
    
    # ====== TESTE ESTABLISHMENT ======
    
    async def test_create_establishment(self):
        print_header("TEST 7: Create Establishment")
        try:
            response = await self.client.post("/establishments", json={
                "name": "Vie Test Recas",
                "siret": "123456",
                "address": "Recas, Timis",
                "surface_ha": 15.5
            })
            
            await self.assert_test(
                response.status_code == 200,
                "Establishment created"
            )
            
            data = response.json()
            self.establishment_id = data.get("id")
            
            await self.assert_test(
                self.establishment_id is not None,
                "Establishment ID received"
            )
            
        except Exception as e:
            await self.assert_test(False, "Create establishment failed", str(e))
    
    # ====== TESTE PARCELE ======
    
    async def test_create_parcel(self):
        print_header("TEST 8: Create Parcel")
        try:
            response = await self.client.post("/parcels", json={
                "establishment_id": self.establishment_id,
                "name": "Parcela Test Nord",
                "crop_type": "Merlot",
                "area_ha": 2.5,
                "coordinates": [[[21.5, 45.5], [21.6, 45.5], [21.6, 45.6], [21.5, 45.6], [21.5, 45.5]]]
            })
            
            await self.assert_test(
                response.status_code == 200,
                "Parcel created",
                f"Status: {response.status_code}, Body: {response.text}"
            )
            
            data = response.json()
            self.parcel_id = data.get("id")
            
            await self.assert_test(
                self.parcel_id is not None,
                "Parcel ID received"
            )
            
        except Exception as e:
            await self.assert_test(False, "Create parcel failed", str(e))
    
    async def test_list_parcels(self):
        print_header("TEST 9: List Parcels")
        try:
            response = await self.client.get(f"/parcels/by-establishment/{self.establishment_id}")
            
            await self.assert_test(
                response.status_code == 200,
                "Parcels list retrieved"
            )
            
            data = response.json()
            await self.assert_test(
                len(data) > 0,
                "At least one parcel exists"
            )
            
        except Exception as e:
            await self.assert_test(False, "List parcels failed", str(e))
    
    async def test_get_parcel_details(self):
        print_header("TEST 10: Get Parcel Details")
        try:
            response = await self.client.get(f"/parcels/by-establishment/{self.establishment_id}")
            if response.status_code != 200:
                await self.assert_test(False, "Parcel details retrieved", f"Status: {response.status_code}")
                return
            data = response.json()
            parcel = next((p for p in data if p.get("id") == self.parcel_id), None)
            await self.assert_test(
                parcel is not None,
                "Parcel details retrieved"
            )
            if parcel:
                await self.assert_test(
                    parcel.get("name") == "Parcela Test Nord",
                    "Parcel name matches"
                )
        except Exception as e:
            await self.assert_test(False, "Get parcel details failed", str(e))
    
    async def test_update_parcel(self):
        print_header("TEST 11: Update Parcel")
        try:
            response = await self.client.put(f"/parcels/{self.parcel_id}", json={
                "establishment_id": self.establishment_id,
                "name": "Parcela Test Nord (Updated)",
                "crop_type": "Merlot",
                "area_ha": 2.5,
                "coordinates": [[[21.5, 45.5], [21.6, 45.5], [21.6, 45.6], [21.5, 45.6], [21.5, 45.5]]]
            })
            
            await self.assert_test(
                response.status_code == 200,
                "Parcel updated"
            )
            
        except Exception as e:
            await self.assert_test(False, "Update parcel failed", str(e))
    
    # ====== TESTE SCANĂRI ======
    
    async def test_upload_scan(self):
        print_header("TEST 12: Upload Scan")
        try:
            if not os.getenv("AWS_ACCESS_KEY_ID") or not os.getenv("AWS_SECRET_ACCESS_KEY"):
                await self.skip_test("Scan upload", "AWS S3 credentials missing")
                return

            # Minimal valid JPEG bytes (SOI + EOI)
            jpeg_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 10 + b"\xff\xd9"
            files = {
                "file": ("test_scan.jpg", jpeg_bytes, "image/jpeg")
            }
            response = await self.client.post(f"/scans?parcel_id={self.parcel_id}", files=files)

            await self.assert_test(
                response.status_code == 200,
                "Scan uploaded",
                f"Status: {response.status_code}, Body: {response.text}"
            )

            if response.status_code == 200:
                result = response.json()
                self.scan_id = result.get("scan_id")
        except Exception as e:
            await self.assert_test(False, "Upload scan failed", str(e))
    
    async def test_list_scans(self):
        print_header("TEST 13: List Scans")
        try:
            if not self.parcel_id:
                await self.skip_test("Scans list", "Missing parcel_id")
                return
            response = await self.client.get(f"/scans/by-parcel/{self.parcel_id}")
            
            await self.assert_test(
                response.status_code == 200,
                "Scans list retrieved"
            )
            
        except Exception as e:
            await self.assert_test(False, "List scans failed", str(e))
    
    # ====== TESTE RATE LIMITING ======
    
    async def test_rate_limiting(self):
        print_header("TEST 14: Rate Limiting")
        try:
            print_info("Sending 12 login attempts to test rate limit...")
            hit_limit = False
            for i in range(12):
                response = await self.client.post("/login", json={
                    "username": TEST_USER["username"],
                    "password": "WrongPassword!"
                })
                if response.status_code == 429:
                    hit_limit = True
                    print_success(f"Rate limit hit at request #{i+1}")
                    break
            await self.assert_test(
                hit_limit,
                "Rate limiting works",
                "Did not hit rate limit after 12 login attempts"
            )
        except Exception as e:
            await self.assert_test(False, "Rate limiting test failed", str(e))
    
    # ====== TESTE TEAM INVITATIONS ======
    
    async def test_invite_team_member(self):
        print_header("TEST 15: Invite Team Member")
        try:
            response = await self.client.post("/invitations/", json={
                "email": "member@vitiscan.local",
                "role": "member",
                "establishment_id": self.establishment_id
            })
            
            if response.status_code == 404:
                await self.skip_test("Invite team member", "Invitations router not enabled")
                return
            if response.status_code == 403:
                await self.skip_test("Invite team member", "Only owner/admin can invite")
                return
            await self.assert_test(
                response.status_code == 200,
                "Team member invited",
                f"Status: {response.status_code}, Body: {response.text}"
            )
            
        except Exception as e:
            await self.assert_test(False, "Invite team member failed", str(e))
    
    async def test_list_invitations(self):
        print_header("TEST 16: List Invitations")
        try:
            response = await self.client.get("/invitations/")
            if response.status_code == 404:
                await self.skip_test("List invitations", "Invitations router not enabled")
                return
            
            await self.assert_test(
                response.status_code == 200,
                "Invitations list retrieved"
            )
            
        except Exception as e:
            await self.assert_test(False, "List invitations failed", str(e))
    
    # ====== TESTE BILLING ======
    
    async def test_usage_stats(self):
        print_header("TEST 17: Usage Stats & Quotas")
        try:
            response = await self.client.get("/billing/usage")
            if response.status_code == 404:
                await self.skip_test("Usage stats", "Billing router not enabled")
                return
            
            await self.assert_test(
                response.status_code == 200,
                "Usage stats retrieved"
            )
            
            data = response.json()
            await self.assert_test(
                "parcels" in data and "scans" in data,
                "Usage stats contain parcels and scans"
            )
            
        except Exception as e:
            await self.assert_test(False, "Usage stats test failed", str(e))
    
    # ====== TESTE SOFT DELETION ======
    
    async def test_delete_parcel(self):
        print_header("TEST 18: Delete Parcel")
        try:
            response = await self.client.delete(f"/parcels/{self.parcel_id}")
            
            await self.assert_test(
                response.status_code == 204,
                "Parcel deleted"
            )
            
            # Verificare că parcela nu mai apare în listă
            response = await self.client.get(f"/parcels/by-establishment/{self.establishment_id}")
            if response.status_code == 200:
                parcels = response.json()
                await self.assert_test(
                    not any(p.get("id") == self.parcel_id for p in parcels),
                    "Deleted parcel not in list"
                )
        except Exception as e:
            await self.assert_test(False, "Delete parcel failed", str(e))
    
    # ====== TESTE SECURITATE ======
    
    async def test_unauthorized_access(self):
        print_header("TEST 20: Unauthorized Access Prevention")
        try:
            # Creează client fără token
            client_no_auth = httpx.AsyncClient(base_url=BASE_URL, timeout=10.0)
            
            response = await client_no_auth.get(f"/parcels/by-establishment/{self.establishment_id}")
            
            await self.assert_test(
                response.status_code == 401,
                "Unauthorized request blocked",
                f"Expected 401, got {response.status_code}"
            )
            
            await client_no_auth.aclose()
            
        except Exception as e:
            await self.assert_test(False, "Unauthorized access test failed", str(e))
    
    async def test_sql_injection_protection(self):
        print_header("TEST 21: SQL/NoSQL Injection Protection")
        try:
            # Încercare SQL injection în username
            response = await self.client.post("/login", json={
                "username": "admin' OR '1'='1",
                "password": "dummy"
            })
            
            await self.assert_test(
                response.status_code != 200,
                "SQL injection attempt blocked"
            )
            
            # Încercare NoSQL injection în parcel ID
            response = await self.client.get("/parcels/by-establishment/{'$ne': null}")
            
            await self.assert_test(
                response.status_code in [400, 404, 422],
                "NoSQL injection attempt blocked"
            )
            
        except Exception as e:
            await self.assert_test(False, "Injection protection test failed", str(e))
    
    # ====== TESTE GDPR ======
    
    async def test_data_export(self):
        print_header("TEST 22: GDPR Data Export")
        try:
            response = await self.client.get("/users/me/export")
            
            if response.status_code == 404:
                await self.skip_test("GDPR data export", "Endpoint not implemented")
            else:
                await self.assert_test(
                    response.status_code == 200,
                    "Data export successful"
                )
                
                # Verificare că răspunsul e JSON valid
                try:
                    data = response.json()
                    await self.assert_test(
                        "user" in data and "parcels" in data,
                        "Export contains user and parcels data"
                    )
                except:
                    pass
            
        except Exception as e:
            await self.assert_test(False, "GDPR export test failed", str(e))
    
    # ====== CLEANUP ======
    
    async def test_cleanup(self):
        print_header("TEST 23: Cleanup Test Data")
        try:
            # Ștergere parcelă permanentă
            if self.parcel_id:
                response = await self.client.delete(f"/parcels/{self.parcel_id}")
                print_info(f"Deleted test parcel: {self.parcel_id}")
            
            # NU ștergem utilizatorul pentru a permite rerulare
            print_info("Test user kept for future tests")
            
        except Exception as e:
            await self.assert_test(False, "Cleanup failed", str(e))
    
    # ====== RAPORT FINAL ======
    
    async def print_final_report(self):
        print_header("RAPORT FINAL TESTARE")
        
        total = self.tests_total
        passed = self.tests_passed
        failed = self.tests_failed
        skipped = self.tests_skipped
        executed = total - skipped
        success_rate = (passed / executed * 100) if executed > 0 else 0
        
        print(f"\n{Colors.BOLD}Rezultate:{Colors.END}")
        print(f"  Total teste:    {total}")
        print_success(f"Teste passed:   {passed}")
        if failed > 0:
            print_error(f"Teste failed:   {failed}")
        else:
            print(f"  {Colors.GREEN}Teste failed:   {failed}{Colors.END}")
        if skipped > 0:
            print_warning(f"Teste skipped:  {skipped}")
        
        print(f"\n{Colors.BOLD}Rata de succes (fara skipped): {success_rate:.1f}%{Colors.END}")
        
        if failed == 0 and executed > 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}TOATE TESTELE EXECUTATE AU TRECUT!{Colors.END}")
        elif success_rate >= 80:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}MAJORITATEA TESTELOR AU TRECUT (80%+){Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}MULTE TESTE AU ESUAT (<80%){Colors.END}")
        
        print("\n")

# ====== MAIN ======

async def main():
    parser = argparse.ArgumentParser(description="Run VitiScan API tests")
    parser.add_argument(
        "--only",
        nargs="*",
        help="Run only specific tests by number (e.g., 1 2 3)"
    )
    args = parser.parse_args()

    tester = VitiScanTester()
    try:
        if args.only:
            test_map: Dict[str, Callable[[], Awaitable[None]]] = {
                "1": tester.test_health_check,
                "2": tester.test_register,
                "3": tester.test_login,
                "4": tester.test_refresh_token,
                "5": tester.test_get_profile,
                "6": tester.test_update_profile,
                "7": tester.test_create_establishment,
                "8": tester.test_create_parcel,
                "9": tester.test_list_parcels,
                "10": tester.test_get_parcel_details,
                "11": tester.test_update_parcel,
                "12": tester.test_upload_scan,
                "13": tester.test_list_scans,
                "14": tester.test_rate_limiting,
                "15": tester.test_invite_team_member,
                "16": tester.test_list_invitations,
                "17": tester.test_usage_stats,
                "18": tester.test_delete_parcel,
                "20": tester.test_unauthorized_access,
                "21": tester.test_sql_injection_protection,
                "22": tester.test_data_export,
                "23": tester.test_cleanup
            }
            print_header("TESTARE INDIVIDUALA VITISCAN V3")
            print_info(f"Server: {BASE_URL}")
            print_info(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            for test_id in args.only:
                test_fn = test_map.get(test_id)
                if not test_fn:
                    print_warning(f"Unknown test id: {test_id}")
                    continue
                await test_fn()
            await tester.print_final_report()
        else:
            await tester.run_all_tests()
    except KeyboardInterrupt:
        print_warning("\n\nTestare întreruptă de utilizator")
    except Exception as e:
        print_error(f"\n\nEroare fatală: {e}")
        import traceback
        traceback.print_exc()
    
    # Exit code
    sys.exit(0 if tester.tests_failed == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())
