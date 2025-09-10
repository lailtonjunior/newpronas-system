# Stage 1: Build com dependências de compilação
FROM python:3.11-slim as builder
WORKDIR /opt/venv
RUN python -m venv .
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Imagem final de produção
FROM python:3.11-slim as final
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Criar usuário não-root
RUN useradd -m -u 1000 appuser
USER appuser
WORKDIR /home/appuser/app

# Copiar apenas o ambiente virtual e o código fonte
COPY --from=builder /opt/venv /opt/venv
COPY ./src ./src
COPY ./alembic.ini .
COPY ./alembic ./alembic

ENV PATH="/opt/venv/bin:$PATH"
EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000"]