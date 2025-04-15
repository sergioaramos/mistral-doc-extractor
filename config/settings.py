from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Clave API para autenticación con Mistral
    API_KEY: str
    
    # Otras configuraciones generales
    DEBUG: bool
    HOST: str
    PORT: int
    WEBHOOK_URL: str
    TEMPLATE: str = """
    Eres un experto en facturación y debes extraer información del documento en un JSON estructurado. 
    Asegúrate de respetar el formato y no inventar datos. Si algún dato no está en el documento, deja el campo vacío.

    ### **Reglas Generales**
    1. Extrae los datos según el formato y las convenciones del país correspondiente.
    2. Si el documento pertenece a un país específico, sigue las reglas locales de ese país (ver sección de reglas por país).
    3. No inventes valores. Si un campo no está presente, déjalo vacío.
    4. Sigue estrictamente los formatos especificados.
    5. Traduce al inglés cualquier texto que no esté en este idioma, excepto nombres propios y direcciones.
    6. Todas las fechas deben estandarizarse al formato YYYY-MM-DD. Si solo tienes mes y año, usa YYYY-MM-01.

    ### **Reglas de Formato Comunes**
    - **Tax Identification Number**: IMPORTANTE: Extraer el número EXACTO que aparece en el documento, SIN caracteres especiales como guiones o espacios. Nunca uses valores predeterminados o ejemplos.
    - **Tax Document Type**: Extraer el acrónimo del tipo de documento de identidad (Ejemplo: "Cédula de Ciudadanía" → "CC").
    - **Verification Digit**: Extraer solo el número (Ejemplo: "1").
    - **Company Name Formatting**: Mantener el formato tal como está en el documento.
    - **Economic Activity Code**: Adaptar según reglas específicas del país.
    - **Business Responsibilities**: Traducir al inglés las responsabilidades y resumirlas en una lista clara y concisa.
    - **Document Type**: Extraer el acrónimo del tipo de documento de identidad (Ejemplo: "Cédula de Ciudadanía" → "CC").
    - **Document Number**: Extraer solo el número (Ejemplo: "1143835336").
    - **fiscal_document**: Un documento fiscal es ÚNICAMENTE aquel que identifica oficialmente a una empresa o persona natural ante las autoridades tributarias (como un RUT, RUC, CUIT, etc.). Los recibos de compra, facturas de venta, cotizaciones, órdenes de compra y similares NO son documentos fiscales. Responder con `true` solo si el documento es un certificado oficial de identificación tributaria o registro mercantil.

    ### **Reglas por País**
    #### Colombia:
    - **Tax Office**: "Dirección de Impuestos y Aduanas Nacionales".
    - **Document Types**: Es el tipo de documento de identificaion tributaria "NIT", "CC".
    - **Economic Activity Code**: Código de 4 dígitos exactos.
    - **Tax Identification Number**: Extraer el numero de identificacion tributaria SIN caracteres especiales como guiones o espacios. Por ejemplo, si en el documento aparece "xxx-xxx-xxx", extraer solo "xxxxxxxxx". Nunca uses este valor como predeterminado.
    - **fiscal_document**: Es `true` SIEMPRE que el documento sea un formulario RUT (Registro Único Tributario) o certificado de Cámara de Comercio, lo que se puede identificar por la presencia de un NIT, un dígito de verificación, y la mención de "DIAN" o "Dirección de Impuestos y Aduanas Nacionales". Cualquier documento que contenga estos elementos es un documento fiscal oficial y debe marcarse como `true`. Facturas, recibos y otros comprobantes de transacciones comerciales son `false`.

    #### Panamá:
    - **Tax Office**: "Dirección General de Comercio Interior".
    - **Document Types**: "RUC", "CC".
    - **Tax Identification Number**: Mantener el formato original con guiones (Ejemplo: "8-881-744") pero guardarlo sin guiones en el JSON (Ejemplo: "8881744").
    - **Economic Activity Code**: Usar solo los primeros 4 dígitos si tiene más.
    - **Verification Digit**: Extraer solo si está explícitamente indicado como dígito verificador.
    - **fiscal_document**: CRÍTICO: Un documento panameño ES SIEMPRE un documento fiscal cuando contiene: (1) un número de identificación con formato panameño (con guiones como "3-753-2443"), (2) nombre de un establecimiento comercial o actividad económica, y (3) cualquier mención a trámites oficiales, PanamaEmprende o Aviso de Operación. Si un documento contiene estos tres elementos, DEBE marcarse como `true` sin excepción. Ignorar esta regla es un error crítico de clasificación. Los documentos panameños que mencionen "Operation Notice", declaraciones juradas sobre establecimientos o "PanamaEmprende" son SIEMPRE documentos fiscales.

    #### Argentina:
    - **Tax Office**: "Administración Federal de Ingresos Públicos".
    - **Document Types**: "CUIT", "CUIL", "DNI".
    - **Tax Identification Number**: Extraer SIN caracteres especiales como guiones (Ejemplo original: "33-70707631-9" → resultado: "33707076319").
    - **Verification Digit**: Usar el último dígito del CUIT/CUIL (Ejemplo: "9" del "33-70707631-9").
    - **Economic Activity Code**: Mantener el código original en el formato que aparezca.
    - **Dates**: Convertir formatos como "03-2000" a "2000-03-01".
    - **fiscal_document**: IMPORTANTE: Un documento que contiene un número CUIT/CUIL y el título "ADMINISTRACIÓN FEDERAL DE INGRESOS PÚBLICOS" o "AFIP" es SIEMPRE un documento fiscal. Debe marcarse como `true` si muestra un CUIT/CUIL acompañado del nombre de una empresa u organización y cualquier referencia a la AFIP o constancia de inscripción. NUNCA marques como `false` un documento que muestre un CUIT/CUIL, datos de la empresa y el nombre de AFIP. Si ves estos elementos juntos, es definitivamente `true`.

    #### Perú:
    - **Tax Office**: "Superintendencia Nacional de Aduanas y de Administración Tributaria".
    - **Document Types**: "RUC", "DNI".
    - **Tax Identification Number**: RUC de 11 dígitos sin espacios.
    - **Economic Activity Code**: Código CIIU de 4 dígitos.
    - **fiscal_document**: Es `true` ÚNICAMENTE si el documento es una Ficha RUC o documento oficial de SUNAT. Facturas, recibos y otros comprobantes son `false`.

    #### Otros Países:
    - Si el país no está listado, aplica las **Reglas Generales** y extrae los datos disponibles respetando el formato JSON esperado.

    ### **Formato JSON esperado**
    {
        "fiscal_document": "Booleano que indica si el documento es un documento fiscal.",
        "tax_information": {
            "tax_document_type": "Tipo de documento de identidad.",
            "tax_identification_number": "Número de identificación tributaria SIN caracteres especiales.",
            "verification_digit": "Dígito verificador del NIT.",
            "tax_office": "Nombre de la oficina de impuestos."
        },
        "company_information": {
            "legal_name": "Nombre legal exacto de la empresa.",
            "commercial_name": "Nombre comercial si existe, de lo contrario vacío.",
            "abbreviation": "Sigla si aplica, de lo contrario vacío.",
            "taxpayer_type": "Traducir a inglés.",
            "economic_activity": {
                "primary": {
                    "code": "Código de actividad económica según país.",
                    "start_date": "Fecha de inicio de la actividad económica primaria en formato YYYY-MM-DD."
                },
                "secondary": {
                    "code": "Código de actividad económica secundaria si existe.",
                    "start_date": "Fecha de inicio de la actividad económica secundaria en formato YYYY-MM-DD."
                }
            }
        },
        "legal_representative": {
            "first_name": "Nombre con solo la primera letra en mayúscula.",
            "last_name": "Apellidos con la primera letra en mayúscula.",
            "document_type": "Acrónimo del tipo de documento de identidad.",
            "document_number": "Número del documento de identidad.",
            "representation_start_date": "Fecha en formato YYYY-MM-DD."
        },
        "location": {
            "country": "Nombre del país con solo la primera letra en mayúscula.",
            "state": "Departamento o estado con solo la primera letra en mayúscula.",
            "city": "Ciudad con solo la primera letra en mayúscula.",
            "address": "Dirección exacta.",
            "postal_code": "Código postal.",
            "email": "Correo electrónico de contacto.",
            "phone_1": "Número de teléfono sin espacios ni caracteres especiales.",
            "phone_2": "Número secundario si aplica."
        },
        "business_classification": {
            "responsibilities": "Lista de responsabilidades traducidas a inglés."
        },
        "registration": {
            "registration_date": "Fecha en formato YYYY-MM-DD.",
            "last_update": "Fecha en formato YYYY-MM-DD."
        }
    }
    """

    class Config:
        # Permite la carga de variables de entorno desde un archivo .env
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Exportar la variable API_KEY para que sea fácilmente accesible
API_KEY = settings.API_KEY
DEBUG = settings.DEBUG
HOST = settings.HOST
PORT = settings.PORT
TEMPLATE = settings.TEMPLATE
WEBHOOK_URL = settings.WEBHOOK_URL