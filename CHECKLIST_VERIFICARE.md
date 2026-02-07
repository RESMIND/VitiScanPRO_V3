# ✅ CHECKLIST VERIFICARE COMPLETĂ - VitiScan v3
## Pre-Production Launch Checklist

**Data:** 3 Februarie 2026  
**Versiune:** 1.0  
**Responsabil QA:** _________________

---

## 📋 I. VERIFICĂRI FUNCȚIONALE

### 1. Autentificare & Autorizare

- [ ] **Register funcționează**
  - [ ] Validare email format (reject invalid emails)
  - [ ] Validare parolă puternică (min 8 char, uppercase, number, special)
  - [ ] Eroare la username duplicat
  - [ ] Eroare la email duplicat
  - [ ] Hash bcrypt aplicat (12 rounds)

- [ ] **Login funcționează**
  - [ ] Login cu username corect + parolă corectă → Success
  - [ ] Login cu parolă greșită → 401 Unauthorized
  - [ ] Login cu username inexistent → 401 Unauthorized
  - [ ] Returnează access_token + refresh_token
  - [ ] Token-urile sunt JWT valide

- [ ] **Token refresh funcționează**
  - [ ] Refresh token valid → noi tokens
  - [ ] Refresh token expirat → 401
  - [ ] Refresh token invalid → 401

- [ ] **Logout funcționează**
  - [ ] Client-side token deletion works
  - [ ] (BONUS) Server-side token blacklist

- [ ] **Protected endpoints necesită autentificare**
  - [ ] GET /parcels fără token → 401
  - [ ] POST /parcels fără token → 401
  - [ ] Token invalid → 401
  - [ ] Token expirat → 401

### 2. Multi-Tenancy & Izolare Date

- [ ] **Tenant context funcționează**
  - [ ] JWT conține tenant_id
  - [ ] Middleware setează tenant context
  - [ ] User poate vedea DOAR datele din tenant-ul său

- [ ] **Cross-tenant access blocat**
  - [ ] User A nu poate vedea parcels de la User B
  - [ ] User A nu poate edita establishments de la User B
  - [ ] User A nu poate șterge scans de la User B

- [ ] **Tenant switching funcționează**
  - [ ] POST /auth/switch-tenant cu tenant valid → Success
  - [ ] Switch la tenant unde user NU e membru → 403
  - [ ] După switch, queries returnează date din noul tenant

### 3. Establishments (Ferme)

- [ ] **Create establishment**
  - [ ] Establishment creat cu success
  - [ ] User devine automat OWNER
  - [ ] ID returnat în răspuns

- [ ] **List establishments**
  - [ ] Returnează doar establishments unde user e membru
  - [ ] Afișează rol user pentru fiecare establishment

- [ ] **Update establishment**
  - [ ] OWNER poate edita → Success
  - [ ] ADMIN poate edita → Success
  - [ ] MEMBER nu poate edita → 403

- [ ] **Delete establishment**
  - [ ] Doar OWNER poate șterge → Success
  - [ ] ADMIN nu poate șterge → 403

### 4. Parcele

- [ ] **Create parcel**
  - [ ] Parcel creat în establishment valid → Success
  - [ ] Parcel în establishment străin → 403
  - [ ] Geometry GeoJSON validă salvată
  - [ ] Hectares calculate corect

- [ ] **List parcels**
  - [ ] Returnează doar parcels din tenant curent
  - [ ] Filtrare by establishment_id funcționează
  - [ ] Parcels soft-deleted NU apar

- [ ] **Get parcel details**
  - [ ] Parcel propriu → Success cu toate datele
  - [ ] Parcel străin → 404 sau 403

- [ ] **Update parcel**
  - [ ] MEMBER+ poate edita → Success
  - [ ] VIEWER nu poate edita → 403
  - [ ] Update geometry funcționează
  - [ ] Update hectares funcționează

- [ ] **Delete parcel (soft)**
  - [ ] ADMIN+ poate șterge → Success
  - [ ] is_deleted=true, deleted_at set
  - [ ] Parcel NU mai apare în list
  - [ ] Parcel apare în /trash

### 5. Scanări (Scans)

- [ ] **Upload scan**
  - [ ] Upload fișier valid (.jpg, .png, .tiff) → Success
  - [ ] Upload fișier invalid (.exe, .zip) → 400
  - [ ] Fișier prea mare (>50MB) → 413
  - [ ] Virus scan funcționează (test cu fișier EICAR)
  - [ ] Metadata salvată corect (parcel_id, scan_type, date)

- [ ] **List scans**
  - [ ] Filtrare by parcel_id funcționează
  - [ ] Filtrare by date_range funcționează
  - [ ] Filtrare by scan_type funcționează

- [ ] **Download scan**
  - [ ] Download fișier propriu → Success cu FileResponse
  - [ ] Download fișier străin → 403
  - [ ] Fișier lipsă → 404

- [ ] **Delete scan**
  - [ ] Soft delete funcționează
  - [ ] Fișierul rămâne pe disk (pentru recovery)

### 6. Team Invitations

- [ ] **Create invitation**
  - [ ] OWNER poate invita → Success
  - [ ] ADMIN poate invita → Success
  - [ ] MEMBER nu poate invita → 403
  - [ ] Invite code generat (32 bytes)
  - [ ] Email trimis la invitat (dacă SMTP configurat)

- [ ] **List invitations**
  - [ ] Returnează doar invitații din tenant curent
  - [ ] Status-uri corecte (pending, accepted, expired, revoked)

- [ ] **Accept invitation**
  - [ ] Invite code valid → User adăugat în team
  - [ ] Invite code expirat (>7 zile) → 400
  - [ ] Invite code deja folosit → 400

- [ ] **Revoke invitation**
  - [ ] OWNER poate revoca → Success
  - [ ] Status schimbat în "revoked"
  - [ ] Invite code devine invalid

- [ ] **Remove team member**
  - [ ] OWNER poate elimina pe oricine → Success
  - [ ] OWNER nu poate fi eliminat → 400
  - [ ] ADMIN nu poate elimina OWNER → 403

- [ ] **Change member role**
  - [ ] OWNER poate schimba rol → Success
  - [ ] ADMIN nu poate schimba rol OWNER → 403

### 7. Rate Limiting & Quotas

- [ ] **Rate limiting funcționează**
  - [ ] 100 requests/min → După request 101 → 429 Too Many Requests
  - [ ] Rate limit reset după 1 minut
  - [ ] Different users au rate limits separate

- [ ] **Quota enforcement**
  - [ ] FREE plan: 3 parcels max → Parcel #4 → 402 Payment Required
  - [ ] PRO plan: 50 parcels max
  - [ ] ENTERPRISE plan: unlimited
  - [ ] Scans per month counting corect
  - [ ] Storage usage calculat corect

- [ ] **Usage stats**
  - [ ] GET /billing/usage returnează current/limit pentru toate resursele
  - [ ] Percentage calculation corect
  - [ ] Scans this month reset la începutul lunii

### 8. Billing & Subscriptions

- [ ] **Plans display**
  - [ ] 3 plans afișate (Free, Pro, Enterprise)
  - [ ] Current plan indicat
  - [ ] Features list corectă

- [ ] **Upgrade flow**
  - [ ] Click "Upgrade to Pro" → Redirect la Stripe Checkout
  - [ ] Stripe checkout session created
  - [ ] (BONUS) Webhook handle subscription.created

- [ ] **Invoices**
  - [ ] (BONUS) Invoices generate after payment
  - [ ] (BONUS) Invoices downloadable

### 9. Trash & Recovery

- [ ] **List trash**
  - [ ] Returnează soft-deleted resources
  - [ ] Filtrare by type (parcel, scan) funcționează
  - [ ] Afișează days_until_permanent delete

- [ ] **Restore resource**
  - [ ] Restore în primele 30 zile → Success
  - [ ] Restore după 30 zile → 400 "Cannot restore"
  - [ ] Resource restored apare din nou în list

- [ ] **Permanent delete**
  - [ ] Delete imediat → Success, resource ștearsă complet
  - [ ] Fișierele pe disk șterse
  - [ ] NU mai poate fi restored

- [ ] **Empty trash**
  - [ ] Șterge toate resursele din trash
  - [ ] Confirmă număr de items șterse

### 10. Admin Panel

- [ ] **Global stats**
  - [ ] Total users count corect
  - [ ] Total establishments count corect
  - [ ] Total parcels/scans count corect
  - [ ] Storage used calculat corect

- [ ] **Recent users**
  - [ ] Afișează ultimii 5 useri
  - [ ] Active status indicator corect

- [ ] **Recent activity**
  - [ ] Audit logs afișate (10 cele mai recente)
  - [ ] Action icons corespund tipului
  - [ ] IP address logged

- [ ] **Access control**
  - [ ] SUPERADMIN role poate accesa → Success
  - [ ] User normal nu poate accesa → 403

---

## 🔐 II. VERIFICĂRI SECURITATE

### 1. Vulnerabilități Critice

- [ ] **V1.1: Secret keys în environment variables**
  - [ ] JWT_SECRET_KEY în .env (NU hardcodat în cod)
  - [ ] REFRESH_SECRET_KEY separat
  - [ ] MongoDB password în .env

- [ ] **V3.1: HTTPS enforced**
  - [ ] Production folosește HTTPS
  - [ ] HTTP redirect la HTTPS
  - [ ] HSTS header prezent

- [ ] **V3.3: CORS configurare restrictivă**
  - [ ] allow_origins conține DOAR domenii autorizate
  - [ ] NU permite "*" în production

- [ ] **V5.1: File upload validare**
  - [ ] Extensii whitelist (.jpg, .png, .tiff, .pdf)
  - [ ] MIME type verificat
  - [ ] Magic bytes verificate
  - [ ] Upload .exe blocat

- [ ] **V2.1: GDPR consent**
  - [ ] Checkbox "Accept terms" la register
  - [ ] Consimțământ logged în database

### 2. Autentificare Securizată

- [ ] **Password hashing**
  - [ ] Bcrypt cu 12 rounds (verifică în database)
  - [ ] Parole NU în plaintext nicăieri

- [ ] **Token security**
  - [ ] JWT signed cu HS256
  - [ ] Secret key suficient de complex (32+ chars)
  - [ ] Expirare tokens (30 min access, 7 zile refresh)

- [ ] **2FA (dacă implementat)**
  - [ ] TOTP funcționează
  - [ ] QR code generat corect
  - [ ] Recovery codes salvate

### 3. Input Validation

- [ ] **SQL/NoSQL injection protection**
  - [ ] Input `admin' OR '1'='1` blocat
  - [ ] Input `{'$ne': null}` blocat
  - [ ] Toate queries parametrizate

- [ ] **XSS protection**
  - [ ] Input `<script>alert('XSS')</script>` sanitizat
  - [ ] HTML tags stripped din nume parcels

- [ ] **Path traversal protection**
  - [ ] Upload filename `../../etc/passwd` blocat
  - [ ] Download path `../../../secret.txt` blocat

### 4. Authorization Checks

- [ ] **Role-based access**
  - [ ] VIEWER nu poate crea parcels → 403
  - [ ] MEMBER nu poate invita → 403
  - [ ] ADMIN nu poate elimina OWNER → 403

- [ ] **Resource ownership**
  - [ ] User A nu poate edita parcel de la User B
  - [ ] User A nu poate downloada scan de la User B

### 5. File Upload Security

- [ ] **File validation**
  - [ ] Extensie validată
  - [ ] MIME type validat
  - [ ] Magic bytes validate

- [ ] **Virus scanning (dacă implementat)**
  - [ ] ClamAV scanează toate fișierele
  - [ ] Fișier infectat blocat

- [ ] **Storage security**
  - [ ] Fișiere NU accesibile direct (fără endpoint)
  - [ ] (BONUS) Fișiere encrypted at rest

---

## 📊 III. VERIFICĂRI GDPR & CONFORMITATE

### 1. Drepturile Utilizatorilor

- [ ] **Dreptul la informare**
  - [ ] Privacy Policy publicată și accesibilă
  - [ ] Terms of Service publicate
  - [ ] Cookie policy (dacă folosești cookies)

- [ ] **Dreptul de acces**
  - [ ] User poate vedea toate datele sale
  - [ ] GET /users/me funcționează

- [ ] **Dreptul la portabilitate**
  - [ ] (BONUS) GET /users/me/export returnează JSON
  - [ ] (BONUS) Include toate datele (user, parcels, scans)

- [ ] **Dreptul la ștergere**
  - [ ] (BONUS) DELETE /users/me/gdpr-delete funcționează
  - [ ] (BONUS) Toate datele șterse permanent
  - [ ] (BONUS) Audit logs pseudonimized

- [ ] **Dreptul la rectificare**
  - [ ] PATCH /users/me funcționează
  - [ ] User poate edita email, nume, telefon

### 2. Consimțământ & Logging

- [ ] **Consimțământ la register**
  - [ ] Checkbox obligatoriu "Accept Terms"
  - [ ] Checkbox obligatoriu "Accept Privacy Policy"
  - [ ] (Optional) Checkbox marketing consent

- [ ] **Logging consimțământ**
  - [ ] Timestamp consimțământ salvat
  - [ ] IP address logged
  - [ ] User-agent logged

### 3. Data Retention

- [ ] **Soft deletion retention**
  - [ ] 30 zile recovery period
  - [ ] După 30 zile → permanent delete automat

- [ ] **GDPR delete**
  - [ ] Ștergere completă la cerere
  - [ ] Pseudonimizare audit logs (nu ștergere completă)

---

## 🧪 IV. TESTE AUTOMATE

### 1. Unit Tests

- [ ] **Backend tests pass**
  - [ ] `pytest tests/` → All green
  - [ ] Coverage > 80%

### 2. Integration Tests

- [ ] **Run test_complete_flow.py**
  - [ ] Toate cele 23 teste pass
  - [ ] Success rate 100%

### 3. Frontend Tests

- [ ] **(BONUS) Jest tests pass**
  - [ ] Component tests
  - [ ] Integration tests

---

## 🚀 V. DEPLOYMENT & PRODUCTION

### 1. Environment Variables

- [ ] **Backend .env complet**
  ```
  JWT_SECRET_KEY=<32+ char random>
  REFRESH_SECRET_KEY=<32+ char random>
  MONGO_URL=mongodb://user:pass@host:27017/dbname
  STRIPE_API_KEY=sk_live_...
  STRIPE_WEBHOOK_SECRET=whsec_...
  FILE_ENCRYPTION_KEY=<Fernet key>
  PASSWORD_PEPPER=<random string>
  ALLOWED_ORIGINS=https://app.vitiscan.com
  ENV=production
  ```

- [ ] **Frontend .env complet**
  ```
  NEXT_PUBLIC_API_URL=https://api.vitiscan.com
  NEXT_PUBLIC_STRIPE_PUBLIC_KEY=pk_live_...
  ```

### 2. Database

- [ ] **MongoDB configurare**
  - [ ] Autentificare activată
  - [ ] Encryption at rest activat
  - [ ] Backup zilnic configurat
  - [ ] Indexuri create (user_id, tenant_id, is_deleted)

### 3. HTTPS & SSL

- [ ] **Certificat SSL valid**
  - [ ] Let's Encrypt sau Digicert
  - [ ] Valabil minim 30 zile
  - [ ] Wildcard pentru subdomeniilor (*.vitiscan.com)

- [ ] **HTTPS redirect**
  - [ ] HTTP → HTTPS redirect
  - [ ] HSTS header cu max-age 1 an

### 4. Monitoring & Logging

- [ ] **Sentry configurare**
  - [ ] Frontend Sentry DSN setat
  - [ ] Backend Sentry DSN setat
  - [ ] Error tracking funcționează

- [ ] **(BONUS) Centralized logging**
  - [ ] Logs streaming la Logtail/Datadog
  - [ ] Retention 1 an

### 5. External Services

- [ ] **Stripe**
  - [ ] Products create (Pro, Enterprise)
  - [ ] Webhook endpoint configurat
  - [ ] Webhook secret în .env

- [ ] **(BONUS) Redis**
  - [ ] Redis instance running
  - [ ] Rate limiting folosește Redis
  - [ ] Token blacklist folosește Redis

- [ ] **(BONUS) Email service**
  - [ ] SendGrid/Resend API key configurat
  - [ ] Email templates create
  - [ ] Test email send funcționează

- [ ] **(BONUS) ClamAV**
  - [ ] ClamAV daemon running
  - [ ] Virus scan funcționează
  - [ ] False positive rate acceptabil

---

## 📝 VI. DOCUMENTAȚIE

- [ ] **README complet**
  - [ ] Installation instructions
  - [ ] Environment setup
  - [ ] Running locally
  - [ ] Deployment guide

- [ ] **API Documentation**
  - [ ] (BONUS) OpenAPI/Swagger disponibil
  - [ ] Endpoints documentate
  - [ ] Request/response examples

- [ ] **User Documentation**
  - [ ] User guide creat (GHID_UTILIZATOR_SECURITATE.md)
  - [ ] FAQ page
  - [ ] Video tutorials (optional)

---

## ✅ APROBARE FINALĂ

### Responsabili Semnare

- [ ] **CTO/Tech Lead:** ___________________ Data: _______
  - [ ] Toate testele tehnice pass
  - [ ] Vulnerabilități critice remediate
  - [ ] Performance acceptabil

- [ ] **DPO (Data Protection Officer):** ___________________ Data: _______
  - [ ] GDPR compliant
  - [ ] Consimțământ implementat
  - [ ] Data retention policy OK

- [ ] **Legal Counsel:** ___________________ Data: _______
  - [ ] Terms of Service reviewed
  - [ ] Privacy Policy reviewed
  - [ ] SLA documented

- [ ] **Security Lead:** ___________________ Data: _______
  - [ ] Penetration test completat
  - [ ] Vulnerabilities remediate
  - [ ] Security headers OK

- [ ] **CEO/Product Owner:** ___________________ Data: _______
  - [ ] Product ready for launch
  - [ ] Business requirements met
  - [ ] Go/No-Go decision: **GO** ☐ / **NO-GO** ☐

---

## 🎯 SCOR FINAL

**Total checkboxes:** _____ / 250  
**Completion rate:** _____ %

**Criterii Launch:**
- ✅ **Minimum 90%** pentru launch production
- ⚠️ **80-90%:** Launch cu plan remediere în 2 săptămâni
- ❌ **<80%:** NU lansa, fix critical issues first

**Data estimată launch:** _________________

**Status final:** ☐ **READY FOR PRODUCTION** / ☐ **NEEDS MORE WORK**

---

*Checklist generat: 3 Februarie 2026*  
*Versiune: 1.0*  
*Template pentru audit pre-production*
