import re
from typing import Dict, Any
from utils.logger import logger
from utils.post_processing.utils.ocr_extractor import extract_tax_id_from_ocr

def validate_tax_id(tax_info: Dict[str, Any], country: str, ocr_markdown: str = "") -> None:
    """
    Valida y corrige el tax_identification_number según patrones específicos por país
    
    Args:
        tax_info: Información fiscal a validar y corregir
        country: País del documento
        ocr_markdown: Texto OCR para extraer información adicional
    """
    if not tax_info:
        return
        
    tax_id = tax_info.get('tax_identification_number', '')
    doc_type = tax_info.get('tax_document_type', '').upper()
    
    # Si no hay tax_id pero tenemos OCR, intentar extraerlo
    if not tax_id and ocr_markdown:
        tax_id = extract_tax_id_from_ocr(doc_type, country, ocr_markdown)
        if tax_id:
            tax_info['tax_identification_number'] = tax_id
    
    # Si no hay tax_id después de buscar en OCR, terminar
    if not tax_id:
        return
        
    # Eliminar caracteres no numéricos para validación
    clean_id = re.sub(r'[^0-9]', '', tax_id)
    
    # Validaciones específicas por país
    if 'colombia' in country:
        _validate_colombia_tax_id(tax_info, doc_type, tax_id, clean_id)
    elif 'panama' in country or 'panamá' in country:
        _validate_panama_tax_id(tax_info, tax_id, clean_id)
    elif 'argentina' in country:
        _validate_argentina_tax_id(tax_info, doc_type, tax_id, clean_id)
    elif 'peru' in country or 'perú' in country:
        _validate_peru_tax_id(tax_info, doc_type, clean_id)
    
    # Actualizar con el ID limpio
    tax_info['tax_identification_number'] = clean_id

def _validate_colombia_tax_id(tax_info: Dict[str, Any], doc_type: str, tax_id: str, clean_id: str) -> None:
    """Valida y corrige el tax_identification_number para Colombia"""
    if doc_type == 'NIT':
        # Verificar DV y formato
        if len(clean_id) > 10:
            if not tax_info.get('verification_digit'):
                tax_info['verification_digit'] = clean_id[-1]
                tax_info['tax_identification_number'] = clean_id[:-1]
                logger.info(f"Extrayendo DV del tax_identification_number: {clean_id[:-1]}, DV: {tax_info['verification_digit']}")
        
        # Buscar DV en el formato original (ej. 900123456-7)
        elif '-' in tax_id and not tax_info.get('verification_digit'):
            parts = tax_id.split('-')
            if len(parts) == 2 and len(parts[1]) == 1:
                tax_info['verification_digit'] = parts[1]
                logger.info(f"DV detectado en formato NIT: {parts[1]}")

def _validate_panama_tax_id(tax_info: Dict[str, Any], tax_id: str, clean_id: str) -> None:
    """Valida y corrige el tax_identification_number para Panamá"""
    # RUC panameño puede tener formato variado, pero generalmente
    # sigue el patrón X-XXX-XXXX o similar con guiones
    if '-' in tax_id:
        # Conservar el formato con guiones en el original
        formatted_id = tax_id
        logger.info(f"Formato RUC panameño detectado: {formatted_id}, limpio: {clean_id}")

def _validate_argentina_tax_id(tax_info: Dict[str, Any], doc_type: str, tax_id: str, clean_id: str) -> None:
    """Valida y corrige el tax_identification_number para Argentina"""
    if doc_type == 'CUIT' or doc_type == 'CUIL':
        # Si ya tiene 11 dígitos, separar el último como verificador
        if len(clean_id) == 11:
            if not tax_info.get('verification_digit'):
                tax_info['verification_digit'] = clean_id[-1]
            tax_info['tax_identification_number'] = clean_id[:-1]
            logger.info(f"Separando dígito verificador del CUIT/CUIL: {clean_id[:-1]}, DV: {clean_id[-1]}")
            
        # Buscar DV en el formato original (ej. 20-12345678-9)
        elif '-' in tax_id and len(tax_id.split('-')) == 3:
            parts = tax_id.split('-')
            if len(parts[2]) == 1:
                tax_info['verification_digit'] = parts[2]
                tax_info['tax_identification_number'] = parts[0] + parts[1]
                logger.info(f"DV detectado en formato CUIT/CUIL: {parts[2]}")

def _validate_peru_tax_id(tax_info: Dict[str, Any], doc_type: str, clean_id: str) -> None:
    """Valida y corrige el tax_identification_number para Perú"""
    # RUC peruano debe tener 11 dígitos
    if doc_type == 'RUC' and len(clean_id) != 11 and len(clean_id) > 0:
        logger.warning(f"RUC peruano con longitud inválida: {len(clean_id)} dígitos")
        
    # DNI peruano debe tener 8 dígitos
    elif doc_type == 'DNI' and len(clean_id) != 8 and len(clean_id) > 0:
        logger.warning(f"DNI peruano con longitud inválida: {len(clean_id)} dígitos")