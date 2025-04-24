import { useState, useEffect } from 'react';
import { caixaService, adaptImovelData, Imovel } from '@/services/caixaService';

export const useImoveis = (page: number = 1) => {
  const [imoveis, setImoveis] = useState<Imovel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalPages, setTotalPages] = useState(0);
  const [totalItems, setTotalItems] = useState(0);

  useEffect(() => {
    const fetchImoveis = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await caixaService.getImoveis(page);
        setImoveis(response.results.map(adaptImovelData));
        setTotalItems(response.count);
        setTotalPages(Math.ceil(response.count / 20)); // Assumindo 20 itens por página
      } catch (err) {
        setError('Erro ao carregar imóveis. Por favor, tente novamente mais tarde.');
        console.error('Erro ao buscar imóveis:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchImoveis();
  }, [page]);

  return { 
    imoveis, 
    loading, 
    error, 
    totalPages,
    totalItems,
    currentPage: page
  };
}; 