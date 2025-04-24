import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Interceptor para adicionar headers em todas as requisições
axiosInstance.interceptors.request.use(
  (config) => {
    console.log('Enviando requisição:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      headers: config.headers,
      params: config.params
    });
    return config;
  },
  (error) => {
    console.error('Erro na requisição:', error);
    return Promise.reject(error);
  }
);

// Interceptor para tratar respostas
axiosInstance.interceptors.response.use(
  (response) => {
    console.log('Resposta recebida:', {
      status: response.status,
      url: response.config.url,
      baseURL: response.config.baseURL,
      data: response.data
    });
    return response;
  },
  (error) => {
    if (error.response) {
      console.error('Erro na resposta:', {
        status: error.response.status,
        data: error.response.data,
        headers: error.response.headers,
        config: {
          url: error.config?.url,
          baseURL: error.config?.baseURL,
          method: error.config?.method,
          params: error.config?.params,
          headers: error.config?.headers
        }
      });
    } else if (error.request) {
      console.error('Erro na requisição:', error.request);
    } else {
      console.error('Erro:', error.message);
    }
    return Promise.reject(error);
  }
);

export default axiosInstance; 