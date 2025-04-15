import re
from typing import Dict, Any

def normalize_dates(data: Dict[str, Any]) -> None:
    """
    Normaliza todas las fechas al formato YYYY-MM-DD
    
    Args:
        data: Datos del documento con fechas a normalizar
    """
    # Patrones comunes de fechas
    date_patterns = [
        # DD/MM/YYYY
        (r'(\d{1,2})/(\d{1,2})/(\d{4})', lambda m: f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"),
        # MM/DD/YYYY
        (r'(\d{1,2})/(\d{1,2})/(\d{4})', lambda m: f"{m.group(3)}-{m.group(1).zfill(2)}-{m.group(2).zfill(2)}"),
        # DD-MM-YYYY
        (r'(\d{1,2})-(\d{1,2})-(\d{4})', lambda m: f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"),
        # YYYY/MM/DD
        (r'(\d{4})/(\d{1,2})/(\d{1,2})', lambda m: f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"),
        # MM-YYYY (convertir a YYYY-MM-01)
        (r'(\d{1,2})-(\d{4})', lambda m: f"{m.group(2)}-{m.group(1).zfill(2)}-01"),
    ]
    
    # Campos que contienen fechas
    date_fields = [
        ['registration', 'registration_date'],
        ['registration', 'last_update'],
        ['company_information', 'economic_activity', 'primary', 'start_date'],
        ['company_information', 'economic_activity', 'secondary', 'start_date'],
        ['legal_representative', 'representation_start_date']
    ]
    
    # Normalizar cada campo de fecha
    for path in date_fields:
        _normalize_date_field(data, path, date_patterns)

def _normalize_date_field(data: Dict[str, Any], path: list, patterns: list) -> None:
    """Normaliza un campo de fecha específico"""
    current = data
    for i, key in enumerate(path):
        if i == len(path) - 1:
            # Llegamos al campo de fecha
            date_value = current.get(key, '')
            if date_value and isinstance(date_value, str):
                # Aplicar patrones de normalización
                for pattern, replacement in patterns:
                    if re.match(pattern, date_value):
                        current[key] = re.sub(pattern, replacement, date_value)
                        break
        elif key in current:
            current = current[key]
        else:
            break