# Sistema de Gestão PRONAS/PCD com Inteligência Artificial

## 📋 Visão Geral

Sistema completo de gestão de projetos para o Programa Nacional de Apoio à Atenção da Saúde da Pessoa com Deficiência (PRONAS/PCD), utilizando Inteligência Artificial para otimizar a criação, análise e aprovação de projetos.

## 🚀 Funcionalidades Principais

-   **Geração Automática de Projetos com IA**: Extração de dados de documentos com OCR e geração inteligente de propostas.
-   **Detecção de Viés**: Análise de equidade em 4 dimensões (institucional, geográfica, complexidade, orçamentária).
-   **Sugestões em Tempo Real**: Feedback instantâneo durante o preenchimento de propostas.
-   **Validação de Conformidade**: Verificação automática de conformidade com as diretrizes do programa.
-   **Colaboração em Tempo Real**: Edição colaborativa de documentos via WebSocket.
-   **Monitoramento Completo**: Métricas, logs e rastreamento distribuído para garantir a saúde do sistema.

## 🛠️ Stack Tecnológica

| Categoria       | Tecnologia                                                                                                |
| --------------- | --------------------------------------------------------------------------------------------------------- |
| **Backend** | FastAPI, PostgreSQL (com PostGIS), Redis, Elasticsearch, MinIO (S3 compatible)                            |
| **IA/ML** | PyTorch, Transformers (BERTimbau), XGBoost, Tesseract, SpaCy                                              |
| **Frontend** | Next.js, React, Tailwind CSS                                                                              |
| **Infra & DevOps** | Docker, Kubernetes, Terraform, Kong API Gateway, Prometheus, Grafana, Jaeger, GitHub Actions              |

## 📊 Arquitetura

```mermaid
graph TD
    subgraph "Usuário Final"
        UI[Next.js App]
    end

    subgraph "Gateway"
        KONG[Kong API Gateway]
    end

    subgraph "Microsserviços"
        AUTH[Auth Service]
        AI[AI Service]
        PROJ[Projects Service]
        INST[Institutions Service]
    end

    subgraph "Data Stores"
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

    PROJ --> AI

    AUTH --> PG
    PROJ --> PG
    INST --> PG

    AI --> ES
    PROJ --> ES

    AUTH --> REDIS
    PROJ --> REDIS

    AI --> S3
    PROJ --> S3
📦 Estrutura do Projeto
pronas-suite-system/
├── services/           # Microsserviços
│   ├── ai-service/
│   ├── auth-service/
│   ├── projects-service/
│   └── institutions-service/
├── frontend/           # Next.js Frontend
├── infrastructure/     # IaC (Terraform) e Configs (Kubernetes, Docker)
├── .github/            # Workflows de CI/CD
├── docker-compose.yml
└── README.md
🔧 Começando (Ambiente Local)
Pré-requisitos
Docker 20.10+ & Docker Compose 2.0+

Node.js 18+

Python 3.11+

Terraform 1.0+ (para deploy em nuvem)

make (opcional, para usar os comandos do Makefile)

Passos para Instalação
Clone o repositório:

Bash

git clone [https://github.com/your-org/pronas-suite-system.git](https://github.com/your-org/pronas-suite-system.git)
cd pronas-suite-system
Configure as variáveis de ambiente:

Bash

cp .env.example .env
Edite o arquivo .env com suas configurações locais. As senhas padrão já são seguras para desenvolvimento.

Inicie todos os serviços:

Bash

docker-compose up -d --build
Acesse as aplicações:

Frontend: http://localhost:3000

API Gateway: http://localhost:8080

Grafana: http://localhost:3001 (admin/senha do .env)

MinIO Console: http://localhost:9001 (usuário/senha do .env)

Jaeger UI: http://localhost:16686

📝 Documentação da API (Swagger)
Após iniciar os serviços, a documentação interativa estará disponível em:

Auth Service: http://localhost:8001/docs

AI Service: http://localhost:8002/docs

Projects Service: http://localhost:8003/docs

Institutions Service: http://localhost:8004/docs

🚀 Deploy em Produção (AWS EKS)
Configure suas credenciais da AWS:

Bash

aws configure
Inicialize e aplique a infraestrutura com Terraform:

Bash

cd infrastructure/terraform
terraform init
terraform plan
terraform apply
Aplique os manifestos do Kubernetes:

Bash

kubectl apply -f infrastructure/k8s/
🤝 Contribuindo
Adoramos contribuições! Por favor, leia o CONTRIBUTING.md para entender nossos padrões de código e o processo de pull request.

📄 Licença
Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

