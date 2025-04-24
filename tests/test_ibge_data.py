import unittest
from unittest.mock import patch, MagicMock
from analysis.integrations.ibge_data import IBGEDataCollector

class TestIBGEDataCollector(unittest.TestCase):
    def setUp(self):
        self.collector = IBGEDataCollector()

    @patch('requests.get')
    def test_get_codigo_municipio_success(self, mock_get):
        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": 3550308, "nome": "São Paulo", "microrregiao": {"mesorregiao": {"UF": {"sigla": "SP"}}}}
        ]
        mock_get.return_value = mock_response

        # Teste
        codigo = self.collector.get_codigo_municipio("São Paulo", "SP")
        self.assertEqual(codigo, 3550308)

    @patch('requests.get')
    def test_get_codigo_municipio_not_found(self, mock_get):
        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # Teste
        codigo = self.collector.get_codigo_municipio("Cidade Inexistente", "XX")
        self.assertIsNone(codigo)

    @patch('requests.get')
    def test_get_municipio_data_success(self, mock_get):
        # Mock das respostas da API
        mock_response = MagicMock()
        mock_response.json.side_effect = [
            [{"nome": "São Paulo", "populacao": 12000000}],
            [{"valor": 1000000000}],
            [{"id": 1, "valor": 0.8}]
        ]
        mock_get.return_value = mock_response

        # Teste
        dados = self.collector.get_municipio_data(3550308)
        self.assertIsNotNone(dados)
        self.assertIn("demograficos", dados)
        self.assertIn("economicos", dados)
        self.assertIn("sociais", dados)

    @patch('requests.get')
    def test_get_municipio_data_error(self, mock_get):
        # Mock de erro na API
        mock_get.side_effect = Exception("Erro na API")

        # Teste
        dados = self.collector.get_municipio_data(3550308)
        self.assertIsNone(dados)

    def test_calcular_densidade(self):
        # Teste
        densidade = self.collector._calcular_densidade(1000000, 1000)
        self.assertEqual(densidade, 1000)

    def test_calcular_pib_per_capita(self):
        # Teste
        pib_per_capita = self.collector._calcular_pib_per_capita(1000000, 1000)
        self.assertEqual(pib_per_capita, 1000)

    def test_calcular_idh(self):
        # Teste
        idh = self.collector._calcular_idh(0.8, 0.7, 0.9)
        self.assertEqual(idh, 0.8)

if __name__ == '__main__':
    unittest.main() 