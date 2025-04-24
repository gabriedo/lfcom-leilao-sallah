import axios from 'axios';

interface ImagemResponse {
  url: string;
}

export interface Imovel {
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

interface ApiResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Imovel[];
}

const API_KEY = 'gAAAAABn3ODQd_A82IRyOyKE_AwEAXITB6TY4Q0lxFVkiG_DxA0Ochmod4g-0jcReIuh2X7DaZLBJ5TbZIpZTxvsXRWuinq_NFxnf3chEWUZiaFPRFfhONMnIB2mtkV3cgDq2TlODXez';
const BASE_URL = 'https://scraphub.comercify.shop/api';

export const caixaService = {
  async getImoveis(page: number = 1): Promise<ApiResponse> {
    try {
      const response = await axios.get<ApiResponse>(`${BASE_URL}/items/2/`, {
        params: { page },
        headers: {
          'X-Api-Key': API_KEY
        }
      });
      return response.data;
    } catch (error) {
      console.error('Erro ao buscar imóveis:', error);
      throw error;
    }
  },

  async getImagem(imageUrl: string): Promise<string> {
    try {
      // Como as URLs das imagens já vêm completas da API, apenas retornamos a URL
      return imageUrl;
    } catch (error) {
      console.error('Erro ao buscar imagem:', error);
      throw error;
    }
  }
};

// Função auxiliar para adaptar os dados da API
export const adaptImovelData = (apiImovel: any): Imovel => {
  return {
    id: apiImovel.id,
    data: {
      ...apiImovel.data,
      images: apiImovel.data.images || [],
      sale_value: apiImovel.data.sale_value?.replace(/[^0-9,.]/g, '') || '0',
      preco_avaliacao: apiImovel.data.preco_avaliacao?.replace(/[^0-9,.]/g, '') || '0',
      desconto: apiImovel.data.desconto || '0',
      title: apiImovel.data.title?.trim() || '',
      description: apiImovel.data.description?.trim() || '',
      address: apiImovel.data.address?.trim() || '',
      city: apiImovel.data.city?.trim() || '',
      state: apiImovel.data.state?.trim() || '',
      type: apiImovel.data.type?.trim() || '',
      modality: apiImovel.data.modality?.trim() || '',
      total_area: apiImovel.data.total_area?.trim() || '',
      private_area: apiImovel.data.private_area?.trim() || '',
      quartos: apiImovel.data.quartos?.trim() || '',
      banheiros: apiImovel.data.banheiros?.trim() || '',
      garagem: apiImovel.data.garagem?.trim() || '',
      ps: apiImovel.data.ps || []
    }
  };
}; 