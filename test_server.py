from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from analise_imovel import AnaliseImovel
from monitoring import Monitoring
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('server.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuração simplificada do CORS
CORS(app, 
     resources={r"/api/*": {"origins": "*"}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-Admin-Token"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,X-Admin-Token')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

monitoring = Monitoring()

# Inicialização do analisador
analisador = AnaliseImovel(
    openweather_api_key=os.getenv('OPENWEATHER_API_KEY'),
    google_maps_api_key=os.getenv('GOOGLE_MAPS_API_KEY'),
    legal_api_key=os.getenv('LEGAL_API_KEY'),
    market_api_key=os.getenv('MARKET_API_KEY')
)

# Armazenamento temporário de análises (substituir por banco de dados)
analises = {}

@app.route('/')
def index():
    logger.info("Requisição recebida na rota principal")
    return jsonify({"status": "online", "message": "Servidor de análise de imóveis"})

@app.route('/api/health')
def health_check():
    logger.info("Requisição recebida na rota de saúde")
    return jsonify({"status": "healthy"})

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_property():
    """Endpoint para análise de imóveis"""
    logger.info(f"Requisição recebida: {request.method} {request.path}")
    logger.debug(f"Headers: {dict(request.headers)}")
    
    # Responde ao preflight request
    if request.method == 'OPTIONS':
        logger.info("Respondendo ao preflight request")
        response = jsonify({'status': 'ok'})
        return response
    
    try:
        data = request.get_json()
        logger.info(f"Dados recebidos: {data}")
        
        if not data or 'url' not in data:
            logger.warning("URL não fornecida")
            return jsonify({'erro': 'URL não fornecida'}), 400
            
        # Extrai dados preliminares
        resultado = analisador.extrair_dados_preliminares(data['url'])
        logger.info(f"Resultado da extração: {resultado}")
        
        if 'erro' in resultado:
            logger.error(f"Erro na extração: {resultado['erro']}")
            return jsonify(resultado), 400
            
        # Gera ID único para a análise
        analise_id = str(uuid.uuid4())
        
        # Armazena a análise
        analises[analise_id] = {
            'id': analise_id,
            'url': data['url'],
            'dados': resultado,
            'status': 'preliminar',
            'data_criacao': datetime.now().isoformat()
        }
        
        logger.info(f"Análise criada com ID: {analise_id}")
        return jsonify({
            'analise_id': analise_id,
            'dados': resultado
        })
        
    except Exception as e:
        logger.error(f"Erro na análise: {str(e)}", exc_info=True)
        monitoring.record_error(e, {
            'error_type': type(e).__name__,
            'error_message': str(e),
            'context': {
                'endpoint': '/api/analyze',
                'duration': 0.0
            }
        })
        return jsonify({'erro': str(e)}), 500

@app.route('/api/analyze/complete', methods=['POST'])
def complete_analysis():
    """Endpoint para análise completa"""
    try:
        data = request.get_json()
        if not data or 'analise_id' not in data:
            return jsonify({'erro': 'ID da análise não fornecido'}), 400
            
        analise_id = data['analise_id']
        if analise_id not in analises:
            return jsonify({'erro': 'Análise não encontrada'}), 404
            
        # Verifica se o pagamento foi confirmado
        if not data.get('pagamento_confirmado'):
            return jsonify({'erro': 'Pagamento não confirmado'}), 402
            
        # Inicia análise completa
        resultado = analisador.iniciar_analise_completa(analises[analise_id]['url'])
        if 'erro' in resultado:
            return jsonify(resultado), 400
            
        # Atualiza a análise
        analises[analise_id].update({
            'dados': resultado,
            'status': 'completa',
            'data_conclusao': datetime.now().isoformat()
        })
        
        return jsonify({
            'analise_id': analise_id,
            'dados': resultado
        })
        
    except Exception as e:
        logger.error(f"Erro na análise completa: {str(e)}")
        monitoring.record_error(e, {
            'error_type': type(e).__name__,
            'error_message': str(e),
            'context': {
                'endpoint': '/api/analyze/complete',
                'duration': 0.0
            }
        })
        return jsonify({'erro': str(e)}), 500

@app.route('/api/analyze/status/<analise_id>', methods=['GET'])
def get_analysis_status(analise_id):
    """Endpoint para verificar status da análise"""
    try:
        if analise_id not in analises:
            return jsonify({'erro': 'Análise não encontrada'}), 404
            
        return jsonify({
            'analise_id': analise_id,
            'status': analises[analise_id]['status'],
            'data_criacao': analises[analise_id]['data_criacao'],
            'data_conclusao': analises[analise_id].get('data_conclusao')
        })
        
    except Exception as e:
        logger.error(f"Erro ao verificar status: {str(e)}")
        return jsonify({'erro': str(e)}), 500

@app.route('/api/analyze/admin/edit', methods=['POST'])
def admin_edit_analysis():
    """Endpoint para edição administrativa"""
    try:
        # Verifica token de administrador
        if request.headers.get('X-Admin-Token') != os.getenv('ADMIN_TOKEN'):
            return jsonify({'erro': 'Não autorizado'}), 401
            
        data = request.get_json()
        if not data or 'analise_id' not in data:
            return jsonify({'erro': 'ID da análise não fornecido'}), 400
            
        analise_id = data['analise_id']
        if analise_id not in analises:
            return jsonify({'erro': 'Análise não encontrada'}), 404
            
        # Edita a análise
        resultado = analisador.editar_analise(analise_id, data)
        if 'erro' in resultado:
            return jsonify(resultado), 400
            
        # Atualiza a análise
        analises[analise_id].update({
            'dados': resultado,
            'status': 'editado',
            'data_edicao': datetime.now().isoformat()
        })
        
        return jsonify({
            'analise_id': analise_id,
            'dados': resultado
        })
        
    except Exception as e:
        logger.error(f"Erro na edição administrativa: {str(e)}")
        return jsonify({'erro': str(e)}), 500

@app.route('/api/metrics')
def get_metrics():
    """Retorna as métricas do servidor"""
    return jsonify(monitoring.get_metrics())

@app.route('/api/test', methods=['GET'])
def test_connection():
    """Endpoint para teste de conectividade"""
    try:
        logger.info("Teste de conectividade solicitado")
        return jsonify({
            'status': 'success',
            'message': 'Conexão estabelecida com sucesso',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Erro no teste de conectividade: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    # Verifica se todas as chaves de API estão configuradas
    required_env_vars = [
        'OPENWEATHER_API_KEY',
        'GOOGLE_MAPS_API_KEY',
        'LEGAL_API_KEY',
        'MARKET_API_KEY',
        'ADMIN_TOKEN'
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Variáveis de ambiente ausentes: {', '.join(missing_vars)}")
        exit(1)
        
    port = int(os.getenv('PORT', 5002))
    logger.info(f"Iniciando servidor na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=True) 