import unittest
from unittest.mock import patch, MagicMock
from analysis.integrations.osm_api import OSMAPI
import time

class TestOSMAPI(unittest.TestCase):
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.osm = OSMAPI()
        
    @patch('requests.get')
    def test_search_location(self, mock_get):
        """Testa a busca de localização"""
        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.json.return_value = [{
            "display_name": "São Paulo, SP, Brasil",
            "lat": "-23.5505",
            "lon": "-46.6333",
            "address": {
                "city": "São Paulo",
                "state": "SP",
                "country": "Brasil"
            }
        }]
        mock_get.return_value = mock_response
        
        # Testa a busca
        result = self.osm.search_location("São Paulo")
        
        # Verifica se a chamada foi feita corretamente
        mock_get.assert_called_once()
        
        # Verifica se o resultado está no formato esperado
        self.assertEqual(result["nome"], "São Paulo, SP, Brasil")
        self.assertEqual(result["coordenadas"]["latitude"], "-23.5505")
        self.assertEqual(result["coordenadas"]["longitude"], "-46.6333")
        self.assertEqual(result["endereco"]["cidade"], "São Paulo")
        
    @patch('requests.get')
    def test_reverse_geocode(self, mock_get):
        """Testa o geocoding reverso"""
        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "display_name": "Rua Augusta, São Paulo, SP, Brasil",
            "address": {
                "road": "Rua Augusta",
                "city": "São Paulo",
                "state": "SP",
                "country": "Brasil"
            }
        }
        mock_get.return_value = mock_response
        
        # Testa o geocoding reverso
        result = self.osm.reverse_geocode(-23.5505, -46.6333)
        
        # Verifica se a chamada foi feita corretamente
        mock_get.assert_called_once()
        
        # Verifica se o resultado está no formato esperado
        self.assertEqual(result["endereco_completo"], "Rua Augusta, São Paulo, SP, Brasil")
        self.assertEqual(result["rua"], "Rua Augusta")
        self.assertEqual(result["cidade"], "São Paulo")
        
    @patch('requests.get')
    def test_get_pois_nearby(self, mock_get):
        """Testa a busca de POIs próximos"""
        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "elements": [
                {
                    "tags": {
                        "amenity": "restaurant",
                        "name": "Restaurante Teste"
                    },
                    "lat": -23.5505,
                    "lon": -46.6333
                },
                {
                    "tags": {
                        "shop": "supermarket",
                        "name": "Supermercado Teste"
                    },
                    "lat": -23.5506,
                    "lon": -46.6334
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Testa a busca de POIs
        result = self.osm.get_pois_nearby(-23.5505, -46.6333, 1000)
        
        # Verifica se a chamada foi feita corretamente
        mock_get.assert_called_once()
        
        # Verifica se o resultado está no formato esperado
        self.assertEqual(len(result["amenity"]), 1)
        self.assertEqual(len(result["shop"]), 1)
        self.assertEqual(result["amenity"][0]["nome"], "Restaurante Teste")
        
    @patch('requests.get')
    def test_get_location_analysis(self, mock_get):
        """Testa a análise completa de localização"""
        # Mock das respostas para cada chamada
        mock_response = MagicMock()
        mock_response.json.side_effect = [
            {  # search_location
                "display_name": "São Paulo, SP, Brasil",
                "lat": "-23.5505",
                "lon": "-46.6333",
                "address": {
                    "city": "São Paulo",
                    "state": "SP",
                    "country": "Brasil"
                }
            },
            {  # get_pois_nearby
                "elements": [
                    {
                        "tags": {
                            "amenity": "restaurant",
                            "name": "Restaurante Teste"
                        },
                        "lat": -23.5505,
                        "lon": -46.6333
                    }
                ]
            }
        ]
        mock_get.return_value = mock_response
        
        # Testa a análise completa
        result = self.osm.get_location_analysis("São Paulo")
        
        # Verifica se as chamadas foram feitas corretamente
        self.assertEqual(mock_get.call_count, 2)
        
        # Verifica se o resultado está no formato esperado
        self.assertIn("localizacao", result)
        self.assertIn("pois_proximos", result)
        self.assertIn("metricas", result)
        
    def test_rate_limiting(self):
        """Testa o rate limiting"""
        # Testa múltiplas chamadas em sequência
        start_time = time.time()
        
        # Faz 3 chamadas (deve levar pelo menos 2 segundos)
        for _ in range(3):
            self.osm.search_location("test")
            
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Verifica se o tempo mínimo foi respeitado
        self.assertGreaterEqual(elapsed_time, 2)
        
    def test_error_handling(self):
        """Testa o tratamento de erros"""
        # Testa com dados inválidos
        result = self.osm.search_location("")
        self.assertIn("error", result)
        
        result = self.osm.reverse_geocode(0, 0)
        self.assertIn("error", result)
        
        result = self.osm.get_pois_nearby(0, 0, -1)
        self.assertIn("error", result)
        
        result = self.osm.get_location_analysis("")
        self.assertIn("error", result)

if __name__ == '__main__':
    unittest.main() 