import os
import requests
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

logger = logging.getLogger(__name__)

class GeographicData:
    """Classe para integração com dados geográficos"""
    
    def __init__(self, openweather_api_key: str, google_maps_api_key: str):
        """Inicializa a integração com dados geográficos"""
        self.openweather_api_key = openweather_api_key
        self.google_maps_api_key = google_maps_api_key
        self.logger = logging.getLogger(__name__)
        
    def obter_dados_ibge(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Obtém dados do IBGE para as coordenadas"""
        try:
            # Faz a requisição HTTP para a API do IBGE
            response = requests.get(
                f'https://servicodados.ibge.gov.br/api/v1/localidades/coordenadas/{latitude},{longitude}'
            )
            response.raise_for_status()
            
            # Retorna os dados do IBGE
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do IBGE: {str(e)}")
            return {}
            
    def obter_dados_clima(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Obtém dados climáticos para as coordenadas"""
        try:
            # Faz a requisição HTTP para a API do OpenWeather
            response = requests.get(
                f'https://api.openweathermap.org/data/2.5/weather',
                params={
                    'lat': latitude,
                    'lon': longitude,
                    'appid': self.openweather_api_key,
                    'units': 'metric',
                    'lang': 'pt_br'
                }
            )
            response.raise_for_status()
            
            # Retorna os dados climáticos
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados climáticos: {str(e)}")
            return {}
            
    def obter_dados_ambientais(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Obtém dados ambientais para as coordenadas"""
        try:
            # Faz a requisição HTTP para a API do Google Maps
            response = requests.get(
                f'https://maps.googleapis.com/maps/api/geocode/json',
                params={
                    'latlng': f'{latitude},{longitude}',
                    'key': self.google_maps_api_key
                }
            )
            response.raise_for_status()
            
            # Processa os dados ambientais
            dados = response.json()
            if dados.get('results'):
                endereco = dados['results'][0]
                
                # Extrai informações relevantes
                dados_ambientais = {
                    'endereco': endereco.get('formatted_address'),
                    'componentes': {}
                }
                
                # Processa os componentes do endereço
                for componente in endereco.get('address_components', []):
                    tipos = componente.get('types', [])
                    nome = componente.get('long_name')
                    
                    if 'administrative_area_level_1' in tipos:
                        dados_ambientais['componentes']['estado'] = nome
                    elif 'administrative_area_level_2' in tipos:
                        dados_ambientais['componentes']['cidade'] = nome
                    elif 'sublocality' in tipos:
                        dados_ambientais['componentes']['bairro'] = nome
                    elif 'route' in tipos:
                        dados_ambientais['componentes']['rua'] = nome
                        
                return dados_ambientais
                
            return {}
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados ambientais: {str(e)}")
            return {}
            
    def obter_dados_completos(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Obtém todos os dados geográficos para as coordenadas"""
        try:
            # Obtém dados do IBGE
            dados_ibge = self.obter_dados_ibge(latitude, longitude)
            
            # Obtém dados climáticos
            dados_clima = self.obter_dados_clima(latitude, longitude)
            
            # Obtém dados ambientais
            dados_ambientais = self.obter_dados_ambientais(latitude, longitude)
            
            # Compila todos os dados
            dados = {
                'ibge': dados_ibge,
                'clima': dados_clima,
                'ambientais': dados_ambientais
            }
            
            return dados
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados geográficos completos: {str(e)}")
            return {} 