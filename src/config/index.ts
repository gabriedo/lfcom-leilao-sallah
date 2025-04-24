export const API_CONFIG = {
  getApiUrl: () => {
    return '/api/properties';
  },
  
  getRequestOptions: () => {
    return {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      credentials: 'include',
    };
  }
}; 