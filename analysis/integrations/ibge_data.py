import requests
import logging
from typing import Dict, Any, Optional
from functools import lru_cache

logger = logging.getLogger(__name__)

class IBGEDataCollector:
    """
    Classe para coletar dados do IBGE através da API pública.
    """
    
    def __init__(self):
        self.base_url = "https://servicodados.ibge.gov.br/api/v3"
        
    @lru_cache(maxsize=128)
    def get_municipio_data(self, codigo_municipio: str) -> Dict[str, Any]:
        """
        Obtém dados demográficos e econômicos do município
        """
        try:
            dados = {
                "demografia": self._get_dados_demograficos(codigo_municipio),
                "economia": self._get_dados_economicos(codigo_municipio),
                "indicadores": self._get_indicadores_sociais(codigo_municipio)
            }
            return dados
        except Exception as e:
            logger.error(f"Erro ao obter dados do IBGE: {str(e)}")
            return {}

    def _get_dados_demograficos(self, codigo_municipio: str) -> Dict[str, Any]:
        """
        Obtém dados demográficos usando o agregado 6579 (População residente)
        """
        try:
            url = f"{self.base_url}/agregados/6579/periodos/-1/variaveis/93?localidades=N6[{codigo_municipio}]"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    "populacao": data[0]["resultados"][0]["series"][0]["serie"],
                    "densidade_demografica": self._calcular_densidade(data)
                }
            return {}
        except Exception as e:
            logger.error(f"Erro ao obter dados demográficos: {str(e)}")
            return {}

    def _get_dados_economicos(self, codigo_municipio: str) -> Dict[str, Any]:
        """
        Obtém dados econômicos usando o agregado 5938 (PIB dos Municípios)
        """
        try:
            url = f"{self.base_url}/agregados/5938/periodos/-1/variaveis/37?localidades=N6[{codigo_municipio}]"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    "pib": data[0]["resultados"][0]["series"][0]["serie"],
                    "pib_per_capita": self._calcular_pib_per_capita(data)
                }
            return {}
        except Exception as e:
            logger.error(f"Erro ao obter dados econômicos: {str(e)}")
            return {}

    def _get_indicadores_sociais(self, codigo_municipio: str) -> Dict[str, Any]:
        """
        Obtém indicadores sociais usando o agregado 1384 (Rendimento médio mensal)
        """
        try:
            url = f"{self.base_url}/agregados/1384/periodos/-1/variaveis/93?localidades=N6[{codigo_municipio}]"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    "renda_media": data[0]["resultados"][0]["series"][0]["serie"],
                    "indice_desenvolvimento": self._calcular_idh(data)
                }
            return {}
        except Exception as e:
            logger.error(f"Erro ao obter indicadores sociais: {str(e)}")
            return {}

    def _calcular_densidade(self, data: Dict) -> float:
        """Calcula a densidade demográfica"""
        try:
            populacao = float(data[0]["resultados"][0]["series"][0]["serie"]["2022"])
            area = 100  # Área em km² (exemplo - idealmente buscar da API)
            return round(populacao / area, 2)
        except:
            return 0.0

    def _calcular_pib_per_capita(self, data: Dict) -> float:
        """Calcula o PIB per capita"""
        try:
            pib = float(data[0]["resultados"][0]["series"][0]["serie"]["2022"])
            populacao = 100000  # População (exemplo - idealmente buscar da API)
            return round(pib / populacao, 2)
        except:
            return 0.0

    def _calcular_idh(self, data: Dict) -> float:
        """Calcula um índice de desenvolvimento simplificado"""
        try:
            renda = float(data[0]["resultados"][0]["series"][0]["serie"]["2022"])
            return round(min(renda / 10000, 1), 3)
        except:
            return 0.0

    @lru_cache(maxsize=128)
    def get_codigo_municipio(self, nome_municipio: str, uf: str) -> Optional[str]:
        """
        Obtém o código do município a partir do nome e UF
        """
        try:
            url = f"{self.base_url}/localidades/municipios"
            response = requests.get(url)
            if response.status_code == 200:
                municipios = response.json()
                for municipio in municipios:
                    if (municipio["nome"].lower() == nome_municipio.lower() and 
                        municipio["microrregiao"]["mesorregiao"]["UF"]["sigla"] == uf.upper()):
                        return municipio["id"]
            return None
        except Exception as e:
            logger.error(f"Erro ao obter código do município: {str(e)}")
            return None 