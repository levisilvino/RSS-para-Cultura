import { type FC } from 'react';
import { Calendar, ExternalLink, Clock, Building2 } from 'lucide-react';
import { Edital } from '../types';

interface EditalPreviewProps {
  edital: Edital | null;
}

export const EditalPreview: FC<EditalPreviewProps> = ({ edital }) => {
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

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'Não informado';
    return new Date(dateStr).toLocaleDateString('pt-BR');
  };

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
    <div className="h-[calc(100vh-8rem)] overflow-y-auto bg-white p-8">
      <div className="max-w-3xl mx-auto">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">{edital.nome}</h2>
            <div className="flex flex-wrap gap-2">
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
            className="flex items-center text-purple-600 hover:text-purple-500 transition-colors"
          >
            <span className="mr-2">Abrir edital</span>
            <ExternalLink className="h-5 w-5" />
          </a>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center text-gray-600">
              <Calendar className="h-5 w-5 mr-2" />
              <div>
                <p className="text-sm font-medium">Data de Publicação</p>
                <p className="text-lg">{formatDate(edital.data_publicacao)}</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center text-gray-600">
              <Clock className="h-5 w-5 mr-2" />
              <div>
                <p className="text-sm font-medium">Data de Vencimento</p>
                <p className="text-lg">
                  {formatDate(edital.data_vencimento)}
                  {daysLeft !== null && (
                    <span className={`ml-2 text-sm ${isUrgent ? 'text-red-600' : 'text-gray-500'}`}>
                      ({daysLeft} dias restantes)
                    </span>
                  )}
                </p>
              </div>
            </div>
          </div>
        </div>

        {edital.descricao && (
          <div className="prose max-w-none">
            <h3 className="text-lg font-semibold mb-4">Descrição do Edital</h3>
            <div className="bg-gray-50 p-6 rounded-lg">
              <p className="whitespace-pre-line">{edital.descricao}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};