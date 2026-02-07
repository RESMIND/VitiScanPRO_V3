'use client';

import { useState, useEffect } from 'react';

interface CalendarEventModalProps {
  parcelId: string;
  onClose: () => void;
}

interface CalendarDay {
  date: number;
  isCurrentMonth: boolean;
  isToday: boolean;
  events: string[];
}

const EVENT_TYPES = {
  Tous: 'Toate',
  Manuel: 'Manual',
  Intelligent: 'Inteligent'
};

export default function CalendarEventModal({ parcelId, onClose }: CalendarEventModalProps) {
  const [currentDate, setCurrentDate] = useState(new Date(2026, 0, 1)); // January 2026
  const [selectedFilter, setSelectedFilter] = useState<'Tous' | 'Manuel' | 'Intelligent'>('Tous');
  const [calendarDays, setCalendarDays] = useState<CalendarDay[]>([]);

  // Generate calendar days
  useEffect(() => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days: CalendarDay[] = [];

    // Previous month days
    const prevMonthLastDay = new Date(year, month, 0).getDate();
    for (let i = startingDayOfWeek - 1; i >= 0; i--) {
      days.push({
        date: prevMonthLastDay - i,
        isCurrentMonth: false,
        isToday: false,
        events: []
      });
    }

    // Current month days
    for (let i = 1; i <= daysInMonth; i++) {
      days.push({
        date: i,
        isCurrentMonth: true,
        isToday: i === 29 && month === 0, // 29 Jan 2026 highlighted in image
        events: i === 29 ? ['Travail'] : []
      });
    }

    // Next month days
    const totalCells = days.length;
    const remainingCells = 42 - totalCells;
    for (let i = 1; i <= remainingCells; i++) {
      days.push({
        date: i,
        isCurrentMonth: false,
        isToday: false,
        events: []
      });
    }

    setCalendarDays(days);
  }, [currentDate]);

  const monthName = currentDate.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
  const weekDays = ['LUN', 'MAR', 'MER', 'JEU', 'VEN', 'SAM', 'DIM'];

  const previousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-white text-2xl font-bold">PARCELA-01-SAOREL</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            ✕
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left - History Sidebar */}
          <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700">
            <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
              📅 Historique
            </h3>
            <div className="text-sm text-gray-400">01-SAOREL</div>
            <div className="mt-4 bg-gray-800 rounded p-3 border border-gray-700">
              <h4 className="text-green-400 text-xs font-bold flex items-center gap-2 mb-2">
                ✓ TAILLE
              </h4>
              <p className="text-gray-400 text-xs">2025-2026</p>
            </div>
          </div>

          {/* Center - Calendar */}
          <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700">
            <div className="mb-4">
              <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                📅 Calendrier
              </h3>

              {/* Month Navigation */}
              <div className="flex items-center justify-between mb-4">
                <button
                  onClick={previousMonth}
                  className="text-gray-400 hover:text-white text-xl"
                >
                  ‹
                </button>
                <h4 className="text-white font-semibold capitalize text-center flex-1">
                  {monthName}
                </h4>
                <button
                  onClick={nextMonth}
                  className="text-gray-400 hover:text-white text-xl"
                >
                  ›
                </button>
              </div>

              {/* Week Days Header */}
              <div className="grid grid-cols-7 gap-1 mb-2">
                {weekDays.map(day => (
                  <div key={day} className="text-gray-400 text-xs font-semibold text-center py-1">
                    {day}
                  </div>
                ))}
              </div>

              {/* Calendar Grid */}
              <div className="grid grid-cols-7 gap-1">
                {calendarDays.map((day, idx) => (
                  <button
                    key={idx}
                    className={`
                      aspect-square flex items-center justify-center rounded text-sm font-semibold transition-colors
                      ${!day.isCurrentMonth
                        ? 'text-gray-600 bg-gray-800/30'
                        : day.isToday
                        ? 'bg-pink-500 text-white hover:bg-pink-600'
                        : 'text-gray-300 bg-gray-800 hover:bg-gray-700'
                      }
                    `}
                  >
                    {day.date}
                  </button>
                ))}
              </div>

              {/* Filter Legend */}
              <div className="mt-4 flex items-center gap-2 justify-center text-xs">
                <span className="text-purple-400">✦ Intelligent</span>
                <span className="text-gray-600">•</span>
                <span className="text-white">⬤ Manuel</span>
              </div>
            </div>
          </div>

          {/* Right - Events List & Filter */}
          <div className="space-y-4">
            {/* Filter Buttons */}
            <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700">
              <h3 className="text-white font-semibold mb-3">Filtru</h3>
              <div className="space-y-2">
                {(Object.entries(EVENT_TYPES) as Array<['Tous' | 'Manuel' | 'Intelligent', string]>).map(([key, label]) => (
                  <button
                    key={key}
                    onClick={() => setSelectedFilter(key)}
                    className={`
                      w-full text-left px-3 py-2 rounded text-sm transition-colors
                      ${selectedFilter === key
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                      }
                    `}
                  >
                    {key === 'Tous' ? '📅 Toate' : key === 'Manuel' ? '✍️ Manual' : '✨ Inteligent'}
                  </button>
                ))}
              </div>
            </div>

            {/* Events List */}
            <div className="bg-gray-900/50 rounded-lg p-4 border border-gray-700">
              <h3 className="text-white font-semibold mb-3">🗓️ Evenimente</h3>
              <div className="text-center py-8">
                <div className="text-gray-400 text-sm">📅</div>
                <p className="text-gray-400 text-xs mt-2">Aucun événement pour le moment</p>
              </div>
            </div>

            {/* Add Event Button */}
            <button className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded font-semibold transition-colors">
              ➕ Ajouter événement
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
