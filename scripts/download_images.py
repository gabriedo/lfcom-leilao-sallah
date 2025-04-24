import asyncio
import logging
from src.services.image_downloader import ImageDownloader
from src.integrations.caixa_api import CaixaImoveisAPI
import sys

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('download_images.log')
    ]
)
logger = logging.getLogger(__name__)

async def download_all_images():
    logger.info("Iniciando download de imagens...")
    caixa_api = CaixaImoveisAPI()
    page = 1
    total_processed = 0
    
    try:
        async with ImageDownloader() as downloader:
            while True:
                try:
                    logger.info(f"Buscando imóveis da página {page}...")
                    # Busca imóveis da API
                    data = caixa_api.get_imoveis(page)
                    logger.info(f"Dados recebidos da API: {data.keys() if data else 'Nenhum dado'}")
                    
                    if not data or not data.get('results'):
                        logger.warning(f"Nenhum resultado encontrado na página {page}")
                        break
                    
                    items = data.get('results', [])
                    logger.info(f"Encontrados {len(items)} imóveis na página {page}")
                    
                    # Processa imagens dos imóveis
                    results = await downloader.process_properties_images(items)
                    total_processed += len(results)
                    
                    logger.info(f"Página {page} processada. Total de imóveis processados: {total_processed}")
                    logger.info(f"Resultados da página {page}: {results}")
                    
                    # Verifica se há mais páginas
                    next_page = data.get('next')
                    if not next_page:
                        logger.info("Não há mais páginas para processar")
                        break
                    
                    page += 1
                    
                except Exception as e:
                    logger.error(f"Erro ao processar página {page}: {e}", exc_info=True)
                    break
    except Exception as e:
        logger.error(f"Erro fatal no processamento: {e}", exc_info=True)
    
    logger.info(f"Download concluído. Total de imóveis processados: {total_processed}")

if __name__ == "__main__":
    logger.info("Iniciando script de download...")
    asyncio.run(download_all_images()) 