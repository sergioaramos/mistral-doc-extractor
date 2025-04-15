from typing import Any, Dict, List
import json
from mistralai.models import ImageURLChunk, TextChunk

from config.settings import TEMPLATE
from utils.logger import logger


class ChatProcessor:
    def __init__(self, client: Any):
        """
        Inicializa el procesador de chat con una instancia del cliente de Mistral.
        
        :param client: Instancia del cliente Mistral, ya configurado con la clave API.
        """
        self.client = client

    def get_structured_response_image(self, base64_data_url: str, ocr_markdown: str) -> str:
        """
        Genera una respuesta estructurada en JSON para imágenes a partir del OCR obtenido.

        :param base64_data_url: Imagen codificada en base64 en formato data URL.
        :param ocr_markdown: Texto obtenido del OCR en formato markdown.
        :return: Cadena JSON con la respuesta estructurada.
        """
        # Definición de la plantilla JSON para la respuesta
        template = TEMPLATE
        messages: List[Dict] = [
            {
                "role": "user",
                "content": [
                    ImageURLChunk(image_url=base64_data_url),
                    TextChunk(
                        text=(
                            f"This is image's OCR in markdown:\n\n{ocr_markdown}\n\n"
                            "IMPORTANTE: Debes devolver SIEMPRE un JSON válido con la siguiente estructura. "
                            "Si algún campo no está presente en el documento, déjalo como cadena vacía pero manteniendo "
                            "la estructura intacta.\n\n"
                            
                            "DETECCIÓN DE DOCUMENTOS FISCALES: Analiza cuidadosamente cada país según estas reglas:\n\n"
                            
                            "1. COLOMBIA: Un documento colombiano ES un documento fiscal si contiene UNO DE ESTOS elementos: "
                            "(a) Menciona 'RUT' o 'Registro Único Tributario' en cualquier parte del documento, O "
                            "(b) Contiene un NIT junto con un dígito de verificación, O "
                            "(c) Contiene una referencia a la DIAN. "
                            "Si cualquiera de estos elementos está presente, el documento es fiscal (`true`).\n\n"
                            
                            "2. PANAMÁ: Un documento panameño ES un documento fiscal cuando contiene: "
                            "(a) Un número de identificación con guiones (como '3-753-2443'), Y "
                            "(b) Menciona un establecimiento comercial o actividades económicas, Y "
                            "(c) Contiene referencias a PanamaEmprende o Aviso de Operación.\n\n"
                            
                            "3. ARGENTINA: Un documento argentino ES un documento fiscal cuando contiene: "
                            "(a) Un número CUIT/CUIL (como '33-70707631-9'), Y "
                            "(b) Menciona una empresa u organización, Y "
                            "(c) Hace referencia a la AFIP.\n\n"
                            
                            "IMPORTANTE: No exijas que se cumplan TODAS las condiciones para Colombia, con UNA es suficiente.\n\n"
                            
                            f"{template}"
                        )
                    ),
                ],
            }
        ]

        chat_response = self.client.chat.complete(
            model="pixtral-12b-latest",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0,
        )

        # Verificar si la respuesta es un JSON válido
        try:
            response_content = chat_response.choices[0].message.content
            json.loads(response_content)  # Intentar cargar como JSON
        except json.JSONDecodeError:
            logger.error("La respuesta del modelo no es un JSON válido")
            raise ValueError("La respuesta del modelo no es un JSON válido")
        
        return chat_response.choices[0].message.content

    def get_structured_response_pdf(self, document_url: str) -> str:
        """
        Genera una respuesta estructurada en JSON para documentos PDF a partir de su URL firmado.

        :param document_url: URL firmado del documento PDF.
        :return: Cadena JSON con la respuesta estructurada.
        """
        template = TEMPLATE
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "document_url",
                        "document_url": document_url
                    },
                    {
                        "type": "text", 
                        "text": "DETECCIÓN DE DOCUMENTOS FISCALES: Analiza cuidadosamente cada país según estas reglas:\n\n"
                            
                            "1. COLOMBIA: Un documento colombiano ES un documento fiscal si contiene UNO DE ESTOS elementos: "
                            "(a) Menciona 'RUT' o 'Registro Único Tributario' en cualquier parte del documento, O "
                            "(b) Contiene un NIT junto con un dígito de verificación, O "
                            "(c) Contiene una referencia a la DIAN. "
                            "Si cualquiera de estos elementos está presente, el documento es fiscal (`true`).\n\n"
                            
                            "2. PANAMÁ: Un documento panameño ES un documento fiscal cuando contiene: "
                            "(a) Un número de identificación con guiones (como '3-753-2443'), Y "
                            "(b) Menciona un establecimiento comercial o actividades económicas, Y "
                            "(c) Contiene referencias a PanamaEmprende o Aviso de Operación.\n\n"
                            
                            "3. ARGENTINA: Un documento argentino ES un documento fiscal cuando contiene: "
                            "(a) Un número CUIT/CUIL (como '33-70707631-9'), Y "
                            "(b) Menciona una empresa u organización, Y "
                            "(c) Hace referencia a la AFIP.\n\n"
                            
                            "IMPORTANTE: No exijas que se cumplan TODAS las condiciones para Colombia, con UNA es suficiente."
                    },
                    {
                        "type": "text",
                        "text": "Puedes devolver un json estructurado con la siguiente estructura"
                    },
                    {
                        "type": "text",
                        "text": template
                    }
                ]
            }
        ]

        chat_response = self.client.chat.complete(
            model="pixtral-12b-latest",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0,
        )

        # Verificar si la respuesta es un JSON válido
        try:
            response_content = chat_response.choices[0].message.content
            json.loads(response_content)  # Intentar cargar como JSON
        except json.JSONDecodeError:
            logger.error("La respuesta del modelo no es un JSON válido")
            raise ValueError("La respuesta del modelo no es un JSON válido")
        return chat_response.choices[0].message.content