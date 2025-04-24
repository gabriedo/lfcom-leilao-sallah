import axiosInstance from './axiosConfig';
import axios from 'axios';

export interface ScraphubProperty {
  id: number;
  site_id: string;
  data: {
    tipo: string;
    modalidade: string;
    valor_venda: string;
    desconto: string;
    area_total: string;
    quartos: number;
    banheiros: number;
    vagas: number;
    endereco: {
      cidade: string;
      estado: string;
      bairro: string;
    };
    imagens: Array<{ url: string }>;
    aceita_financiamento?: string;
    aceita_FGTS?: string;
    data_inicio?: string;
    hora_inicio?: string;
    data_fim?: string;
    hora_fim?: string;
    fim_1?: string;
    fim_2?: string;
    fim_venda_online?: string;
  };
}

export interface ScraphubApiResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: ScraphubProperty[];
}

export interface SearchParams {
  page?: number;
  limit?: number;
  cidade?: string;
  estado?: string;
  tipo?: string;
  modalidade?: string;
  min_valor?: number;
  max_valor?: number;
  quartos?: number;
  vagas?: number;
  min_area?: number;
  max_area?: number;
  aceita_financiamento?: boolean;
  aceita_FGTS?: boolean;
  min_desconto?: number;
}

export class ScraphubService {
  private static instance: ScraphubService;

  private constructor() {}

  public static getInstance(): ScraphubService {
    if (!ScraphubService.instance) {
      ScraphubService.instance = new ScraphubService();
    }
    return ScraphubService.instance;
  }

  private handleError(error: unknown): never {
    if (axios.isAxiosError(error)) {
      if (error.response) {
        console.error('Erro na API:', {
          status: error.response.status,
          data: error.response.data,
          url: error.config?.url,
          baseURL: error.config?.baseURL
        });
        throw new Error(`Erro na API: ${error.response.status} - ${JSON.stringify(error.response.data)}`);
      } else if (error.request) {
        console.error('Erro de conexão:', error.request);
        throw new Error('Erro de conexão com o servidor. Por favor, verifique sua conexão com a internet.');
      }
    }
    console.error('Erro inesperado:', error);
    throw new Error('Ocorreu um erro inesperado. Por favor, tente novamente mais tarde.');
  }

  public async getProperties(page: number = 1): Promise<ScraphubApiResponse> {
    try {
      const response = await axiosInstance.get<ScraphubApiResponse>('/imoveis/', {
        params: {
          page,
          limit: 20
        }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  public async getPropertyById(id: number): Promise<ScraphubProperty> {
    try {
      const response = await axiosInstance.get<ScraphubProperty>(`/imoveis/${id}/`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  public async searchProperties(params: SearchParams): Promise<ScraphubApiResponse> {
    try {
      // Remove parâmetros undefined ou vazios
      const cleanParams = Object.entries(params).reduce((acc, [key, value]) => {
        if (value !== undefined && value !== '' && value !== 0) {
          acc[key] = value;
        }
        return acc;
      }, {} as Record<string, any>);

      const response = await axiosInstance.get<ScraphubApiResponse>('/imoveis/', {
        params: cleanParams
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }
} 