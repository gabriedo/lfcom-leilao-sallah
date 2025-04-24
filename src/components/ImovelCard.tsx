import React from 'react';
import { Imovel } from '@/services/caixaService';
import { Link } from 'react-router-dom';

interface ImovelCardProps {
  imovel: Imovel;
}

export const ImovelCard: React.FC<ImovelCardProps> = ({ imovel }) => {
  const { data } = imovel;
  const primeiraImagem = data.images[0] || '';

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
      <Link to={`/imovel/${imovel.id}`}>
        <div className="relative h-48">
          {primeiraImagem ? (
            <img
              src={primeiraImagem}
              alt={data.title}
              className="w-full h-full object-cover"
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full bg-gray-200 flex items-center justify-center">
              <span className="text-gray-500">Sem imagem</span>
            </div>
          )}
        </div>

        <div className="p-4">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            {data.title}
          </h3>
          
          <div className="text-gray-600 mb-2">
            <p>{data.address}</p>
            <p>{data.city} - {data.state}</p>
          </div>

          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-gray-500">{data.type}</span>
            <span className="text-sm text-gray-500">{data.modality}</span>
          </div>

          <div className="flex justify-between items-center">
            <span className="text-lg font-bold text-primary">
              R$ {data.sale_value}
            </span>
            {data.desconto && (
              <span className="text-sm text-green-600">
                {data.desconto}% de desconto
              </span>
            )}
          </div>

          <div className="mt-2 flex gap-4 text-sm text-gray-500">
            {data.quartos && <span>{data.quartos} quartos</span>}
            {data.banheiros && <span>{data.banheiros} banheiros</span>}
            {data.garagem && <span>{data.garagem} vagas</span>}
          </div>
        </div>
      </Link>
    </div>
  );
}; 