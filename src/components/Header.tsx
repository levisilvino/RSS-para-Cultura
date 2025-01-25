import React from 'react';
import { Bell, Search } from 'lucide-react';

interface HeaderProps {
  onSearch: (term: string) => void;
}

export function Header({ onSearch }: HeaderProps) {
  return (
    <header className="bg-purple-700 text-white sticky top-0 z-10 shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Bell className="h-7 w-7" />
            <h1 className="text-2xl font-bold">Cultura Alerta</h1>
          </div>
          <div className="flex items-center space-x-4">
            <div className="relative">
              <input
                type="search"
                placeholder="Buscar editais..."
                onChange={(e) => onSearch(e.target.value)}
                className="w-64 px-4 py-2 rounded-full text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-300 transition-shadow"
              />
              <Search className="absolute right-3 top-2.5 h-5 w-5 text-gray-400 pointer-events-none" />
            </div>
            <button className="bg-purple-600 hover:bg-purple-500 px-4 py-2 rounded-full transition-colors duration-200 flex items-center space-x-2">
              <Bell className="h-4 w-4" />
              <span>Criar Alerta</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}