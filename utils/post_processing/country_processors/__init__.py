import re
from typing import Dict, Any, Optional

from utils.logger import logger
from utils.post_processing.country_processors.base_processor import CountryProcessor
from utils.post_processing.country_processors.colombia_processor import ColombiaProcessor
from utils.post_processing.country_processors.panama_processor import PanamaProcessor
from utils.post_processing.country_processors.argentina_processor import ArgentinaProcessor
from utils.post_processing.country_processors.peru_processor import PeruProcessor

# Registro de procesadores disponibles
_PROCESSORS = {
    'colombia': ColombiaProcessor(),
    'panama': PanamaProcessor(),
    'argentina': ArgentinaProcessor(),
    'peru': PeruProcessor()
}

def get_country_processor(country: str) -> Optional[CountryProcessor]:
    """
    Retorna el procesador específico para el país indicado
    
    Args:
        country: Nombre del país (en minúsculas)
        
    Returns:
        Instancia del procesador específico o None si no hay coincidencia
    """
    if not country:
        return None
        
    for key, processor in _PROCESSORS.items():
        if key in country:
            return processor
    return None

def detect_country(data: Dict[str, Any], ocr_markdown: str = "") -> Optional[str]:
    """
    Detecta el país basado en patrones de identificación
    
    Args:
        data: Datos del documento
        ocr_markdown: Texto OCR original
        
    Returns:
        Nombre del país detectado o None si no se puede determinar
    """
    tax_info = data.get('tax_information', {})
    tax_id = tax_info.get('tax_identification_number', '')
    
    # Patrones para Colombia: NIT con dígito de verificación
    if re.search(r'\d{9,10}-\d{1}', tax_id) or re.search(r'\d{1,3}\.\d{3}\.\d{3}-\d{1}', tax_id):
        logger.info("Patrón de NIT colombiano detectado por formato")
        return "Colombia"
    
    # Patrones para Panamá: ID con formato X-XXX-XXXX
    elif re.search(r'\d{1,2}-\d{3,4}-\d{3,4}', tax_id):
        logger.info("Patrón de identificación panameña detectado por formato")
        return "Panama"
    
    # Patrones para Argentina: CUIT/CUIL con formato XX-XXXXXXXX-X
    elif re.search(r'\d{2}-\d{8}-\d{1}', tax_id):
        logger.info("Patrón de CUIT/CUIL argentino detectado por formato")
        return "Argentina"
    
    # Patrones para Perú: RUC siempre tiene 11 dígitos
    elif tax_id and len(tax_id) == 11:
        logger.info("Posible RUC peruano detectado por longitud (11 dígitos)")
        return "Peru"
    
    # Si no se detecta por los datos, intentar inferir del OCR
    elif ocr_markdown:
        # Buscar patrones específicos de países en el OCR
        if re.search(r'NIT|DIAN|Colombia|Colombiana|Bogot[aá]|Medell[ií]n|Cali', ocr_markdown, re.IGNORECASE):
            logger.info("País Colombia detectado por OCR")
            return "Colombia"
        
        elif re.search(r'RUC|Panam[aá]|Ciudad de Panam[aá]|Panamanian', ocr_markdown, re.IGNORECASE):
            logger.info("País Panamá detectado por OCR")
            return "Panama"
        
        elif re.search(r'CUIT|CUIL|AFIP|Argentina|Buenos Aires|Mendoza|C[oó]rdoba', ocr_markdown, re.IGNORECASE):
            logger.info("País Argentina detectado por OCR")
            return "Argentina"
        
        elif re.search(r'RUC|Per[uú]|SUNAT|Lima|Arequipa|Trujillo', ocr_markdown, re.IGNORECASE):
            logger.info("País Perú detectado por OCR")
            return "Peru"
    
    return None