# VitiScan PRO - Documentație Hartă Unificată

## Harta Unificată (UnifiedMapModal.js)

### 1.1 Descriere Generală
Harta Unificată reprezintă evoluția finală a sistemului cartografic VitiScan, combinând toate funcționalitățile din cele trei hărți anterioare (IGN, ZNT, Meteo/NDVI) într-o singură interfață puternică și intuitivă.

**Fișier:** `/app/frontend/src/components/UnifiedMapModal.js` (~95KB)

**Avantaje:**
- **Simplificare UX:** O singură hartă pentru toate nevoile
- **Performanță:** Un singur container Leaflet încărcat
- **Integrare:** Toate overlay-urile și controalele într-un singur loc
- **Flexibilitate:** Toggle-uri pentru activarea/dezactivarea funcționalităților

### 1.2 Interfață UI - Toolbar Unificat

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🗺️ Carte Unifiée VitiScan                      [OSM][Satellite][Plan IGN][Cadastre]         │
│    Parcelles: 30 | Surface: 45.2 ha                                                        │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│ 🎨🗂️📍📅🛡️👁️🌡️🌧️☁️💨 ⛶ ✕                                                     │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Butoane din Toolbar (grupate logic):**

| Grupă | Butoane | Funcție |
|-------|---------|---------|
| **Vizualizare** | 🎨 Palette | Colorare pe soiuri |
| | 🗂️ Layers | Afișează/ascunde legenda |
| | 📍 MapPin | Etichete localități |
| | 📅 Calendar | Mod planificare vizuală |
| **Conformitate** | 🛡️ Shield | Straturi ZNT (BCAE, BD TOPO) |
| **Monitorizare** | 👁️ Eye | Overlay NDVI |
| | 🌡️🌧️☁️💨 | Overlay-uri meteorologice |
| **Controale** | ⛶ | Fullscreen |
| | ✕ | Închide modalul |

### 1.3 Straturi de Bază Integrate

Toate straturile din hărțile anterioare sunt disponibile:

| Sursă | Straturi | Descriere |
|-------|----------|-----------|
| **IGN Géoportail** | Satellite, Plan IGN, Cadastre | Hartă oficială franceză |
| **OpenStreetMap** | OSM | Hartă rutieră clasică |
| **OpenWeatherMap** | Temp, Precipitation, Clouds, Wind | Overlay-uri meteo |
| **Backend VitiScan** | Parcele, ZNT, NDVI | Date specifice aplicației |

### 1.4 Funcționalități Integrate

#### A) Gestionarea Parcelelor (din IGN Map)
- Vizualizare poligoane cu click pentru detalii
- Colorare dinamică: soiuri, planificare, NDVI
- Editare contur (funcționalitate păstrată)
- Popup-uri detaliate cu KPIs

#### B) Mod Planificare Vizuală (din IGN Map)
- 3 stări de culoare pentru fiecare parcelă
- Statistici în timp real (hectare per stare)
- Salvare automată în `planning_states`

#### C) Conformitate ZNT (din ZNT Map)
- Strat BCAE PAC (referință oficială)
- Strat BD TOPO (indicativ)
- Zone tampon calculate
- Verificare conformitate automată
- Adăugare puncte personalizate

#### D) Monitorizare Vegetație (din Meteo/NDVI Map)
- Overlay NDVI cu scară color
- Etichete procentuale pe parcele
- Overlay-uri meteorologice multiple
- Integrare cu prognoza 5 zile

### 1.5 Panel Lateral Unificat

În loc de panel-uri separate, un singur panel lateral cu secțiuni:

```
┌─────────────────────────────────────┐
│ 🍇 Légende Soiuri                   │
│ ● Grenache #22C55E                  │
│ ● Syrah #7C3AED                     │
│ [+ Ajouter cépage]                 │
├─────────────────────────────────────┤
│ 📅 État Planification               │
│ ● Taille: 12 parc. • 18.5 ha       │
│ ● En cours: 8 parc. • 12.3 ha      │
│ ● Non fait: 10 parc. • 14.4 ha     │
├─────────────────────────────────────┤
│ 👁️ Légende NDVI                     │
│ 🔴 CRITIC (<10%)                    │
│ 🟠 AVERTISMENT (10-30%)             │
│ 🟢 OPTIMAL (30-70%)                 │
│ 🟡 VIGOR EXCES (>70%)               │
├─────────────────────────────────────┤
│ 🛡️ ZNT Actif                        │
│ ✅ CONFORME                         │
│ Sources: BCAE PAC 2024              │
└─────────────────────────────────────┘
```

### 1.6 Moduri de Funcționare

Harta unificată suportă **moduri multiple simultane**:

| Mod | Activare | Efect |
|-----|----------|-------|
| **Standard** | Default | Vizualizare parcele albastre |
| **Soiuri** | 🎨 | Colorare pe tipuri de struguri |
| **Planificare** | 📅 | Stări de lucru cu statistici |
| **NDVI** | 👁️ | Sănătate vegetație cu etichete |
| **ZNT** | 🛡️ | Conformitate cu zone tampon |
| **Meteo** | 🌡️🌧️☁️💨 | Overlay-uri meteorologice |

**Moduri pot fi combinate:** De exemplu, poți activa simultan NDVI + ZNT + Planificare pentru o analiză completă.

### 1.7 API-uri Backend Utilizate

Toate endpoint-urile din hărțile anterioare sunt păstrate:

| Funcționalitate | Endpoint | Metodă |
|----------------|----------|--------|
| Parcele | `/api/parcels/{user_id}` | GET |
| Setări soiuri | `/api/variety-settings/{user_id}` | GET/PUT |
| Stări planificare | `/api/planning-states/{user_id}` | GET/PUT |
| ZNT parcelă | `/api/znt/parcelle/{parcel_id}` | GET |
| NDVI curent | `/api/ndvi/{parcel_id}/current` | GET |
| Meteo curent | `/api/weather/{parcel_id}/current` | GET |

### 1.8 Performanță și Optimizări

**Încărcare Inteligentă:**
- Datele se încarcă doar când sunt necesare
- Cache pentru setări și stări
- Lazy loading pentru overlay-uri mari

**Optimizări UX:**
- Un singur container Leaflet (nu 3)
- Toggle-uri pentru activarea funcționalităților
- Panel lateral colapsabil
- Fullscreen nativ

### 1.9 Integrare în Aplicație

**Înlocuire componente existente:**
```javascript
// În Dashboard.js
import UnifiedMapModal from './components/UnifiedMapModal';

// Înlocuiește cele 3 componente separate
// <IGNMapModal /> + <ZNTMapModal /> + <WeatherNDVIMap />

<UnifiedMapModal
  isOpen={showUnifiedMap}
  onClose={() => setShowUnifiedMap(false)}
  user={currentUser}
  parcels={userParcels}
  focusParcel={selectedParcel}
/>
```

**Avantaje integrare:**
- Reducere cod cu ~60%
- Experiență utilizator simplificată
- Mentenanță mai ușoară
- Performanță îmbunătățită

---

## 2. COMPARAȚIE: Hărți Separate vs Harta Unificată

| Aspect | Hărți Separate | Hartă Unificată |
|--------|----------------|-----------------|
| **Număr componente** | 3 (IGN + ZNT + Meteo) | 1 |
| **Complexitate cod** | ~280KB | ~95KB |
| **Număr containere Leaflet** | 3 | 1 |
| **API calls** | 9 endpoint-uri diferite | 6 endpoint-uri |
| **UX Complexity** | 3 modaluri diferite | 1 modal cu toggle-uri |
| **Performanță** | 3× mai multe resurse | Optimizat |
| **Mentenanță** | 3 fișiere separate | 1 fișier central |
| **Extensibilitate** | Limitată | Foarte bună |

---

## 3. UTILIZARE RECOMANDATĂ

### 3.1 Scenarii de Utilizare

**Pentru Management Zilnic:**
1. Activează strat OSM sau Plan IGN
2. Activează colorare pe soiuri (🎨)
3. Activează mod planificare (📅)
4. Verifică stările în panel lateral

**Pentru Conformitate ZNT:**
1. Activează strat Satellite pentru vizibilitate
2. Activează overlay ZNT (🛡️)
3. Verifică status conformitate în panel
4. Adaugă puncte personalizate dacă necesar

**Pentru Monitorizare Vegetație:**
1. Activează strat Satellite
2. Activează overlay NDVI (👁️)
3. Activează overlay temperatură (🌡️)
4. Compară cu stările de planificare

**Pentru Analiză Completă:**
1. Activează toate overlay-urile relevante
2. Folosește fullscreen (⛶)
3. Consultă panel lateral pentru toate informațiile

### 3.2 Configurație Tehnică

**Dependențe:** Identice cu hărțile separate
**API Keys:** Păstrate (IGN public, OpenWeatherMap)
**Backend:** Compatibil 100% cu API-urile existente

---

## 4. EVOLUȚIE ȘI COMPATIBILITATE

**Migrare de la hărți separate:**
- Componenta UnifiedMapModal înlocuiește complet IGNMapModal, ZNTMapModal, și WeatherNDVIMap
- Toate props-urile sunt păstrate pentru compatibilitate
- Funcționalitățile sunt identice, doar interfața este unificată

**Beneficii pentru dezvoltare:**
- Reducere complexitate codebase
- Mai ușor de adăugat funcționalități noi
- Testare simplificată
- Documentație unificată

---

*Document actualizat: Februarie 2026*
*VitiScan PRO v3.0 - Hartă Unificată*