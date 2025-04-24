import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração do MongoDB
MONGO_URI = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('MONGODB_DATABASE', 'leilao_insights')
COLLECTION_NAME = os.getenv('MONGODB_COLLECTION', 'images')

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

def check_images():
    try:
        # Conecta ao MongoDB
        db = connect_to_mongo()
        collection = db[COLLECTION_NAME]
        
        # Pega um documento como exemplo
        sample_doc = collection.find_one()
        
        if not sample_doc:
            print("Nenhum documento encontrado na coleção")
            return
        
        print("\nEstrutura do documento:")
        print("-" * 50)
        
        # Verifica se contém dados binários
        if 'data' in sample_doc and isinstance(sample_doc['data'], bytes):
            print(f"Contém dados binários de imagem: {len(sample_doc['data'])} bytes")
        
        # Verifica outros campos importantes
        print("\nCampos disponíveis:")
        for key, value in sample_doc.items():
            if key != 'data':  # Não mostra o conteúdo binário
                print(f"{key}: {type(value)}")
        
        # Conta total de documentos
        total_docs = collection.count_documents({})
        print(f"\nTotal de documentos na coleção: {total_docs}")
        
        # Verifica documentos com dados binários
        docs_with_binary = collection.count_documents({'data': {'$type': 'binData'}})
        print(f"Documentos com dados binários: {docs_with_binary}")
        
    except Exception as e:
        print(f"Erro durante a verificação: {e}")

if __name__ == "__main__":
    check_images() 