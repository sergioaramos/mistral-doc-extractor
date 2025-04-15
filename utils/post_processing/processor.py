import json
from typing import Dict, Any, Optional

from utils.logger import logger
from utils.post_processing.country_processors import (
    get_country_processor,
    detect_country
)
from utils.post_processing.validators import (
    validate_tax_document,
    validate_tax_id,
    validate_person_document
)
from utils.post_processing.utils.date_normalizer import normalize_dates

class ResponsePostProcessor:
    """
    Clase principal para post-procesar y corregir datos extraídos de documentos fiscales
    después de la validación fiscal.
    """
    
    @staticmethod
    def process_response(json_response: str, ocr_markdown: str = "") -> str:
        """
        Procesa y corrige la respuesta JSON para asegurar que los datos estén
        correctamente formateados según las reglas específicas de cada país.
        
        Args:
            json_response: Respuesta JSON original (ya validada por fiscal_validator)
            ocr_markdown: Texto OCR original para validaciones adicionales
            
        Returns:
            JSON corregido y estandarizado
        """
        try:
            data = json.loads(json_response)
            
            # Obtener o detectar el país
            country = data.get('location', {}).get('country', '').lower()
            if not country:
                country = detect_country(data, ocr_markdown)
                if country:
                    if 'location' not in data:
                        data['location'] = {}
                    data['location']['country'] = country
            
            # Obtener el procesador específico para el país
            country_processor = get_country_processor(country)
            
            # Procesar datos específicos del país
            if country_processor:
                country_processor.process(data, ocr_markdown)
            
            # Aplicar validaciones generales
            ResponsePostProcessor._apply_general_fixes(data, ocr_markdown)
            
            logger.info("Post-procesamiento completado correctamente")
            return json.dumps(data)
        
        except json.JSONDecodeError:
            logger.error("Error decodificando JSON en el post-procesador")
            return json_response
        except Exception as e:
            logger.error(f"Error en el post-procesamiento: {e}")
            return json_response
    
    @staticmethod
    def _apply_general_fixes(data: Dict[str, Any], ocr_markdown: str = "") -> None:
        """Aplica correcciones generales a cualquier documento"""
        # Validar y corregir los campos críticos
        tax_info = data.get('tax_information', {})
        legal_rep = data.get('legal_representative', {})
        country = data.get('location', {}).get('country', '').lower()
        
        # Validar tax_document_type
        validate_tax_document(tax_info, country, data, ocr_markdown)
        
        # Validar tax_identification_number
        validate_tax_id(tax_info, country, ocr_markdown)
        
        # Validar document_type y document_number del representante legal
        validate_person_document(legal_rep, country, ocr_markdown)
        
        # Normalizar formato de fechas
        normalize_dates(data)
        
        # Asegurar que fiscal_document sea booleano
        if 'fiscal_document' in data and not isinstance(data['fiscal_document'], bool):
            if isinstance(data['fiscal_document'], str):
                data['fiscal_document'] = data['fiscal_document'].lower() == 'true'