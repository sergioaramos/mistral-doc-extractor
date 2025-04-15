from fastapi import FastAPI
import uvicorn

from api.endpoints import router as document_router

app = FastAPI(
    title="Mistral API",
    version="1.0.0",
    description="API para procesamiento de documentos utilizando Mistral para OCR y generación de respuestas estructuradas."
)

# Incluir los endpoints definidos en endpoints.py con un prefijo para la versión o agrupación
app.include_router(document_router, prefix="/api")


if __name__ == "__main__":
    from config.settings import DEBUG, HOST, PORT
    # Ejecutar la aplicación con Uvicorn
    uvicorn.run("api.main:app", host=HOST, port=PORT, reload=True, debug=DEBUG)