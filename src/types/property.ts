export interface Property {
  id: string;
  data: {
    id: string;
    title: string;
    address: string;
    city: string;
    state: string;
    type: string;
    sale_value: string;
    preco_avaliacao: string;
    desconto: string;
    total_area: string;
    private_area: string;
    quartos: string;
    banheiros: string;
    garagem: string;
    images: string[];
    modality: string;
    fim_1: string | null;
    fim_2: string | null;
    fim_venda_online: string | null;
    aceita_financiamento: string | null;
    aceita_FGTS: string | null;
    aceita_parcelamento: string | null;
    aceita_consorcio: string | null;
    description: string;
    ps: string[];
    matricula_number?: string;
    inscricao_imobiliaria?: string;
    matricula_url?: string;
    edital_url?: string;
    regras_de_venda_url?: string;
    url?: string;
  };
}

export interface PropertyFiltersType {
  city: string;
  state: string;
  propertyType: string;
  modality: string;
  priceMin: number;
  priceMax: number;
  bedrooms: number;
  parking: number;
  acceptsFinancing: boolean | null;
  acceptsFGTS: boolean | null;
  minDiscount: number;
  areaMin: number;
  sortBy: string;
} 