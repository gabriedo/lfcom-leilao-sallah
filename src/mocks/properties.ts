import { Property } from '@/types/property';

export const mockProperties: Property[] = [
  {
    id: "1",
    data: {
      id: "1",
      title: "Apartamento 3 quartos - Centro",
      address: "Rua Exemplo, 123",
      city: "São Paulo",
      state: "SP",
      type: "Apartamento",
      sale_value: "500000",
      preco_avaliacao: "600000",
      desconto: "16.67",
      total_area: "120",
      private_area: "90",
      quartos: "3",
      banheiros: "2",
      garagem: "2",
      images: ["https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800&q=80"],
      modality: "Leilão SFI",
      fim_1: "2024-05-01",
      fim_2: "2024-05-15",
      fim_venda_online: null,
      aceita_financiamento: "Sim",
      aceita_FGTS: "Sim",
      aceita_parcelamento: "Sim",
      aceita_consorcio: "Não",
      description: "Excelente apartamento no centro da cidade...",
      ps: ["Imóvel ocupado", "Necessita reforma"]
    }
  },
  {
    id: "2",
    data: {
      id: "2",
      title: "Casa 4 quartos - Jardins",
      address: "Av. Exemplo, 456",
      city: "São Paulo",
      state: "SP",
      type: "Casa",
      sale_value: "1200000",
      preco_avaliacao: "1500000",
      desconto: "20.00",
      total_area: "300",
      private_area: "250",
      quartos: "4",
      banheiros: "3",
      garagem: "3",
      images: ["https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800&q=80"],
      modality: "Venda Online",
      fim_1: null,
      fim_2: null,
      fim_venda_online: "2024-04-30",
      aceita_financiamento: "Sim",
      aceita_FGTS: "Sim",
      aceita_parcelamento: "Sim",
      aceita_consorcio: "Sim",
      description: "Casa espaçosa em excelente localização...",
      ps: ["Imóvel desocupado", "Em bom estado de conservação"]
    }
  },
  {
    id: "3",
    data: {
      id: "3",
      title: "Sobrado 3 quartos - Butantã",
      address: "Rua Exemplo, 789",
      city: "São Paulo",
      state: "SP",
      type: "Sobrado",
      sale_value: "800000",
      preco_avaliacao: "950000",
      desconto: "15.79",
      total_area: "200",
      private_area: "180",
      quartos: "3",
      banheiros: "3",
      garagem: "2",
      images: ["https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&q=80"],
      modality: "Licitação Aberta",
      fim_1: null,
      fim_2: null,
      fim_venda_online: "2024-05-20",
      aceita_financiamento: "Sim",
      aceita_FGTS: "Não",
      aceita_parcelamento: "Sim",
      aceita_consorcio: "Não",
      description: "Sobrado em excelente localização com ótimo acabamento...",
      ps: ["Imóvel desocupado", "Pronto para morar"]
    }
  }
]; 