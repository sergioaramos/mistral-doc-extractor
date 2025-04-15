## Descripción

Mistral API es una aplicación avanzada para el procesamiento de documentos fiscales y corporativos utilizando modelos de IA de Mistral. La plataforma integra tecnología OCR (Reconocimiento Óptico de Caracteres) y sistemas de post-procesamiento para extraer, validar y estructurar información a partir de documentos fiscales en diferentes formatos. 

Esta solución está especialmente diseñada para gestionar documentos tributarios de múltiples países latinoamericanos, proporcionando interpretación contextual precisa según las normativas locales y generando respuestas estructuradas en formato JSON que pueden integrarse fácilmente con otros sistemas empresariales.

## Características Principales

- **Procesamiento Multiformato**: Soporte para imágenes (JPG, JPEG, PNG, WEBP, GIF) y documentos PDF.
- **OCR Avanzado**: Extracción precisa de texto utilizando el modelo OCR de Mistral.
- **Generación Inteligente**: Conversión del texto extraído en respuestas JSON estructuradas.
- **Validación Fiscal Contextual**: Identificación automática de documentos fiscales con criterios específicos por país.
- **Sistema Sofisticado de Post-procesamiento**:
  - **Detección Automática de País**: Reconocimiento del país de origen con o sin información explícita.
  - **Normalización de Datos**: Estandarización de fechas, formatos de identificación y otros campos críticos.
  - **Validación Especializada**: Verificación de identificadores fiscales según reglas nacionales específicas.
  - **Corrección Automática**: Ajuste de formatos y tipos de documentos según estándares oficiales.
  - **Procesamiento por País**: Lógica especializada para Colombia, Panamá, Argentina y Perú.
- **Arquitectura Extensible**: Diseño modular que facilita la adición de soporte para nuevos países.
- **Notificaciones de Error**: Sistema integrado de alertas vía webhook para monitoreo de incidencias.
- **Trazabilidad Completa**: Sistema de logs detallado para seguimiento de operaciones.

## Soporte para Países y Documentos Fiscales

El sistema incluye validación y procesamiento especializado para:

- **Colombia**:
  - Documentos: RUT (Registro Único Tributario), Certificados de Cámara de Comercio
  - Identificadores: NIT con dígito verificador
  - Autoridades: DIAN (Dirección de Impuestos y Aduanas Nacionales)
  - Tipos de documento: NIT, CC, CE, TI, PP

- **Panamá**:
  - Documentos: Avisos de Operación, Certificados PanamaEmprende
  - Identificadores: RUC, formato X-XXX-XXXX
  - Autoridades: Dirección General de Comercio Interior
  - Tipos de documento: RUC, CI, Pasaporte

- **Argentina**:
  - Documentos: Constancias de inscripción fiscal, certificados AFIP
  - Identificadores: CUIT/CUIL con formato XX-XXXXXXXX-X y dígito verificador
  - Autoridades: AFIP (Administración Federal de Ingresos Públicos)
  - Tipos de documento: CUIT, CUIL, DNI, LE, LC

- **Perú**:
  - Documentos: Ficha RUC, certificados SUNAT
  - Identificadores: RUC de 11 dígitos
  - Autoridades: SUNAT (Superintendencia Nacional de Aduanas y Administración Tributaria)
  - Tipos de documento: RUC, DNI, CE, PTP

## Requisitos Técnicos

- **Python**: Versión 3.9 o superior
- **Dependencias Principales**:
  - `mistralai==1.5.2`: Cliente oficial para interactuar con la API de Mistral
  - `fastapi`: Framework web de alto rendimiento para APIs
  - `uvicorn`: Servidor ASGI para aplicaciones Python
  - `python-multipart`: Soporte para procesamiento de archivos multipart
  - `pydantic-settings`: Gestión de configuraciones con validación
  - `requests`: Cliente HTTP para comunicación con servicios externos

## Instalación y Configuración

### Instalación Básica

1. **Clonar el Repositorio**:
   ```sh
   git clone <URL_DEL_REPOSITORIO>
   cd Mistral
   ```

2. **Configurar Entorno Virtual**:
   ```sh
   # Crear entorno virtual
   python -m venv venv
   
   # Activar entorno virtual
   # En macOS/Linux:
   source venv/bin/activate
   
   # En Windows:
   venv\Scripts\activate
   ```

3. **Instalar Dependencias**:
   ```sh
   pip install -r requirements.txt
   ```

### Configuración del Entorno

1. **Crear Archivo de Variables de Entorno**:
   Crea un archivo `.env` en el directorio raíz con las siguientes variables:

   ```ini
   # Clave API de Mistral (obligatoria)
   API_KEY=tu_api_key_de_mistral
   
   # Configuración del servidor
   DEBUG=True
   HOST=0.0.0.0
   PORT=5001
   
   # URL para notificaciones de errores
   WEBHOOK_URL=https://tu_webhook_url
   ```

2. **Configuración Avanzada** (opcional):

   Si necesitas personalizar el comportamiento de procesamiento para países específicos, puedes modificar las clases correspondientes en el directorio `utils/post_processing/country_processors/`.

3. **Verificación de Instalación**:
   ```sh
   # Iniciar el servidor para verificar
   uvicorn api.main:app --reload
   
   # Comprobar si el servicio está funcionando
   curl http://localhost:5001/api/health
   ```

## Uso y Ejemplos

### Iniciar el Servicio

```sh
# Iniciar con reinicio automático para desarrollo
uvicorn api.main:app --reload --host 0.0.0.0 --port 5001

# Iniciar en modo producción
uvicorn api.main:app --host 0.0.0.0 --port 5001
```

La API estará disponible en `http://localhost:5001`.

### Documentación Interactiva

La documentación interactiva de la API estará disponible en:
- Swagger UI: `http://localhost:5001/docs`
- ReDoc: `http://localhost:5001/redoc`

### Endpoints API

#### 1. Procesar Documento Fiscal

**Endpoint**: `POST /api/upload-document/`

**Descripción**: Procesa un documento fiscal (imagen o PDF) y extrae información estructurada.

**Parámetros**:
- `file`: Archivo de imagen (JPG, JPEG, PNG, WEBP, GIF) o PDF para procesar.

**Cuerpo de la solicitud** (multipart/form-data):
```
file=@ruta/al/documento.jpg
```

**Ejemplo de solicitud cURL**:
```sh
curl -X 'POST' \
  'http://localhost:5001/api/upload-document/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/ruta/al/documento.jpg'
```

**Ejemplo de respuesta** (para un RUT colombiano):
```json
{
  "fiscal_document": true,
  "tax_information": {
    "tax_document_type": "NIT",
    "tax_identification_number": "9001234567",
    "verification_digit": "8",
    "tax_office": "Dirección de Impuestos y Aduanas Nacionales"
  },
  "company_information": {
    "legal_name": "EMPRESA EJEMPLO S.A.S",
    "commercial_name": "EMPRESA EJEMPLO",
    "abbreviation": "",
    "taxpayer_type": "Legal entity",
    "economic_activity": {
      "primary": {
        "code": "6201",
        "start_date": "2020-01-15"
      },
      "secondary": {
        "code": "7020",
        "start_date": "2020-05-20"
      }
    }
  },
  "legal_representative": {
    "first_name": "Juan",
    "last_name": "Pérez Gómez",
    "document_type": "CC",
    "document_number": "1014253698",
    "representation_start_date": "2020-01-15"
  },
  "location": {
    "country": "Colombia",
    "state": "Bogotá D.C.",
    "city": "Bogotá",
    "address": "Calle 93 # 11-13, Oficina 401",
    "postal_code": "110221",
    "email": "contacto@empresaejemplo.com",
    "phone_1": "6013752211",
    "phone_2": ""
  },
  "business_classification": {
    "responsibilities": ["VAT responsible", "Income tax payer", "ICA tax payer"]
  },
  "registration": {
    "registration_date": "2020-01-15",
    "last_update": "2023-05-10"
  }
}
```

#### 2. Verificar Estado del Servicio

**Endpoint**: `GET /api/health`

**Descripción**: Verifica si el servicio está funcionando correctamente.

**Ejemplo de solicitud cURL**:
```sh
curl -X 'GET' 'http://localhost:5001/api/health'
```

**Respuesta**:
```json
{"status": "ok"}
```

### Códigos de Respuesta HTTP

- **200 OK**: Solicitud exitosa.
- **400 Bad Request**: Solicitud mal formada o datos inválidos.
- **415 Unsupported Media Type**: Tipo de archivo no soportado.
- **500 Internal Server Error**: Error en el procesamiento del documento.

## Arquitectura del Sistema

El sistema está diseñado con una arquitectura modular orientada a microservicios, facilitando su mantenimiento y extensibilidad.

### Componentes Principales

#### 1. **Capa de API (FastAPI)**
- **`endpoints.py`**: Define los puntos de entrada HTTP para el procesamiento de documentos.
- **`main.py`**: Inicializa la aplicación FastAPI y configura las rutas.

#### 2. **Capa de Servicios**
- **`DocumentProcessor`**: Actúa como orquestador central, coordinando el flujo completo de procesamiento.
- **`OCRProcessor`**: Encapsula la interacción con la API de OCR de Mistral para extraer texto de imágenes y PDFs.
- **`ChatProcessor`**: Gestiona la comunicación con el modelo de lenguaje Mistral para generar respuestas estructuradas.
- **`WebhookService`**: Proporciona capacidades de notificación para monitoreo y alertas.

#### 3. **Sistema de Post-procesamiento**
- **`FiscalDocumentValidator`**: Implementa lógica especializada para identificar documentos fiscales según patrones específicos por país.
- **`ResponsePostProcessor`**: Coordina la validación, corrección y normalización de los datos extraídos.
- **Procesadores específicos por país**:
  - `ColombiaProcessor`: Aplica reglas específicas para documentos colombianos (NIT, dígito verificador).
  - `PanamaProcessor`: Procesa identificaciones fiscales panameñas (formato RUC).
  - `ArgentinaProcessor`: Gestiona documentos argentinos (CUIT/CUIL).
  - `PeruProcessor`: Aplica validaciones para documentos peruanos (RUC).

#### 4. **Módulos de Validación**
- **`tax_document_validator`**: Valida y corrige tipos de documentos fiscales.
- **`tax_id_validator`**: Verifica identificadores fiscales según normativas locales.
- **`document_validator`**: Valida documentos de identidad personal.

#### 5. **Utilidades**
- **`date_normalizer`**: Estandariza formatos de fecha a ISO (YYYY-MM-DD).
- **`ocr_extractor`**: Extrae información específica del texto OCR.
- **`file_encoder`**: Gestiona la codificación de archivos para su procesamiento.
- **`logger`**: Proporciona servicios de registro estructurado para diagnóstico y seguimiento.

### Diagrama de Flujo de Datos

```
Cliente → API (endpoints.py) → DocumentProcessor
                               ↓
                               OCRProcessor → API Mistral OCR
                               ↓
                               ChatProcessor → API Mistral LLM
                               ↓
                               FiscalDocumentValidator
                               ↓
                               ResponsePostProcessor → Procesadores por país
                               ↓
                               Respuesta JSON Estructurada
```

## Estructura del Proyecto

```
mistral-api/
│
├── api/                      # Endpoints y lógica de API
│   ├── endpoints.py          # Definición de rutas y controladores
│   └── main.py               # Punto de entrada de la aplicación
│
├── config/                   # Configuración
│   └── settings.py           # Variables de configuración
│
├── services/                 # Servicios principales
│   ├── chat_processor.py     # Procesamiento de chat con Mistral
│   ├── document_processor.py # Orquestación de procesamiento de documentos
│   ├── ocr_processor.py      # Procesamiento OCR
│   └── webhook.py            # Servicio de notificaciones
│
├── utils/                    # Utilidades
│   ├── file_encoder.py       # Codificación de archivos
│   ├── logger.py             # Sistema de logs
│   │
│   └── post_processing/      # Sistema de post-procesamiento
│       ├── processor.py      # Procesador principal
│       │
│       ├── country_processors/   # Procesadores específicos por país
│       │   ├── argentina_processor.py
│       │   ├── base_processor.py
│       │   ├── colombia_processor.py
│       │   ├── panama_processor.py
│       │   └── peru_processor.py
│       │
│       ├── utils/            # Utilidades de post-procesamiento
│       │   ├── date_normalizer.py   # Normalización de fechas
│       │   └── ocr_extractor.py     # Extracción de datos de OCR
│       │
│       └── validators/       # Validadores
│           ├── document_validator.py    # Validación de documentos personales
│           ├── fiscal_validator.py      # Validación de documentos fiscales
│           ├── tax_document_validator.py  # Validación de tipos de documentos fiscales
│           └── tax_id_validator.py     # Validación de IDs fiscales
│
├── .env                      # Variables de entorno (no en control de versiones)
├── .gitignore                # Archivos ignorados por git
├── README.md                 # Documentación del proyecto
└── requirements.txt          # Dependencias del proyecto
```

## Flujo de Procesamiento

El sistema implementa un sofisticado flujo de procesamiento de documentos que combina OCR, procesamiento de lenguaje natural y reglas de negocio específicas por país:

### 1. Recepción y Validación Inicial
- **API FastAPI**: Recibe la solicitud HTTP con el documento adjunto.
- **Validación de Tipo**: Verifica que el archivo sea una imagen (JPG, JPEG, PNG, WEBP, GIF) o PDF.
- **Almacenamiento Temporal**: Guarda el archivo para su procesamiento.

### 2. Extracción de Texto (OCR)
- **OCRProcessor**: Utiliza el modelo OCR de Mistral para extraer texto del documento.
- **Procesamiento Específico**:
  - Para imágenes: Convierte a base64 y envía directamente al servicio OCR.
  - Para PDFs: Gestiona la subida del documento y obtiene una URL firmada para su procesamiento.

### 3. Generación de Respuesta Estructurada
- **ChatProcessor**: Envía el texto extraído al modelo de lenguaje Mistral con instrucciones específicas.
- **Plantilla Especializada**: Utiliza un prompt detallado que guía al modelo para extraer información según el tipo de documento y país.
- **Formato JSON**: Genera una respuesta estructurada siguiendo un esquema predefinido.

### 4. Validación Fiscal
- **FiscalDocumentValidator**: Analiza el documento para determinar si es un documento fiscal.
- **Patrones Específicos por País**: Aplica reglas específicas según el país identificado:
  - Colombia: Busca referencias a NIT, RUT o DIAN.
  - Panamá: Verifica formato de RUC y referencias a PanamaEmprende.
  - Argentina: Identifica CUIT/CUIL y menciones a AFIP.
  - Perú: Detecta RUC y referencias a SUNAT.

### 5. Post-procesamiento y Normalización
- **ResponsePostProcessor**: Coordina la aplicación de correcciones y validaciones.
- **Detección de País**: Si no está explícito, infiere el país por patrones en el texto o estructura de IDs.
- **Procesador Específico**: Selecciona y aplica el procesador adecuado según el país.
- **Validaciones Específicas**:
  - Normalización de fechas a formato YYYY-MM-DD.
  - Validación y corrección de tipos de documentos fiscales.
  - Verificación de identificadores fiscales según reglas locales.
  - Validación de información del representante legal.

### 6. Finalización
- **Respuesta al Cliente**: Retorna el JSON estructurado, validado y normalizado.
- **Limpieza**: Elimina el archivo temporal del servidor.
- **Registro**: Guarda logs detallados del procesamiento para auditoría y diagnóstico.

## Características de Seguridad

- **Validación de Entradas**: Control riguroso de tipos de archivos aceptados.
- **Procesamiento Temporal**: Los archivos se eliminan después del procesamiento.
- **Control de Errores**: Manejo estructurado de excepciones con notificaciones vía webhook.
- **Logs Detallados**: Seguimiento completo de operaciones para auditoría.

## Extensibilidad

El sistema está diseñado para facilitar la extensión a nuevos países o tipos de documentos:

1. **Añadir Nuevo País**:
   - Crear una clase derivada de `CountryProcessor` en `country_processors/`.
   - Implementar reglas específicas en los métodos correspondientes.
   - Registrar el nuevo procesador en `country_processors/__init__.py`.

2. **Añadir Nuevos Validadores**:
   - Implementar nuevas funciones de validación en el directorio `validators/`.
   - Actualizar la lógica de post-procesamiento para incluir las nuevas validaciones.

## Contribuciones

Las contribuciones son bienvenidas. Para contribuir:

1. Haz fork del repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-caracteristica`)
3. Realiza tus cambios y asegúrate de incluir pruebas
4. Envía un pull request


---

© 2025 Mistral API | Versión documentación: 1.0 | Actualizado: 11 de abril de 2025