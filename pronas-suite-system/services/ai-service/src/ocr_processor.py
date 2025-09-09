import pytesseract
from PIL import Image
import pdf2image
import cv2
import numpy as np
from typing import List, Dict, Optional
import aiohttp
import asyncio
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

class OCRProcessor:
    def __init__(self):
        self.supported_formats = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff']
        self.tesseract_config = '--oem 3 --psm 6 -l por'
        
    async def extract_text(self, document_url: str) -> str:
        """Extrai texto de documento usando OCR"""
        try:
            # Download do documento
            document_bytes = await self._download_document(document_url)
            
            # Determinar tipo de documento
            if document_url.lower().endswith('.pdf'):
                return await self._extract_from_pdf(document_bytes)
            else:
                return await self._extract_from_image(document_bytes)
                
        except Exception as e:
            logger.error(f"Erro no OCR para {document_url}: {str(e)}")
            raise
    
    async def _download_document(self, url: str) -> bytes:
        """Faz download do documento"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.read()
    
    async def _extract_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extrai texto de PDF"""
        # Converter PDF para imagens
        images = pdf2image.convert_from_bytes(pdf_bytes, dpi=300)
        
        texts = []
        for i, image in enumerate(images):
            # Preprocessar imagem
            processed_image = self._preprocess_image(np.array(image))
            
            # Aplicar OCR
            text = pytesseract.image_to_string(
                processed_image,
                config=self.tesseract_config
            )
            texts.append(text)
            
            logger.info(f"Processada página {i+1} do PDF")
        
        return '\n\n'.join(texts)
    
    async def _extract_from_image(self, image_bytes: bytes) -> str:
        """Extrai texto de imagem"""
        # Carregar imagem
        image = Image.open(BytesIO(image_bytes))
        
        # Preprocessar
        processed_image = self._preprocess_image(np.array(image))
        
        # Aplicar OCR
        text = pytesseract.image_to_string(
            processed_image,
            config=self.tesseract_config
        )
        
        return text
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocessa imagem para melhorar OCR"""
        # Converter para escala de cinza
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Remover ruído
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Binarização adaptativa
        binary = cv2.adaptiveThreshold(
            denoised, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Correção de inclinação
        coords = np.column_stack(np.where(binary > 0))
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = 90 + angle
            
        (h, w) = binary.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            binary, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        return rotated
    
    async def extract_tables(self, document_url: str) -> List[Dict]:
        """Extrai tabelas de documentos"""
        # Implementação para extração de tabelas
        document_bytes = await self._download_document(document_url)
        
        if document_url.lower().endswith('.pdf'):
            import tabula
            tables = tabula.read_pdf(BytesIO(document_bytes), pages='all')
            return [table.to_dict() for table in tables]
        
        return []
    
    async def extract_structured_data(self, document_url: str) -> Dict:
        """Extrai dados estruturados do documento"""
        text = await self.extract_text(document_url)
        tables = await self.extract_tables(document_url)
        
        return {
            "text": text,
            "tables": tables,
            "metadata": {
                "url": document_url,
                "word_count": len(text.split()),
                "char_count": len(text)
            }
        }