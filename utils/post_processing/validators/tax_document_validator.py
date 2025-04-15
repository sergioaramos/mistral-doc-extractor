import re
from typing import Dict, Any
from utils.logger import logger

def validate_tax_document(tax_info: Dict[str, Any], country: str, data: Dict[str, Any], ocr_markdown: str = "") -> None:
    """
    Valida y corrige el tax_document_type según reglas específicas por país
    
    Args:
        tax_info: Información fiscal a validar y corregir
        country: País del documento
        data: Datos completos del documento
        ocr_markdown: Texto OCR para extraer información adicional
    """
    if not tax_info:
        return
        
    company_name = data.get('company_information', {}).get('legal_name', '')
    current_type = tax_info.get('tax_document_type', '').upper()
    
    # Lista de tipos válidos por país
    valid_types = {
        'colombia': ['NIT', 'CC', 'CE', 'TI', 'PP'],
        'panama': ['RUC', 'CI'],
        'argentina': ['CUIT', 'CUIL', 'DNI'],
        'peru': ['RUC', 'DNI']
    }
    
    # Si el tax_document_type está vacío, intentar extraerlo del OCR
    if not current_type and ocr_markdown:
        # Patrones para buscar el tipo de documento en el OCR
        type_patterns = {
            'colombia': [
                (r'NIT\s*:?\s*\d', 'NIT'),
                (r'C[eé]dula\s*de\s*Ciudadan[ií]a', 'CC'),
                (r'C\.?C\.?\s*:?\s*\d', 'CC'),
                (r'C[eé]dula\s*de\s*Extranjer[ií]a', 'CE'),
                (r'C\.?E\.?\s*:?\s*\d', 'CE')
            ],
            'panama': [
                (r'RUC\s*:?\s*\d', 'RUC'),
                (r'C[eé]dula\s*de\s*Identidad', 'CI'),
                (r'C\.?I\.?\s*:?\s*\d', 'CI')
            ],
            'argentina': [
                (r'CUIT\s*:?\s*\d', 'CUIT'),
                (r'CUIL\s*:?\s*\d', 'CUIL'),
                (r'DNI\s*:?\s*\d', 'DNI')
            ],
            'peru': [
                (r'RUC\s*:?\s*\d', 'RUC'),
                (r'DNI\s*:?\s*\d', 'DNI')
            ]
        }
        
        # Buscar patrones en el OCR para el país detectado
        for c, patterns in type_patterns.items():
            if c in country:
                for pattern, doc_type in patterns:
                    if re.search(pattern, ocr_markdown, re.IGNORECASE):
                        current_type = doc_type
                        logger.info(f"Tipo de documento fiscal '{doc_type}' detectado por OCR")
                        break
                
                if current_type:
                    break
    
    # Determinar el país para aplicar reglas
    target_country = None
    for c in valid_types.keys():
        if c in country:
            target_country = c
            break
    
    if not target_country:
        return  # No podemos determinar el país
    
    # Corrección basada en país y contenido
    correct_type = None
    
    if target_country == 'colombia':
        # Para Colombia: empresas usan NIT, personas naturales CC
        if company_name:
            correct_type = 'NIT'
        else:
            # Si no es empresa y el tipo actual no es válido, usar CC por defecto
            correct_type = current_type if current_type in valid_types['colombia'] else 'CC'
    
    elif target_country == 'panama':
        # Para Panamá: casi siempre es RUC para documentos fiscales
        correct_type = 'RUC'
    
    elif target_country == 'argentina':
        # Para Argentina: empresas usan CUIT, personas CUIL
        if company_name:
            correct_type = 'CUIT'
        else:
            # Si no es una empresa, intentar determinar entre CUIL y DNI
            if current_type in valid_types['argentina']:
                correct_type = current_type
            else:
                correct_type = 'CUIL'  # Por defecto para personas
    
    elif target_country == 'peru':
        # Para Perú: empresas usan RUC, personas DNI
        if company_name:
            correct_type = 'RUC'
        else:
            correct_type = 'DNI'
    
    # Verificar si el tipo actual es válido, si no, corregirlo
    if current_type not in valid_types[target_country]:
        logger.info(f"Corrigiendo tax_document_type de '{current_type}' a '{correct_type}'")
        tax_info['tax_document_type'] = correct_type
    elif not current_type:
        logger.info(f"Asignando tax_document_type por defecto: '{correct_type}'")
        tax_info['tax_document_type'] = correct_type