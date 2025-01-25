import React from 'react';
import { Calendar, ExternalLink, Clock } from 'lucide-react';
import { Edital } from '../types/edital';

interface EditalPreviewProps {
  edital: Edital | null;
}

export function EditalPreview({ edital }: EditalPreviewProps) {
  if (!edital) {
    return (
      <div className="h-[calc(100vh-8rem)] flex items-center justify-center bg-gray-50 text-gray-500">
        <div className="text-center">
          <Calendar className="h-12 w-12 mx-auto mb-2" />
          <p>Selecione um edital para visualizar</p>
        </div>
      </div>
    );
  }

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
    <div className="h-[calc(100vh-8rem)] overflow-y-auto bg-white p-8">
      <div className="max-w-3xl mx-auto">
        <div className="flex justify-between items-start mb-6">
          <h2 className="text-2xl font-bold text-gray-900">{edital.nome}</h2>
          <a
            href={edital.link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center text-purple-600 hover:text-purple-500 transition-colors"
          >
            <span className="mr-2">Abrir edital</span>
            <ExternalLink className="h-5 w-5" />
          </a>
        </div>

        <div className="bg-purple-50 rounded-lg p-6 mb-8">
          <div className="grid grid-cols-2 gap-6">
            <div>
              <div className="text-sm text-gray-500 mb-1">Categoria</div>
              <div className="font-medium text-purple-800">{edital.categoria}</div>
            </div>
            <div>
              <div className="text-sm text-gray-500 mb-1">Data de Publicação</div>
              <div className="font-medium flex items-center">
                <Calendar className="h-4 w-4 mr-2" />
                {formatDate(edital.dataPublicacao)}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500 mb-1">Data de Vencimento</div>
              <div className="font-medium flex items-center">
                <Calendar className="h-4 w-4 mr-2" />
                {formatDate(edital.dataVencimento)}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-500 mb-1">Prazo Restante</div>
              <div className={`font-medium flex items-center ${isUrgent ? 'text-red-600' : 'text-gray-900'}`}>
                <Clock className="h-4 w-4 mr-2" />
                {daysLeft} dias restantes
              </div>
            </div>
          </div>
        </div>

        <div className="prose max-w-none">
          <div className="whitespace-pre-wrap text-gray-600 leading-relaxed">
            {edital.descricao}
          </div>
        </div>
      </div>
    </div>
  );
}