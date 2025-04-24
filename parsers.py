from typing import Dict, Any, Optional
import re
import logging
import json
from datetime import datetime
from decimal import Decimal
from bs4 import BeautifulSoup
import requests
from openai import OpenAI
import os
from dotenv import load_dotenv
from config import OPENAI_API_KEY, OPENAI_MODEL

# Carrega variáveis de ambiente
load_dotenv()

logger = logging.getLogger(__name__)

class DocumentParser:
    def __init__(self):
        """Inicializa o parser de documentos"""
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
    def parse_edital(self, edital_texto: str) -> Dict[str, Any]:
        """
        Analisa o texto do edital usando IA e extração de padrões.
        
        Args:
            edital_texto: Texto completo do edital
            
        Returns:
            Dict com informações extraídas do edital
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise de editais de leilão de imóveis."},
                    {"role": "user", "content": f"Analise o seguinte edital e extraia as informações relevantes: {edital_texto}"}
                ]
            )
            
            return {
                'resumo': response.choices[0].message.content,
                'status': 'sucesso'
            }
            
        except Exception as e:
            logger.error(f"Erro na análise com IA: {str(e)}")
            return {
                'resumo': None,
                'status': 'erro',
                'mensagem': str(e)
            }
            
    def parse_matricula(self, matricula_texto: str) -> Dict[str, Any]:
        """
        Analisa o texto da matrícula usando IA e extração de padrões.
        
        Args:
            matricula_texto: Texto completo da matrícula
            
        Returns:
            Dict com informações extraídas da matrícula
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise de matrículas de imóveis."},
                    {"role": "user", "content": f"Analise a seguinte matrícula e extraia as informações relevantes: {matricula_texto}"}
                ]
            )
            
            return {
                'resumo': response.choices[0].message.content,
                'status': 'sucesso'
            }
            
        except Exception as e:
            logger.error(f"Erro na análise com IA: {str(e)}")
            return {
                'resumo': None,
                'status': 'erro',
                'mensagem': str(e)
            }
            
    def extract_from_url(self, url: str) -> Dict[str, Any]:
        """
        Extrai informações de uma URL usando web scraping e IA.
        
        Args:
            url: URL do imóvel
            
        Returns:
            Dict com informações extraídas da URL
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extrai informações básicas
            dados = {
                'titulo': soup.title.string if soup.title else None,
                'descricao': soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else None,
                'imagens': [img['src'] for img in soup.find_all('img') if img.get('src')],
                'links': [a['href'] for a in soup.find_all('a') if a.get('href')]
            }
            
            return dados
            
        except Exception as e:
            logger.error(f"Erro ao extrair informações da URL: {str(e)}")
            return {
                'status': 'erro',
                'mensagem': str(e)
            }
            
    def _normalizar_valor(self, chave: str, valor: str) -> Any:
        """Normaliza valores extraídos de acordo com seu tipo."""
        try:
            if chave in ['valor_inicial', 'dividas_condominiais', 'dividas_fiscais']:
                # Remove R$, pontos e converte vírgula para ponto
                valor_limpo = valor.replace('R$', '').replace('.', '').replace(',', '.')
                return float(valor_limpo)
                
            elif chave in ['area']:
                # Remove m² e converte para float
                valor_limpo = valor.replace('m²', '').replace('.', '').replace(',', '.')
                return float(valor_limpo)
                
            elif chave in ['data_leilao']:
                # Converte para datetime
                return datetime.strptime(valor, '%d/%m/%Y').isoformat()
                
            elif chave in ['hora_leilao']:
                # Mantém como string HH:MM
                return valor
                
            else:
                # Retorna string normalizada
                return valor.strip()
                
        except Exception as e:
            logger.warning(f"Erro ao normalizar valor {valor} para {chave}: {str(e)}")
            return valor
            
    def _combinar_resultados(self, regex_results: Dict[str, Any], ia_results: Dict[str, Any]) -> Dict[str, Any]:
        """Combina e valida resultados da extração por regex e análise IA."""
        resultado = {
            'dados_basicos': regex_results,
            'analise_detalhada': ia_results,
            'alertas': [],
            'inconsistencias': []
        }
        
        # Verifica inconsistências entre regex e IA
        for chave in regex_results:
            if chave in ia_results and regex_results[chave] != ia_results[chave]:
                resultado['inconsistencias'].append({
                    'campo': chave,
                    'valor_regex': regex_results[chave],
                    'valor_ia': ia_results[chave]
                })
        
        # Adiciona alertas baseados na análise
        if ia_results.get('penhoras_ativas'):
            resultado['alertas'].append("Imóvel com penhora ativa")
        if ia_results.get('dividas_condominiais'):
            resultado['alertas'].append(f"Existem dívidas condominiais: R$ {ia_results['dividas_condominiais']}")
        if ia_results.get('dividas_fiscais'):
            resultado['alertas'].append(f"Existem dívidas fiscais: R$ {ia_results['dividas_fiscais']}")
        if ia_results.get('ocupacao') == 'ocupado':
            resultado['alertas'].append("Imóvel ocupado - verificar condições de desocupação")
            
        return resultado 