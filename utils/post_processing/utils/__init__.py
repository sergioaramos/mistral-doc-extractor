# Exportar utilidades específicas
from utils.post_processing.utils.date_normalizer import normalize_dates
from utils.post_processing.utils.ocr_extractor import extract_tax_id_from_ocr

__all__ = [
    'normalize_dates',
    'extract_tax_id_from_ocr'
]