import { type FC, useState } from 'react';
import { updateFeeds, clearCache } from '../services/api';
import { FilterBar } from './FilterBar';
import { Settings, RefreshCw, Trash2 } from 'lucide-react';
import { EditalFilters } from '../types';

interface FilterSectionProps {
  filters: EditalFilters;
  onFilterChange: (filters: EditalFilters) => void;
  onSourceManagerClick: () => void;
}

export const FilterSection: FC<FilterSectionProps> = ({ 
  filters, 
  onFilterChange, 
  onSourceManagerClick 
}) => {
  const [updating, setUpdating] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [status, setStatus] = useState<{ type: 'success' | 'error' | null; message: string }>({
    type: null,
    message: ''
  });

  const showStatus = (type: 'success' | 'error', message: string) => {
    setStatus({ type, message });
    setTimeout(() => setStatus({ type: null, message: '' }), 5000);
  };

  const handleUpdate = async () => {
    try {
      setUpdating(true);
      const result = await updateFeeds();
      if (result.success) {
        showStatus('success', result.message);
        window.location.reload();
      } else {
        showStatus('error', result.message);
      }
    } catch (error) {
      showStatus('error', 'Erro ao atualizar feeds. Tente novamente.');
    } finally {
      setUpdating(false);
    }
  };

  const handleClearCache = async () => {
    if (window.confirm('Tem certeza que deseja limpar todos os editais salvos? Esta ação não pode ser desfeita.')) {
      try {
        setClearing(true);
        const result = await clearCache();
        if (result.success) {
          showStatus('success', result.message);
          window.location.reload();
        } else {
          showStatus('error', result.message);
        }
      } catch (error) {
        showStatus('error', 'Erro ao limpar cache. Tente novamente.');
      } finally {
        setClearing(false);
      }
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex-grow">
          <FilterBar filters={filters} onFilterChange={onFilterChange} />
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={handleUpdate}
            disabled={updating || clearing}
            className={`flex items-center px-4 py-2 rounded text-white transition-colors ${
              updating 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-blue-500 hover:bg-blue-600'
            }`}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${updating ? 'animate-spin' : ''}`} />
            {updating ? 'Atualizando...' : 'Atualizar Feeds'}
          </button>
          
          <button
            onClick={handleClearCache}
            disabled={updating || clearing}
            className={`flex items-center px-4 py-2 rounded text-white transition-colors ${
              clearing 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-red-500 hover:bg-red-600'
            }`}
          >
            <Trash2 className="h-4 w-4 mr-2" />
            {clearing ? 'Limpando...' : 'Limpar Cache'}
          </button>

          <button
            onClick={onSourceManagerClick}
            className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            <Settings className="h-4 w-4 mr-2" />
            Gerenciar Fontes
          </button>
        </div>
      </div>
      
      {status.type && (
        <div
          className={`p-4 rounded ${
            status.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          }`}
        >
          {status.message}
        </div>
      )}
    </div>
  );
};
