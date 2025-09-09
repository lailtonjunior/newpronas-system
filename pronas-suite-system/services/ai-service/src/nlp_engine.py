import torch
from transformers import AutoTokenizer, AutoModel, pipeline
from sentence_transformers import SentenceTransformer
import spacy
from typing import List, Dict, Optional, Any
import numpy as np
import asyncio
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class NLPEngine:
    def __init__(self):
        self.bert_model = None
        self.tokenizer = None
        self.sentence_model = None
        self.nlp = None
        self.sentiment_analyzer = None
        self.summarizer = None
        self.guidelines_cache = {}
        
    async def load_models(self):
        """Load NLP models"""
        try:
            logger.info("Loading NLP models...")
            
            # BERT for Portuguese
            self.tokenizer = AutoTokenizer.from_pretrained(
                'neuralmind/bert-large-portuguese-cased'
            )
            self.bert_model = AutoModel.from_pretrained(
                'neuralmind/bert-large-portuguese-cased'
            )
            
            # Sentence embeddings
            self.sentence_model = SentenceTransformer(
                'rufimelo/Legal-BERTimbau-base'
            )
            
            # SpaCy for text processing
            self.nlp = spacy.load("pt_core_news_lg")
            
            # Additional pipelines
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment"
            )
            
            self.summarizer = pipeline(
                "summarization",
                model="unicamp-dl/ptt5-base-portuguese-vocab"
            )
            
            logger.info("NLP models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading NLP models: {str(e)}")
            raise
    
    async def process_guidelines(self, texts: List[str]) -> Dict[str, Any]:
        """Process guidelines and extract structured information"""
        processed = {
            "requirements": [],
            "objectives": [],
            "restrictions": [],
            "criteria": [],
            "keywords": set(),
            "entities": []
        }
        
        for text in texts:
            # Process with SpaCy
            doc = self.nlp(text)
            
            # Extract entities
            for ent in doc.ents:
                processed["entities"].append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                })
            
            # Extract requirements, objectives, etc.
            for sent in doc.sents:
                sent_text = sent.text.strip()
                sent_lower = sent_text.lower()
                
                # Create embedding for semantic analysis
                embedding = self.sentence_model.encode(sent_text)
                
                # Classify sentence type
                if self._is_requirement(sent_lower):
                    processed["requirements"].append({
                        "text": sent_text,
                        "entities": [ent.text for ent in sent.ents],
                        "embedding": embedding.tolist(),
                        "mandatory": "deve" in sent_lower or "obrigatório" in sent_lower
                    })
                
                elif self._is_objective(sent_lower):
                    processed["objectives"].append({
                        "text": sent_text,
                        "embedding": embedding.tolist(),
                        "priority": self._extract_priority(sent_text)
                    })
                
                elif self._is_restriction(sent_lower):
                    processed["restrictions"].append({
                        "text": sent_text,
                        "type": self._classify_restriction(sent_text),
                        "severity": "high" if "vedado" in sent_lower else "medium"
                    })
                
                # Extract keywords
                for token in sent:
                    if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 3:
                        processed["keywords"].add(token.lemma_)
        
        processed["keywords"] = list(processed["keywords"])
        return processed
    
    def _is_requirement(self, text: str) -> bool:
        """Check if text is a requirement"""
        requirement_keywords = [
            "deve", "deverá", "obrigatório", "necessário", 
            "requisito", "exigido", "precisa", "essencial"
        ]
        return any(keyword in text for keyword in requirement_keywords)
    
    def _is_objective(self, text: str) -> bool:
        """Check if text is an objective"""
        objective_keywords = [
            "objetivo", "meta", "finalidade", "propósito",
            "visa", "busca", "pretende", "almeja"
        ]
        return any(keyword in text for keyword in objective_keywords)
    
    def _is_restriction(self, text: str) -> bool:
        """Check if text is a restriction"""
        restriction_keywords = [
            "não pode", "proibido", "vedado", "limitado",
            "restrição", "impedido", "exceto", "salvo"
        ]
        return any(keyword in text for keyword in restriction_keywords)
    
    def _classify_restriction(self, text: str) -> str:
        """Classify type of restriction"""
        if "orçamento" in text.lower() or "valor" in text.lower():
            return "budget"
        elif "prazo" in text.lower() or "tempo" in text.lower():
            return "timeline"
        elif "equipe" in text.lower() or "profissional" in text.lower():
            return "team"
        else:
            return "general"
    
    def _extract_priority(self, text: str) -> str:
        """Extract priority level from text"""
        high_priority = ["principal", "fundamental", "prioritário", "crítico"]
        low_priority = ["secundário", "opcional", "desejável"]
        
        text_lower = text.lower()
        if any(word in text_lower for word in high_priority):
            return "high"
        elif any(word in text_lower for word in low_priority):
            return "low"
        return "medium"
    
    async def improve_text(
        self, 
        text: str, 
        context: Dict[str, Any], 
        field_type: str
    ) -> Dict[str, Any]:
        """Improve text based on context and approved examples"""
        try:
            # Get current text embedding
            current_embedding = self.sentence_model.encode(text)
            
            # Find similar approved texts
            approved_examples = context.get("approved_projects", [])
            improvements = []
            
            for example in approved_examples:
                if field_type in example:
                    example_text = example[field_type]
                    example_embedding = self.sentence_model.encode(example_text)
                    
                    # Calculate similarity
                    similarity = cosine_similarity(
                        [current_embedding], 
                        [example_embedding]
                    )[0][0]
                    
                    if 0.5 < similarity < 0.95:  # Similar but not identical
                        improvements.append({
                            "text": example_text,
                            "similarity": float(similarity),
                            "project_id": example.get("id")
                        })
            
            if improvements:
                # Sort by similarity
                improvements.sort(key=lambda x: x["similarity"], reverse=True)
                best_improvement = improvements[0]
                
                # Merge texts intelligently
                improved_text = await self._merge_texts(
                    original=text,
                    reference=best_improvement["text"],
                    field_type=field_type
                )
                
                return {
                    "improved_text": improved_text,
                    "confidence": best_improvement["similarity"],
                    "reasoning": f"Baseado em projeto aprovado similar (ID: {best_improvement['project_id']}) com {best_improvement['similarity']:.2%} de similaridade",
                    "changes_made": self._identify_changes(text, improved_text)
                }
            
            # If no good examples, try to enhance with general improvements
            enhanced_text = await self._enhance_text(text, field_type)
            
            return {
                "improved_text": enhanced_text,
                "confidence": 0.6,
                "reasoning": "Melhorias gerais aplicadas baseadas em boas práticas",
                "changes_made": self._identify_changes(text, enhanced_text)
            }
            
        except Exception as e:
            logger.error(f"Error improving text: {str(e)}")
            return {
                "improved_text": text,
                "confidence": 0.0,
                "reasoning": "Erro ao processar melhorias",
                "changes_made": []
            }
    
    async def _merge_texts(
        self, 
        original: str, 
        reference: str, 
        field_type: str
    ) -> str:
        """Intelligently merge original text with reference"""
        # Parse both texts
        doc_original = self.nlp(original)
        doc_reference = self.nlp(reference)
        
        # Extract key sentences from both
        original_sents = [sent.text for sent in doc_original.sents]
        reference_sents = [sent.text for sent in doc_reference.sents]
        
        # Keep unique valuable content from original
        merged_sentences = []
        
        # Add strong opening from reference if better
        if reference_sents and field_type == "justification":
            merged_sentences.append(reference_sents[0])
        
        # Add unique content from original
        for sent in original_sents:
            sent_embedding = self.sentence_model.encode(sent)
            is_unique = True
            
            for ref_sent in reference_sents:
                ref_embedding = self.sentence_model.encode(ref_sent)
                similarity = cosine_similarity(
                    [sent_embedding], 
                    [ref_embedding]
                )[0][0]
                
                if similarity > 0.85:  # Too similar
                    is_unique = False
                    break
            
            if is_unique and len(sent.split()) > 5:  # Keep unique substantial sentences
                merged_sentences.append(sent)
        
        # Add strong conclusions from reference
        if reference_sents and field_type in ["justification", "objectives"]:
            merged_sentences.append(reference_sents[-1])
        
        # Join and clean up
        merged_text = " ".join(merged_sentences)
        merged_text = self._clean_text(merged_text)
        
        return merged_text
    
    async def _enhance_text(self, text: str, field_type: str) -> str:
        """Enhance text with general improvements"""
        enhancements = {
            "justification": [
                "considerando as diretrizes do PRONAS/PCD",
                "atendendo às necessidades da população com deficiência",
                "promovendo inclusão e acessibilidade"
            ],
            "objectives": [
                "de forma mensurável e alcançável",
                "com indicadores claros de sucesso",
                "alinhado às políticas públicas vigentes"
            ],
            "methodology": [
                "seguindo metodologia científica rigorosa",
                "com validação por especialistas",
                "garantindo replicabilidade e sustentabilidade"
            ]
        }
        
        # Add relevant enhancements
        enhanced = text
        if field_type in enhancements:
            for enhancement in enhancements[field_type]:
                if enhancement not in text.lower():
                    enhanced += f", {enhancement}"
        
        return self._clean_text(enhanced)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra spaces
        text = " ".join(text.split())
        
        # Fix punctuation
        text = text.replace(" ,", ",").replace(" .", ".")
        text = text.replace(",,", ",").replace("..", ".")
        
        # Ensure proper capitalization
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        
        # Ensure ends with period
        if text and text[-1] not in ".!?":
            text += "."
        
        return text
    
    def _identify_changes(self, original: str, improved: str) -> List[str]:
        """Identify what changes were made"""
        changes = []
        
        # Compare lengths
        len_diff = len(improved.split()) - len(original.split())
        if len_diff > 10:
            changes.append(f"Texto expandido em {len_diff} palavras")
        elif len_diff < -10:
            changes.append(f"Texto reduzido em {abs(len_diff)} palavras")
        
        # Check for new keywords
        original_lower = original.lower()
        improved_lower = improved.lower()
        
        keywords_added = []
        for keyword in ["objetivo", "meta", "requisito", "diretriz", "inclusão"]:
            if keyword in improved_lower and keyword not in original_lower:
                keywords_added.append(keyword)
        
        if keywords_added:
            changes.append(f"Adicionados termos-chave: {', '.join(keywords_added)}")
        
        return changes
    
    async def validate_section(
        self, 
        section: str, 
        content: str, 
        guidelines: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate a section against guidelines"""
        validation_result = {
            "section": section,
            "score": 0.0,
            "issues": [],
            "suggestions": []
        }
        
        # Check minimum length
        word_count = len(content.split())
        min_lengths = {
            "justification": 200,
            "objectives": 50,
            "methodology": 150
        }
        
        if section in min_lengths and word_count < min_lengths[section]:
            validation_result["issues"].append({
                "type": "length",
                "message": f"{section} deve ter pelo menos {min_lengths[section]} palavras (atual: {word_count})"
            })
            validation_result["score"] -= 0.2
        
        # Check for required keywords
        required_keywords = guidelines.get("keywords", [])
        content_lower = content.lower()
        missing_keywords = []
        
        for keyword in required_keywords[:10]:  # Check top 10 keywords
            if keyword.lower() not in content_lower:
                missing_keywords.append(keyword)
        
        if missing_keywords:
            validation_result["issues"].append({
                "type": "keywords",
                "message": f"Palavras-chave ausentes: {', '.join(missing_keywords[:5])}"
            })
            validation_result["score"] -= 0.1 * len(missing_keywords)
        
        # Check sentiment and tone
        sentiment = self.sentiment_analyzer(content[:512])[0]  # Limit for model
        if sentiment["label"] in ["1 star", "2 stars"]:
            validation_result["issues"].append({
                "type": "tone",
                "message": "Tom do texto pode ser melhorado para ser mais positivo e construtivo"
            })
            validation_result["score"] -= 0.1
        
        # Calculate final score (0-1 range)
        validation_result["score"] = max(0, min(1, 1 + validation_result["score"]))
        
        # Generate suggestions based on issues
        for issue in validation_result["issues"]:
            if issue["type"] == "length":
                validation_result["suggestions"].append(
                    f"Expanda {section} com mais detalhes e justificativas"
                )
            elif issue["type"] == "keywords":
                validation_result["suggestions"].append(
                    f"Inclua termos relevantes como: {', '.join(missing_keywords[:3])}"
                )
        
        return validation_result
    
    async def load_current_guidelines(self) -> Dict[str, Any]:
        """Load current PRONAS/PCD guidelines"""
        # Check cache first
        if "current" in self.guidelines_cache:
            return self.guidelines_cache["current"]
        
        # In production, this would load from database or external source
        guidelines = {
            "version": "2024.1",
            "keywords": [
                "inclusão", "acessibilidade", "deficiência", "reabilitação",
                "tecnologia assistiva", "autonomia", "qualidade de vida",
                "direitos", "cidadania", "participação social"
            ],
            "requirements": [
                "Atender pessoas com deficiência",
                "Seguir normas de acessibilidade",
                "Apresentar indicadores mensuráveis",
                "Garantir sustentabilidade do projeto"
            ],
            "restrictions": [
                "Não discriminar por tipo de deficiência",
                "Não exceder limite orçamentário estabelecido",
                "Não duplicar serviços existentes"
            ]
        }
        
        self.guidelines_cache["current"] = guidelines
        return guidelines
    
    async def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text"""
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "type": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        
        return entities
    
    async def summarize_text(self, text: str, max_length: int = 150) -> str:
        """Summarize long text"""
        try:
            if len(text.split()) < max_length:
                return text
            
            summary = self.summarizer(
                text,
                max_length=max_length,
                min_length=50,
                do_sample=False
            )
            
            return summary[0]["summary_text"]
        except Exception as e:
            logger.error(f"Error summarizing text: {str(e)}")
            # Fallback to simple truncation
            words = text.split()[:max_length]
            return " ".join(words) + "..."
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        try:
            result = self.sentiment_analyzer(text[:512])
            return {
                "label": result[0]["label"],
                "score": result[0]["score"]
            }
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {"label": "neutral", "score": 0.5}
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up NLP engine resources")
        # Clear cache
        self.guidelines_cache.clear()
        # Clear models from memory if needed
        if self.bert_model:
            del self.bert_model
        if self.sentence_model:
            del self.sentence_model