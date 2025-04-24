from typing import Dict, Any, Optional
from ..analyzers.legal_analyzer import LegalAnalyzer
from ..analyzers.financial_analyzer import FinancialAnalyzer
from ..analyzers.physical_analyzer import PhysicalAnalyzer
from ..analyzers.document_analyzer import DocumentAnalyzer
from ..utils.recommendations import RecommendationGenerator
import logging

logger = logging.getLogger(__name__)

class AnaliseImovel:
    def __init__(self, edital: str, matricula: str):
        self.edital = edital
        self.matricula = matricula
        self.legal_analyzer = LegalAnalyzer()
        self.financial_analyzer = FinancialAnalyzer()
        self.physical_analyzer = PhysicalAnalyzer()
        self.document_analyzer = DocumentAnalyzer()
        self.recommendation_generator = RecommendationGenerator()
        
    def analisar(self) -> Dict[str, Any]:
        """
        Realiza a análise completa do imóvel.
        """
        try:
            # Análise dos documentos
            doc_analysis = self.document_analyzer.analyze(self.edital, self.matricula)
            
            # Análises específicas
            legal_analysis = self.legal_analyzer.analyze(doc_analysis)
            financial_analysis = self.financial_analyzer.analyze(doc_analysis)
            physical_analysis = self.physical_analyzer.analyze(doc_analysis)
            
            # Gera recomendações
            recommendations = self.recommendation_generator.generate(
                legal_analysis,
                financial_analysis,
                physical_analysis
            )
            
            return {
                "documentacao": doc_analysis,
                "analise_juridica": legal_analysis,
                "analise_financeira": financial_analysis,
                "analise_fisica": physical_analysis,
                "recomendacoes": recommendations
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar imóvel: {str(e)}")
            raise 