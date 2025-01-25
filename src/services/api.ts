import axios from 'axios';
import { Edital } from '../types';

const api = axios.create({
    baseURL: '/api'
});

export const getEditais = async (params: Record<string, string>) => {
    const response = await api.get<Edital[]>('/editais', { params });
    return response.data;
};

export const getCategorias = async () => {
    const response = await api.get<string[]>('/categorias');
    return response.data;
};
