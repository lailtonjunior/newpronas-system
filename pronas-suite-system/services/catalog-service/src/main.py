from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List

from . import crud, schemas
from .database import SessionLocal

app = FastAPI(
    title="Serviço de Catálogo",
    description="Fornece acesso a um banco de dados consolidado de equipamentos, materiais e serviços.",
    version="1.0.0"
)

# --- Dependência ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints ---

@app.get("/catalog/search", response_model=List[schemas.CatalogItem])
def search_catalog_items(q: str, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """
    Busca por itens no catálogo com base numa query de texto.
    Este endpoint é público para ser consumido por outros serviços.
    """
    if not q:
        return []
    items = crud.search_items(db, query=q, skip=skip, limit=limit)
    return items

@app.post("/catalog/ingest-renem-csv", status_code=status.HTTP_201_CREATED)
def upload_renem_csv(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """
    Endpoint para carregar e processar o arquivo CSV do RENEM.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a CSV.")
    
    result = crud.ingest_renem_data_from_csv(db, file.file)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["detail"])
        
    return result

@app.get("/health")
def health_check():
    """Endpoint de health check para o Kubernetes."""
    return {"status": "ok"}