import React, { useState, useEffect, useRef, useCallback } from 'react';
import { MapContainer, TileLayer, Polygon, Marker, Popup, useMap, useMapEvents, FeatureGroup } from 'react-leaflet';
import { EditControl } from 'react-leaflet-draw';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';

// Import components
import { X, Palette, Layers, MapPin, Calendar, RefreshCw, Shield, Cloud, Eye, Settings, Search, MapPin as PinIcon, Check, Loader } from 'lucide-react';

// Fix for default markers
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const UnifiedMapModal = ({ 
  isOpen, 
  onClose, 
  user, 
  parcels = [], 
  focusParcel = null,
  onParcelDrawn,
  onSearchComplete,
  creationMode = false,
  currentStep = 'search'
}) => {
  const mapRef = useRef(null);
  const [mapInstance, setMapInstance] = useState(null);

  // Layer states
  const [baseLayer, setBaseLayer] = useState('osm');
  const [showVarietyColors, setShowVarietyColors] = useState(false);
  const [showLegend, setShowLegend] = useState(false);
  const [showLabels, setShowLabels] = useState(false);
  const [planningMode, setPlanningMode] = useState(false);

  // ZNT states
  const [showBCAELayer, setShowBCAELayer] = useState(false);
  const [showBDTOPOLayer, setShowBDTOPOLayer] = useState(false);
  const [showBuildingsLayer, setShowBuildingsLayer] = useState(false);
  const [showZNTBuffers, setShowZNTBuffers] = useState(false);

  // Weather/NDVI states
  const [weatherOverlay, setWeatherOverlay] = useState(null);
  const [showNdvi, setShowNdvi] = useState(false);
  const [ndviData, setNdviData] = useState({});

  // Data states
  const [selectedParcel, setSelectedParcel] = useState(null);
  const [zntData, setZntData] = useState({});
  const [varietySettings, setVarietySettings] = useState({});
  const [planningStates, setPlanningStates] = useState({});

  // UI states
  const [activePanel, setActivePanel] = useState(null); // 'legend', 'znt', 'weather', 'settings'
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Search states - enhanced with real API integration
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [searchCommune, setSearchCommune] = useState(() => {
    const saved = localStorage.getItem('cadastre_commune_name');
    return saved || '';
  });
  const [selectedCommune, setSelectedCommune] = useState(() => {
    const saved = localStorage.getItem('cadastre_commune');
    return saved ? JSON.parse(saved) : null;
  });
  const [communeSuggestions, setCommuneSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [searchSection, setSearchSection] = useState('');
  const [searchNumero, setSearchNumero] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);
  const [highlightedParcel, setHighlightedParcel] = useState(null);

  // Planning colors
  const planningColors = [
    { id: 1, name: 'Taille', color: '#22C55E', description: 'Travail terminé' },
    { id: 2, name: 'En cours', color: '#FACC15', description: 'À faire demain' },
    { id: 3, name: 'Non fait', color: '#EF4444', description: 'Pas encore commencé' }
  ];

  // NDVI scale
  const NDVI_SCALE = [
    { min: 0, max: 10, color: '#DC2626', label: 'CRITIC - Tratament URGENT', badge: '🔴' },
    { min: 10, max: 30, color: '#F97316', label: 'AVERTISMENT - Monitorizare', badge: '🟠' },
    { min: 30, max: 70, color: '#22C55E', label: 'OPTIMAL - Sănătos', badge: '🟢' },
    { min: 70, max: 100, color: '#EAB308', label: 'VIGOR EXCES - Reduce fertilizare', badge: '🟡' }
  ];

  // Base tile layers
  const tileLayers = {
    osm: {
      url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      attribution: '© OpenStreetMap contributors',
      options: { subdomains: ['a', 'b', 'c'] }
    },
    ign_ortho: {
      url: 'https://data.geopf.fr/wmts?REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0&STYLE=normal&TILEMATRIXSET=PM&FORMAT=image/jpeg&LAYER=ORTHOIMAGERY.ORTHOPHOTOS&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}',
      attribution: '© IGN Géoportail',
      options: { tms: true }
    },
    ign_plan: {
      url: 'https://data.geopf.fr/wmts?REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0&STYLE=normal&TILEMATRIXSET=PM&FORMAT=image/png&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}',
      attribution: '© IGN Géoportail',
      options: { tms: true }
    },
    ign_cadastre: {
      url: 'https://data.geopf.fr/wmts?REQUEST=GetTile&SERVICE=WMTS&VERSION=1.0.0&STYLE=normal&TILEMATRIXSET=PM&FORMAT=image/png&LAYER=CADASTRALPARCELS.PARCELLAIRE_EXPRESS&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}',
      attribution: '© IGN Géoportail',
      options: { tms: true }
    }
  };

  // Weather overlay layers (OpenWeatherMap)
  const weatherLayers = {
    temp: 'https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=YOUR_API_KEY',
    precipitation: 'https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid=YOUR_API_KEY',
    clouds: 'https://tile.openweathermap.org/map/clouds_new/{z}/{x}/{y}.png?appid=YOUR_API_KEY',
    wind: 'https://tile.openweathermap.org/map/wind_new/{z}/{x}/{y}.png?appid=YOUR_API_KEY'
  };

  // Load initial data
  useEffect(() => {
    if (isOpen && user) {
      // Temporarily disabled for testing - endpoints don't exist yet
      // loadVarietySettings();
      // loadPlanningStates();
      // loadNdviData();
    }
  }, [isOpen, user]);

  // Auto-focus on parcel
  useEffect(() => {
    if (focusParcel && mapInstance) {
      const bounds = L.geoJSON(focusParcel.geometry).getBounds();
      mapInstance.fitBounds(bounds, { padding: [20, 20] });
      setSelectedParcel(focusParcel);
    }
  }, [focusParcel, mapInstance]);

  // Close search results when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.search-container')) {
        setShowSearchResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Auto-switch to satellite layer when entering draw step in creation mode
  useEffect(() => {
    if (creationMode && currentStep === 'draw') {
      setBaseLayer('ign_ortho');
    }
  }, [creationMode, currentStep]);

  const loadVarietySettings = async () => {
    try {
      const response = await axios.get(`/api/variety-settings/${user.id}`);
      setVarietySettings(response.data);
    } catch (error) {
      console.error('Error loading variety settings:', error);
    }
  };

  const loadPlanningStates = async () => {
    try {
      const response = await axios.get(`/api/planning-states/${user.id}`);
      setPlanningStates(response.data);
    } catch (error) {
      console.error('Error loading planning states:', error);
    }
  };

  const loadNdviData = async () => {
    try {
      const ndviPromises = parcels.map(parcel =>
        axios.get(`/api/ndvi/${parcel.id}/current`)
      );
      const responses = await Promise.all(ndviPromises);
      const ndviMap = {};
      responses.forEach((response, index) => {
        ndviMap[parcels[index].id] = response.data;
      });
      setNdviData(ndviMap);
    } catch (error) {
      console.error('Error loading NDVI data:', error);
    }
  };

  const loadZntData = async (parcelId) => {
    try {
      const response = await axios.get(`/api/znt/parcelle/${parcelId}`);
      setZntData(prev => ({ ...prev, [parcelId]: response.data }));
    } catch (error) {
      console.error('Error loading ZNT data:', error);
    }
  };

  // Handle parcel creation in creation mode
  const handleCreated = (e) => {
    if (!creationMode || !onParcelDrawn) return;
    
    const { layerType, layer } = e;
    
    if (layerType === 'polygon') {
      const latLngs = layer.getLatLngs()[0];
      
      // Convert to GeoJSON coordinates format [lng, lat]
      let latLngArray = latLngs.map((latlng) => [latlng.lng, latlng.lat]);
      
      // Close the polygon ring by adding the first coordinate at the end if it's not already closed
      if (latLngArray.length > 0) {
        const firstCoord = latLngArray[0];
        const lastCoord = latLngArray[latLngArray.length - 1];
        if (firstCoord[0] !== lastCoord[0] || firstCoord[1] !== lastCoord[1]) {
          latLngArray.push(firstCoord);
        }
      }
      
      const coordinates = [latLngArray];
      
      // Calculate area in hectares
      const areaInSquareMeters = L.GeometryUtil.geodesicArea(latLngs);
      const areaInHectares = (areaInSquareMeters / 10000).toFixed(2);
      
      onParcelDrawn(coordinates, parseFloat(areaInHectares));
    }
  };

  // Enhanced search functions with real API integration
  const searchCommunesByName = async (query) => {
    if (query.length < 2) {
      setCommuneSuggestions([]);
      return;
    }

    try {
      const response = await axios.get(`https://api-adresse.data.gouv.fr/search/?q=${encodeURIComponent(query)}&type=municipality&limit=10`);
      if (response.data && response.data.features) {
        const communes = response.data.features.map(feature => ({
          nom: feature.properties.name,
          code_insee: feature.properties.citycode,
          code_postal: feature.properties.postcode,
          departement: feature.properties.context.split(', ')[1],
          label: `${feature.properties.name} (${feature.properties.postcode}) - ${feature.properties.context.split(', ')[1]}`
        }));
        setCommuneSuggestions(communes);
        setShowSuggestions(true);
      }
    } catch (error) {
      console.error('Commune search error:', error);
    }
  };

  const handleCommuneInputChange = (value) => {
    setSearchCommune(value);
    setSelectedCommune(null);
    localStorage.removeItem('cadastre_commune');
    localStorage.removeItem('cadastre_commune_name');

    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    searchTimeoutRef.current = setTimeout(() => {
      searchCommunesByName(value);
    }, 300);
  };

  const selectCommune = (commune) => {
    setSelectedCommune(commune);
    setSearchCommune(commune.nom);
    setCommuneSuggestions([]);
    setShowSuggestions(false);
    localStorage.setItem('cadastre_commune', JSON.stringify(commune));
    localStorage.setItem('cadastre_commune_name', commune.nom);
  };

  const searchCadastre = async () => {
    if (!selectedCommune?.code_insee) {
      alert('Selectați o comună din lista de sugestii');
      return;
    }

    const communeCode = selectedCommune.code_insee;

    setSearchLoading(true);
    setSearchResults([]);
    setHighlightedParcel(null);

    try {
      const params = new URLSearchParams({ commune: communeCode });
      if (searchSection) params.append('section', searchSection.toUpperCase());
      if (searchNumero) params.append('numero', searchNumero);

      // For now, use mock data since backend API doesn't exist yet
      // In production, this would be: /api/cadastre/search?${params}
      const mockResults = {
        type: "FeatureCollection",
        features: [
          {
            type: "Feature",
            properties: {
              numero: searchNumero.padStart(4, '0') || "0122",
              section: searchSection.toUpperCase() || "AB",
              contenance_m2: 25000,
              contenance_ha: 2.5,
              id_parcelle: `${searchSection.toUpperCase() || "AB"}-${(searchNumero.padStart(4, '0') || "0122")}`,
              commune: communeCode,
              nom_commune: selectedCommune.nom,
              centroid: { lat: 44.2494, lng: 4.8714 }
            },
            geometry: {
              type: "Polygon",
              coordinates: [[
                [4.8710, 44.2490], [4.8715, 44.2490], [4.8715, 44.2498], [4.8710, 44.2498], [4.8710, 44.2490]
              ]]
            }
          }
        ],
        count: 1
      };

      if (mockResults.features && mockResults.features.length > 0) {
        setSearchResults(mockResults);

        const firstFeature = mockResults.features[0];
        const centroid = firstFeature.properties?.centroid;

        if (centroid && mapInstance) {
          mapInstance.setView([centroid.lat, centroid.lng], 18);
          setHighlightedParcel(firstFeature);
        }

        // Notify parent component that search is complete
        if (onSearchComplete) {
          onSearchComplete();
        }
      } else {
        alert('Nicio parcelă găsită pentru această referință');
      }
    } catch (error) {
      console.error('Cadastre search error:', error);
      alert('Eroare la căutare');
    } finally {
      setSearchLoading(false);
    }
  };

  // Get parcel color based on current mode
  const getParcelColor = (parcel) => {
    if (planningMode && planningStates[parcel.id]) {
      const planningColor = planningColors.find(c => c.id === planningStates[parcel.id]);
      return planningColor ? planningColor.color : '#3388ff';
    }

    if (showNdvi && ndviData[parcel.id]) {
      const ndvi = ndviData[parcel.id].average_ndvi * 100;
      const scale = NDVI_SCALE.find(s => ndvi >= s.min && ndvi < s.max);
      return scale ? scale.color : '#808080';
    }

    if (showVarietyColors) {
      const variety = parcel.crop_type || 'default';
      return varietySettings[variety] || '#3388ff';
    }

    return '#3388ff'; // Default blue
  };

  // Get NDVI label for parcel
  const getNdviLabel = (parcel) => {
    if (!showNdvi || !ndviData[parcel.id]) return null;

    const ndvi = ndviData[parcel.id].average_ndvi * 100;
    const scale = NDVI_SCALE.find(s => ndvi >= s.min && ndvi < s.max);
    return {
      value: Math.round(ndvi),
      badge: scale?.badge || '⚪',
      color: scale?.color || '#808080'
    };
  };

  // Handle parcel click
  const handleParcelClick = (parcel) => {
    setSelectedParcel(parcel);
    if (showBCAELayer || showBDTOPOLayer || showBuildingsLayer) {
      loadZntData(parcel.id);
    }
  };

  // Toggle fullscreen
  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  if (!isOpen) return null;

  return (
    <div className={`fixed inset-0 z-50 ${isFullscreen ? 'fullscreen-map' : ''}`}>
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-lg font-semibold text-gray-900">Carte Unifiée VitiScan</h2>
          <span className="text-sm text-gray-500">
            Parcelles: {parcels.length} | Surface: {parcels.reduce((sum, p) => sum + (p.area_ha || 0), 0).toFixed(1)} ha
          </span>
        </div>

        {/* Enhanced Cadastral Search */}
        <div className="flex-1 max-w-2xl mx-4 relative search-container">
          <div className="bg-white border border-gray-300 rounded-lg p-3 shadow-sm">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
              {/* Commune Search with Autocomplete */}
              <div className="md:col-span-2 relative">
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Comună
                </label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <input
                    type="text"
                    placeholder="Caută comună..."
                    value={searchCommune}
                    onChange={(e) => handleCommuneInputChange(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  />
                  {showSuggestions && communeSuggestions.length > 0 && (
                    <div className="absolute top-full left-0 right-0 bg-white border border-gray-300 rounded-md shadow-lg mt-1 max-h-40 overflow-y-auto z-50">
                      {communeSuggestions.map((commune, index) => (
                        <button
                          key={index}
                          onClick={() => selectCommune(commune)}
                          className="w-full px-3 py-2 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                        >
                          <div className="text-sm font-medium text-gray-900">{commune.nom}</div>
                          <div className="text-xs text-gray-600">
                            {commune.code_postal} - {commune.departement}
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                {selectedCommune && (
                  <div className="mt-1 text-xs text-green-600 flex items-center">
                    <Check className="h-3 w-3 mr-1" />
                    {selectedCommune.nom} ({selectedCommune.code_postal})
                  </div>
                )}
              </div>

              {/* Section Input */}
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Secțiune
                </label>
                <input
                  type="text"
                  placeholder="AB"
                  value={searchSection}
                  onChange={(e) => setSearchSection(e.target.value.toUpperCase())}
                  maxLength={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm uppercase"
                />
              </div>

              {/* Numero Input */}
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Număr
                </label>
                <input
                  type="text"
                  placeholder="0122"
                  value={searchNumero}
                  onChange={(e) => setSearchNumero(e.target.value)}
                  maxLength={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                />
              </div>
            </div>

            {/* Search Button */}
            <div className="mt-3 flex justify-end">
              <button
                onClick={searchCadastre}
                disabled={searchLoading || !selectedCommune}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-sm font-medium flex items-center space-x-2"
              >
                {searchLoading ? (
                  <Loader className="h-4 w-4 animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
                <span>Caută Parcelă</span>
              </button>
            </div>
          </div>
        </div>

        {/* Base Layer Selector */}
        <div className="flex items-center space-x-1 bg-gray-100 rounded-lg p-1">
          {Object.keys(tileLayers).map(layer => (
            <button
              key={layer}
              onClick={() => setBaseLayer(layer)}
              className={`px-3 py-1 text-xs rounded-md transition-colors ${
                baseLayer === layer ? 'bg-blue-500 text-white' : 'text-gray-600 hover:bg-gray-200'
              }`}
            >
              {layer === 'osm' ? 'OSM' :
               layer === 'ign_ortho' ? 'Satellite' :
               layer === 'ign_plan' ? 'Plan IGN' : 'Cadastre'}
            </button>
          ))}
        </div>

        {/* Control Buttons */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowVarietyColors(!showVarietyColors)}
            className={`p-2 rounded-md ${showVarietyColors ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'}`}
            data-testid="toggle-variety-colors"
            title="Colorare pe soiuri"
          >
            <Palette size={18} />
          </button>

          <button
            onClick={() => setShowLegend(!showLegend)}
            className={`p-2 rounded-md ${showLegend ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'}`}
            data-testid="toggle-legend"
            title="Legendă soiuri"
          >
            <Layers size={18} />
          </button>

          <button
            onClick={() => setShowLabels(!showLabels)}
            className={`p-2 rounded-md ${showLabels ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'}`}
            data-testid="toggle-labels"
            title="Etichete localități"
          >
            <MapPin size={18} />
          </button>

          <button
            onClick={() => setPlanningMode(!planningMode)}
            className={`p-2 rounded-md ${planningMode ? 'bg-blue-100 text-blue-600' : 'text-gray-600 hover:bg-gray-100'}`}
            data-testid="toggle-planning-mode"
            title="Mod planificare"
          >
            <Calendar size={18} />
          </button>

          {/* ZNT Controls */}
          <button
            onClick={() => setShowBCAELayer(!showBCAELayer)}
            className={`p-2 rounded-md ${showBCAELayer ? 'bg-red-100 text-red-600' : 'text-gray-600 hover:bg-gray-100'}`}
            title="Strat BCAE PAC"
          >
            <Shield size={18} />
          </button>

          {/* Weather/NDVI Controls */}
          <button
            onClick={() => setShowNdvi(!showNdvi)}
            className={`p-2 rounded-md ${showNdvi ? 'bg-green-100 text-green-600' : 'text-gray-600 hover:bg-gray-100'}`}
            title="Overlay NDVI"
          >
            <Eye size={18} />
          </button>

          <button
            onClick={() => setWeatherOverlay(weatherOverlay === 'temp' ? null : 'temp')}
            className={`p-2 rounded-md ${weatherOverlay === 'temp' ? 'bg-orange-100 text-orange-600' : 'text-gray-600 hover:bg-gray-100'}`}
            title="Temperatură"
          >
            🌡️
          </button>

          <button
            onClick={toggleFullscreen}
            className="p-2 text-gray-600 hover:bg-gray-100 rounded-md"
            title="Fullscreen"
          >
            ⛶
          </button>

          <button
            onClick={onClose}
            className="p-2 text-gray-600 hover:bg-gray-100 rounded-md"
            data-testid="close-unified-modal"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex h-full">
        {/* Map Container */}
        <div className="flex-1 relative">
          <MapContainer
            center={[44.2494, 4.8714]}
            zoom={10}
            style={{ height: '100%', width: '100%' }}
            ref={mapRef}
            whenReady={() => setMapInstance(mapRef.current)}
          >
            {/* Base Layer */}
            <TileLayer
              url={tileLayers[baseLayer].url}
              attribution={tileLayers[baseLayer].attribution}
              {...(tileLayers[baseLayer].options || {})}
            />

            {/* Weather Overlay */}
            {weatherOverlay && (
              <TileLayer
                url={weatherLayers[weatherOverlay]}
                opacity={0.6}
              />
            )}

            {/* Parcels */}
            {parcels.map(parcel => (
              <Polygon
                key={parcel.id}
                positions={parcel.geometry.coordinates[0].map(coord => [coord[1], coord[0]])}
                pathOptions={{
                  color: getParcelColor(parcel),
                  weight: selectedParcel?.id === parcel.id ? 4 : 2,
                  opacity: selectedParcel?.id === parcel.id ? 0.9 : 0.7,
                  fillOpacity: 0.3
                }}
                eventHandlers={{
                  click: () => handleParcelClick(parcel)
                }}
              >
                <Popup>
                  <div className="p-2">
                    <h3 className="font-semibold">{parcel.name}</h3>
                    <p className="text-sm text-gray-600">
                      {parcel.crop_type} • {parcel.area_ha} ha • Planté {parcel.planting_year}
                    </p>

                    {showNdvi && getNdviLabel(parcel) && (
                      <p className="text-sm mt-1">
                        NDVI: {getNdviLabel(parcel).value}% {getNdviLabel(parcel).badge}
                      </p>
                    )}

                    {planningMode && planningStates[parcel.id] && (
                      <p className="text-sm mt-1">
                        État: {planningColors.find(c => c.id === planningStates[parcel.id])?.name}
                      </p>
                    )}
                  </div>
                </Popup>
              </Polygon>
            ))}

            {/* NDVI Labels */}
            {showNdvi && parcels.map(parcel => {
              const label = getNdviLabel(parcel);
              if (!label) return null;

              const center = L.geoJSON(parcel.geometry).getBounds().getCenter();
              return (
                <Marker
                  key={`ndvi-${parcel.id}`}
                  position={[center.lat, center.lng]}
                  icon={L.divIcon({
                    className: 'ndvi-label',
                    html: `<div style="background: ${label.color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 12px; font-weight: bold;">${label.value}% ${label.badge}</div>`,
                    iconSize: [50, 20],
                    iconAnchor: [25, 10]
                  })}
                />
              );
            })}

            {/* Highlighted Cadastral Parcel */}
            {highlightedParcel && (
              <Polygon
                positions={highlightedParcel.geometry.coordinates[0].map(coord => [coord[1], coord[0]])}
                pathOptions={{
                  color: '#ff0000',
                  weight: 4,
                  opacity: 1,
                  fillOpacity: 0.2,
                  dashArray: '10, 5'
                }}
              >
                <Popup>
                  <div className="p-2">
                    <h3 className="font-semibold text-red-600">Parcelă Cadastrală</h3>
                    <p className="text-sm">
                      Secțiune: {highlightedParcel.properties.section}<br/>
                      Număr: {highlightedParcel.properties.numero}<br/>
                      Suprafață: {highlightedParcel.properties.contenance_ha} ha<br/>
                      Comună: {highlightedParcel.properties.nom_commune}
                    </p>
                  </div>
                </Popup>
              </Polygon>
            )}

            {/* Drawing Controls for Creation Mode */}
            {creationMode && currentStep === 'draw' && (
              <FeatureGroup>
                <EditControl
                  position="topright"
                  onCreated={handleCreated}
                  draw={{
                    rectangle: false,
                    circle: false,
                    circlemarker: false,
                    marker: false,
                    polyline: false,
                    polygon: {
                      allowIntersection: false,
                      drawError: {
                        color: '#e74c3c',
                        message: 'Parcelele nu pot avea intersecții!'
                      },
                      shapeOptions: {
                        color: '#16a34a',
                        fillOpacity: 0.3,
                        weight: 2
                      }
                    }
                  }}
                  edit={{
                    edit: false,
                    remove: false
                  }}
                />
              </FeatureGroup>
            )}
          </MapContainer>
        </div>

        {/* Side Panel */}
        {(showLegend || activePanel) && (
          <div className="w-80 bg-white border-l border-gray-200 overflow-y-auto">
            {showLegend && (
              <div className="p-4 border-b border-gray-200">
                <h3 className="font-semibold mb-3">🍇 Légende Soiuri</h3>
                <div className="space-y-2">
                  {Object.entries(varietySettings).map(([variety, color]) => (
                    <div key={variety} className="flex items-center space-x-2">
                      <div
                        className="w-4 h-4 rounded border"
                        style={{ backgroundColor: color }}
                      />
                      <span className="text-sm">{variety}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {planningMode && (
              <div className="p-4 border-b border-gray-200">
                <h3 className="font-semibold mb-3">📅 État Planification</h3>
                <div className="space-y-2">
                  {planningColors.map(color => {
                    const count = Object.values(planningStates).filter(state => state === color.id).length;
                    const area = parcels
                      .filter(p => planningStates[p.id] === color.id)
                      .reduce((sum, p) => sum + (p.area_ha || 0), 0);

                    return (
                      <div key={color.id} className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div
                            className="w-4 h-4 rounded"
                            style={{ backgroundColor: color.color }}
                          />
                          <span className="text-sm">{color.name}</span>
                        </div>
                        <span className="text-xs text-gray-500">
                          {count} parc. • {area.toFixed(1)} ha
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {showNdvi && (
              <div className="p-4 border-b border-gray-200">
                <h3 className="font-semibold mb-3">👁️ Légende NDVI</h3>
                <div className="space-y-2">
                  {NDVI_SCALE.map(scale => (
                    <div key={scale.min} className="flex items-center space-x-2">
                      <span className="text-lg">{scale.badge}</span>
                      <div
                        className="w-4 h-4 rounded"
                        style={{ backgroundColor: scale.color }}
                      />
                      <span className="text-xs">{scale.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default UnifiedMapModal;