#  Enterprise-Grade FinTech & AI Analytics Platform

An enterprise-ready, event-driven distributed platform designed for real-time cryptocurrency analytics, multi-model Deep Learning market prediction (LSTM/GRU/Dense), and semantic RAG (Retrieval-Augmented Generation) news insights.

Engineered from scratch to demonstrate **Production-Ready Software Engineering**, **Scalable Microservices Topology**, **Event Streaming**, and **Automated MLOps Benchmarking**.

---

## 💡 Engineering Motivation & Problem Statement

Financial technology platforms require **high throughput**, **fault isolation**, and **low-latency algorithmic responses**. Traditional monolithic approaches to time-series machine learning often suffer from blocking execution and tight coupling.

This platform solves these domain challenges through:

1. **Asynchronous Event Streaming:** Decoupling high-overhead deep learning tasks from web servers via **Apache Kafka**.
2. **Dynamic MLOps Model Selection:** Automatically benchmarking deep learning models in real-time to prevent model drift and vanishing gradients.
3. **API Gateway & Edge Isolation:** Protecting internal domain services behind a unified, rate-limited, reverse-proxy gateway.

---

## 🏗 System Architecture & Distributed Design

The ecosystem is split into domain-driven, containerized microservices operating over a private overlay network (`crypto-network`).

```
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

* **API Gateway (`:8000`):** Single point of entry handling request routing, payload proxying, and service abstraction.
* **Auth & User Management (`:8001`):** Manages identity, JWT sessions, and relational user crypto lists backed by **MySQL 8.0** and **Redis** for session/query caching.
* **ML Engine Service (`:8002`):** Ingests live market data from exchange APIs, computes 14+ technical indicators using **TA-Lib**, executes model training/evaluations, and streams execution events to **Apache Kafka**.
* **RAG News Intelligence (`:8003`):** High-speed vector similarity engine querying market news and sentiment vectors powered by **Qdrant Vector Database**.
* **Frontend Web Application (`:5173`):** Modern React single-page application built with **Vite** and **Tailwind CSS**.

---

## 🧠 Advanced Machine Learning Engine & MLOps

Instead of serving static or single-model forecasts, the platform implements an **Automated Model Benchmarking Engine** running on every prediction trigger:

```
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

1. **Feature Engineering:** Computes technical indicators (RSI, MACD, MFI, CCI, Aroon, Trix, Moving Averages) to convert raw price action into multidimensional feature spaces.
2. **Multi-Architecture Competition:**
* **LSTM (Long Short-Term Memory):** Handles long-term temporal dependencies across macro trends.
* **GRU (Gated Recurrent Unit):** Optimized recurrent structure providing rapid convergence on short-term price volatility.
* **Dense Baseline:** Serves as statistical control to ensure deep recurrent architectures outperform basic regression.


3. **Dynamic Serving:** Computes Validation Loss (MSE/RMSE) in real-time and dynamically serves only the highest-performing model's outputs and visual charts back to the client.

---

## 🛠 Tech Stack & Modern Tooling

| Domain | Industry Standard Technologies |
| --- | --- |
| **Frontend Architecture** | React.js (Vite), JavaScript (ES6+), Axios, Tailwind CSS, Component Modularization |
| **Backend & Microservices** | Python 3.12, FastAPI, Uvicorn, RESTful API Design, JWT, Pydantic |
| **AI / Machine Learning** | TensorFlow / Keras, TA-Lib, NumPy, Pandas, Scikit-learn, Vector Embeddings |
| **Databases & Caching** | MySQL 8.0 (Relational), Redis (InMemory Cache), Qdrant (Vector DB) |
| **Event Streaming & Queues** | Apache Kafka, Zookeeper |
| **DevOps & Infrastructure** | Docker, Multi-stage Dockerfiles, Docker Compose, GitHub Actions CI/CD |

---

## ⚡ Quick Start (Local Production-Like Environment)

The entire multi-container ecosystem is orchestrated using Docker Compose.

### Prerequisites

* **Docker Desktop** installed and running.
* **Git** installed.

### 1. Clone & Setup Environment

```bash
git clone https://github.com/OmerSoyleyen24/Cryptocurrency.git
cd Cryptocurrency

```

Create a `.env` file in the project root:

```env
# Database Credentials
DB_HOST=mysql
DB_NAME=cryptodb
DB_USER=cryptouser
DB_PASS=cryptopassword
DB_PORT=3306

# System Security
SECRET_KEY=f7e9a2b4c6d8e0f1a3b5c7d9e1f2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d4e6f8

```

### 2. Launch the Ecosystem

Build and start all 8 containers (4 Microservices, 4 Infrastructure Services, 1 Frontend) with a single command:

```bash
docker-compose up -d --build

```

### 3. Verify Local Endpoints

Once containers show healthy, access the following entrypoints:

* 🌐 **Frontend Application:** `http://localhost:5173`
* 🔌 **API Gateway:** `http://localhost:8000`
* 📊 **Qdrant Vector Engine Dashboard:** `http://localhost:6333/dashboard`
* 🔐 **Auth Service Health:** `http://localhost:8001`
* 🧠 **ML Engine Health:** `http://localhost:8002`
* 🔍 **RAG Service Health:** `http://localhost:8003`

---

## 🛠 CI/CD Pipeline & Quality Assurance

This repository employs automated **GitHub Actions** workflows to enforce code quality, linting, and build verification on every pull request:

* **Automated Linting:** Code formatting check via `flake8` and `ESLint`.
* **Container Build Checks:** Verifies that all Dockerfiles successfully compile without layer caching issues.
* **Continuous Integration:** Ensures no breaking changes enter the `main` branch.

---

## 👤 Author

**Ömer Söyleyen**

* **Portfolio:** [portfolio-website-omersoyleyen.netlify.app](https://portfolio-website-omersoyleyen.netlify.app)
* **GitHub:** [@OmerSoyleyen24](https://www.google.com/search?q=https://github.com/OmerSoyleyen24)
