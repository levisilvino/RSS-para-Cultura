import { type FC, useState, useEffect } from 'react';
import { Header } from './components/Header';
import { FilterBar } from './components/FilterBar';
import { EditalList } from './components/EditalList';
import { EditalPreview } from './components/EditalPreview';
import { SourceManager } from './components/SourceManager';
import { Settings } from 'lucide-react';
import { Edital, EditalFilters } from './types';

const App: FC = () => {
  const [editais, setEditais] = useState<Edital[]>([]);
  const [selectedEdital, setSelectedEdital] = useState<Edital | null>(null);
  const [showSourceManager, setShowSourceManager] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<EditalFilters>({
    search: '',
    categoria: '',
    dataInicio: '',
    dataFim: ''
  });

  useEffect(() => {
    fetchEditais();
  }, [filters]);

  const fetchEditais = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filters.categoria) params.append('categoria', filters.categoria);
      if (filters.search) params.append('search', filters.search);
      if (filters.dataInicio) params.append('data_inicio', filters.dataInicio);
      if (filters.dataFim) params.append('data_fim', filters.dataFim);

      const response = await fetch(`/api/editais?${params.toString()}`);
      if (!response.ok) throw new Error('Falha ao carregar editais');
      
      const data = await response.json();
      setEditais(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar editais');
      setEditais([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      
      <div className="container mx-auto px-4 py-6">
        <div className="flex justify-between items-center mb-6">
          <FilterBar filters={filters} onFilterChange={setFilters} />
          <button
            onClick={() => setShowSourceManager(!showSourceManager)}
            className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            <Settings className="h-5 w-5 mr-2" />
            Gerenciar Fontes
          </button>
        </div>

        {showSourceManager ? (
          <SourceManager />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {loading ? (
              <div className="col-span-3 flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
              </div>
            ) : error ? (
              <div className="col-span-3 text-center text-red-600">{error}</div>
            ) : (
              <>
                <div className="lg:col-span-1">
                  <EditalList
                    editais={editais}
                    selectedEdital={selectedEdital}
                    onSelectEdital={setSelectedEdital}
                  />
                </div>
                <div className="lg:col-span-2">
                  {selectedEdital && <EditalPreview edital={selectedEdital} />}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;