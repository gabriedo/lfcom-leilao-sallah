from typing import Dict, Any, List, Type, Optional
from .base_template import LeilaoTemplate
from .mega_leiloes import MegaLeiloesTemplate
from .smart_template import SmartTemplate
import logging

class LeilaoTemplateManager:
    """Gerenciador de templates para extração de dados de diferentes sites de leilão"""
    
    def __init__(self):
        """Inicializa o gerenciador de templates"""
        self.logger = logging.getLogger(__name__)
        self.templates: List[Type[LeilaoTemplate]] = [
            MegaLeiloesTemplate,  # Template específico para Mega Leilões
            SmartTemplate  # Template inteligente para outros sites
        ]
        
    def get_template(self, url: str) -> Optional[LeilaoTemplate]:
        """Retorna o template apropriado para a URL fornecida"""
        # Primeiro tenta usar templates específicos
        for template_class in self.templates[:-1]:  # Exclui o SmartTemplate
            template = template_class()
            if template.validar_url(url):
                self.logger.info(f"Usando template específico: {template_class.__name__}")
                return template
                
        # Se nenhum template específico servir, usa o SmartTemplate
        smart_template = self.templates[-1]()  # SmartTemplate é sempre o último
        if smart_template.validar_url(url):
            self.logger.info("Usando template inteligente para extração de dados")
            return smart_template
            
        return None
        
    def extrair_dados(self, url: str) -> Dict[str, Any]:
        """Extrai dados do imóvel usando o template apropriado"""
        try:
            template = self.get_template(url)
            if not template:
                self.logger.error(f"Nenhum template encontrado para a URL: {url}")
                return {'erro': 'URL não suportada'}
                
            dados = template.extrair_dados(url)
            if not dados:
                self.logger.error(f"Falha ao extrair dados da URL: {url}")
                return {'erro': 'Falha na extração de dados'}
                
            # Adiciona informação sobre o template usado
            dados['template_usado'] = template.__class__.__name__
            
            return dados
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair dados: {str(e)}")
            return {'erro': str(e)}
            
    def listar_templates(self) -> List[str]:
        """Lista os templates disponíveis"""
        return [template.__name__ for template in self.templates] 