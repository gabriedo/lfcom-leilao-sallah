import os
import logging
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

# Configurações de APIs externas
MARKET_API_KEY = os.getenv('MARKET_API_KEY')
LEGAL_API_KEY = os.getenv('LEGAL_API_KEY')

# Configurações do servidor
SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('SERVER_PORT', 5001))

# Configurações de cache
CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))  # 1 hora em segundos

# Configurações de geolocalização
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

# Configurações da API
API_PORT = int(os.getenv("API_PORT", 5000))
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"

# Configurações de diretórios
REPORTS_DIR = "relatorios"
os.makedirs(REPORTS_DIR, exist_ok=True) 