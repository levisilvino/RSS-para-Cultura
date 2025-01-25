import React from 'react';
import { EditalFilters } from '../types';

interface Props {
    filters: EditalFilters;
    categorias: string[];
    onFilterChange: (filters: EditalFilters) => void;
}

export const EditalFilters: React.FC<Props> = ({ filters, categorias, onFilterChange }) => {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        onFilterChange({ ...filters, [name]: value });
    };

    return (
        <div className="bg-white p-4 rounded-lg shadow mb-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                    <label htmlFor="search" className="block text-sm font-medium text-gray-700">
                        Pesquisar
                    </label>
                    <input
                        type="text"
                        name="search"
                        id="search"
                        value={filters.search}
                        onChange={handleChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                        placeholder="Buscar editais..."
                    />
                </div>

                <div>
                    <label htmlFor="categoria" className="block text-sm font-medium text-gray-700">
                        Categoria
                    </label>
                    <select
                        name="categoria"
                        id="categoria"
                        value={filters.categoria}
                        onChange={handleChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    >
                        <option value="">Todas as categorias</option>
                        {categorias.map((cat) => (
                            <option key={cat} value={cat}>
                                {cat}
                            </option>
                        ))}
                    </select>
                </div>

                <div>
                    <label htmlFor="dataInicio" className="block text-sm font-medium text-gray-700">
                        Data Início
                    </label>
                    <input
                        type="date"
                        name="dataInicio"
                        id="dataInicio"
                        value={filters.dataInicio}
                        onChange={handleChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    />
                </div>

                <div>
                    <label htmlFor="dataFim" className="block text-sm font-medium text-gray-700">
                        Data Fim
                    </label>
                    <input
                        type="date"
                        name="dataFim"
                        id="dataFim"
                        value={filters.dataFim}
                        onChange={handleChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    />
                </div>
            </div>
        </div>
    );
};
