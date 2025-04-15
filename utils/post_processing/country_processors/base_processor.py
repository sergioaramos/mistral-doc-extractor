from abc import ABC, abstractmethod
from typing import Dict, Any

class CountryProcessor(ABC):
    """Clase base abstracta para procesadores específicos de cada país"""
    
    @abstractmethod
    def process(self, data: Dict[str, Any], ocr_markdown: str = "") -> None:
        """Procesa y corrige datos específicos del país"""
        pass
    
    @classmethod
    def get_country_name(cls) -> str:
        """Retorna el nombre del país que maneja este procesador"""
        pass