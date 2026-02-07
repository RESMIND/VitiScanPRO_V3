# VitiScan v3 — STATUS (Release/QA)

## 1) Onboarding
### ✅ Livrat
- /beta-request (formular acces beta) — frontend + API
- /register-complete (finalizare cont) — frontend + API
- /login, /register, /me — API auth + UI

### 🔍 De verificat (manual QA)
- Flux complet beta: request → email/token → completare cont
- Validări și mesaje de eroare (accept_terms/accept_privacy)

### ❌ Nelivrat / Opțional
- MFA (neimplementat)

---

## 2) Core user journey
### ✅ Livrat
- /dashboard (KPI + listare scanări/parcele) — UI + API
- /establishments/new (formular fermă) — UI + API
- /parcels/new (creare parcelă) — UI + API
- /parcels/[id] (detalii parcelă + hartă + scanări) — UI + API
- /scans + /scans/new (listare + upload scan) — UI + API

### 🔍 De verificat (manual QA)
- Permisiuni pe resurse (doar owner vede/parcele)
- Flux creare fermă → parcelă → scanare
- Upload scan (fișiere mari, tipuri valide)

### ❌ Nelivrat / Opțional
- AI scan / analiză automată

---

## 3) Tratamente & Export DRAAF
### ✅ Livrat
- Tratamente (listare + creare) pe /parcels/[id]
- Endpointuri: GET/POST /parcels/{id}/treatments
- Export PDF DRAAF: GET /parcels/{id}/export
- /parcels/[id]/export (UI export)
- Validări: dată nu în viitor, doză > 0, produs listă/override
- Logo-uri DRAAF/firmă via env

### 🔍 De verificat (manual QA)
- Conținut PDF (tabel, layout A4, date corecte)
- Logo-uri și semnătură/dată export
- Produse custom (override) funcțional

### ❌ Nelivrat / Opțional
- Ștergere/editare tratamente

---

## 4) Admin & Audit
### ✅ Livrat
- Admin global: stats + recent users
- Audit: logs + stats
- Beta requests admin (list/approve/reject)
- AuthZ debug/why endpoint

### 🔍 De verificat (manual QA)
- Acces doar admin
- Filtre audit & volum date

---

## 5) Platformă & Config
### ✅ Livrat
- Rate limiting (SlowAPI)
- Logging middleware
- CORS + security headers
- MongoDB (motor) + indexes
- Env config (JWT, S3, etc.)

### 🔍 De verificat (manual QA)
- ENV variabile obligatorii în production
- Config logo-uri export PDF (DRAAF_LOGO_PATH, COMPANY_LOGO_PATH)

---

## 6) UI Pages (extra)
### ✅ Livrat
- /team
- /settings/profile
- /settings/security
- /settings/tokens
- /billing
- /admin/*
- /view/[token]
- /parcels/[id]/share

### 🔍 De verificat (manual QA)
- Navigație între pagini + empty states
- Token share/view flow

---

## 7) Teste
### ✅ Livrat
- Pytest suite (auth, authz, parcels) — passing

### 🔍 De verificat (manual QA)
- Teste UI (manual)
- End-to-end flows

---

## Rezumat livrare
✅ Funcționalități principale livrate pentru release. 
🔍 QA manual recomandat pe fluxurile cheie (onboarding, tratamente, export). 
❌ Funcții opționale nelivrate: AI scan, MFA, edit/delete tratamente.
