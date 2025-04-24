import unittest
from analysis.monitoring import Monitoring
import time

class TestMonitoring(unittest.TestCase):
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.monitoring = Monitoring()
        
    def test_record_api_call(self):
        """Testa o registro de chamadas de API"""
        # Registra uma chamada
        self.monitoring.record_api_call("test_endpoint", 0.5)
        
        # Verifica se a chamada foi registrada
        metrics = self.monitoring.get_metrics()
        self.assertEqual(len(metrics["api_calls"]), 1)
        self.assertEqual(metrics["api_calls"][0]["endpoint"], "test_endpoint")
        self.assertEqual(metrics["api_calls"][0]["duration"], 0.5)
        
    def test_record_cache_hit(self):
        """Testa o registro de hits no cache"""
        # Registra um hit
        self.monitoring.record_cache_hit("test_key")
        
        # Verifica se o hit foi registrado
        metrics = self.monitoring.get_metrics()
        self.assertEqual(metrics["cache_hits"], 1)
        
    def test_record_cache_miss(self):
        """Testa o registro de misses no cache"""
        # Registra um miss
        self.monitoring.record_cache_miss("test_key")
        
        # Verifica se o miss foi registrado
        metrics = self.monitoring.get_metrics()
        self.assertEqual(metrics["cache_misses"], 1)
        
    def test_record_error(self):
        """Testa o registro de erros"""
        # Registra um erro
        error = {
            "error_type": "TestError",
            "error_message": "Test error message",
            "context": {"test": "context"}
        }
        self.monitoring.record_error(error)
        
        # Verifica se o erro foi registrado
        metrics = self.monitoring.get_metrics()
        self.assertEqual(len(metrics["errors"]), 1)
        self.assertEqual(metrics["errors"][0]["error_type"], "TestError")
        
    def test_get_metrics(self):
        """Testa a obtenção de métricas"""
        # Registra várias métricas
        self.monitoring.record_api_call("endpoint1", 0.5)
        self.monitoring.record_api_call("endpoint2", 1.0)
        self.monitoring.record_cache_hit("key1")
        self.monitoring.record_cache_miss("key2")
        self.monitoring.record_error({
            "error_type": "TestError",
            "error_message": "Test error message"
        })
        
        # Obtém as métricas
        metrics = self.monitoring.get_metrics()
        
        # Verifica se todas as métricas foram registradas
        self.assertEqual(len(metrics["api_calls"]), 2)
        self.assertEqual(metrics["cache_hits"], 1)
        self.assertEqual(metrics["cache_misses"], 1)
        self.assertEqual(len(metrics["errors"]), 1)
        
    def test_metrics_reset(self):
        """Testa o reset das métricas"""
        # Registra algumas métricas
        self.monitoring.record_api_call("test_endpoint", 0.5)
        self.monitoring.record_cache_hit("test_key")
        self.monitoring.record_error({
            "error_type": "TestError",
            "error_message": "Test error message"
        })
        
        # Reseta as métricas
        self.monitoring.reset_metrics()
        
        # Verifica se as métricas foram resetadas
        metrics = self.monitoring.get_metrics()
        self.assertEqual(len(metrics["api_calls"]), 0)
        self.assertEqual(metrics["cache_hits"], 0)
        self.assertEqual(metrics["cache_misses"], 0)
        self.assertEqual(len(metrics["errors"]), 0)
        
    def test_metrics_timestamp(self):
        """Testa o timestamp das métricas"""
        # Registra uma métrica
        self.monitoring.record_api_call("test_endpoint", 0.5)
        
        # Obtém as métricas
        metrics = self.monitoring.get_metrics()
        
        # Verifica se o timestamp está presente e é válido
        self.assertIn("timestamp", metrics)
        self.assertIsInstance(metrics["timestamp"], str)
        
    def test_error_handling(self):
        """Testa o tratamento de erros"""
        # Testa com dados inválidos
        with self.assertRaises(ValueError):
            self.monitoring.record_api_call("", -1)
            
        with self.assertRaises(ValueError):
            self.monitoring.record_error({})

if __name__ == '__main__':
    unittest.main() 