import requests
from typing import Dict, Optional
from cache_manager import CacheManager
import logging

logger = logging.getLogger(__name__)

class CaixaImoveisAPI:
    def __init__(self):
        self.base_url = "https://scraphub.comercify.shop/api/items/2/"
        self.api_key = "gAAAAABn3ODQd_A82IRyOyKE_AwEAXITB6TY4Q0lxFVkiG_DxA0Ochmod4g-0jcReIuh2X7DaZLBJ5TbZIpZTxvsXRWuinq_NFxnf3chEWUZiaFPRFfhONMnIB2mtkV3cgDq2TlODXez"
        self.cache_duration = 3600  # 1 hora em segundos
        self.cache_manager = CacheManager()

    def get_imoveis(self, page: int = 1) -> Dict:
        """Busca imóveis da API da Caixa com cache"""
        cache_key = f"imoveis_caixa_page_{page}"
        
        # Tenta buscar do cache primeiro
        cached_data = self.cache_manager.get(cache_key)
        if cached_data:
            return cached_data
            
        # Se não estiver em cache, busca da API
        headers = {
            "X-Api-Key": self.api_key
        }
        
        try:
            response = requests.get(
                f"{self.base_url}?page={page}",
                headers=headers,
                timeout=30  # Timeout de 30 segundos
            )
            response.raise_for_status()
            data = response.json()
            
            # Validação básica dos dados
            if not isinstance(data, dict):
                raise ValueError("Resposta inválida da API")
            
            # Salva no cache
            self.cache_manager.set(cache_key, data, self.cache_duration)
            
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar imóveis da Caixa: {str(e)}")
            raise Exception("Erro ao buscar imóveis da Caixa")
        except ValueError as e:
            logger.error(f"Erro de validação dos dados: {str(e)}")
            raise Exception("Dados inválidos retornados pela API") 