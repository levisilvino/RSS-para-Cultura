export interface Edital {
    id: number;
    nome: string;
    link: string;
    data_publicacao: string;
    data_vencimento: string | null;
    categoria: string | null;
    descricao: string | null;
    fonte: string;
}

export interface EditalFilters {
    search: string;
    categoria: string;
    dataInicio: string;
    dataFim: string;
}
