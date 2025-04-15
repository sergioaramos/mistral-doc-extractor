import json
import re
from typing import Dict, Any
from utils.logger import logger


class FiscalDocumentValidator:
    def __init__(self):
        # Country-specific regex patterns for fiscal identifiers
        self.patterns = {
            "colombia": {
                "nit": r'\b\d{9,10}[-\s]?\d?\b',  # NIT pattern with optional verification digit
                "rut": r'\bRUT\b|Registro\s+[Úú]nico\s+Tributario',
                "dian": r'\bDIAN\b|Direcci[óo]n\s+de\s+Impuestos\s+y\s+Aduanas'
            },
            "panama": {
                "id": r'\b\d{1,2}[-\s]\d{3,4}[-\s]\d{3,4}\b',  # Panamá ID format: X-XXX-XXXX
                "business": r'PanamaEmprende|Aviso\s+de\s+Operaci[óo]n|establecimiento\s+comercial'
            },
            "argentina": {
                "cuit": r'\b\d{2}[-\s]\d{8}[-\s]\d{1}\b',  # CUIT/CUIL format: XX-XXXXXXXX-X
                "afip": r'\bAFIP\b|Administraci[óo]n\s+Federal\s+de\s+Ingresos\s+P[úu]blicos'
            },
            "peru": {
                "ruc": r'\bRUC\s*[:=]?\s*\d{11}\b',
                "sunat": r'\bSUNAT\b|Superintendencia\s+Nacional\s+de\s+Aduanas'
            }
        }
    
    def validate(self, json_response: str, original_text: str) -> str:
        """
        Validate if a document classified as non-fiscal might actually be fiscal
        
        Args:
            json_response: The original JSON response string from Mistral
            original_text: The raw text extracted from the document through OCR
            
        Returns:
            Updated JSON response string with corrected fiscal_document value if needed
        """
        try:
            response_data = json.loads(json_response)
            print(f"Validating fiscal document with fiscal_document status: {response_data.get('fiscal_document')}")
            
            # Only run validation if fiscal_document is false
            if not response_data.get("fiscal_document"):
                fiscal_status = self._determine_fiscal_status(original_text, response_data)
                
                if fiscal_status:
                    logger.info("Document reclassified as fiscal by validator")
                    response_data["fiscal_document"] = True
                    return json.dumps(response_data)
            
            return json_response
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON response - cannot validate fiscal status")
            return json_response
    
    def _determine_fiscal_status(self, text: str, response_data: Dict[str, Any]) -> bool:
        """Determine if document is fiscal based on text patterns and tax information"""
        # Get country from location if available
        country = response_data.get("location", {}).get("country", "").lower()
        
        # Check tax ID - if present, strong indicator of fiscal document
        tax_id = response_data.get("tax_information", {}).get("tax_identification_number")
        if tax_id and len(tax_id) >= 8:
            return True
            
        # Run country-specific checks
        if country == "colombia" or self._check_patterns(text, self.patterns["colombia"]):
            # In Colombia, ANY of these conditions makes it fiscal
            return (
                self._check_patterns(text, self.patterns["colombia"]) or
                "nit" in text.lower() or "rut" in text.lower() or 
                "dian" in text.lower()
            )
            
        elif country == "panama" or self._check_patterns(text, self.patterns["panama"]):
            # For Panama, need both ID pattern and business reference
            patterns = self.patterns["panama"]
            has_id = bool(re.search(patterns["id"], text))
            has_business = bool(re.search(patterns["business"], text))
            return has_id and has_business
            
        elif country == "argentina" or self._check_patterns(text, self.patterns["argentina"]):
            # For Argentina, need CUIT pattern and AFIP reference
            patterns = self.patterns["argentina"]
            return bool(re.search(patterns["cuit"], text) and re.search(patterns["afip"], text))
            
        elif country == "peru" or self._check_patterns(text, self.patterns["peru"]):
            # For Peru, need RUC pattern and SUNAT reference
            patterns = self.patterns["peru"]
            return bool(re.search(patterns["ruc"], text) and re.search(patterns["sunat"], text))
            
        return False
    
    def _check_patterns(self, text: str, patterns: Dict[str, str]) -> bool:
        """Check if any pattern in the dictionary matches the text"""
        return any(bool(re.search(pattern, text, re.IGNORECASE)) for pattern in patterns.values())