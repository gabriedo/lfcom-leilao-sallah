import requests
import logging
from typing import Dict, Any, Optional
from urllib.parse import quote

logger = logging.getLogger(__name__)

class AddressAPI:
    def __init__(self):
        self.base_url = "https://viacep.com.br/ws"
        
    def get_address_info(self, cep: str) -> Dict[str, Any]:
        """
        Busca informações de endereço pelo CEP usando a API ViaCEP.
        
        Args:
            cep: CEP no formato 00000000 (apenas números)
            
        Returns:
            Dict com informações do endereço ou erro
        """
        try:
            # Remove caracteres não numéricos
            cep = ''.join(filter(str.isdigit, cep))
            
            if len(cep) != 8:
                return {
                    "error": "CEP inválido",
                    "message": "O CEP deve conter 8 dígitos"
                }
                
            response = requests.get(f"{self.base_url}/{cep}/json/")
            response.raise_for_status()
            
            data = response.json()
            
            if "erro" in data:
                return {
                    "error": "CEP não encontrado",
                    "message": "O CEP informado não existe"
                }
                
            return {
                "cep": data["cep"],
                "logradouro": data["logradouro"],
                "complemento": data["complemento"],
                "bairro": data["bairro"],
                "cidade": data["localidade"],
                "estado": data["uf"],
                "ibge": data["ibge"],
                "gia": data["gia"],
                "ddd": data["ddd"],
                "siafi": data["siafi"]
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar CEP: {str(e)}")
            return {
                "error": "Erro na consulta",
                "message": "Não foi possível consultar o CEP"
            }
            
    def search_address(self, uf: str, cidade: str, logradouro: str) -> Dict[str, Any]:
        """
        Busca CEP por endereço usando a API ViaCEP.
        
        Args:
            uf: Sigla do estado (ex: SP)
            cidade: Nome da cidade
            logradouro: Nome do logradouro
            
        Returns:
            Lista de endereços encontrados ou erro
        """
        try:
            # Codifica os parâmetros para URL
            uf = quote(uf.upper())
            cidade = quote(cidade)
            logradouro = quote(logradouro)
            
            response = requests.get(
                f"{self.base_url}/{uf}/{cidade}/{logradouro}/json/"
            )
            response.raise_for_status()
            
            data = response.json()
            
            if isinstance(data, dict) and "erro" in data:
                return {
                    "error": "Endereço não encontrado",
                    "message": "Nenhum endereço encontrado com os parâmetros informados"
                }
                
            # Se retornar apenas um resultado, converte para lista
            if isinstance(data, dict):
                data = [data]
                
            return {
                "results": [
                    {
                        "cep": item["cep"],
                        "logradouro": item["logradouro"],
                        "complemento": item["complemento"],
                        "bairro": item["bairro"],
                        "cidade": item["localidade"],
                        "estado": item["uf"]
                    }
                    for item in data
                ]
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar endereço: {str(e)}")
            return {
                "error": "Erro na consulta",
                "message": "Não foi possível buscar o endereço"
            }
            
    def enrich_address(self, address: str) -> Dict[str, Any]:
        """
        Tenta enriquecer um endereço com informações adicionais.
        
        Args:
            address: Endereço completo
            
        Returns:
            Dict com endereço enriquecido ou erro
        """
        try:
            # Tenta extrair CEP do endereço
            cep = ''.join(filter(str.isdigit, address))
            if len(cep) == 8:
                return self.get_address_info(cep)
                
            # Se não encontrar CEP, tenta buscar por partes do endereço
            parts = address.split(',')
            if len(parts) >= 2:
                logradouro = parts[0].strip()
                cidade_estado = parts[1].strip().split('-')
                if len(cidade_estado) == 2:
                    cidade = cidade_estado[0].strip()
                    uf = cidade_estado[1].strip()
                    return self.search_address(uf, cidade, logradouro)
                    
            return {
                "error": "Endereço inválido",
                "message": "Não foi possível processar o endereço informado"
            }
            
        except Exception as e:
            logger.error(f"Erro ao enriquecer endereço: {str(e)}")
            return {
                "error": "Erro no processamento",
                "message": "Não foi possível processar o endereço"
            } 