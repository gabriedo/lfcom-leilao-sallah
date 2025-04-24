import unittest
from analysis.analyzers.legal_analyzer import LegalAnalyzer

class TestLegalAnalyzer(unittest.TestCase):
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.analyzer = LegalAnalyzer()
        
    def test_analyze_risks(self):
        """Testa a análise de riscos legais"""
        # Teste sem riscos
        doc_info = {
            'restricoes': []
        }
        resultado = self.analyzer._analyze_risks(doc_info)
        self.assertEqual(resultado['nivel'], 'baixo')
        self.assertEqual(len(resultado['riscos']), 0)
        
        # Teste com penhora
        doc_info = {
            'restricoes': ['penhora']
        }
        resultado = self.analyzer._analyze_risks(doc_info)
        self.assertEqual(resultado['nivel'], 'alto')
        self.assertEqual(len(resultado['riscos']), 1)
        self.assertEqual(resultado['riscos'][0]['tipo'], 'penhora')
        
        # Teste com hipoteca
        doc_info = {
            'restricoes': ['hipoteca']
        }
        resultado = self.analyzer._analyze_risks(doc_info)
        self.assertEqual(resultado['nivel'], 'medio')
        self.assertEqual(len(resultado['riscos']), 1)
        self.assertEqual(resultado['riscos'][0]['tipo'], 'hipoteca')
        
    def test_analyze_liens(self):
        """Testa a análise de ônus"""
        # Teste sem ônus
        doc_info = {
            'onus': []
        }
        resultado = self.analyzer._analyze_liens(doc_info)
        self.assertEqual(len(resultado['onus']), 0)
        
        # Teste com múltiplos ônus
        doc_info = {
            'onus': ['usufruto', 'servidao']
        }
        resultado = self.analyzer._analyze_liens(doc_info)
        self.assertEqual(len(resultado['onus']), 2)
        self.assertIn('usufruto', [o['tipo'] for o in resultado['onus']])
        self.assertIn('servidao', [o['tipo'] for o in resultado['onus']])
        
    def test_evaluate_legal_status(self):
        """Testa a avaliação do status legal"""
        # Teste sem restrições
        doc_info = {
            'restricoes': []
        }
        resultado = self.analyzer._evaluate_legal_status(doc_info)
        self.assertEqual(resultado['status'], 'regular')
        
        # Teste com penhora
        doc_info = {
            'restricoes': ['penhora']
        }
        resultado = self.analyzer._evaluate_legal_status(doc_info)
        self.assertEqual(resultado['status'], 'irregular')
        
    def test_generate_recommendations(self):
        """Testa a geração de recomendações"""
        # Teste sem riscos
        doc_info = {
            'restricoes': []
        }
        resultado = self.analyzer._generate_recommendations(doc_info)
        self.assertEqual(len(resultado), 0)
        
        # Teste com penhora
        doc_info = {
            'restricoes': ['penhora']
        }
        resultado = self.analyzer._generate_recommendations(doc_info)
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]['tipo'], 'regularizacao')
        self.assertEqual(resultado[0]['prioridade'], 'alta')
        
    def test_complete_analysis(self):
        """Testa a análise completa"""
        doc_info = {
            'restricoes': ['penhora'],
            'onus': ['usufruto']
        }
        resultado = self.analyzer.analyze(doc_info)
        
        # Verifica a estrutura do resultado
        self.assertIn('riscos', resultado)
        self.assertIn('onus', resultado)
        self.assertIn('status', resultado)
        self.assertIn('recomendacoes', resultado)
        
        # Verifica os valores
        self.assertEqual(resultado['riscos']['nivel'], 'alto')
        self.assertEqual(len(resultado['onus']), 1)
        self.assertEqual(resultado['status']['status'], 'irregular')
        self.assertEqual(len(resultado['recomendacoes']), 1)

if __name__ == '__main__':
    unittest.main() 