import re
from typing import Optional
from utils.logger import logger

def extract_tax_id_from_ocr(doc_type: str, country: str, ocr_markdown: str) -> Optional[str]:
    """
    Extrae el número de identificación fiscal del texto OCR
    
    Args:
        doc_type: Tipo de documento fiscal
        country: País del documento
        ocr_markdown: Texto OCR para extraer información
        
    Returns:
        Número de identificación fiscal extraído o None si no se encuentra
    """
    if not ocr_markdown:
        return None
    
    # Patrones específicos por tipo de documento y país
    if 'colombia' in country:
        if doc_type == 'NIT':
            # Buscar patrones de NIT en el OCR
            nit_patterns = [
                r'NIT\s*:?\s*(\d{1,3}[\.,]?\d{3}[\.,]?\d{3}[-]?\d?)',
                r'N\.?I\.?T\.?\s*:?\s*(\d{1,3}[\.,]?\d{3}[\.,]?\d{3}[-]?\d?)',
                r'(?:Número|Numero)?\s*(?:de)?\s*(?:Identificación|Identificacion)?\s*(?:Tributaria?)?:?\s*(\d{1,3}[\.,]?\d{3}[\.,]?\d{3}[-]?\d?)'
            ]
            
            for pattern in nit_patterns:
                match = re.search(pattern, ocr_markdown, re.IGNORECASE)
                if match:
                    return match.group(1)
    
    elif 'panama' in country or 'panamá' in country:
        if doc_type == 'RUC':
            # Buscar patrones de RUC panameño
            ruc_patterns = [
                r'RUC\s*:?\s*(\d{1,2}[-]?\d{3,4}[-]?\d{3,4})',
                r'R\.?U\.?C\.?\s*:?\s*(\d{1,2}[-]?\d{3,4}[-]?\d{3,4})',
                r'Registro\s+[ÚúUu]nico\s+(?:de)?\s*Contribuyente\s*:?\s*(\d{1,2}[-]?\d{3,4}[-]?\d{3,4})'
            ]
            
            for pattern in ruc_patterns:
                match = re.search(pattern, ocr_markdown, re.IGNORECASE)
                if match:
                    return match.group(1)
    
    elif 'argentina' in country:
        if doc_type == 'CUIT' or doc_type == 'CUIL':
            # Buscar patrones de CUIT/CUIL argentino
            cuit_patterns = [
                r'CUIT\s*:?\s*(\d{2}[-]?\d{8}[-]?\d{1})',
                r'CUIL\s*:?\s*(\d{2}[-]?\d{8}[-]?\d{1})',
                r'C\.?U\.?I\.?T\.?\s*:?\s*(\d{2}[-]?\d{8}[-]?\d{1})',
                r'C\.?U\.?I\.?L\.?\s*:?\s*(\d{2}[-]?\d{8}[-]?\d{1})'
            ]
            
            for pattern in cuit_patterns:
                match = re.search(pattern, ocr_markdown, re.IGNORECASE)
                if match:
                    return match.group(1)
    
    elif 'peru' in country or 'perú' in country:
        if doc_type == 'RUC':
            # Buscar patrones de RUC peruano
            ruc_patterns = [
                r'RUC\s*:?\s*(\d{11})',
                r'R\.?U\.?C\.?\s*:?\s*(\d{11})',
                r'Registro\s+[ÚúUu]nico\s+(?:de)?\s*Contribuyente\s*:?\s*(\d{11})'
            ]
            
            for pattern in ruc_patterns:
                match = re.search(pattern, ocr_markdown, re.IGNORECASE)
                if match:
                    return match.group(1)
                    
    # Si llegamos aquí, buscar cualquier secuencia de números que pueda ser un ID fiscal
    # en función del país y el tipo de documento
    if 'colombia' in country and doc_type == 'NIT':
        # NIT sin formato específico (9-10 dígitos)
        general_match = re.search(r'(\d{9,10})', ocr_markdown)
        if general_match:
            logger.info(f"Posible NIT colombiano encontrado por patrón general: {general_match.group(1)}")
            return general_match.group(1)
            
    elif 'argentina' in country and (doc_type == 'CUIT' or doc_type == 'CUIL'):
        # CUIT/CUIL sin formato específico (11 dígitos)
        general_match = re.search(r'(\d{11})', ocr_markdown)
        if general_match:
            logger.info(f"Posible CUIT/CUIL argentino encontrado por patrón general: {general_match.group(1)}")
            return general_match.group(1)
            
    elif 'peru' in country and doc_type == 'RUC':
        # RUC sin formato específico (11 dígitos)
        general_match = re.search(r'(\d{11})', ocr_markdown)
        if general_match:
            logger.info(f"Posible RUC peruano encontrado por patrón general: {general_match.group(1)}")
            return general_match.group(1)
    
    return None