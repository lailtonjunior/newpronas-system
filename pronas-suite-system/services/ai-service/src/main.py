from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import uvicorn
from datetime import datetime
import asyncio
from contextlib import asynccontextmanager
import logging
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import PlainTextResponse

from .ocr_processor import OCRProcessor
from .nlp_engine import NLPEngine
from .ml_models import ProjectPredictor
from .document_generator import DocumentGenerator
from .bias_detector import BiasDetector
from .database import get_db, init_db
from .telemetry import setup_telemetry

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metrics
request_counter = Counter('ai_requests_total', 'Total AI requests', ['endpoint', 'status'])
processing_histogram = Histogram('ai_processing_duration_seconds', 'AI processing duration')

# Initialize components
ocr_processor = OCRProcessor()
nlp_engine = NLPEngine()
project_predictor = ProjectPredictor()
doc_generator = DocumentGenerator()
bias_detector = BiasDetector()

# Setup telemetry
tracer, meter, _ = setup_telemetry("ai-service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting AI Service...")
    await init_db()
    await nlp_engine.load_models()
    await project_predictor.load_models()
    logger.info("AI Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Service...")
    await nlp_engine.cleanup()
    logger.info("AI Service shut down successfully")

# Create FastAPI app
app = FastAPI(
    title="PRONAS/PCD AI Service",
    version="1.0.0",
    description="Serviço de Inteligência Artificial para gestão de projetos PRONAS/PCD",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ProjectRequest(BaseModel):
    institution_id: str
    project_type: str
    documents: List[str]
    initial_data: Dict[str, Any]
    guidelines: Optional[List[str]] = []
    use_ai: bool = True

class ProjectSuggestion(BaseModel):
    field: str
    current_value: str
    suggested_value: str
    confidence: float
    reasoning: str

class ConformityReport(BaseModel):
    compliant: bool
    score: float
    issues: List[Dict]
    recommendations: List[str]
    timestamp: datetime

class FeedbackRequest(BaseModel):
    project_id: str
    feedback_type: str
    data: Dict[str, Any]

# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check if models are loaded
        if not project_predictor.models_loaded:
            raise HTTPException(status_code=503, detail="Models not loaded")
        return {"status": "ready", "timestamp": datetime.now()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

# Main AI endpoints
@app.post("/api/v1/generate-project")
async def generate_project(
    request: ProjectRequest,
    background_tasks: BackgroundTasks,
    db: Any = Depends(get_db)
):
    """Generate project automatically using AI"""
    with tracer.start_as_current_span("generate_project"):
        try:
            request_counter.labels(endpoint="generate_project", status="started").inc()
            
            # Extract text from documents
            extracted_texts = []
            for doc_url in request.documents:
                text = await ocr_processor.extract_text(doc_url)
                extracted_texts.append(text)
            
            # Process guidelines with NLP
            processed_guidelines = await nlp_engine.process_guidelines(
                request.guidelines + extracted_texts
            )
            
            # Generate project structure
            with processing_histogram.time():
                project_structure = await project_predictor.generate_project_structure(
                    institution_id=request.institution_id,
                    project_type=request.project_type,
                    guidelines=processed_guidelines,
                    initial_data=request.initial_data
                )
            
            # Detect biases
            bias_analysis = await bias_detector.analyze(project_structure)
            
            # Generate documents
            documents = await doc_generator.generate_documents(
                project_structure,
                templates=["proposal", "budget", "workplan"]
            )
            
            # Store in database
            # await store_project(db, project_structure)
            
            # Schedule background tasks
            background_tasks.add_task(
                project_predictor.store_feedback,
                project_structure["id"],
                "generated",
                {"structure": project_structure}
            )
            
            request_counter.labels(endpoint="generate_project", status="success").inc()
            
            return {
                "project_id": project_structure["id"],
                "structure": project_structure,
                "documents": documents,
                "bias_analysis": bias_analysis,
                "confidence_score": project_structure.get("confidence", 0.85)
            }
            
        except Exception as e:
            request_counter.labels(endpoint="generate_project", status="error").inc()
            logger.error(f"Error generating project: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/suggest-improvements")
async def suggest_improvements(
    project_id: str,
    current_data: Dict[str, Any]
):
    """Suggest improvements in real-time"""
    with tracer.start_as_current_span("suggest_improvements"):
        try:
            suggestions = []
            
            # Find similar projects
            similar_projects = await project_predictor.find_similar_projects(current_data)
            
            # Generate suggestions for text fields
            for field, value in current_data.items():
                if field in ["justification", "objectives", "methodology"]:
                    suggestion = await nlp_engine.improve_text(
                        value,
                        context={"approved_projects": similar_projects},
                        field_type=field
                    )
                    
                    if suggestion["improved_text"] != value:
                        suggestions.append(ProjectSuggestion(
                            field=field,
                            current_value=value,
                            suggested_value=suggestion["improved_text"],
                            confidence=suggestion["confidence"],
                            reasoning=suggestion["reasoning"]
                        ))
            
            # Predict approval probability
            approval_probability = await project_predictor.predict_approval_probability(
                current_data
            )
            
            return {
                "suggestions": suggestions,
                "approval_probability": approval_probability,
                "similar_projects_count": len(similar_projects)
            }
            
        except Exception as e:
            logger.error(f"Error suggesting improvements: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/validate-conformity")
async def validate_conformity(
    project_id: str,
    project_data: Dict[str, Any]
):
    """Validate project conformity with guidelines"""
    with tracer.start_as_current_span("validate_conformity"):
        try:
            # Load current guidelines
            guidelines = await nlp_engine.load_current_guidelines()
            
            # Validate each section
            validation_results = []
            for section, content in project_data.items():
                if section in ["justification", "objectives", "methodology"]:
                    result = await nlp_engine.validate_section(
                        section=section,
                        content=content,
                        guidelines=guidelines
                    )
                    validation_results.append(result)
            
            # Calculate overall score
            if validation_results:
                overall_score = sum(r.get("score", 0) for r in validation_results) / len(validation_results)
            else:
                overall_score = 0.0
            
            # Identify issues
            issues = []
            for result in validation_results:
                if result.get("issues"):
                    issues.extend(result["issues"])
            
            # Generate recommendations
            recommendations = await project_predictor.generate_recommendations(
                validation_results,
                project_data
            )
            
            return ConformityReport(
                compliant=overall_score >= 0.8,
                score=overall_score,
                issues=issues,
                recommendations=recommendations,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error validating conformity: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/extract-text")
async def extract_text(file: UploadFile = File(...)):
    """Extract text from uploaded document"""
    try:
        # Save uploaded file temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Extract text
        text = await ocr_processor.extract_text(f"file://{tmp_file_path}")
        
        # Extract structured data
        structured_data = await ocr_processor.extract_structured_data(f"file://{tmp_file_path}")
        
        # Clean up
        os.unlink(tmp_file_path)
        
        return {
            "text": text,
            "structured_data": structured_data,
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"Error extracting text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/detect-bias")
async def detect_bias(project_data: Dict[str, Any]):
    """Detect bias in project"""
    try:
        analysis = await bias_detector.analyze(project_data)
        return analysis
    except Exception as e:
        logger.error(f"Error detecting bias: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/feedback")
async def process_feedback(
    feedback: FeedbackRequest,
    background_tasks: BackgroundTasks
):
    """Process feedback from analysts"""
    try:
        # Store feedback
        await project_predictor.store_feedback(
            project_id=feedback.project_id,
            feedback_type=feedback.feedback_type,
            data=feedback.data
        )
        
        # Learn from feedback for bias detection
        if feedback.feedback_type == "approval_decision":
            await bias_detector.learn_from_feedback(
                project_id=feedback.project_id,
                outcome=feedback.data.get("outcome"),
                features=feedback.data.get("features", {})
            )
        
        # Check if retraining is needed
        feedback_count = await project_predictor.get_feedback_count()
        if feedback_count >= 100:
            background_tasks.add_task(project_predictor.retrain_models)
        
        return {
            "status": "feedback_received",
            "feedback_count": feedback_count,
            "retraining_scheduled": feedback_count >= 100
        }
        
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/performance")
async def get_performance_metrics():
    """Get AI performance metrics"""
    try:
        # This would connect to your metrics store
        return {
            "accuracy": 0.87,
            "precision": 0.85,
            "recall": 0.89,
            "f1_score": 0.87,
            "total_projects_processed": 1250,
            "average_processing_time": 2.3,
            "bias_detection_rate": 0.15,
            "feedback_incorporated": 450,
            "last_retraining": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )