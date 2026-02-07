# 🗺️ Integrare IGN + Leaflet - VitiScan v3

## 📋 Prezentare Generală

VitiScan v3 folosește **IGN (Institut national de l'information géographique et forestière)** pentru hărțile satelit din Franța, în combinație cu **Leaflet** pentru trasarea interactivă a parcelelor agricole.

## 🔑 Obținere API Key IGN

### Pas 1: Creare Cont
1. Accesează https://geoservices.ign.fr/
2. Click pe **"Créer un compte"** (Creare cont)
3. Completează formularul de înregistrare

### Pas 2: Generare Cheie API
1. Autentifică-te în contul IGN
2. Accesează **"Mes clés"** (Cheile mele)
3. Click pe **"Créer une nouvelle clé"**
4. Selectează serviciile:
   - ✅ WMTS (Web Map Tile Service)
   - ✅ ORTHOIMAGERY.ORTHOPHOTOS
5. Copiază cheia generată

### Pas 3: Configurare în VitiScan
Adaugă cheia în `frontend/.env.local`:
```env
NEXT_PUBLIC_IGN_API_KEY=ta_cheie_ign_aici
```

## 🛠️ Tehnologii Folosite

### Frontend
- **Leaflet** - Librărie open-source pentru hărți interactive
- **React-Leaflet** - Componente React pentru Leaflet
- **Leaflet-Draw** - Plugin pentru desenare poligoane
- **Leaflet-GeometryUtil** - Calcul suprafețe în hectare

### Backend
- **MongoDB** - Stocare coordonate GeoJSON
- **FastAPI** - API endpoints pentru parcele

## 🗂️ Format Date GeoJSON

Coordonatele parcelelor sunt stocate în format GeoJSON Polygon:

```json
{
  "coordinates": [
    [
      [2.3522, 48.8566],  // [longitude, latitude]
      [2.3530, 48.8570],
      [2.3540, 48.8565],
      [2.3522, 48.8566]   // închide poligonul
    ]
  ]
}
```

## 📐 Calcul Suprafață

Suprafața este calculată automat folosind **algoritm geodezic**:
```typescript
const areaInSquareMeters = L.GeometryUtil.geodesicArea(latLngs);
const areaInHectares = areaInSquareMeters / 10000;
```

## 🎨 Layere IGN Disponibile

### 1. ORTHOIMAGERY.ORTHOPHOTOS (default)
Fotografii aeriene de înaltă rezoluție
- **Rezoluție**: până la 20cm/pixel
- **Acoperire**: întreaga Franță
- **Actualizare**: anuală

### 2. CADASTRALPARCELS.PARCELLAIRE_EXPRESS
Parcele cadastrale oficiale
```typescript
const cadastreLayer = L.tileLayer(
  `https://wxs.ign.fr/${API_KEY}/geoportail/wmts?layer=CADASTRALPARCELS.PARCELLAIRE_EXPRESS&...`
);
```

### 3. GEOGRAPHICALGRIDSYSTEMS.MAPS
Hărți topografice clasice
```typescript
const topoLayer = L.tileLayer(
  `https://wxs.ign.fr/${API_KEY}/geoportail/wmts?layer=GEOGRAPHICALGRIDSYSTEMS.MAPS&...`
);
```

## 🚀 Utilizare

### 1. Trasare Parcelă Nouă
```tsx
import ParcelMap from '@/components/ParcelMap';

<ParcelMap
  center={[45.9432, 24.9668]}  // Romania center
  zoom={7}
  editable={true}
  onParcelDrawn={(coordinates, area) => {
    console.log('Suprafață:', area, 'ha');
    console.log('Coordonate:', coordinates);
  }}
/>
```

### 2. Vizualizare Parcele Existente
```tsx
<ParcelMap
  parcels={[
    {
      id: '123',
      name: 'Parcelă Nord',
      coordinates: [[[2.35, 48.85], ...]],
      surface_ha: 5.2,
      crop_type: 'Viță de vie'
    }
  ]}
  editable={false}
/>
```

## 🔧 Troubleshooting

### Probleme Comune

**1. Harta nu se încarcă**
- Verifică API Key-ul IGN în `.env.local`
- Verifică conexiunea la internet
- Deschide Console (F12) pentru erori

**2. Iconuri marker lipsesc**
```typescript
// Fix în ParcelMap.tsx
L.Icon.Default.mergeOptions({
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  // ...
});
```

**3. Calcul suprafață incorect**
- Asigură-te că coordonatele sunt [lng, lat]
- Verifică că poligonul este închis (primul punct = ultimul)

## 📚 Resurse Utile

- [IGN Geoservices](https://geoservices.ign.fr/)
- [Leaflet Documentation](https://leafletjs.com/)
- [React-Leaflet Docs](https://react-leaflet.js.org/)
- [Leaflet-Draw Plugin](https://leaflet.github.io/Leaflet.draw/)
- [GeoJSON Specification](https://geojson.org/)

## 🌍 Alternative la IGN

Pentru alte țări în afară de Franța:

### OpenStreetMap (global)
```typescript
<TileLayer
  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
  attribution='&copy; OpenStreetMap'
/>
```

### Mapbox (necesită cont)
```typescript
<TileLayer
  url="https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{z}/{x}/{y}?access_token={accessToken}"
/>
```

### Google Maps
Necesită Google Maps API key (plătit pentru volume mari)

## 💡 Best Practices

1. **Validare Coordonate**
   - Verifică că longitudine: -180 la 180
   - Verifică că latitudine: -90 la 90

2. **Optimizare Performance**
   - Limitează numărul de parcele afișate simultan
   - Folosește clustering pentru multe parcele

3. **UX Design**
   - Adaugă zoom pe parcelă după creare
   - Afișează suprafață în timp real la desenare
   - Butoane clare pentru salvare/anulare

## 📝 Licență

IGN oferă date sub licență **Licence Ouverte / Open Licence**
- Utilizare gratuită pentru scopuri personale
- Atribuire necesară: "© IGN"
- Detalii: https://www.ign.fr/institut/geoservices/aide-en-ligne

---

**Dezvoltat pentru VitiScan v3** 🌿
