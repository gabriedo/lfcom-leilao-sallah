import React, { useState } from 'react';
import { useImoveis } from '@/hooks/useImoveis';
import { ImovelCard } from './ImovelCard';
import { Pagination } from './Pagination';
import { LoadingSpinner } from './LoadingSpinner';
import { ErrorMessage } from './ErrorMessage';

export const ImovelList: React.FC = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const { imoveis, loading, error, totalPages } = useImoveis(currentPage);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {imoveis.map((imovel) => (
          <ImovelCard key={imovel.id} imovel={imovel} />
        ))}
      </div>
      
      {totalPages > 1 && (
        <div className="mt-8">
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setCurrentPage}
          />
        </div>
      )}
    </div>
  );
}; 