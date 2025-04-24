from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger, swag_from
from analise_imovel import AnaliseImovel
from config import logger, API_PORT, DEBUG_MODE
from cache_manager import CacheManager
from monitoring import metrics_collector
from src.integrations.caixa_api import CaixaImoveisAPI
import time
import traceback
import threading
import schedule
import logging
import os

app = Flask(__name__)

# Configuração do CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:8083", "http://127.0.0.1:8083"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuração do Rate Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Configuração do Swagger
swagger = Swagger(app)

# Headers de segurança
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

cache_manager = CacheManager()

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def collect_system_metrics():
    """Coleta métricas do sistema periodicamente"""
    try:
        metrics_collector.collect_metrics()
    except Exception as e:
        logger.error(f"Erro ao coletar métricas: {str(e)}")

def start_metrics_collection():
    """Inicia a coleta periódica de métricas."""
    schedule.every(5).minutes.do(collect_system_metrics)
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()

# Rota raiz para servir o frontend
@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'index.html')

# Rotas da API
@app.route('/api/health', methods=['GET'])
def health_check():
    """Rota para verificar a saúde da API."""
    return jsonify({"status": "ok", "message": "API está funcionando!"})

@app.route('/api/analyze', methods=['POST'])
def analyze_property():
    """Rota principal para análise de imóveis."""
    start_time = time.time()
    try:
        data = request.get_json()
        
        if not data or 'edital' not in data or 'matricula' not in data:
            logger.error("Dados inválidos recebidos na requisição")
            return jsonify({'error': 'Dados inválidos. É necessário fornecer edital e matricula.'}), 400
            
        analise = AnaliseImovel(edital=data['edital'], matricula=data['matricula'])
        resultado = analise.analisar()
        
        duration = time.time() - start_time
        metrics_collector.record_api_call('/api/analyze', duration)
        
        return jsonify(resultado)
        
    except Exception as e:
        metrics_collector.record_error(e, {'endpoint': '/api/analyze'})
        logger.error(f"Erro ao analisar imóvel: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/url', methods=['POST'])
def analyze_property_by_url():
    """Rota para análise de imóveis por URL."""
    start_time = time.time()
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            logger.error("URL não fornecida na requisição")
            return jsonify({'error': 'URL não fornecida'}), 400
            
        # Inicializa o analisador com a URL
        analise = AnaliseImovel()
        resultado = analise.analisar(url=data['url'])
        
        duration = time.time() - start_time
        metrics_collector.record_api_call('/api/analyze/url', duration)
        
        return jsonify(resultado)
        
    except Exception as e:
        metrics_collector.record_error(e, {'endpoint': '/api/analyze/url'})
        logger.error(f"Erro ao analisar imóvel por URL: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/extract', methods=['GET'])
def extract_data():
    """Rota para extrair dados de uma URL."""
    start_time = time.time()
    try:
        url = request.args.get('url')
        
        if not url:
            logger.error("URL não fornecida na requisição")
            return jsonify({'error': 'URL não fornecida'}), 400
            
        # Inicializa o analisador com a URL
        analise = AnaliseImovel()
        resultado = analise.analisar(url=url)
        
        duration = time.time() - start_time
        metrics_collector.record_api_call('/api/extract', duration)
        
        return jsonify(resultado)
        
    except Exception as e:
        metrics_collector.record_error(e, {'endpoint': '/api/extract'})
        logger.error(f"Erro ao extrair dados da URL: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Rota para obter métricas do sistema."""
    try:
        metrics = metrics_collector.get_metrics()
        return jsonify({
            "status": "success",
            "metrics": metrics,
            "cache_hit_rate": metrics_collector.get_cache_hit_rate(),
            "error_rate": metrics_collector.get_error_rate()
        })
    except Exception as e:
        logger.error(f"Erro ao obter métricas: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cache/maintenance', methods=['POST'])
def cache_maintenance():
    """Rota para manutenção do cache."""
    start_time = time.time()
    try:
        action = request.args.get('action', 'clean')
        
        if action == 'clean':
            cache_manager.clear_expired_cache()
            metrics_collector.record_api_call(True, time.time() - start_time)
            return jsonify({
                "status": "success",
                "message": "Cache limpo com sucesso"
            })
        else:
            metrics_collector.record_api_call(False, time.time() - start_time)
            return jsonify({
                "status": "error",
                "message": "Ação inválida"
            }), 400
            
    except Exception as e:
        logger.error(f"Erro na manutenção do cache: {str(e)}")
        metrics_collector.record_api_call(False, time.time() - start_time)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/imoveis-caixa', methods=['GET'])
@limiter.limit("30 per minute")
@swag_from({
    'tags': ['Imóveis'],
    'parameters': [
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'default': 1,
            'description': 'Número da página'
        }
    ],
    'responses': {
        200: {
            'description': 'Lista de imóveis retornada com sucesso',
            'schema': {
                'type': 'object',
                'properties': {
                    'items': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'integer'},
                                'titulo': {'type': 'string'},
                                'preco': {'type': 'number'},
                                'endereco': {'type': 'string'}
                            }
                        }
                    },
                    'total_pages': {'type': 'integer'},
                    'current_page': {'type': 'integer'}
                }
            }
        },
        500: {
            'description': 'Erro interno do servidor'
        }
    }
})
def get_imoveis_caixa():
    """Rota para buscar imóveis da Caixa."""
    start_time = time.time()
    try:
        # Pega o número da página dos query params, default é 1
        page = request.args.get('page', 1, type=int)
        
        # Busca os dados da API
        caixa_api = CaixaImoveisAPI()
        resultado = caixa_api.get_imoveis(page)
        
        duration = time.time() - start_time
        metrics_collector.record_api_call('/api/imoveis-caixa', duration)
        
        return jsonify(resultado)
        
    except Exception as e:
        metrics_collector.record_error(e, {'endpoint': '/api/imoveis-caixa'})
        logger.error(f"Erro ao buscar imóveis da Caixa: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    try:
        # Inicia o coletor de métricas
        start_metrics_collection()
        
        # Inicia o servidor Flask
        app.run(host='0.0.0.0', port=5002, debug=False)
    except Exception as e:
        logger.error(f"Erro ao iniciar o servidor: {str(e)}")
        raise 