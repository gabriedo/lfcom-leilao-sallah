// Configurações da API
export const API_CONFIG = {
  // URL base da API
  BASE_URL: "/api/properties",
  
  // URL da API externa direta (mantemos para referência)
  EXTERNAL_API_URL: "https://scraphub.comercify.shop/api/items/2",
  
  // Chave de API
  API_KEY: "gAAAAABn3ODQd_A82IRyOyKE_AwEAXITB6TY4Q0lxFVkiG_DxA0Ochmod4g-0jcReIuh2X7DaZLBJ5TbZIpZTxvsXRWuinq_NFxnf3chEWUZiaFPRFfhONMnIB2mtkV3cgDq2TlODXez",
  
  // Configurações para lidar com CORS
  CORS: {
    // Se true, usa um proxy CORS para evitar problemas de CORS. 
    // Recomendado definir como false em produção e configurar o backend corretamente
    USE_PROXY: false,
    
    // URL do proxy CORS - você pode usar um proxy público como o cors-anywhere
    // Mas para uma solução mais confiável em produção, configure seu próprio proxy
    PROXY_URL: "https://cors-anywhere.herokuapp.com/",
  },
  
  // Função para formatar a URL da API com o proxy CORS se necessário
  getApiUrl: function(path: string = ""): string {
    const url = `${this.BASE_URL}${path}`;
    return this.CORS.USE_PROXY ? `${this.CORS.PROXY_URL}${url}` : url;
  },
  
  // Função para obter os cabeçalhos da API
  getHeaders: function(): Headers {
    const headers = new Headers();
    // Quando usamos nosso backend local, não precisamos enviar a chave API
    // Ele adiciona a chave internamente ao fazer requisições para a API externa
    // headers.append("X-Api-Key", this.API_KEY);
    headers.append("Accept", "application/json");
    return headers;
  },
  
  // Função para obter as opções padrão para requisições fetch
  getRequestOptions: function(method: string = 'GET'): RequestInit {
    return {
      method: method,
      headers: this.getHeaders(),
      redirect: 'follow' as RequestRedirect,
      mode: 'cors' as RequestMode
    };
  }
};