export interface Edital {
  id: number;
  nome: string;
  link: string;
  dataPublicacao: Date;
  dataVencimento: Date;
  categoria: string;
  descricao: string;
}