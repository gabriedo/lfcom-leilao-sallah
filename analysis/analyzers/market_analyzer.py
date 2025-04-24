from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import requests
from statistics import mean, median
from ..integrations.market_data import MarketData

logger = logging.getLogger(__name__)

class MarketAnalyzer:
    """Classe para análise de mercado de imóveis em leilão"""
    
    def __init__(self, market_data: MarketData):
        """Inicializa o analisador de mercado"""
        self.market_data = market_data
        self.logger = logging.getLogger(__name__)
        
    def analisar_mercado(self, endereco: str, area: float, valor_inicial: float) -> Dict[str, Any]:
        """Analisa o mercado para o imóvel"""
        try:
            # Obtém dados de mercado
            dados_mercado = self.market_data.obter_dados_mercado(endereco)
            if not dados_mercado:
                return {'erro': 'Não foi possível obter dados de mercado'}
                
            # Obtém dados comparativos
            dados_comparativos = self.market_data.obter_dados_comparativos(endereco, area)
            if not dados_comparativos:
                return {'erro': 'Não foi possível obter dados comparativos'}
                
            # Obtém dados de evolução
            dados_evolucao = self.market_data.obter_dados_evolucao(endereco)
            if not dados_evolucao:
                return {'erro': 'Não foi possível obter dados de evolução'}
                
            # Analisa o mercado
            analise = {
                'mercado': self._analisar_dados_mercado(dados_mercado),
                'comparativos': self._analisar_comparativos(dados_comparativos, valor_inicial),
                'evolucao': self._analisar_evolucao(dados_evolucao),
                'recomendacoes': self._gerar_recomendacoes(dados_mercado, dados_comparativos, dados_evolucao)
            }
            
            return analise
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar mercado: {str(e)}")
            return {'erro': str(e)}
            
    def _analisar_dados_mercado(self, dados_mercado: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa os dados de mercado"""
        analise = {
            'status': 'neutro',
            'descricao': [],
            'indicadores': {}
        }
        
        # Verifica a demanda
        if dados_mercado.get('demanda') == 'alta':
            analise['status'] = 'favoravel'
            analise['descricao'].append('Alta demanda na região')
        elif dados_mercado.get('demanda') == 'baixa':
            analise['status'] = 'desfavoravel'
            analise['descricao'].append('Baixa demanda na região')
            
        # Verifica a oferta
        if dados_mercado.get('oferta') == 'alta':
            analise['status'] = 'desfavoravel'
            analise['descricao'].append('Alta oferta na região')
        elif dados_mercado.get('oferta') == 'baixa':
            analise['status'] = 'favoravel'
            analise['descricao'].append('Baixa oferta na região')
            
        # Calcula indicadores
        if dados_mercado.get('preco_medio'):
            analise['indicadores']['preco_medio'] = dados_mercado['preco_medio']
            
        if dados_mercado.get('tempo_medio_venda'):
            analise['indicadores']['tempo_medio_venda'] = dados_mercado['tempo_medio_venda']
            
        return analise
        
    def _analisar_comparativos(self, dados_comparativos: Dict[str, Any], valor_inicial: float) -> Dict[str, Any]:
        """Analisa os dados comparativos"""
        analise = {
            'status': 'neutro',
            'descricao': [],
            'indicadores': {}
        }
        
        # Verifica o preço por m²
        if dados_comparativos.get('preco_medio_m2'):
            preco_medio_m2 = dados_comparativos['preco_medio_m2']
            preco_m2_imovel = valor_inicial / dados_comparativos.get('area_media', 1)
            
            if preco_m2_imovel < preco_medio_m2 * 0.8:
                analise['status'] = 'favoravel'
                analise['descricao'].append('Preço por m² abaixo da média')
            elif preco_m2_imovel > preco_medio_m2 * 1.2:
                analise['status'] = 'desfavoravel'
                analise['descricao'].append('Preço por m² acima da média')
                
            analise['indicadores']['preco_medio_m2'] = preco_medio_m2
            analise['indicadores']['preco_m2_imovel'] = preco_m2_imovel
            
        # Verifica características
        if dados_comparativos.get('caracteristicas'):
            caracteristicas = dados_comparativos['caracteristicas']
            analise['indicadores']['caracteristicas'] = caracteristicas
            
        return analise
        
    def _analisar_evolucao(self, dados_evolucao: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa a evolução dos preços"""
        analise = {
            'status': 'neutro',
            'descricao': [],
            'indicadores': {}
        }
        
        # Verifica a tendência
        if dados_evolucao.get('tendencia'):
            tendencia = dados_evolucao['tendencia']
            if tendencia == 'alta':
                analise['status'] = 'favoravel'
                analise['descricao'].append('Tendência de alta nos preços')
            elif tendencia == 'baixa':
                analise['status'] = 'desfavoravel'
                analise['descricao'].append('Tendência de baixa nos preços')
                
            analise['indicadores']['tendencia'] = tendencia
            
        # Verifica a variação
        if dados_evolucao.get('variacao'):
            variacao = dados_evolucao['variacao']
            analise['indicadores']['variacao'] = variacao
            
        return analise
        
    def _gerar_recomendacoes(self, dados_mercado: Dict[str, Any], dados_comparativos: Dict[str, Any], dados_evolucao: Dict[str, Any]) -> Dict[str, Any]:
        """Gera recomendações baseadas na análise dos dados"""
        recomendacoes = {
            'gerais': [],
            'especificas': []
        }
        
        # Recomendações gerais
        recomendacoes['gerais'].append('Consultar um corretor de imóveis')
        recomendacoes['gerais'].append('Verificar a documentação do imóvel')
        
        # Recomendações específicas
        if dados_mercado.get('demanda') == 'alta':
            recomendacoes['especificas'].append('Considerar oferta acima do valor inicial')
            
        if dados_comparativos.get('preco_medio_m2'):
            preco_medio_m2 = dados_comparativos['preco_medio_m2']
            preco_m2_imovel = dados_comparativos.get('valor_inicial', 0) / dados_comparativos.get('area_media', 1)
            
            if preco_m2_imovel < preco_medio_m2 * 0.8:
                recomendacoes['especificas'].append('Oportunidade de investimento')
            elif preco_m2_imovel > preco_medio_m2 * 1.2:
                recomendacoes['especificas'].append('Avaliar negociação do preço')
                
        if dados_evolucao.get('tendencia') == 'alta':
            recomendacoes['especificas'].append('Considerar valorização futura')
            
        return recomendacoes

    def analyze(self, imovel_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa os aspectos de mercado do imóvel.
        
        Args:
            imovel_info: Informações básicas do imóvel
            
        Returns:
            Dict contendo a análise de mercado
        """
        try:
            # Extrai valores básicos com tratamento para nulos
            area = imovel_info.get('area', 0)
            valor_inicial = imovel_info.get('valor_inicial', 0)
            valor_primeira_praca = imovel_info.get('valor_primeira_praca', 0)
            valor_segunda_praca = imovel_info.get('valor_segunda_praca', 0)
            valor_avaliacao = imovel_info.get('valor_avaliacao', 0)
            
            # Se não tiver área ou valores, retorna análise limitada
            if not area or not (valor_inicial or valor_primeira_praca or valor_segunda_praca or valor_avaliacao):
                return {
                    'status': 'parcial',
                    'mensagem': 'Análise limitada por falta de dados básicos',
                    'indicadores': {
                        'valor_m2': None,
                        'potencial_valorizacao': None,
                        'desconto_primeira_praca': None,
                        'desconto_segunda_praca': None
                    },
                    'recomendacoes': [
                        {
                            'prioridade': 'alta',
                            'descricao': 'Buscar mais informações sobre área e valores do imóvel'
                        }
                    ]
                }
            
            # Calcula indicadores
            valor_m2 = None
            desconto_primeira_praca = None
            desconto_segunda_praca = None
            
            # Usa o maior valor para calcular o valor por m²
            if area > 0:
                if valor_avaliacao:
                    valor_m2 = valor_avaliacao / area
                elif valor_primeira_praca:
                    valor_m2 = valor_primeira_praca / area
                elif valor_segunda_praca:
                    valor_m2 = valor_segunda_praca / area
                    
            # Calcula descontos se tiver os valores
            if valor_avaliacao and valor_avaliacao > 0:
                if valor_primeira_praca:
                    desconto_primeira_praca = ((valor_avaliacao - valor_primeira_praca) / valor_avaliacao) * 100
                if valor_segunda_praca:
                    desconto_segunda_praca = ((valor_avaliacao - valor_segunda_praca) / valor_avaliacao) * 100
            
            # Analisa potencial com base na área
            potencial = None
            if area:
                if area < 50:
                    potencial = 'baixo'
                elif area < 100:
                    potencial = 'médio'
                else:
                    potencial = 'alto'
            
            # Gera recomendações
            recomendacoes = []
            
            # Analisa valor por m²
            if valor_m2:
                if valor_m2 > 5000:
                    recomendacoes.append({
                        'prioridade': 'média',
                        'descricao': 'Valor por m² acima da média. Verificar justificativa.'
                    })
                elif valor_m2 < 2000:
                    recomendacoes.append({
                        'prioridade': 'alta',
                        'descricao': 'Valor por m² muito baixo. Verificar possíveis problemas.'
                    })
            
            # Analisa descontos
            if desconto_segunda_praca:
                if desconto_segunda_praca > 40:
                    recomendacoes.append({
                        'prioridade': 'alta',
                        'descricao': f'Desconto significativo na 2ª praça de {desconto_segunda_praca:.1f}%. Verificar motivos.'
                    })
                elif desconto_segunda_praca < 10:
                    recomendacoes.append({
                        'prioridade': 'média',
                        'descricao': 'Desconto baixo na 2ª praça. Considerar aguardar outras oportunidades.'
                    })
            
            return {
                'status': 'sucesso',
                'indicadores': {
                    'valor_m2': round(valor_m2, 2) if valor_m2 else None,
                    'potencial_valorizacao': potencial,
                    'desconto_primeira_praca': round(desconto_primeira_praca, 2) if desconto_primeira_praca else None,
                    'desconto_segunda_praca': round(desconto_segunda_praca, 2) if desconto_segunda_praca else None
                },
                'recomendacoes': recomendacoes
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de mercado: {str(e)}")
            return {
                'status': 'erro',
                'mensagem': str(e)
            }
            
    def _generate_recommendations(self, area: Optional[float], valor_m2: Optional[float]) -> List[Dict[str, str]]:
        """Gera recomendações baseadas nos dados de mercado"""
        recomendacoes = []
        
        if not area or not valor_m2:
            recomendacoes.append({
                'prioridade': 'alta',
                'descricao': 'Realizar vistoria presencial para avaliar condições do imóvel'
            })
        else:
            if valor_m2 > 5000:
                recomendacoes.append({
                    'prioridade': 'média',
                    'descricao': 'Valor por m² acima da média. Verificar justificativa.'
                })
            elif valor_m2 < 2000:
                recomendacoes.append({
                    'prioridade': 'alta',
                    'descricao': 'Valor por m² muito baixo. Verificar possíveis problemas.'
                })
        
        return recomendacoes 