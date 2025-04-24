import React, { useEffect, useState } from 'react';
import { usePagination } from '../hooks/usePagination';
import Pagination from './Pagination';
import { caixaService } from '../services/caixaService';

interface Imovel {
  id: number;
  titulo: string;
  preco: number;
  endereco: string;
}

const ImoveisList: React.FC = () => {
  const [imoveis, setImoveis] = useState<Imovel[]>([]);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { currentPage, goToPage } = usePagination({
    initialPage: 1,
    totalPages,
  });

  useEffect(() => {
    const fetchImoveis = async () => {
      try {
        setLoading(true);
        const response = await caixaService.getImoveis(currentPage);
        setImoveis(response.items);
        setTotalPages(response.total_pages);
        setError(null);
      } catch (err) {
        setError('Erro ao carregar imóveis. Tente novamente mais tarde.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchImoveis();
  }, [currentPage]);

  if (loading) {
    return <div className="flex justify-center items-center h-64">Carregando...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center p-4">{error}</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Imóveis da Caixa</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {imoveis.map((imovel) => (
          <div key={imovel.id} className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-2">{imovel.titulo}</h2>
            <p className="text-gray-600 mb-2">{imovel.endereco}</p>
            <p className="text-green-600 font-bold">
              R$ {imovel.preco.toLocaleString('pt-BR')}
            </p>
          </div>
        ))}
      </div>

      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={goToPage}
      />
    </div>
  );
};

export default ImoveisList; 