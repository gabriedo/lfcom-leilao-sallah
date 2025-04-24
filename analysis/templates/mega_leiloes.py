from bs4 import BeautifulSoup
import requests
import re
import logging
from typing import Dict, Any
from .base_template import LeilaoTemplate

class MegaLeiloesTemplate(LeilaoTemplate):
    """Template para extração de dados do site Mega Leilões"""
    
    def __init__(self):
        """Inicializa o template"""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
    def validar_url(self, url: str) -> bool:
        """Verifica se a URL é do site Mega Leilões"""
        return 'megaleiloes.com.br' in url.lower()
        
    def extrair_dados(self, url: str) -> Dict[str, Any]:
        """Extrai dados do imóvel do site Mega Leilões"""
        try:
            self.logger.info(f"Iniciando extração de dados da URL: {url}")
            
            # Configuração do header para simular um navegador
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
            }
            
            # Faz a requisição HTTP
            self.logger.debug("Fazendo requisição HTTP...")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse do HTML
            self.logger.debug("Fazendo parse do HTML...")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extração dos dados
            dados = {}
            
            # Título
            titulo_elem = soup.find('h1', class_='property-title') or soup.find('h1', class_='titulo-imovel') or soup.find('h1')
            if titulo_elem:
                dados['titulo'] = titulo_elem.text.strip()
                self.logger.debug(f"Título encontrado: {dados['titulo']}")
            
            # Tipo do imóvel
            tipo_elem = soup.find('div', text=re.compile('Tipo:', re.IGNORECASE))
            if tipo_elem:
                dados['tipo_imovel'] = tipo_elem.find_next('div').text.strip()
                self.logger.debug(f"Tipo do imóvel encontrado: {dados['tipo_imovel']}")
            
            # Endereço
            endereco_elem = soup.find('div', text=re.compile('Endereço:', re.IGNORECASE))
            if endereco_elem:
                dados['endereco'] = endereco_elem.find_next('div').text.strip()
                self.logger.debug(f"Endereço encontrado: {dados['endereco']}")
            
            # Lance mínimo
            lance_elem = soup.find('div', text=re.compile('Lance mínimo:', re.IGNORECASE))
            if lance_elem:
                dados['valor_inicial'] = self._extrair_valor(lance_elem.find_next('div').text)
                self.logger.debug(f"Lance mínimo encontrado: {dados['valor_inicial']}")
            
            # Valor avaliado
            avaliacao_elem = soup.find('div', text=re.compile('Valor avaliado:', re.IGNORECASE))
            if avaliacao_elem:
                dados['valor_avaliacao'] = self._extrair_valor(avaliacao_elem.find_next('div').text)
                self.logger.debug(f"Valor avaliado encontrado: {dados['valor_avaliacao']}")
            
            # Data do leilão
            data_elem = soup.find('div', text=re.compile('Data do leilão:', re.IGNORECASE))
            if data_elem:
                dados['data_leilao'] = data_elem.find_next('div').text.strip()
                self.logger.debug(f"Data do leilão encontrada: {dados['data_leilao']}")
            
            # Tipo de leilão
            tipo_leilao_elem = soup.find('div', text=re.compile('Tipo de leilão:', re.IGNORECASE))
            if tipo_leilao_elem:
                dados['tipo_leilao'] = tipo_leilao_elem.find_next('div').text.strip()
                self.logger.debug(f"Tipo de leilão encontrado: {dados['tipo_leilao']}")
            
            # Número do processo
            processo_elem = soup.find('div', text=re.compile('Processo:', re.IGNORECASE))
            if processo_elem:
                dados['numero_processo'] = processo_elem.find_next('div').text.strip()
                self.logger.debug(f"Número do processo encontrado: {dados['numero_processo']}")
            
            # Links de documentos
            docs_container = soup.find('div', text=re.compile('Documentos:', re.IGNORECASE))
            dados['documentos'] = []
            if docs_container:
                links = docs_container.find_next('div').find_all('a', href=True)
                dados['documentos'] = [link['href'] for link in links if link['href'].lower().endswith(('.pdf', '.doc', '.docx'))]
                self.logger.debug(f"Documentos encontrados: {len(dados['documentos'])}")
            
            self.logger.info("Extração de dados concluída com sucesso")
            return dados
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erro na requisição HTTP: {str(e)}")
            return {'erro': f"Erro ao acessar a URL: {str(e)}"}
        except Exception as e:
            self.logger.error(f"Erro ao extrair dados: {str(e)}", exc_info=True)
            return {'erro': f"Erro na extração: {str(e)}"}
            
    def _extrair_valor(self, texto: str) -> float:
        """Extrai valor numérico de um texto"""
        try:
            # Remove caracteres não numéricos exceto ponto e vírgula
            valor_str = re.sub(r'[^\d.,]', '', texto)
            # Substitui vírgula por ponto e converte para float
            return float(valor_str.replace('.', '').replace(',', '.'))
        except Exception as e:
            self.logger.error(f"Erro ao extrair valor de '{texto}': {str(e)}")
            return None 