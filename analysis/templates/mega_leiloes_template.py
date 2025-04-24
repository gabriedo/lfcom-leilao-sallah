from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import re
from .base_template import LeilaoTemplate

class MegaLeiloesTemplate(LeilaoTemplate):
    """Template para extração de dados do site Mega Leilões"""
    
    def pode_processar(self, url: str) -> bool:
        """Verifica se a URL é do Mega Leilões"""
        return 'megaleiloes.com.br' in url.lower()
        
    def extrair_dados(self, url: str) -> Dict[str, Any]:
        """Extrai dados do imóvel do Mega Leilões"""
        if not self._validar_url(url):
            self.logger.error("URL inválida")
            return {}
            
        html = self._fazer_requisicao(url)
        if not html:
            return {}
            
        soup = self._parse_html(html)
        if not soup:
            return {}
            
        try:
            # Extrai título
            titulo = self._extrair_texto(soup.find('h1', class_='titulo-imovel'))
            
            # Extrai endereço
            endereco = self._extrair_texto(soup.find('div', class_='endereco'))
            
            # Extrai descrição
            descricao = self._extrair_texto(soup.find('div', class_='descricao'))
            
            # Extrai valores
            valores = soup.find_all('div', class_='valor')
            valor_inicial = None
            valor_avaliacao = None
            for valor in valores:
                texto = self._extrair_texto(valor)
                if 'valor inicial' in texto.lower():
                    valor_inicial = self._extrair_valor(texto)
                elif 'valor de avaliação' in texto.lower():
                    valor_avaliacao = self._extrair_valor(texto)
                    
            # Extrai tipo de leilão
            tipo_leilao = self._extrair_texto(soup.find('div', class_='tipo-leilao'))
            
            # Extrai data do leilão
            data_leilao = self._extrair_texto(soup.find('div', class_='data-leilao'))
            
            # Extrai número do processo
            processo = self._extrair_texto(soup.find('div', class_='numero-processo'))
            
            # Extrai vara/foro
            vara = self._extrair_texto(soup.find('div', class_='vara'))
            
            # Extrai área usando regex
            area = None
            if descricao:
                match = re.search(r'(\d+(?:\.\d+)?)\s*m²', descricao)
                if match:
                    area = float(match.group(1))
                    
            # Extrai número de matrícula usando regex
            matricula = None
            if descricao:
                match = re.search(r'matr[íi]cula\s*[nºN]\s*(\d+)', descricao, re.IGNORECASE)
                if match:
                    matricula = match.group(1)
                    
            # Extrai links de documentos
            documentos = []
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                if any(ext in href.lower() for ext in ['.pdf', '.doc', '.docx']):
                    documentos.append(href)
                    
            return {
                'titulo': titulo,
                'endereco': endereco,
                'descricao': descricao,
                'valor_inicial': valor_inicial,
                'valor_avaliacao': valor_avaliacao,
                'tipo_leilao': tipo_leilao,
                'data_leilao': data_leilao,
                'processo': processo,
                'vara': vara,
                'area': area,
                'matricula': matricula,
                'documentos': documentos
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair dados: {str(e)}")
            return {} 