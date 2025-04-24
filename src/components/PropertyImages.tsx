import React, { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { API_CONFIG } from "@/config/api";
import {
  Box,
  IconButton,
  Modal,
  Typography,
  CircularProgress,
} from '@mui/material';
import { ZoomIn } from '@mui/icons-material';
import { Property } from '../types/property';

interface PropertyImagesProps {
  imovelId: string;
  imagens?: string[];
}

export const PropertyImages: React.FC<PropertyImagesProps> = ({ imovelId, imagens = [] }) => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [imageUrls, setImageUrls] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [failedImages, setFailedImages] = useState<Set<string>>(new Set());

  useEffect(() => {
    const fetchImages = async () => {
      try {
        setLoading(true);
        setError(null);
        if (!imagens || imagens.length === 0) {
          setLoading(false);
          return;
        }

        const urls = await Promise.all(
          imagens.map(async (imagemUrl) => {
            if (failedImages.has(imagemUrl)) {
              return null;
            }

            try {
              // Extrai o nome do arquivo da URL
              const nomeArquivo = imagemUrl.split('/').pop();
              if (!nomeArquivo) {
                console.error('Nome do arquivo não encontrado na URL:', imagemUrl);
                return null;
              }

              // Usa o endpoint que serve as imagens do MongoDB
              return API_CONFIG.getApiUrl(`/images/${imovelId}/${nomeArquivo}`);
            } catch (error) {
              console.error(`Erro ao carregar imagem ${imagemUrl}:`, error);
              setFailedImages(prev => new Set([...prev, imagemUrl]));
              return null;
            }
          })
        );

        const validUrls = urls.filter((url): url is string => url !== null);
        
        if (validUrls.length === 0) {
          setError('Não foi possível carregar nenhuma imagem');
        } else {
          setImageUrls(validUrls);
          setCurrentImageIndex(0);
        }
      } catch (error) {
        console.error('Erro ao buscar imagens:', error);
        setError('Não foi possível carregar as imagens do imóvel');
      } finally {
        setLoading(false);
      }
    };

    fetchImages();
  }, [imovelId, imagens, failedImages]);

  const handlePrevImage = () => {
    setCurrentImageIndex((prev) => (prev > 0 ? prev - 1 : imageUrls.length - 1));
  };

  const handleNextImage = () => {
    setCurrentImageIndex((prev) => (prev < imageUrls.length - 1 ? prev + 1 : 0));
  };

  const handleOpen = (image: string) => {
    setSelectedImage(image);
  };

  const handleClose = () => {
    setSelectedImage(null);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !imageUrls || imageUrls.length === 0) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={200} className="bg-gray-100">
        <div className="text-center">
          <img
            src="/placeholder.svg"
            alt="Imagem não disponível"
            className="w-16 h-16 mx-auto mb-2 opacity-50"
          />
          <Typography className="text-gray-500">
            {error || 'Nenhuma imagem disponível'}
          </Typography>
        </div>
      </Box>
    );
  }

  return (
    <Box className="relative group">
      <div className="relative w-full aspect-video">
        <img
          src={imageUrls[currentImageIndex]}
          alt={`Imagem ${currentImageIndex + 1} do imóvel`}
          className="w-full h-full object-cover"
          loading="lazy"
          onError={(e) => {
            const target = e.target as HTMLImageElement;
            target.src = '/placeholder.svg';
            target.className = 'w-full h-full object-contain p-4 bg-gray-100';
          }}
        />
        
        {/* Indicador de quantidade de imagens */}
        <div className="absolute bottom-2 right-2 bg-black/50 text-white px-2 py-1 rounded text-sm">
          {currentImageIndex + 1} / {imageUrls.length}
        </div>
      </div>

      {/* Botões de navegação */}
      {imageUrls.length > 1 && (
        <>
          <button
            onClick={handlePrevImage}
            className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/50 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
            aria-label="Imagem anterior"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>
          <button
            onClick={handleNextImage}
            className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/50 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
            aria-label="Próxima imagem"
          >
            <ChevronRight className="w-6 h-6" />
          </button>
        </>
      )}

      {/* Modal para visualização ampliada */}
      <Modal
        open={!!selectedImage}
        onClose={handleClose}
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Box
          sx={{
            maxWidth: '90%',
            maxHeight: '90%',
            outline: 'none',
          }}
        >
          {selectedImage && (
            <img
              src={selectedImage}
              alt="Imagem ampliada"
              style={{
                maxWidth: '100%',
                maxHeight: '90vh',
                objectFit: 'contain',
              }}
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.src = '/placeholder.svg';
                target.className = 'max-w-full max-h-[90vh] object-contain p-4 bg-gray-100';
              }}
            />
          )}
        </Box>
      </Modal>
    </Box>
  );
}; 