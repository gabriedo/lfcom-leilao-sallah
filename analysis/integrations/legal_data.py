import requests
import logging
from typing import Dict, Any, Optional

class LegalData:
    """Classe para integração com dados jurídicos"""
    
    def __init__(self, api_key: str):
        """Inicializa a integração com dados jurídicos"""
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        
    def obter_dados_processo(self, numero_processo: str) -> Dict[str, Any]:
        """Obtém dados de um processo judicial"""
        try:
            # Configuração do header com a API key
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Faz a requisição HTTP
            response = requests.get(
                f'https://api.judicial.com/processos/{numero_processo}',
                headers=headers
            )
            response.raise_for_status()
            
            # Retorna os dados do processo
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do processo {numero_processo}: {str(e)}")
            return {}
            
    def obter_dados_matricula(self, numero_matricula: str) -> Dict[str, Any]:
        """Obtém dados de uma matrícula imobiliária"""
        try:
            # Configuração do header com a API key
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Faz a requisição HTTP
            response = requests.get(
                f'https://api.registral.com/matriculas/{numero_matricula}',
                headers=headers
            )
            response.raise_for_status()
            
            # Retorna os dados da matrícula
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados da matrícula {numero_matricula}: {str(e)}")
            return {}
            
    def obter_dados_tribunal(self, sigla_tribunal: str) -> Dict[str, Any]:
        """Obtém dados de um tribunal"""
        try:
            # Configuração do header com a API key
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Faz a requisição HTTP
            response = requests.get(
                f'https://api.judicial.com/tribunais/{sigla_tribunal}',
                headers=headers
            )
            response.raise_for_status()
            
            # Retorna os dados do tribunal
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do tribunal {sigla_tribunal}: {str(e)}")
            return {} 