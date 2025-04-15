import re
from typing import Dict, Any
from utils.logger import logger
from utils.post_processing.country_processors.base_processor import CountryProcessor

class PanamaProcessor(CountryProcessor):
    """Procesador específico para documentos panameños"""
    
    @classmethod
    def get_country_name(cls) -> str:
        return "panama"
    
    def process(self, data: Dict[str, Any], ocr_markdown: str = "") -> None:
        """Procesa y corrige datos específicos para Panamá"""
        tax_info = data.get('tax_information', {})
        
        # Siempre usar RUC para documentos fiscales en Panamá
        if not tax_info.get('tax_document_type') or tax_info.get('tax_document_type') == '':
            tax_info['tax_document_type'] = 'RUC'
            logger.info("Asignado tipo de documento 'RUC' por defecto")
        
        # Procesar identificación panameña (formato X-XXX-XXXX)
        self._process_ruc(tax_info)
        
        # Establecer tax_office específico para Panamá
        if not tax_info.get('tax_office'):
            tax_info['tax_office'] = "Dirección General de Comercio Interior"
            logger.info("Asignada oficina de impuestos por defecto para Panamá")
        
        # Corregir document_type para representante legal
        self._process_representative(data)
    
    def _process_ruc(self, tax_info: Dict[str, Any]) -> None:
        """Procesa el RUC panameño"""
        tax_id = tax_info.get('tax_identification_number', '')
        if re.search(r'\d{1,2}-\d{3,4}-\d{3,4}', tax_id):
            # Ya tenemos el formato correcto, solo eliminamos los guiones
            clean_id = re.sub(r'[^0-9]', '', tax_id)
            tax_info['tax_identification_number'] = clean_id
            logger.info(f"Identificación panameña procesada: {tax_id} → {clean_id}")
    
    def _process_representative(self, data: Dict[str, Any]) -> None:
        """Procesa los datos del representante legal"""
        legal_rep = data.get('legal_representative', {})
        if legal_rep:
            if not legal_rep.get('document_type') or legal_rep.get('document_type') == '':
                legal_rep['document_type'] = 'CI'
                logger.info("Asignado tipo de documento 'CI' por defecto al representante legal")