import { type FC } from 'react';
import { Calendar, Clock } from 'lucide-react';
import { Edital } from '../types';

interface EditalListItemProps {
  edital: Edital;
  isSelected: boolean;
  onClick: () => void;
}

const EditalListItem: FC<EditalListItemProps> = ({ edital, isSelected, onClick }) => {
  const getDaysUntilDeadline = (dateStr: string | null) => {
    if (!dateStr) return null;
    const today = new Date();
    const deadline = new Date(dateStr);
    const diffTime = deadline.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const daysLeft = edital.data_vencimento ? getDaysUntilDeadline(edital.data_vencimento) : null;
  const isUrgent = daysLeft !== null && daysLeft <= 7;

  return (
    <div
      onClick={onClick}
      className={`p-4 border-b cursor-pointer hover:bg-purple-50 transition-colors ${
        isSelected ? 'bg-purple-100' : 'bg-white'
      }`}
    >
      <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">{edital.nome}</h3>
      <div className="flex items-center justify-between">
        {edital.categoria && (
          <span className="inline-block bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full">
            {edital.categoria}
          </span>
        )}
        {daysLeft !== null && (
          <div className="flex items-center text-gray-500 text-sm">
            <Clock className="h-3 w-3 mr-1" />
            <span className={isUrgent ? 'text-red-600 font-medium' : ''}>
              {daysLeft} dias restantes
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

interface EditalListProps {
  editais: Edital[];
  selectedEdital: Edital | null;
  onSelectEdital: (edital: Edital) => void;
}

export const EditalList: FC<EditalListProps> = ({ editais, selectedEdital, onSelectEdital }) => {
  if (editais.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
        <Calendar className="h-12 w-12 mx-auto mb-2" />
        <p>Nenhum edital encontrado</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow divide-y">
      {editais.map((edital) => (
        <EditalListItem
          key={edital.id}
          edital={edital}
          isSelected={selectedEdital?.id === edital.id}
          onClick={() => onSelectEdital(edital)}
        />
      ))}
    </div>
  );
};