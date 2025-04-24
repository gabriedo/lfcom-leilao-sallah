import unittest
from analysis.analyzers.market_analyzer import MarketAnalyzer

class TestMarketAnalyzer(unittest.TestCase):
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.analyzer = MarketAnalyzer()
        
    def test_analyze_market_value(self):
        """Testa a análise de valor de mercado"""
        # Teste com dados válidos
        imovel_info = {
            'area': 100,
            'valor_inicial': 200000
        }
        resultado = self.analyzer._analyze_market_value(imovel_info)
        self.assertEqual(resultado['valor_medio_m2'], 2000)
        self.assertEqual(resultado['faixa_valor'], 'media')
        
        # Teste com dados inválidos
        imovel_info = {
            'area': 0,
            'valor_inicial': 0
        }
        resultado = self.analyzer._analyze_market_value(imovel_info)
        self.assertEqual(resultado['valor_medio_m2'], 0)
        self.assertEqual(resultado['faixa_valor'], 'indeterminada')
        
    def test_analyze_location(self):
        """Testa a análise de localização"""
        # Teste com endereço completo
        imovel_info = {
            'endereco': 'Rua A, Bairro B, Cidade C'
        }
        resultado = self.analyzer._analyze_location(imovel_info)
        self.assertEqual(resultado['bairro'], 'Rua A')
        self.assertEqual(resultado['cidade'], 'Bairro B')
        self.assertEqual(resultado['estado'], 'Cidade C')
        
        # Teste com endereço vazio
        imovel_info = {
            'endereco': ''
        }
        resultado = self.analyzer._analyze_location(imovel_info)
        self.assertEqual(resultado['bairro'], 'indeterminado')
        self.assertEqual(resultado['cidade'], 'indeterminada')
        self.assertEqual(resultado['estado'], 'indeterminado')
        
    def test_analyze_potential(self):
        """Testa a análise de potencial"""
        # Teste com área grande
        imovel_info = {
            'area': 1200,
            'endereco': 'Rua A, Bairro B, Cidade C'
        }
        resultado = self.analyzer._analyze_potential(imovel_info)
        self.assertEqual(resultado['nivel'], 'alto')
        self.assertIn('comercial', resultado['usos_possiveis'])
        self.assertIn('industrial', resultado['usos_possiveis'])
        
        # Teste com área média
        imovel_info = {
            'area': 600,
            'endereco': 'Rua A, Bairro B, Cidade C'
        }
        resultado = self.analyzer._analyze_potential(imovel_info)
        self.assertEqual(resultado['nivel'], 'medio')
        self.assertIn('residencial', resultado['usos_possiveis'])
        self.assertIn('comercial', resultado['usos_possiveis'])
        
    def test_calculate_indicators(self):
        """Testa o cálculo de indicadores"""
        imovel_info = {
            'area': 100,
            'valor_inicial': 200000,
            'endereco': 'Rua A, Bairro B, Cidade C'
        }
        resultado = self.analyzer._calculate_indicators(imovel_info)
        self.assertEqual(resultado['liquidez'], 'media')
        self.assertEqual(resultado['demanda'], 'alta')
        self.assertEqual(resultado['potencial_valorizacao'], 'baixo')
        self.assertEqual(resultado['risco'], 'medio')
        
    def test_generate_recommendations(self):
        """Testa a geração de recomendações"""
        # Teste com valor baixo
        imovel_info = {
            'area': 100,
            'valor_inicial': 50000,
            'endereco': 'Rua A, Bairro B, Cidade C'
        }
        resultado = self.analyzer._generate_recommendations(imovel_info)
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]['tipo'], 'investimento')
        self.assertEqual(resultado[0]['prioridade'], 'alta')
        
        # Teste com potencial alto
        imovel_info = {
            'area': 1200,
            'valor_inicial': 200000,
            'endereco': 'Rua A, Bairro B, Cidade C'
        }
        resultado = self.analyzer._generate_recommendations(imovel_info)
        self.assertEqual(len(resultado), 2)
        self.assertEqual(resultado[1]['tipo'], 'desenvolvimento')
        self.assertEqual(resultado[1]['prioridade'], 'media')
        
    def test_complete_analysis(self):
        """Testa a análise completa"""
        imovel_info = {
            'area': 100,
            'valor_inicial': 200000,
            'endereco': 'Rua A, Bairro B, Cidade C'
        }
        resultado = self.analyzer.analyze(imovel_info)
        self.assertIn('valor_mercado', resultado)
        self.assertIn('localizacao', resultado)
        self.assertIn('potencial', resultado)
        self.assertIn('indicadores', resultado)
        self.assertIn('recomendacoes', resultado)
        
if __name__ == '__main__':
    unittest.main() 