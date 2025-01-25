import React from 'react';
import { Calendar, Clock } from 'lucide-react';
import { Edital } from '../types/edital';

interface EditalListItemProps {
  edital: Edital;
  isSelected: boolean;
  onClick: () => void;
}

function EditalListItem({ edital, isSelected, onClick }: EditalListItemProps) {
  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('pt-BR');
  };

  const getDaysUntilDeadline = (date: Date) => {
    const today = new Date();
    const deadline = new Date(date);
    const diffTime = deadline.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const daysLeft = getDaysUntilDeadline(edital.dataVencimento);
  const isUrgent = daysLeft <= 7;

  return (
    <div
      onClick={onClick}
      className={`p-4 border-b cursor-pointer hover:bg-purple-50 transition-colors ${
        isSelected ? 'bg-purple-100' : 'bg-white'
      }`}
    >
      <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">{edital.nome}</h3>
      <div className="flex items-center justify-between">
        <span className="inline-block bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full">
          {edital.categoria}
        </span>
        <div className="flex items-center text-gray-500 text-sm">
          <Clock className="h-3 w-3 mr-1" />
          <span className={isUrgent ? 'text-red-600 font-medium' : ''}>
            {daysLeft} dias restantes
          </span>
        </div>
      </div>
    </div>
  );
}

interface EditalListProps {
  editais: Edital[];
  selectedEditalId: number | null;
  onSelectEdital: (edital: Edital) => void;
}

export function EditalList({ editais, selectedEditalId, onSelectEdital }: EditalListProps) {
  return (
    <div className="bg-white h-[calc(100vh-8rem)] overflow-y-auto">
      {editais.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-gray-500 p-4">
          <Calendar className="h-12 w-12 mb-2" />
          <p className="text-center">Nenhum edital encontrado com os filtros selecionados.</p>
        </div>
      ) : (
        editais.map((edital) => (
          <EditalListItem
            key={edital.id}
            edital={edital}
            isSelected={edital.id === selectedEditalId}
            onClick={() => onSelectEdital(edital)}
          />
        ))
      )}
    </div>
  );
}