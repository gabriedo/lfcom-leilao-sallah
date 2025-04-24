import React from 'react';
import { ImovelList } from '@/components/ImovelList';

export const Home: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold text-gray-800">Imóveis Caixa</h1>
        </div>
      </header>

      <main>
        <ImovelList />
      </main>
    </div>
  );
}; 