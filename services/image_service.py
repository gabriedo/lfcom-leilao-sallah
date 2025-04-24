import os
import requests
import logging
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from models.image import PropertyImage

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações
IMAGES_DIR = Path("data/images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

class ImageService:
    def __init__(self, mongo_url: str):
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client.property_images
        self.collection = self.db.images

    async def download_and_save_image(self, image_url: str, property_id: str, image_index: int) -> Optional[str]:
        """Baixa uma imagem e salva no MongoDB."""
        try:
            # Baixa a imagem
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Cria diretório para o imóvel se não existir
            property_dir = IMAGES_DIR / property_id
            property_dir.mkdir(exist_ok=True)
            
            # Define o nome do arquivo
            extension = image_url.split(".")[-1].lower()
            if extension not in ["jpg", "jpeg", "png"]:
                extension = "jpg"
            
            filename = f"{image_index}.{extension}"
            filepath = property_dir / filename
            
            # Salva a imagem localmente
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            # Cria o documento no MongoDB
            image_doc = PropertyImage(
                property_id=property_id,
                image_url=image_url,
                local_path=str(filepath.relative_to(IMAGES_DIR))
            )
            
            # Insere no MongoDB
            result = await self.collection.insert_one(image_doc.dict(by_alias=True))
            
            logger.info(f"Imagem {image_index} do imóvel {property_id} salva com sucesso")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Erro ao baixar e salvar imagem {image_url}: {str(e)}")
            return None

    async def get_property_images(self, property_id: str) -> List[PropertyImage]:
        """Retorna todas as imagens de um imóvel."""
        cursor = self.collection.find({"property_id": property_id})
        images = []
        async for doc in cursor:
            images.append(PropertyImage(**doc))
        return images

    async def get_image_by_id(self, image_id: str) -> Optional[PropertyImage]:
        """Retorna uma imagem pelo ID."""
        doc = await self.collection.find_one({"_id": ObjectId(image_id)})
        if doc:
            return PropertyImage(**doc)
        return None

    async def delete_property_images(self, property_id: str) -> bool:
        """Remove todas as imagens de um imóvel."""
        try:
            # Remove do MongoDB
            result = await self.collection.delete_many({"property_id": property_id})
            
            # Remove os arquivos locais
            property_dir = IMAGES_DIR / property_id
            if property_dir.exists():
                for file in property_dir.iterdir():
                    file.unlink()
                property_dir.rmdir()
            
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Erro ao remover imagens do imóvel {property_id}: {str(e)}")
            return False

    async def update_image(self, image_id: str, image_url: str) -> Optional[PropertyImage]:
        """Atualiza uma imagem existente."""
        try:
            image = await self.get_image_by_id(image_id)
            if not image:
                return None
            
            # Baixa a nova imagem
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Atualiza o arquivo local
            filepath = IMAGES_DIR / image.local_path
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            # Atualiza no MongoDB
            update_data = {
                "image_url": image_url,
                "updated_at": datetime.utcnow()
            }
            
            await self.collection.update_one(
                {"_id": ObjectId(image_id)},
                {"$set": update_data}
            )
            
            return await self.get_image_by_id(image_id)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar imagem {image_id}: {str(e)}")
            return None 