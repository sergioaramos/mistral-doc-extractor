import re
from typing import Dict, Any
from utils.logger import logger
from utils.post_processing.country_processors.base_processor import CountryProcessor

class ColombiaProcessor(CountryProcessor):
    """Procesador específico para documentos colombianos"""
    
    @classmethod
    def get_country_name(cls) -> str:
        return "colombia"
    
    def process(self, data: Dict[str, Any], ocr_markdown: str = "") -> None:
        """Procesa y corrige datos específicos para Colombia"""
        tax_info = data.get('tax_information', {})
        
        # Corregir tax_document_type (siempre NIT para empresas, CC para personas)
        self._set_document_type(data, tax_info)
        
        # Procesar NIT y dígito verificador
        self._process_nit(tax_info)
        
        # Establecer tax_office específico para Colombia
        if not tax_info.get('tax_office'):
            tax_info['tax_office'] = "Dirección de Impuestos y Aduanas Nacionales"
        
        # Corregir document_type para representante legal
        self._process_representative(data)
    
    def _set_document_type(self, data: Dict[str, Any], tax_info: Dict[str, Any]) -> None:
        """Establece el tipo de documento para Colombia"""
        company_name = data.get('company_information', {}).get('legal_name', '')
        if company_name:
            tax_info['tax_document_type'] = 'NIT'
        elif not tax_info.get('tax_document_type'):
            tax_info['tax_document_type'] = 'NIT'  # Por defecto para documentos fiscales
    
    def _process_nit(self, tax_info: Dict[str, Any]) -> None:
        """Procesa el NIT colombiano y extrae el dígito verificador"""
        tax_id = tax_info.get('tax_identification_number', '')
        
        # Buscar patrones de NIT con punto y guión (900.123.456-7)
        nit_pattern = re.search(r'(\d{1,3}(?:\.\d{3}){2})-(\d{1})', tax_id)
        if nit_pattern:
            # Extraer componentes del NIT
            base, dv = nit_pattern.groups()
            # Configurar verification_digit
            tax_info['verification_digit'] = dv
            # Actualizar tax_identification_number sin puntos ni guiones
            tax_info['tax_identification_number'] = re.sub(r'[^0-9]', '', base)
            logger.info(f"NIT colombiano procesado: Base={re.sub(r'[^0-9]', '', base)}, DV={dv}")
        
        # Buscar patrones de NIT sin puntos pero con guión (900123456-7)
        elif '-' in tax_id:
            parts = tax_id.split('-')
            if len(parts) == 2 and parts[1].isdigit() and len(parts[1]) == 1:
                tax_info['verification_digit'] = parts[1]
                tax_info['tax_identification_number'] = parts[0].replace('.', '').replace(' ', '')
                logger.info(f"NIT colombiano con guión procesado: Base={parts[0]}, DV={parts[1]}")
    
    def _process_representative(self, data: Dict[str, Any]) -> None:
        """Procesa los datos del representante legal"""
        legal_rep = data.get('legal_representative', {})
        if legal_rep:
            if not legal_rep.get('document_type') or legal_rep.get('document_type') == '':
                legal_rep['document_type'] = 'CC'
                logger.info("Asignado tipo de documento 'CC' por defecto al representante legal")