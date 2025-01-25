import React, { useState, useMemo } from 'react';
import { Header } from './components/Header';
import { FilterBar } from './components/FilterBar';
import { EditalList } from './components/EditalList';
import { EditalPreview } from './components/EditalPreview';

// Mock data for demonstration
const mockEditais = [
  {
    id: 1,
    nome: "Prêmio Nacional das Artes 2024",
    link: "https://example.com/edital1",
    dataPublicacao: new Date("2024-03-01"),
    dataVencimento: new Date("2024-04-30"),
    categoria: "Artes Visuais",
    descricao: `O Prêmio Nacional das Artes 2024 tem como objetivo reconhecer e premiar artistas visuais que contribuem para o desenvolvimento e inovação das artes no Brasil.

    Categorias de Premiação:
    - Pintura
    - Escultura
    - Fotografia
    - Arte Digital
    
    Valor do Prêmio:
    - 1º lugar: R$ 50.000,00
    - 2º lugar: R$ 30.000,00
    - 3º lugar: R$ 20.000,00
    
    Requisitos:
    - Ser artista brasileiro ou naturalizado
    - Ter mais de 18 anos
    - Apresentar portfólio com até 10 obras
    - Obras devem ter sido produzidas nos últimos 2 anos`
  },
  {
    id: 2,
    nome: "Festival de Música Independente",
    link: "https://example.com/edital2",
    dataPublicacao: new Date("2024-03-05"),
    dataVencimento: new Date("2024-05-15"),
    categoria: "Música",
    descricao: `O Festival de Música Independente é uma iniciativa que visa dar visibilidade e suporte a artistas independentes do cenário musical brasileiro.

    Modalidades:
    - Shows ao vivo
    - Gravação de EP
    - Videoclipe
    
    Benefícios:
    - Gravação profissional
    - Distribuição digital
    - Mentoria com profissionais do mercado
    
    Critérios de Seleção:
    - Originalidade
    - Qualidade técnica
    - Potencial de mercado
    - Diversidade musical`
  },
  {
    id: 3,
    nome: "Edital de Fomento ao Teatro",
    link: "https://example.com/edital3",
    dataPublicacao: new Date("2024-03-10"),
    dataVencimento: new Date("2024-06-01"),
    categoria: "Teatro",
    descricao: `O Edital de Fomento ao Teatro visa apoiar a produção teatral brasileira, com foco em montagens inéditas e circulação de espetáculos.

    Linhas de Apoio:
    - Montagem de espetáculos
    - Circulação de obras
    - Pesquisa e desenvolvimento
    
    Valor do Apoio:
    - Até R$ 100.000,00 por projeto
    
    Contrapartidas:
    - Apresentações gratuitas
    - Oficinas em escolas públicas
    - Documentação do processo
    
    Público-alvo:
    - Companhias de teatro
    - Grupos independentes
    - Artistas solo`
  }
];

export default function App() {
  const [selectedEdital, setSelectedEdital] = useState(mockEditais[0]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategoria, setSelectedCategoria] = useState('');
  const [selectedPrazo, setSelectedPrazo] = useState('');

  const filteredEditais = useMemo(() => {
    return mockEditais.filter(edital => {
      const matchesSearch = edital.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          edital.descricao.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesCategoria = !selectedCategoria || edital.categoria === selectedCategoria;
      
      const matchesPrazo = () => {
        if (!selectedPrazo) return true;
        const hoje = new Date();
        const diasAteVencimento = Math.ceil((edital.dataVencimento.getTime() - hoje.getTime()) / (1000 * 60 * 60 * 24));
        
        switch (selectedPrazo) {
          case '7': return diasAteVencimento <= 7;
          case '15': return diasAteVencimento <= 15;
          case '30': return diasAteVencimento <= 30;
          default: return true;
        }
      };

      return matchesSearch && matchesCategoria && matchesPrazo();
    });
  }, [searchTerm, selectedCategoria, selectedPrazo]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header onSearch={setSearchTerm} />
      <FilterBar
        onCategoriaChange={setSelectedCategoria}
        onPrazoChange={setSelectedPrazo}
        selectedCategoria={selectedCategoria}
        selectedPrazo={selectedPrazo}
      />
      
      <main className="container mx-auto px-4 py-4">
        <div className="grid grid-cols-12 gap-4 bg-white rounded-lg shadow-sm">
          <div className="col-span-4 border-r">
            <EditalList
              editais={filteredEditais}
              selectedEditalId={selectedEdital?.id}
              onSelectEdital={setSelectedEdital}
            />
          </div>
          <div className="col-span-8">
            <EditalPreview edital={selectedEdital} />
          </div>
        </div>
      </main>
    </div>
  );
}