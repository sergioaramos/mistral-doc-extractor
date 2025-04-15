import base64
import logging
from pathlib import Path
from mistralai.models import ImageURLChunk
from utils.logger import logger

class OCRProcessor:
    def __init__(self, client):
        """Inicializa el procesador de OCR con una instancia del cliente Mistral.

        :param client: Instancia del cliente Mistral, configurado con la clave API.
        """
        self.client = client

    def process_image(self, image_path: str) -> str:
        """Procesa una imagen utilizando OCR y retorna el resultado en formato markdown.

        :param image_path: Ruta del archivo de imagen.
        :return: Texto en formato markdown extraído de la imagen.
        :raises FileNotFoundError: Si el archivo no existe.
        :raises Exception: Para otros errores durante el procesamiento.
        """
        image_file = Path(image_path)
        if not image_file.is_file():
            logger.error(f"Archivo no encontrado: {image_path}")
            raise FileNotFoundError(f"Archivo no encontrado: {image_path}")

        try:
            encoded = base64.b64encode(image_file.read_bytes()).decode('utf-8')
            base64_data_url = f"data:image/jpeg;base64,{encoded}"
            image_response = self.client.ocr.process(
                document=ImageURLChunk(image_url=base64_data_url),
                model="mistral-ocr-latest"
            )
            return image_response.pages[0].markdown
        except Exception as e:
            logger.error(f"Error al procesar la imagen {image_path}: {e}")
            raise e

    def process_pdf(self, pdf_path: str) -> str:
        """Procesa un documento PDF utilizando OCR y retorna la URL firmada del documento procesado.

        :param pdf_path: Ruta del archivo PDF.
        :return: URL firmada del documento PDF.
        :raises FileNotFoundError: Si el archivo no existe.
        :raises Exception: Para otros errores durante el procesamiento.
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.is_file():
            logger.error(f"Archivo no encontrado: {pdf_path}")
            raise FileNotFoundError(f"Archivo no encontrado: {pdf_path}")

        try:
            with open(pdf_file, "rb") as file_content:
                uploaded_file = self.client.files.upload(
                    file={
                        "file_name": "uploaded_file.pdf",
                        "content": file_content,
                    },
                    purpose="ocr",
                )
            # Se realiza la recuperación y firma del archivo subido
            self.client.files.retrieve(file_id=uploaded_file.id)
            signed_url = self.client.files.get_signed_url(file_id=uploaded_file.id)

            # Opcional: Procesar el OCR del PDF si se requiere
            ocr_response = self.client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": signed_url.url,
                },
                include_image_base64=True,
            )
            
            return signed_url.url
        except Exception as e:
            logger.error(f"Error al procesar el PDF {pdf_path}: {e}", exc_info=True)
            raise e