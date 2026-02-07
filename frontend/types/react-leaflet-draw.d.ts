declare module 'react-leaflet-draw' {
  import { Control } from 'leaflet';
  import { FC } from 'react';

  export interface EditControlProps {
    position?: 'topleft' | 'topright' | 'bottomleft' | 'bottomright';
    onCreated?: (e: any) => void;
    onEdited?: (e: any) => void;
    onDeleted?: (e: any) => void;
    draw?: any;
    edit?: any;
  }

  export const EditControl: FC<EditControlProps>;
}
