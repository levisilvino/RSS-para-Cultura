import { type FC, useEffect, useState } from 'react';
import { Filter, X } from 'lucide-react';
import { EditalFilters } from '../types';
import { getCategorias } from '../services/api';

interface FilterBarProps {
  filters: EditalFilters;
  onFilterChange: (filters: EditalFilters) => void;
}

export const FilterBar: FC<FilterBarProps> = ({ filters, onFilterChange }) => {
  const [categorias, setCategorias] = useState<string[]>([]);

  useEffect(() => {
    fetchCategorias();
  }, []);

  const fetchCategorias = async () => {
    try {
      const data = await getCategorias();
      setCategorias(data);
    } catch (err) {
      console.error('Erro ao carregar categorias:', err);
    }
  };

  const handleChange = (field: keyof EditalFilters, value: string) => {
    onFilterChange({
      ...filters,
      [field]: value
    });
  };

  const clearFilters = () => {
    onFilterChange({
      search: '',
      categoria: '',
      dataInicio: '',
      dataFim: ''
    });
  };

  const hasActiveFilters = Object.values(filters).some(value => value !== '');

  return (
    <div className="bg-white shadow-sm rounded-lg p-4 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900 flex items-center">
          <Filter className="h-5 w-5 mr-2" />
          Filtros
        </h3>
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="text-sm text-gray-500 hover:text-gray-700 flex items-center"
          >
            <X className="h-4 w-4 mr-1" />
            Limpar filtros
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
            Pesquisar
          </label>
          <input
            type="text"
            id="search"
            value={filters.search}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
            placeholder="Buscar editais..."
            onChange={(e) => handleChange('search', e.target.value)}
          />
        </div>

        <div>
          <label htmlFor="categoria" className="block text-sm font-medium text-gray-700 mb-1">
            Categoria
          </label>
          <select
            id="categoria"
            value={filters.categoria}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
            onChange={(e) => handleChange('categoria', e.target.value)}
          >
            <option value="">Todas as categorias</option>
            {categorias.map((categoria) => (
              <option key={categoria} value={categoria}>
                {categoria}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="dataInicio" className="block text-sm font-medium text-gray-700 mb-1">
            Data Início
          </label>
          <input
            type="date"
            id="dataInicio"
            value={filters.dataInicio}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
            onChange={(e) => handleChange('dataInicio', e.target.value)}
          />
        </div>

        <div>
          <label htmlFor="dataFim" className="block text-sm font-medium text-gray-700 mb-1">
            Data Fim
          </label>
          <input
            type="date"
            id="dataFim"
            value={filters.dataFim}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-purple-500 focus:ring-purple-500 sm:text-sm"
            onChange={(e) => handleChange('dataFim', e.target.value)}
          />
        </div>
      </div>
    </div>
  );
};