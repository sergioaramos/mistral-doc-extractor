import re
from typing import Dict, Any
from utils.logger import logger

def validate_person_document(legal_rep: Dict[str, Any], country: str, ocr_markdown: str = "") -> None:
    """
    Valida y corrige el document_type y document_number del representante legal
    
    Args:
        legal_rep: Datos del representante legal
        country: País del documento
        ocr_markdown: Texto OCR para extraer información adicional
    """
    if not legal_rep:
        return
    
    # Validar document_type
    validate_document_type(legal_rep, country, ocr_markdown)
    
    # Validar document_number
    validate_document_number(legal_rep, country, ocr_markdown)

def validate_document_type(legal_rep: Dict[str, Any], country: str, ocr_markdown: str = "") -> None:
    """Valida y corrige el document_type del representante legal"""
    current_type = legal_rep.get('document_type', '').upper()
    
    # Si no hay document_type pero tenemos OCR, intentar extraerlo
    if not current_type and ocr_markdown:
        # Patrones para buscar el tipo de documento en el OCR
        rep_doc_patterns = {
            'colombia': [
                (r'(?:Representante|Gerente|Director).*?(?:C\.?C\.?|C[eé]dula).*?(\d{6,12})', 'CC'),
                (r'(?:Representante|Gerente|Director).*?(?:C\.?E\.?).*?(\d{6,12})', 'CE'),
                (r'(?:Representante|Gerente|Director).*?(?:Pasaporte).*?([A-Z0-9]{6,12})', 'PP')
            ],
            'panama': [
                (r'(?:Representante|Gerente|Director).*?(?:C\.?I\.?|C[eé]dula).*?(\d{1,2}-\d{3,4}-\d{3,4})', 'CI'),
                (r'(?:Representante|Gerente|Director).*?(?:Pasaporte).*?([A-Z0-9]{6,12})', 'PASAPORTE')
            ],
            'argentina': [
                (r'(?:Representante|Gerente|Director).*?(?:DNI).*?(\d{7,8})', 'DNI'),
                (r'(?:Representante|Gerente|Director).*?(?:CUIT|CUIL).*?(\d{2}-\d{8}-\d{1})', 'CUIT')
            ],
            'peru': [
                (r'(?:Representante|Gerente|Director).*?(?:DNI).*?(\d{8})', 'DNI'),
                (r'(?:Representante|Gerente|Director).*?(?:CE).*?([A-Z0-9]{9,12})', 'CE')
            ]
        }
        
        # Buscar patrones en el OCR para el país detectado
        for c, patterns in rep_doc_patterns.items():
            if c in country:
                for pattern, doc_type in patterns:
                    match = re.search(pattern, ocr_markdown, re.IGNORECASE)
                    if match:
                        current_type = doc_type
                        # Si encontramos también el número, guardarlo
                        legal_rep['document_number'] = match.group(1)
                        logger.info(f"Tipo de documento '{doc_type}' y número '{match.group(1)}' del representante legal detectados por OCR")
                        break
                
                if current_type:
                    break
    
    # Si aún no hay tipo de documento, asignar valor por defecto según el país
    if not current_type:
        # Asignar valor por defecto según el país
        if 'colombia' in country:
            legal_rep['document_type'] = 'CC'
            logger.info("Asignando document_type por defecto para Colombia: CC")
        elif 'panama' in country or 'panamá' in country:
            legal_rep['document_type'] = 'CI'
            logger.info("Asignando document_type por defecto para Panamá: CI")
        elif 'argentina' in country:
            legal_rep['document_type'] = 'DNI'
            logger.info("Asignando document_type por defecto para Argentina: DNI")
        elif 'peru' in country or 'perú' in country:
            legal_rep['document_type'] = 'DNI'
            logger.info("Asignando document_type por defecto para Perú: DNI")
        return
        
    # Lista de tipos válidos por país
    valid_types = {
        'colombia': ['CC', 'CE', 'TI', 'PP'],
        'panama': ['CI', 'RUC', 'PASAPORTE'],
        'argentina': ['DNI', 'CUIT', 'CUIL', 'LE', 'LC'],
        'peru': ['DNI', 'CE', 'PTP']
    }
    
    # Determinar el país para aplicar reglas
    target_country = None
    for c in valid_types.keys():
        if c in country:
            target_country = c
            break
    
    if not target_country:
        return  # No podemos determinar el país
        
    # Verificar si el tipo actual es válido, si no, corregirlo
    if current_type not in valid_types[target_country]:
        # Usar el tipo predeterminado para el país
        default_types = {
            'colombia': 'CC',
            'panama': 'CI',
            'argentina': 'DNI',
            'peru': 'DNI'
        }
        correct_type = default_types[target_country]
        logger.info(f"Corrigiendo document_type de '{current_type}' a '{correct_type}'")
        legal_rep['document_type'] = correct_type
    else:
        legal_rep['document_type'] = current_type

def validate_document_number(legal_rep: Dict[str, Any], country: str, ocr_markdown: str = "") -> None:
    """Valida y corrige el document_number del representante legal"""
    doc_number = legal_rep.get('document_number', '')
    doc_type = legal_rep.get('document_type', '').upper()
    
    # Si no hay document_number pero tenemos OCR y doc_type, intentar extraerlo
    if not doc_number and ocr_markdown and doc_type:
        # Patrones para buscar el número de documento en el OCR según el tipo
        rep_num_patterns = {
            'CC': r'(?:Representante|Gerente|Director).*?(?:C\.?C\.?|C[eé]dula).*?(?:No\.?|Numero|Número)?:?\s*(\d{6,12})',
            'CE': r'(?:Representante|Gerente|Director).*?(?:C\.?E\.?).*?(?:No\.?|Numero|Número)?:?\s*(\d{6,12})',
            'TI': r'(?:Representante|Gerente|Director).*?(?:T\.?I\.?).*?(?:No\.?|Numero|Número)?:?\s*(\d{6,12})',
            'PP': r'(?:Representante|Gerente|Director).*?(?:Pasaporte).*?(?:No\.?|Numero|Número)?:?\s*([A-Z0-9]{6,12})',
            'CI': r'(?:Representante|Gerente|Director).*?(?:C\.?I\.?|C[eé]dula).*?(?:No\.?|Numero|Número)?:?\s*(\d{1,2}-\d{3,4}-\d{3,4}|\d{5,12})',
            'DNI': r'(?:Representante|Gerente|Director).*?(?:DNI).*?(?:No\.?|Numero|Número)?:?\s*(\d{7,8})',
            'CUIT': r'(?:Representante|Gerente|Director).*?(?:CUIT).*?(?:No\.?|Numero|Número)?:?\s*(\d{2}-\d{8}-\d{1}|\d{11})',
            'CUIL': r'(?:Representante|Gerente|Director).*?(?:CUIL).*?(?:No\.?|Numero|Número)?:?\s*(\d{2}-\d{8}-\d{1}|\d{11})'
        }
        
        if doc_type in rep_num_patterns:
            pattern = rep_num_patterns[doc_type]
            match = re.search(pattern, ocr_markdown, re.IGNORECASE)
            if match:
                doc_number = match.group(1)
                legal_rep['document_number'] = doc_number
                logger.info(f"Número de documento del representante legal detectado por OCR: {doc_number}")
    
    # Si aún no hay documento, terminar
    if not doc_number:
        return
        
    # Limpiar caracteres no numéricos (excepto para pasaportes)
    if doc_type != 'PP' and doc_type != 'PASAPORTE':
        clean_number = re.sub(r'[^0-9]', '', doc_number)
    else:
        # Para pasaportes, permitir letras y números, eliminar otros caracteres
        clean_number = re.sub(r'[^A-Z0-9]', '', doc_number.upper())
    
    # Validaciones específicas por país
    if 'colombia' in country:
        # Cédula colombiana generalmente tiene entre 8 y 10 dígitos
        if doc_type == 'CC' and (len(clean_number) < 5 or len(clean_number) > 12):
            logger.warning(f"Posible número de documento colombiano inválido: {clean_number}, longitud: {len(clean_number)}")
        
    elif 'panama' in country or 'panamá' in country:
        # CI panameña generalmente sigue el formato X-XXX-XXXX
        if doc_type == 'CI':
            if '-' in doc_number:
                # Si tenía guiones, verificar que la limpieza los eliminó correctamente
                if doc_number.replace('-', '') != clean_number:
                    logger.info(f"Limpiando guiones del documento panameño: {doc_number} → {clean_number}")
                    
            # Validar longitud
            if len(clean_number) < 5 or len(clean_number) > 12:
                logger.warning(f"Posible número de documento panameño inválido: {clean_number}, longitud: {len(clean_number)}")
        
    elif 'argentina' in country:
        # DNI argentino generalmente tiene entre 7 y 8 dígitos
        if doc_type == 'DNI' and (len(clean_number) < 7 or len(clean_number) > 9):
            logger.warning(f"Posible número de documento argentino inválido: {clean_number}, longitud: {len(clean_number)}")
        
        # CUIT/CUIL debe tener 11 dígitos
        elif (doc_type == 'CUIT' or doc_type == 'CUIL') and len(clean_number) != 11:
            logger.warning(f"CUIT/CUIL debería tener 11 dígitos, encontrado: {len(clean_number)}")
        
    elif 'peru' in country or 'perú' in country:
        # DNI peruano tiene 8 dígitos
        if doc_type == 'DNI' and len(clean_number) != 8:
            logger.warning(f"DNI peruano debería tener 8 dígitos, encontrado: {len(clean_number)}")
    
    # Actualizar con el número limpio
    legal_rep['document_number'] = clean_number