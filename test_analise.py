import unittest
from analise_imovel import AnaliseImovel
import logging

# Configuração de logging para os testes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestAnaliseImovel(unittest.TestCase):
    def setUp(self):
        self.edital = "Edital de Teste"
        self.matricula = "123456"
        self.analise = AnaliseImovel(self.edital, self.matricula)
    
    def test_analise_completa(self):
        """Testa a análise completa do imóvel"""
        resultado = self.analise.analisar()
        
        # Verifica se o resultado contém todas as chaves esperadas
        self.assertIn('info_basicas', resultado)
        self.assertIn('situacao', resultado)
        self.assertIn('metricas', resultado)
        self.assertIn('recomendacoes', resultado)
        
        # Verifica o conteúdo das informações básicas
        info_basicas = resultado['info_basicas']
        self.assertIn('endereco', info_basicas)
        self.assertIn('area', info_basicas)
        self.assertIn('valor', info_basicas)
        
        # Verifica o conteúdo da situação
        situacao = resultado['situacao']
        self.assertIn('status', situacao)
        self.assertIn('pendencias', situacao)
        self.assertIn('documentacao', situacao)
        
        # Verifica o conteúdo das métricas
        metricas = resultado['metricas']
        self.assertIn('valor_m2', metricas)
        self.assertIn('tendencia_mercado', metricas)
        
        # Verifica o conteúdo das recomendações
        recomendacoes = resultado['recomendacoes']
        self.assertIn('sugestoes', recomendacoes)
        self.assertIn('riscos', recomendacoes)
    
    def test_info_basicas(self):
        """Testa a busca de informações básicas"""
        info = self.analise._buscar_info_basicas()
        self.assertIsInstance(info, dict)
        self.assertGreater(info['valor'], 0)
        self.assertGreater(info['area'], 0)
        self.assertIsInstance(info['endereco'], str)
    
    def test_calculo_metricas(self):
        """Testa o cálculo de métricas"""
        info_basicas = {
            'valor': 500000,
            'area': 100
        }
        metricas = self.analise._calcular_metricas(info_basicas)
        self.assertEqual(metricas['valor_m2'], 5000)
        self.assertIn(metricas['tendencia_mercado'], ['estavel', 'alta', 'baixa'])
    
    def test_recomendacoes(self):
        """Testa a geração de recomendações"""
        situacao = {'status': 'regular', 'pendencias': [], 'documentacao': 'completa'}
        metricas = {'valor_m2': 5000, 'tendencia_mercado': 'estavel'}
        
        recomendacoes = self.analise._gerar_recomendacoes(situacao, metricas)
        self.assertIsInstance(recomendacoes['sugestoes'], list)
        self.assertIsInstance(recomendacoes['riscos'], list)
        self.assertTrue(len(recomendacoes['sugestoes']) > 0)
        self.assertTrue(len(recomendacoes['riscos']) > 0)

if __name__ == '__main__':
    unittest.main() 