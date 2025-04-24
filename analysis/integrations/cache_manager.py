import json
import os
import time
from typing import Dict, Any, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
        """
        Inicializa o gerenciador de cache.
        
        Args:
            cache_dir: Diretório para armazenar os arquivos de cache
            ttl_hours: Tempo de vida do cache em horas
        """
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        
        # Cria o diretório de cache se não existir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
    def _get_cache_path(self, key: str) -> str:
        """
        Gera o caminho do arquivo de cache.
        
        Args:
            key: Chave do cache
            
        Returns:
            Caminho do arquivo de cache
        """
        return os.path.join(self.cache_dir, f"{key}.json")
        
    def _generate_key(self, method: str, **kwargs) -> str:
        """
        Gera uma chave única para o cache.
        
        Args:
            method: Nome do método
            **kwargs: Parâmetros do método
            
        Returns:
            Chave única para o cache
        """
        # Ordena os parâmetros para garantir consistência
        sorted_params = sorted(kwargs.items())
        param_str = "_".join(f"{k}_{v}" for k, v in sorted_params)
        return f"{method}_{param_str}"
        
    def get(self, method: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Obtém dados do cache.
        
        Args:
            method: Nome do método
            **kwargs: Parâmetros do método
            
        Returns:
            Dados do cache ou None se não existir ou expirado
        """
        try:
            key = self._generate_key(method, **kwargs)
            cache_path = self._get_cache_path(key)
            
            if not os.path.exists(cache_path):
                return None
                
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
                
            # Verifica se o cache expirou
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cache_time > self.ttl:
                os.remove(cache_path)
                return None
                
            return cache_data['data']
            
        except Exception as e:
            logger.error(f"Erro ao obter cache: {str(e)}")
            return None
            
    def set(self, method: str, data: Dict[str, Any], **kwargs) -> None:
        """
        Armazena dados no cache.
        
        Args:
            method: Nome do método
            data: Dados a serem armazenados
            **kwargs: Parâmetros do método
        """
        try:
            key = self._generate_key(method, **kwargs)
            cache_path = self._get_cache_path(key)
            
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
                
        except Exception as e:
            logger.error(f"Erro ao armazenar cache: {str(e)}")
            
    def clear_expired(self) -> None:
        """
        Remove todos os caches expirados.
        """
        try:
            now = datetime.now()
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    cache_path = os.path.join(self.cache_dir, filename)
                    with open(cache_path, 'r') as f:
                        cache_data = json.load(f)
                        cache_time = datetime.fromisoformat(cache_data['timestamp'])
                        if now - cache_time > self.ttl:
                            os.remove(cache_path)
                            
        except Exception as e:
            logger.error(f"Erro ao limpar cache expirado: {str(e)}")
            
    def clear_all(self) -> None:
        """
        Remove todos os caches.
        """
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
                    
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {str(e)}") 