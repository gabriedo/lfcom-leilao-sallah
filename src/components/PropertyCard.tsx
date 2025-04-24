import React from "react";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { Bed, Bath, Maximize2, MapPin, Tag, Calendar, Home, Square } from "lucide-react";
import { format, parseISO } from "date-fns";
import { ptBR } from "date-fns/locale";
import { PropertyImages } from "@/components/PropertyImages";
import { ScraphubProperty } from '../services/scraphubService';
import { formatCurrency, formatDate, formatArea } from '../utils/formatters';

interface PropertyCardProps {
  property: ScraphubProperty;
}

const PropertyCard: React.FC<PropertyCardProps> = ({ property }) => {
  const {
    data: {
      tipo,
      modalidade,
      valor_venda,
      desconto,
      area_total,
      quartos,
      banheiros,
      vagas,
      endereco,
      imagens,
      aceita_financiamento,
      aceita_FGTS,
      data_inicio,
      hora_inicio
    }
  } = property;

  const getModalityColor = (modality: string) => {
    switch (modality) {
      case 'Leilão SFI':
      case 'Leilão SFI - Edital Único':
        return 'bg-red-500';
      case 'Licitação Aberta':
        return 'bg-blue-500';
      case 'Venda Online':
      case 'Venda Direta Online':
        return 'bg-green-500';
      default:
        return 'bg-gray-500';
    }
  };

  const formatPaymentInfo = () => {
    const paymentMethods = [];
    if (aceita_financiamento?.includes('Permite financiamento')) {
      paymentMethods.push('Financiamento');
    }
    if (aceita_FGTS?.includes('Permite utilização de FGTS')) {
      paymentMethods.push('FGTS');
    }
    return paymentMethods.join(' • ');
  };

  const formatDateTime = () => {
    if (data_inicio && hora_inicio) {
      return `${formatDate(data_inicio)} - ${hora_inicio}`;
    }
    return data_inicio ? formatDate(data_inicio) : 'Data não informada';
  };

  // Remover as URLs de fallback do Unsplash, já que agora temos imagens reais
  const fallbackImage = "/placeholder.svg";
  
  // Helper para verificar se um campo de texto é válido
  const isValidText = (value: any): boolean => {
    return value && typeof value === 'string' && value.trim() !== "" && value.trim() !== "-" && value.trim().toLowerCase() !== "n/a";
  };

  // Helper to determine the end date to show
  const getEndDate = () => {
    let date: string | undefined;
    let label: string = '';
    
    // Esta garantindo a compatibilidade com a nova API
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
        // Se não reconhecermos a modalidade, não exibimos data
        return { formatted: '', label: '' };
    }

    if (date && isValidText(date)) {
      try {
        // Tratamento mais robusto de datas
        if (date === "N/A" || date.toLowerCase().includes("n/a")) {
          return { formatted: '', label };
        }
        
        // Tenta formatação com parseISO para datas no formato ISO (YYYY-MM-DD)
        if (date.includes('-') && !date.includes('h') && !date.includes(':')) {
          return {
            formatted: format(parseISO(date), "dd/MM/yyyy", { locale: ptBR }),
            label
          };
        }
        
        // Para formatos específicos com hora (ex: DD/MM/YYYY - HHhMM)
        if (date.includes('/') && (date.includes('h') || date.includes(':'))) {
          // Extrai apenas a data, ignorando a parte da hora
          const dateOnly = date.split('-')[0].trim();
          // Retorna a data como está, já que está no formato brasileiro
          return { formatted: dateOnly, label };
        }
        
        // Para datas que já estão no formato DD/MM/YYYY ou outros formatos prontos
        return { formatted: date.trim(), label };
      } catch (e) {
        console.error("Error formatting date:", e, date);
        // Em caso de erro, tenta extrair apenas a data do formato, se possível
        if (date.includes('/') && date.includes('-')) {
          const dateOnly = date.split('-')[0].trim();
          return { formatted: dateOnly, label };
        }
        // Se não conseguir extrair, retorna a data como está
        return { formatted: date, label };
      }
    }
    
    return { formatted: '', label };
  };

  const endDate = getEndDate();

  // Verificando se há imagens disponíveis
  const hasImages = Array.isArray(imagens) && imagens.length > 0;
  
  // Extrair apenas os nomes dos arquivos das URLs das imagens
  const imageNames = hasImages ? imagens.map(url => {
    try {
      const decodedUrl = decodeURIComponent(url);
      const nomeArquivo = decodedUrl.split('/').pop();
      if (!nomeArquivo) {
        console.error('Nome do arquivo não encontrado na URL:', url);
        return null;
      }
      return nomeArquivo;
    } catch (error) {
      console.error('Erro ao processar URL da imagem:', error);
      return null;
    }
  }).filter((name): name is string => name !== null) : [];

  // Verificar se há desconto
  const hasDiscount = desconto && 
    parseFloat(desconto.toString().replace(/[^\d.-]/g, '')) > 0;
    
  // Verificar se os campos importantes existem
  const hasTitle = isValidText(tipo);
  const hasAddress = isValidText(endereco.bairro);
  const hasCity = isValidText(endereco.cidade);
  const hasState = isValidText(endereco.estado);
  const hasModality = isValidText(modalidade);
  const hasType = isValidText(tipo);
  
  // Obter valores para campos importantes ou fornecer valores padrão
  const title = hasTitle ? tipo : "Imóvel sem título";
  const address = hasAddress ? endereco.bairro : "Endereço não informado";
  const city = hasCity ? endereco.cidade : "Cidade não informada";
  const state = hasState ? endereco.estado : "";
  const modality = hasModality ? modalidade : "Sem modalidade";
  const type = hasType ? tipo : "Imóvel";

  return (
    <Card className="h-full flex flex-col hover:shadow-lg transition-shadow duration-300">
      <CardHeader className="p-0">
        <div className="relative">
          <img
            src={imagens?.[0]?.url || '/placeholder.jpg'}
            alt={type}
            className="w-full h-48 object-cover rounded-t-lg"
          />
          <Badge className={`absolute top-2 right-2 ${getModalityColor(modality)}`}>
            {modality}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="flex-grow p-4">
        <div className="space-y-2">
          <h3 className="text-lg font-semibold">{title}</h3>
          <p className="text-sm text-muted-foreground flex items-center">
            <MapPin className="h-4 w-4 mr-1" />
            {address}, {state}
          </p>
          <div className="flex items-center justify-between">
            <span className="text-2xl font-bold text-primary">
              {formatCurrency(valor_venda)}
            </span>
            {hasDiscount && (
              <Badge variant="outline" className="text-green-600">
                {desconto}% de desconto
              </Badge>
            )}
          </div>
          <div className="grid grid-cols-3 gap-2 text-sm mt-4">
            <div className="flex items-center">
              <Bed className="mr-1 h-4 w-4" />
              {quartos} quartos
            </div>
            <div className="flex items-center">
              <Bath className="mr-1 h-4 w-4" />
              {banheiros} banheiros
            </div>
            <div className="flex items-center">
              <Square className="mr-1 h-4 w-4" />
              {vagas} vagas
            </div>
          </div>
          <div className="text-sm mt-4 space-y-1">
            <p className="flex items-center">
              <Maximize2 className="h-4 w-4 mr-1" />
              Área: {formatArea(area_total)}
            </p>
            <p className="flex items-center">
              <Calendar className="h-4 w-4 mr-1" />
              Data: {formatDateTime()}
            </p>
            {formatPaymentInfo() && (
              <p className="text-green-600 flex items-center">
                <Tag className="h-4 w-4 mr-1" />
                {formatPaymentInfo()}
              </p>
            )}
          </div>
        </div>
      </CardContent>
      <CardFooter className="p-4 border-t">
        <Button asChild className="w-full">
          <Link to={`/imovel/${property.id}`}>
            Ver Detalhes
          </Link>
        </Button>
      </CardFooter>
    </Card>
  );
};

export default PropertyCard;
