'use client';

import { useState } from 'react';

interface CalendarEventCardProps {
  parcelId: string;
  onOpen: () => void;
}

export default function CalendarEventCard({ parcelId, onOpen }: CalendarEventCardProps) {
  const [eventCount] = useState(0);

  return (
    <div 
      onClick={onOpen}
      className="bg-gray-800/50 border border-gray-700 rounded-lg p-6 cursor-pointer hover:border-green-600 hover:bg-gray-800 transition-all"
    >
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-white font-semibold mb-2 flex items-center gap-2">
            📅 Calendrier & Événements
          </h2>
          <p className="text-gray-400 text-sm">
            {eventCount} événement{eventCount !== 1 ? 's' : ''} pour le moment
          </p>
        </div>
        <div className="text-2xl">➜</div>
      </div>

      <div className="mt-4 bg-gray-900/50 rounded p-3 border border-gray-700 border-dashed">
        <p className="text-gray-400 text-xs text-center">Cliquez pour ouvrir le calendrier</p>
      </div>
    </div>
  );
}
