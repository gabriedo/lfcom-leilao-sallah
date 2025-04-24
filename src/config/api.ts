export const API_CONFIG = {
  BASE_URL: 'http://localhost:8890/api', // URL completa do servidor
  EXTERNAL_API_URL: 'https://api.leilaoinsights.com.br',
  API_KEY: 'gAAAAABn3ODQd_A82IRyOyKE_AwEAXITB6TY4Q0lxFVkiG_DxA0Ochmod4g-0jcReIuh2X7DaZLBJ5TbZIpZTxvsXRWuinq_NFxnf3chEWUZiaFPRFfhONMnIB2mtkV3cgDq2TlODXez',
  CORS: {
    USE_PROXY: false,
    PROXY_URL: 'https://cors-anywhere.herokuapp.com/'
  },
  ENDPOINTS: {
    PROPERTIES: '/properties',
    IMAGES: '/images'
  },
  getApiUrl: (endpoint: string): string => {
    return `${API_CONFIG.BASE_URL}${endpoint}`;
  },
  getHeaders: () => {
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Origin': 'http://localhost:8083'
    };
  },
  getRequestOptions: (method: string = 'GET') => {
    return {
      method,
      headers: API_CONFIG.getHeaders(),
      credentials: 'omit'
    };
  }
}; 