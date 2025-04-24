import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import Layout from "@/components/Layout";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "@/components/ui/carousel";
import { Bed, Bath, Maximize2, MapPin, CalendarDays, Home, Info, Building, Star, Download, ArrowUpRight, Calendar, FileText, Square } from "lucide-react";
import { Link } from "react-router-dom";
import { format, parseISO } from "date-fns";
import { ptBR } from "date-fns/locale";
import { useToast } from "@/hooks/use-toast";
import { API_CONFIG } from "@/config";
import { PropertyImages } from "@/components/PropertyImages";
import { formatCurrency } from "@/utils/format";

export interface Property {
  id: string;
  title: string;
  description: string;
  price: number;
  discount: number;
  originalPrice: number;
  observations: any;
  bedrooms?: number;
  bathrooms?: number;
  area?: number;
  features?: string[];
  auctionDate?: {
    firstAuction: string | null;
    secondAuction: string | null;
    onlineSale: string | null;
  };
  auctionEndDate?: string;
  minimumBid?: number;
  propertyType?: string;
  address: {
    street: string;
    neighborhood: string;
    city: string;
    state: string;
    zipcode: string;
    lat?: number;
    lng?: number;
    number?: string;
    zipCode?: string;
  };
  details?: {
    area: number;
    bedrooms: number;
    bathrooms: number;
    parkingSpots: number;
  };
  images: string[];
  modality?: string;
  modalityColor?: string;
  financing: {
    downPayment: number;
    installment: number;
    term: number;
    acceptsFinancing?: boolean;
    acceptsFGTS?: boolean;
    acceptsInstallments?: boolean;
    acceptsConsortium?: boolean;
  };
  status?: string;
  isAuction?: boolean;
  createdAt?: string;
  updatedAt?: string;
  registryNumber?: string;
  propertyRegistration?: string;
  registryUrl?: string;
  editalUrl?: string;
  salesRulesUrl?: string;
  url?: string;
  similarProperties?: Property[];
  acceptsFinancing?: boolean;
  acceptsFGTS?: boolean;
  acceptsInstallments?: boolean;
  acceptsConsortium?: boolean;
  urlCaixa?: string;
  reportUrl?: string;
}

// Function to fetch property from API
const fetchProperty = async (id: string): Promise<Property> => {
  try {
    console.log(`Buscando imóvel com ID: ${id}`);
    
    // Usar a API para buscar dados do imóvel
    const apiUrl = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.PROPERTIES}/${id}`;
    const requestOptions = API_CONFIG.getRequestOptions();
    
    const response = await fetch(apiUrl, requestOptions);
    
    if (!response.ok) {
      throw new Error(`Erro ao buscar imóvel: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Verificar se dados existem
    if (!data || !data.results || !Array.isArray(data.results)) {
      throw new Error("Dados de imóveis indisponíveis");
    }
    
    // Encontrar o imóvel específico pelo ID
    const propertyData = data.results.find((p: any) => String(p.id) === String(id));
    
    if (!propertyData) {
      throw new Error(`Imóvel com ID ${id} não encontrado`);
    }
    
    // Mapear a estrutura de dados da API para nosso modelo
    return {
      id: propertyData.id,
      title: propertyData?.data?.title || "Imóvel sem título",
      description: propertyData?.data?.description || "Sem descrição disponível",
      price: parseFloat(propertyData?.data?.sale_value || "0"),
      discount: parseFloat(propertyData?.data?.desconto || "0"),
      originalPrice: parseFloat(propertyData?.data?.preco_avaliacao || "0"),
      images: propertyData?.data?.images || ["/placeholder.svg"],
      address: {
        street: propertyData?.data?.address || "Endereço não informado",
        neighborhood: "",
        city: propertyData?.data?.city || "Cidade não informada",
        state: propertyData?.data?.state || "Estado não informado",
        number: "",
        zipCode: "",
        zipcode: "",
        lat: undefined,
        lng: undefined
      },
      details: {
        area: parseInt(propertyData?.data?.total_area || "0", 10),
        bedrooms: parseInt(propertyData?.data?.quartos || "0", 10),
        bathrooms: parseInt(propertyData?.data?.banheiros || "0", 10),
        parkingSpots: parseInt(propertyData?.data?.garagem || "0", 10),
      },
      modality: propertyData?.data?.modality || "Sem modalidade",
      auctionDate: {
        firstAuction: propertyData?.data?.fim_1 || null,
        secondAuction: propertyData?.data?.fim_2 || null,
        onlineSale: propertyData?.data?.fim_venda_online || null,
      },
      financing: {
        downPayment: 0.2, // 20% de entrada como valor padrão
        installment: 0, // será calculado
        term: 35 * 12, // 35 anos em meses como padrão
        acceptsFinancing: propertyData?.data?.aceita_financiamento === "Sim",
        acceptsFGTS: propertyData?.data?.aceita_FGTS === "Sim",
        acceptsInstallments: propertyData?.data?.aceita_parcelamento === "Sim",
        acceptsConsortium: propertyData?.data?.aceita_consorcio === "Sim"
      },
      observations: propertyData?.data?.ps || [],
      similarProperties: data.results
        .filter((p: any) => String(p.id) !== String(id))
        .slice(0, 3) // Apenas os 3 primeiros
        .map((property: any) => ({
          id: property.id,
          title: property?.data?.title || "Imóvel sem título",
          description: property?.data?.description || "Sem descrição disponível",
          price: parseFloat(property?.data?.sale_value || "0"),
          discount: parseFloat(property?.data?.desconto || "0"),
          originalPrice: parseFloat(property?.data?.preco_avaliacao || "0"),
          images: property?.data?.images || ["/placeholder.svg"],
          address: {
            street: property?.data?.address || "Endereço não informado",
            neighborhood: "",
            city: property?.data?.city || "Cidade não informada",
            state: property?.data?.state || "Estado não informado",
            number: "",
            zipCode: "",
            zipcode: "",
            lat: undefined,
            lng: undefined
          },
          details: {
            area: parseInt(property?.data?.total_area || "0", 10),
            bedrooms: parseInt(property?.data?.quartos || "0", 10),
            bathrooms: parseInt(property?.data?.banheiros || "0", 10),
            parkingSpots: parseInt(property?.data?.garagem || "0", 10),
          },
          modality: property?.data?.modality || "Sem modalidade",
        })),
      registryNumber: propertyData?.data?.matricula_number || "",
      propertyRegistration: propertyData?.data?.inscricao_imobiliaria || "",
      registryUrl: propertyData?.data?.matricula_url || "",
      editalUrl: propertyData?.data?.edital_url || "",
      salesRulesUrl: propertyData?.data?.regras_de_venda_url || "",
      url: propertyData?.data?.url || "",
      reportUrl: propertyData?.data?.relatorio_url || "",
    };
  } catch (error) {
    console.error("Erro ao buscar imóvel:", error);
    
    // Simulando dados para desenvolvimento baseado no ID
    console.log("Usando dados simulados como fallback");
    
    // Gerar dados simulados baseados no ID para desenvolvimento
    const modality = parseInt(id) % 3 === 0 ? "Venda Online" : 
                     parseInt(id) % 2 === 0 ? "Leilão SFI" : "Licitação Aberta";
    
    const basePrice = 150000 + (parseInt(id) * 10000);
    const discount = parseInt(id) % 3 === 0 ? (10 + parseInt(id) % 20) : 0;
    const finalPrice = discount > 0 ? basePrice * (1 - discount/100) : basePrice;
    
    // Imagens do Unsplash para evitar problemas de CORS
    const imageUrls = [
      "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800&q=80",
      "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800&q=80",
      "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&q=80",
      "https://images.unsplash.com/photo-1600566753151-384129cf4e3e?w=800&q=80",
      "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80"
    ];
    
    return {
      id,
      title: "Apartamento Simulado",
      description: "Este é um imóvel simulado quando a API não está disponível. Descrição detalhada do imóvel com características, localização e outras informações relevantes.",
      price: finalPrice,
      discount: discount,
      originalPrice: finalPrice,
      observations: "",
      images: imageUrls,
      bedrooms: 2,
      bathrooms: 1,
      area: 65,
      address: {
        street: "Rua Exemplo",
        neighborhood: "Centro",
        city: "São Paulo",
        state: "SP",
        zipcode: "01234-567",
        lat: undefined,
        lng: undefined
      },
      details: {
        area: 65,
        bedrooms: 2,
        bathrooms: 1,
        parkingSpots: 0
      },
      modality: modality,
      modalityColor: "",
      financing: {
        downPayment: 0,
        installment: 0,
        term: 0
      },
      status: "available",
      isAuction: false,
      createdAt: "2025-04-15",
      updatedAt: "2025-04-15",
      registryNumber: "000",
      propertyRegistration: "000",
      registryUrl: "",
      editalUrl: "",
      salesRulesUrl: "",
      similarProperties: [],
      acceptsFinancing: false,
      acceptsFGTS: false,
      acceptsInstallments: false,
      acceptsConsortium: false,
      urlCaixa: "",
      reportUrl: "",
      url: `https://venda-imoveis.caixa.gov.br/sistema/detalhe-imovel.asp?hdnOrigem=index&hdnimovel=${id}`,
    };
  }
};

// Atualizar o componente DocumentCard
const DocumentCard = ({ 
  title, 
  url, 
  icon: Icon = FileText, 
  colorClass = "text-primary" 
}: { 
  title: string; 
  url: string; 
  icon?: React.ElementType; 
  colorClass?: string; 
}) => (
  <Card className="p-4">
    <CardHeader className="pb-2">
      <CardTitle className="text-lg flex items-center gap-2">
        <Icon className={`h-5 w-5 ${colorClass}`} />
        {title}
      </CardTitle>
    </CardHeader>
    <CardContent>
      <Button className="w-full" onClick={() => window.open(url, '_blank')}>
        Visualizar
      </Button>
    </CardContent>
  </Card>
);

export default function PropertyDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  
  const { data: property, isLoading } = useQuery({
    queryKey: ['property', id],
    queryFn: () => fetchProperty(id!),
  });

  // Format currency helper
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', { 
      style: 'currency', 
      currency: 'BRL',
      maximumFractionDigits: 0
    }).format(value);
  };

  // Generate property report directly
  const handleGenerateReport = async () => {
    if (!property) return;
    
    setIsGeneratingReport(true);
    toast({
      title: "Gerando relatório",
      description: "Estamos analisando o imóvel e preparando seu relatório...",
    });
    
    try {
      // Simulate API call delay for report generation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Generate a random report ID
      const reportId = Math.floor(Math.random() * 100000).toString();
      
      // Navigate to the report page
      navigate(`/relatorio/${reportId}`);
      
      // Successful toast message
      toast({
        title: "Relatório gerado com sucesso",
        description: "Seu relatório de análise foi criado e está disponível para visualização.",
      });
    } catch (error) {
      console.error("Error generating report:", error);
      toast({
        variant: "destructive",
        title: "Erro ao gerar relatório",
        description: "Ocorreu um problema ao analisar o imóvel. Por favor, tente novamente.",
      });
    } finally {
      setIsGeneratingReport(false);
    }
  };

  // Helper to determine the auction details based on modality
  const getAuctionInfo = (property: any) => {
    switch(property.modality) {
      case 'Leilão SFI':
        return {
          title: "Leilão SFI",
          dates: [
            { label: "1º Leilão", date: property.fim_1 && formatDate(property.fim_1) },
            { label: "2º Leilão", date: property.fim_2 && formatDate(property.fim_2) }
          ],
          editalInfo: property.editalNumber && property.editalUrl ? {
            number: property.editalNumber,
            url: property.editalUrl
          } : undefined
        };
      case 'Licitação Aberta':
        return {
          title: "Licitação Aberta",
          dates: [
            { label: "Fim da Licitação", date: property.fim_venda_online && formatDate(property.fim_venda_online) }
          ],
          editalInfo: property.editalNumber && property.editalUrl ? {
            number: property.editalNumber,
            url: property.editalUrl
          } : undefined
        };
      case 'Venda Online':
        return {
          title: "Venda Online",
          dates: [
            { label: "Fim da Oferta", date: property.fim_venda_online && formatDate(property.fim_venda_online) }
          ],
          rulesInfo: property.salesRulesUrl ? {
            url: property.salesRulesUrl
          } : undefined
        };
      case 'Venda Direta Online':
        return {
          title: "Venda Direta Online (Compra Imediata)",
          rulesInfo: property.salesRulesUrl ? {
            url: property.salesRulesUrl
          } : undefined
        };
      default:
        return { title: "Informações de Venda", dates: [] };
    }
  };

  // Format date helper
  const formatDate = (dateString: string) => {
    try {
      return format(parseISO(dateString), "dd/MM/yyyy", { locale: ptBR });
    } catch (e) {
      console.error("Error formatting date:", e);
      return dateString;
    }
  };

  // Get modality badge color
  const getModalityColor = (modality: string) => {
    switch(modality) {
      case 'Leilão SFI':
        return "bg-amber-500 hover:bg-amber-500/90";
      case 'Licitação Aberta':
        return "bg-emerald-600 hover:bg-emerald-600/90";
      case 'Venda Online':
        return "bg-blue-500 hover:bg-blue-500/90";
      case 'Venda Direta Online':
        return "bg-purple-500 hover:bg-purple-500/90";
      default:
        return "";
    }
  };

  // Helper to generate a carousel with the property images
  const renderPropertyImageCarousel = () => {
    if (!property.images || !Array.isArray(property.images) || property.images.length === 0) {
      return (
        <div className="w-full h-[400px] bg-gray-200 flex items-center justify-center">
          <span className="text-gray-500">Sem imagens disponíveis</span>
        </div>
      );
    }

    return <PropertyImages
      imovelId={property.id}
      imagens={property.images}
    />;
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-12">
          <div className="flex items-center justify-center h-96">
            <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary"></div>
          </div>
        </div>
      </Layout>
    );
  }

  if (!property) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-12">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">Imóvel não encontrado</h2>
            <p className="mb-6">O imóvel que você está procurando não foi encontrado.</p>
            <Button className="border text-sm p-2" asChild>
              <Link to="/imoveis-caixa">Voltar para listagem</Link>
            </Button>
          </div>
        </div>
      </Layout>
    );
  }

  const auctionInfo = getAuctionInfo(property);

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Breadcrumb */}
        <div className="flex items-center text-sm mb-6">
          <Link to="/" className="text-muted-foreground hover:text-primary">Home</Link>
          <span className="mx-2 text-muted-foreground">/</span>
          <Link to="/imoveis-caixa" className="text-muted-foreground hover:text-primary">Imóveis Caixa</Link>
          <span className="mx-2 text-muted-foreground">/</span>
          <span className="text-foreground">{property.title}</span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Property Details Section */}
          <div className="lg:col-span-2">
            <div className="flex flex-wrap items-center gap-3 mb-2">
              <Badge className={getModalityColor(property.modality)}>
                {property.modality}
              </Badge>
              <Badge className="border">
                {property.details.parkingSpots === 1 ? "Apartamento" : "Casa"}
              </Badge>
              {property.acceptsFinancing && (
                <Badge className="border">Aceita Financiamento</Badge>
              )}
              {property.acceptsFGTS && (
                <Badge className="border">Aceita FGTS</Badge>
              )}
            </div>

            <h1 className="text-3xl font-bold mb-2">{property.title}</h1>
            <p className="text-xl text-muted-foreground mb-4">{property.address.street}, {property.address.city}, {property.address.state}</p>
            
            <div className="flex items-center mb-6">
              <MapPin className="h-5 w-5 mr-1 text-muted-foreground" />
              <span className="mr-2">{property.address.city}, {property.address.state}</span>
              {property.id && (
                <span className="text-sm text-muted-foreground ml-2">
                  Código: {property.id}
                </span>
              )}
            </div>

            {/* Image Carousel */}
            {renderPropertyImageCarousel()}

            {/* Property Information Tabs */}
            <Tabs defaultValue="about" className="mb-10">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="about">Detalhes</TabsTrigger>
                <TabsTrigger value="features">Características</TabsTrigger>
                <TabsTrigger value="documents">Documentos</TabsTrigger>
                <TabsTrigger value="auction">Leilão</TabsTrigger>
                <TabsTrigger value="location">Localização</TabsTrigger>
              </TabsList>
              
              <TabsContent value="about" className="mt-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="flex flex-col items-center p-4 bg-muted/20 rounded-lg">
                    <Maximize2 className="h-6 w-6 mb-2 text-primary" />
                    <span className="text-sm text-muted-foreground">Área Total</span>
                    <span className="font-medium">{property.details.area} m²</span>
                  </div>
                  {property.details.parkingSpots === 1 && (
                    <div className="flex flex-col items-center p-4 bg-muted/20 rounded-lg">
                      <Home className="h-6 w-6 mb-2 text-primary" />
                      <span className="text-sm text-muted-foreground">Área Privativa</span>
                      <span className="font-medium">{property.details.area} m²</span>
                    </div>
                  )}
                  <div className="flex flex-col items-center p-4 bg-muted/20 rounded-lg">
                    <Bed className="h-6 w-6 mb-2 text-primary" />
                    <span className="text-sm text-muted-foreground">Quartos</span>
                    <span className="font-medium">{property.details.bedrooms}</span>
                  </div>
                  <div className="flex flex-col items-center p-4 bg-muted/20 rounded-lg">
                    <Bath className="h-6 w-6 mb-2 text-primary" />
                    <span className="text-sm text-muted-foreground">Banheiros</span>
                    <span className="font-medium">{property.details.bathrooms}</span>
                  </div>
                  <div className="flex flex-col items-center p-4 bg-muted/20 rounded-lg">
                    <Square className="h-6 w-6 mb-2 text-primary" />
                    <span className="text-sm text-muted-foreground">Vagas</span>
                    <span className="font-medium">{property.details.parkingSpots}</span>
                  </div>
                  <div className="flex flex-col items-center p-4 bg-muted/20 rounded-lg">
                    <Building className="h-6 w-6 mb-2 text-primary" />
                    <span className="text-sm text-muted-foreground">Tipo</span>
                    <span className="font-medium">{property.details.parkingSpots === 1 ? "Apartamento" : "Casa"}</span>
                  </div>
                </div>

                <div className="prose max-w-none">
                  <h3 className="text-xl font-semibold mb-4">Sobre este imóvel</h3>
                  {property.description ? (
                    <p className="mb-4">{property.description}</p>
                  ) : (
                    <p className="mb-4">
                      Este {property.details.parkingSpots === 1 ? "apartamento" : "casa"} está localizado em {property.address.city}, {property.address.state}, em uma excelente localização com fácil acesso a comércios, escolas e transporte público. 
                      Com {property.details.bedrooms} {property.details.bedrooms === 1 ? 'quarto' : 'quartos'} e {property.details.bathrooms} {property.details.bathrooms === 1 ? 'banheiro' : 'banheiros'}, 
                      oferece {property.details.area}m² de área {property.details.parkingSpots === 1 ? "total e " + property.details.area + "m² de área privativa" : 'útil'} e excelente oportunidade de investimento.
                    </p>
                  )}
                  
                  <p className="mb-4">
                    Por ser um imóvel da Caixa Econômica Federal, você tem a oportunidade de adquiri-lo com condições diferenciadas 
                    {property.acceptsFinancing && " com possibilidade de financiamento"}
                    {property.acceptsFGTS && " e uso do FGTS"}
                    {(property.acceptsInstallments || property.acceptsConsortium) && ", além de outras facilidades como "}
                    {property.acceptsInstallments && "parcelamento"}
                    {property.acceptsInstallments && property.acceptsConsortium && " e "}
                    {property.acceptsConsortium && "consórcio"}
                    .
                  </p>
                  
                  {property.originalPrice && (
                    <p>
                      <strong>Oportunidade de economia:</strong> Este imóvel está com desconto de {property.discount}% 
                      em relação ao valor de avaliação que é de {formatCurrency(property.originalPrice)}.
                    </p>
                  )}
                  
                  {property.observations && (
                    <div className="mt-6">
                      <h4 className="text-lg font-semibold mb-2">Observações importantes</h4>
                      <div className="p-4 bg-muted/30 rounded-md">
                        {property.observations}
                      </div>
                    </div>
                  )}
                </div>
              </TabsContent>
              
              <TabsContent value="features" className="mt-6">
                <h3 className="text-xl font-semibold mb-4">Características do imóvel</h3>
                <div className="grid grid-cols-2 gap-x-8 gap-y-4">
                  <div className="flex items-center">
                    <div className="h-2 w-2 bg-primary rounded-full mr-2"></div>
                    <span>{property.details.area} m² de área total</span>
                  </div>
                  {property.details.parkingSpots === 1 && (
                    <div className="flex items-center">
                      <div className="h-2 w-2 bg-primary rounded-full mr-2"></div>
                      <span>{property.details.area} m² de área privativa</span>
                    </div>
                  )}
                  {property.details.bedrooms > 0 && (
                    <div className="flex items-center">
                      <div className="h-2 w-2 bg-primary rounded-full mr-2"></div>
                      <span>{property.details.bedrooms} {property.details.bedrooms === 1 ? 'quarto' : 'quartos'}</span>
                    </div>
                  )}
                  {property.details.bathrooms > 0 && (
                    <div className="flex items-center">
                      <div className="h-2 w-2 bg-primary rounded-full mr-2"></div>
                      <span>{property.details.bathrooms} {property.details.bathrooms === 1 ? 'banheiro' : 'banheiros'}</span>
                    </div>
                  )}
                  {property.details.parkingSpots > 0 && (
                    <div className="flex items-center">
                      <div className="h-2 w-2 bg-primary rounded-full mr-2"></div>
                      <span>{property.details.parkingSpots} {property.details.parkingSpots === 1 ? 'vaga de garagem' : 'vagas de garagem'}</span>
                    </div>
                  )}
                  <div className="flex items-center">
                    <div className="h-2 w-2 bg-primary rounded-full mr-2"></div>
                    <span>Tipo: {property.details.parkingSpots === 1 ? "Apartamento" : "Casa"}</span>
                  </div>
                  <div className="flex items-center">
                    <div className="h-2 w-2 bg-primary rounded-full mr-2"></div>
                    <span>Modalidade: {property.modality}</span>
                  </div>
                  {property.acceptsFinancing && (
                    <div className="flex items-center">
                      <div className="h-2 w-2 bg-primary rounded-full mr-2"></div>
                      <span>Aceita financiamento</span>
                    </div>
                  )}
                  {property.acceptsFGTS && (
                    <div className="flex items-center">
                      <div className="h-2 w-2 bg-primary rounded-full mr-2"></div>
                      <span>Aceita FGTS</span>
                    </div>
                  )}
                  {property.acceptsInstallments && (
                    <div className="flex items-center">
                      <div className="h-2 w-2 bg-primary rounded-full mr-2"></div>
                      <span>Aceita parcelamento</span>
                    </div>
                  )}
                  {property.acceptsConsortium && (
                    <div className="flex items-center">
                      <div className="h-2 w-2 bg-primary rounded-full mr-2"></div>
                      <span>Aceita consórcio</span>
                    </div>
                  )}
                  {property.registryNumber && (
                    <div className="flex items-center">
                      <div className="h-2 w-2 bg-primary rounded-full mr-2"></div>
                      <span>Matrícula: {property.registryNumber}</span>
                    </div>
                  )}
                  {property.propertyRegistration && (
                    <div className="flex items-center">
                      <div className="h-2 w-2 bg-primary rounded-full mr-2"></div>
                      <span>Inscrição imobiliária: {property.propertyRegistration}</span>
                    </div>
                  )}
                </div>
              </TabsContent>
              
              <TabsContent value="documents" className="mt-6">
                <h3 className="text-xl font-semibold mb-4">Documentação do Imóvel</h3>
                <p className="mb-4">Documentos relacionados a este imóvel:</p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {property.registryUrl && (
                    <DocumentCard title="Matrícula do Imóvel" url={property.registryUrl} icon={FileText} />
                  )}
                  {property.editalUrl && (
                    <DocumentCard title="Edital do Leilão" url={property.editalUrl} icon={FileText} />
                  )}
                  {property.salesRulesUrl && (
                    <DocumentCard title="Regras de Venda" url={property.salesRulesUrl} icon={FileText} />
                  )}
                  {property.reportUrl && (
                    <DocumentCard 
                      title="Relatório de Análise" 
                      url={property.reportUrl} 
                      icon={Square} 
                      colorClass="text-blue-600" 
                    />
                  )}
                  
                  {!property.registryUrl && !property.editalUrl && !property.salesRulesUrl && !property.reportUrl && (
                    <p className="col-span-3 text-center text-muted-foreground py-6">
                      Nenhum documento disponível para este imóvel
                    </p>
                  )}
                </div>
                
                {property.registryNumber && (
                  <div className="mt-6">
                    <h4 className="text-lg font-semibold mb-3">Informações de Registro</h4>
                    <div className="space-y-2">
                      <div className="flex items-center">
                        <FileText className="h-4 w-4 mr-2 text-primary" />
                        <span className="font-medium">Número de Matrícula: </span>
                        <span className="ml-2">{property.registryNumber}</span>
                      </div>
                      
                      {property.propertyRegistration && (
                        <div className="flex items-center">
                          <Square className="h-4 w-4 mr-2 text-primary" />
                          <span className="font-medium">Inscrição Imobiliária: </span>
                          <span className="ml-2">{property.propertyRegistration}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </TabsContent>
              
              <TabsContent value="auction" className="mt-6">
                <h3 className="text-xl font-semibold mb-4">{auctionInfo.title}</h3>
                
                {auctionInfo.dates && auctionInfo.dates.length > 0 && (
                  <div className="mb-6">
                    <h4 className="font-semibold mb-3">Datas importantes</h4>
                    <div className="space-y-3">
                      {auctionInfo.dates.map((dateInfo, index) => (
                        dateInfo.date && (
                          <div key={index} className="flex items-center">
                            <Calendar className="h-5 w-5 mr-2 text-primary" />
                            <span className="font-medium">{dateInfo.label}: </span>
                            <span className="ml-2">{dateInfo.date}</span>
                          </div>
                        )
                      ))}
                    </div>
                  </div>
                )}
                
                {auctionInfo.editalInfo && (
                  <div className="mb-6">
                    <h4 className="font-semibold mb-3">Informações do Edital</h4>
                    <p className="mb-2">Edital Número: {auctionInfo.editalInfo.number}</p>
                    <Button className="border text-sm p-2" asChild>
                      <a href={auctionInfo.editalInfo.url} target="_blank" rel="noopener noreferrer">
                        <Download className="h-4 w-4 mr-2" />
                        Baixar Edital
                      </a>
                    </Button>
                  </div>
                )}
                
                {auctionInfo.rulesInfo && (
                  <div className="mb-6">
                    <h4 className="font-semibold mb-3">Regras da Venda</h4>
                    <Button className="border text-sm p-2" asChild>
                      <a href={auctionInfo.rulesInfo.url} target="_blank" rel="noopener noreferrer">
                        <Download className="h-4 w-4 mr-2" />
                        Ver Regras de Venda
                      </a>
                    </Button>
                  </div>
                )}
                
                {property.url && (
                  <div className="mt-8">
                    <h4 className="font-semibold mb-3">Acessar oferta no site da Caixa</h4>
                    <Button 
                      className="w-full text-sm" 
                      onClick={handleGenerateReport}
                      disabled={isGeneratingReport}
                    >
                      {isGeneratingReport ? (
                        <>
                          <span className="animate-pulse mr-2">•</span>
                          Gerando análise...
                        </>
                      ) : (
                        "Analisar este imóvel"
                      )}
                    </Button>
                    
                    {property.url && (
                      <Button className="w-full text-sm border border-input bg-background hover:bg-accent hover:text-accent-foreground" asChild>
                        <a href={property.url} target="_blank" rel="noopener noreferrer">
                          Ver no site da Caixa
                        </a>
                      </Button>
                    )}
                  </div>
                )}
              </TabsContent>
              
              <TabsContent value="location" className="mt-6">
                <h3 className="text-xl font-semibold mb-4">Localização</h3>
                <p className="mb-4">{property.address.street}, {property.address.city} - {property.address.state}</p>
                
                <div className="aspect-video bg-muted rounded-lg overflow-hidden">
                  <div className="flex items-center justify-center h-full">
                    <p className="text-muted-foreground">Mapa indisponível</p>
                  </div>
                </div>
                
                <div className="mt-6">
                  <h4 className="font-semibold mb-2">Proximidades</h4>
                  <div className="grid grid-cols-2 gap-x-8 gap-y-2">
                    <div className="flex items-center">
                      <div className="h-2 w-2 bg-primary rounded-full mr-2"></div>
                      <span>Supermercados</span>
                    </div>
                    <div className="flex items-center">
                      <div className="h-2 w-2 bg-primary rounded-full mr-2"></div>
                      <span>Escolas</span>
                    </div>
                    <div className="flex items-center">
                      <div className="h-2 w-2 bg-primary rounded-full mr-2"></div>
                      <span>Hospitais</span>
                    </div>
                    <div className="flex items-center">
                      <div className="h-2 w-2 bg-primary rounded-full mr-2"></div>
                      <span>Transporte público</span>
                    </div>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </div>

          {/* Sidebar with Price and Actions */}
          <div className="lg:col-span-1">
            <Card className="sticky top-20">
              <CardHeader>
                <CardTitle>
                  {property.originalPrice ? (
                    <>
                      <div className="text-sm line-through text-muted-foreground">
                        De {formatCurrency(property.originalPrice)}
                      </div>
                      <div className="text-3xl font-bold text-primary">
                        Por {formatCurrency(property.price)}
                      </div>
                    </>
                  ) : (
                    <div className="text-3xl font-bold">
                      {formatCurrency(property.price)}
                    </div>
                  )}
                  
                  {property.discount && (
                    <Badge variant="destructive" className="mt-2">
                      {property.discount}% de desconto
                    </Badge>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <Button 
                    className="w-full text-sm" 
                    onClick={handleGenerateReport}
                    disabled={isGeneratingReport}
                  >
                    {isGeneratingReport ? (
                      <>
                        <span className="animate-pulse mr-2">•</span>
                        Gerando análise...
                      </>
                    ) : (
                      "Analisar este imóvel"
                    )}
                  </Button>
                  
                  {property.url && (
                    <Button className="w-full text-sm border border-input bg-background hover:bg-accent hover:text-accent-foreground" asChild>
                      <a href={property.url} target="_blank" rel="noopener noreferrer">
                        Ver no site da Caixa
                      </a>
                    </Button>
                  )}
                </div>
                
                <Separator />
                
                {auctionInfo.dates && auctionInfo.dates.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2 flex items-center">
                      <CalendarDays className="h-4 w-4 mr-1" />
                      Datas importantes
                    </h4>
                    
                    <div className="space-y-2">
                      {auctionInfo.dates.map((dateInfo, index) => (
                        dateInfo.date && (
                          <div key={index} className="flex justify-between text-sm">
                            <span>{dateInfo.label}:</span>
                            <span className="font-medium">{dateInfo.date}</span>
                          </div>
                        )
                      ))}
                    </div>
                  </div>
                )}
                
                <Separator />
                
                <div>
                  <h4 className="font-semibold mb-2 flex items-center">
                    <Info className="h-4 w-4 mr-1" />
                    Detalhes do financiamento
                  </h4>
                  <p className="text-sm text-muted-foreground mb-4">
                    Simulação aproximada para este imóvel:
                  </p>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Entrada (20%):</span>
                      <span className="font-medium">{formatCurrency(property.price * 0.2)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Financiamento:</span>
                      <span className="font-medium">{formatCurrency(property.price * 0.8)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Parcela estimada:</span>
                      <span className="font-medium">{formatCurrency((property.price * 0.8) / 360)}/mês</span>
                    </div>
                  </div>
                </div>
                
                <Separator />
                
                <div>
                  <h4 className="font-semibold mb-2 flex items-center">
                    <Star className="h-4 w-4 mr-1" />
                    Análise preliminar
                  </h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Valor do m²:</span>
                      <span className="font-medium">
                        {property.details?.area && property.details.area > 0 
                          ? formatCurrency(property.price / property.details.area)
                          : "Não disponível"}/m²
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Média da região:</span>
                      <span className="font-medium">
                        {property.details?.area && property.details.area > 0 
                          ? formatCurrency((property.price / property.details.area) * 1.1)
                          : "Não disponível"}/m²
                      </span>
                    </div>
                    <div className="flex justify-between text-green-600">
                      <span>Economia potencial:</span>
                      <span className="font-medium">
                        {property.discount ? `${property.discount}%` : "10%"} abaixo do mercado
                      </span>
                    </div>
                  </div>
                </div>
                
                <Button className="w-full text-sm" onClick={handleGenerateReport} disabled={isGeneratingReport}>
                  Ver análise completa
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
        
        <div className="mt-8">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold">Imóveis similares</h2>
            <Button className="text-sm border border-input bg-background hover:bg-accent hover:text-accent-foreground" asChild>
              <Link to="/imoveis-caixa">Ver todos</Link>
            </Button>
          </div>
          
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {property?.similarProperties && property.similarProperties.length > 0 ? (
              property.similarProperties.slice(0, 3).map((similarProperty) => (
                <div key={similarProperty.id} className="p-6 border rounded-lg">
                  <h4 className="text-xl font-semibold mb-2">{similarProperty.title}</h4>
                  <p className="text-sm text-muted-foreground mb-4">{similarProperty.description}</p>
                  <div className="font-bold text-lg mb-4">{formatCurrency(similarProperty.price)}</div>
                  <Button className="w-full" asChild>
                    <Link to={`/imovel/${similarProperty.id}`}>Ver Detalhes</Link>
                  </Button>
                </div>
              ))
            ) : (
              <p className="col-span-3 text-center text-muted-foreground py-6">Nenhum imóvel similar encontrado</p>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
