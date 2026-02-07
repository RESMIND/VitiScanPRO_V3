# V1 -> V3 Master Checklist (Hybrid)
Data: 2026-02-05

Scope (active, counted):
- V1 features active: 126 (Diagnostic AI + ARES excluded)
- V3 core tasks active: 19
- Active total: 145

Gated (not counted):
- V1 gated features: 16 (Diagnostic AI + ARES)
- V3 gated tasks: 2 (AI gated)
- Gated total: 18

Total tasks overall: 163

Progress (active scope only):
- Done: 29
- Remaining: 116
- Progress: 20.0%

Regula: bifam manual cand este gata; procentul se recalculeaza dupa bifari.
Note: Diagnostic AI si ARES sunt gated pana dupa minimum 24 luni de date complete.
Note: Checklist-ul V1 listeaza 142 features in tabele, desi rezumatul vechi mentioneaza 167. Lucram cu cele 142 pana la reconciliere.

## AUTENTIFICARE & ONBOARDING (7 tasks)
- [ ] 1.1.1 Înregistrare cu telefon (FR format) (P0, Blocker)
- [ ] 1.1.2 Login cu telefon + parolă (P0, Blocker)
- [x] 1.1.3 Verificare 2FA via Twilio SMS (P1) ✅ IMPLEMENTAT: SMS verification cu rate limiting, Twilio integration
- [ ] 1.1.4 Resetare parolă via SMS (P1)
- [ ] 1.1.5 Onboarding wizard (4 pași) (P0, Blocker)
- [ ] 1.1.6 Validare session în localStorage (P0, Blocker)
- [x] 1.1.7 Logout cu ștergere session (P0, Blocker) ? client-side token clear

## PROFIL EXPLOATAȚIE (8 tasks)
- [x] 1.2.1 Creare profil exploatație (P0, Blocker) ? mapped to establishments create
- [ ] 1.2.2 Editare: nume, adresă, SIRET (P0, Blocker)
- [ ] 1.2.3 Editare: suprafață totală, nr. parcele (P0, Blocker)
- [ ] 1.2.4 Editare: tip cultură (BIO/Conv/HVE) (P1)
- [ ] 1.2.5 Upload logo exploatație (P2)
- [ ] 1.2.6 Setări notificări (email/SMS/Telegram) (P2)
- [ ] 1.2.7 Linkare cont Telegram (P1)
- [ ] 1.2.8 Informații certiphyto (P1)

## PARCELE (12 tasks)
- [x] 1.3.1 Creare parcelă (nume, suprafață, soi) (P0, Blocker)
- [x] 1.3.2 Desenare contur pe hartă (polygon) (P0, Blocker)
- [ ] 1.3.3 Editare contur (drag & drop vertices) (P1)
- [x] 1.3.4 Calcul automat suprafață din polygon (P0, Blocker)
- [x] 1.3.5 Atribuire soi (variety) (P0, Blocker) ? implemented as crop_type
- [x] 1.3.6 Atribuire an plantare (P1) ? planting_year field present
- [ ] 1.3.7 Atribuire densitate plantare (P2)
- [x] 1.3.8 Ștergere parcelă (P0, Blocker)
- [ ] 1.3.9 Bulk save parcele (P1)
- [x] 1.3.10 Vizualizare pe hartă IGN (P0, Blocker)
- [ ] 1.3.11 Colorare pe soiuri (P2)
- [ ] 1.3.12 Mod planificare vizuală (3 culori) (P2)
- [x] 1.3.13 Căutare cadastrală (comună + secțiune + număr) (P0, Blocker) ✅ IMPLEMENTAT: UnifiedMapModal cu căutare cadastrală integrată
- [x] 1.3.14 Schimbare automată la strat satelit pentru desenare (P0, Blocker) ✅ IMPLEMENTAT: useEffect care schimbă la ign_ortho când currentStep='draw'
- [x] 1.3.15 Modal extins cu analize sol și note (P1) ✅ IMPLEMENTAT: câmpuri soil_analysis și notes în modal
- [x] 1.3.16 Flux creare 3 pași (căutare → desenare → detalii) (P0, Blocker) ✅ IMPLEMENTAT: currentStep state management și UI corespunzătoare

## DIAGNOSTIC AI (GATED - not counted) (12 tasks)
- [ ] 1.4.1 Upload foto frunză (P0, Blocker, GATED)
- [ ] 1.4.2 Diagnostic AI via GPT-4o Vision (P0, Blocker, GATED)
- [ ] 1.4.3 Afișare maladie detectată (P0, Blocker, GATED)
- [ ] 1.4.4 Afișare nivel de încredere (%) (P0, Blocker, GATED)
- [ ] 1.4.5 Afișare severitate (low/medium/high) (P0, Blocker, GATED)
- [ ] 1.4.6 Recomandări tratament (P0, Blocker, GATED)
- [ ] 1.4.7 Feedback utilizator (👍/👎) (P1, GATED)
- [ ] 1.4.8 Chat conversațional post-diagnostic (P1, GATED)
- [ ] 1.4.9 Creare eveniment calendar din diagnostic (P1, GATED)
- [ ] 1.4.10 Istoric diagnostice per utilizator (P1, GATED)
- [ ] 1.4.11 Istoric diagnostice per parcelă (P1, GATED)
- [ ] 1.4.12 Integrare BSV în răspuns AI (P2, GATED)

## CALENDAR & EVENIMENTE (12 tasks)
- [ ] 1.5.1 Vizualizare calendar lunar (P0, Blocker)
- [ ] 1.5.2 Creare eveniment manual (P0, Blocker)
- [ ] 1.5.3 Editare eveniment (P0, Blocker)
- [ ] 1.5.4 Ștergere eveniment (P0, Blocker)
- [ ] 1.5.5 Tipuri eveniment (10+) (P0, Blocker)
- [ ] 1.5.6 Filtrare pe parcelă (P1)
- [ ] 1.5.7 Filtrare pe tip eveniment (P1)
- [ ] 1.5.8 Export CSV evenimente (P1)
- [ ] 1.5.9 Export PDF evenimente (P1)
- [ ] 1.5.10 Evenimente auto din AI (recomandări) (P2)
- [ ] 1.5.11 Calcul cost per eveniment (P1)
- [ ] 1.5.12 Vizualizare ferestre optime tratament (P2)

## TRATAMENTE FITOSANITARE (11 tasks)
- [x] 1.6.1 Creare tratament (P0, Blocker)
- [x] 1.6.2 Căutare produs în e-Phy (ANSES) (P0, Blocker) ? e-Phy endpoints + UI page
- [x] 1.6.3 Completare automată AMM, ZNT, DAR (P0, Blocker)
- [x] 1.6.4 Înregistrare doză, suprafață (P0, Blocker)
- [x] 1.6.5 Calcul cantitate utilizată (P0, Blocker)
- [ ] 1.6.6 Validare conformitate ZNT (P1)
- [ ] 1.6.7 Înregistrare applicateur + certiphyto (P1)
- [ ] 1.6.8 Înregistrare lot produs (P2)
- [ ] 1.6.9 Decrementare automată stoc (P2)
- [ ] 1.6.10 Export registru DRAAF PDF (P0, Blocker)
- [ ] 1.6.11 Export registru Excel (P1)

## STOC FITOSANITAR (9 tasks)
- [ ] 1.7.1 Creare lot (achiziție) (P1)
- [ ] 1.7.2 Editare lot (P1)
- [ ] 1.7.3 Ștergere lot (P1)
- [ ] 1.7.4 Înregistrare mișcări (intrare/ieșire) (P1)
- [ ] 1.7.5 Istoric mișcări per lot (P2)
- [ ] 1.7.6 Alertă stoc scăzut (P2)
- [ ] 1.7.7 Alertă expirare (P2)
- [ ] 1.7.8 Dashboard stoc (P1)
- [ ] 1.7.9 Export stoc CSV/XLSX (P2)

## DEȘEURI (WASTE/ADIVALOR) (5 tasks)
- [ ] 1.8.1 Înregistrare eveniment deșeu (P2)
- [ ] 1.8.2 Tipuri deșeuri (EVPP, PPNU, etc.) (P2)
- [ ] 1.8.3 Metode eliminare (Adivalor, etc.) (P2)
- [ ] 1.8.4 Dashboard deșeuri (P2)
- [ ] 1.8.5 Export deșeuri (P3)

## METEO (7 tasks)
- [ ] 1.9.1 Meteo curentă per parcelă (P0, Blocker)
- [ ] 1.9.2 Prognoză 5 zile (P1)
- [ ] 1.9.3 Istoric meteo (P2)
- [ ] 1.9.4 Alerte meteo critice (P1)
- [ ] 1.9.5 Widget meteo în dashboard (P1)
- [ ] 1.9.6 Overlay meteo pe hartă (P2)
- [ ] 1.9.7 Ferestre optime tratament (P2)

## NDVI & SATELIT (5 tasks)
- [ ] 1.10.1 Calcul NDVI per parcelă (P1)
- [ ] 1.10.2 Istoric NDVI (12 luni) (P2)
- [ ] 1.10.3 Colorare parcele pe NDVI (P2)
- [ ] 1.10.4 Alerte NDVI scăzut (P2)
- [ ] 1.10.5 Widget NDVI în detalii parcelă (P2)

## ZNT (ZONE NON TRAITÉES) (7 tasks)
- [ ] 1.11.1 Afișare cursuri apă BCAE PAC (P1)
- [ ] 1.11.2 Afișare BD TOPO (indicativ) (P2)
- [ ] 1.11.3 Afișare clădiri/locuințe (P2)
- [ ] 1.11.4 Calcul buffer zones (P1)
- [ ] 1.11.5 Verificare conformitate (P1)
- [ ] 1.11.6 Adăugare puncte personalizate (P2)
- [ ] 1.11.7 Override ZNT manual (P2)

## BSV (BULETINE SANITARE) (5 tasks)
- [ ] 1.12.1 Afișare BSV-uri PACA (2021-2025) (P2)
- [ ] 1.12.2 Extragere alertes din PDF (P2)
- [ ] 1.12.3 Timeline BSV-uri (P2)
- [ ] 1.12.4 Query BSV via ARES (P2)
- [ ] 1.12.5 Crawler automat BSV noi (P3)

## EXPORT PDF (9 tasks)
- [x] 1.13.1 Template DRAAF (registru oficial) (P0, Blocker) ? basic DRAAF PDF export (parcel)
- [ ] 1.13.2 Template Économique (costuri) (P1)
- [ ] 1.13.3 Template Certification (HVE/AB) (P2)
- [ ] 1.13.4 Template Main d'Œuvre (P2)
- [ ] 1.13.5 Filtrare pe perioadă/campanie (P1)
- [ ] 1.13.6 Filtrare pe parcele (P1)
- [ ] 1.13.7 Includere GPS (P1)
- [ ] 1.13.8 Includere meteo (P2)
- [ ] 1.13.9 Export Excel (XLSX) (P1)

## HĂRȚI (7 tasks)
- [x] 1.14.1 Hartă IGN (OSM, Satellite, Plan, Cadastre) (P0, Blocker) ? IGN/OSM base layers
- [ ] 1.14.2 Hartă ZNT (P1)
- [ ] 1.14.3 Hartă Meteo/NDVI (P2)
- [ ] 1.14.4 Colorare parcele pe soiuri (P2)
- [ ] 1.14.5 Mod planificare vizuală (P2)
- [ ] 1.14.6 Legendă editabilă (P2)
- [ ] 1.14.7 Fullscreen mode (P2)

## STATISTICI (7 tasks)
- [ ] 1.15.1 Stats diagnostice per user (P2)
- [ ] 1.15.2 Distribuție maladii (Pie Chart) (P2)
- [ ] 1.15.3 Distribuție severități (Bar Chart) (P2)
- [ ] 1.15.4 Timeline (Line Chart) (P2)
- [ ] 1.15.5 Stats per parcelă (P2)
- [ ] 1.15.6 Precizie AI (feedback) (P2)
- [ ] 1.15.7 Admin: stats globale platformă (P2)

## TELEGRAM BOT (6 tasks)
- [x] 1.16.1 Linkare cont via telefon (P2) ✅ IMPLEMENTAT: Telegram bot configurat și testat (@VitiScanPRO_bot)
- [ ] 1.16.2 Comenzi: /start, /help, /parcels (P2)
- [ ] 1.16.3 Comenzi: /alerts, /weather (P2)
- [ ] 1.16.4 Notificări alerte maladii (P2)
- [ ] 1.16.5 Notificări backup (admin) (P2)
- [ ] 1.16.6 Confirmare backup via bot (P2)

## ADMIN (9 tasks)
- [ ] 1.17.1 Lista utilizatori (P1)
- [ ] 1.17.2 Detalii utilizator (P1)
- [ ] 1.17.3 Impersonare utilizator (P2)
- [ ] 1.17.4 RBAC (roles/permissions) (P2)
- [ ] 1.17.5 Toate parcelele pe hartă (P2)
- [ ] 1.17.6 Feedbacks utilizatori (P2)
- [ ] 1.17.7 AI Calibration (P2)
- [ ] 1.17.8 Backup management (P1)
- [ ] 1.17.9 Logs activitate (P2)

## ARES (ASISTENT AI) (GATED - not counted) (4 tasks)
- [ ] 1.18.1 Chat conversațional (P2, GATED)
- [ ] 1.18.2 Interogare BSV-uri (P2, GATED)
- [ ] 1.18.3 Recomandări personalizate (P2, GATED)
- [ ] 1.18.4 Acces context exploatație (P2, GATED)

# V3 Core Tasks (post-parity)
## Stabilizare V3 (Faza 0) (5 tasks)
- [x] Implement /auth/refresh
- [x] Rate limiting: Redis config + fallback
- [x] Fix tests/test_scans.py + aliniere endpoint-uri
- [x] Include rute lipsa (invitations, trash) in main.py
- [x] Aliniere AuthZ decoratori la modele reale (user_id/tenant_id/resource_id)

## Cost/kg Core (V3) (4 tasks)
- [x] Model cost ledger (DB schema)
- [x] Import CSV/Excel costuri
- [x] Calcul cost/kg per ha + agregare per soi/parcela/exploatatie
- [x] Export PDF/CSV cost/kg

## Cooperative Core (V3) (3 tasks)
- [ ] Portal coop (UI agregat)
- [ ] RBAC dedicat pentru cooperative
- [ ] Benchmark anonim + dashboard

## Preventie Proactiva (V3) (4 tasks)
- [ ] BSV ingest (S3) + storage
- [ ] Meteo integration (curent + forecast)
- [ ] NDVI integration (curent + istoric)
- [ ] Alertare programata + feedback loop

## AI Gated (dupa 24 luni date complete) (GATED - not counted) (2 tasks)
- [ ] Re-activare diagnostic AI (gated)
- [ ] AI advice + KPI reduction cost/kg

---

## 📋 REZUMAT ACTIVITATE 2026-02-05

### ✅ COMPLETAT ASTĂZI:
1. **Verificare 2FA via Twilio SMS** (1.1.3) ✅
   - Implementat sistem complet de verificare SMS pentru onboarding
   - Rate limiting și validare numere românești/franceze
   - Integrare Twilio cu fallback-uri de securitate

2. **Linkare cont Telegram** (1.16.1) ✅  
   - Configurat și testat bot-ul Telegram (@VitiScanPRO_bot)
   - Verificat conexiunea și disponibilitatea API
   - Pregătit pentru notificări și comenzi viitoare

3. **Sistem creare parcele avansat** (1.3.13, 1.3.14, 1.3.15, 1.3.16) ✅
   - Implementat flux complet 3 pași: căutare cadastrală → desenare → detalii
   - Integrat UnifiedMapModal cu controale desenare pentru polygon
   - Adăugat căutare cadastrală (comună + secțiune + număr)
   - Schimbare automată la strat satelit pentru desenare precisă
   - Modal extins cu câmpuri pentru analize sol și note suplimentare
   - Calcul automat suprafață și perimetru la închiderea poligonului

### 🔄 ACTIVITĂȚI SUPLIMENTARE:
- **Business Intelligence pentru Admin**: Implementat sistem de analiză automată a cererilor beta cu informații despre firme, premii, competiții
- **Traduceri Interfață**: Tradus interfața admin la franceză pentru piața franceză, apoi revenit la română pentru precizie în comunicare
- **Testare Sistem**: Verificat funcționalitatea completă a autentificării, onboarding-ului și notificărilor

### 📊 PROGRES ACTUALIZAT:
- **Task-uri completate azi**: 5 (2 + 3 noi)
- **Total task-uri finalizate**: 29/145 (20.0%)
- **Task-uri rămase**: 116

### 🎯 URMĂTOARELE PRIORITĂȚI:
1. **Onboarding wizard** - Finalizare flux complet înregistrare utilizator (4 pași)
2. **Validare sesiuni** - Implementare localStorage și refresh tokens  
3. **Admin dashboard** - Extindere funcționalități management utilizatori
4. **Midpoint vertices** - Implementare puncte intermediare personalizabile în polygon

---
