import base64
import logging
from pathlib import Path
from utils.logger import logger


class FileEncoder:
    @staticmethod
    def encode_image(image_path: str) -> str:
        """Codifica una imagen a una cadena en base64.

        :param image_path: Ruta del archivo de imagen.
        :return: Cadena codificada en base64 o None si ocurre un error.
        """
        image_file = Path(image_path)
        if not image_file.is_file():
            logger.error(f"Archivo no encontrado: {image_path}")
            return None
        
        try:
            with open(image_file, "rb") as f:
                encoded_data = base64.b64encode(f.read()).decode('utf-8')
            return encoded_data
        except Exception as e:
            logger.error(f"Error al codificar la imagen {image_path}: {e}")
            return None
