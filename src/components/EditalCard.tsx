import { type FC } from 'react';
import { Calendar, ExternalLink, Building2 } from 'lucide-react';
import { Edital } from '../types';

interface EditalCardProps {
  edital: Edital;
}

export const EditalCard: FC<EditalCardProps> = ({ edital }) => {
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'Não informado';
    return new Date(dateStr).toLocaleDateString('pt-BR');
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">{edital.nome}</h3>
          <div className="flex flex-wrap gap-2 mb-2">
            {edital.categoria && (
              <span className="inline-block bg-purple-100 text-purple-800 text-sm px-3 py-1 rounded-full">
                {edital.categoria}
              </span>
            )}
            <span className="inline-block bg-gray-100 text-gray-800 text-sm px-3 py-1 rounded-full flex items-center">
              <Building2 className="h-4 w-4 mr-1" />
              {edital.fonte}
            </span>
          </div>
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
            Publicado: {formatDate(edital.data_publicacao)}
          </span>
        </div>
        <div className="flex items-center">
          <Calendar className="h-4 w-4 mr-2" />
          <span className="text-sm">
            Vence: {formatDate(edital.data_vencimento)}
          </span>
        </div>
      </div>

      {edital.descricao && (
        <div className="mt-4 text-gray-600">
          <p className="text-sm line-clamp-3">{edital.descricao}</p>
        </div>
      )}
    </div>
  );
};