from typing import Dict, Any, List, Optional
import logging
import re
from ..integrations.legal_data import LegalData

logger = logging.getLogger(__name__)

class LegalAnalyzer:
    """Classe para análise jurídica de imóveis em leilão"""
    
    def __init__(self, legal_data: LegalData):
        """Inicializa o analisador jurídico"""
        self.legal_data = legal_data
        self.logger = logging.getLogger(__name__)
        
    def analisar_riscos(self, numero_processo: str, numero_matricula: str) -> Dict[str, Any]:
        """Analisa os riscos jurídicos do imóvel"""
        try:
            # Obtém dados do processo
            dados_processo = self.legal_data.obter_dados_processo(numero_processo)
            if not dados_processo:
                return {'erro': 'Não foi possível obter dados do processo'}
                
            # Obtém dados da matrícula
            dados_matricula = self.legal_data.obter_dados_matricula(numero_matricula)
            if not dados_matricula:
                return {'erro': 'Não foi possível obter dados da matrícula'}
                
            # Analisa os riscos
            riscos = {
                'processo': self._analisar_riscos_processo(dados_processo),
                'matricula': self._analisar_riscos_matricula(dados_matricula),
                'recomendacoes': self._gerar_recomendacoes(dados_processo, dados_matricula)
            }
            
            return riscos
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar riscos jurídicos: {str(e)}")
            return {'erro': str(e)}
            
    def _analisar_riscos_processo(self, dados_processo: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa os riscos do processo judicial"""
        riscos = {
            'status': 'baixo',
            'descricao': [],
            'alertas': []
        }
        
        # Verifica se há embargos
        if dados_processo.get('embargos'):
            riscos['status'] = 'alto'
            riscos['descricao'].append('Existem embargos no processo')
            riscos['alertas'].append('Verificar a natureza dos embargos')
            
        # Verifica se há recursos pendentes
        if dados_processo.get('recursos_pendentes'):
            riscos['status'] = 'medio'
            riscos['descricao'].append('Existem recursos pendentes')
            riscos['alertas'].append('Avaliar o impacto dos recursos no prazo do leilão')
            
        # Verifica se há execução fiscal
        if dados_processo.get('execucao_fiscal'):
            riscos['status'] = 'alto'
            riscos['descricao'].append('Processo de execução fiscal')
            riscos['alertas'].append('Verificar débitos fiscais pendentes')
            
        return riscos
        
    def _analisar_riscos_matricula(self, dados_matricula: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa os riscos da matrícula imobiliária"""
        riscos = {
            'status': 'baixo',
            'descricao': [],
            'alertas': []
        }
        
        # Verifica se há ônus
        if dados_matricula.get('onus'):
            riscos['status'] = 'medio'
            riscos['descricao'].append('Existem ônus na matrícula')
            riscos['alertas'].append('Verificar a natureza dos ônus')
            
        # Verifica se há usucapião
        if dados_matricula.get('usucapiao'):
            riscos['status'] = 'alto'
            riscos['descricao'].append('Processo de usucapião')
            riscos['alertas'].append('Verificar o estágio do processo de usucapião')
            
        # Verifica se há regularização pendente
        if dados_matricula.get('regularizacao_pendente'):
            riscos['status'] = 'medio'
            riscos['descricao'].append('Regularização pendente')
            riscos['alertas'].append('Verificar os requisitos para regularização')
            
        return riscos
        
    def _gerar_recomendacoes(self, dados_processo: Dict[str, Any], dados_matricula: Dict[str, Any]) -> Dict[str, Any]:
        """Gera recomendações baseadas na análise dos dados"""
        recomendacoes = {
            'gerais': [],
            'especificas': []
        }
        
        # Recomendações gerais
        recomendacoes['gerais'].append('Consultar um advogado especializado')
        recomendacoes['gerais'].append('Verificar a documentação completa')
        
        # Recomendações específicas
        if dados_processo.get('embargos'):
            recomendacoes['especificas'].append('Avaliar o impacto dos embargos no leilão')
            
        if dados_matricula.get('onus'):
            recomendacoes['especificas'].append('Verificar a possibilidade de remoção dos ônus')
            
        if dados_matricula.get('regularizacao_pendente'):
            recomendacoes['especificas'].append('Avaliar o custo e prazo da regularização')
            
        return recomendacoes

    def analyze(self, edital_info: Dict[str, Any], matricula_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analisa os aspectos legais do imóvel.
        
        Args:
            edital_info: Informações do edital
            matricula_info: Informações da matrícula (opcional)
            
        Returns:
            Dict contendo a análise legal
        """
        try:
            riscos = []
            restricoes = []
            recomendacoes = []
            
            # Analisa informações do edital
            if edital_info:
                if 'restricoes' in edital_info:
                    restricoes.extend(edital_info['restricoes'])
                    
            # Analisa informações da matrícula se disponível
            if matricula_info:
                if matricula_info.get('hipoteca'):
                    riscos.append({
                        'tipo': 'hipoteca',
                        'nivel': 'alto',
                        'descricao': 'Imóvel possui hipoteca registrada'
                    })
                    
                if matricula_info.get('penhora'):
                    riscos.append({
                        'tipo': 'penhora',
                        'nivel': 'alto',
                        'descricao': 'Imóvel possui penhora registrada'
                    })
            
            # Gera recomendações baseadas nos riscos
            if riscos:
                recomendacoes.append({
                    'prioridade': 'alta',
                    'descricao': 'Consultar advogado para análise dos riscos identificados'
                })
            
            return {
                'status': 'sucesso',
                'riscos': riscos,
                'restricoes': restricoes,
                'recomendacoes': recomendacoes
            }
            
        except Exception as e:
            logger.error(f"Erro na análise legal: {str(e)}")
            return {
                'status': 'erro',
                'mensagem': str(e)
            }
            
    def _analyze_risks(self, edital_info: Dict[str, Any], matricula_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa os riscos legais"""
        riscos = []
        nivel = "baixo"
        
        if matricula_info.get('inconsistencias'):
            riscos.append({
                'tipo': 'inconsistencia',
                'descricao': 'Inconsistências encontradas na matrícula',
                'nivel': 'alto'
            })
            nivel = "alto"
            
        if edital_info.get('restricoes'):
            riscos.append({
                'tipo': 'restricao',
                'descricao': 'Restrições mencionadas no edital',
                'nivel': 'medio'
            })
            nivel = "medio" if nivel != "alto" else "alto"
            
        return {
            'nivel': nivel,
            'riscos': riscos
        }
        
    def _analyze_liens(self, matricula_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analisa os ônus registrados"""
        onus = []
        
        if matricula_info.get('hipoteca'):
            onus.append({
                'tipo': 'hipoteca',
                'valor': matricula_info['hipoteca']['valor'],
                'credor': matricula_info['hipoteca']['credor']
            })
            
        if matricula_info.get('penhora'):
            onus.append({
                'tipo': 'penhora',
                'processo': matricula_info['penhora']['processo'],
                'valor': matricula_info['penhora']['valor']
            })
            
        return onus
        
    def _evaluate_legal_status(self, matricula_info: Dict[str, Any]) -> Dict[str, Any]:
        """Avalia o status legal do imóvel"""
        if matricula_info.get('inconsistencias'):
            return {'status': 'irregular', 'motivo': 'Inconsistências na matrícula'}
            
        if matricula_info.get('hipoteca') or matricula_info.get('penhora'):
            return {'status': 'regular_com_onus', 'motivo': 'Ônus registrados'}
            
        return {'status': 'regular', 'motivo': 'Nenhuma irregularidade encontrada'}
        
    def _generate_recommendations(self, matricula_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gera recomendações baseadas na análise"""
        recomendacoes = []
        
        if matricula_info.get('inconsistencias'):
            recomendacoes.append({
                'tipo': 'inconsistencia',
                'descricao': 'Verificar e corrigir inconsistências na matrícula',
                'prioridade': 'alta'
            })
            
        if matricula_info.get('hipoteca'):
            recomendacoes.append({
                'tipo': 'hipoteca',
                'descricao': 'Avaliar possibilidade de quitação da hipoteca',
                'prioridade': 'media'
            })
            
        if matricula_info.get('penhora'):
            recomendacoes.append({
                'tipo': 'penhora',
                'descricao': 'Verificar status do processo judicial',
                'prioridade': 'alta'
            })
            
        return recomendacoes 