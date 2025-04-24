import React from 'react';

export default function FeatureHighlights() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-semibold mb-4">Análise Avançada</h3>
        <p className="text-gray-600">
          Visualize dados detalhados e insights sobre os leilões em tempo real.
        </p>
      </div>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-semibold mb-4">Monitoramento Inteligente</h3>
        <p className="text-gray-600">
          Acompanhe os leilões de interesse com alertas personalizados.
        </p>
      </div>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-semibold mb-4">Relatórios Personalizados</h3>
        <p className="text-gray-600">
          Gere relatórios detalhados com os dados mais relevantes para sua análise.
        </p>
      </div>
    </div>
  );
}
