from pathlib import Path

from mistralai import Mistral
from services.ocr_processor import OCRProcessor
from services.chat_processor import ChatProcessor
from utils.post_processing.validators.fiscal_validator import FiscalDocumentValidator
from utils.post_processing.processor import ResponsePostProcessor
from utils.file_encoder import FileEncoder
from utils.logger import logger


class DocumentProcessor:
    def __init__(self, api_key: str):
        """Inicializa el procesador de documentos creando instancias del cliente Mistral, OCRProcessor y ChatProcessor."""
        self.client = Mistral(api_key=api_key)
        self.ocr_processor = OCRProcessor(self.client)
        self.chat_processor = ChatProcessor(self.client)
        self.fiscal_validator = FiscalDocumentValidator()
        self.post_processor = ResponsePostProcessor()

    def process_document(self, file_path: str) -> str:
        """Procesa un documento (imagen o PDF) basado en su extensión y retorna una respuesta estructurada en formato JSON.

        :param file_path: Ruta del archivo a procesar.
        :return: Respuesta estructurada en formato JSON.
        :raises ValueError: Si el tipo de archivo no es soportado o falla la codificación de la imagen.
        """
        file_ext = Path(file_path).suffix.lower()
        ocr_markdown = ""

        if file_ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
            ocr_markdown = self.ocr_processor.process_image(file_path)
            base64_image = FileEncoder.encode_image(file_path)
            if base64_image is None:
                logger.error(f"Error al codificar la imagen: {file_path}")
                raise ValueError(f"Error al codificar la imagen: {file_path}")
            base64_data_url = f"data:image/jpeg;base64,{base64_image}"
            structured_response = self.chat_processor.get_structured_response_image(base64_data_url, ocr_markdown)
        elif file_ext == ".pdf":
            document_url = self.ocr_processor.process_pdf(file_path)
            structured_response = self.chat_processor.get_structured_response_pdf(document_url)
        else:
            logger.error(f"Tipo de archivo no soportado: {file_ext}")
            raise ValueError("Tipo de archivo no soportado. Solo se permiten PDFs e imágenes (JPG, JPEG, PNG, WEBP, GIF).")

        logger.info(f"Respuesta estructurada generada: {structured_response}")

        # Validar el documento fiscal
        try:
            structured_response = self.fiscal_validator.validate(structured_response, ocr_markdown)
        except Exception as e:
            logger.error(f"Error al validar el documento fiscal: {e}")
            raise ValueError(f"Error al validar el documento fiscal: {e}")
        
        # Post-procesar la respuesta estructurada
        try:
            structured_response = self.post_processor.process_response(structured_response, ocr_markdown)
        except Exception as e:
            logger.error(f"Error al post-procesar la respuesta estructurada: {e}")
            raise ValueError(f"Error al post-procesar la respuesta estructurada: {e}")
        
        logger.info(f"Documento validado y post procesado: {structured_response}")
        return structured_response