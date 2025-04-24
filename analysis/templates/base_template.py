from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

class LeilaoTemplate(ABC):
    """Classe base para templates de extração de dados de sites de leilão"""
    
    def __init__(self):
        """Inicializa o template"""
        self.logger = logging.getLogger(__name__)
        
    @abstractmethod
    def validar_url(self, url: str) -> bool:
        """Verifica se a URL é do site específico"""
        pass
        
    @abstractmethod
    def extrair_dados(self, url: str) -> Dict[str, Any]:
        """Extrai dados do imóvel do site específico"""
        pass
        
    def _validar_url(self, url: str) -> bool:
        """Valida se a URL é válida"""
        if not url or not isinstance(url, str):
            return False
        return url.startswith(('http://', 'https://'))
        
    def _fazer_requisicao(self, url: str) -> Optional[str]:
        """Faz requisição HTTP para a URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.logger.error(f"Erro ao fazer requisição: {str(e)}")
            return None
            
    def _parse_html(self, html: str) -> Optional[BeautifulSoup]:
        """Faz o parse do HTML"""
        try:
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            self.logger.error(f"Erro ao fazer parse do HTML: {str(e)}")
            return None
            
    def _extrair_texto(self, elemento) -> Optional[str]:
        """Extrai texto de um elemento BeautifulSoup"""
        if not elemento:
            return None
        try:
            return elemento.get_text(strip=True)
        except Exception as e:
            self.logger.error(f"Erro ao extrair texto: {str(e)}")
            return None
            
    def _extrair_valor(self, texto: str) -> Optional[float]:
        """Extrai valor numérico de um texto"""
        if not texto:
            return None
        try:
            # Remove caracteres não numéricos exceto ponto e vírgula
            valor = re.sub(r'[^\d,.]', '', texto)
            # Substitui vírgula por ponto
            valor = valor.replace(',', '.')
            return float(valor)
        except Exception as e:
            self.logger.error(f"Erro ao extrair valor: {str(e)}")
            return None

    def _extrair_area(self, texto: str) -> Optional[float]:
        """Extrai área em m² de uma string"""
        try:
            # Remove 'm²' e espaços
            texto = texto.replace('m²', '').strip()
            # Remove pontos de milhar
            texto = texto.replace('.', '')
            # Substitui vírgula por ponto
            texto = texto.replace(',', '.')
            return float(texto)
        except Exception:
            return None 