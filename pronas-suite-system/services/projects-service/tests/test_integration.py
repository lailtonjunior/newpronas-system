import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app, get_db
from src.database import Base

# Configuração do banco de dados de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Sobrescrever a dependência do banco de dados para usar o de teste
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_and_read_project():
    # Criar um projeto
    response = client.post(
        "/projects/",
        json={"title": "Projeto Teste", "description": "Descrição Teste", "institution_id": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Projeto Teste"
    assert "id" in data
    project_id = data["id"]

    # Ler o projeto criado
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Projeto Teste"
    assert data["id"] == project_id