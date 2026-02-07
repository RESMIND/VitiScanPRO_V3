# 🧪 GHID TESTARE & VERIFICARE - VitiScan v3

## Cum să testezi și verifici platforma complet

**Data:** 3 Februarie 2026  
**Versiune:** 1.0

---

## 📋 PREGĂTIRE TESTARE

### 1. Verificare Dependențe Backend

```powershell
cd backend
pip install -r requirements.txt
```

**Pachete obligatorii:**
- fastapi
- uvicorn
- motor (MongoDB async)
- python-jose (JWT)
- bcrypt
- python-multipart
- slowapi (rate limiting)
- pydantic
- httpx (pentru teste)

### 2. Verificare MongoDB Rulează

```powershell
# Verifică dacă MongoDB e pornit
mongosh --eval "db.version()"
```

**Dacă nu rulează:**
```powershell
# Windows: Start MongoDB service
net start MongoDB

# Sau rulează manual
mongod --dbpath C:\data\db
```

### 3. Configurare Environment Variables

Creează fișier `.env` în folder `backend/`:

```env
# JWT Secrets (SCHIMBĂ VALORILE!)
JWT_SECRET_KEY=super-secret-key-change-in-production-min-32-chars
JWT_ALGORITHM=HS256
REFRESH_SECRET_KEY=another-secret-for-refresh-tokens-change-this

# MongoDB
MONGO_URL=mongodb://localhost:27017
MONGO_DB_NAME=vitiscan_v3

# Server
ENV=development
HOST=0.0.0.0
PORT=8000

# CORS (în dev permite localhost)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Rate Limiting
RATE_LIMIT_ENABLED=true
MAX_REQUESTS_PER_MINUTE=100

# File Upload
MAX_FILE_SIZE_MB=50
UPLOAD_DIR=uploads/

# Optional: External Services
# STRIPE_API_KEY=sk_test_...
# STRIPE_WEBHOOK_SECRET=whsec_...
# REDIS_URL=redis://localhost:6379
# SENTRY_DSN=https://...
```

---

## 🚀 PORNIRE BACKEND

### Opțiune 1: Uvicorn Normal

```powershell
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Output așteptat:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Opțiune 2: Python Direct

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

### Verificare Server Pornit

Deschide browser: http://localhost:8000/docs

Ar trebui să vezi **Swagger UI** cu toate endpoint-urile API.

---

## ✅ TESTARE MANUALĂ RAPIDĂ

### 1. Health Check

**Browser:** http://localhost:8000/health

**Expected:**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-03T10:00:00",
  "version": "3.0.0"
}
```

### 2. Register User

**Swagger UI:** http://localhost:8000/docs  
**Endpoint:** POST /auth/register

**Body:**
```json
{
  "username": "test_viticultor",
  "email": "test@vitiscan.local",
  "password": "Test2026!Secure",
  "full_name": "Test Viticultor",
  "phone": "+40700000000"
}
```

**Expected Response (200):**
```json
{
  "user_id": "65c1a2b3c4d5e6f7g8h9i0j1",
  "username": "test_viticultor",
  "email": "test@vitiscan.local",
  "message": "User created successfully"
}
```

### 3. Login

**Endpoint:** POST /auth/login

**Body:**
```json
{
  "username": "test_viticultor",
  "password": "Test2026!Secure"
}
```

**Expected Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**IMPORTANT:** Copiază `access_token` pentru următoarele teste!

### 4. Get Profile (cu autentificare)

**Endpoint:** GET /auth/me

**Headers:**
```
Authorization: Bearer <access_token>
```

**Expected Response (200):**
```json
{
  "_id": "65c1a2b3c4d5e6f7g8h9i0j1",
  "username": "test_viticultor",
  "email": "test@vitiscan.local",
  "full_name": "Test Viticultor",
  "phone": "+40700000000",
  "created_at": "2026-02-03T10:00:00",
  "is_active": true
}
```

### 5. Create Establishment

**Endpoint:** POST /establishments

**Headers:**
```
Authorization: Bearer <access_token>
```

**Body:**
```json
{
  "name": "Vie Recaș",
  "region": "Banat",
  "total_hectares": 15.5,
  "address": "Recaș, Timiș, România"
}
```

**Expected Response (200):**
```json
{
  "establishment_id": "65c1a2b3c4d5e6f7g8h9i0j2",
  "name": "Vie Recaș",
  "user_id": "65c1a2b3c4d5e6f7g8h9i0j1",
  "created_at": "2026-02-03T10:05:00"
}
```

### 6. Create Parcel

**Endpoint:** POST /parcels

**Headers:**
```
Authorization: Bearer <access_token>
```

**Body:**
```json
{
  "establishment_id": "65c1a2b3c4d5e6f7g8h9i0j2",
  "name": "Parcelă Nord Merlot",
  "hectares": 2.5,
  "variety": "Merlot",
  "planting_year": 2018,
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [21.6856, 45.4547],
        [21.6870, 45.4547],
        [21.6870, 45.4560],
        [21.6856, 45.4560],
        [21.6856, 45.4547]
      ]
    ]
  }
}
```

**Expected Response (200):**
```json
{
  "parcel_id": "65c1a2b3c4d5e6f7g8h9i0j3",
  "name": "Parcelă Nord Merlot",
  "establishment_id": "65c1a2b3c4d5e6f7g8h9i0j2",
  "hectares": 2.5,
  "created_at": "2026-02-03T10:10:00"
}
```

---

## 🤖 TESTARE AUTOMATĂ COMPLETĂ

### Rulare Suite de Teste

**Asigură-te că backend-ul RULEAZĂ pe http://localhost:8000**

```powershell
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Teste (în alt terminal)
cd backend
python test_complete_flow.py
```

### Output Așteptat

```
============================================================
  🚀 TESTARE COMPLETĂ VITISCAN V3
============================================================

ℹ️  Server: http://localhost:8000
ℹ️  Data: 2026-02-03 10:15:30

============================================================
  TEST 1: Health Check
============================================================

✅ Health endpoint accessible
✅ Server status healthy

============================================================
  TEST 2: Register User
============================================================

✅ User registration successful
✅ User ID received

... (alte teste)

============================================================
  📊 RAPORT FINAL TESTARE
============================================================

Rezultate:
  Total teste:    31
✅ Teste passed:   28
❌ Teste failed:   3

Rata de succes: 90.3%

⚠️  MAJORITATEA TESTELOR AU TRECUT (80%+)
```

### Interpretare Rezultate

**90%+ pass rate:** 🟢 **EXCELENT** - Ready for production  
**80-89% pass rate:** 🟡 **BUN** - Minor fixes needed  
**70-79% pass rate:** 🟠 **ACCEPTABIL** - Some issues to fix  
**<70% pass rate:** 🔴 **PROBLEME** - Major fixes needed

---

## 🔍 VERIFICARE ERORI DE COD

### Check Toate Erorile Pylance

```powershell
# Verifică erori în VS Code
# Sau rulează manual:
cd backend
python -m pylint app/
```

**Erori așteptate (false positives):**
- `db["collection"]` - Pylance nu înțelege dict dynamic access (IGNORE)
- Import warnings pentru pachete opționale (telegram, twilio, resend) - OK dacă nu le folosești

**Erori CRITICE (FIX URGENT):**
- Import errors pentru pachete mandatory (fastapi, motor, bcrypt)
- Syntax errors
- Undefined variables

### Instalare Pachete Lipsă

Dacă vezi erori de import:

```powershell
cd backend
pip install <nume_pachet>
pip freeze > requirements.txt  # Actualizare requirements
```

---

## 📊 VERIFICARE SECURITATE

### 1. Verificare Secret Keys

```powershell
cd backend
grep -r "your-secret-key" app/
```

**NU ar trebui să găsească nimic!** Toate secretele trebuie în `.env`.

### 2. Verificare CORS

**Fișier:** `backend/app/main.py`

```python
# ❌ NU PERMITE în production:
allow_origins=["*"]

# ✅ CORECT în production:
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
allow_origins=ALLOWED_ORIGINS
```

### 3. Test Rate Limiting

**Script rapid:**
```powershell
# PowerShell script
for ($i=1; $i -le 105; $i++) {
    Invoke-RestMethod -Uri "http://localhost:8000/parcels" -Headers @{"Authorization"="Bearer YOUR_TOKEN"}
    Write-Host "Request $i"
}
```

**După request ~101:** Ar trebui să primești **429 Too Many Requests**

### 4. Test Unauthorized Access

**Fără token:**
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/parcels"
```

**Expected:** `401 Unauthorized` sau `403 Forbidden`

---

## 🧪 TESTARE GDPR COMPLIANCE

### 1. Verificare Consimțământ la Register

**Check:** Există checkbox-uri "Accept Terms" în UI frontend?

**Backend validation:**
```python
# În RegisterRequest model:
accept_terms: bool
accept_privacy: bool

# În endpoint /auth/register:
if not data.accept_terms or not data.accept_privacy:
    raise HTTPException(400, "Must accept terms")
```

### 2. Test Data Export

**Endpoint:** GET /users/me/export

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/users/me/export" -Headers @{"Authorization"="Bearer YOUR_TOKEN"} | ConvertTo-Json
```

**Expected:** JSON cu toate datele utilizatorului (user, parcels, scans, etc.)

### 3. Test Account Deletion

**Endpoint:** DELETE /users/me/gdpr-delete

**Body:**
```json
{
  "password": "Test2026!Secure"
}
```

**Expected:** Cont șters permanent, date pseudonimized în audit logs.

---

## 📱 TESTARE FRONTEND

### 1. Start Frontend Dev Server

```powershell
cd frontend
npm run dev
```

**Output:**
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

### 2. Test Flow Complet în Browser

**Scenariul utilizator:**

1. ✅ Deschide http://localhost:3000
2. ✅ Click "Register" → Completează formular → Success
3. ✅ Login cu credențiale create
4. ✅ Dashboard se încarcă (KPIs vizibile)
5. ✅ Adaugă fermă nouă → Formular funcționează
6. ✅ Adaugă parcelă → Desenează pe hartă → Success
7. ✅ Upload scanare → Fișier validat → Success
8. ✅ Vezi istoric scanări → Lista afișată
9. ✅ Settings → Schimbă parolă → Success
10. ✅ Team → Invită membru → Email trimis
11. ✅ Billing → Vezi usage stats → Corect
12. ✅ Logout → Redirecționare la login

### 3. Test Responsive Design

**Device testing:**
- Desktop (1920x1080)
- Tablet (768x1024)
- Mobile (375x667)

**Tools:** Chrome DevTools → Toggle device toolbar (Ctrl+Shift+M)

### 4. Test Cross-Browser

- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Edge (latest)
- ✅ Safari (latest) - dacă ai Mac

---

## 🔐 TESTARE SECURITATE AVANSATĂ

### 1. SQL Injection Test

**Endpoint:** POST /auth/login

**Body cu injection attempt:**
```json
{
  "username": "admin' OR '1'='1",
  "password": "dummy"
}
```

**Expected:** `401 Unauthorized` (NU ar trebui să funcționeze login-ul!)

### 2. XSS Test

**Endpoint:** POST /parcels

**Body cu XSS:**
```json
{
  "name": "<script>alert('XSS')</script>",
  "establishment_id": "...",
  "hectares": 1.0,
  "variety": "Test"
}
```

**Expected:** Script tag sanitized sau escaped în frontend.

### 3. File Upload Test - Malware

**⚠️ ATENȚIE:** NU uploada malware REAL! Folosește **EICAR test file**.

**EICAR test string:**
```
X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*
```

Salvează într-un fișier `test_virus.txt` și încearcă să îl uploadezi.

**Expected (dacă ClamAV e activ):** `400 Bad Request - File failed security scan`

### 4. Brute Force Test

**Script PowerShell:**
```powershell
# 10 încercări rapide de login cu parolă greșită
for ($i=1; $i -le 10; $i++) {
    $body = @{username="test_viticultor"; password="WrongPass$i"} | ConvertTo-Json
    Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method POST -Body $body -ContentType "application/json"
    Write-Host "Attempt $i"
}
```

**Expected (cu rate limiting):** După 5 încercări → `429 Too Many Requests`

---

## 📈 MONITORING & LOGS

### 1. Check Application Logs

**Backend logs (console):**
```
INFO:     127.0.0.1:54321 - "POST /auth/login HTTP/1.1" 200 OK
INFO:     127.0.0.1:54321 - "GET /parcels HTTP/1.1" 200 OK
```

**Check pentru:**
- ❌ ERROR messages (bugs)
- ⚠️ WARNING messages (potential issues)
- ✅ INFO messages (normal operation)

### 2. Check MongoDB Logs

```powershell
# Conectare la MongoDB
mongosh

# Verificare colecții
use vitiscan_v3
show collections

# Verificare audit logs
db.audit_logs.find().sort({timestamp: -1}).limit(10).pretty()
```

### 3. Check Rate Limiting

**MongoDB sau Redis:**
```powershell
# Dacă folosești Redis pentru rate limiting
redis-cli
KEYS rate_limit:*
GET rate_limit:user:USER_ID
```

---

## ✅ CHECKLIST FINAL TESTARE

### Pre-Production Checklist

- [ ] **Backend pornește fără erori**
- [ ] **MongoDB conectat și funcționează**
- [ ] **Toate endpoint-urile API răspund corect (Swagger)**
- [ ] **Test suite automată pass rate >90%**
- [ ] **Frontend se încarcă și afișează date corect**
- [ ] **Login/Register flow funcționează**
- [ ] **CRUD parcels funcționează**
- [ ] **File upload funcționează și validează**
- [ ] **Rate limiting activat și funcționează**
- [ ] **Team invitations funcționează**
- [ ] **Billing/quotas calculate corect**
- [ ] **Soft delete/restore funcționează**
- [ ] **Unauthorized access blocat**
- [ ] **SQL injection blocat**
- [ ] **XSS sanitized**
- [ ] **CORS configurat corect (nu "*" în production)**
- [ ] **Secret keys în .env (NU hardcoded)**
- [ ] **HTTPS enforced (în production)**
- [ ] **Audit logs funcționează**
- [ ] **Error handling corect (nu stack traces în production)**
- [ ] **Performance acceptabil (<500ms response time)**

---

## 🚨 TROUBLESHOOTING

### Problema: Backend nu pornește

**Eroare:** `ModuleNotFoundError: No module named 'fastapi'`

**Fix:**
```powershell
cd backend
pip install -r requirements.txt
```

---

### Problema: MongoDB connection error

**Eroare:** `ServerSelectionTimeoutError: localhost:27017`

**Fix:**
```powershell
# Verifică dacă MongoDB rulează
mongosh

# Dacă nu, pornește-l
net start MongoDB
```

---

### Problema: Import errors în cod

**Eroare:** `ImportError: cannot import name 'x' from 'y'`

**Fix:**
```powershell
# Reinstalează pachetul
pip uninstall <pachet>
pip install <pachet>
```

---

### Problema: Teste fail cu 401/403

**Eroare:** `401 Unauthorized` în toate testele

**Cauză:** Token-ul a expirat sau e invalid.

**Fix:**
```powershell
# Re-login în test script sau manual obține token nou
```

---

### Problema: Rate limiting prea agresiv

**Eroare:** `429 Too Many Requests` după 10 requests

**Fix temporar (DOAR PENTRU DEV):**
```python
# backend/app/core/rate_limiting.py
# Schimbă temporar la 1000 requests/min
MAX_REQUESTS = 1000
```

---

## 📞 SUPORT

**Documentație completă:**
- `AUDIT_SECURITATE_COMPLET.md` - Vulnerabilități și fix-uri
- `GHID_UTILIZATOR_SECURITATE.md` - Best practices pentru useri
- `CHECKLIST_VERIFICARE.md` - 250 puncte de verificare
- `REZUMAT_EXECUTIV_AUDIT.md` - Overview management

**Contact dezvoltatori:**
- Email: dev@vitiscan.com
- Slack: #vitiscan-dev
- GitHub Issues: github.com/vitiscan/vitiscan-v3/issues

---

**Succes la testare! 🚀**

*Document creat: 3 Februarie 2026*  
*Versiune: 1.0*
