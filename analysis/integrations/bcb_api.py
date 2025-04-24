import requests
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class BCBAPI:
    def __init__(self):
        self.base_url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs"
        
    def get_selic_rate(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Obtém a taxa SELIC histórica.
        
        Args:
            start_date: Data inicial no formato dd/mm/yyyy
            end_date: Data final no formato dd/mm/yyyy
            
        Returns:
            Dict com dados da SELIC ou erro
        """
        try:
            # Se não fornecidas datas, usa últimos 12 meses
            if not start_date or not end_date:
                end_date = datetime.now().strftime("%d/%m/%Y")
                start_date = (datetime.now() - timedelta(days=365)).strftime("%d/%m/%Y")
                
            response = requests.get(
                f"{self.base_url}.11/dados",
                params={
                    "formato": "json",
                    "dataInicial": start_date,
                    "dataFinal": end_date
                }
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "periodo": {
                    "inicio": start_date,
                    "fim": end_date
                },
                "dados": [
                    {
                        "data": item["data"],
                        "valor": item["valor"]
                    }
                    for item in data
                ]
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar SELIC: {str(e)}")
            return {
                "error": "Erro na consulta",
                "message": "Não foi possível consultar a taxa SELIC"
            }
            
    def get_inflation(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Obtém dados de inflação (IPCA).
        
        Args:
            start_date: Data inicial no formato dd/mm/yyyy
            end_date: Data final no formato dd/mm/yyyy
            
        Returns:
            Dict com dados de inflação ou erro
        """
        try:
            if not start_date or not end_date:
                end_date = datetime.now().strftime("%d/%m/%Y")
                start_date = (datetime.now() - timedelta(days=365)).strftime("%d/%m/%Y")
                
            response = requests.get(
                f"{self.base_url}.433/dados",
                params={
                    "formato": "json",
                    "dataInicial": start_date,
                    "dataFinal": end_date
                }
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "periodo": {
                    "inicio": start_date,
                    "fim": end_date
                },
                "dados": [
                    {
                        "data": item["data"],
                        "valor": item["valor"]
                    }
                    for item in data
                ]
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar inflação: {str(e)}")
            return {
                "error": "Erro na consulta",
                "message": "Não foi possível consultar dados de inflação"
            }
            
    def get_exchange_rate(self, currency: str = "USD", 
                         start_date: str = None, 
                         end_date: str = None) -> Dict[str, Any]:
        """
        Obtém dados de câmbio.
        
        Args:
            currency: Moeda (USD, EUR, etc)
            start_date: Data inicial no formato dd/mm/yyyy
            end_date: Data final no formato dd/mm/yyyy
            
        Returns:
            Dict com dados de câmbio ou erro
        """
        try:
            if not start_date or not end_date:
                end_date = datetime.now().strftime("%d/%m/%Y")
                start_date = (datetime.now() - timedelta(days=30)).strftime("%d/%m/%Y")
                
            # Mapeamento de moedas para códigos BCB
            currency_codes = {
                "USD": 1,
                "EUR": 21619,
                "GBP": 21620
            }
            
            code = currency_codes.get(currency.upper(), 1)  # Default para USD
            
            response = requests.get(
                f"{self.base_url}.{code}/dados",
                params={
                    "formato": "json",
                    "dataInicial": start_date,
                    "dataFinal": end_date
                }
            )
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "moeda": currency.upper(),
                "periodo": {
                    "inicio": start_date,
                    "fim": end_date
                },
                "dados": [
                    {
                        "data": item["data"],
                        "valor": item["valor"]
                    }
                    for item in data
                ]
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar câmbio: {str(e)}")
            return {
                "error": "Erro na consulta",
                "message": "Não foi possível consultar dados de câmbio"
            }
            
    def get_economic_indicators(self) -> Dict[str, Any]:
        """
        Obtém os principais indicadores econômicos.
        
        Returns:
            Dict com indicadores econômicos ou erro
        """
        try:
            # Taxa SELIC atual
            selic = self.get_selic_rate()
            if "error" in selic:
                return selic
                
            # Inflação acumulada 12 meses
            inflacao = self.get_inflation()
            if "error" in inflacao:
                return inflacao
                
            # Câmbio atual
            cambio = self.get_exchange_rate()
            if "error" in cambio:
                return cambio
                
            return {
                "selic": selic["dados"][-1]["valor"] if selic["dados"] else None,
                "inflacao_12m": sum(item["valor"] for item in inflacao["dados"][-12:]) if inflacao["dados"] else None,
                "cambio_usd": cambio["dados"][-1]["valor"] if cambio["dados"] else None,
                "data_atualizacao": datetime.now().strftime("%d/%m/%Y")
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter indicadores: {str(e)}")
            return {
                "error": "Erro no processamento",
                "message": "Não foi possível obter os indicadores econômicos"
            } 