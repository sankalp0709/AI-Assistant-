# BHIV-AI-ASSISTANT

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

**Brain-Human Interface Virtual (BHIV)** is a multi-agent AI assistant backend designed for advanced reasoning, secure memory, intelligent task mapping, and multi-platform integration.
It integrates Seeya's NLU system, Sankalp’s cognitive task engine, and Chandresh’s secure embeddings with your BHIV multi-agent brain.

```
User Input → SummaryFlow → IntentFlow → TaskFlow → Decision Hub → BHIV Core → Reasoning Engine → Multi-Agent System → Tools → Memory
                                                                │
                                                                └─ Simple Response (LLM)
```

---

# 🧠 Core Architecture

## BHIV Multi-Agent System
- **5 Specialized Agents**: Planner, Researcher, Analyst, Executor, Evaluator  
- **Reasoning Engine**: Multi-step chain-of-thought orchestration  
- **Secure Embeddings**: User-specific obfuscation via EmbedCore  
- **Cognitive Mapping**: TaskFlow by Sankalp  
- **NLU Layer**: SummaryFlow + IntentFlow by Seeya  

## Key Features
- Multi-Agent Reasoning (BHIV Core)
- Secure memory with vector embeddings
- Advanced NLU pipeline (summary → intent → task)
- Cognitive task classification (reminders, meetings, emails, notes...)
- Multi-LLM support: **OpenAI, Groq, Google, Mistral**
- Speech-to-text & text-to-speech
- Tools for automation, search, browsing, calculator, files
- Security: JWT, API keys, rate limiting, encrypted memory
- Multi-platform clients (Android, iOS, Web, Desktop)

---

# 🚀 Quick Start

## Prerequisites
- Python **3.11+**
- Docker (optional)

## Local Development

### 1. Clone Repository
```bash
git clone <repository-url>
cd BHIV-AI-ASSISTANT
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
```
Add your API keys inside `.env`.

### 4. Run Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access UI
- API Docs → http://localhost:8000/docs  
- Health → http://localhost:8000/health  
- Metrics → http://localhost:8000/metrics  

---

# 🐳 Docker Deployment

### Docker Compose
```bash
docker-compose up --build
```

### Or Build Manually
```bash
docker build -t bhiv-ai-assistant .
docker run -p 8000:8000 --env-file .env bhiv-ai-assistant
```

---

# 🏗️ Module Architecture

## BHIV Core System
- `core/bhiv_core.py` — Multi-agent orchestrator  
- `core/bhiv_reasoner.py` — Reasoning engine (Planner → Researcher → Analyst → Executor → Evaluator)  
- `agents/` — Specialized reasoning agents  

## NLU Processing (Seeya)
- `summaryflow.py`  
- `intentflow.py`  

## Task Engine (Sankalp)
- `taskflow.py`  
- `decision_hub.py`  

## Memory & Embeddings (Chandresh)
- `database.py`  
- `memory_manager.py`  
- `security.py`  

---

# 🚦 Go-Live Readiness Checklist (Phase 1 & 2)

Use this checklist to verify system health before deployment.

### 1. Verify Environment
Ensure Python 3.11+ and compatible dependencies.
```bash
python --version
pip show sqlalchemy  # Must be >= 2.0.36
```

### 2. Verify Assistant Response Layer (ARL v1)
Confirm contract compliance and integration logic.
```bash
# Verify Integration Logic (Mocked Decision Hub)
python scripts/verify_integration.py

# Verify Response Composer Logic
python -m pytest -q tests/test_response_composer.py
```

### 3. Verify Trust & Governance (Quiet Mode)
Ensure trust signals are ingested but not exposed.
```bash
# Verify Node.js Trust Signal Ingestion
node scripts/test_node_trust.js

# Verify Python Trust Signal Ingestion
python -m pytest -q tests/test_trust_readiness.py
```

### 4. Full Suite Validation
Run all pre-commit hooks and tests.
```bash
pre-commit run --all-files
python -m pytest
```

### 5. Handoff Notes
- **Nilesh (Backend)**: Use `app/core/response_composer.py` or `node/response_composer.js` for all outputs.
- **Yash (Frontend)**: Render `assistant_message` (markdown) and `next_steps` (chips). Gate on `response_version="v1"`.
- **Docs**: See [ASSISTANT_RESPONSE_LAYER.md](ASSISTANT_RESPONSE_LAYER.md) for full contract specs.
