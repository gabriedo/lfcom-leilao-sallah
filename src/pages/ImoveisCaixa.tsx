import React, { useEffect, useState } from 'react';
import { ScraphubService, ScraphubProperty } from '../services/scraphubService';
import PropertyCard from '../components/PropertyCard';
import { Pagination } from '../components/Pagination';
import Layout from "@/components/Layout";
import PropertyFilters from "@/components/PropertyFilters";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

export default function ImoveisCaixa() {
  const [properties, setProperties] = useState<ScraphubProperty[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const [filters, setFilters] = useState({
    cidade: "",
    estado: "",
    tipo: "",
    modalidade: "",
    min_valor: 0,
    max_valor: 100000000,
    quartos: 0,
    vagas: 0,
    min_area: 0,
    max_area: 10000,
    aceita_financiamento: false,
    aceita_FGTS: false,
    min_desconto: 0
  });

  const fetchProperties = async (page: number = 1) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await ScraphubService.getInstance().getProperties(page);
      setProperties(response.results);
      setTotalPages(Math.ceil(response.count / 20));
      setTotalItems(response.count);
      setCurrentPage(page);
    } catch (err) {
      console.error('Erro ao buscar imóveis:', err);
      setError('Erro ao carregar imóveis. Por favor, tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };

  const searchProperties = async (page: number = 1) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await ScraphubService.getInstance().searchProperties({
        ...filters,
        page,
        limit: 20
      });
      
      setProperties(response.results);
      setTotalPages(Math.ceil(response.count / 20));
      setTotalItems(response.count);
      setCurrentPage(page);
    } catch (err) {
      console.error('Erro ao buscar imóveis:', err);
      setError('Erro ao carregar imóveis. Por favor, tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProperties();
  }, []);

  const handlePageChange = (page: number) => {
    if (Object.values(filters).some(value => value !== 0 && value !== "" && value !== false)) {
      searchProperties(page);
    } else {
      fetchProperties(page);
    }
  };

  const handleClearFilters = () => {
    setFilters({
      cidade: "",
      estado: "",
      tipo: "",
      modalidade: "",
      min_valor: 0,
      max_valor: 100000000,
      quartos: 0,
      vagas: 0,
      min_area: 0,
      max_area: 10000,
      aceita_financiamento: false,
      aceita_FGTS: false,
      min_desconto: 0
    });
    fetchProperties();
  };

  if (loading && properties.length === 0) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="flex flex-col items-center justify-center min-h-screen">
          <div className="text-red-500 text-lg mb-4">{error}</div>
          <Button onClick={() => fetchProperties()}>Tentar Novamente</Button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="bg-background py-12">
        <div className="container mx-auto px-4">
          <div className="mb-10 text-center">
            <h1 className="text-3xl font-bold mb-2">Imóveis da Caixa Econômica Federal</h1>
            <p className="text-lg text-muted-foreground">
              Encontre as melhores oportunidades de imóveis da Caixa com descontos exclusivos
            </p>
          </div>

          <PropertyFilters filters={filters} setFilters={setFilters} onSearch={() => searchProperties(1)} />

          <div className="flex justify-between items-center mt-4">
            <p className="text-muted-foreground">
              {totalItems} imóveis encontrados
            </p>
            <Button
              className="bg-red-500 hover:bg-red-600 text-white"
              onClick={handleClearFilters}
            >
              Limpar Filtros
            </Button>
          </div>

          {properties.length > 0 ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
                {properties.map((property) => (
                  <PropertyCard key={property.id} property={property} />
                ))}
              </div>

              <div className="mt-8">
                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  onPageChange={handlePageChange}
                />
              </div>
            </>
          ) : (
            <div className="text-center py-16">
              <h3 className="text-xl font-medium mb-2">Nenhum imóvel encontrado</h3>
              <p className="text-muted-foreground">
                Tente modificar os filtros para encontrar mais resultados.
              </p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
