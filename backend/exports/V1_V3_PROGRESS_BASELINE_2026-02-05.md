# V1 -> V3 Progress Baseline (2026-02-05)

Scope: 155 V1 features (see V1_V3_MIGRATION_CHECKLIST.md), excluding Diagnostic AI (12 features) until AI is allowed after minimum 24 months of complete data.
Method: strict V1 parity. Implemented=1, Partial=0.5, Missing=0.
Note: Any module that appears 100% will not be re-verified until final pass.

## Overall baseline
- Backend: 15.0 / 155 = 9.7%
- Frontend: 16.5 / 155 = 10.6%
- UI: 16.5 / 155 = 10.6% (UI measured as presence of usable screens for V1 features)

## Module breakdown (counts)
| Module | Total | Backend | Frontend | UI | Notes |
|---|---:|---:|---:|---:|---|
| Auth & Onboarding | 7 | 1.5 | 3.0 | 3.0 | Register/login exist but not phone/SMS; password reset is email; onboarding wizard missing |
| Profil Exploatatie | 8 | 1.0 | 1.0 | 1.0 | Create only; edit/settings missing |
| Parcele | 12 | 5.5 | 6.5 | 6.5 | Polygon draw + delete present; edit contour disabled; variety is crop_type (partial) |
| Diagnostic AI | 12 | 0 | 0 | 0 | Excluded from baseline (AI gated until minimum 24 months of complete data) |
| Calendar & Evenimente | 12 | 0 | 0 | 0 | Missing |
| Tratamente Phyto | 11 | 4.0 | 2.0 | 2.0 | Basic treatment create + e-Phy search + DRAAF PDF; missing AMM/ZNT/DAR auto-fill, stock, validations |
| Stoc | 9 | 0 | 0 | 0 | Missing |
| Deseuri | 5 | 0 | 0 | 0 | Missing |
| Meteo | 7 | 0 | 0 | 0 | Missing |
| NDVI | 5 | 0 | 0 | 0 | Missing |
| ZNT | 7 | 0 | 0 | 0 | Missing |
| BSV | 5 | 0 | 0 | 0 | Missing |
| Export PDF | 9 | 1.0 | 1.0 | 1.0 | Only DRAAF template |
| Harti | 7 | 0 | 1.0 | 1.0 | IGN/OSM base layers only |
| Statistici | 7 | 0 | 0 | 0 | Missing |
| Telegram | 6 | 0 | 0 | 0 | Missing |
| Admin | 9 | 2.0 | 2.0 | 2.0 | Audit logs + basic global stats; no impersonation/backup/etc |
| ARES | 4 | 0 | 0 | 0 | Missing |

## Next step
- Build per-feature evidence list and update counts (backend/frontend/UI) as we implement.
- Track blockers MVP separately (Auth, Profil, Parcele, Calendar, Tratamente+e-Phy, Export PDF DRAAF, Meteo).
