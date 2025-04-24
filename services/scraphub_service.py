import os
import requests
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ScraphubService:
    def __init__(self):
        self.base_url = "https://scraphub.comercify.shop/api"
        self.api_key = os.getenv("SCRAPHUB_API_KEY")
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def get_items(self, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Busca itens da API do Scraphub com paginação
        
        Args:
            page (int): Número da página
            per_page (int): Quantidade de itens por página
            
        Returns:
            Dict[str, Any]: Resposta da API com os itens
        """
        try:
            url = f"{self.base_url}/items/2/?page={page}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar itens do Scraphub: {str(e)}")
            raise

    def get_item_details(self, item_id: str) -> Dict[str, Any]:
        """
        Busca detalhes de um item específico
        
        Args:
            item_id (str): ID do item
            
        Returns:
            Dict[str, Any]: Detalhes do item
        """
        try:
            url = f"{self.base_url}/items/{item_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar detalhes do item {item_id}: {str(e)}")
            raise

# Exemplo de uso
if __name__ == "__main__":
    service = ScraphubService()
    try:
        items = service.get_items(page=1)
        print(items)
    except Exception as e:
        print(f"Erro: {str(e)}") 