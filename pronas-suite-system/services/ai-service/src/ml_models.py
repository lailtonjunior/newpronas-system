import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
import xgboost as xgb
from typing import Dict, List, Optional, Tuple
import pickle
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ProjectPredictor:
    def __init__(self):
        self.approval_model = None
        self.quality_model = None
        self.timeline_model = None
        self.budget_model = None
        self.tokenizer = None
        self.bert_model = None
        self.models_loaded = False
        
    async def load_models(self):
        """Carrega modelos treinados"""
        try:
            # Carregar BERT para análise de texto
            self.tokenizer = AutoTokenizer.from_pretrained(
                'neuralmind/bert-base-portuguese-cased'
            )
            self.bert_model = AutoModelForSequenceClassification.from_pretrained(
                'neuralmind/bert-base-portuguese-cased',
                num_labels=2
            )
            
            # Carregar modelos de ML
            self.approval_model = await self._load_or_create_model(
                'approval_model.pkl',
                RandomForestClassifier(n_estimators=100, random_state=42)
            )
            
            self.quality_model = await self._load_or_create_model(
                'quality_model.pkl',
                GradientBoostingRegressor(n_estimators=100, random_state=42)
            )
            
            self.timeline_model = await self._load_or_create_model(
                'timeline_model.pkl',
                xgb.XGBRegressor(n_estimators=100, random_state=42)
            )
            
            self.budget_model = await self._load_or_create_model(
                'budget_model.pkl',
                xgb.XGBRegressor(n_estimators=100, random_state=42)
            )
            
            self.models_loaded = True
            logger.info("Modelos carregados com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelos: {str(e)}")
            raise
    
    async def _load_or_create_model(self, filename: str, default_model):
        """Carrega modelo salvo ou cria novo"""
        try:
            with open(f'/models/{filename}', 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            logger.info(f"Criando novo modelo: {filename}")
            return default_model
    
    async def generate_project_structure(
        self,
        institution_id: str,
        project_type: str,
        guidelines: Dict,
        initial_data: Dict
    ) -> Dict:
        """Gera estrutura completa do projeto"""
        
        # Analisar diretrizes
        requirements = guidelines.get('requirements', [])
        objectives = guidelines.get('objectives', [])
        
        # Gerar seções do projeto
        project_structure = {
            "id": f"proj_{datetime.now().timestamp()}",
            "institution_id": institution_id,
            "type": project_type,
            "title": await self._generate_title(initial_data, objectives),
            "justification": await self._generate_justification(
                initial_data, requirements
            ),
            "objectives": await self._generate_objectives(objectives),
            "methodology": await self._generate_methodology(
                project_type, requirements
            ),
            "expected_results": await self._generate_expected_results(
                objectives
            ),
            "budget": await self._generate_budget(project_type, initial_data),
            "timeline": await self._generate_timeline(project_type),
            "team": await self._generate_team(project_type),
            "resources": await self._generate_resources(project_type),
            "evaluation_metrics": await self._generate_metrics(objectives),
            "sustainability": await self._generate_sustainability_plan(),
            "risks": await self._analyze_risks(project_type),
            "confidence": 0.85,
            "generated_at": datetime.now().isoformat()
        }
        
        # Calcular score de qualidade
        quality_score = await self._calculate_quality_score(project_structure)
        project_structure["quality_score"] = quality_score
        
        return project_structure
    
    async def _generate_title(self, data: Dict, objectives: List) -> str:
        """Gera título do projeto"""
        base_title = data.get('title', '')
        
        if not base_title and objectives:
            # Gerar título baseado nos objetivos
            main_objective = objectives[0].get('text', '') if objectives else ''
            base_title = f"Projeto para {main_objective[:100]}"
        
        return base_title or "Projeto PRONAS/PCD"
    
    async def _generate_justification(
        self, data: Dict, requirements: List
    ) -> str:
        """Gera justificativa do projeto"""
        justification_template = """
        Este projeto se justifica pela necessidade de {objetivo_principal}, 
        considerando {contexto}. A relevância desta iniciativa está fundamentada 
        em {fundamentacao}, atendendo aos requisitos estabelecidos pelo PRONAS/PCD.
        
        {requisitos_atendidos}
        
        O impacto esperado inclui {impactos}, beneficiando diretamente 
        {beneficiarios} pessoas com deficiência.
        """
        
        # Preencher template com dados
        justification = justification_template.format(
            objetivo_principal=data.get('main_objective', 'desenvolver soluções inovadoras'),
            contexto=data.get('context', 'o cenário atual de inclusão'),
            fundamentacao=data.get('foundation', 'evidências científicas e demandas sociais'),
            requisitos_atendidos=self._format_requirements(requirements),
            impactos=data.get('impacts', 'melhorias significativas na qualidade de vida'),
            beneficiarios=data.get('beneficiaries', '1000')
        )
        
        return justification.strip()
    
    def _format_requirements(self, requirements: List) -> str:
        """Formata requisitos para inclusão na justificativa"""
        if not requirements:
            return ""
        
        req_texts = [f"- {req.get('text', '')}" for req in requirements[:5]]
        return "Este projeto atende aos seguintes requisitos:\n" + "\n".join(req_texts)
    
    async def _generate_objectives(self, objectives_data: List) -> Dict:
        """Gera objetivos do projeto"""
        general_objective = ""
        specific_objectives = []
        
        if objectives_data:
            # Objetivo geral baseado no primeiro objetivo das diretrizes
            general_objective = objectives_data[0].get('text', '')
            
            # Objetivos específicos
            for obj in objectives_data[1:4]:
                specific_objectives.append(obj.get('text', ''))
        
        # Adicionar objetivos padrão se necessário
        if not specific_objectives:
            specific_objectives = [
                "Desenvolver metodologia inovadora para atendimento",
                "Capacitar profissionais na área de atuação",
                "Estabelecer indicadores de impacto e qualidade",
                "Garantir sustentabilidade das ações propostas"
            ]
        
        return {
            "general": general_objective or "Promover a inclusão e qualidade de vida de pessoas com deficiência",
            "specific": specific_objectives
        }
    
    async def _generate_methodology(
        self, project_type: str, requirements: List
    ) -> Dict:
        """Gera metodologia do projeto"""
        methodologies = {
            "research": {
                "approach": "Pesquisa aplicada com abordagem quali-quantitativa",
                "phases": [
                    "Revisão sistemática da literatura",
                    "Definição de protocolo de pesquisa",
                    "Coleta de dados primários e secundários",
                    "Análise estatística e interpretação",
                    "Validação dos resultados",
                    "Disseminação do conhecimento"
                ],
                "techniques": [
                    "Análise bibliométrica",
                    "Surveys estruturados",
                    "Entrevistas semi-estruturadas",
                    "Análise de conteúdo",
                    "Modelagem estatística"
                ]
            },
            "development": {
                "approach": "Desenvolvimento iterativo e incremental",
                "phases": [
                    "Análise de requisitos",
                    "Design e prototipação",
                    "Desenvolvimento e implementação",
                    "Testes e validação",
                    "Implantação piloto",
                    "Avaliação e ajustes"
                ],
                "techniques": [
                    "Design thinking",
                    "Prototipação rápida",
                    "Testes de usabilidade",
                    "Metodologia ágil",
                    "Validação com usuários"
                ]
            },
            "training": {
                "approach": "Formação teórico-prática com metodologias ativas",
                "phases": [
                    "Diagnóstico de necessidades",
                    "Desenvolvimento curricular",
                    "Produção de material didático",
                    "Execução dos módulos",
                    "Avaliação de aprendizagem",
                    "Certificação e acompanhamento"
                ],
                "techniques": [
                    "Aprendizagem baseada em problemas",
                    "Estudos de caso",
                    "Simulações práticas",
                    "Mentoria e coaching",
                    "Avaliação por competências"
                ]
            }
        }
        
        return methodologies.get(project_type, methodologies["development"])
    
    async def _generate_budget(self, project_type: str, data: Dict) -> Dict:
        """Gera orçamento do projeto"""
        base_budget = data.get('budget', 500000)
        
        # Distribuição típica por categoria
        budget_distribution = {
            "human_resources": base_budget * 0.40,
            "equipment": base_budget * 0.20,
            "materials": base_budget * 0.15,
            "services": base_budget * 0.15,
            "indirect_costs": base_budget * 0.10
        }
        
        # Detalhamento por categoria
        budget_items = {
            "human_resources": [
                {"description": "Coordenador do Projeto", "value": base_budget * 0.15},
                {"description": "Pesquisadores", "value": base_budget * 0.15},
                {"description": "Equipe de Apoio", "value": base_budget * 0.10}
            ],
            "equipment": [
                {"description": "Equipamentos de Informática", "value": base_budget * 0.10},
                {"description": "Equipamentos Especializados", "value": base_budget * 0.10}
            ],
            "materials": [
                {"description": "Material de Consumo", "value": base_budget * 0.08},
                {"description": "Material Didático", "value": base_budget * 0.07}
            ],
            "services": [
                {"description": "Consultoria Especializada", "value": base_budget * 0.08},
                {"description": "Serviços de Terceiros", "value": base_budget * 0.07}
            ],
            "indirect_costs": [
                {"description": "Custos Administrativos", "value": base_budget * 0.10}
            ]
        }
        
        return {
            "total": base_budget,
            "distribution": budget_distribution,
            "items": budget_items,
            "currency": "BRL"
        }
    
    async def _generate_timeline(self, project_type: str) -> List[Dict]:
        """Gera cronograma do projeto"""
        timelines = {
            "research": 24,  # meses
            "development": 18,
            "training": 12
        }
        
        duration = timelines.get(project_type, 18)
        
        phases = []
        phase_duration = duration // 6  # 6 fases principais
        
        phase_names = [
            "Planejamento e Preparação",
            "Execução - Fase 1",
            "Execução - Fase 2", 
            "Validação e Testes",
            "Implementação Final",
            "Avaliação e Encerramento"
        ]
        
        for i, name in enumerate(phase_names):
            phases.append({
                "phase": name,
                "start_month": i * phase_duration + 1,
                "end_month": (i + 1) * phase_duration,
                "deliverables": [
                    f"Relatório de {name}",
                    f"Indicadores de {name}",
                    f"Documentação de {name}"
                ]
            })
        
        return phases
    
    async def _generate_team(self, project_type: str) -> List[Dict]:
        """Gera equipe do projeto"""
        team = [
            {
                "role": "Coordenador Geral",
                "quantity": 1,
                "hours_per_week": 20,
                "qualifications": "Doutorado na área, experiência em gestão de projetos"
            },
            {
                "role": "Pesquisador Senior",
                "quantity": 2,
                "hours_per_week": 30,
                "qualifications": "Mestrado na área, publicações relevantes"
            },
            {
                "role": "Pesquisador Junior",
                "quantity": 3,
                "hours_per_week": 40,
                "qualifications": "Graduação na área, experiência em pesquisa"
            },
            {
                "role": "Assistente de Pesquisa",
                "quantity": 2,
                "hours_per_week": 20,
                "qualifications": "Estudante de graduação ou pós-graduação"
            },
            {
                "role": "Especialista em Acessibilidade",
                "quantity": 1,
                "hours_per_week": 15,
                "qualifications": "Certificação em acessibilidade, experiência prática"
            }
        ]
        
        return team
    
    async def _generate_resources(self, project_type: str) -> Dict:
        """Gera recursos necessários"""
        return {
            "infrastructure": [
                "Espaço físico adequado e acessível",
                "Laboratório equipado",
                "Sala de reuniões",
                "Ambiente de testes"
            ],
            "technology": [
                "Computadores e notebooks",
                "Software especializado",
                "Plataforma de gestão de projetos",
                "Ferramentas de análise de dados"
            ],
            "partnerships": [
                "Instituições de ensino",
                "Organizações de pessoas com deficiência",
                "Órgãos governamentais",
                "Empresas parceiras"
            ]
        }
    
    async def _generate_expected_results(self, objectives: List) -> List[str]:
        """Gera resultados esperados"""
        results = [
            "Desenvolvimento de solução inovadora validada pelos usuários",
            "Publicação de artigos científicos em periódicos qualificados",
            "Formação de recursos humanos especializados",
            "Criação de protocolo replicável para outras instituições",
            "Melhoria mensurável na qualidade de vida dos beneficiários",
            "Estabelecimento de rede de colaboração permanente"
        ]
        
        return results
    
    async def _generate_metrics(self, objectives: List) -> List[Dict]:
        """Gera métricas de avaliação"""
        metrics = [
            {
                "indicator": "Número de beneficiários atendidos",
                "target": 1000,
                "measurement": "Registro de atendimentos",
                "frequency": "Mensal"
            },
            {
                "indicator": "Satisfação dos usuários",
                "target": 85,
                "measurement": "Pesquisa de satisfação (%)",
                "frequency": "Trimestral"
            },
            {
                "indicator": "Publicações científicas",
                "target": 5,
                "measurement": "Artigos publicados",
                "frequency": "Semestral"
            },
            {
                "indicator": "Profissionais capacitados",
                "target": 50,
                "measurement": "Certificados emitidos",
                "frequency": "Trimestral"
            },
            {
                "indicator": "Taxa de adesão ao protocolo",
                "target": 80,
                "measurement": "Percentual de adesão",
                "frequency": "Mensal"
            }
        ]
        
        return metrics
    
    async def _generate_sustainability_plan(self) -> Dict:
        """Gera plano de sustentabilidade"""
        return {
            "financial": [
                "Busca de financiamento continuado",
                "Parcerias público-privadas",
                "Geração de receita própria",
                "Captação de recursos via editais"
            ],
            "institutional": [
                "Integração com políticas públicas",
                "Institucionalização das práticas",
                "Formação de rede de apoio",
                "Documentação e transferência de conhecimento"
            ],
            "social": [
                "Engajamento da comunidade",
                "Formação de multiplicadores",
                "Advocacy e conscientização",
                "Empoderamento dos beneficiários"
            ]
        }
    
    async def _analyze_risks(self, project_type: str) -> List[Dict]:
        """Analisa riscos do projeto"""
        risks = [
            {
                "risk": "Dificuldade de recrutamento de participantes",
                "probability": "Média",
                "impact": "Alto",
                "mitigation": "Parcerias com organizações e divulgação ampla"
            },
            {
                "risk": "Atrasos no cronograma",
                "probability": "Média",
                "impact": "Médio",
                "mitigation": "Planejamento com margens de segurança e monitoramento contínuo"
            },
            {
                "risk": "Limitações orçamentárias",
                "probability": "Baixa",
                "impact": "Alto",
                "mitigation": "Gestão financeira rigorosa e busca de recursos complementares"
            },
            {
                "risk": "Resistência à mudança",
                "probability": "Média",
                "impact": "Médio",
                "mitigation": "Programa de sensibilização e capacitação gradual"
            },
            {
                "risk": "Questões éticas e regulatórias",
                "probability": "Baixa",
                "impact": "Alto",
                "mitigation": "Aprovação em comitê de ética e compliance regulatório"
            }
        ]
        
        return risks
    
    async def _calculate_quality_score(self, project: Dict) -> float:
        """Calcula score de qualidade do projeto"""
        scores = []
        
        # Completude
        required_fields = [
            'title', 'justification', 'objectives', 'methodology',
            'budget', 'timeline', 'expected_results'
        ]
        completeness = sum(1 for field in required_fields if project.get(field)) / len(required_fields)
        scores.append(completeness)
        
        # Detalhamento
        detail_score = 0
        if len(project.get('justification', '')) > 500:
            detail_score += 0.25
        if len(project.get('objectives', {}).get('specific', [])) >= 3:
            detail_score += 0.25
        if project.get('budget', {}).get('items'):
            detail_score += 0.25
        if len(project.get('timeline', [])) >= 4:
            detail_score += 0.25
        scores.append(detail_score)
        
        # Coerência (simplified)
        scores.append(0.85)  # Placeholder para análise mais complexa
        
        return np.mean(scores)
    
    async def find_similar_projects(self, project_data: Dict) -> List[Dict]:
        """Busca projetos similares no histórico"""
        # Simulação de busca em banco de dados
        # Em produção, isso seria uma query real ao banco
        similar_projects = [
            {
                "id": "proj_123",
                "title": "Projeto Similar 1",
                "justification": "Justificativa exemplar...",
                "approval_status": "approved",
                "similarity_score": 0.85
            },
            {
                "id": "proj_456",
                "title": "Projeto Similar 2",
                "objectives": {
                    "general": "Objetivo geral exemplar",
                    "specific": ["Obj 1", "Obj 2", "Obj 3"]
                },
                "approval_status": "approved",
                "similarity_score": 0.78
            }
        ]
        
        return similar_projects
    
    async def predict_approval_probability(self, project_data: Dict) -> float:
        """Prediz probabilidade de aprovação"""
        if not self.models_loaded:
            await self.load_models()
        
        # Extrair features do projeto
        features = await self._extract_features(project_data)
        
        # Fazer predição
        if self.approval_model:
            probability = self.approval_model.predict_proba([features])[0][1]
            return float(probability)
        
        return 0.75  # Default
    
    async def _extract_features(self, project_data: Dict) -> np.ndarray:
        """Extrai features para os modelos"""
        features = []
        
        # Features textuais
        features.append(len(project_data.get('justification', '')))
        features.append(len(project_data.get('objectives', {}).get('specific', [])))
        
        # Features numéricas
        features.append(project_data.get('budget', {}).get('total', 0))
        features.append(len(project_data.get('timeline', [])))
        features.append(len(project_data.get('team', [])))
        
        # Features categóricas (encoded)
        project_type = project_data.get('type', 'development')
        type_encoding = {'research': 0, 'development': 1, 'training': 2}
        features.append(type_encoding.get(project_type, 1))
        
        return np.array(features)
    
    async def generate_recommendations(
        self, validation_results: List[Dict], project_data: Dict
    ) -> List[str]:
        """Gera recomendações para melhorar o projeto"""
        recommendations = []
        
        for result in validation_results:
            if result.get('score', 1) < 0.7:
                section = result.get('section', 'seção')
                recommendations.append(
                    f"Revisar e expandir a {section} para atender melhor às diretrizes"
                )
        
        # Recomendações baseadas em projetos similares aprovados
        similar_projects = await self.find_similar_projects(project_data)
        if similar_projects:
            recommendations.append(
                "Considerar estrutura similar aos projetos aprovados anteriormente"
            )
        
        # Recomendações específicas
        if len(project_data.get('justification', '')) < 1000:
            recommendations.append(
                "Expandir a justificativa com mais evidências e fundamentação teórica"
            )
        
        if not project_data.get('evaluation_metrics'):
            recommendations.append(
                "Incluir métricas claras de avaliação e indicadores de sucesso"
            )
        
        return recommendations
    
    async def store_feedback(
        self, project_id: str, feedback_type: str, data: Dict
    ):
        """Armazena feedback para retraining"""
        feedback_entry = {
            "project_id": project_id,
            "type": feedback_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Salvar em banco de dados ou sistema de filas
        # Implementação real dependeria da infraestrutura
        logger.info(f"Feedback armazenado: {feedback_entry}")
    
    async def get_feedback_count(self) -> int:
        """Retorna contagem de feedbacks pendentes"""
        # Em produção, isso seria uma query ao banco
        return 42
    
    async def retrain_models(self):
        """Retreina modelos com novos dados"""
        logger.info("Iniciando retraining dos modelos...")
        
        # 1. Coletar dados de feedback
        # 2. Preparar dataset de treino
        # 3. Retreinar modelos
        # 4. Validar performance
        # 5. Deploy se melhor que modelo atual
        
        await asyncio.sleep(1)  # Simulação
        logger.info("Retraining concluído")