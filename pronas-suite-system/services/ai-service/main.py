from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from typing import Dict, Any

from src.ocr_processor import OCRProcessor
from src.bias_detector import BiasDetector
from src.document_generator import DocumentGenerator
from src.ml_models import ProjectPredictor
from src.nlp_engine import NLPEngine

app = FastAPI(
    title="Serviço de IA - PRONAS/PCD",
    description="Serviço para OCR, análise de texto, detecção de viés e geração de documentos.",
    version="1.0.0",
)

# Injeção de Dependências (melhor para testes e manutenção)
def get_ocr_processor():
    return OCRProcessor()

def get_bias_detector():
    return BiasDetector()

def get_doc_generator():
    return DocumentGenerator()

def get_ml_predictor():
    return ProjectPredictor()

def get_nlp_engine():
    return NLPEngine()

@app.post("/analyze-document", summary="Analisa um documento PDF")
async def analyze_document(
    file: UploadFile = File(...),
    ocr: OCRProcessor = Depends(get_ocr_processor),
    nlp: NLPEngine = Depends(get_nlp_engine),
    bias: BiasDetector = Depends(get_bias_detector)
):
    """
    Recebe um documento PDF, extrai o texto com OCR, e realiza uma análise preliminar
    de viés e conformidade.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Formato de arquivo inválido. Apenas PDF é aceito.")

    contents = await file.read()
    extracted_text = await ocr.extract_text_from_pdf_bytes(contents)
    if not extracted_text:
        raise HTTPException(status_code=422, detail="Não foi possível extrair texto do documento.")

    # Simulação de dados do projeto extraídos do texto
    project_data_simulation = {"text": extracted_text, "region": "sudeste"}
    bias_analysis = await bias.analyze(project_data_simulation)

    return {
        "filename": file.filename,
        "extracted_text_snippet": extracted_text[:1000] + "...",
        "bias_analysis": bias_analysis,
    }

@app.post("/generate-documents", summary="Gera documentos de projeto")
async def generate_documents(
    project_data: Dict[str, Any],
    doc_gen: DocumentGenerator = Depends(get_doc_generator)
):
    """
    Gera documentos como proposta e orçamento com base nos dados do projeto.
    """
    generated_files = await doc_gen.generate_documents(project_data, ["proposal_docx", "budget_xlsx"])
    return {"message": "Documentos gerados com sucesso", "files": generated_files}


@app.get("/health", summary="Verifica a saúde do serviço")
def health_check():
    """Endpoint de health check."""
    return {"status": "ok"}