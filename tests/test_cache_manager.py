import unittest
import os
import json
import time
from datetime import datetime, timedelta
from analysis.integrations.cache_manager import CacheManager
import shutil

class TestCacheManager(unittest.TestCase):
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.test_cache_dir = "test_cache"
        self.cache = CacheManager(cache_dir=self.test_cache_dir, ttl_hours=1)
        
    def tearDown(self):
        """Limpeza após cada teste"""
        if os.path.exists(self.test_cache_dir):
            shutil.rmtree(self.test_cache_dir)
            
    def test_cache_creation(self):
        """Testa a criação do diretório de cache"""
        self.assertTrue(os.path.exists(self.test_cache_dir))
        
    def test_cache_set_and_get(self):
        """Testa armazenamento e recuperação de dados do cache"""
        # Dados de teste
        test_data = {"test": "data"}
        
        # Armazena no cache
        self.cache.set("test_method", test_data, param1="value1")
        
        # Recupera do cache
        cached_data = self.cache.get("test_method", param1="value1")
        
        # Verifica se os dados foram armazenados e recuperados corretamente
        self.assertEqual(cached_data, test_data)
        
    def test_cache_expiration(self):
        """Testa a expiração do cache"""
        # Cria um cache com TTL de 1 segundo
        cache = CacheManager(cache_dir=self.test_cache_dir, ttl_hours=1/3600)  # 1 segundo
        
        # Armazena dados
        cache.set("test_method", {"test": "data"}, param1="value1")
        
        # Aguarda 2 segundos
        time.sleep(2)
        
        # Tenta recuperar os dados
        cached_data = cache.get("test_method", param1="value1")
        
        # Verifica se o cache expirou
        self.assertIsNone(cached_data)
        
    def test_cache_key_generation(self):
        """Testa a geração de chaves de cache"""
        # Testa com diferentes parâmetros
        key1 = self.cache._generate_key("method1", param1="value1")
        key2 = self.cache._generate_key("method1", param1="value2")
        key3 = self.cache._generate_key("method2", param1="value1")
        
        # Verifica se as chaves são diferentes
        self.assertNotEqual(key1, key2)
        self.assertNotEqual(key1, key3)
        self.assertNotEqual(key2, key3)
        
    def test_cache_clear_expired(self):
        """Testa a limpeza de cache expirado"""
        # Cria um cache com TTL curto
        cache = CacheManager(cache_dir=self.test_cache_dir, ttl_hours=1/3600)  # 1 segundo
        
        # Armazena dados
        cache.set("test_method1", {"test": "data1"}, param1="value1")
        cache.set("test_method2", {"test": "data2"}, param1="value2")
        
        # Aguarda 2 segundos
        time.sleep(2)
        
        # Limpa cache expirado
        cache.clear_expired()
        
        # Verifica se os arquivos foram removidos
        self.assertEqual(len(os.listdir(self.test_cache_dir)), 0)
        
    def test_cache_clear_all(self):
        """Testa a limpeza total do cache"""
        # Armazena dados
        self.cache.set("test_method1", {"test": "data1"}, param1="value1")
        self.cache.set("test_method2", {"test": "data2"}, param1="value2")
        
        # Limpa todo o cache
        self.cache.clear_all()
        
        # Verifica se os arquivos foram removidos
        self.assertEqual(len(os.listdir(self.test_cache_dir)), 0)
        
    def test_cache_file_format(self):
        """Testa o formato do arquivo de cache"""
        # Armazena dados
        test_data = {"test": "data"}
        self.cache.set("test_method", test_data, param1="value1")
        
        # Lê o arquivo diretamente
        cache_path = os.path.join(self.test_cache_dir, "test_method_param1_value1.json")
        with open(cache_path, 'r') as f:
            cache_content = json.load(f)
            
        # Verifica o formato do arquivo
        self.assertIn("timestamp", cache_content)
        self.assertIn("data", cache_content)
        self.assertEqual(cache_content["data"], test_data)
        
    def test_cache_error_handling(self):
        """Testa o tratamento de erros"""
        # Testa com diretório de cache inválido
        with self.assertRaises(Exception):
            CacheManager(cache_dir="/invalid/path")
            
        # Testa com TTL inválido
        with self.assertRaises(Exception):
            CacheManager(ttl_hours=-1)

if __name__ == '__main__':
    unittest.main() 