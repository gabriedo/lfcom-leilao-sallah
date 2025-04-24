from fastapi import FastAPI, HTTPException, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
import requests
import json
from urllib.parse import quote_plus, urlparse
import random
import re
import base64
import os
import hashlib
from pathlib import Path
from dotenv import load_dotenv
import time
import logging
from functools import lru_cache
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from src.services.image_service import ImageService
from services.scraphub_service import ScraphubService
import io
from pymongo import MongoClient

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do MongoDB
MONGO_URI = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGODB_DATABASE", "leilao_insights")
COLLECTION_NAME = "images"

# Configuração do cache
CACHE_DURATION = timedelta(hours=1)
cache: Dict[str, tuple] = {}

# Cache específico para URLs de imagem
image_url_cache: Dict[str, Tuple[str, datetime]] = {}
IMAGE_CACHE_DURATION = timedelta(hours=24)

# Configuração do retry
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

app = FastAPI(
    title="LFCOM API",
    description="API para análise e geração de relatórios de imóveis em leilão",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8083", "http://localhost:5000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Adicionar headers CORS manualmente
@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:8083"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# Lista de imagens alternativas do Unsplash para casos de URLs inválidas
FALLBACK_IMAGES = [
    "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800&q=80",
    "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800&q=80",
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&q=80",
    "https://images.unsplash.com/photo-1600566753151-384129cf4e3e?w=800&q=80",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80"
]

# Dicionário para mapear tipos de propriedades com imagens relevantes
PROPERTY_TYPE_IMAGES = {
    "Apartamento": [
        "https://images.unsplash.com/photo-1574362848149-11496d93a7c7?w=800&q=80",
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&q=80",
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&q=80",
    ],
    "Casa": [
        "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800&q=80",
        "https://images.unsplash.com/photo-1576941089067-2de3c901e126?w=800&q=80",
        "https://images.unsplash.com/photo-1575517111839-3a3843ee7f5d?w=800&q=80",
    ]
}

class PropertyAnalysisRequest(BaseModel):
    url: Optional[str] = None
    edital_texto: Optional[str] = None
    matricula_texto: Optional[str] = None
    valor_mercado: float
    valor_minimo_leilao: float

# Inicialização do serviço de imagens
image_service = ImageService()

@app.get("/")
async def root():
    return {"message": "LFCOM API"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/items/")
async def get_items():
    try:
        # Dados de exemplo
        properties = [
            {
                "id": "1",
                "data": {
                    "id": "1",
                    "title": "Apartamento 3 quartos - Centro",
                    "address": "Rua Exemplo, 123",
                    "city": "São Paulo",
                    "state": "SP",
                    "type": "Apartamento",
                    "sale_value": "500000",
                    "preco_avaliacao": "600000",
                    "desconto": "16.67",
                    "total_area": "120",
                    "private_area": "90",
                    "quartos": "3",
                    "banheiros": "2",
                    "garagem": "2",
                    "images": [
                        "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800&q=80",
                        "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800&q=80"
                    ],
                    "modality": "Leilão SFI",
                    "fim_1": "2024-05-01",
                    "fim_2": "2024-05-15",
                    "fim_venda_online": None,
                    "aceita_financiamento": "Sim",
                    "aceita_FGTS": "Sim",
                    "aceita_parcelamento": "Sim",
                    "aceita_consorcio": "Não",
                    "description": "Excelente apartamento no centro da cidade...",
                    "ps": ["Imóvel ocupado", "Necessita reforma"]
                }
            },
            {
                "id": "2",
                "data": {
                    "id": "2",
                    "title": "Casa 4 quartos - Jardins",
                    "address": "Av. Exemplo, 456",
                    "city": "São Paulo",
                    "state": "SP",
                    "type": "Casa",
                    "sale_value": "1200000",
                    "preco_avaliacao": "1500000",
                    "desconto": "20.00",
                    "total_area": "300",
                    "private_area": "250",
                    "quartos": "4",
                    "banheiros": "3",
                    "garagem": "3",
                    "images": [
                        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&q=80",
                        "https://images.unsplash.com/photo-1600566753151-384129cf4e3e?w=800&q=80"
                    ],
                    "modality": "Venda Online",
                    "fim_1": None,
                    "fim_2": None,
                    "fim_venda_online": "2024-04-30",
                    "aceita_financiamento": "Sim",
                    "aceita_FGTS": "Sim",
                    "aceita_parcelamento": "Sim",
                    "aceita_consorcio": "Sim",
                    "description": "Casa espaçosa em excelente localização...",
                    "ps": ["Imóvel desocupado", "Em bom estado de conservação"]
                }
            }
        ]
        
        return {
            "status": "success",
            "results": properties
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analisar_imovel/")
async def analyze_property_endpoint(request: PropertyAnalysisRequest):
    try:
        # Por enquanto, apenas retorna os dados recebidos
        return {
            "status": "success",
            "dados_recebidos": request.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def is_valid_image_url(url: str) -> bool:
    """Verifica se uma URL é uma imagem válida."""
    try:
        response = http.head(url, timeout=5.0)
        content_type = response.headers.get('content-type', '')
        content_length = int(response.headers.get('content-length', 0))
        
        # Verifica se é uma imagem e tem tamanho razoável (entre 1KB e 10MB)
        return (
            response.status_code == 200 and
            'image' in content_type and
            1024 <= content_length <= 10_485_760
        )
    except:
        return False

def get_cached_image_url(url: str) -> Optional[str]:
    """Retorna URL do cache se ainda válida."""
    if url in image_url_cache:
        cached_url, timestamp = image_url_cache[url]
        if datetime.now() - timestamp < IMAGE_CACHE_DURATION:
            return cached_url
        del image_url_cache[url]
    return None

def process_image_urls(image_urls):
    """
    Processa as URLs de imagem, usando o serviço images.weserv.nl para imagens da Caixa
    e mantendo as URLs originais para outras fontes.
    """
    if not image_urls or not isinstance(image_urls, list):
        logger.warning("Lista de imagens vazia ou inválida")
        return [FALLBACK_IMAGES[0]]
    
    processed_urls = []
    
    for img_url in image_urls:
        if not img_url or not isinstance(img_url, str):
            logger.warning(f"URL de imagem inválida: {img_url}")
            continue
            
        # Limpar a URL
        img_url = img_url.strip().replace("\n", "").replace("\t", "").replace("\r", "")
        
        # Verificar cache primeiro
        cached_url = get_cached_image_url(img_url)
        if cached_url:
            logger.info(f"Usando URL em cache: {cached_url}")
            processed_urls.append(cached_url)
            continue
        
        # Se já for uma URL do Unsplash, usa diretamente
        if "unsplash.com" in img_url:
            logger.info(f"Usando URL do Unsplash: {img_url}")
            image_url_cache[img_url] = (img_url, datetime.now())
            processed_urls.append(img_url)
            continue
            
        # Para URLs da Caixa, usar o serviço images.weserv.nl
        if "venda-imoveis.caixa.gov.br" in img_url:
            try:
                # Verificar se a URL é válida antes de processar
                if is_valid_image_url(img_url):
                    proxy_url = f"https://images.weserv.nl/?url={quote_plus(img_url)}&output=jpg&maxage=7d"
                    logger.info(f"Processando URL da Caixa: {img_url} -> {proxy_url}")
                    image_url_cache[img_url] = (proxy_url, datetime.now())
                    processed_urls.append(proxy_url)
                else:
                    logger.warning(f"URL da Caixa inválida: {img_url}")
                    processed_urls.append(FALLBACK_IMAGES[0])
            except Exception as e:
                logger.error(f"Erro ao processar URL da Caixa: {str(e)}")
                processed_urls.append(FALLBACK_IMAGES[0])
            continue
            
        # Para qualquer outra URL válida
        if img_url.startswith("http"):
            try:
                if is_valid_image_url(img_url):
                    logger.info(f"Usando URL externa válida: {img_url}")
                    image_url_cache[img_url] = (img_url, datetime.now())
                    processed_urls.append(img_url)
                else:
                    logger.warning(f"URL externa inválida: {img_url}")
            except Exception as e:
                logger.error(f"Erro ao validar URL externa: {str(e)}")
    
    # Se não conseguiu processar nenhuma URL, usa fallback
    if not processed_urls:
        logger.warning("Nenhuma URL válida encontrada, usando fallback")
        return [FALLBACK_IMAGES[0]]
        
    logger.info(f"Processadas {len(processed_urls)} URLs de imagem")
    return processed_urls

def process_property_data(property_data):
    """Processa um imóvel, garantindo que todos os dados estejam corretos e as imagens sejam exibidas."""
    if not property_data or not isinstance(property_data, dict) or "data" not in property_data:
        return property_data
        
    # Garantir que property_data.data seja um dicionário
    if not isinstance(property_data["data"], dict):
        property_data["data"] = {}
    
    # Processar imagens
    if "images" in property_data["data"]:
        # Guardar as imagens originais
        original_images = property_data["data"]["images"]
        
        # Processar as URLs das imagens
        property_data["data"]["images"] = process_image_urls(original_images)
        
        # Log para debug
        print(f"Imóvel {property_data.get('id')}: {len(property_data['data']['images'])} imagens processadas")
        
    # Tratar campos numéricos
    numeric_fields = ["total_area", "private_area", "quartos", "banheiros", "garagem", 
                      "sale_value", "preco_avaliacao", "desconto"]
    
    for field in numeric_fields:
        if field in property_data["data"]:
            value = property_data["data"][field]
            
            if value is None:
                property_data["data"][field] = "0"
            elif not isinstance(value, str):
                property_data["data"][field] = str(value)
            elif value.upper() == "N/A" or value.strip() == "-":
                property_data["data"][field] = "0"
    
    # Garantir que campos obrigatórios existam
    default_fields = {
        "title": "Imóvel sem título",
        "address": "Endereço não informado",
        "city": "Cidade não informada",
        "state": "SP",
        "type": "Imóvel",
        "sale_value": "0",
        "preco_avaliacao": "0",
        "desconto": "0",
        "total_area": "0",
        "private_area": "0",
        "quartos": "0",
        "banheiros": "0",
        "garagem": "0",
        "modality": "Sem modalidade",
        "description": "Sem descrição disponível",
        "ps": []
    }
    
    for field, default_value in default_fields.items():
        if field not in property_data["data"] or property_data["data"][field] is None:
            property_data["data"][field] = default_value
    
    # Limpar o título
    if "title" in property_data["data"]:
        title = property_data["data"]["title"].replace("\n", " ").replace("\t", " ").strip()
        # Remover espaços múltiplos
        while "  " in title:
            title = title.replace("  ", " ")
        property_data["data"]["title"] = title
    
    return property_data

def get_cached_data(cache_key: str, max_age: timedelta = CACHE_DURATION) -> Optional[dict]:
    """Retorna dados do cache se ainda forem válidos."""
    if cache_key in cache:
        data, timestamp = cache[cache_key]
        if datetime.now() - timestamp < max_age:
            logger.info(f"Cache hit para {cache_key}")
            return data
        else:
            logger.info(f"Cache expirado para {cache_key}")
            del cache[cache_key]
    return None

def set_cached_data(cache_key: str, data: dict):
    """Armazena dados no cache."""
    cache[cache_key] = (data, datetime.now())
    logger.info(f"Dados armazenados em cache para {cache_key}")

@app.get("/api/properties")
async def get_properties(
    page: int = 1,
    per_page: int = 50,
    city: Optional[str] = None,
    state: Optional[str] = None,
    type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    try:
        # Gerar chave de cache
        cache_key = f"properties_{page}_{per_page}_{city}_{state}_{type}_{min_price}_{max_price}"
        
        # Tentar obter dados do cache
        cached_data = get_cached_data(cache_key)
        if cached_data:
            logger.info("Retornando dados do cache")
            return cached_data
            
        logger.info("Iniciando requisição para a API externa...")
        start_time = time.time()
        
        # Por enquanto, retornar dados de exemplo
        properties = [
            {
                "id": "1",
                "data": {
                    "id": "1",
                    "title": "Apartamento 3 quartos - Centro",
                    "address": "Rua Exemplo, 123",
                    "city": "São Paulo",
                    "state": "SP",
                    "type": "Apartamento",
                    "sale_value": "500000",
                    "preco_avaliacao": "600000",
                    "desconto": "16.67",
                    "total_area": "120",
                    "private_area": "90",
                    "quartos": "3",
                    "banheiros": "2",
                    "garagem": "2",
                    "images": [
                        "https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800&q=80",
                        "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800&q=80"
                    ],
                    "modality": "Leilão SFI",
                    "fim_1": "2024-05-01",
                    "fim_2": "2024-05-15",
                    "fim_venda_online": None,
                    "aceita_financiamento": "Sim",
                    "aceita_FGTS": "Sim",
                    "aceita_parcelamento": "Sim",
                    "aceita_consorcio": "Não",
                    "description": "Excelente apartamento no centro da cidade...",
                    "ps": ["Imóvel ocupado", "Necessita reforma"]
                }
            }
        ]
        
        data = {
            "properties": properties,
            "totalPages": 1  # Por enquanto, apenas uma página
        }
        
        # Armazenar no cache
        set_cached_data(cache_key, data)
        
        # Log de performance
        elapsed_time = time.time() - start_time
        logger.info(f"Tempo total de processamento: {elapsed_time:.2f} segundos")
        
        return data
                
    except Exception as e:
        logger.error(f"Erro ao buscar propriedades: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/images/{property_id}/{image_id}")
async def get_image(property_id: str, image_id: str):
    """Endpoint para servir uma imagem pelo ID do imóvel e nome do arquivo"""
    try:
        # Conecta ao MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Busca a imagem no MongoDB
        image = collection.find_one({
            "property_id": property_id,
            "url": {"$regex": f".*{image_id}$"}
        })
        
        if not image or "data" not in image:
            raise HTTPException(status_code=404, detail="Imagem não encontrada")
            
        # Retorna a imagem como resposta
        return Response(
            content=image["data"],
            media_type="image/jpeg"
        )
    except Exception as e:
        logger.error(f"Erro ao buscar imagem: {e}")
        raise HTTPException(status_code=500, detail="Erro ao buscar imagem")

@app.get("/api/properties/{property_id}/images")
async def get_property_images(property_id: str):
    """Endpoint para listar todas as imagens de um imóvel"""
    try:
        images = await image_service.get_property_images(property_id)
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scraphub/items")
async def get_scraphub_items(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
):
    """
    Endpoint para buscar itens do Scraphub com paginação
    
    Args:
        page (int): Número da página (padrão: 1)
        per_page (int): Quantidade de itens por página (padrão: 10, máximo: 100)
        
    Returns:
        Dict[str, Any]: Resposta da API com os itens
    """
    try:
        service = ScraphubService()
        items = service.get_items(page=page, per_page=per_page)
        return items
    except Exception as e:
        logger.error(f"Erro ao buscar itens do Scraphub: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scraphub/items/{item_id}")
async def get_scraphub_item(item_id: str):
    """
    Endpoint para buscar detalhes de um item específico do Scraphub
    
    Args:
        item_id (str): ID do item
        
    Returns:
        Dict[str, Any]: Detalhes do item
    """
    try:
        service = ScraphubService()
        item = service.get_item_details(item_id)
        return item
    except Exception as e:
        logger.error(f"Erro ao buscar detalhes do item {item_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8890, log_level="info") 