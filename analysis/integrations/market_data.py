import requests
import logging
from typing import Dict, Any, Optional

class MarketData:
    """Classe para integração com dados de mercado imobiliário"""
    
    def __init__(self, api_key: str):
        """Inicializa a integração com dados de mercado"""
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        
    def obter_dados_mercado(self, endereco: str) -> Dict[str, Any]:
        """Obtém dados de mercado para um endereço"""
        try:
            # Configuração do header com a API key
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Faz a requisição HTTP
            response = requests.get(
                f'https://api.imobiliaria.com/mercado',
                params={'endereco': endereco},
                headers=headers
            )
            response.raise_for_status()
            
            # Retorna os dados de mercado
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados de mercado para o endereço {endereco}: {str(e)}")
            return {}
            
    def obter_dados_comparativos(self, endereco: str, area: float) -> Dict[str, Any]:
        """Obtém dados comparativos de imóveis similares"""
        try:
            # Configuração do header com a API key
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Faz a requisição HTTP
            response = requests.get(
                f'https://api.imobiliaria.com/comparativos',
                params={
                    'endereco': endereco,
                    'area': area
                },
                headers=headers
            )
            response.raise_for_status()
            
            # Retorna os dados comparativos
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados comparativos para o endereço {endereco}: {str(e)}")
            return {}
            
    def obter_dados_evolucao(self, endereco: str) -> Dict[str, Any]:
        """Obtém dados de evolução de preços"""
        try:
            # Configuração do header com a API key
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Faz a requisição HTTP
            response = requests.get(
                f'https://api.imobiliaria.com/evolucao',
                params={'endereco': endereco},
                headers=headers
            )
            response.raise_for_status()
            
            # Retorna os dados de evolução
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados de evolução para o endereço {endereco}: {str(e)}")
            return {} 