import re
from typing import Dict, Any
from utils.logger import logger
from utils.post_processing.country_processors.base_processor import CountryProcessor

class PeruProcessor(CountryProcessor):
    """Procesador específico para documentos peruanos"""
    
    @classmethod
    def get_country_name(cls) -> str:
        return "peru"
    
    def process(self, data: Dict[str, Any], ocr_markdown: str = "") -> None:
        """Procesa y corrige datos específicos para Perú"""
        tax_info = data.get('tax_information', {})
        
        # Siempre usar RUC para documentos fiscales en Perú
        if not tax_info.get('tax_document_type') or tax_info.get('tax_document_type') == '':
            tax_info['tax_document_type'] = 'RUC'
            logger.info("Asignado tipo de documento 'RUC' por defecto")
        
        # Validar formato RUC
        self._validate_ruc(tax_info)
        
        # Establecer tax_office específico para Perú
        if not tax_info.get('tax_office'):
            tax_info['tax_office'] = "Superintendencia Nacional de Aduanas y de Administración Tributaria"
            logger.info("Asignada oficina de impuestos por defecto para Perú")
        
        # Corregir document_type para representante legal
        self._process_representative(data)
    
    def _validate_ruc(self, tax_info: Dict[str, Any]) -> None:
        """Valida el formato del RUC peruano"""
        if tax_info.get('tax_document_type') == 'RUC' and tax_info.get('tax_identification_number'):
            tax_id = re.sub(r'[^0-9]', '', tax_info['tax_identification_number'])
            if len(tax_id) > 0 and len(tax_id) != 11:
                logger.warning(f"RUC peruano no tiene 11 dígitos: {tax_id}")
            tax_info['tax_identification_number'] = tax_id
    
    def _process_representative(self, data: Dict[str, Any]) -> None:
        """Procesa los datos del representante legal"""
        legal_rep = data.get('legal_representative', {})
        if legal_rep:
            if not legal_rep.get('document_type') or legal_rep.get('document_type') == '':
                legal_rep['document_type'] = 'DNI'
                logger.info("Asignado tipo de documento 'DNI' por defecto al representante legal")