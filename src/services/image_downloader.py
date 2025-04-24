import aiohttp
import asyncio
from typing import List, Dict
import logging
from src.services.image_service import ImageService
import os
from dotenv import load_dotenv

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class ImageDownloader:
    def __init__(self):
        self.image_service = ImageService()
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def download_and_save_image(self, property_id: str, image_url: str) -> str:
        """Baixa uma imagem e salva no MongoDB"""
        try:
            logger.info(f"Tentando baixar imagem: {image_url}")
            async with self.session.get(image_url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    image_id = await self.image_service.save_image(property_id, image_url, image_data)
                    logger.info(f"Imagem salva com sucesso: {image_id}")
                    return image_id
                else:
                    logger.error(f"Erro ao baixar imagem: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Erro ao processar imagem: {e}")
            return None
            
    async def process_property_images(self, property_id: str, image_urls: List[str]) -> List[str]:
        """Processa todas as imagens de um imóvel"""
        saved_image_ids = []
        logger.info(f"Processando imagens do imóvel {property_id}: {image_urls}")
        for url in image_urls:
            image_id = await self.download_and_save_image(property_id, url)
            if image_id:
                saved_image_ids.append(image_id)
        return saved_image_ids
        
    async def process_properties_images(self, properties: List[Dict]) -> Dict[str, List[str]]:
        """Processa imagens de múltiplos imóveis"""
        results = {}
        for property_data in properties:
            logger.info(f"Processando imóvel: {property_data.keys()}")
            property_id = str(property_data.get('id'))
            images = property_data.get('data', {}).get('images', [])
            logger.info(f"Imagens encontradas: {images}")
            if images:
                saved_ids = await self.process_property_images(property_id, images)
                results[property_id] = saved_ids
        return results 