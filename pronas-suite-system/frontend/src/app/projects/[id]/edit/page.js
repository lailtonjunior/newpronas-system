from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Simulação de um banco de dados em memória para simplicidade
fake_db = {
    "institutions": [
        {"id": 1, "name": "Hospital das Clínicas", "cnpj": "12.345.678/0001-99"},
        {"id": 2, "name": "AACD", "cnpj": "98.765.432/0001-11"},
    ]
}

app = FastAPI(
    title="Serviço de Instituições",
    description="Gerencia as instituições proponentes de projetos.",
    version="1.0.0"
)

class Institution(BaseModel):
    id: int
    name: str
    cnpj: str

@app.get("/institutions/", response_model=List[Institution])
def read_institutions():
    return fake_db["institutions"]

@app.get("/institutions/{institution_id}", response_model=Institution)
def read_institution(institution_id: int):
    institution = next((inst for inst in fake_db["institutions"] if inst["id"] == institution_id), None)
    if institution is None:
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    return institution

@app.get("/health")
def health_check():
    return {"status": "ok"}