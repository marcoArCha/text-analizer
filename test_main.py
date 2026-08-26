from fastapi.testclient import TestClient
from main import app, API_KEY_SECRETA

client = TestClient(app)

def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "mensaje" in response.json()

def test_analizar_sin_api_key_falla():
    response = client.post("/analizar", json={"texto": "Hola mundo"})
    assert response.status_code == 401

def test_analizar_con_api_key_exitosa():
    headers = {"x-api-key": API_KEY_SECRETA}
    payload = {"texto": "Backend en AWS Lambda con FastAPI"}
    
    response = client.post("/analizar", json=payload, headers=headers)
    
    assert response.status_code == 200
    datos = response.json()
    assert datos["status"] == "exito"
    assert datos["resultado"]["total_palabras"] == 6