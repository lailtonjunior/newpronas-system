from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import pytesseract
from pdf2image import convert_from_path
import spacy
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega o modelo de NLP do spaCy (necessário baixar: python -m spacy download pt_core_news_sm)
try:
    nlp = spacy.load("pt_core_news_sm")
except OSError:
    logger.warning("Modelo 'pt_core_news_sm' não encontrado. Baixe com 'python -m spacy download pt_core_news_sm'.")
    nlp = None

app = FastAPI(
    title="Serviço de IA - PRONAS/PCD",
    description="Serviço para OCR, análise de texto e detecção de viés.",
    version="0.1.0",
)

class AnalysisResult(BaseModel):
    filename: str
    extracted_text: str
    compliance_score: float
    bias_warnings: list[str]

def perform_ocr(file_path: str) -> str:
    """Extrai texto de um arquivo PDF usando Tesseract."""
    try:
        images = convert_from_path(file_path)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image, lang='por')
        return text
    except Exception as e:
        logger.error(f"Erro no OCR: {e}")
        raise HTTPException(status_code=500, detail="Falha ao processar o PDF com OCR.")

def analyze_bias(text: str) -> list[str]:
    """Função placeholder para detectar viés no texto do projeto."""
    warnings = []
    # Lógica de exemplo: verifica se termos sensíveis são mencionados sem contexto adequado
    sensitive_terms = ["apenas", "somente para", "exclusivamente"]
    for term in sensitive_terms:
        if term in text.lower():
            warnings.append(f"Potencial viés detectado: uso do termo '{term}'. Verifique o contexto de elegibilidade.")
    return warnings

@app.post("/analyze-document", response_model=AnalysisResult)
async def analyze_document(file: UploadFile = File(...)):
    """
    Recebe um documento PDF, extrai o texto com OCR, e realiza uma análise preliminar.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido. Apenas PDF é aceito.")

    # Salva o arquivo temporariamente para processamento
    temp_file_path = f"/tmp/{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    logger.info(f"Iniciando análise para o arquivo: {file.filename}")

    # 1. Extração de texto com OCR
    extracted_text = perform_ocr(temp_file_path)
    if not extracted_text:
        raise HTTPException(status_code=422, detail="Não foi possível extrair texto do documento.")

    # 2. Análise de Viés (exemplo)
    bias_warnings = analyze_bias(extracted_text)

    # 3. Análise de conformidade (exemplo)
    # Aqui entraria a lógica com XGBoost ou outro modelo para prever a viabilidade
    compliance_score = 0.75  # Placeholder

    logger.info(f"Análise concluída para {file.filename}")

    return AnalysisResult(
        filename=file.filename,
        extracted_text=extracted_text[:2000],  # Retorna apenas uma parte para não sobrecarregar
        compliance_score=compliance_score,
        bias_warnings=bias_warnings,
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}
