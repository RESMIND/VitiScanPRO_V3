# VitiScan PRO V3 - Hybrid Direction (V1 x V3)
Data: 2026-02-05

Acest document este referinta unica pentru: ce avem, ce lipseste, si directia rezultata din hibridizarea V1 (functional) cu V3 (strategie noua).

---

## 0) Premise si reguli de gating

- Launch rule: V3 poate fi lansat catre utilizatori doar cand reproduce functional V1 (fara Diagnostic AI).
- AI rule: Diagnostic AI si orice AI advice sunt blocate pana dupa minimum 24 luni de date complete (toate activitatile din exploatatie).
- Scope de lucru curent: 155 features V1 (167 total minus 12 de Diagnostic AI).

---

## 1) Directia hibrida (North Star)

Hibridul V1 x V3 inseamna:
- V1 ofera operational backbone (auth, parcele, calendar, tratamente, export DRAAF, meteo).
- V3 adauga platform core (tenancy/RBAC/cooperative, cost/kg core, preventie proactiva).
- AI este exclus la inceput; construim fundamentul de date si procesele reale.

Pe scurt: **"V1 parity + V3 platform core (cost/kg + coop + preventie), fara AI."**

---

## 2) Ce avem acum (din codul V3)

### Backend (existente functionale)
- Auth: /register, /login, /me (JWT 60 min)
- Establishments + Parcels CRUD
- Scans upload + list + download (fara diagnostic AI)
- Treatments create/list (basic)
- e-Phy search + match endpoints
- Export DRAAF PDF (parcela)
- AuthZ (RBAC/ABAC/ReBAC) + audit trail
- Beta onboarding endpoints
- Admin global stats + audit logs

### Frontend/UI (existente)
- Auth pages: /login, /register
- Parcels: list, new, detail, map, share, export
- Scans: list, new (upload)
- Admin: audit logs, global stats, beta requests
- e-Phy search page
- Settings/billing/team basic pages

---

## 3) Ce lipseste (pentru V1 parity, fara AI)

### Blocante MVP (din V1)
- Profil exploatatie complet (editari, setari, notificari)
- Calendar + evenimente complete (CRUD + export CSV/PDF)
- Tratamente complete (auto-fill AMM/ZNT/DAR, validari conformitate, export Excel)
- Meteo curenta + forecast + context pe parcela
- Export PDF DRAAF complet si verificat end-to-end
- Onboarding wizard (multi-step) + flows reale (nu doar pagina)

### Lipsuri majore (V1 non-blocker, dar necesare pentru parity completa)
- Stoc fitosanitar
- Deseuri (Adivalor)
- NDVI
- ZNT
- BSV
- Statistici
- Telegram bot
- Admin complet (impersonare, backup, management)

---

## 4) Directia modulara (Hibrid: Keep / Build / Defer)

Legenda:
- KEEP = folosim functionalitatea V1 ca etalon (paritate)
- BUILD = dezvoltam in V3 cu arhitectura noua
- DEFER = dupa parity si cost/kg core

| Modul | V1 Valoare | V3 Status | Directie Hibrida | Note |
|---|---|---|---|---|
| Auth & Onboarding | Critic | Partial | KEEP | lipsa phone/SMS, onboarding wizard |
| Profil exploatatie | Critic | Minimal | KEEP | doar create, lipsesc editari |
| Parcele + Harta | Nucleu | Partial | KEEP+BUILD | map IGN exista; edit contour lipsa |
| Calendar & Evenimente | Critic | Lipsa | KEEP | trebuie CRUD + export |
| Tratamente + e-Phy | Critic | Partial | KEEP+BUILD | e-Phy exista; tratamente incomplete |
| Export PDF DRAAF | Critic | Partial | KEEP | doar template de baza |
| Meteo | Critic | Lipsa | KEEP | fara meteo nu lansam |
| Stoc | Importanta | Lipsa | KEEP (post-parity) | nu blocheaza MVP |
| Deseuri | Nice | Lipsa | DEFER | post-parity |
| NDVI | Nice | Lipsa | DEFER | post-parity |
| ZNT | Nice | Lipsa | DEFER | post-parity |
| BSV | Nice | Lipsa | DEFER | post-parity |
| Statistici | Nice | Lipsa | DEFER | post-parity |
| Admin complet | Nice | Partial | DEFER | exista doar stats/audit |
| Cooperative portal | V3 core | Lipsa | BUILD | dupa parity |
| Cost/kg core | V3 core | Lipsa | BUILD | imediat dupa parity |
| Preventie proactiva | V3 core | Lipsa | BUILD | dupa cost/kg + date |
| Diagnostic AI | V1 | Excluded | DEFER (gated) | dupa 24 luni date complete |

---

## 5) Criteriu de "gata de lansare" (V1 parity fara AI)

V3 este "launch-ready" cand:
- Toate blockerele V1 sunt functionale end-to-end (fara AI).
- Fluxuri E2E din V1 ruleaza in V3:
  1) Onboarding -> exploatatie -> parcela -> calendar
  2) Parcela -> tratament -> registru DRAAF PDF
  3) Meteo curenta pe parcela

---

## 6) Ce urmeaza (ordine recomandata)

1) Stabilizare V3: refresh token, rate limiting, test suite, rute lipsa, aliniere AuthZ
2) V1 parity blocante: profil, calendar, tratamente complete, export DRAAF, meteo
3) Cost/kg core (ledger + import + KPI)
4) Cooperative core (RBAC + agregare + benchmark)
5) Preventie proactiva (BSV + meteo + NDVI)
6) AI gated (doar dupa 24 luni date complete)

---

## 7) Status de progres (baseline)

Vezi baseline detaliat in:
- backend/exports/V1_V3_PROGRESS_BASELINE_2026-02-05.md

