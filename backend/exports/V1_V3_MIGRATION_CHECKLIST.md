# VitiScan PRO V1 → V3 Migration Checklist

## Document de Mapping Complet pentru Migrare

---

# 1. LISTĂ COMPLETĂ FEATURE-URI V1 (FUNCȚIONALE)

## 1.1 MODUL: AUTENTIFICARE & ONBOARDING

| # | Feature | Status V1 | Prioritate | Blocant? |
|---|---------|-----------|------------|----------|
| 1.1.1 | Înregistrare cu telefon (FR format) | ✅ Funcțional | P0 | DA |
| 1.1.2 | Login cu telefon + parolă | ✅ Funcțional | P0 | DA |
| 1.1.3 | Verificare 2FA via Twilio SMS | ✅ Funcțional | P1 | NU |
| 1.1.4 | Resetare parolă via SMS | ✅ Funcțional | P1 | NU |
| 1.1.5 | Onboarding wizard (4 pași) | ✅ Funcțional | P0 | DA |
| 1.1.6 | Validare session în localStorage | ✅ Funcțional | P0 | DA |
| 1.1.7 | Logout cu ștergere session | ✅ Funcțional | P0 | DA |

## 1.2 MODUL: PROFIL EXPLOATAȚIE

| # | Feature | Status V1 | Prioritate | Blocant? |
|---|---------|-----------|------------|----------|
| 1.2.1 | Creare profil exploatație | ✅ Funcțional | P0 | DA |
| 1.2.2 | Editare: nume, adresă, SIRET | ✅ Funcțional | P0 | DA |
| 1.2.3 | Editare: suprafață totală, nr. parcele | ✅ Funcțional | P0 | DA |
| 1.2.4 | Editare: tip cultură (BIO/Conv/HVE) | ✅ Funcțional | P1 | NU |
| 1.2.5 | Upload logo exploatație | ✅ Funcțional | P2 | NU |
| 1.2.6 | Setări notificări (email/SMS/Telegram) | ⚠️ Parțial | P2 | NU |
| 1.2.7 | Linkare cont Telegram | ✅ Funcțional | P1 | NU |
| 1.2.8 | Informații certiphyto | ✅ Funcțional | P1 | NU |

## 1.3 MODUL: PARCELE

| # | Feature | Status V1 | Prioritate | Blocant? |
|---|---------|-----------|------------|----------|
| 1.3.1 | Creare parcelă (nume, suprafață, soi) | ✅ Funcțional | P0 | DA |
| 1.3.2 | Desenare contur pe hartă (polygon) | ✅ Funcțional | P0 | DA |
| 1.3.3 | Editare contur (drag & drop vertices) | ✅ Funcțional | P1 | NU |
| 1.3.4 | Calcul automat suprafață din polygon | ✅ Funcțional | P0 | DA |
| 1.3.5 | Atribuire soi (variety) | ✅ Funcțional | P0 | DA |
| 1.3.6 | Atribuire an plantare | ✅ Funcțional | P1 | NU |
| 1.3.7 | Atribuire densitate plantare | ✅ Funcțional | P2 | NU |
| 1.3.8 | Ștergere parcelă | ✅ Funcțional | P0 | DA |
| 1.3.9 | Bulk save parcele | ✅ Funcțional | P1 | NU |
| 1.3.10 | Vizualizare pe hartă IGN | ✅ Funcțional | P0 | DA |
| 1.3.11 | Colorare pe soiuri | ✅ Funcțional | P2 | NU |
| 1.3.12 | Mod planificare vizuală (3 culori) | ✅ Funcțional | P2 | NU |

## 1.4 MODUL: DIAGNOSTIC AI

| # | Feature | Status V1 | Prioritate | Blocant? |
|---|---------|-----------|------------|----------|
| 1.4.1 | Upload foto frunză | ✅ Funcțional | P0 | DA |
| 1.4.2 | Diagnostic AI via GPT-4o Vision | ✅ Funcțional | P0 | DA |
| 1.4.3 | Afișare maladie detectată | ✅ Funcțional | P0 | DA |
| 1.4.4 | Afișare nivel de încredere (%) | ✅ Funcțional | P0 | DA |
| 1.4.5 | Afișare severitate (low/medium/high) | ✅ Funcțional | P0 | DA |
| 1.4.6 | Recomandări tratament | ✅ Funcțional | P0 | DA |
| 1.4.7 | Feedback utilizator (👍/👎) | ✅ Funcțional | P1 | NU |
| 1.4.8 | Chat conversațional post-diagnostic | ✅ Funcțional | P1 | NU |
| 1.4.9 | Creare eveniment calendar din diagnostic | ✅ Funcțional | P1 | NU |
| 1.4.10 | Istoric diagnostice per utilizator | ✅ Funcțional | P1 | NU |
| 1.4.11 | Istoric diagnostice per parcelă | ✅ Funcțional | P1 | NU |
| 1.4.12 | Integrare BSV în răspuns AI | ✅ Funcțional | P2 | NU |

## 1.5 MODUL: CALENDAR & EVENIMENTE

| # | Feature | Status V1 | Prioritate | Blocant? |
|---|---------|-----------|------------|----------|
| 1.5.1 | Vizualizare calendar lunar | ✅ Funcțional | P0 | DA |
| 1.5.2 | Creare eveniment manual | ✅ Funcțional | P0 | DA |
| 1.5.3 | Editare eveniment | ✅ Funcțional | P0 | DA |
| 1.5.4 | Ștergere eveniment | ✅ Funcțional | P0 | DA |
| 1.5.5 | Tipuri eveniment (10+) | ✅ Funcțional | P0 | DA |
| 1.5.6 | Filtrare pe parcelă | ✅ Funcțional | P1 | NU |
| 1.5.7 | Filtrare pe tip eveniment | ✅ Funcțional | P1 | NU |
| 1.5.8 | Export CSV evenimente | ✅ Funcțional | P1 | NU |
| 1.5.9 | Export PDF evenimente | ✅ Funcțional | P1 | NU |
| 1.5.10 | Evenimente auto din AI (recomandări) | ✅ Funcțional | P2 | NU |
| 1.5.11 | Calcul cost per eveniment | ✅ Funcțional | P1 | NU |
| 1.5.12 | Vizualizare ferestre optime tratament | ✅ Funcțional | P2 | NU |

## 1.6 MODUL: TRATAMENTE FITOSANITARE

| # | Feature | Status V1 | Prioritate | Blocant? |
|---|---------|-----------|------------|----------|
| 1.6.1 | Creare tratament | ✅ Funcțional | P0 | DA |
| 1.6.2 | Căutare produs în e-Phy (ANSES) | ✅ Funcțional | P0 | DA |
| 1.6.3 | Completare automată AMM, ZNT, DAR | ✅ Funcțional | P0 | DA |
| 1.6.4 | Înregistrare doză, suprafață | ✅ Funcțional | P0 | DA |
| 1.6.5 | Calcul cantitate utilizată | ✅ Funcțional | P0 | DA |
| 1.6.6 | Validare conformitate ZNT | ✅ Funcțional | P1 | NU |
| 1.6.7 | Înregistrare applicateur + certiphyto | ✅ Funcțional | P1 | NU |
| 1.6.8 | Înregistrare lot produs | ✅ Funcțional | P2 | NU |
| 1.6.9 | Decrementare automată stoc | ⚠️ Parțial | P2 | NU |
| 1.6.10 | Export registru DRAAF PDF | ✅ Funcțional | P0 | DA |
| 1.6.11 | Export registru Excel | ✅ Funcțional | P1 | NU |

## 1.7 MODUL: STOC FITOSANITAR

| # | Feature | Status V1 | Prioritate | Blocant? |
|---|---------|-----------|------------|----------|
| 1.7.1 | Creare lot (achiziție) | ✅ Funcțional | P1 | NU |
| 1.7.2 | Editare lot | ✅ Funcțional | P1 | NU |
| 1.7.3 | Ștergere lot | ✅ Funcțional | P1 | NU |
| 1.7.4 | Înregistrare mișcări (intrare/ieșire) | ✅ Funcțional | P1 | NU |
| 1.7.5 | Istoric mișcări per lot | ✅ Funcțional | P2 | NU |
| 1.7.6 | Alertă stoc scăzut | ✅ Funcțional | P2 | NU |
| 1.7.7 | Alertă expirare | ✅ Funcțional | P2 | NU |
| 1.7.8 | Dashboard stoc | ✅ Funcțional | P1 | NU |
| 1.7.9 | Export stoc CSV/XLSX | ✅ Funcțional | P2 | NU |

## 1.8 MODUL: DEȘEURI (WASTE/ADIVALOR)

| # | Feature | Status V1 | Prioritate | Blocant? |
|---|---------|-----------|------------|----------|
| 1.8.1 | Înregistrare eveniment deșeu | ✅ Funcțional | P2 | NU |
| 1.8.2 | Tipuri deșeuri (EVPP, PPNU, etc.) | ✅ Funcțional | P2 | NU |
| 1.8.3 | Metode eliminare (Adivalor, etc.) | ✅ Funcțional | P2 | NU |
| 1.8.4 | Dashboard deșeuri | ✅ Funcțional | P2 | NU |
| 1.8.5 | Export deșeuri | ✅ Funcțional | P3 | NU |

## 1.9 MODUL: METEO

| # | Feature | Status V1 | Prioritate | Blocant? |
|---|---------|-----------|------------|----------|
| 1.9.1 | Meteo curentă per parcelă | ✅ Funcțional | P0 | DA |
| 1.9.2 | Prognoză 5 zile | ✅ Funcțional | P1 | NU |
| 1.9.3 | Istoric meteo | ✅ Funcțional | P2 | NU |
| 1.9.4 | Alerte meteo critice | ⚠️ Manual | P1 | NU |
| 1.9.5 | Widget meteo în dashboard | ✅ Funcțional | P1 | NU |
| 1.9.6 | Overlay meteo pe hartă | ✅ Funcțional | P2 | NU |
| 1.9.7 | Ferestre optime tratament | ✅ Funcțional | P2 | NU |

## 1.10 MODUL: NDVI & SATELIT

| # | Feature | Status V1 | Prioritate | Blocant? |
|---|---------|-----------|------------|----------|
| 1.10.1 | Calcul NDVI per parcelă | ✅ Funcțional | P1 | NU |
| 1.10.2 | Istoric NDVI (12 luni) | ✅ Funcțional | P2 | NU |
| 1.10.3 | Colorare parcele pe NDVI | ✅ Funcțional | P2 | NU |
| 1.10.4 | Alerte NDVI scăzut | ✅ Funcțional | P2 | NU |
| 1.10.5 | Widget NDVI în detalii parcelă | ✅ Funcțional | P2 | NU |

## 1.11 MODUL: ZNT (ZONE NON TRAITÉES)

| # | Feature | Status V1 | Prioritate | Blocant? |
|---|---------|-----------|------------|----------|
| 1.11.1 | Afișare cursuri apă BCAE PAC | ✅ Funcțional | P1 | NU |
| 1.11.2 | Afișare BD TOPO (indicativ) | ✅ Funcțional | P2 | NU |
| 1.11.3 | Afișare clădiri/locuințe | ✅ Funcțional | P2 | NU |
| 1.11.4 | Calcul buffer zones | ✅ Funcțional | P1 | NU |
| 1.11.5 | Verificare conformitate | ✅ Funcțional | P1 | NU |
| 1.11.6 | Adăugare puncte personalizate | ✅ Funcțional | P2 | NU |
| 1.11.7 | Override ZNT manual | ✅ Funcțional | P2 | NU |

## 1.12 MODUL: BSV (BULETINE SANITARE)

| # | Feature | Status V1 | Prioritate | Blocant? |
|---|---------|-----------|------------|----------|
| 1.12.1 | Afișare BSV-uri PACA (2021-2025) | ✅ Funcțional | P2 | NU |
| 1.12.2 | Extragere alertes din PDF | ✅ Funcțional | P2 | NU |
| 1.12.3 | Timeline BSV-uri | ✅ Funcțional | P2 | NU |
| 1.12.4 | Query BSV via ARES | ✅ Funcțional | P2 | NU |
| 1.12.5 | Crawler automat BSV noi | ❌ Nu funcționează | P3 | NU |

## 1.13 MODUL: EXPORT PDF

| # | Feature | Status V1 | Prioritate | Blocant? |
|---|---------|-----------|------------|----------|
| 1.13.1 | Template DRAAF (registru oficial) | ✅ Funcțional | P0 | DA |
| 1.13.2 | Template Économique (costuri) | ✅ Funcțional | P1 | NU |
| 1.13.3 | Template Certification (HVE/AB) | ✅ Funcțional | P2 | NU |
| 1.13.4 | Template Main d'Œuvre | ✅ Funcțional | P2 | NU |
| 1.13.5 | Filtrare pe perioadă/campanie | ✅ Funcțional | P1 | NU |
| 1.13.6 | Filtrare pe parcele | ✅ Funcțional | P1 | NU |
| 1.13.7 | Includere GPS | ✅ Funcțional | P1 | NU |
| 1.13.8 | Includere meteo | ✅ Funcțional | P2 | NU |
| 1.13.9 | Export Excel (XLSX) | ✅ Funcțional | P1 | NU |

## 1.14 MODUL: HĂRȚI

| # | Feature | Status V1 | Prioritate | Blocant? |
|---|---------|-----------|------------|----------|
| 1.14.1 | Hartă IGN (OSM, Satellite, Plan, Cadastre) | ✅ Funcțional | P0 | DA |
| 1.14.2 | Hartă ZNT | ✅ Funcțional | P1 | NU |
| 1.14.3 | Hartă Meteo/NDVI | ✅ Funcțional | P2 | NU |
| 1.14.4 | Colorare parcele pe soiuri | ✅ Funcțional | P2 | NU |
| 1.14.5 | Mod planificare vizuală | ✅ Funcțional | P2 | NU |
| 1.14.6 | Legendă editabilă | ✅ Funcțional | P2 | NU |
| 1.14.7 | Fullscreen mode | ✅ Funcțional | P2 | NU |

## 1.15 MODUL: STATISTICI

| # | Feature | Status V1 | Prioritate | Blocant? |
|---|---------|-----------|------------|----------|
| 1.15.1 | Stats diagnostice per user | ✅ Funcțional | P2 | NU |
| 1.15.2 | Distribuție maladii (Pie Chart) | ✅ Funcțional | P2 | NU |
| 1.15.3 | Distribuție severități (Bar Chart) | ✅ Funcțional | P2 | NU |
| 1.15.4 | Timeline (Line Chart) | ✅ Funcțional | P2 | NU |
| 1.15.5 | Stats per parcelă | ✅ Funcțional | P2 | NU |
| 1.15.6 | Precizie AI (feedback) | ✅ Funcțional | P2 | NU |
| 1.15.7 | Admin: stats globale platformă | ✅ Funcțional | P2 | NU |

## 1.16 MODUL: TELEGRAM BOT

| # | Feature | Status V1 | Prioritate | Blocant? |
|---|---------|-----------|------------|----------|
| 1.16.1 | Linkare cont via telefon | ✅ Funcțional | P2 | NU |
| 1.16.2 | Comenzi: /start, /help, /parcels | ✅ Funcțional | P2 | NU |
| 1.16.3 | Comenzi: /alerts, /weather | ✅ Funcțional | P2 | NU |
| 1.16.4 | Notificări alerte maladii | ⚠️ Manual | P2 | NU |
| 1.16.5 | Notificări backup (admin) | ✅ Funcțional | P2 | NU |
| 1.16.6 | Confirmare backup via bot | ✅ Funcțional | P2 | NU |

## 1.17 MODUL: ADMIN

| # | Feature | Status V1 | Prioritate | Blocant? |
|---|---------|-----------|------------|----------|
| 1.17.1 | Lista utilizatori | ✅ Funcțional | P1 | NU |
| 1.17.2 | Detalii utilizator | ✅ Funcțional | P1 | NU |
| 1.17.3 | Impersonare utilizator | ✅ Funcțional | P2 | NU |
| 1.17.4 | RBAC (roles/permissions) | ✅ Funcțional | P2 | NU |
| 1.17.5 | Toate parcelele pe hartă | ✅ Funcțional | P2 | NU |
| 1.17.6 | Feedbacks utilizatori | ✅ Funcțional | P2 | NU |
| 1.17.7 | AI Calibration | ✅ Funcțional | P2 | NU |
| 1.17.8 | Backup management | ✅ Funcțional | P1 | NU |
| 1.17.9 | Logs activitate | ✅ Funcțional | P2 | NU |

## 1.18 MODUL: ARES (ASISTENT AI)

| # | Feature | Status V1 | Prioritate | Blocant? |
|---|---------|-----------|------------|----------|
| 1.18.1 | Chat conversațional | ✅ Funcțional | P2 | NU |
| 1.18.2 | Interogare BSV-uri | ✅ Funcțional | P2 | NU |
| 1.18.3 | Recomandări personalizate | ✅ Funcțional | P2 | NU |
| 1.18.4 | Acces context exploatație | ✅ Funcțional | P2 | NU |

---

# 2. FLUXURI CRITICE END-TO-END

## Flux 1: ONBOARDING → EXPLOATAȚIE → PARCELĂ → DIAGNOSTIC

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ 1. LANDING    │────>│ 2. REGISTER   │────>│ 3. ONBOARDING │────>│ 4. DASHBOARD  │
│ /             │     │ /auth         │     │ /onboarding   │     │ /dashboard    │
└───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘
                                                   │
                      ┌────────────────────────────┘
                      v
┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ 5. PROFIL     │────>│ 6. ADD PARCEL │────>│ 7. DRAW MAP   │────>│ 8. SAVE       │
│ exploatație   │     │ modal         │     │ polygon       │     │ parcel        │
└───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘
                                                                          │
                      ┌───────────────────────────────────────────────────┘
                      v
┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ 9. UPLOAD     │────>│ 10. AI DIAG   │────>│ 11. RESULTS   │────>│ 12. FEEDBACK  │
│ photo         │     │ GPT-4o        │     │ + recommend   │     │ + calendar    │
└───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘
```

**API-uri implicate (în ordine):**
1. `POST /api/auth/register`
2. `POST /api/auth/login`
3. `PUT /api/exploitation/profile/{user_id}`
4. `POST /api/parcels`
5. `POST /api/parcels/bulk-save`
6. `POST /api/upload`
7. `POST /api/diagnostic/v2`
8. `POST /api/diagnostic/{id}/feedback`
9. `POST /api/diagnostic/{id}/create-calendar-events`

---

## Flux 2: PARCELĂ → TRATAMENT → STOC → REGISTRU PDF

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ 1. CALENDAR   │────>│ 2. ADD EVENT  │────>│ 3. SEARCH     │────>│ 4. SELECT     │
│ parcelă       │     │ treatment     │     │ e-Phy         │     │ product       │
└───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘
                                                                          │
                      ┌───────────────────────────────────────────────────┘
                      v
┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ 5. FILL FORM  │────>│ 6. VALIDATE   │────>│ 7. SAVE       │────>│ 8. UPDATE     │
│ dose, surface │     │ ZNT/DAR       │     │ treatment     │     │ stock (auto)  │
└───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘
                                                                          │
                      ┌───────────────────────────────────────────────────┘
                      v
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ 9. EXPORT     │────>│ 10. SELECT    │────>│ 11. DOWNLOAD  │
│ modal         │     │ DRAAF         │     │ PDF           │
└───────────────┘     └───────────────┘     └───────────────┘
```

**API-uri implicate:**
1. `GET /api/events/parcel/{parcel_id}`
2. `GET /api/ephy/products/search?q=...`
3. `GET /api/ephy/products/{product_id}`
4. `GET /api/stock/dashboard?user_id=...`
5. `POST /api/treatments/v2`
6. `POST /api/stock/movement` (auto)
7. `POST /api/export/pdf/advanced`

---

## Flux 3: DIAGNOSTIC → CALENDAR → COST/KG

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ 1. DIAGNOSTIC │────>│ 2. RECOMMEND  │────>│ 3. CREATE     │────>│ 4. EVENT      │
│ AI            │     │ treatment     │     │ cal. event    │     │ saved         │
└───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘
                                                                          │
                      ┌───────────────────────────────────────────────────┘
                      v
┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ 5. CALENDAR   │────>│ 6. COSTS      │────>│ 7. HARVEST    │────>│ 8. COST/KG    │
│ view          │     │ accumulated   │     │ production    │     │ calculated    │
└───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘
```

**Formula Cost/kg:**
```
cost_par_kg = total_costs_ht / kg_production

Unde:
- total_costs_ht = Σ(costs_manuels + costs_mécaniques + costs_traitements)
- kg_production = rendement_kg_ha × surface_ha
```

---

# 3. ECRANE/ROUTE-URI V1 (UI MAP)

## 3.1 PAGINI PUBLICE

| Route | Componentă | Status | Must Have |
|-------|------------|--------|-----------|
| `/` | `Landing.jsx` | ✅ | DA |
| `/onboarding` | `Onboarding.jsx` | ✅ | DA |
| `/confidentialite` | `Confidentialite.jsx` | ✅ | DA (RGPD) |
| `/prestateurs-viticoles` | `PrestatairesViticoles.jsx` | ✅ | NU |
| `/login` | `Auth.js` | ✅ | DA |
| `/auth` | `Auth.js` (alias) | ✅ | DA |

## 3.2 PAGINI AUTENTIFICATE

| Route | Componentă | Status | Must Have |
|-------|------------|--------|-----------|
| `/dashboard` | `Dashboard.js` | ✅ | DA |
| `/phyto-registry` | `PhytoRegistry.js` | ✅ | DA |
| `/profil-exploitation` | `ProfilExploitation.js` | ✅ | DA |
| `/setup` | `SetupWizard.js` | ✅ | DA |
| `/ai-test` | `AITestPage.jsx` | ✅ | NU |

## 3.3 PAGINI ADMIN

| Route | Componentă | Status | Must Have |
|-------|------------|--------|-----------|
| `/admin` | `Dashboard.js` (adminMode) | ✅ | DA |
| `/admin/feedbacks` | `AdminFeedbacks.jsx` | ✅ | NU |
| `/admin/users` | `AdminUsers.jsx` | ✅ | DA |
| `/admin/users/:userId` | `AdminUserDetail.jsx` | ✅ | NU |
| `/admin/parcelles` | `AdminParcelles.jsx` | ✅ | NU |
| `/admin/rbac` | `AdminRBAC.jsx` | ✅ | NU |

## 3.4 TAB-URI DASHBOARD

| Tab | Descriere | Status | Must Have |
|-----|-----------|--------|-----------|
| `upload` | Diagnostic AI (home) | ✅ | DA |
| `result` | Rezultat diagnostic | ✅ | DA |
| `maps` | Hărți IGN/ZNT/Meteo | ✅ | DA |
| `history` | Istoric diagnostice | ✅ | DA |
| `alerts` | Alerte maladii | ✅ | DA |
| `stats` | Statistici | ✅ | NU |
| `weather` | Meteo detaliată | ✅ | NU |
| `gdpr` | Setări RGPD | ✅ | DA (legal) |
| `contact` | Contact/Support | ✅ | NU |
| `admin` | Admin panel | ✅ | DA (admin) |
| `users` | Users list (admin) | ✅ | DA (admin) |
| `ai-calibration` | AI calibration | ✅ | NU |

---

# 4. API-URI V1 EXPUSE

## 4.1 AUTH (6 endpoints)

| Endpoint | Method | Auth | Payload | Response |
|----------|--------|------|---------|----------|
| `/api/auth/register` | POST | No | `{phone, password, nom?, prenom?}` | `{user}` |
| `/api/auth/login` | POST | No | `{phone, password}` | `{user, token?}` |
| `/api/auth/verify-2fa` | POST | No | `{phone, code}` | `{verified}` |
| `/api/auth/request-reset` | POST | No | `{phone}` | `{sent}` |
| `/api/auth/reset-password` | POST | No | `{phone, code, new_password}` | `{success}` |
| `/api/auth/login/v2` | POST | No | `{phone, password}` | ❌ 401 (BUG) |

## 4.2 EXPLOITATION (4 endpoints)

| Endpoint | Method | Auth | Payload | Response |
|----------|--------|------|---------|----------|
| `/api/exploitation/profile/{user_id}` | GET | Yes | - | `{profile}` |
| `/api/exploitation/profile/{user_id}` | PUT | Yes | `{nom, adresse, siret...}` | `{profile}` |
| `/api/exploitation/setup-complete/{user_id}` | POST | Yes | - | `{success}` |
| `/api/exploitation/onboarding-status/{user_id}` | GET | Yes | - | `{status}` |

## 4.3 PARCELS (8 endpoints)

| Endpoint | Method | Auth | Payload | Response |
|----------|--------|------|---------|----------|
| `/api/parcels/{user_id}` | GET | Yes | - | `[parcels]` |
| `/api/parcels` | POST | Yes | `{name, area_ha, variety, geometry}` | `{parcel}` |
| `/api/parcels/{parcel_id}` | PUT | Yes | `{name?, area_ha?, geometry?}` | `{parcel}` |
| `/api/parcels/{parcel_id}` | DELETE | Yes | - | `{deleted}` |
| `/api/parcels/bulk-save` | POST | Yes | `{parcels: [...]}` | `{parcels}` |
| `/api/parcels/{parcel_id}/geometry` | PUT | Yes | `{geometry}` | `{parcel}` |
| `/api/variety-settings/{user_id}` | GET | Yes | - | `{settings}` |
| `/api/variety-settings/{user_id}` | PUT | Yes | `{colors, custom}` | `{settings}` |

## 4.4 DIAGNOSTIC (12 endpoints)

| Endpoint | Method | Auth | Payload | Response |
|----------|--------|------|---------|----------|
| `/api/upload` | POST | Yes | FormData (image) | `{file_url}` |
| `/api/diagnostic/v2` | POST | Yes | `{image_url, parcel_id, user_id}` | `{diagnostic}` |
| `/api/diagnostic/{id}/feedback` | POST | Yes | `{correct, correction?}` | `{saved}` |
| `/api/diagnostic/{id}/chat` | POST | Yes | `{message}` | `{response}` |
| `/api/diagnostic/{id}/chat-with-image` | POST | Yes | `{message, image_url}` | `{response}` |
| `/api/diagnostic/{id}/conversation` | GET | Yes | - | `[messages]` |
| `/api/diagnostic/{id}/create-calendar-events` | POST | Yes | `{parcel_id}` | `{events}` |
| `/api/diagnostics/history/{user_id}` | GET | Yes | - | `[diagnostics]` |
| `/api/diagnostics/parcel/{parcel_id}` | GET | Yes | - | `[diagnostics]` |
| `/api/disease-treatments/{disease_key}` | GET | Yes | - | `{treatments}` |
| `/api/diagnostic/v2/feedback` | POST | Yes | `{feedback}` | `{saved}` |
| `/api/diagnostic/v2/feedback/analytics` | GET | Yes | - | `{analytics}` |

## 4.5 EVENTS (7 endpoints)

| Endpoint | Method | Auth | Payload | Response |
|----------|--------|------|---------|----------|
| `/api/events` | POST | Yes | `{parcel_id, event_type, date...}` | `{event}` |
| `/api/events/parcel/{parcel_id}` | GET | Yes | - | `[events]` |
| `/api/events/user/{user_id}` | GET | Yes | - | `[events]` |
| `/api/events/{event_id}` | PUT | Yes | `{title?, date?...}` | `{event}` |
| `/api/events/{event_id}` | DELETE | Yes | - | `{deleted}` |
| `/api/events/export/csv` | GET | Yes | `?parcel_id=&start=&end=` | CSV file |
| `/api/events/{recommendation_id}/apply-treatment` | POST | Yes | - | `{applied}` |

## 4.6 TREATMENTS (8 endpoints)

| Endpoint | Method | Auth | Payload | Response |
|----------|--------|------|---------|----------|
| `/api/treatments/v2` | POST | Yes | `{parcel_id, product_name, dose...}` | `{treatment}` |
| `/api/treatments/v2` | GET | Yes | `?user_id=&parcel_id=` | `[treatments]` |
| `/api/treatments/{treatment_id}` | GET | Yes | - | `{treatment}` |
| `/api/treatments/{treatment_id}` | DELETE | Yes | - | `{deleted}` |
| `/api/treatments/parcel/{parcel_id}` | GET | Yes | - | `[treatments]` |
| `/api/treatments/export/v2` | GET | Yes | `?user_id=&format=` | CSV/XLSX |
| `/api/treatments/export/csv` | GET | Yes | `?parcel_id=` | CSV file |
| `/api/export/pdf/advanced` | POST | Yes | `{template, parcel_ids...}` | PDF blob |

## 4.7 STOCK (8 endpoints)

| Endpoint | Method | Auth | Payload | Response |
|----------|--------|------|---------|----------|
| `/api/stock/dashboard` | GET | Yes | `?user_id=` | `{positions}` |
| `/api/stock/batch` | POST | Yes | `{product_name, quantity...}` | `{batch}` |
| `/api/stock/batch/{batch_id}` | PUT | Yes | `{quantity?, expiration?}` | `{batch}` |
| `/api/stock/batch/{batch_id}` | DELETE | Yes | - | `{deleted}` |
| `/api/stock/movement` | POST | Yes | `{batch_id, type, quantity}` | `{movement}` |
| `/api/stock/batch/{batch_id}/history` | GET | Yes | - | `[movements]` |
| `/api/stock/alerts` | GET | Yes | `?user_id=` | `[alerts]` |
| `/api/stock/export` | GET | Yes | `?user_id=&format=` | CSV/XLSX |

## 4.8 WASTE (6 endpoints)

| Endpoint | Method | Auth | Payload | Response |
|----------|--------|------|---------|----------|
| `/api/waste/list` | GET | Yes | `?user_id=&campaign=` | `[waste_events]` |
| `/api/waste` | POST | Yes | `{waste_type, quantity...}` | `{waste}` |
| `/api/waste/{id}` | PUT | Yes | `{...}` | `{waste}` |
| `/api/waste/{id}` | DELETE | Yes | - | `{deleted}` |
| `/api/waste/dashboard/{user_id}` | GET | Yes | - | `{summary}` |
| `/api/waste/export` | GET | Yes | `?user_id=&format=` | CSV/XLSX |

## 4.9 E-PHY/ANSES (4 endpoints)

| Endpoint | Method | Auth | Payload | Response |
|----------|--------|------|---------|----------|
| `/api/ephy/products/search` | GET | Yes | `?q=&culture=&etat=&limit=` | `{results}` |
| `/api/ephy/products/{product_id}` | GET | Yes | - | `{product, dsr, znt, usages}` |
| `/api/ephy/products/by-amm/{numero_amm}` | GET | Yes | - | `{product}` |
| `/api/ephy/products/match` | POST | Yes | `{nom_commercial}` | `{match}` |

## 4.10 WEATHER (8 endpoints)

| Endpoint | Method | Auth | Payload | Response |
|----------|--------|------|---------|----------|
| `/api/weather` | GET | Yes | `?lat=&lon=` | `{current}` |
| `/api/weather/{parcel_id}/current` | GET | Yes | - | `{weather}` |
| `/api/parcels/{parcel_id}/weather/current` | GET | Yes | - | `{weather}` |
| `/api/parcels/{parcel_id}/weather/forecast` | GET | Yes | - | `{forecast}` |
| `/api/parcels/{parcel_id}/weather` | GET | Yes | - | `{weather}` |
| `/api/weather/history/{parcel_id}` | GET | Yes | - | `{history}` |
| `/api/weather/parcel/{parcel_id}/history` | GET | Yes | - | `{history}` |
| `/api/weather/{parcel_id}/optimal-windows` | GET | Yes | - | `{windows}` |

## 4.11 NDVI (5 endpoints)

| Endpoint | Method | Auth | Payload | Response |
|----------|--------|------|---------|----------|
| `/api/ndvi/{parcel_id}/calculate` | POST | Yes | - | `{ndvi}` |
| `/api/ndvi/{parcel_id}/current` | GET | Yes | - | `{ndvi}` |
| `/api/ndvi/{parcel_id}/history` | GET | Yes | - | `[ndvi_history]` |
| `/api/ndvi/alerts` | GET | Yes | `?user_id=` | `[alerts]` |
| `/api/ndvi/operators/test` | GET | Yes | - | `{test}` |

## 4.12 ZNT (7 endpoints)

| Endpoint | Method | Auth | Payload | Response |
|----------|--------|------|---------|----------|
| `/api/znt/parcelle/{parcelle_id}` | GET | Yes | - | `{znt_data}` |
| `/api/znt/traitement/{traitement_id}` | GET | Yes | - | `{compliance}` |
| `/api/znt/custom-points` | GET | Yes | `?user_id=` | `[points]` |
| `/api/znt/custom-points` | POST | Yes | `{type, lat, lng, parcel_id}` | `{point}` |
| `/api/znt/custom-points/{point_id}` | DELETE | Yes | - | `{deleted}` |
| `/api/znt/check-compliance` | GET | Yes | `?parcel_id=&znt=` | `{compliance}` |
| `/api/cadastre/overlay` | GET | No | `?bbox=` | `{features}` |

## 4.13 BSV (6 endpoints)

| Endpoint | Method | Auth | Payload | Response |
|----------|--------|------|---------|----------|
| `/api/bsv/latest` | GET | Yes | - | `{bulletin}` |
| `/api/bsv` | GET | Yes | `?limit=` | `[bulletins]` |
| `/api/bsv/year/{year}` | GET | Yes | - | `[bulletins]` |
| `/api/bsv/timeline` | GET | Yes | - | `{timeline}` |
| `/api/bsv/crawl` | POST | Admin | - | `{crawled}` |
| `/api/ares/query-bsv` | GET | Yes | `?query=` | `{response}` |

## 4.14 ADMIN (15+ endpoints)

| Endpoint | Method | Auth | Response |
|----------|--------|------|----------|
| `/api/admin/users/all` | GET | Admin | `[users]` |
| `/api/admin/users/{id}` | GET | Admin | `{user}` |
| `/api/admin/users/{id}` | DELETE | Admin | `{deleted}` |
| `/api/admin/stats` | GET | Admin | `{stats}` |
| `/api/admin/backup/request` | POST | Admin | `{request_id}` |
| `/api/admin/backup/list` | GET | Admin | `[backups]` |
| `/api/admin/impersonate/{user_id}` | POST | Admin | `{token}` |
| `/api/admin/logs` | GET | Admin | `[logs]` |
| `/api/telegram/webhook` | POST | No | `{ok}` |

---

# 5. INTEGRĂRI EXTERNE V1

## 5.1 OBLIGATORII LA LANSARE

| Integrare | Provider | Utilizare | Status | Obligatorie |
|-----------|----------|-----------|--------|-------------|
| **LLM Vision** | OpenAI GPT-4o | Diagnostic AI foto | ✅ | DA |
| **Meteo** | Open-Meteo | Condiții curente + prognoză | ✅ | DA |
| **Hărți bază** | OpenStreetMap | Tiles hartă | ✅ | DA |
| **Hărți FR** | IGN Géoportail | Cadastre, Ortho, Plan | ✅ | DA |
| **MongoDB** | MongoDB Atlas | Bază de date | ✅ | DA |

## 5.2 IMPORTANTE DAR NU BLOCANTE

| Integrare | Provider | Utilizare | Status | Obligatorie |
|-----------|----------|-----------|--------|-------------|
| **SMS/2FA** | Twilio | Verificare, reset parolă | ✅ | NU (alt metod auth) |
| **Telegram** | Telegram Bot API | Notificări, comenzi | ✅ | NU |
| **NDVI Satelit** | Sentinel Hub | Date vegetație | ⚠️ Placeholder | NU |
| **ZNT/BCAE** | IGN WFS | Cursuri apă oficiale | ✅ | NU |
| **Overlay meteo** | OpenWeatherMap | Tiles meteo | ✅ | NU |

## 5.3 NICE-TO-HAVE

| Integrare | Provider | Utilizare | Status | Obligatorie |
|-----------|----------|-----------|--------|-------------|
| **BSV Crawling** | DRAAF PACA | Buletine sanitare | ❌ Nu funcționează | NU |
| **S3 Backup** | AWS S3 | Stocare backup | ✅ | NU |
| **AI TTS** | - | Text-to-speech | ❌ Nu implementat | NU |

---

# 6. MODEL DE DATE V1

## 6.1 COLECȚII MONGODB

| Colecție | Documente | Rol |
|----------|-----------|-----|
| `users` | ~59 refs | Utilizatori + profile |
| `parcels` | ~59 refs | Parcele cu geometrii |
| `parcel_events` | ~39 refs | Evenimente calendar |
| `diagnostics` | ~25 refs | Diagnostice AI |
| `treatments` | ~13 refs | Tratamente phyto |
| `productions` | ~15 refs | Producții/recoltă |
| `ndvi_data` | ~14 refs | Date NDVI |
| `weather_alerts` | ~12 refs | Alerte meteo |
| `soil_analyses` | ~10 refs | Analize sol |
| `bsv_bulletins` | ~4 refs | Buletine BSV |
| `stock_batches` | - | Loturi stoc |
| `stock_movements` | - | Mișcări stoc |
| `waste_events` | - | Deșeuri |
| `ephy_products_v2` | 13,488 | Produse ANSES |
| `ephy_usages_v2` | - | Utilizări produse |

## 6.2 ENTITĂȚI PRINCIPALE

### User (users)
```javascript
{
  id: String (UUID),           // OBLIGATORIU
  phone: String,               // OBLIGATORIU (format FR)
  password_hash: String,       // OBLIGATORIU
  nom: String,
  prenom: String,
  email: String,
  is_admin: Boolean,
  telegram_id: String,
  
  // Profil exploatație
  exploitation_nom: String,
  exploitation_adresse: String,
  exploitation_siret: String,
  surface_totale_ha: Number,
  type_culture: String,        // BIO, CONV, HVE
  certiphyto_numero: String,
  
  // Metadata
  created_at: ISODate,
  last_login: ISODate,
  onboarding_completed: Boolean
}
```

### Parcel (parcels)
```javascript
{
  id: String (UUID),           // OBLIGATORIU
  user_id: String,             // OBLIGATORIU (ref users.id)
  name: String,                // OBLIGATORIU
  area_ha: Number,             // OBLIGATORIU
  variety: String,             // OBLIGATORIU (soi)
  
  // Geometrie
  geometry: {                  // OBLIGATORIU
    type: "Polygon",
    coordinates: [[[lng, lat], ...]]
  },
  center_lat: Number,
  center_lng: Number,
  
  // Opțional
  year_planted: Number,
  density: Number,             // plants/ha
  row_spacing: Number,
  vine_spacing: Number,
  
  created_at: ISODate,
  updated_at: ISODate
}
```

### ParcelEvent (parcel_events)
```javascript
{
  id: String (UUID),           // OBLIGATORIU
  parcel_id: String,           // OBLIGATORIU
  user_id: String,             // OBLIGATORIU
  event_type: String,          // OBLIGATORIU (din EVENT_TYPES)
  title: String,
  description: String,
  event_date: ISODate,         // OBLIGATORIU
  status: String,              // planned, completed, cancelled
  
  // Costuri
  cost_total_ht: Number,
  cost_per_ha: Number,
  hours_worked: Number,
  
  // Tratament specific
  product_name: String,
  product_amm: String,
  dose: Number,
  
  source: String,              // manual, intelligent
  auto_created: Boolean,
  
  created_at: ISODate
}
```

### Diagnostic (diagnostics)
```javascript
{
  id: String (UUID),           // OBLIGATORIU
  user_id: String,             // OBLIGATORIU
  parcel_id: String,
  image_url: String,           // OBLIGATORIU
  
  // Rezultat AI
  disease: String,             // OBLIGATORIU
  confidence: Number,          // OBLIGATORIU (0-100)
  severity: String,            // low, medium, high
  recommendations: [String],
  
  // Feedback
  feedback_correct: Boolean,
  feedback_correction: String,
  feedback_date: ISODate,
  
  // Context
  weather_snapshot: Object,
  bsv_bulletin: Object,
  
  created_at: ISODate
}
```

### Treatment (treatments)
```javascript
{
  id: String (UUID),           // OBLIGATORIU
  parcel_id: String,           // OBLIGATORIU
  user_id: String,             // OBLIGATORIU
  date_traitement: ISODate,    // OBLIGATORIU
  
  // Produs
  product_name: String,        // OBLIGATORIU
  product_amm: String,         // OBLIGATORIU
  
  // Application
  dose: Number,                // OBLIGATORIU
  dose_unite: String,          // L/ha, kg/ha
  surface_traitee_ha: Number,  // OBLIGATORIU
  quantite_produit_utilisee: Number,
  
  // Cible
  cible: String,               // Mildiou, Oïdium...
  
  // Conformité
  znt_aquatique: Number,
  delai_avant_recolte: Number,
  validation_status: String,
  
  // Applicateur
  applicateur_nom: String,
  applicateur_certiphyto: String,
  
  // Traçabilité
  lot_produit: String,
  conditions_meteo: Object,
  
  created_at: ISODate
}
```

---

# 7. REGULI DE BUSINESS ESENȚIALE

## 7.1 VALIDĂRI

| Regulă | Câmp | Validare |
|--------|------|----------|
| Telefon FR | `phone` | Regex: `^(0033\|\\+33\|0)[1-9][0-9]{8}$` |
| Suprafață | `area_ha` | > 0, max 1000 |
| Doză | `dose` | > 0, conform AMM |
| ZNT | `znt_aquatique` | Conform produs e-Phy |
| DAR | `delai_avant_recolte` | Conform produs e-Phy |
| NDVI | `ndvi_value` | 0-100 (%) |
| Coordonate | `geometry` | Valid GeoJSON Polygon |

## 7.2 CALCULE COST/KG

### Formula Principală
```
COST_PAR_KG = TOTAL_COUTS_HT / KG_PRODUCTION

Unde:
TOTAL_COUTS_HT = 
  + Σ(events manuels × TAUX_MANUEL)           // 23 €/h
  + Σ(events mécaniques × TAUX_MECANIQUE)     // 70 €/h
  + Σ(traitements × cost_produit)
  + Σ(fertilisation)
  + vendange

KG_PRODUCTION = rendement_kg_ha × surface_ha
```

### Constantes
```javascript
const TAUX_MANUEL = 23;        // €/h
const TAUX_MECANIQUE = 70;     // €/h (tractor + chauffeur)
const TVA_RATE = 0.20;         // 20%

const HEURES_PAR_HA = {
  taille: 80,                  // h/ha
  attachage: 10,
  ébourgeonnage: 9,
  effeuillage: 8,
  relevage: 9,                 // × 2 passages
  vendange_manuelle: 80        // dépend kg/ha
};

const COUT_MECANIQUE_HA = {
  pretaille: 100,
  broyage: 75,
  rognage: 100,                // × 2 passages
  travail_sol: 500,
  vendange_mecanique: 490,
  transport: 95
};

const COUT_TRAITEMENT_HA = 50; // par passage (7 passages/an)
```

## 7.3 KPIs CALCULÉS

| KPI | Formule | Unité |
|-----|---------|-------|
| **Coût/ha total** | `Σ(costs) / surface_ha` | €/ha |
| **Coût/kg** | `Σ(costs) / kg_production` | €/kg |
| **IFT** | Indice Fréquence Traitement | sans unité |
| **Rendement** | `kg_production / surface_ha` | kg/ha |
| **Marge brute** | `(prix_vente × kg) - costs` | € |

---

# 8. SCÉNARII UTILIZARE RECURENTĂ

## 8.1 SCENARII ZILNICE

| # | Scenariu | Frecvență |
|---|----------|-----------|
| 1 | Verificare meteo dimineață | Zilnic |
| 2 | Upload foto diagnostic | 2-3x/săptămână (sezon) |
| 3 | Consultare alerte maladii | Zilnic (sezon) |
| 4 | Verificare prognoză 5 zile | 2-3x/săptămână |

## 8.2 SCENARII SĂPTĂMÂNALE

| # | Scenariu | Frecvență |
|---|----------|-----------|
| 5 | Adăugare eveniment calendar | 3-5x/săptămână |
| 6 | Înregistrare tratament | 1x/săptămână (sezon) |
| 7 | Consultare registru tratamente | 1x/săptămână |
| 8 | Verificare stocuri | 1x/săptămână |

## 8.3 SCENARII LUNARE

| # | Scenariu | Frecvență |
|---|----------|-----------|
| 9 | Export PDF registru | 1x/lună |
| 10 | Verificare costuri acumulate | 1-2x/lună |
| 11 | Comparație NDVI parcele | 1x/lună |
| 12 | Consultare BSV-uri | 2x/lună |

## 8.4 SCENARII ANUALE

| # | Scenariu | Frecvență |
|---|----------|-----------|
| 13 | Creare parcele noi | 1x/an |
| 14 | Export registru complet campanie | 1x/an |
| 15 | Calcul cost/kg final | 1x/an (post-vendange) |
| 16 | Înregistrare producție/recoltă | 1x/an |

---

# 9. NICE-TO-HAVE vs BLOCKER

## 9.1 BLOCKERS (MVP)

| Feature | Motiv |
|---------|-------|
| Auth (register/login) | Fără auth = nu există utilizatori |
| Profil exploatație | Context obligatoriu pentru toate funcțiile |
| Parcele CRUD + hartă | Nucleu aplicație |
| Diagnostic AI | Valoare principală aplicație |
| Calendar evenimente | Traçabilitate obligatorie |
| Tratamente + e-Phy | Conformitate legală DRAAF |
| Export PDF DRAAF | Document oficial obligatoriu |
| Meteo curentă | Context pentru decizii |

## 9.2 NICE-TO-HAVE (Post-MVP)

| Feature | Prioritate | Motiv |
|---------|------------|-------|
| Telegram bot | P2 | Convenabil dar nu obligatoriu |
| NDVI satelit | P2 | Date indicative, nu critice |
| ZNT map | P2 | Util pentru conformitate |
| BSV integration | P2 | Context regional suplimentar |
| Stoc management | P2 | Poate fi ținut extern |
| Waste management | P3 | Utilizare rară |
| Statistici avansate | P3 | Nice-to-have |
| Admin impersonation | P3 | Doar pentru debug |
| AI calibration | P3 | Doar pentru optimizare |
| Multi-limbă | P3 | FR suficient inițial |

---

# 10. METRICI DE PROGRES V1→V3

## Formula Progres

```
PROGRES_TOTAL = (Features_Implement / Features_Total) × 100

Unde:
- Features_Total = 167 features (din secțiunea 1)
- Features_Implement = features migrate și funcționale în V3
```

## Breakdown pe Module

| Modul | Features | Pondere | Status V1 |
|-------|----------|---------|-----------|
| Auth & Onboarding | 7 | 4% | ✅ 100% |
| Profil Exploatație | 8 | 5% | ✅ 100% |
| Parcele | 12 | 7% | ✅ 100% |
| Diagnostic AI | 12 | 7% | ✅ 100% |
| Calendar & Evenimente | 12 | 7% | ✅ 100% |
| Tratamente Phyto | 11 | 7% | ✅ 100% |
| Stoc | 9 | 5% | ✅ 100% |
| Deșeuri | 5 | 3% | ✅ 100% |
| Meteo | 7 | 4% | ✅ 100% |
| NDVI | 5 | 3% | ✅ 100% |
| ZNT | 7 | 4% | ✅ 100% |
| BSV | 5 | 3% | ⚠️ 80% |
| Export PDF | 9 | 5% | ✅ 100% |
| Hărți | 7 | 4% | ✅ 100% |
| Statistici | 7 | 4% | ✅ 100% |
| Telegram | 6 | 4% | ⚠️ 80% |
| Admin | 9 | 5% | ✅ 100% |
| ARES | 4 | 2% | ✅ 100% |
| **TOTAL** | **167** | **100%** | **~97%** |

---

# 11. CHECKLIST MIGRARE V1→V3

## 11.1 FAZĂ 0: PREGĂTIRE
- [ ] Export complet date MongoDB V1
- [ ] Documentare schema V1 (acest document)
- [ ] Identificare diferențe schema V3
- [ ] Script migrare date (existent: `migrate_v1_to_v2.py`)

## 11.2 FAZĂ 1: NUCLEU (MVP)
- [ ] Auth module
- [ ] User/Exploitation module
- [ ] Parcels CRUD + map
- [ ] Diagnostic AI
- [ ] Calendar CRUD
- [ ] Treatments CRUD
- [ ] e-Phy search
- [ ] Export PDF DRAAF

## 11.3 FAZĂ 2: COMPLETARE
- [ ] Meteo integration
- [ ] Stock management
- [ ] ZNT module
- [ ] NDVI module
- [ ] BSV integration

## 11.4 FAZĂ 3: POLISH
- [ ] Telegram bot
- [ ] Waste management
- [ ] Statistics module
- [ ] Admin module
- [ ] ARES assistant

---

*Document generat: Decembrie 2024*
*VitiScan PRO V1 Complete Feature Map*
*Total: 167 features | 166+ API endpoints | 15+ colecții MongoDB*
