# Sistema de Gestão PRONAS/PCD com Inteligência Artificial

## 📋 Visão Geral

Sistema completo de gestão de projetos para o Programa Nacional de Apoio à Atenção da Saúde da Pessoa com Deficiência (PRONAS/PCD), utilizando Inteligência Artificial para otimizar a criação, análise e aprovação de projetos.

## 🚀 Funcionalidades Principais

- **Geração Automática de Projetos com IA**: OCR de documentos e geração inteligente
- **Detecção de Viés**: Análise de equidade em 4 dimensões
- **Sugestões em Tempo Real**: Feedback instantâneo durante preenchimento
- **Validação de Conformidade**: Verificação automática de diretrizes
- **Colaboração em Tempo Real**: WebSocket para edição colaborativa
- **Monitoramento Completo**: Métricas, logs e rastreamento distribuído

## 🛠️ Stack Tecnológica

### Backend
- **FastAPI** - APIs RESTful de alta performance
- **PostgreSQL** - Banco de dados principal
- **Redis** - Cache e filas
- **Elasticsearch** - Busca e indexação
- **MinIO** - Armazenamento de objetos (S3 compatible)

### IA/ML
- **PyTorch** - Deep Learning
- **Transformers** - BERT em português
- **XGBoost** - Modelos preditivos
- **Tesseract** - OCR
- **SpaCy** - Processamento de linguagem natural

### Infraestrutura
- **Docker** - Containerização
- **Kubernetes** - Orquestração
- **Terraform** - IaC
- **Kong** - API Gateway
- **Prometheus/Grafana** - Monitoramento

## 📦 Estrutura do Projeto
pronas-suite-system/
├── services/           # Microsserviços
│   ├── ai-service/    # Serviço de IA
│   ├── auth-service/  # Autenticação
│   ├── projects-service/
│   └── institutions-service/
├── frontend/          # Next.js Frontend
├── infrastructure/    # IaC e Kubernetes
├── docker-compose.yml
└── README.md

## 🔧 Instalação e Configuração

### Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- Node.js 18+ (para desenvolvimento frontend)
- Python 3.11+ (para desenvolvimento backend)
- GPU NVIDIA (opcional, para IA)

### Quick Start

1. Clone o repositório:
```bash
git clone https://github.com/your-org/pronas-suite-system.git
cd pronas-suite-system

Configure as variáveis de ambiente:

bashcp .env.example .env
# Edite .env com suas configurações

Inicie os serviços:

bashdocker-compose up -d

Acesse as aplicações:


Frontend: http://localhost:3000
API: http://localhost:8080
Grafana: http://localhost:3001
MinIO: http://localhost:9001

📊 Arquitetura
mermaidgraph TB
    subgraph Frontend
        UI[Next.js App]
    end
    
    subgraph Gateway
        KONG[Kong API Gateway]
    end
    
    subgraph Services
        AUTH[Auth Service]
        AI[AI Service]
        PROJ[Projects Service]
        INST[Institutions Service]
    end
    
    subgraph Data
        PG[(PostgreSQL)]
        REDIS[(Redis)]
        ES[(Elasticsearch)]
        S3[MinIO/S3]
    end
    
    UI --> KONG
    KONG --> AUTH
    KONG --> AI
    KONG --> PROJ
    KONG --> INST
    
    Services --> PG
    Services --> REDIS
    AI --> ES
    Services --> S3
🔐 Segurança

OAuth2 com JWT
MFA (Multi-Factor Authentication)
Criptografia AES-256
Rate limiting
CORS configurado
Logs de auditoria

📈 Monitoramento

Prometheus: Métricas
Grafana: Dashboards
Jaeger: Distributed tracing
ELK Stack: Logs centralizados

🧪 Testes
bash# Testes unitários
docker-compose exec ai-service pytest tests/unit

# Testes de integração
docker-compose exec ai-service pytest tests/integration

# Testes E2E
npm run test:e2e
📝 API Documentation
Após iniciar os serviços, acesse:

http://localhost:8001/docs - Auth Service
http://localhost:8002/docs - AI Service
http://localhost:8003/docs - Projects Service
http://localhost:8004/docs - Institutions Service

🚀 Deploy em Produção
AWS EKS
bash# Configure AWS CLI
aws configure

# Deploy infraestrutura
cd infrastructure/terraform
terraform init
terraform plan
terraform apply

# Deploy aplicações
kubectl apply -f infrastructure/k8s/
🤝 Contribuindo

Fork o projeto
Crie sua feature branch (git checkout -b feature/AmazingFeature)
Commit suas mudanças (git commit -m 'Add some AmazingFeature')
Push para a branch (git push origin feature/AmazingFeature)
Abra um Pull Request

📄 Licença
Este projeto está sob licença MIT. Veja LICENSE para mais detalhes.
👥 Equipe

DevOps: Infraestrutura e CI/CD
Backend: APIs e Microsserviços
AI/ML: Modelos e Processamento
Frontend: Interface e UX

📞 Suporte

Email: suporte@pronas-pcd.gov.br
Issues: GitHub Issues
Wiki: Documentação Completa

