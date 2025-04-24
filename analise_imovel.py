import os
from dotenv import load_dotenv
from openai import OpenAI
from config import logger, OPENAI_API_KEY, OPENAI_MODEL, OPENWEATHER_API_KEY, GOOGLE_MAPS_API_KEY, LEGAL_API_KEY, MARKET_API_KEY
from cache_manager import CacheManager
from monitoring import metrics_collector
import logging
import time
import requests
from bs4 import BeautifulSoup
from parsers import DocumentParser
from analysis.analyzers.legal_analyzer import LegalAnalyzer
from analysis.integrations.market_data import MarketData
from analysis.analyzers.market_analyzer import MarketAnalyzer
from analysis.integrations.geographic_data import GeographicData
from analysis.integrations.osm_api import OSMAPI
from analysis.integrations.legal_data import LegalData
from analysis.templates.template_manager import LeilaoTemplateManager
from analysis.templates import LeilaoTemplateManager
from analysis.integrations import GeographicData, LegalData, MarketData
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from analysis.integrations.ibge_data import IBGEDataCollector

# Carrega as variáveis de ambiente
load_dotenv()

# Obtém as chaves de API das variáveis de ambiente
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LEGAL_API_KEY = os.getenv('LEGAL_API_KEY')

logger = logging.getLogger(__name__)

# Inicializa o cliente OpenAI e o gerenciador de cache
client = OpenAI(api_key=OPENAI_API_KEY)
cache_manager = CacheManager()

class Validator:
    """Classe para validação de dados"""
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Valida se a URL é válida"""
        if not url:
            return False
            
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
            
    @staticmethod
    def validate_documents(documents: List[Dict[str, str]]) -> bool:
        """Valida se os documentos são válidos"""
        if not documents:
            return False
            
        required_fields = ['tipo', 'conteudo']
        return all(
            all(field in doc for field in required_fields)
            for doc in documents
        )
            
    @staticmethod
    def validate_property_data(data: Dict[str, Any]) -> bool:
        """Valida se os dados do imóvel são válidos"""
        if not data:
            return False
            
        required_fields = [
            'tipo_imovel',
            'area_total',
            'endereco',
            'valor_inicial',
            'valor_atual',
            'data_inicio'
        ]
        return all(field in data for field in required_fields)

class CacheManager:
    def __init__(self):
        self.cache = {}
        self.expiry_time = timedelta(hours=24)

    def get_cached_analysis(self, cache_key: str) -> Optional[Dict]:
        """Recupera análise do cache se existir e não estiver expirada"""
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if datetime.now() - entry["timestamp"] < self.expiry_time:
                metrics_collector.record_cache_operation(True, len(self.cache))
                return entry["data"]
        metrics_collector.record_cache_operation(False, len(self.cache))
        return None

    def save_analysis(self, cache_key: str, analysis_data: Dict):
        """Salva análise no cache com timestamp"""
        self.cache[cache_key] = {
            "data": analysis_data,
            "timestamp": datetime.now()
        }
        metrics_collector.record_cache_operation(True, len(self.cache))

    def clear_expired_cache(self):
        """Remove entradas expiradas do cache"""
        current_time = datetime.now()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry["timestamp"] > self.expiry_time
        ]
        for key in expired_keys:
            del self.cache[key]
        metrics_collector.record_cache_operation(True, len(self.cache))

class AnaliseImovel:
    """Classe principal para análise de imóveis em leilão"""
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.cache_manager = CacheManager()
        self.template_manager = LeilaoTemplateManager()
        self.legal_data = LegalData(api_key=LEGAL_API_KEY)
        self.legal_analyzer = LegalAnalyzer(self.legal_data)
        self.market_data = MarketData(api_key=MARKET_API_KEY)
        self.market_analyzer = MarketAnalyzer(market_data=self.market_data)
        self.validator = Validator()
        self.ibge_collector = IBGEDataCollector()
        
    def _validate_url(self, url: str) -> bool:
        """Valida se a URL fornecida é válida"""
        url_pattern = re.compile(
            r'^https?://'  # http:// ou https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domínio
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # porta opcional
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(url))
        
    def _validate_documents(self, documents: List[Dict[str, str]]) -> bool:
        """Valida se os documentos fornecidos são válidos"""
        if not documents or not isinstance(documents, list):
            return False
            
        required_fields = {"tipo", "conteudo"}
        for doc in documents:
            if not isinstance(doc, dict) or not all(field in doc for field in required_fields):
                return False
        return True
        
    def _validate_property_data(self, data: Dict[str, Any]) -> bool:
        """Valida se os dados do imóvel são válidos"""
        required_fields = {"tipo_imovel", "area_total", "endereco", "valor_inicial"}
        return isinstance(data, dict) and all(field in data for field in required_fields)
        
    async def analyze_from_url(self, url: str) -> Dict[str, Any]:
        """Analisa um imóvel a partir da URL do leilão"""
        if not self._validate_url(url):
            raise ValueError("URL inválida")
            
        try:
            # Extrai dados do imóvel da URL
            dados_imovel = await self.template_manager.extract_data(url)
            
            # Realiza análises
            analise_legal = await self.legal_analyzer.analyze(dados_imovel)
            analise_mercado = await self.market_analyzer.analyze(dados_imovel)
            
            # Monta resultado
            return {
                "dados_imovel": dados_imovel,
                "analise_legal": analise_legal,
                "analise_mercado": analise_mercado,
                "url_origem": url,
                "data_analise": datetime.now().isoformat()
            }
        except Exception as e:
            raise Exception(f"Erro ao analisar URL: {str(e)}")
            
    async def analyze_from_documents(self, documents: List[Dict[str, str]], property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa um imóvel a partir dos documentos fornecidos"""
        if not self._validate_documents(documents):
            raise ValueError("Documentos inválidos")
            
        if not self._validate_property_data(property_data):
            raise ValueError("Dados do imóvel inválidos")
            
        try:
            # Realiza análises
            analise_legal = await self.legal_analyzer.analyze_documents(documents)
            analise_mercado = await self.market_analyzer.analyze_property(property_data)
            
            # Monta resultado
            return {
                "dados_imovel": property_data,
                "analise_legal": analise_legal,
                "analise_mercado": analise_mercado,
                "documentos": documents,
                "data_analise": datetime.now().isoformat()
            }
        except Exception as e:
            raise Exception(f"Erro ao analisar documentos: {str(e)}")

    def _extrair_dados_url(self, url: str) -> Dict[str, Any]:
        """Extrai dados do imóvel a partir da URL"""
        try:
            # Obtém o template apropriado
            template = self.template_manager.get_template(url)
            if not template:
                self.logger.error(f"Nenhum template encontrado para a URL: {url}")
                return {}
                
            # Extrai os dados
            dados = template.extrair_dados(url)
            if not dados:
                self.logger.error(f"Falha ao extrair dados da URL: {url}")
                return {}
                
            return dados
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair dados da URL: {str(e)}")
            return {}
            
    def _analisar_dados_geograficos(self, endereco: str) -> Dict[str, Any]:
        """Analisa os dados geográficos do imóvel"""
        try:
            logger.info(f"Analisando dados geográficos para o endereço: {endereco}")
            
            # Obtém dados do IBGE
            dados_ibge = self._obter_dados_ibge(endereco)
            
            # Obtém dados meteorológicos
            dados_meteorologicos = self.geographic_data.obter_dados_clima(0, 0)  # Coordenadas temporárias
            
            # Obtém dados ambientais
            dados_ambientais = self.geographic_data.obter_dados_ambientais(0, 0)  # Coordenadas temporárias
            
            return {
                'dados_ibge': dados_ibge,
                'dados_meteorologicos': dados_meteorologicos,
                'dados_ambientais': dados_ambientais
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar dados geográficos: {str(e)}")
            return {'erro': str(e)}
            
    def _obter_dados_ibge(self, endereco: str) -> Dict[str, Any]:
        """Obtém dados do IBGE para o endereço"""
        try:
            if not endereco:
                self.logger.warning("Endereço vazio, retornando dados padrão")
                return {
                    'codigo_municipio': None,
                    'nome_municipio': None,
                    'uf': None,
                    'regiao': None,
                    'populacao': None,
                    'pib_per_capita': None,
                    'idh': None
                }
                
            # Tenta obter dados do IBGE
            response = requests.get(f"https://servicodados.ibge.gov.br/api/v1/localidades/enderecos/{endereco}")
            
            if response.status_code == 404:
                self.logger.warning("Endereço não encontrado no IBGE, retornando dados padrão")
                return {
                    'codigo_municipio': None,
                    'nome_municipio': None,
                    'uf': None,
                    'regiao': None,
                    'populacao': None,
                    'pib_per_capita': None,
                    'idh': None
                }
                
            if response.status_code != 200:
                raise Exception(f"Erro ao obter dados do IBGE: {response.status_code} {response.text}")
                
            data = response.json()
            
            return {
                'codigo_municipio': data.get('municipio', {}).get('id'),
                'nome_municipio': data.get('municipio', {}).get('nome'),
                'uf': data.get('municipio', {}).get('microrregiao', {}).get('mesorregiao', {}).get('UF', {}).get('sigla'),
                'regiao': data.get('municipio', {}).get('microrregiao', {}).get('mesorregiao', {}).get('UF', {}).get('regiao', {}).get('nome'),
                'populacao': None,  # Será preenchido posteriormente
                'pib_per_capita': None,  # Será preenchido posteriormente
                'idh': None  # Será preenchido posteriormente
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do IBGE: {str(e)}")
            return {
                'codigo_municipio': None,
                'nome_municipio': None,
                'uf': None,
                'regiao': None,
                'populacao': None,
                'pib_per_capita': None,
                'idh': None
            }
            
    def _analisar_acessibilidade(self, coordenadas: Dict[str, float]) -> Dict[str, Any]:
        """Analisa acessibilidade do imóvel"""
        try:
            # TODO: Implementar análise de acessibilidade usando APIs de transporte
            return {
                'proximidade_transporte_publico': 'não analisado',
                'acesso_rodovias': 'não analisado',
                'tempo_centro': 'não analisado'
            }
        except Exception as e:
            self.logger.error(f"Erro na análise de acessibilidade: {str(e)}")
            return {}
            
    def _analisar_riscos_ambientais(self, env_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa riscos ambientais do imóvel"""
        try:
            # TODO: Implementar análise de riscos ambientais
            return {
                'risco_inundacao': 'não analisado',
                'risco_deslizamento': 'não analisado',
                'poluicao_ar': 'não analisado',
                'poluicao_sonora': 'não analisado'
            }
        except Exception as e:
            self.logger.error(f"Erro na análise de riscos ambientais: {str(e)}")
            return {}
            
    def _analisar_dados_juridicos(self, numero_processo: str, matricula: str, edital: str, matricula_texto: str) -> Dict[str, Any]:
        """Analisa dados jurídicos do imóvel"""
        try:
            # TODO: Implementar análise jurídica detalhada
            return {
                'riscos': 'não analisado',
                'onus': 'não analisado',
                'status': 'não analisado'
            }
        except Exception as e:
            self.logger.error(f"Erro na análise jurídica: {str(e)}")
            return {}
            
    def _analisar_dados_mercado(self, endereco: str, area: str, valor_inicial: str) -> Dict[str, Any]:
        """Analisa dados de mercado do imóvel"""
        try:
            # TODO: Implementar análise de mercado detalhada
            return {
                'valor_mercado': 'não analisado',
                'indicadores': 'não analisado',
                'potencial': 'não analisado'
            }
        except Exception as e:
            self.logger.error(f"Erro na análise de mercado: {str(e)}")
            return {}
            
    def _gerar_recomendacoes(self, dados_imovel: Dict[str, Any], dados_juridicos: Dict[str, Any], 
                            dados_mercado: Dict[str, Any], dados_geograficos: Dict[str, Any]) -> Dict[str, Any]:
        """Gera recomendações baseadas nos dados analisados"""
        try:
            recomendacoes = {
                'gerais': [],
                'juridicas': [],
                'mercado': [],
                'geograficas': []
            }
            
            # Recomendações gerais
            if isinstance(dados_imovel, dict):
                if dados_imovel.get('valor_inicial') and dados_imovel.get('valor_atual'):
                    valor_inicial = float(dados_imovel.get('valor_inicial', 0))
                    valor_atual = float(dados_imovel.get('valor_atual', 0))
                    if valor_atual > valor_inicial:
                        recomendacoes['gerais'].append({
                            'titulo': 'Valorização do Imóvel',
                            'descricao': 'O imóvel está com valorização positiva em relação ao valor inicial.',
                            'prioridade': 'alta'
                        })
            
            # Recomendações jurídicas
            if isinstance(dados_juridicos, dict):
                if dados_juridicos.get('riscos_juridicos'):
                    recomendacoes['juridicas'].append({
                        'titulo': 'Riscos Jurídicos',
                        'descricao': 'Identificados riscos jurídicos que precisam ser analisados.',
                        'prioridade': 'alta'
                    })
            
            # Recomendações de mercado
            if isinstance(dados_mercado, dict):
                if dados_mercado.get('indicadores_mercado'):
                    recomendacoes['mercado'].append({
                        'titulo': 'Análise de Mercado',
                        'descricao': 'Considere os indicadores de mercado na sua decisão.',
                        'prioridade': 'media'
                    })
            
            # Recomendações geográficas
            if isinstance(dados_geograficos, dict):
                if dados_geograficos.get('dados_ibge'):
                    recomendacoes['geograficas'].append({
                        'titulo': 'Dados Regionais',
                        'descricao': 'Analise os dados regionais para melhor compreensão do contexto.',
                        'prioridade': 'media'
                    })
            
            # Resumo das recomendações
            total_recomendacoes = sum(len(v) for v in recomendacoes.values())
            recomendacoes_altas = sum(1 for v in recomendacoes.values() for r in v if r['prioridade'] == 'alta')
            
            return {
                'recomendacoes': recomendacoes,
                'resumo': {
                    'total_recomendacoes': total_recomendacoes,
                    'recomendacoes_altas': recomendacoes_altas,
                    'status': 'positivo' if recomendacoes_altas == 0 else 'atencao'
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar recomendações: {str(e)}")
            return {
                'recomendacoes': {
                    'gerais': [],
                    'juridicas': [],
                    'mercado': [],
                    'geograficas': []
                },
                'resumo': {
                    'total_recomendacoes': 0,
                    'recomendacoes_altas': 0,
                    'status': 'neutro'
                }
            }

    def _analisar_documentos(self) -> Dict[str, Any]:
        """Realiza a análise tradicional com documentos"""
        try:
            # Verifica se já existe análise em cache
            cached_analysis = self.cache_manager.get_cached_analysis(
                self.edital or "",
                self.matricula or ""
            )
            
            if cached_analysis:
                logger.info("Utilizando análise do cache")
                return cached_analysis

            # Prepara o prompt para o GPT-4
            prompt = f"""
            Analise os seguintes documentos de um imóvel em leilão e extraia as seguintes informações:
            
            Documentos fornecidos:
            Edital: {self.edital or 'Não fornecido'}
            Matrícula: {self.matricula or 'Não fornecido'}
            
            Por favor, identifique e retorne APENAS as seguintes informações em formato JSON:
            1. Se há penhoras ou gravames (sim/não)
            2. Se há dívidas de condomínio (sim/não)
            3. Se o imóvel está ocupado (sim/não)
            4. Observações relevantes sobre condições e riscos jurídicos
            
            Retorne APENAS o JSON, sem texto adicional.
            """

            logger.info("Iniciando análise com OpenAI")
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Você é um especialista em análise de documentos imobiliários."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )

            # Extrai e retorna a análise
            analysis = response.choices[0].message.content
            result = eval(analysis)  # Converte a string JSON em dicionário
            
            # Salva a análise no cache
            self.cache_manager.save_analysis(
                self.edital or "",
                self.matricula or "",
                result
            )
            
            return result

        except Exception as e:
            logger.error(f"Erro na análise do imóvel: {str(e)}")
            return {
                "penhora": "erro",
                "dividas_condominio": "erro",
                "ocupado": "erro",
                "observacoes": f"Erro na análise: {str(e)}"
            }

    def _processar_edital_pdf(self, pdf_url: str) -> str:
        """Processa o conteúdo do edital em PDF"""
        try:
            self.logger.info(f"Processando documento PDF: {pdf_url}")
            
            # Configuração do header para simular um navegador
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Baixa o PDF
            response = requests.get(pdf_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Salva o PDF temporariamente
            temp_pdf = f"temp_{hash(pdf_url)}.pdf"
            with open(temp_pdf, 'wb') as f:
                f.write(response.content)
            
            # Converte PDF para texto
            import PyPDF2
            pdf_reader = PyPDF2.PdfReader(temp_pdf)
            texto = ""
            
            # Processa cada página
            for page in pdf_reader.pages:
                texto_pagina = page.extract_text()
                if texto_pagina:
                    # Limpa o texto
                    texto_pagina = texto_pagina.replace('\n', ' ')
                    texto_pagina = re.sub(r'\s+', ' ', texto_pagina)
                    texto += texto_pagina + '\n'
            
            # Remove o arquivo temporário
            os.remove(temp_pdf)
            
            self.logger.info("Documento PDF processado com sucesso")
            return texto.strip()
            
        except Exception as e:
            self.logger.error(f"Erro ao processar edital PDF: {str(e)}")
            return ""

    def calcular_margem_financeira(self) -> Optional[float]:
        """Calcula a margem financeira percentual."""
        if self.valor_mercado and self.valor_minimo and self.valor_mercado > 0:
            return ((self.valor_mercado - self.valor_minimo) / self.valor_mercado) * 100
        return None
        
    def formatar_descricao(self) -> str:
        """Formata a descrição para o relatório."""
        if len(self.descricao) > 200:
            return self.descricao[:200] + "..."
        return self.descricao
        
    def gerar_analise(self) -> Dict[str, Any]:
        """Gera a análise completa do imóvel."""
        margem = self.calcular_margem_financeira()
        
        return {
            "id": self.imovel_id,
            "url": self.url,
            "data_analise": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "margem_financeira": f"{margem:.2f}%" if margem else "Não calculável",
            "resumo": {
                "descricao": self.formatar_descricao(),
                "observacoes": "Análise inicial realizada. Recomenda-se verificação detalhada dos documentos."
            }
        } 

    def _check_cache(self, key: str) -> Dict[str, Any] | None:
        """Verifica se existe um resultado em cache para a chave fornecida."""
        if key in self.cache:
            cached_data = self.cache[key]
            if datetime.now() - cached_data['timestamp'] < self.cache_ttl:
                metrics_collector.record_cache_hit()
                return cached_data['result']
            else:
                del self.cache[key]
        
        metrics_collector.record_cache_miss()
        return None
    
    def _update_cache(self, key: str, result: Dict[str, Any]) -> None:
        """Atualiza o cache com um novo resultado."""
        self.cache[key] = {
            'timestamp': datetime.now(),
            'result': result
        }
    
    def analyze_property(self, edital_texto: str, matricula_texto: str) -> Dict[str, Any]:
        """
        Analisa um imóvel com base no texto do edital e da matrícula.
        
        Args:
            edital_texto: Texto do edital do imóvel
            matricula_texto: Texto da matrícula do imóvel
            
        Returns:
            Dict contendo as análises realizadas
        """
        start_time = time.time()
        cache_key = f"{hash(edital_texto)}_{hash(matricula_texto)}"
        
        try:
            # Verifica cache
            cached_result = self._check_cache(cache_key)
            if cached_result:
                return cached_result
            
            # Realiza as análises
            result = {
                'edital': self._analyze_edital(edital_texto),
                'matricula': self._analyze_matricula(matricula_texto),
                'timestamp': datetime.now().isoformat()
            }
            
            # Atualiza cache
            self._update_cache(cache_key, result)
            
            # Registra métricas
            duration = time.time() - start_time
            metrics_collector.record_api_call('analyze_property', duration)
            
            return result
            
        except Exception as e:
            metrics_collector.record_error(e, {
                'edital_length': len(edital_texto),
                'matricula_length': len(matricula_texto)
            })
            logger.error(f"Erro ao analisar imóvel: {str(e)}")
            raise
    
    def _analyze_edital(self, edital_texto: str) -> Dict[str, Any]:
        """Analisa o texto do edital."""
        # TODO: Implementar análise do edital
        return {}
    
    def _analyze_matricula(self, matricula_texto: str) -> Dict[str, Any]:
        """Analisa o texto da matrícula."""
        # TODO: Implementar análise da matrícula
        return {}

    def calculate_financial_margin(self, valor_avaliacao: float, valor_minimo: float) -> float:
        """Calcula a margem financeira entre o valor de avaliação e o valor mínimo."""
        try:
            if valor_avaliacao <= 0 or valor_minimo <= 0:
                raise ValueError("Valores devem ser positivos")
            
            return ((valor_avaliacao - valor_minimo) / valor_minimo) * 100
        except Exception as e:
            logger.error(f"Erro no cálculo da margem financeira: {str(e)}")
            raise

    def extrair_dados_preliminares(self, url: str) -> Dict[str, Any]:
        """Extrai dados preliminares do imóvel para análise inicial"""
        try:
            self.logger.info(f"Extraindo dados preliminares da URL: {url}")
            
            # Usa o template adequado para extrair os dados
            template = self.template_manager.get_template(url)
            if not template:
                return {'erro': 'URL não suportada'}
                
            # Extrai os dados usando o template
            dados = template.extrair_dados(url)
            if 'erro' in dados:
                return dados
                
            # Formata os dados para retorno
            return {
                'titulo': dados.get('titulo'),
                'tipo_imovel': dados.get('tipo_imovel'),
                'endereco': dados.get('endereco'),
                'valor_inicial': dados.get('valor_inicial'),
                'valor_avaliacao': dados.get('valor_avaliacao'),
                'data_leilao': dados.get('data_leilao'),
                'tipo_leilao': dados.get('tipo_leilao'),
                'numero_processo': dados.get('numero_processo'),
                'documentos': dados.get('documentos', []),
                'data_analise': datetime.now().isoformat(),
                'status': 'preliminar'
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair dados preliminares: {str(e)}", exc_info=True)
            return {'erro': str(e)}

    def iniciar_analise_completa(self, url: str) -> Dict[str, Any]:
        """Inicia a análise completa do imóvel"""
        try:
            logger.info(f"Iniciando análise completa para URL: {url}")
            
            # Extrai dados preliminares
            dados_preliminares = self.extrair_dados_preliminares(url)
            if 'erro' in dados_preliminares:
                return dados_preliminares
                
            # Analisa dados geográficos
            dados_geograficos = self._analisar_dados_geograficos(dados_preliminares.get('endereco', ''))
            
            # Analisa aspectos legais
            analise_legal = self.legal_analyzer.analyze({
                'processo': dados_preliminares.get('processo'),
                'matricula': dados_preliminares.get('matricula')
            })
            
            # Analisa aspectos de mercado
            analise_mercado = self.market_analyzer.analyze({
                'endereco': dados_preliminares.get('endereco'),
                'area': dados_preliminares.get('area'),
                'valor_avaliacao': dados_preliminares.get('valor_avaliacao')
            })
            
            # Compila os resultados
            resultado = {
                'dados_preliminares': dados_preliminares,
                'dados_geograficos': dados_geograficos,
                'analise_legal': analise_legal,
                'analise_mercado': analise_mercado,
                'data_analise': datetime.now().isoformat(),
                'status': 'completa'
            }
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao realizar análise completa: {str(e)}")
            return {'erro': str(e)}

    def editar_analise(self, analise_id: str, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Edita uma análise existente"""
        try:
            logger.info(f"Editando análise {analise_id}")
            
            # Valida os dados fornecidos
            if not dados:
                return {'erro': 'Nenhum dado fornecido para edição'}
                
            # Atualiza a análise com os novos dados
            resultado = self.iniciar_analise_completa(dados.get('url', ''))
            if 'erro' in resultado:
                return resultado
                
            # Adiciona informações de edição
            resultado.update({
                'data_edicao': datetime.now().isoformat(),
                'status': 'editado'
            })
            
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao editar análise: {str(e)}")
            return {'erro': str(e)}

    def _obter_dados_geograficos(self, endereco: str) -> Dict[str, Any]:
        """Obtém dados geográficos para o endereço"""
        try:
            if not endereco:
                self.logger.warning("Endereço vazio, retornando dados padrão")
                return {
                    'latitude': None,
                    'longitude': None,
                    'endereco_formatado': None,
                    'dados_ibge': {
                        'codigo_municipio': None,
                        'nome_municipio': None,
                        'uf': None,
                        'regiao': None,
                        'populacao': None,
                        'pib_per_capita': None,
                        'idh': None
                    },
                    'dados_meteorologicos': {
                        'temperatura_atual': None,
                        'condicao_climatica': None,
                        'umidade': None,
                        'velocidade_vento': None
                    }
                }
                
            # Obtém coordenadas
            coordenadas = self._obter_coordenadas(endereco)
            if not coordenadas:
                raise Exception("Não foi possível obter coordenadas para o endereço")
                
            # Obtém dados do IBGE
            dados_ibge = self._obter_dados_ibge(endereco)
            
            # Obtém dados meteorológicos
            dados_meteorologicos = self._obter_dados_meteorologicos(coordenadas)
            
            return {
                'latitude': coordenadas.get('latitude'),
                'longitude': coordenadas.get('longitude'),
                'endereco_formatado': coordenadas.get('endereco_formatado'),
                'dados_ibge': dados_ibge,
                'dados_meteorologicos': dados_meteorologicos
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados geográficos: {str(e)}")
            return {
                'latitude': None,
                'longitude': None,
                'endereco_formatado': None,
                'dados_ibge': {
                    'codigo_municipio': None,
                    'nome_municipio': None,
                    'uf': None,
                    'regiao': None,
                    'populacao': None,
                    'pib_per_capita': None,
                    'idh': None
                },
                'dados_meteorologicos': {
                    'temperatura_atual': None,
                    'condicao_climatica': None,
                    'umidade': None,
                    'velocidade_vento': None
                }
            }

    async def analisar_imovel(self, url: str) -> Dict[str, Any]:
        """
        Analisa um imóvel a partir de sua URL
        """
        try:
            # Validação inicial
            if not self.validator.validar_url(url):
                raise ValueError("URL inválida")

            # Verifica cache
            cache_key = f"analise_{url}"
            cached_data = self.cache_manager.get(cache_key)
            if cached_data:
                return cached_data

            # Extrai dados do imóvel
            dados_imovel = await self._extrair_dados_imovel(url)
            
            # Obtém dados do IBGE
            codigo_municipio = self.ibge_collector.get_codigo_municipio(
                dados_imovel.get("cidade", ""),
                dados_imovel.get("estado", "")
            )
            
            if codigo_municipio:
                dados_ibge = self.ibge_collector.get_municipio_data(codigo_municipio)
                dados_imovel["dados_ibge"] = dados_ibge

            # Salva no cache
            self.cache_manager.set(cache_key, dados_imovel)
            
            return dados_imovel

        except Exception as e:
            logger.error(f"Erro ao analisar imóvel: {str(e)}")
            raise

async def analyze_property(edital_texto: Optional[str] = None, matricula_texto: Optional[str] = None) -> Dict:
    """Analisa o edital e a matrícula do imóvel usando GPT"""
    try:
        # Verifica se há análise em cache
        cache_key = f"{edital_texto[:100]}_{matricula_texto[:100]}"
        cached_result = cache_manager.get_cached_analysis(cache_key)
        if cached_result:
            logger.info("Análise encontrada em cache")
            return cached_result

        logger.info("Iniciando análise do imóvel")
        
        # Prepara o prompt para o GPT
        system_prompt = """Você é um especialista em análise de imóveis em leilão.
        Analise o edital e a matrícula fornecidos e extraia as informações relevantes."""
        
        user_prompt = f"""
        Edital: {edital_texto if edital_texto else 'Não fornecido'}
        
        Matrícula: {matricula_texto if matricula_texto else 'Não fornecida'}
        
        Por favor, analise os documentos e forneça:
        1. Dados básicos do imóvel (tipo, área, localização)
        2. Valor de avaliação e lance mínimo
        3. Riscos jurídicos identificados
        4. Ônus e gravames
        5. Restrições de uso
        6. Recomendações gerais
        """

        # Faz a chamada para a API do GPT
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )

        # Processa a resposta
        analysis_text = response.choices[0].message.content
        
        # Estrutura o resultado
        result = {
            "success": True,
            "analysis": analysis_text,
            "timestamp": datetime.now().isoformat(),
            "model_used": OPENAI_MODEL
        }

        # Salva no cache
        cache_manager.save_analysis(cache_key, result)
        logger.info("Análise concluída e salva em cache")
        
        return result

    except Exception as e:
        logger.error(f"Erro ao analisar propriedade: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def calculate_financial_margin(valor_mercado: float, valor_minimo_leilao: float) -> float:
    """
    Calcula a margem financeira percentual entre o valor de mercado e o valor mínimo do leilão.
    """
    try:
        if valor_mercado <= 0 or valor_minimo_leilao <= 0:
            logger.error("Valores inválidos para cálculo de margem financeira")
            raise ValueError("Valores devem ser positivos")
        
        margem = ((valor_mercado - valor_minimo_leilao) / valor_mercado) * 100
        logger.info(f"Margem financeira calculada: {margem:.2f}%")
        return round(margem, 2)
    except Exception as e:
        logger.error(f"Erro no cálculo da margem financeira: {str(e)}")
        raise 