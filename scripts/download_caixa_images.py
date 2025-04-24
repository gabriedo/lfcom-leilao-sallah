import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração do MongoDB
MONGO_URI = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('MONGODB_DATABASE', 'leilao_insights')
COLLECTION_NAME = os.getenv('MONGODB_COLLECTION', 'images')
IMAGES_COLLECTION = 'downloaded_images'  # Nova coleção para imagens baixadas

def connect_to_mongo():
    """Estabelece conexão com o MongoDB"""
    try:
        print(f"Conectando ao MongoDB em: {MONGO_URI}")
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        return db
    except Exception as e:
        print(f"Erro ao conectar ao MongoDB: {e}")
        raise

def download_image(url):
    """Baixa uma imagem da URL fornecida"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Erro ao baixar imagem de {url}: {e}")
        return None

def process_image(db, image_data):
    """Processa uma imagem individual"""
    try:
        url = image_data.get('url')
        property_id = image_data.get('property_id')
        
        if not url or not property_id:
            return False

        # Verifica se a imagem já foi baixada
        if db[IMAGES_COLLECTION].find_one({'property_id': property_id, 'original_url': url}):
            return False

        # Baixa a imagem
        image_content = download_image(url)
        if not image_content:
            return False

        # Salva a imagem no MongoDB
        image_doc = {
            'property_id': property_id,
            'original_url': url,
            'image_data': image_content,
            'downloaded_at': time.time()
        }
        db[IMAGES_COLLECTION].insert_one(image_doc)
        return True

    except Exception as e:
        print(f"Erro ao processar imagem: {e}")
        return False

def main():
    try:
        # Conecta ao MongoDB
        db = connect_to_mongo()
        
        # Recupera todos os documentos com URLs de imagens
        images_collection = db[COLLECTION_NAME]
        image_docs = list(images_collection.find({}, {'url': 1, 'property_id': 1}))
        
        print(f"Total de imagens encontradas: {len(image_docs)}")
        
        # Configura a barra de progresso
        with tqdm(total=len(image_docs), desc="Baixando imagens") as pbar:
            # Usa ThreadPoolExecutor para download paralelo
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                for doc in image_docs:
                    future = executor.submit(process_image, db, doc)
                    futures.append(future)
                
                # Processa os resultados
                success_count = 0
                for future in as_completed(futures):
                    if future.result():
                        success_count += 1
                    pbar.update(1)
        
        print(f"\nDownload concluído!")
        print(f"Total de imagens baixadas com sucesso: {success_count}")
        print(f"Total de imagens que falharam: {len(image_docs) - success_count}")

    except Exception as e:
        print(f"Erro durante o processo: {e}")

if __name__ == "__main__":
    main() 