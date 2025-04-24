import unittest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from analise_imovel import AnaliseImovel

class TestAnaliseImovel(unittest.TestCase):
    def setUp(self):
        self.analise = AnaliseImovel()
        
    @patch('analise_imovel.LeilaoTemplateManager')
    @patch('analise_imovel.LegalAnalyzer')
    @patch('analise_imovel.MarketAnalyzer')
    async def test_analyze_from_url_success(self, mock_market, mock_legal, mock_template):
        # Configura mocks
        mock_data = {
            "tipo_imovel": "Apartamento",
            "area_total": 100,
            "endereco": "Rua Teste, 123",
            "valor_inicial": 500000
        }
        mock_template.return_value.extract_data = AsyncMock(return_value=mock_data)
        mock_legal.return_value.analyze = AsyncMock(return_value={"risco": "baixo"})
        mock_market.return_value.analyze = AsyncMock(return_value={"valorização": 0.1})
        
        # Executa análise
        url = "http://teste.com/leilao/123"
        result = await self.analise.analyze_from_url(url)
        
        # Verifica resultado
        self.assertEqual(result["dados_imovel"], mock_data)
        self.assertEqual(result["analise_legal"], {"risco": "baixo"})
        self.assertEqual(result["analise_mercado"], {"valorização": 0.1})
        self.assertEqual(result["url_origem"], url)
        self.assertTrue("data_analise" in result)
        
    @patch('analise_imovel.LegalAnalyzer')
    @patch('analise_imovel.MarketAnalyzer')
    async def test_analyze_from_documents_success(self, mock_market, mock_legal):
        # Configura mocks
        mock_legal.return_value.analyze_documents = AsyncMock(return_value={"risco": "baixo"})
        mock_market.return_value.analyze_property = AsyncMock(return_value={"valorização": 0.1})
        
        # Dados de teste
        documents = [
            {"tipo": "matricula", "conteudo": "Texto da matrícula"},
            {"tipo": "edital", "conteudo": "Texto do edital"}
        ]
        property_data = {
            "tipo_imovel": "Casa",
            "area_total": 200,
            "endereco": "Rua Teste, 456",
            "valor_inicial": 800000
        }
        
        # Executa análise
        result = await self.analise.analyze_from_documents(documents, property_data)
        
        # Verifica resultado
        self.assertEqual(result["dados_imovel"], property_data)
        self.assertEqual(result["analise_legal"], {"risco": "baixo"})
        self.assertEqual(result["analise_mercado"], {"valorização": 0.1})
        self.assertEqual(result["documentos"], documents)
        self.assertTrue("data_analise" in result)
        
    async def test_analyze_from_url_invalid_url(self):
        with self.assertRaises(ValueError) as context:
            await self.analise.analyze_from_url("url_invalida")
        self.assertEqual(str(context.exception), "URL inválida")
        
    async def test_analyze_from_documents_invalid_docs(self):
        with self.assertRaises(ValueError) as context:
            await self.analise.analyze_from_documents([], {})
        self.assertEqual(str(context.exception), "Documentos inválidos")
        
    async def test_analyze_from_documents_invalid_data(self):
        docs = [{"tipo": "matricula", "conteudo": "teste"}]
        with self.assertRaises(ValueError) as context:
            await self.analise.analyze_from_documents(docs, {})
        self.assertEqual(str(context.exception), "Dados do imóvel inválidos")

if __name__ == '__main__':
    unittest.main() 