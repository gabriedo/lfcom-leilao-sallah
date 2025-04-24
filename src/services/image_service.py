import os
from typing import List, Optional
import motor.motor_asyncio
from bson import ObjectId
from dotenv import load_dotenv
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class ImageService:
    def __init__(self, mongodb_url: Optional[str] = None):
        self.mongodb_url = mongodb_url or os.getenv("MONGODB_URL")
        self.database = os.getenv("MONGODB_DATABASE", "leilao_insights")
        self.collection = os.getenv("MONGODB_COLLECTION", "images")
        
        if not self.mongodb_url:
            raise ValueError("MONGODB_URL não configurada")
            
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongodb_url)
        self.db = self.client[self.database]
        self.images = self.db[self.collection]
        
    async def save_image(self, property_id: str, image_url: str, image_data: bytes) -> str:
        """Salva uma imagem no MongoDB e retorna o ID do documento"""
        try:
            result = await self.images.insert_one({
                "property_id": property_id,
                "url": image_url,
                "data": image_data
            })
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Erro ao salvar imagem: {e}")
            raise
            
    async def get_image(self, image_id: str) -> Optional[bytes]:
        """Retorna os dados de uma imagem pelo ID"""
        try:
            image = await self.images.find_one({"_id": ObjectId(image_id)})
            return image["data"] if image else None
        except Exception as e:
            logger.error(f"Erro ao buscar imagem: {e}")
            return None
            
    async def delete_images(self, property_id: str) -> None:
        """Deleta todas as imagens de um imóvel"""
        try:
            await self.images.delete_many({"property_id": property_id})
        except Exception as e:
            logger.error(f"Erro ao deletar imagens: {e}")
            raise
            
    async def get_property_images(self, property_id: str) -> List[dict]:
        """Retorna todas as imagens de um imóvel"""
        try:
            cursor = self.images.find({"property_id": property_id})
            images = []
            async for image in cursor:
                images.append({
                    "id": str(image["_id"]),
                    "url": image["url"]
                })
            return images
        except Exception as e:
            logger.error(f"Erro ao buscar imagens do imóvel: {e}")
            return [] 