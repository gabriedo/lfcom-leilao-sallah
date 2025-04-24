import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { MapPin, Bed, Bath, Car, Ruler, Calendar, FileText, Tag, Home, Building2, LandPlot } from "lucide-react";
import { format, parseISO } from "date-fns";
import { ptBR } from "date-fns/locale";
import { getApiUrl, getRequestOptions } from "@/config/api";
import { Property } from "@/types/property";
import { PropertyImages } from "@/components/PropertyImages";
import { formatCurrency } from "@/utils/format";

export default function ImovelDetalhes() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [property, setProperty] = useState<Property | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    const fetchProperty = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const url = getApiUrl(`/items/2/${id}`);
        const response = await fetch(url, getRequestOptions());

        if (!response.ok) {
          throw new Error(`Erro ao buscar imóvel: ${response.status}`);
        }

        const data = await response.json();
        setProperty(data);
      } catch (err) {
        console.error("Erro ao buscar imóvel:", err);
        setError(err instanceof Error ? err.message : "Erro ao buscar imóvel");
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchProperty();
    }
  }, [id]);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Carregando detalhes do imóvel...</p>
        </div>
      </div>
    );
  }

  if (error || !property) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h3 className="text-xl font-medium mb-2 text-destructive">Erro ao carregar imóvel</h3>
          <p className="text-muted-foreground mb-4">{error}</p>
          <Button onClick={() => navigate(-1)}>Voltar</Button>
        </div>
      </div>
    );
  }

  const getEndDate = () => {
    let date: string | undefined;
    let label: string = '';
    
    const modality = property.data.modality || '';
    
    if (!modality) return { formatted: '', label: '' };
    
    switch(modality) {
      case 'Leilão SFI - Edital Único':
      case 'Leilão SFI':
        date = property.data.fim_2 || property.data.fim_1;
        label = property.data.fim_2 ? '2º Leilão' : '1º Leilão';
        break;
      case 'Licitação Aberta':
        date = property.data.fim_venda_online;
        label = 'Fim Licitação';
        break;
      case 'Venda Online':
        date = property.data.fim_venda_online;
        label = 'Fim Oferta';
        break;
      case 'Venda Direta Online':
        label = 'Compra Imediata';
        break;
      default:
        return { formatted: '', label: '' };
    }

    if (date) {
      try {
        return {
          formatted: format(parseISO(date), "dd/MM/yyyy", { locale: ptBR }),
          label
        };
      } catch (e) {
        console.error("Error formatting date:", e, date);
        return { formatted: date, label };
      }
    }
    
    return { formatted: '', label };
  };

  const endDate = getEndDate();

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Button onClick={() => navigate(-1)}>
          Voltar
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <PropertyImages propertyId={property.data.id} images={property.data.images} />
          
          <Card className="mt-6">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-2xl">{property.data.title}</CardTitle>
                <Badge variant="outline" className="text-lg">
                  {formatCurrency(property.data.sale_value)}
                </Badge>
              </div>
              <div className="flex items-center text-muted-foreground mt-2">
                <MapPin className="w-4 h-4 mr-1" />
                <span>{property.data.city}, {property.data.state}</span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="flex items-center">
                  <Bed className="w-4 h-4 mr-1" />
                  <span>{property.data.quartos} quartos</span>
                </div>
                <div className="flex items-center">
                  <Bath className="w-4 h-4 mr-1" />
                  <span>{property.data.banheiros} banheiros</span>
                </div>
                <div className="flex items-center">
                  <Car className="w-4 h-4 mr-1" />
                  <span>{property.data.garagem} vagas</span>
                </div>
                <div className="flex items-center">
                  <Ruler className="w-4 h-4 mr-1" />
                  <span>{property.data.total_area} m²</span>
                </div>
              </div>

              <Tabs value={activeTab} onChange={handleTabChange} aria-label="property details tabs">
                <TabsList className="mb-4">
                  <TabsTrigger value="descricao">Descrição</TabsTrigger>
                  <TabsTrigger value="detalhes">Detalhes</TabsTrigger>
                  <TabsTrigger value="documentos">Documentos</TabsTrigger>
                </TabsList>
                <TabsContent value="descricao">
                  <p className="text-muted-foreground">{property.data.description}</p>
                </TabsContent>
                <TabsContent value="detalhes">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium mb-2">Informações do Imóvel</h4>
                      <ul className="space-y-2 text-muted-foreground">
                        <li className="flex items-center">
                          <Home className="w-4 h-4 mr-2" />
                          <span>Tipo: {property.data.type}</span>
                        </li>
                        <li className="flex items-center">
                          <Tag className="w-4 h-4 mr-2" />
                          <span>Modalidade: {property.data.modality}</span>
                        </li>
                        <li className="flex items-center">
                          <Calendar className="w-4 h-4 mr-2" />
                          <span>{endDate.label}: {endDate.formatted}</span>
                        </li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Valores</h4>
                      <ul className="space-y-2 text-muted-foreground">
                        <li>Preço de Venda: {formatCurrency(property.data.sale_value)}</li>
                        <li>Preço de Avaliação: {formatCurrency(property.data.preco_avaliacao)}</li>
                        <li>Desconto: {property.data.desconto}%</li>
                      </ul>
                    </div>
                  </div>
                </TabsContent>
                <TabsContent value="documentos">
                  <div className="space-y-4">
                    {property.data.matricula_url && (
                      <div>
                        <h4 className="font-medium mb-2">Matrícula</h4>
                        <p className="text-muted-foreground mb-2">
                          Número: {property.data.matricula_number}
                        </p>
                        <Button asChild>
                          <a href={property.data.matricula_url} target="_blank" rel="noopener noreferrer">
                            Ver Matrícula
                          </a>
                        </Button>
                      </div>
                    )}
                    {property.data.edital_url && (
                      <div>
                        <h4 className="font-medium mb-2">Edital</h4>
                        <Button asChild>
                          <a href={property.data.edital_url} target="_blank" rel="noopener noreferrer">
                            Ver Edital
                          </a>
                        </Button>
                      </div>
                    )}
                    {property.data.regras_de_venda_url && (
                      <div>
                        <h4 className="font-medium mb-2">Regras de Venda</h4>
                        <Button asChild>
                          <a href={property.data.regras_de_venda_url} target="_blank" rel="noopener noreferrer">
                            Ver Regras
                          </a>
                        </Button>
                      </div>
                    )}
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Informações Adicionais</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-4">
                <li className="flex items-center">
                  <input
                    type="checkbox"
                    checked={property.data.aceita_financiamento === "true"}
                    readOnly
                    className="mr-2"
                  />
                  <span>Aceita Financiamento</span>
                </li>
                <li className="flex items-center">
                  <input
                    type="checkbox"
                    checked={property.data.aceita_FGTS === "true"}
                    readOnly
                    className="mr-2"
                  />
                  <span>Aceita FGTS</span>
                </li>
                <li className="flex items-center">
                  <input
                    type="checkbox"
                    checked={property.data.aceita_parcelamento === "true"}
                    readOnly
                    className="mr-2"
                  />
                  <span>Aceita Parcelamento</span>
                </li>
                <li className="flex items-center">
                  <input
                    type="checkbox"
                    checked={property.data.aceita_consorcio === "true"}
                    readOnly
                    className="mr-2"
                  />
                  <span>Aceita Consórcio</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Contato</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground mb-4">
                Para mais informações sobre este imóvel, entre em contato com a Caixa Econômica Federal.
              </p>
              <Button className="w-full" asChild>
                <a href={property.data.url} target="_blank" rel="noopener noreferrer">
                  Ver no Site da Caixa
                </a>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 