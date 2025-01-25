import React from 'react';
import { Calendar, ExternalLink } from 'lucide-react';
import { Edital } from '../types/edital';

interface EditalCardProps {
  edital: Edital;
}

export function EditalCard({ edital }: EditalCardProps) {
  const formatDate = (date: Date) => {
    return new Date(date).toLocaleDateString('pt-BR');
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">{edital.nome}</h3>
          <span className="inline-block bg-purple-100 text-purple-800 text-sm px-3 py-1 rounded-full">
            {edital.categoria}
          </span>
        </div>
        <a
          href={edital.link}
          target="_blank"
          rel="noopener noreferrer"
          className="text-purple-600 hover:text-purple-500"
        >
          <ExternalLink className="h-5 w-5" />
        </a>
      </div>
      
      <div className="mt-4 flex items-center space-x-4 text-gray-600">
        <div className="flex items-center">
          <Calendar className="h-4 w-4 mr-2" />
          <span className="text-sm">
            Publicado: {formatDate(edital.dataPublicacao)}
          </span>
        </div>
        <div className="flex items-center">
          <Calendar className="h-4 w-4 mr-2" />
          <span className="text-sm">
            Vence: {formatDate(edital.dataVencimento)}
          </span>
        </div>
      </div>
    </div>
  );
}