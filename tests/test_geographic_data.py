import unittest
from unittest.mock import patch, MagicMock
from analysis.integrations.geographic_data import GeographicData
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

class TestGeographicData(unittest.TestCase):
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.geo = GeographicData()
        
    @patch('analysis.integrations.geographic_data.requests.get')
    def test_get_ibge_data(self, mock_get):
        """Testa a obtenção de dados do IBGE"""
        # Mock da resposta da API do IBGE
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'nome': 'São Paulo',
            'microrregiao': {'mesorregiao': {'UF': {'nome': 'São Paulo'}}},
            'regiao-imediata': {'regiao-intermediaria': {'UF': {'regiao': {'nome': 'Sudeste'}}}}
        }
        mock_get.return_value = mock_response
        
        # Teste com código válido
        resultado = self.geo.get_ibge_data('3550308')
        self.assertEqual(resultado['nome'], 'São Paulo')
        self.assertEqual(resultado['estado'], 'São Paulo')
        self.assertEqual(resultado['regiao'], 'Sudeste')
        
        # Teste com código inválido
        mock_get.side_effect = Exception('Erro na API')
        resultado = self.geo.get_ibge_data('0000000')
        self.assertIn('erro', resultado)
        
    @patch('analysis.integrations.geographic_data.requests.get')
    def test_get_weather_data(self, mock_get):
        """Testa a obtenção de dados meteorológicos"""
        # Mock da resposta da API do OpenWeather
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'main': {'temp': 25.5},
            'weather': [{'description': 'céu limpo'}],
            'wind': {'speed': 3.2}
        }
        mock_get.return_value = mock_response
        
        # Teste com coordenadas válidas
        resultado = self.geo.get_weather_data(-23.5505, -46.6333)
        self.assertEqual(resultado['temperatura'], 25.5)
        self.assertEqual(resultado['condicao'], 'céu limpo')
        self.assertEqual(resultado['vento'], 3.2)
        
        # Teste com coordenadas inválidas
        mock_get.side_effect = Exception('Erro na API')
        resultado = self.geo.get_weather_data(0, 0)
        self.assertIn('erro', resultado)
        
    @patch('analysis.integrations.geographic_data.requests.get')
    def test_get_environmental_data(self, mock_get):
        """Testa a obtenção de dados ambientais"""
        # Mock da resposta da API do OpenAQ
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'results': [
                {'parameter': 'pm25', 'value': 12.5},
                {'parameter': 'pm10', 'value': 20.0}
            ]
        }
        mock_get.return_value = mock_response
        
        # Teste com coordenadas válidas
        resultado = self.geo.get_environmental_data(-23.5505, -46.6333)
        self.assertEqual(resultado['pm25'], 12.5)
        self.assertEqual(resultado['pm10'], 20.0)
        
        # Teste com coordenadas inválidas
        mock_get.side_effect = Exception('Erro na API')
        resultado = self.geo.get_environmental_data(0, 0)
        self.assertIn('erro', resultado)
        
    @patch('analysis.integrations.geographic_data.GeographicData.get_ibge_data')
    @patch('analysis.integrations.geographic_data.GeographicData.get_weather_data')
    @patch('analysis.integrations.geographic_data.GeographicData.get_environmental_data')
    def test_get_complete_location_data(self, mock_env, mock_weather, mock_ibge):
        """Testa a obtenção de todos os dados de uma localização"""
        # Mock das respostas
        mock_ibge.return_value = {
            'nome': 'São Paulo',
            'estado': 'São Paulo',
            'regiao': 'Sudeste'
        }
        mock_weather.return_value = {
            'temperatura': 25.5,
            'condicao': 'céu limpo',
            'vento': 3.2
        }
        mock_env.return_value = {
            'pm25': 12.5,
            'pm10': 20.0
        }
        
        # Teste com dados válidos
        resultado = self.geo.get_complete_location_data(-23.5505, -46.6333, '3550308')
        self.assertEqual(resultado['cidade'], 'São Paulo')
        self.assertEqual(resultado['temperatura'], 25.5)
        self.assertEqual(resultado['pm25'], 12.5)
        
        # Teste com erro em uma das APIs
        mock_ibge.side_effect = Exception('Erro na API')
        resultado = self.geo.get_complete_location_data(-23.5505, -46.6333, '0000000')
        self.assertIn('erro', resultado)
        
    def test_error_handling(self):
        """Testa o tratamento de erros"""
        # Testa com dados inválidos
        result = self.geo.get_ibge_data("invalid_code")
        self.assertIn("error", result)
        
        result = self.geo.get_weather_data(0, 0)
        self.assertIn("error", result)
        
        result = self.geo.get_environmental_data(0, 0)
        self.assertIn("error", result)
        
        result = self.geo.get_complete_location_data(0, 0, "invalid_code")
        self.assertIn("error", result)

if __name__ == '__main__':
    unittest.main() 