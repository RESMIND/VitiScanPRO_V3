'use client';

import { MapContainer, TileLayer, FeatureGroup, Polygon, Popup, LayersControl } from 'react-leaflet';
import { EditControl } from 'react-leaflet-draw';
import { LatLngExpression } from 'leaflet';
import { useState, useEffect } from 'react';
import L from 'leaflet';

// Fix Leaflet icon issue in Next.js
if (typeof window !== 'undefined') {
  delete (L.Icon.Default.prototype as any)._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  });
}

interface ParcelData {
  id?: string;
  name: string;
  coordinates: number[][][];
  surface_ha?: number;
  crop_type?: string;
}

interface ParcelMapProps {
  parcels?: ParcelData[];
  onParcelDrawn?: (coordinates: number[][][], area: number) => void;
  onParcelClick?: (parcelId: string) => void;
  center?: LatLngExpression;
  zoom?: number;
  editable?: boolean;
  useUserLocation?: boolean;
  mapClassName?: string;
  placeholderClassName?: string;
}

const DEFAULT_CENTER: LatLngExpression = [46.603354, 1.888334]; // Center of France

export default function ParcelMap({
  parcels = [],
  onParcelDrawn,
  onParcelClick,
  center = DEFAULT_CENTER,
  zoom = 6,
  editable = true,
  useUserLocation = false,
  mapClassName,
  placeholderClassName
}: ParcelMapProps) {
  const [isMounted, setIsMounted] = useState(false);
  const [mapCenter, setMapCenter] = useState<LatLngExpression>(center);
  const [mapInstance, setMapInstance] = useState<L.Map | null>(null);
  
  const IGN_API_KEY = process.env.NEXT_PUBLIC_IGN_API_KEY;
  const useIgn = Boolean(IGN_API_KEY && IGN_API_KEY.trim().length > 0);
  const [ignAvailable, setIgnAvailable] = useState(useIgn);
  const ignAttribution = '&copy; <a href="https://www.ign.fr/">IGN</a>';
  const osmAttribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>';
  const ignBase = `https://wxs.ign.fr/${IGN_API_KEY}/geoportail/wmts?style=normal&tilematrixset=PM&Service=WMTS&Request=GetTile&Version=1.0.0&TileMatrix={z}&TileCol={x}&TileRow={y}`;
  const ignSatelliteUrl = `${ignBase}&layer=ORTHOIMAGERY.ORTHOPHOTOS&Format=image/jpeg`;
  const ignPlanUrl = `${ignBase}&layer=GEOGRAPHICALGRIDSYSTEMS.MAPS&Format=image/png`;
  const ignCadastreUrl = `${ignBase}&layer=CADASTRALPARCELS.PARCELLAIRE_EXPRESS&Format=image/png`;

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    if (!useUserLocation || typeof window === 'undefined' || !navigator.geolocation) return;

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setMapCenter([position.coords.latitude, position.coords.longitude]);
      },
      () => {
        // Keep fallback center on error/deny
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 }
    );
  }, [useUserLocation]);

  useEffect(() => {
    if (!mapInstance) return;
    const container = mapInstance.getContainer();
    if (!container) return;
    mapInstance.setView(mapCenter, zoom, { animate: false });
    mapInstance.invalidateSize();
  }, [mapInstance, mapCenter, zoom]);

  const handleIgnTileError = () => {
    if (!ignAvailable) return;
    setIgnAvailable(false);
  };

  const handleCreated = (e: any) => {
    const { layerType, layer } = e;
    
    if (layerType === 'polygon') {
      const latLngs = layer.getLatLngs()[0];
      
      // Convert to GeoJSON coordinates format [lng, lat]
      let latLngArray = latLngs.map((latlng: any) => [latlng.lng, latlng.lat]);
      
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
      
      if (onParcelDrawn) {
        onParcelDrawn(coordinates, parseFloat(areaInHectares));
      }
    }
  };

  if (!isMounted) {
    return (
      <div className={placeholderClassName ?? "w-full h-[600px] bg-gray-200 rounded-lg flex items-center justify-center"}>
        <p className="text-gray-600">Chargement de la carte...</p>
      </div>
    );
  }

  return (
    <MapContainer
      center={mapCenter}
      zoom={zoom}
      className={mapClassName ?? "w-full h-[600px] rounded-lg"}
      style={{ zIndex: 0 }}
      whenReady={() => {
        // Map is ready, drawing tools will be initialized after
      }}
    >
      <LayersControl position="topright">
        {ignAvailable && (
          <>
            <LayersControl.BaseLayer checked name="IGN Satellite">
              <TileLayer
                url={ignSatelliteUrl}
                attribution={ignAttribution}
                maxZoom={19}
                eventHandlers={{ tileerror: handleIgnTileError }}
              />
            </LayersControl.BaseLayer>
            <LayersControl.BaseLayer name="IGN Plan">
              <TileLayer
                url={ignPlanUrl}
                attribution={ignAttribution}
                maxZoom={19}
                eventHandlers={{ tileerror: handleIgnTileError }}
              />
            </LayersControl.BaseLayer>
            <LayersControl.BaseLayer name="IGN Cadastre">
              <TileLayer
                url={ignCadastreUrl}
                attribution={ignAttribution}
                maxZoom={19}
                eventHandlers={{ tileerror: handleIgnTileError }}
              />
            </LayersControl.BaseLayer>
          </>
        )}
        <LayersControl.BaseLayer checked={!ignAvailable} name="OpenStreetMap">
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution={osmAttribution}
            maxZoom={19}
          />
        </LayersControl.BaseLayer>
      </LayersControl>

      {/* Drawing Controls */}
      {editable && (
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
                  fillOpacity: 0.3
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

      {/* Existing Parcels */}
      {parcels.map((parcel, index) => {
        if (!parcel.coordinates || parcel.coordinates.length === 0) return null;
        
        // Convert GeoJSON coordinates [lng, lat] to Leaflet [lat, lng]
        const positions: LatLngExpression[] = parcel.coordinates[0].map(
          (coord) => [coord[1], coord[0]] as LatLngExpression
        );

        return (
          <Polygon
            key={parcel.id || index}
            positions={positions}
            pathOptions={{
              color: '#16a34a',
              fillColor: '#16a34a',
              fillOpacity: 0.3,
              weight: 2
            }}
            eventHandlers={{
              click: () => {
                if (onParcelClick && parcel.id) {
                  onParcelClick(parcel.id);
                }
              }
            }}
          >
            <Popup>
              <div className="p-2">
                <h3 className="font-bold text-green-800">{parcel.name}</h3>
                {parcel.surface_ha && (
                  <p className="text-sm">Suprafață: {parcel.surface_ha} ha</p>
                )}
                {parcel.crop_type && (
                  <p className="text-sm">Cultură: {parcel.crop_type}</p>
                )}
              </div>
            </Popup>
          </Polygon>
        );
      })}
    </MapContainer>
  );
}
