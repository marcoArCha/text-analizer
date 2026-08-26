import os
from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Text Analyzer API")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite cualquier origen (localhost, GitHub Pages, etc.)
    allow_credentials=True,
    allow_methods=["*"],  # Permite GET, POST, OPTIONS, etc.
    allow_headers=["*"],  # Permite x-api-key, Content-Type, etc.
)

# Lee la variable de entorno configurada en AWS Lambda
API_KEY_SECRETA = os.getenv("API_KEY", "clave-fallback-local")

class TextoRequest(BaseModel):
    texto: str

@app.get("/")
def home():
    return {"mensaje": "API corriendo exitosamente en AWS Lambda"}

@app.post("/analizar")
def analizar_texto(body: TextoRequest, x_api_key: str = Header(None)):
    # Validación de seguridad (Login / Autenticación por API Key)
    if x_api_key != API_KEY_SECRETA:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida o no proporcionada"
        )
    
    contenido = body.texto.strip()
    palabras = len(contenido.split()) if contenido else 0
    caracteres = len(contenido)
    
    return {
        "status": "exito",
        "resultado": {
            "total_palabras": palabras,
            "total_caracteres": caracteres,
            "es_vacio": palabras == 0
        }
    }

# Manejador para AWS Lambda
handler = Mangum(app)