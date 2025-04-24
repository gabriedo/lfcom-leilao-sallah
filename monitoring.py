import time
import logging
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class Metrics:
    api_calls: Dict[str, list] = None
    cache_hits: int = 0
    cache_misses: int = 0
    errors: list = None
    
    def __post_init__(self):
        if self.api_calls is None:
            self.api_calls = {}
        if self.errors is None:
            self.errors = []

class Monitoring:
    def __init__(self):
        """Inicializa o monitoramento de métricas"""
        self.metrics = {
            'api_calls': [],
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': [],
            'start_time': time.time()
        }
        
    def record_api_call(self, endpoint: str, duration: float) -> None:
        """Registra uma chamada de API"""
        self.metrics['api_calls'].append({
            'endpoint': endpoint,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        })
        
    def record_cache_hit(self) -> None:
        """Registra um hit no cache"""
        self.metrics['cache_hits'] += 1
        
    def record_cache_miss(self) -> None:
        """Registra um miss no cache"""
        self.metrics['cache_misses'] += 1
        
    def record_cache_operation(self, is_hit: bool, cache_size: int) -> None:
        """Registra uma operação de cache"""
        if is_hit:
            self.record_cache_hit()
        else:
            self.record_cache_miss()
        self.metrics['cache_size'] = cache_size
        
    def record_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """Registra um erro"""
        self.metrics['errors'].append({
            'type': type(error).__name__,
            'message': str(error),
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        })
        
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna todas as métricas coletadas"""
        return {
            **self.metrics,
            'uptime': time.time() - self.metrics['start_time']
        }
        
    def reset_metrics(self) -> None:
        """Reseta todas as métricas"""
        self.metrics = {
            'api_calls': [],
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': [],
            'start_time': time.time()
        }

# Instância global do coletor de métricas
metrics_collector = Monitoring() 