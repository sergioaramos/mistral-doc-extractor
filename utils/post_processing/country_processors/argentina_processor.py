import re
from typing import Dict, Any
from utils.logger import logger
from utils.post_processing.country_processors.base_processor import CountryProcessor

class ArgentinaProcessor(CountryProcessor):
    """Procesador específico para documentos argentinos"""
    
    @classmethod
    def get_country_name(cls) -> str:
        return "argentina"
    
    def process(self, data: Dict[str, Any], ocr_markdown: str = "") -> None:
        """Procesa y corrige datos específicos para Argentina"""
        tax_info = data.get('tax_information', {})
        
        # Ajustar tipo de documento, CUIT para empresas, CUIL para personas
        self._set_document_type(data, tax_info)
        
        # Procesar CUIT/CUIL argentino
        self._process_cuit_cuil(tax_info)
        
        # Establecer tax_office específico para Argentina
        if not tax_info.get('tax_office'):
            tax_info['tax_office'] = "Administración Federal de Ingresos Públicos"
        
        # Corregir document_type para representante legal
        self._process_representative(data)
    
    def _set_document_type(self, data: Dict[str, Any], tax_info: Dict[str, Any]) -> None:
        """Establece el tipo de documento para Argentina"""
        company_name = data.get('company_information', {}).get('legal_name', '')
        if company_name:
            tax_info['tax_document_type'] = 'CUIT'
        elif not tax_info.get('tax_document_type') or tax_info.get('tax_document_type') == '':
            tax_info['tax_document_type'] = 'CUIT'  # Por defecto para documentos fiscales
    
    def _process_cuit_cuil(self, tax_info: Dict[str, Any]) -> None:
        """Procesa el CUIT/CUIL argentino"""
        tax_id = tax_info.get('tax_identification_number', '')
        
        # Verificar formato con guiones (XX-XXXXXXXX-X)
        cuit_pattern = re.search(r'(\d{2})-(\d{8})-(\d{1})', tax_id)
        if cuit_pattern:
            part1, part2, part3 = cuit_pattern.groups()
            tax_info['verification_digit'] = part3
            tax_info['tax_identification_number'] = f"{part1}{part2}"
            logger.info(f"CUIT/CUIL argentino procesado: Base={part1}{part2}, DV={part3}")
        
        # Si ya tenemos un CUIT/CUIL de 11 dígitos sin guiones
        elif tax_id and len(tax_id) == 11:
            if not tax_info.get('verification_digit'):
                tax_info['verification_digit'] = tax_id[-1]
            tax_info['tax_identification_number'] = tax_id[:-1]
            logger.info(f"CUIT/CUIL argentino corregido: separando DV={tax_id[-1]}")
    
    def _process_representative(self, data: Dict[str, Any]) -> None:
        """Procesa los datos del representante legal"""
        legal_rep = data.get('legal_representative', {})
        if legal_rep:
            if not legal_rep.get('document_type') or legal_rep.get('document_type') == '':
                legal_rep['document_type'] = 'DNI'
            
            # Si el representante legal también tiene CUIT/CUIL, aplicar la misma lógica
            if legal_rep.get('document_type') in ['CUIT', 'CUIL'] and legal_rep.get('document_number'):
                doc_number = legal_rep.get('document_number')
                if len(doc_number) == 11:
                    legal_rep['document_number'] = doc_number[:-1]