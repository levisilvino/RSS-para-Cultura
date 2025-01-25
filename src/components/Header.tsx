import { type FC } from 'react';
import { AlertCircle } from 'lucide-react';

export const Header: FC = () => {
  return (
    <header className="bg-white shadow">
      <div className="container mx-auto px-4 py-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Cultura Alerta</h1>
            <p className="mt-1 text-gray-600">
              Encontre editais e oportunidades para projetos culturais
            </p>
          </div>
          <div className="mt-4 md:mt-0">
            <a
              href="https://github.com/levisilvino/PsiGabriel"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
            >
              <AlertCircle className="h-4 w-4 mr-1" />
              Sobre o projeto
            </a>
          </div>
        </div>
      </div>
    </header>
  );
};