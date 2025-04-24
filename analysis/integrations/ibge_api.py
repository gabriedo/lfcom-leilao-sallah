import requests
import logging
from typing import Dict, Any, List
from urllib.parse import quote

logger = logging.getLogger(__name__)

class IBGEAPI:
    def __init__(self):
        self.base_url = "https://servicodados.ibge.gov.br/api/v1"
        
    def get_city_info(self, city_code: str) -> Dict[str, Any]:
        """
        Obtém informações básicas de um município pelo código IBGE.
        
        Args:
            city_code: Código IBGE do município (7 dígitos)
            
        Returns:
            Dict com informações do município ou erro
        """
        try:
            response = requests.get(f"{self.base_url}/localidades/municipios/{city_code}")
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "id": data["id"],
                "nome": data["nome"],
                "microrregiao": {
                    "id": data["microrregiao"]["id"],
                    "nome": data["microrregiao"]["nome"],
                    "mesorregiao": {
                        "id": data["microrregiao"]["mesorregiao"]["id"],
                        "nome": data["microrregiao"]["mesorregiao"]["nome"],
                        "uf": {
                            "id": data["microrregiao"]["mesorregiao"]["UF"]["id"],
                            "sigla": data["microrregiao"]["mesorregiao"]["UF"]["sigla"],
                            "nome": data["microrregiao"]["mesorregiao"]["UF"]["nome"],
                            "regiao": {
                                "id": data["microrregiao"]["mesorregiao"]["UF"]["regiao"]["id"],
                                "sigla": data["microrregiao"]["mesorregiao"]["UF"]["regiao"]["sigla"],
                                "nome": data["microrregiao"]["mesorregiao"]["UF"]["regiao"]["nome"]
                            }
                        }
                    }
                }
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar município: {str(e)}")
            return {
                "error": "Erro na consulta",
                "message": "Não foi possível consultar o município"
            }
            
    def get_population(self, city_code: str) -> Dict[str, Any]:
        """
        Obtém dados populacionais de um município.
        
        Args:
            city_code: Código IBGE do município
            
        Returns:
            Dict com dados populacionais ou erro
        """
        try:
            response = requests.get(
                f"{self.base_url}/projecoes/populacao/{city_code}",
                params={"data": "2020"}  # Último censo disponível
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "populacao": data["projecao"]["populacao"],
                "ano": data["projecao"]["ano"],
                "periodo": data["projecao"]["periodo"]
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar população: {str(e)}")
            return {
                "error": "Erro na consulta",
                "message": "Não foi possível consultar dados populacionais"
            }
            
    def get_economic_data(self, city_code: str) -> Dict[str, Any]:
        """
        Obtém dados econômicos de um município.
        
        Args:
            city_code: Código IBGE do município
            
        Returns:
            Dict com dados econômicos ou erro
        """
        try:
            # PIB per capita
            pib_response = requests.get(
                f"{self.base_url}/economia/pib-municipios/{city_code}",
                params={"ano": "2020"}  # Último ano disponível
            )
            pib_response.raise_for_status()
            pib_data = pib_response.json()
            
            # IDH
            idh_response = requests.get(
                f"{self.base_url}/indicadores/idh/{city_code}"
            )
            idh_response.raise_for_status()
            idh_data = idh_response.json()
            
            return {
                "pib_per_capita": pib_data.get("valor", 0),
                "idh": idh_data.get("valor", 0),
                "ano": "2020"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar dados econômicos: {str(e)}")
            return {
                "error": "Erro na consulta",
                "message": "Não foi possível consultar dados econômicos"
            }
            
    def get_indicators(self, city_code: str) -> Dict[str, Any]:
        """
        Obtém indicadores socioeconômicos de um município.
        
        Args:
            city_code: Código IBGE do município
            
        Returns:
            Dict com indicadores ou erro
        """
        try:
            # Taxa de desemprego
            desemprego_response = requests.get(
                f"{self.base_url}/indicadores/desemprego/{city_code}"
            )
            desemprego_response.raise_for_status()
            desemprego_data = desemprego_response.json()
            
            # Renda média
            renda_response = requests.get(
                f"{self.base_url}/indicadores/renda-media/{city_code}"
            )
            renda_response.raise_for_status()
            renda_data = renda_response.json()
            
            return {
                "taxa_desemprego": desemprego_data.get("valor", 0),
                "renda_media": renda_data.get("valor", 0),
                "ano": "2020"
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar indicadores: {str(e)}")
            return {
                "error": "Erro na consulta",
                "message": "Não foi possível consultar indicadores"
            }
            
    def get_complete_city_data(self, city_code: str) -> Dict[str, Any]:
        """
        Obtém todos os dados disponíveis de um município.
        
        Args:
            city_code: Código IBGE do município
            
        Returns:
            Dict com todos os dados disponíveis ou erro
        """
        try:
            city_info = self.get_city_info(city_code)
            if "error" in city_info:
                return city_info
                
            population = self.get_population(city_code)
            economic = self.get_economic_data(city_code)
            indicators = self.get_indicators(city_code)
            
            return {
                "informacoes_gerais": city_info,
                "dados_populacionais": population,
                "dados_economicos": economic,
                "indicadores": indicators
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter dados completos: {str(e)}")
            return {
                "error": "Erro no processamento",
                "message": "Não foi possível obter os dados completos"
            } 