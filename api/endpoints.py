from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from pathlib import Path
import os
import json

from services.document_processor import DocumentProcessor
from services.webhook import WebhookService
from config.settings import API_KEY
from utils.logger import logger

router = APIRouter()
webhook_service = WebhookService()


def get_document_processor() -> DocumentProcessor:
    """Función de inyección de dependencias para obtener la instancia de DocumentProcessor."""
    return DocumentProcessor(api_key=API_KEY)


@router.post("/upload-document/")
async def upload_document(
    file: UploadFile = File(...), 
    document_processor: DocumentProcessor = Depends(get_document_processor)
):
    """Endpoint para la carga y procesamiento de documentos (imágenes o PDF)."""
    # Guardar el archivo en un directorio temporal
    tmp_dir = Path("/tmp")
    tmp_dir.mkdir(exist_ok=True)
    file_path = tmp_dir / file.filename

    # Validar el tipo de archivo
    file_ext = file_path.suffix.lower()
    if file_ext not in ['.jpg', '.jpeg', '.png', '.pdf']:
        logger.error(f"Unsupported file type: {file_ext}")
        webhook_service.send_to_webhook(f"Unsupported file type: {file_ext}")
        raise HTTPException(status_code=415, detail="Unsupported file type. Only PDFs and images are allowed.")

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        webhook_service.send_to_webhook(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving file: {e}")

    try:
        response = document_processor.process_document(str(file_path))
        response_json = json.loads(response)  # Convertir la cadena JSON a un objeto JSON
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        webhook_service.send_to_webhook(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {e}")

    # Eliminar el archivo temporal después del procesamiento
    try:
        os.remove(file_path)
    except Exception as e:
        logger.warning(f"Error deleting file: {e}")
        # Se podría registrar el error, pero no interrumpe la respuesta
        pass

    return JSONResponse(content=response_json)


@router.get("/health")
async def health():
    return {"status": "ok"}