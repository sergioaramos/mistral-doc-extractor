import logging
import sys

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configura y retorna un logger con el nombre y nivel especificados.
    
    :param name: Nombre del logger.
    :param level: Nivel de logging (por defecto, INFO).
    :return: Instancia de logging.Logger configurada.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Evitar añadir múltiples handlers si ya existen
    if not logger.handlers:
        # Crear un handler para la salida en consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # Definir el formato del log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
    return logger

# Configuración del logger para el módulo actual
logger = setup_logger(__name__)