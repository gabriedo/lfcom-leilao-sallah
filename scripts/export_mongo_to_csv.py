import os
import csv
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import base64

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração do MongoDB
MONGO_URI = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('MONGODB_DATABASE', 'leilao_insights')
COLLECTION_NAME = os.getenv('MONGODB_COLLECTION', 'images')

def connect_to_mongo():
    """Estabelece conexão com o MongoDB"""
    try:
        print(f"Tentando conectar ao MongoDB em: {MONGO_URI}")
        print(f"Banco de dados: {DB_NAME}")
        print(f"Coleção: {COLLECTION_NAME}")
        
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Verifica se a conexão foi estabelecida
        collection.count_documents({})
        print("Conexão com MongoDB estabelecida com sucesso!")
        return collection
    except Exception as e:
        print(f"Erro ao conectar ao MongoDB: {e}")
        raise

def get_all_documents(collection):
    """Recupera todos os documentos da coleção"""
    try:
        count = collection.count_documents({})
        print(f"Total de documentos encontrados: {count}")
        
        if count == 0:
            print("Nenhum documento encontrado na coleção")
            return []
            
        documents = list(collection.find())
        print(f"Documentos recuperados com sucesso: {len(documents)}")
        return documents
    except Exception as e:
        print(f"Erro ao recuperar documentos: {e}")
        raise

def process_value(value):
    """Processa um valor para garantir que seja serializável para CSV"""
    if isinstance(value, bytes):
        return f"<binary_data_{len(value)}_bytes>"
    elif isinstance(value, (dict, list)):
        return str(value)
    return value

def flatten_document(doc):
    """Achata o documento para formato CSV"""
    flattened = {}
    
    # Processa campos do nível superior
    for key, value in doc.items():
        if key != '_id':  # Exclui o campo _id do MongoDB
            if isinstance(value, dict):
                # Se for um dicionário, achata seus campos
                for sub_key, sub_value in value.items():
                    flattened[f"{key}_{sub_key}"] = process_value(sub_value)
            else:
                flattened[key] = process_value(value)
    
    return flattened

def export_to_csv(documents, output_file):
    """Exporta os documentos para CSV"""
    if not documents:
        print("Nenhum documento encontrado para exportar")
        return
    
    # Obtém todos os campos possíveis
    all_fields = set()
    processed_docs = []
    
    print("Processando documentos...")
    for doc in documents:
        try:
            flattened = flatten_document(doc)
            all_fields.update(flattened.keys())
            processed_docs.append(flattened)
        except Exception as e:
            print(f"Erro ao processar documento: {e}")
            continue
    
    # Ordena os campos para consistência
    fieldnames = sorted(list(all_fields))
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for doc in processed_docs:
                writer.writerow(doc)
        
        print(f"Exportação concluída! Arquivo salvo em: {output_file}")
        print(f"Total de documentos exportados: {len(processed_docs)}")
    except Exception as e:
        print(f"Erro ao exportar para CSV: {e}")
        raise

def main():
    # Gera nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"imoveis_export_{timestamp}.csv"
    
    try:
        # Conecta ao MongoDB
        collection = connect_to_mongo()
        
        # Recupera todos os documentos
        documents = get_all_documents(collection)
        
        # Exporta para CSV
        export_to_csv(documents, output_file)
        
    except Exception as e:
        print(f"Erro durante a exportação: {e}")

if __name__ == "__main__":
    main() 