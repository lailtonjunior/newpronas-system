import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BiasDetector:
    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.bias_patterns = {}
        self.historical_data = []
        
    async def analyze(self, project_data: Dict) -> Dict:
        """Analisa projeto em busca de vieses"""
        analysis = {
            "bias_detected": False,
            "bias_score": 0.0,
            "patterns": [],
            "recommendations": [],
            "fairness_metrics": {}
        }
        
        # Detectar viés institucional
        institutional_bias = await self._detect_institutional_bias(project_data)
        if institutional_bias['detected']:
            analysis['patterns'].append(institutional_bias)
        
        # Detectar viés geográfico
        geographic_bias = await self._detect_geographic_bias(project_data)
        if geographic_bias['detected']:
            analysis['patterns'].append(geographic_bias)
        
        # Detectar viés de complexidade
        complexity_bias = await self._detect_complexity_bias(project_data)
        if complexity_bias['detected']:
            analysis['patterns'].append(complexity_bias)
        
        # Detectar viés orçamentário
        budget_bias = await self._detect_budget_bias(project_data)
        if budget_bias['detected']:
            analysis['patterns'].append(budget_bias)
        
        # Calcular score geral de viés
        if analysis['patterns']:
            analysis['bias_detected'] = True
            analysis['bias_score'] = np.mean([p['score'] for p in analysis['patterns']])
            analysis['recommendations'] = await self._generate_bias_recommendations(
                analysis['patterns']
            )
        
        # Métricas de equidade
        analysis['fairness_metrics'] = await self._calculate_fairness_metrics(project_data)
        
        return analysis
    
    async def _detect_institutional_bias(self, project_data: Dict) -> Dict:
        """Detecta viés relacionado ao tipo de instituição"""
        bias_result = {
            "type": "institutional",
            "detected": False,
            "score": 0.0,
            "description": ""
        }
        
        # Simular análise baseada em dados históricos
        institution_type = project_data.get('institution_type', '')
        
        # Padrões conhecidos de viés (baseado em dados históricos fictícios)
        approval_rates = {
            'university': 0.75,
            'hospital': 0.70,
            'ngo': 0.45,
            'private': 0.40
        }
        
        avg_approval = np.mean(list(approval_rates.values()))
        
        if institution_type in approval_rates:
            rate = approval_rates[institution_type]
            if abs(rate - avg_approval) > 0.15:
                bias_result['detected'] = True
                bias_result['score'] = abs(rate - avg_approval)
                bias_result['description'] = (
                    f"Instituições do tipo '{institution_type}' têm taxa de aprovação "
                    f"{'superior' if rate > avg_approval else 'inferior'} à média"
                )
        
        return bias_result
    
    async def _detect_geographic_bias(self, project_data: Dict) -> Dict:
        """Detecta viés geográfico"""
        bias_result = {
            "type": "geographic",
            "detected": False,
            "score": 0.0,
            "description": ""
        }
        
        # Análise por região
        region = project_data.get('region', '')
        
        regional_distribution = {
            'sudeste': 0.45,
            'sul': 0.25,
            'nordeste': 0.15,
            'centro-oeste': 0.10,
            'norte': 0.05
        }
        
        expected_distribution = 1 / len(regional_distribution)
        
        if region.lower() in regional_distribution:
            actual = regional_distribution[region.lower()]
            if abs(actual - expected_distribution) > 0.1:
                bias_result['detected'] = True
                bias_result['score'] = abs(actual - expected_distribution)
                bias_result['description'] = (
                    f"Região {region} está {'sobre' if actual > expected_distribution else 'sub'}"
                    f"-representada nos projetos aprovados"
                )
        
        return bias_result
    
    async def _detect_complexity_bias(self, project_data: Dict) -> Dict:
        """Detecta viés relacionado à complexidade do projeto"""
        bias_result = {
            "type": "complexity",
            "detected": False,
            "score": 0.0,
            "description": ""
        }
        
        # Calcular complexidade do projeto
        complexity_score = 0
        
        # Fatores de complexidade
        if len(project_data.get('objectives', {}).get('specific', [])) > 5:
            complexity_score += 1
        if project_data.get('budget', {}).get('total', 0) > 1000000:
            complexity_score += 1
        if len(project_data.get('timeline', [])) > 8:
            complexity_score += 1
        if len(project_data.get('team', [])) > 10:
            complexity_score += 1
        
        # Verificar se projetos complexos são favorecidos/desfavorecidos
        if complexity_score >= 3:
            bias_result['detected'] = True
            bias_result['score'] = 0.3
            bias_result['description'] = (
                "Projetos com alta complexidade tendem a ter tratamento diferenciado"
            )
        
        return bias_result
    
    async def _detect_budget_bias(self, project_data: Dict) -> Dict:
        """Detecta viés relacionado ao orçamento"""
        bias_result = {
            "type": "budget",
            "detected": False,
            "score": 0.0,
            "description": ""
        }
        
        budget = project_data.get('budget', {}).get('total', 0)
        
        # Faixas de orçamento e suas taxas de aprovação (simulado)
        budget_ranges = [
            (0, 100000, 0.35),
            (100000, 500000, 0.65),
            (500000, 1000000, 0.70),
            (1000000, float('inf'), 0.45)
        ]
        
        for min_val, max_val, approval_rate in budget_ranges:
            if min_val <= budget < max_val:
                if approval_rate < 0.4 or approval_rate > 0.6:
                    bias_result['detected'] = True
                    bias_result['score'] = abs(approval_rate - 0.5)
                    bias_result['description'] = (
                        f"Projetos na faixa de R$ {min_val:,.0f} a R$ {max_val:,.0f} "
                        f"têm taxa de aprovação {'alta' if approval_rate > 0.6 else 'baixa'}"
                    )
                break
        
        return bias_result
    
    async def _generate_bias_recommendations(self, patterns: List[Dict]) -> List[str]:
        """Gera recomendações para mitigar vieses detectados"""
        recommendations = []
        
        for pattern in patterns:
            if pattern['type'] == 'institutional':
                recommendations.append(
                    "Considere revisar os critérios de avaliação para garantir "
                    "equidade entre diferentes tipos de instituições"
                )
            elif pattern['type'] == 'geographic':
                recommendations.append(
                    "Ajuste o projeto para alinhar com a distribuição geográfica "
                    "esperada ou justifique a concentração regional"
                )
            elif pattern['type'] == 'complexity':
                recommendations.append(
                    "Simplifique a estrutura do projeto ou divida em fases menores "
                    "para melhorar as chances de aprovação"
                )
            elif pattern['type'] == 'budget':
                recommendations.append(
                    "Revise o orçamento para alinhar com faixas de maior probabilidade "
                    "de aprovação ou justifique detalhadamente os valores"
                )
        
        return recommendations
    
    async def _calculate_fairness_metrics(self, project_data: Dict) -> Dict:
        """Calcula métricas de equidade"""
        metrics = {
            "demographic_parity": 0.0,
            "equal_opportunity": 0.0,
            "disparate_impact": 0.0
        }
        
        # Simulação de cálculo de métricas
        # Em produção, isso seria baseado em dados reais
        
        # Paridade demográfica
        metrics['demographic_parity'] = np.random.uniform(0.7, 0.9)
        
        # Igualdade de oportunidade
        metrics['equal_opportunity'] = np.random.uniform(0.75, 0.95)
        
        # Impacto desproporcional
        metrics['disparate_impact'] = np.random.uniform(0.8, 1.2)
        
        return metrics
    
    async def learn_from_feedback(self, project_id: str, outcome: str, features: Dict):
        """Aprende com feedback para melhorar detecção de viés"""
        feedback_entry = {
            "project_id": project_id,
            "outcome": outcome,
            "features": features,
            "timestamp": datetime.now().isoformat()
        }
        
        self.historical_data.append(feedback_entry)
        
        # Retreinar modelo de detecção se houver dados suficientes
        if len(self.historical_data) >= 100:
            await self._retrain_bias_detector()
    
    async def _retrain_bias_detector(self):
        """Retreina detector de viés com novos dados"""
        logger.info("Retreinando detector de viés...")
        
        # Preparar dados
        df = pd.DataFrame(self.historical_data)
        
        # Extrair features
        features = []
        for entry in self.historical_data:
            feature_vector = [
                entry['features'].get('budget', 0),
                len(entry['features'].get('objectives', [])),
                len(entry['features'].get('team', [])),
                # ... mais features
            ]
            features.append(feature_vector)
        
        # Normalizar e treinar
        features_scaled = self.scaler.fit_transform(features)
        self.isolation_forest.fit(features_scaled)
        
        logger.info("Detector de viés retreinado com sucesso")