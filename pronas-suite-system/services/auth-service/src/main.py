from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from .security import create_access_token, verify_password

app = FastAPI(title="Serviço de Autenticação")

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # Em um caso real, você buscaria o usuário no banco de dados
    # Aqui, estamos usando um usuário mockado para simplicidade
    user_in_db = {"username": "user", "hashed_password": "$2b$12$EixZaYVK1e.JSqU7lR1dZ.eJz.ay2./d2B/2A.KjH2A.8nZk2KzKy"} # Senha é "password"

    if not user_in_db or not verify_password(form_data.password, user_in_db["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user_in_db["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/health")
def health_check():
    return {"status": "ok"}