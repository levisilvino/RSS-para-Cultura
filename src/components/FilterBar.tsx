import React from 'react';
import { Filter, X } from 'lucide-react';

interface FilterBarProps {
  onCategoriaChange: (categoria: string) => void;
  onPrazoChange: (prazo: string) => void;
  selectedCategoria: string;
  selectedPrazo: string;
}

export function FilterBar({
  onCategoriaChange,
  onPrazoChange,
  selectedCategoria,
  selectedPrazo
}: FilterBarProps) {
  const hasFilters = selectedCategoria || selectedPrazo;

  return (
    <div className="bg-white shadow-sm sticky top-16 z-10">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center space-x-4">
          <div className="flex items-center text-gray-600">
            <Filter className="h-4 w-4 mr-2" />
            <span className="text-sm font-medium">Filtros:</span>
          </div>
          
          <select
            value={selectedCategoria}
            onChange={(e) => onCategoriaChange(e.target.value)}
            className="bg-white border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-300 transition-shadow cursor-pointer"
          >
            <option value="">Todas as categorias</option>
            <option value="Música">Música</option>
            <option value="Teatro">Teatro</option>
            <option value="Dança">Dança</option>
            <option value="Artes Visuais">Artes Visuais</option>
            <option value="Literatura">Literatura</option>
          </select>
          
          <select
            value={selectedPrazo}
            onChange={(e) => onPrazoChange(e.target.value)}
            className="bg-white border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-300 transition-shadow cursor-pointer"
          >
            <option value="">Todos os prazos</option>
            <option value="7">Próximos 7 dias</option>
            <option value="15">Próximos 15 dias</option>
            <option value="30">Próximos 30 dias</option>
          </select>

          {hasFilters && (
            <button
              onClick={() => {
                onCategoriaChange('');
                onPrazoChange('');
              }}
              className="text-purple-600 hover:text-purple-500 font-medium text-sm flex items-center transition-colors"
            >
              <X className="h-4 w-4 mr-1" />
              Limpar filtros
            </button>
          )}
        </div>
      </div>
    </div>
  );
}