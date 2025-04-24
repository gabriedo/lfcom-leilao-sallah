import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from config import logger, REPORTS_DIR, CACHE_TTL
from monitoring import metrics_collector
import hashlib

class CacheManager:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "analises_cache.json")
        self.images_cache_file = os.path.join(cache_dir, "images_cache.json")
        self.cache_ttl = 7 * 24 * 3600  # 7 dias em segundos
        
        # Cria diretório de cache se não existir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Inicializa os arquivos de cache se não existirem
        if not os.path.exists(self.cache_file):
            self._save_cache({})
        if not os.path.exists(self.images_cache_file):
            self._save_images_cache({})
            
        # Inicializa o campo cache_size no dicionário de métricas
        metrics_collector.metrics['cache_size'] = 0
    
    def _load_cache(self) -> Dict:
        """Carrega o cache do arquivo."""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar cache: {str(e)}")
            return {}
    
    def _save_cache(self, cache: Dict):
        """Salva o cache no arquivo."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {str(e)}")
            
    def _load_images_cache(self) -> Dict:
        """Carrega o cache de imagens do arquivo."""
        try:
            with open(self.images_cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar cache de imagens: {str(e)}")
            return {}
    
    def _save_images_cache(self, cache: Dict):
        """Salva o cache de imagens no arquivo."""
        try:
            with open(self.images_cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar cache de imagens: {str(e)}")
    
    def _generate_key(self, edital: str, matricula: str) -> str:
        """Gera uma chave única para o cache baseada no conteúdo dos documentos."""
        content = f"{edital}{matricula}".encode('utf-8')
        return hashlib.md5(content).hexdigest()
        
    def _generate_image_key(self, url: str) -> str:
        """Gera uma chave única para o cache de imagens baseada na URL."""
        return hashlib.md5(url.encode('utf-8')).hexdigest()
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Recupera um item do cache de imagens."""
        cache = self._load_images_cache()
        
        if key in cache:
            entry = cache[key]
            cache_time = datetime.fromisoformat(entry['timestamp'])
            if datetime.now() - cache_time < timedelta(seconds=self.cache_ttl):
                logger.info(f"Item encontrado no cache: {key}")
                return entry['data']
            else:
                logger.info(f"Cache expirado para: {key}")
                del cache[key]
                self._save_images_cache(cache)
        return None
    
    def set(self, key: str, data: Any, ttl: int = None):
        """Salva um item no cache de imagens."""
        cache = self._load_images_cache()
        
        cache[key] = {
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'ttl': ttl or self.cache_ttl
        }
        
        self._save_images_cache(cache)
        logger.info(f"Item salvo no cache: {key}")
    
    def get_cached_analysis(self, edital: str, matricula: str) -> Optional[Dict[str, Any]]:
        """
        Recupera uma análise do cache se existir e não estiver expirada.
        
        Args:
            edital: Texto do edital
            matricula: Texto da matrícula
            
        Returns:
            Dict com a análise ou None se não encontrada/expirada
        """
        cache = self._load_cache()
        key = self._generate_key(edital, matricula)
        
        if key in cache:
            entry = cache[key]
            if datetime.now() - entry['timestamp'] < timedelta(seconds=self.cache_ttl):
                logger.info(f"Análise encontrada no cache: {key}")
                metrics_collector.record_cache_operation(True, len(cache))
                return entry['data']
            else:
                logger.info(f"Cache expirado para: {key}")
                del cache[key]
                self._save_cache(cache)
        
        metrics_collector.record_cache_operation(False, len(cache))
        return None
    
    def save_analysis(self, edital: str, matricula: str, analysis: Dict[str, Any]) -> None:
        """
        Salva uma análise no cache.
        
        Args:
            edital: Texto do edital
            matricula: Texto da matrícula
            analysis: Resultado da análise
        """
        cache = self._load_cache()
        key = self._generate_key(edital, matricula)
        
        cache[key] = {
            'data': analysis,
            'timestamp': datetime.now().isoformat()
        }
        
        self._save_cache(cache)
        logger.info(f"Análise salva no cache: {key}")
        metrics_collector.record_cache_operation(True, len(cache))
    
    def clear_expired_cache(self):
        """Remove entradas expiradas do cache."""
        # Limpa cache de análises
        cache = self._load_cache()
        now = datetime.now()
        expired_keys = []
        
        for key, data in cache.items():
            cache_time = datetime.fromisoformat(data['timestamp'])
            if now - cache_time > self.cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del cache[key]
        
        if expired_keys:
            self._save_cache(cache)
            logger.info(f"Removidas {len(expired_keys)} entradas expiradas do cache de análises")
            
        # Limpa cache de imagens
        images_cache = self._load_images_cache()
        expired_keys = []
        
        for key, data in images_cache.items():
            cache_time = datetime.fromisoformat(data['timestamp'])
            ttl = timedelta(seconds=data.get('ttl', self.cache_ttl))
            if now - cache_time > ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del images_cache[key]
        
        if expired_keys:
            self._save_images_cache(images_cache)
            logger.info(f"Removidas {len(expired_keys)} entradas expiradas do cache de imagens") 