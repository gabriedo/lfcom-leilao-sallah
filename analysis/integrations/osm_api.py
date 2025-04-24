import requests
import logging
from typing import Dict, Any, List, Tuple, Optional
from urllib.parse import quote
import time
from datetime import datetime
import os
from cache_manager import CacheManager
import math

logger = logging.getLogger(__name__)

class OSMAPI:
    def __init__(self):
        """Inicializa o integrador com a API do OpenStreetMap"""
        self.base_url = "https://nominatim.openstreetmap.org"
        self.headers = {
            'User-Agent': 'LFComLeilaoInsights/1.0 (contato@lfcom.com.br)'
        }
        self.cache = CacheManager(cache_dir="cache/osm")  # Cache para requisições
        self.last_request_time = 0
        self.min_request_interval = 1.0  # segundos entre requisições
        
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcula a distância em metros entre dois pontos usando a fórmula de Haversine.
        
        Args:
            lat1, lon1: Coordenadas do primeiro ponto
            lat2, lon2: Coordenadas do segundo ponto
            
        Returns:
            Distância em metros
        """
        R = 6371000  # Raio da Terra em metros
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_phi/2) * math.sin(delta_phi/2) +
             math.cos(phi1) * math.cos(phi2) *
             math.sin(delta_lambda/2) * math.sin(delta_lambda/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
        
    def _wait_for_rate_limit(self):
        """Espera o tempo necessário para respeitar o rate limit"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
            
        self.last_request_time = time.time()
        
    def search_location(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Busca informações de localização usando o Nominatim.
        
        Args:
            address: Endereço a ser pesquisado
            
        Returns:
            Dict com informações da localização ou None se não encontrado
        """
        try:
            self._wait_for_rate_limit()
            
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            
            response = requests.get(
                f"{self.base_url}/search",
                params=params,
                headers=self.headers
            )
            
            if response.status_code == 200:
                results = response.json()
                if results and len(results) > 0:
                    result = results[0]
                    return {
                        'lat': float(result['lat']),
                        'lon': float(result['lon']),
                        'display_name': result['display_name'],
                        'address': result.get('address', {})
                    }
                else:
                    logger.warning(f"Nenhum resultado encontrado para o endereço: {address}")
                    return None
            else:
                logger.error(f"Erro na requisição ao OSM: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao buscar localização: {str(e)}")
            return None
            
    def reverse_geocode(self, lat: float, lon: float) -> Dict[str, Any]:
        """Obtém informações de endereço a partir de coordenadas"""
        try:
            url = f"{self.base_url}/reverse"
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'addressdetails': 1
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'status': 'sucesso',
                'resultados': [{
                    'nome': data.get('display_name'),
                    'endereco': {
                        'rua': data.get('address', {}).get('road'),
                        'numero': data.get('address', {}).get('house_number'),
                        'bairro': data.get('address', {}).get('suburb'),
                        'cidade': data.get('address', {}).get('city'),
                        'estado': data.get('address', {}).get('state'),
                        'pais': data.get('address', {}).get('country'),
                        'cep': data.get('address', {}).get('postcode')
                    },
                    'city_code': data.get('address', {}).get('city_code')
                }]
            }
            
        except Exception as e:
            logger.error(f"Erro ao fazer geocodificação reversa: {str(e)}")
            return {
                'status': 'erro',
                'mensagem': str(e)
            }
            
    def get_pois_nearby(self, lat: float, lon: float, 
                       radius: int = 1000, 
                       categories: List[str] = None) -> Dict[str, Any]:
        """
        Obtém pontos de interesse próximos.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius: Raio de busca em metros
            categories: Lista de categorias de interesse
            
        Returns:
            Dict com pontos de interesse ou erro
        """
        # Verifica cache
        cached_data = self.cache.get("get_pois_nearby", lat=lat, lon=lon, radius=radius, categories=categories)
        if cached_data:
            return cached_data
            
        try:
            # Adiciona delay para respeitar limite de requisições
            time.sleep(1)
            
            # Categorias padrão se não especificadas
            if not categories:
                categories = [
                    "amenity",  # Serviços
                    "shop",     # Comércio
                    "leisure",  # Lazer
                    "tourism",  # Turismo
                    "building", # Edificações
                    "highway",  # Vias
                    "public_transport" # Transporte público
                ]
                
            pois = []
            for category in categories:
                response = requests.get(
                    f"{self.base_url}/search",
                    params={
                        "q": f"[{category}]",
                        "format": "json",
                        "limit": 50,
                        "viewbox": f"{lon-0.01},{lat-0.01},{lon+0.01},{lat+0.01}",
                        "bounded": 1
                    },
                    headers={"User-Agent": self.headers['User-Agent']}
                )
                response.raise_for_status()
                
                data = response.json()
                pois.extend([
                    {
                        "nome": item["display_name"],
                        "tipo": item["type"],
                        "categoria": category,
                        "coordenadas": {
                            "lat": float(item["lat"]),
                            "lon": float(item["lon"])
                        }
                    }
                    for item in data
                ])
                
            result = {
                "total": len(pois),
                "pontos_interesse": pois
            }
            
            # Armazena no cache
            self.cache.set("get_pois_nearby", result, lat=lat, lon=lon, radius=radius, categories=categories)
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar pontos de interesse: {str(e)}")
            return {
                "error": "Erro na consulta",
                "message": "Não foi possível buscar pontos de interesse"
            }
            
    def get_location_analysis(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Realiza análise completa de uma localização.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dict com análise completa da localização ou erro
        """
        # Verifica cache
        cached_data = self.cache.get("get_location_analysis", lat=lat, lon=lon)
        if cached_data:
            return cached_data
            
        try:
            # Obtém informações do endereço
            address = self.reverse_geocode(lat, lon)
            if "error" in address:
                return address
                
            # Obtém pontos de interesse próximos
            pois = self.get_pois_nearby(lat, lon)
            if "error" in pois:
                return pois
                
            # Categoriza pontos de interesse
            categorized_pois = {}
            for poi in pois["pontos_interesse"]:
                category = poi["categoria"]
                if category not in categorized_pois:
                    categorized_pois[category] = []
                categorized_pois[category].append(poi)
                
            return {
                "endereco": address,
                "pontos_interesse": {
                    "total": pois["total"],
                    "categorias": categorized_pois
                },
                "analise": {
                    "densidade_servicos": len(categorized_pois.get("amenity", [])),
                    "densidade_comercio": len(categorized_pois.get("shop", [])),
                    "densidade_lazer": len(categorized_pois.get("leisure", [])),
                    "densidade_turismo": len(categorized_pois.get("tourism", []))
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar localização: {str(e)}")
            return {
                "error": "Erro no processamento",
                "message": "Não foi possível analisar a localização"
            } 