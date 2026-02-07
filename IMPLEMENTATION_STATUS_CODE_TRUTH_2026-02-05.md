# VitiScan PRO V3 - Implementation Status (Code-Truth)
## Data: 05 Februarie 2026 (verifica data locala)

---

## Rezumat executiv

- Status real: partial functional, cu gap-uri critice pe authz/tenancy, refresh token, test suite si fluxuri front-end.
- Production ready: NU (rate limiting dependent de Redis; test suite instabil; rute neincluse).
- Directie confirmata: Hub Digital viticol + cooperative imediat + cost/kg core + preventie proactiva (BSV + meteo + NDVI); fara diagnostic AI in V3 initial; orice AI doar dupa minimum 24 luni de date complete (toate activitatile din exploatatie).

---

## Backend (realitate din cod)

### Implementat
- FastAPI async + MongoDB (Motor) cu structure pe routes.
- Auth: /register, /login, /me (JWT 60 min).
- CRUD: establishments, parcels, crops, scans.
- Beta onboarding: /beta-request + /admin/beta-requests + completare token.
- AuthZ: /authz (RBAC + ABAC + ReBAC) + audit trail + admin global.
- Billing (basic), password reset, health endpoints.
- Tenancy middleware, logging, CORS, HTTPS redirect (prod), HSTS.

### Lipsa / nealiniat
- Nu exista /auth/refresh (promis in documente vechi, absent in cod).
- Rate limiting necesita Redis; fara Redis nu e production ready.
- Rute invitations/trash exista ca fisiere, dar nu sunt incluse in main.py.
- Inconsistenta endpoint: /beta-request vs /beta-requests in teste/loguri.
- AuthZ decoratori nu sunt aliniati cu modelele actuale (campuri/IDs).
- Lipsesc modele pentru cost/kg, cooperative, tratamente, stoc, deseuri.

### Teste
- pytest exista, dar tests/test_scans.py are eroare de sintaxa -> suite instabila.

---

## Frontend (realitate din cod)

### Implementat (pagini)
- /login, /register, /dashboard
- /beta-request, /register-complete
- /admin/beta-requests, /admin/audit/logs, /admin/global
- /authz/debug
- /parcels (list), /parcels/new, /parcels/[id], /parcels/[id]/share, /parcels/[id]/export, /parcels/map
- /scans, /scans/new
- /team, /settings/profile, /settings/security, /settings/tokens, /billing
- /view/[token]

### Lipsa / incomplet
- Flux complet beta in UI (verificare reala + feedback UI robust).
- Dashboard KPI reale (cost/kg, preventie, coop).
- UI pentru cooperative (portal agregat + benchmark).
- UI pentru calendar/tratamente/stock/deseuri.

---

## UI/UX (realitate)

- Exista componente de navigatie si UI de baza, dar nu exista un shell unificat cu fluxuri coerente.
- Limbaj si UI inconsistente intre zone (admin vs user).
- Lipsesc fluxurile critice: cost/kg, preventie, traseu complet coop.

---

## Triplul sistem de autorizare (RBAC + ABAC + ReBAC)

- Documentat in backend/AUTHORIZATION_SYSTEM.md.
- Implementat ca /authz/check si /authz/why, plus relationships.
- Trebuie aliniat cu modelele curente (user_id/tenant_id, resurse reale).

---

## User Journey (propunere) + mapare modulara

Nota: diagnostic AI este exclus din V3 initial; AI este permis doar dupa minimum 24 luni de date complete despre activitatile exploatatiei.

1) Onboarding & identitate
- Module: Auth + Beta onboarding + Consent
- Cod: backend/app/routes/auth.py, backend/app/routes/beta_requests.py
- Doc: UI_DOCUMENTATION.md, README_QUICK_NAV.md
- Gap: refresh token + SMS flow complet

2) Setup exploatatie + parcele
- Module: Establishments + Parcels + Map
- Cod: backend/app/routes/establishments.py, parcels.py, frontend/app/parcels/*, components/ParcelMap.tsx
- Doc: IGN_LEAFLET_GUIDE.md, UI_DOCUMENTATION.md

3) Calendar de lucrari + tratamente
- Module: Calendar + Treatments (lipsesc in V3)
- Doc V1: seed_events_with_costs.py (V1) + documente cost
- Gap: nu exista in V3

4) Cost/kg core
- Module: Cost Ledger + Import CSV/Excel + KPI
- Gap: nu exista in V3

5) Cooperative portal
- Module: Coop RBAC + agregare + benchmark
- Gap: nu exista in V3

6) Preventie proactiva
- Module: BSV (S3) + Meteo + NDVI + Alertare
- Gap: nu exista in V3

7) Trasabilitate completa (stoc + deseuri)
- Module: Stock + Waste + e-Phy + registre
- Gap: nu exista in V3

---

## Gap-uri critice (blocante pentru productie)

- /auth/refresh lipsa
- Redis pentru rate limiting neconfigurat
- test_scans invalid -> test suite instabila
- Rute neincluse (invitations/trash)
- Aliniere AuthZ cu modele reale

---

## Plan de start (fara estimari)

Faza 0 - Stabilizare
- Fix refresh token
- Fix rate limiting (Redis + fallback)
- Fix test_scans + aliniere endpoint-uri
- Include rute lipsa
- Aliniere AuthZ la modele reale

Faza 1 - Cost/kg core
- Model cost ledger + import CSV/Excel
- Calcul cost/kg per ha + agregare per soi/parcela/exploatatie
- Export PDF/CSV

Faza 2 - Cooperative core
- Portal coop + RBAC dedicat
- Benchmark anonim + dashboard

Faza 3 - Preventie proactiva
- BSV ingest (S3) + meteo + NDVI
- Alertare programata + feedback loop

Faza 4 - AI advice (gated)
- Activare doar dupa minimum 24 luni de date complete (toate activitatile din exploatatie); diagnostic AI blocat pana atunci
- KPI: reducere 10-15% cost/kg anual

---

Nota: Acest document este separat de IMPLEMENTATION_STATUS.md pentru comparatie.
