import requests
import json
from typing import Dict, Any, List
import pandas as pd
from collections import Counter
import logging
from datetime import datetime
import os
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraphub_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

class ScraphubAnalyzer:
    def __init__(self):
        self.base_url = "https://scraphub.comercify.shop/api"
        self.api_key = os.getenv("SCRAPHUB_API_KEY")
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Configurar sessão com retry
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        self.session.headers.update(self.headers)

    def test_connection(self) -> bool:
        """Testa a conexão com a API"""
        try:
            url = f"{self.base_url}/items/2/?page=1"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Conexão bem-sucedida. Status: {response.status_code}")
            logger.info(f"Headers da resposta: {dict(response.headers)}")
            
            # Tentar analisar a resposta
            try:
                data = response.json()
                logger.info(f"Estrutura da resposta: {type(data)}")
                if isinstance(data, list):
                    logger.info(f"Primeiro item: {data[0] if data else 'Lista vazia'}")
                else:
                    logger.info(f"Resposta completa: {data}")
            except json.JSONDecodeError:
                logger.error("Resposta não é um JSON válido")
                logger.info(f"Conteúdo da resposta: {response.text[:500]}...")
                
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar com a API: {str(e)}")
            return False

    def get_all_items(self, max_pages: int = 10) -> List[Dict[str, Any]]:
        """Busca todos os itens disponíveis até o limite de páginas"""
        all_items = []
        page = 1
        
        while page <= max_pages:
            try:
                url = f"{self.base_url}/items/2/?page={page}"
                logger.info(f"Buscando página {page}...")
                
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Resposta recebida: {type(data)}")
                
                if not data:
                    logger.info("Resposta vazia")
                    break
                    
                if isinstance(data, dict):
                    logger.info(f"Resposta é um dicionário: {data.keys()}")
                    if 'items' in data:
                        data = data['items']
                    elif 'results' in data:
                        data = data['results']
                    else:
                        logger.error(f"Estrutura inesperada: {data}")
                        break
                
                if not isinstance(data, list):
                    logger.error(f"Tipo de dados inesperado: {type(data)}")
                    break
                    
                all_items.extend(data)
                logger.info(f"Página {page} processada. Total de itens: {len(all_items)}")
                
                if len(data) < 10:
                    logger.info("Página com menos de 10 itens, provavelmente última página")
                    break
                    
                page += 1
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro na requisição: {str(e)}")
                break
            except Exception as e:
                logger.error(f"Erro inesperado: {str(e)}")
                break
                
        return all_items

    def analyze_data_structure(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa a estrutura dos dados"""
        if not items:
            logger.warning("Nenhum item para analisar")
            return {}
            
        # Pega o primeiro item como exemplo
        sample_item = items[0]
        logger.info(f"Exemplo de item: {json.dumps(sample_item, indent=2)}")
        
        # Conta campos presentes em todos os itens
        field_counts = Counter()
        for item in items:
            field_counts.update(item.keys())
            
        # Analisa tipos de dados
        type_counts = {}
        for field in field_counts:
            types = Counter(type(item.get(field)).__name__ for item in items if field in item)
            type_counts[field] = dict(types)
            
        return {
            "total_items": len(items),
            "fields_present": dict(field_counts),
            "data_types": type_counts,
            "sample_item": sample_item
        }

    def analyze_field_values(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analisa os valores dos campos"""
        if not items:
            return {}
            
        analysis = {}
        
        for field in items[0].keys():
            values = [item.get(field) for item in items if field in item]
            
            # Análise básica
            analysis[field] = {
                "total_values": len(values),
                "unique_values": len(set(values)),
                "null_values": values.count(None),
                "sample_values": list(set(values))[:5]  # Primeiros 5 valores únicos
            }
            
            # Análise específica para campos numéricos
            if all(isinstance(v, (int, float)) for v in values if v is not None):
                numeric_values = [v for v in values if v is not None]
                if numeric_values:
                    analysis[field].update({
                        "min": min(numeric_values),
                        "max": max(numeric_values),
                        "mean": sum(numeric_values) / len(numeric_values)
                    })
                    
        return analysis

    def generate_report(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gera um relatório completo da análise"""
        return {
            "timestamp": datetime.now().isoformat(),
            "data_structure": self.analyze_data_structure(items),
            "field_analysis": self.analyze_field_values(items),
            "summary": {
                "total_items": len(items),
                "total_fields": len(items[0]) if items else 0,
                "fields": list(items[0].keys()) if items else []
            }
        }

def main():
    analyzer = ScraphubAnalyzer()
    
    # Testar conexão
    logger.info("Testando conexão com a API...")
    if not analyzer.test_connection():
        logger.error("Falha na conexão com a API. Verifique as configurações.")
        return
    
    # Buscar todos os itens
    logger.info("Iniciando coleta de dados...")
    items = analyzer.get_all_items()
    
    if not items:
        logger.error("Nenhum item encontrado. Verifique a API e as credenciais.")
        return
    
    # Gerar análise
    logger.info("Gerando análise...")
    report = analyzer.generate_report(items)
    
    # Salvar relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"scraphub_analysis_{timestamp}.json"
    
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Relatório salvo em {report_file}")
    
    # Imprimir resumo
    print("\nResumo da Análise:")
    print(f"Total de itens analisados: {report['summary']['total_items']}")
    print(f"Total de campos por item: {report['summary']['total_fields']}")
    print("\nCampos encontrados:")
    for field in report['summary']['fields']:
        print(f"- {field}")
    
    # Salvar também em CSV para análise
    if items:
        df = pd.DataFrame(items)
        csv_file = f"scraphub_data_{timestamp}.csv"
        df.to_csv(csv_file, index=False)
        logger.info(f"Dados salvos em CSV: {csv_file}")

if __name__ == "__main__":
    main() 