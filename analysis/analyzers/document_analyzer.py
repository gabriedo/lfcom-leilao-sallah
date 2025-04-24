from typing import Dict, Any
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentAnalyzer:
    def analyze(self, edital: str, matricula: str) -> Dict[str, Any]:
        """
        Analisa o edital e a matrícula para extrair informações relevantes.
        """
        try:
            edital_info = self._parse_edital(edital)
            matricula_info = self._parse_matricula(matricula)
            
            return {
                "edital": edital_info,
                "matricula": matricula_info,
                "inconsistencias": self._check_inconsistencies(edital_info, matricula_info)
            }
        except Exception as e:
            logger.error(f"Erro ao analisar documentos: {str(e)}")
            raise

    def _parse_edital(self, edital: str) -> Dict[str, Any]:
        """
        Extrai informações do edital usando regex e análise de texto.
        """
        info = {}
        
        # Processo
        processo_match = re.search(r'Processo[^\d]*(\d+[-./]\d+)', edital)
        if processo_match:
            info['numero_processo'] = processo_match.group(1)
            
        # Valor
        valor_match = re.search(r'R\$\s*([\d.,]+)', edital)
        if valor_match:
            valor = valor_match.group(1).replace('.', '').replace(',', '.')
            info['valor_inicial'] = float(valor)
            
        # Data e hora
        data_match = re.search(r'(\d{2}/\d{2}/\d{4})\s*[àas]*\s*(\d{2}:\d{2})', edital)
        if data_match:
            info['data_leilao'] = data_match.group(1)
            info['hora_leilao'] = data_match.group(2)
            
        # Endereço
        endereco_match = re.search(r'(?:localizado|situado)[^\n]*([^\n]+)', edital, re.I)
        if endereco_match:
            info['endereco'] = endereco_match.group(1).strip()
            
        # Área
        area_match = re.search(r'(\d+[,.]?\d*)\s*m²', edital)
        if area_match:
            area = area_match.group(1).replace(',', '.')
            info['area'] = float(area)
            
        return info

    def _parse_matricula(self, matricula: str) -> Dict[str, Any]:
        """
        Extrai informações da matrícula usando regex e análise de texto.
        """
        info = {}
        
        # Número da matrícula
        num_match = re.search(r'Matrícula[^\d]*(\d+)', matricula)
        if num_match:
            info['numero'] = num_match.group(1)
            
        # Proprietário
        prop_match = re.search(r'(?:proprietário|dono)[^\n]*([^\n]+)', matricula, re.I)
        if prop_match:
            info['proprietario'] = prop_match.group(1).strip()
            
        # Ônus
        onus_match = re.search(r'(?:ônus|gravames)[^\n]*([^\n]+)', matricula, re.I)
        if onus_match:
            info['onus'] = onus_match.group(1).strip()
            
        return info

    def _check_inconsistencies(self, edital_info: Dict[str, Any], 
                             matricula_info: Dict[str, Any]) -> list:
        """
        Verifica inconsistências entre edital e matrícula.
        """
        inconsistencias = []
        
        # Verifica área
        if 'area' in edital_info and 'area' in matricula_info:
            if abs(edital_info['area'] - matricula_info['area']) > 0.01:
                inconsistencias.append({
                    'tipo': 'area',
                    'edital': edital_info['area'],
                    'matricula': matricula_info['area']
                })
                
        # Verifica endereço
        if 'endereco' in edital_info and 'endereco' in matricula_info:
            if not self._similar_addresses(edital_info['endereco'], 
                                        matricula_info['endereco']):
                inconsistencias.append({
                    'tipo': 'endereco',
                    'edital': edital_info['endereco'],
                    'matricula': matricula_info['endereco']
                })
                
        return inconsistencias

    def _similar_addresses(self, addr1: str, addr2: str) -> bool:
        """
        Verifica se dois endereços são similares usando comparação simplificada.
        """
        def normalize(addr: str) -> str:
            return re.sub(r'[^\w\s]', '', addr.lower())
        
        addr1_norm = normalize(addr1)
        addr2_norm = normalize(addr2)
        
        return addr1_norm in addr2_norm or addr2_norm in addr1_norm 