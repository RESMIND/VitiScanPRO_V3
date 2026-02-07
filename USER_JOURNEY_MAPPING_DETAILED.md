# VitiScan PRO - User Journey Mapping Detaliat

## 🎯 CALĂTORIA UTILIZATORULUI PRIN PLATFORMĂ

### Documentație Completă a Fluxurilor de Utilizare

---

## 1. 🎬 ETAPA 1: ÎNREGISTRARE ȘI ONBOARDING

### 1.1 Primul Contact cu Platforma

**Scenariu:** Utilizator nou descoperă VitiScan PRO prin:
- Recomandare de la colegi viticultori
- Căutare Google pentru "software gestiune vie"
- Participare la târg agricol
- Newsletter specializat

**Primul Impresion:**
```
🌟 Landing Page VitiScan PRO
├── Hero Section: "Management Viticol Inteligente"
├── Demo Video: 30 sec prezentare funcționalități
├── Testimoniale: "Am economisit 200€/ha cu VitiScan"
├── CTA: "Începe Demo Gratuită" sau "Înregistrează-te"
└── Features Grid: 8 funcționalități cheie
```

### 1.2 Procesul de Înregistrare

**Pas 1: Formular Înregistrare**
```
📝 Form Fields:
├── Email (validare format + verificare disponibilitate)
├── Parolă (minim 8 caractere + complexitate)
├── Confirmare Parolă
├── Nume Exploatație
├── Tip Exploatație (Individual/Familial/Cooperativă)
├── Suprafață Totală (ha)
└── Departament (dropdown cu toate departamentele franceze)
```

**Pas 2: Verificare Email**
```
📧 Email Verification Flow:
├── Trimitere email cu link de verificare
├── Link expira în 24h
├── Re-trimitere automată după 5 min dacă nu s-a confirmat
└── Redirecționare către dashboard după confirmare
```

**Pas 3: Setup Inițial**
```
🚀 Welcome Wizard (3 pași):
├── Pas 1: "Spune-ne despre tine"
│   ├── Rol: Proprietar/Manager/Consultant
│   ├── Experiență: Începător/Intermediar/Expert
│   └── Obiective: Productivitate/Costuri/Conformitate
├── Pas 2: "Configurează exploatația"
│   ├── Încarcă parcele (GeoJSON/KML/Shapefile)
│   ├── Definește soiuri principale
│   └── Setează alertă meteo
└── Pas 3: "Tutorial rapid"
    ├── 5 minute video ghidat
    └── Checklist onboarding completat
```

### 1.3 Primul Login

**Post-Înregistrare Experience:**
```
🔐 First Login:
├── Email confirmat → Redirect către login
├── Autofill email din URL parameter
├── Login reușit → Welcome modal cu tutorial
└── Dashboard gol cu CTA pentru import parcele
```

---

## 2. 🏡 ETAPA 2: CONFIGURARE EXPLOATAȚIE

### 2.1 Import Parcele

**Metode de Import:**
```
📤 Import Options:
├── Upload Fișiere
│   ├── GeoJSON (recomandat)
│   ├── KML (Google Earth)
│   ├── Shapefile (QGIS/ArcGIS)
│   └── CSV cu coordonate
├── Integrare API
│   ├── IGN Cadastre (Franța)
│   └── RP (Registre Parcellaire)
└── Desenare Manuală
    ├── Click pe hartă pentru vârfuri
    ├── Calcul automat suprafață
    └── Validare geometrie
```

**Proces Import Detaliat:**
```
1️⃣ Selectare Metodă Import
2️⃣ Upload/Conectare Sursă
3️⃣ Mapare Câmpuri (nume, suprafață, soi, an plantare)
4️⃣ Preview pe Hartă
5️⃣ Validare și Corecții
6️⃣ Salvare în Bază de Date
7️⃣ Generare Raport Import
```

### 2.2 Configurare Soiuri și Setări

**Personalizare Culori Soiuri:**
```
🎨 Variety Settings:
├── Paletă Culori Predefinită (PACA standard)
│   ├── Grenache: #DC2626 (roșu)
│   ├── Syrah: #7C3AED (violet)
│   ├── Mourvèdre: #2563EB (albastru)
│   └── Chardonnay: #16A34A (verde)
├── Culori Personalizate
│   ├── Color Picker pentru fiecare soi
│   ├── Preview în timp real pe hartă
│   └── Salvare automată în cloud
└── Adăugare Soiuri Noi
    ├── Căutare în baza de date europeană
    └── Validare ortografică
```

**Setări Exploatație:**
```
⚙️ Farm Settings:
├── Unități de Măsura (ha/m², kg/hl, €)
├── Monedă (EUR, USD, GBP)
├── Limbă (FR, EN, ES, IT)
├── Fus Orar (automat din locație)
└── Preferințe Notificări
    ├── Email pentru alerte
    ├── Push notifications
    └── SMS pentru urgențe
```

### 2.3 Configurare ZNT (Zone Non Traitées)

**Setup Conformitate:**
```
🛡️ ZNT Configuration:
├── ZNT Eau: 20m (default PAC BCAE)
├── ZNT Riverains: 10m (default)
├── Surse Date Active
│   ├── BCAE PAC (oficial - prioritate 1)
│   ├── BD TOPO IGN (indicativ)
│   └── Puncte Personalizate
└── Validare Automată
    ├── Verificare conformitate toate parcele
    └── Raport PDF pentru autorități
```

---

## 3. 📊 ETAPA 3: UTILIZARE ZILNICĂ - DASHBOARD

### 3.1 Dashboard Principal

**Layout Dashboard:**
```
📈 Main Dashboard Layout:
├── Header: Logo + User Menu + Notifications
├── KPIs Row (4 carduri)
│   ├── Suprafață Totală
│   ├── Productivitate Medie
│   ├── Costuri/ha Medii
│   └── Alertă Meteo
├── Harta Mini (30% din ecran)
│   ├── Toate parcelele cu status
│   ├── Click → Hartă Completă
│   └── Overlay meteo activ
├── Widget-uri Dreapta (70% din ecran)
│   ├── Calendar Lucrări
│   ├── Tratament Urgente
│   ├── NDVI Monitor
│   └── Costuri Lunare
└── Navigare Rapidă Bottom
    ├── Calendar, Tratament, Costuri, Hartă
```

**KPIs Dinamice:**
```
📊 KPI Cards:
├── Suprafață: "45.2 ha" + trend ↑2.1%
├── Productivitate: "52 hl/ha" + trend ↑5.3%
├── Costuri: "€850/ha" + trend ↓3.2%
└── Meteo: "🌧️ 15mm prevăzut" + alertă
```

### 3.2 Navigare și Meniu

**Structură Meniu:**
```
🧭 Navigation Structure:
├── Dashboard (acasă)
├── 📅 Calendar & Planning
│   ├── Calendar Lunar
│   ├── Planificare Lucrări
│   └── Istoric Lucrări
├── 🌱 Tratament & Fitoprotecție
│   ├── Tratament Nou
│   ├── Istoric Tratament
│   └── Stoc Produse
├── 💰 Costuri & Buget
│   ├── Înregistrare Costuri
│   ├── Analiză Costuri
│   └── Export Rapoarte
├── 🗺️ Hărți & Monitorizare
│   ├── Hartă Unificată
│   ├── NDVI Satellite
│   └── ZNT Conformitate
├── 📊 Analize & Rapoarte
│   ├── Productivitate
│   ├── Rentabilitate
│   └── Conformitate
└── ⚙️ Setări & Profil
    ├── Profil Utilizator
    ├── Setări Exploatație
    └── Integrări API
```

---

## 4. 📅 ETAPA 4: PLANIFICARE ȘI CALENDAR

### 4.1 Calendar Lunar

**Interfață Calendar:**
```
📅 Monthly Calendar View:
├── Navigare: Săptămână/Lună/An
├── Filtre: Tip Lucrare, Parcelă, Status
├── Evenimente Colorate
│   ├── 🔵 Taille (albastru)
│   ├── 🟡 Fertilizare (galben)
│   ├── 🟢 Tratament (verde)
│   └── 🔴 Recoltă (roșu)
└── Quick Actions
    ├── + Adaugă Eveniment
    ├── 📋 Template-uri
    └── 📊 Statistici Lună
```

**Adăugare Eveniment:**
```
➕ Add Event Flow:
├── Selectare Dată + Parcelă
├── Tip Eveniment (dropdown)
├── Detalii: Produs, Doză, Cost Estimat
├── Notificări: Email/SMS înainte
└── Recurență: Zilnic/Săptămânal/Lunar
```

### 4.2 Mod Planificare Vizuală

**Pe Hartă Unificată:**
```
🎨 Planning Mode on Map:
├── 3 Culori Status
│   ├── 🟢 Taille Terminată
│   ├── 🟡 În Curs (azi)
│   └── 🔴 Neîncepută
├── Statistici Timp Real
│   ├── Hectare per Status
│   └── Progres General
└── Export Stare Curentă
```

### 4.3 Template-uri și Automatizare

**Template-uri Lucrări:**
```
📋 Work Templates:
├── "Taille Hiver" (Dec-Mar)
│   ├── Sarcini: Taille, Curățare, Fertilizare
│   ├── Materiale Necesare
│   └── Cost Estimat
├── "Tratament Mildiu" (Apr-Jun)
│   ├── Produse Recomandate
│   ├── Calendar Aplicare
│   └── ZNT Verificare
└── "Recoltă" (Aug-Oct)
    ├── Planificare Echipă
    ├── Logistică Transport
    └── Documente Calitate
```

---

## 5. 🌱 ETAPA 5: GESTIONARE TRATAMENTE

### 5.1 Înregistrare Tratament Nou

**Formular Tratament Detaliat:**
```
💉 Treatment Form:
├── Parcelă Selectată (din hartă)
├── Produs (căutare e-Phy)
│   ├── Auto-complete din baza de date
│   ├── AMM, ZNT, DAR auto-populate
│   └── Stoc verificare
├── Doză și Concentrație
│   ├── Calcul cantitate totală
│   ├── Suprafață tratată
│   └── Unități corecte
├── Condiții Aplicare
│   ├── Meteo compatibil
│   ├── ZNT respectat
│   └── Perioadă vegetativă
└── Documentare
    ├── Fotografii înainte/după
    ├── Certificat aplicare
    └── Notă pentru conformitate
```

**Integrare e-Phy:**
```
🔗 e-Phy Integration:
├── Căutare Produs: "copper" → 15 rezultate
├── Selectare → Auto-fill
│   ├── AMM: "Cupric Sulfate"
│   ├── ZNT Eau: 20m
│   ├── DAR: 30 zile
│   └── Doză Recomandată: 2kg/ha
└── Validare Conformitate
    ├── Verificare ZNT automat
    └── Alertă dacă incompatibil
```

### 5.2 Monitorizare Tratament

**Dashboard Tratament:**
```
📈 Treatment Dashboard:
├── Tratament Active (ultimele 30 zile)
├── Următoare Programate
├── Alertă Re-tratament
└── Istoric pe Parcelă
```

**Notificări Inteligente:**
```
🔔 Smart Notifications:
├── "Tratament Mildiu expira în 3 zile"
├── "Condiții meteo ideale pentru aplicare"
├── "Stoc produs scăzut - reînnoiește"
└── "ZNT încălcat - ajustează distanță"
```

### 5.3 Rapoarte Conformitate

**Generare Raport PAC:**
```
📄 PAC Compliance Report:
├── Perioada: 01/01/2024 - 31/12/2024
├── Tratament Listate cu:
│   ├── Dată aplicare
│   ├── Produs + Doză
│   ├── Suprafață tratată
│   └── ZNT respectat (✅/❌)
├── Semnătură Digitală
└── Export PDF/XML pentru autorități
```

---

## 6. 💰 ETAPA 6: GESTIONARE COSTURI

### 6.1 Înregistrare Costuri

**Categorii Costuri:**
```
💸 Cost Categories:
├── Input-uri
│   ├── Semințe & Butași
│   ├── Îngrășăminte
│   └── Pesticide & Fungicide
├── Lucrări
│   ├── Taille Manuală
│   ├── Mașini Agricole
│   └── Întreținere Echipamente
├── Logistică
│   ├── Transport
│   ├── Depozitare
│   └── Ambalare
└── Administrativ
    ├── Asigurări
    ├── Consultanță
    └── Taxe & Impozite
```

**Formular Cost Detaliat:**
```
📝 Cost Entry Form:
├── Dată + Categorie
├── Parcelă Asociată (opțional)
├── Furnizor + Factură
├── Cantitate + Unitate + Preț
├── TVA Automat (20%)
└── Atașament Factură (PDF/foto)
```

### 6.2 Analiză Costuri

**Dashboard Costuri:**
```
📊 Cost Analysis Dashboard:
├── Costuri Lunare (grafic bar)
├── Costuri pe Categorie (pie chart)
├── Costuri/ha pe Parcelă
├── Trend Anual
└── Buget vs Real vs Prognoză
```

**Filtre Avansate:**
```
🔍 Advanced Filters:
├── Perioadă: Săptămână/Lună/Trimestru/An
├── Categorie: Toate/Input-uri/Lucrări
├── Parcelă: Toate/Specifică
├── Furnizor: Top 5 / Specific
└── Export: Excel/PDF/CSV
```

### 6.3 Bugetare și Prognoză

**Planificare Bugetară:**
```
💰 Budget Planning:
├── Buget Anual pe Categorii
├── Prognoză Bazată pe Istoric
├── Alerte când se depășește 80%
└── Comparare cu Anul Precedent
```

---

## 7. 🗺️ ETAPA 7: UTILIZARE HARTĂ UNIFICATĂ

### 7.1 Accesare Hartă

**Modal Hartă Unificată:**
```
🗺️ Unified Map Access:
├── Din Dashboard: Click "Carte Unifiée"
├── Din Calendar: "Vizualizează pe Hartă"
├── Din Tratament: "Vezi Parcelă"
└── Din Costuri: "Hartă Costuri/ha"
```

### 7.2 Moduri de Funcționare

**Mod Standard:**
```
🌐 Standard Mode:
├── Strat OSM/IGN selectabil
├── Parcele albastre cu popup info
├── Zoom automat pe toate parcelele
└── Search parcelă după nume
```

**Mod Planificare:**
```
📅 Planning Mode:
├── Toggle 🎨 pentru activare
├── 3 culori status pe parcele
├── Statistici în panel lateral
└── Click parcelă → schimbare status
```

**Mod ZNT:**
```
🛡️ ZNT Mode:
├── Toggle 🛡️ pentru activare
├── Straturi BCAE + BD TOPO
├── Zone tampon evidențiate
├── Status conformitate per parcelă
└── Adăugare puncte personalizate
```

**Mod NDVI:**
```
👁️ NDVI Mode:
├── Toggle 👁️ pentru activare
├── Overlay NDVI colorat
├── Etichete procent pe parcele
├── Legendă scală sănătate
└── Filtru valori critice
```

**Mod Meteo:**
```
🌡️ Weather Mode:
├── Toggle 🌡️🌧️☁️💨 pentru overlay-uri
├── Temperatură, precipitații, nori, vânt
├── Actualizare în timp real
└── Prognoză 5 zile integrată
```

### 7.3 Funcții Avansate

**Fullscreen și Export:**
```
⛶ Fullscreen Mode:
├── Apăsare ESC pentru ieșire
├── Toate controale disponibile
└── Export imagine hartă
```

**Multi-Select și Comparare:**
```
🔍 Advanced Selection:
├── Ctrl+Click pentru selecție multiplă
├── Comparare KPIs între parcele
├── Export date comparate
└── Filtrare vizuală
```

---

## 8. 📊 ETAPA 8: ANALIZE ȘI RAPOARTE

### 8.1 Dashboard Analize

**Metrice Principale:**
```
📈 Key Metrics Dashboard:
├── Productivitate Istorică
│   ├── Grafic hl/ha pe ani
│   ├── Comparare soiuri
│   └── Trend vreme
├── Rentabilitate
│   ├── Venituri vs Costuri
│   ├── Profit/ha
│   └── Break-even analysis
└── Sănătate Viței
    ├── NDVI mediu
    ├── Tratament eficacitate
    └── Risc boli
```

### 8.2 Rapoarte Personalizate

**Tipuri Rapoarte:**
```
📄 Report Types:
├── Raport Lunar Operațiuni
├── Raport Anual Productivitate
├── Raport Conformitate PAC
├── Raport Cost-Beneficiu
└── Raport Sustenabilitate
```

**Programare Rapoarte:**
```
⏰ Scheduled Reports:
├── Frecvență: Zilnic/Săptămânal/Lunar
├── Format: PDF/Excel/Email
├── Destinatari: Proprietar/Consultant/Autorități
└── Automatizare completă
```

### 8.3 Export și Integrare

**Opțiuni Export:**
```
📤 Export Options:
├── Excel: Date brute + grafice
├── PDF: Rapoarte formatate
├── CSV: Pentru alte sisteme
└── API: Integrare sisteme externe
```

---

## 9. 🔧 ETAPA 9: SETĂRI ȘI ÎNTREȚINERE

### 9.1 Gestionare Profil

**Setări Utilizator:**
```
👤 User Profile Settings:
├── Informații Personale
├── Preferințe Interfață
├── Notificări și Alerte
└── Securitate (2FA, schimbare parolă)
```

### 9.2 Administrare Exploatație

**Setări Avansate:**
```
⚙️ Farm Administration:
├── Utilizatori Multipli
│   ├── Roluri: Admin/Manager/Worker
│   ├── Permisiuni Granulare
│   └── Audit Log activități
├── Backup Automat
│   ├── Zilnic în cloud
│   ├── Restaurare punctuală
│   └── Export date complete
└── Integrări API
    ├── Stații Meteo
    ├── Furnizori Input-uri
    └── Cooperativa
```

### 9.3 Suport și Asistență

**Centru Ajutor:**
```
🆘 Help & Support:
├── Bază Cunoștințe
│   ├── Tutoriale Video
│   ├── Ghiduri Pas-cu-Pas
│   └── FAQ Interactivă
├── Chat Live
│   ├── Disponibil 8h-18h
│   ├── Răspuns <5 min
│   └── Istoric conversații
└── Contact Suport
    ├── Email prioritizat
    ├── Telefon urgențe
    └── Programare consultanță
```

---

## 10. 🎯 SCENARII SPECIALE DE UTILIZARE

### 10.1 Utilizator Începător

**Onboarding Simplificat:**
```
🆕 Beginner User Journey:
├── Tutorial Ghidat (5 minute)
├── Template-uri Pre-configurate
├── Asistent Virtual pentru Întrebări
└── Suport Prioritar 30 Zile
```

### 10.2 Utilizator Expert

**Funcții Avansate:**
```
🔬 Expert User Features:
├── API Access pentru Integrări
├── Analize Personalizate
├── Import Date Externe
└── Custom Dashboard Widgets
```

### 10.3 Utilizator Cooperativă

**Management Multi-Farm:**
```
🏢 Cooperative Management:
├── Dashboard Consolidat
├── Comparare Exploatații
├── Gestionare Membri
└── Rapoarte Agregate
```

### 10.4 Utilizator Consultant

**Mod Consultant:**
```
👨‍💼 Consultant Mode:
├── Acces Multipli Clienți
├── Comparare Portofoliu
├── Template-uri Personalizate
└── Rapoarte Profesionale
```

---

## 11. 📱 EXPERIENȚĂ MOBILĂ ȘI RESPONSIVE

### 11.1 App Mobilă

**Funcționalități Mobile:**
```
📱 Mobile App Features:
├── Hartă Offline (cache straturi)
├── Scanare Coduri Produse
├── Fotografii Tratament cu GPS
├── Notificări Push Urgente
└── Sincronizare Automată Cloud
```

### 11.2 Responsive Design

**Adaptare Ecran:**
```
🖥️ Responsive Breakpoints:
├── Desktop (>1200px): Layout complet
├── Tablet (768-1199px): Sidebar colapsabil
├── Mobile (<767px): Single column + bottom nav
└── Small Mobile (<480px): Simplified interface
```

---

## 12. 🔄 CICLUL DE VITAȚĂ AL UTILIZATORULUI

### 12.1 Etape Evoluție

**De la Începător la Expert:**
```
📈 User Lifecycle:
├── Săptămână 1: Explorare și setup
├── Lună 1: Utilizare zilnică de bază
├── Trimestru 1: Adoptare funcții avansate
├── An 1: Expert și optimizare
└── An 2+: Innovator și feedback
```

### 12.2 Reținere și Engagement

**Strategii Reținere:**
```
💎 Retention Strategies:
├── Onboarding Personalizat
├── Tutoriale Contextuale
├── Newsletter Lunar cu Tips
├── Update-uri Regulate cu Noutăți
└── Program Loyalty (reduceri upgrade)
```

---

*Document creat: Februarie 2026*
*VitiScan PRO v3.0 - User Journey Mapping Complet*