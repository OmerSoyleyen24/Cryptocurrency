```markdown
# Enterprise-Grade FinTech & AI Analytics Platform

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-005571?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-Vite-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Kafka](https://img.shields.io/badge/Apache_Kafka-Event_Driven-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-FF5722?style=for-the-badge&logo=qdrant&logoColor=white)

An enterprise-ready, event-driven distributed platform designed for real-time cryptocurrency analytics, multi-model Deep Learning market prediction (LSTM/GRU/Dense), and semantic RAG (Retrieval-Augmented Generation) news insights.

Engineered from scratch to demonstrate Production-Ready Software Engineering, Scalable Microservices Topology, Event Streaming, and Automated MLOps Benchmarking.

---

## 💡 Engineering Motivation & Problem Statement

Financial technology platforms require high throughput, fault isolation, and low-latency algorithmic responses. Traditional monolithic approaches to time-series machine learning often suffer from blocking execution and tight coupling.

This platform solves these domain challenges through:
* **Asynchronous Event Streaming:** Decoupling high-overhead deep learning tasks from web servers via Apache Kafka.
* **Dynamic MLOps Model Selection:** Automatically benchmarking deep learning models in real-time to prevent model drift and vanishing gradients.
* **API Gateway & Edge Isolation:** Protecting internal domain services behind a unified, rate-limited, reverse-proxy gateway.

---

## 🏗 System Architecture & Distributed Design

The ecosystem is split into domain-driven, containerized microservices operating over a private overlay network (`crypto-network`).

```text
                         ┌───────────────────────────────────────────┐
                         │   React + Vite Frontend (localhost:5173)  │
                         └─────────────────────┬─────────────────────┘
                                               │
                                       (HTTP REST / JSON)
                                               ▼
                         ┌───────────────────────────────────────────┐
                         │   API Gateway Service (localhost:8000)    │
                         └─────────────────────┬─────────────────────┘
                                               │
         ┌─────────────────────────────────────┼─────────────────────────────────────┐
         │ Proxy: /api/auth/*                  │ Proxy: /api/ml/*                    │ Proxy: /api/rag/*
         ▼                                     ▼                                     ▼
┌──────────────────┐                  ┌──────────────────┐                  ┌──────────────────┐
│  Auth Service    │                  │  ML Engine Sec.  │                  │ RAG News Service │
│ (localhost:8001) │                  │ (localhost:8002) │                  │ (localhost:8003) │
└────────┬─────────┘                  └────────┬─────────┘                  └────────┬─────────┘
         │                                     │                                     │
   ┌─────┴─────┐                         ┌─────┴─────┐                         ┌─────┴─────┐
   │  MySQL    │                         │   Kafka   │                         │  Qdrant   │
   │  Redis    │                         │ Zookeeper │                         │ Vector DB │
   └───────────┘                         └───────────┘                         └───────────┘

```

### 🧩 Core Domain Microservices:

* **API Gateway (:8000):** Single point of entry handling request routing, payload proxying, and service abstraction.
* **Auth & User Management (:8001):** Manages identity, JWT sessions, and relational user crypto lists backed by MySQL 8.0 and Redis for session/query caching.
* **ML Engine Service (:8002):** Ingests live market data from exchange APIs, computes 14+ technical indicators using TA-Lib, executes model training/evaluations, and streams execution events to Apache Kafka.
* **RAG News Intelligence (:8003):** High-speed vector similarity engine querying market news and sentiment vectors powered by Qdrant Vector Database.
* **Frontend Web Application (:5173):** Modern React single-page application built with Vite and Tailwind CSS.

---

## 🔌 Core API Endpoints

| Service | Method | Endpoint | Description |
| --- | --- | --- | --- |
| **Auth Service** | `POST` | `/api/auth/register` | User registration & account creation |
| **Auth Service** | `POST` | `/api/auth/login` | JWT token generation & authentication |
| **ML Engine** | `POST` | `/api/ml/predict` | Triggers dynamic LSTM/GRU benchmarking & candle forecast |
| **RAG Service** | `POST` | `/api/rag/query` | Semantic news similarity search & vector retrieval |

---

## 🧠 Advanced Machine Learning Engine & MLOps

Instead of serving static or single-model forecasts, the platform implements an Automated Model Benchmarking Engine running on every prediction trigger:

```text
[ Market Candle Data ] ➔ [ Feature Extraction (RSI, MACD, MFI, TRIX) ] ➔ [ MinMaxScaler ]
                                                                             │
                       ┌─────────────────────────────────────────────────────┤
                       ▼                                                     ▼
               ┌──────────────┐                                      ┌──────────────┐
               │ LSTM Network │                                      │ GRU Network  │
               └──────┬───────┘                                      └──────┬───────┘
                      │                                                     │
                      └──────────────────────────┬──────────────────────────┘
                                                 ▼
                                  [ Validate Loss Benchmark ]
                                                 │
                                                 ▼
                                 [ Serve Lowest MSE/RMSE Model ]

```

* **Feature Engineering:** Computes technical indicators (RSI, MACD, MFI, CCI, Aroon, Trix, Moving Averages) to convert raw price action into multidimensional feature spaces.
* **Multi-Architecture Competition:**
* **LSTM (Long Short-Term Memory):** Handles long-term temporal dependencies across macro trends.
* **GRU (Gated Recurrent Unit):** Optimized recurrent structure providing rapid convergence on short-term price volatility.
* **Dense Baseline:** Serves as statistical control to ensure deep recurrent architectures outperform basic regression.


* **Dynamic Serving:** Computes Validation Loss (MSE/RMSE) in real-time and dynamically serves only the highest-performing model's outputs and visual charts back to the client.

---

## 💡 Engineering Trade-Offs & Architecture Decisions

* **Why Apache Kafka?** To prevent HTTP blocking and decouple heavy deep learning inference/training tasks from the synchronous web request-response cycle.
* **Why Qdrant Vector DB?** High-throughput vector indexing specifically optimized for semantic similarity search over high-dimensional news embedding spaces.
* **Why Dynamic MLOps Benchmarking?** Static models degrade rapidly due to market regime shifts. Benchmarking LSTM, GRU, and Dense baselines *on every trigger* ensures only the lowest validation loss model serves predictions.

---

## 🛠 Tech Stack & Modern Tooling

| Domain | Industry Standard Technologies |
| --- | --- |
| **Frontend Architecture** | React.js (Vite), JavaScript (ES6+), Axios, Tailwind CSS, Component Modularization |
| **Backend & Microservices** | Python 3.12, FastAPI, Uvicorn, RESTful API Design, JWT, Pydantic |
| **AI / Machine Learning** | TensorFlow / Keras, TA-Lib, NumPy, Pandas, Scikit-learn, Vector Embeddings |
| **Databases & Caching** | MySQL 8.0 (Relational), Redis (In-Memory Cache), Qdrant (Vector DB) |
| **Event Streaming & Queues** | Apache Kafka, Zookeeper |
| **DevOps & Infrastructure** | Docker, Multi-stage Dockerfiles, Docker Compose, GitHub Actions CI/CD |

---

## ⚡ Quick Start (Local Production-Like Environment)

The entire multi-container ecosystem is orchestrated using Docker Compose.

### Prerequisites

* Docker Desktop installed and running.
* Git installed.

### 1. Clone & Setup Environment

```bash
git clone [https://github.com/OmerSoyleyen24/Cryptocurrency.git](https://github.com/OmerSoyleyen24/Cryptocurrency.git)
cd Cryptocurrency

```

Create a `.env` file in the root directory using the production-grade template below:

```env
# ==========================================
# ENTERPRISE FINTECH PLATFORM - ENVIRONMENT CONFIGURATION
# ==========================================

# --- APPLICATION ENVIRONMENT ---
ENVIRONMENT=development
DEBUG=True

# --- SECURITY & JWT ---
SECRET_KEY=f7e9a2b4c6d8e0f1a3b5c7d9e1f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d4e6f8
ACCESS_TOKEN_EXPIRE_MINUTES=60

# --- MYSQL DATABASE (Auth & Relational Data) ---
DB_HOST=mysql
DB_PORT=3306
DB_NAME=cryptodb
DB_USER=cryptouser
DB_PASS=cryptopassword
MYSQL_ROOT_PASSWORD=rootpassword123

# --- REDIS (Session & Query Caching) ---
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# --- APACHE KAFKA (Event Streaming) ---
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
ZOOKEEPER_CLIENT_PORT=2181

# --- QDRANT VECTOR DATABASE (RAG News Intelligence) ---
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_GRPC_PORT=6334

# --- MICROSERVICES INTERNAL PORTS ---
API_GATEWAY_PORT=8000
AUTH_SERVICE_PORT=8001
ML_ENGINE_PORT=8002
RAG_SERVICE_PORT=8003
FRONTEND_PORT=5173

```

### 2. Launch the Ecosystem

Build and start all containers (Microservices, Infrastructure Services, and Frontend) with a single command:

```bash
docker-compose up -d --build

```

### 3. Verify Local Endpoints

Once containers show healthy, access the following entrypoints:

* 🌐 **Frontend Application:** http://localhost:5173
* 🔌 **API Gateway:** http://localhost:8000
* 📊 **Qdrant Vector Engine Dashboard:** http://localhost:6333/dashboard
* 🔐 **Auth Service Health:** http://localhost:8001
* 🧠 **ML Engine Health:** http://localhost:8002
* 🔍 **RAG Service Health:** http://localhost:8003

---

## 🛠 CI/CD Pipeline & Quality Assurance

This repository employs automated GitHub Actions workflows to enforce code quality, linting, and build verification on every pull request:

* **Automated Linting:** Code formatting check via flake8 and ESLint.
* **Container Build Checks:** Verifies that all Dockerfiles successfully compile without layer caching issues.
* **Continuous Integration:** Ensures no breaking changes enter the main branch.

---

## 👤 Author

* **Ömer Söyleyen**
* **Portfolio:** [portfolio-website-omersoyleyen.netlify.app](https://portfolio-website-omersoyleyen.netlify.app)
* **GitHub:** [@OmerSoyleyen24](https://www.google.com/search?q=https://github.com/OmerSoyleyen24)

```

```
