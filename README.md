#  BHIV Multi-Agent AI System

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
cd assistant-core-v3
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
docker build -t assistant-core .
docker run -p 8000:8000 --env-file .env assistant-core
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

## Cognitive Task Mapping (Sankalp)
- `taskflow.py` (reminder, meeting, call, note, email, alarm, calendar, general_task)  

## Memory & Embeddings (Chandresh)
- `embed_core/` — Secure embedding pipeline  
- `memory/memory_manager.py` — Vector memory  

## Core Infrastructure
- `database.py` — Database layer  
- `logging.py` — Logging  
- `security.py` — Authentication + audit logging  
- `llm_bridge.py` — Multi-LLM manager  
- `decision_hub.py` — Simple vs complex task routing  
- `rl_selector.py` — RL action handler  

## Tools
- Search tool  
- Web browser automation  
- Calculator  
- File operations  
- Automation  

---

# 🔌 API Endpoints

### BHIV System
- `POST /api/bhiv/run` — Execute complex tasks with BHIV  
- `POST /api/respond` — General LLM-based response  

### NLU (Seeya)
- `POST /api/summarize`  
- `POST /api/intent`  

### Task Mapping (Sankalp)
- `POST /api/task`  

### Embeddings (Chandresh)
- `POST /api/embed`  
- `POST /api/embed/similarity`  

### Voice
- `POST /api/voice-stt`  
- `POST /api/voice-tts`  

### System
- `/health`  
- `/metrics`  

### Optional (disabled for now)
- `/api/external-app`  

---

# 🔄 BHIV Processing Pipeline

### Input Processing
1. SummaryFlow → extract key points  
2. IntentFlow → classify + extract entities  
3. TaskFlow → convert into structured task  
4. DecisionHub → select simple vs complex  

### Complex Task Execution
5. BHIV Core  
6. Reasoning Engine (multi-step chain-of-thought)  
7. Multi-Agent System (planner → researcher → analyst → executor → evaluator)  
8. Tool execution  
9. Memory update via EmbedCore  

---

# ⚙️ Configuration

### Required
- `API_KEY`
- `JWT_SECRET_KEY`

### LLM Keys
- `OPENAI_API_KEY`
- `GROQ_API_KEY`
- `GOOGLE_API_KEY`
- `MISTRAL_API_KEY`

### Optional
- `SENTRY_DSN`
- `DATABASE_URL`
- `LOG_FILE`

---

# 📁 Project Structure

```
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── bhiv_core.py
│   │   ├── bhiv_reasoner.py
│   │   ├── summaryflow.py
│   │   ├── intentflow.py
│   │   ├── taskflow.py
│   │   ├── decision_hub.py
│   │   ├── llm_bridge.py
│   │   └── ...
│   ├── agents/
│   ├── tools/
│   ├── memory/
│   │   ├── memory_manager.py
│   │   ├── long_term.json
│   │   ├── short_term.json
│   │   ├── traits.json
│   │   └── user_profile.json
│   ├── embed_core/
│   └── routers/
├── client_adapters/
├── deploy/
├── hooks/
├── tests/
├── data/
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

# 🚀 Usage Examples

### 1. Simple Response
```bash
curl -X POST "http://localhost:8000/api/respond" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"text": "What is the weather today?", "model": "openai"}'
```

### 2. Full BHIV Multi-Agent Task
```bash
curl -X POST "http://localhost:8000/api/bhiv/run" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"text": "Research renewable energy trends and create a summary"}'
```

### 3. NLU Pipeline
```bash
curl -X POST "http://localhost:8000/api/summarize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your long text"}'

curl -X POST "http://localhost:8000/api/intent" \
  -H "Content-Type: application/json" \
  -d '{"text": "Remind me to call John tomorrow at 3pm"}'

curl -X POST "http://localhost:8000/api/task" \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "task",
    "entities": {"text": "Call John"},
    "text": "Remind me to call John tomorrow at 3pm"
  }'
```

### 4. Secure Embeddings
```bash
curl -X POST "http://localhost:8000/api/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Hello world"],
    "user_id": "user123",
    "platform": "web"
  }'
```

---

# 👥 Team Contributions

- **Nilesh** — BHIV Core, DecisionHub, LLM Bridge, Architecture  
- **Seeya** — SummaryFlow + IntentFlow (NLU Engine)  
- **Sankalp** — Cognitive TaskFlow Engine  
- **Chandresh** — EmbedCore + Secure Memory  

---

# 🔧 Development & Testing

```bash
pytest tests/
```

Check modules:
```bash
python -c "from app.core.summaryflow import summary_flow; print('OK')"
python -c "from app.core.intentflow import intent_flow; print('OK')"
python -c "from app.core.taskflow import task_flow; print('OK')"
python -c "from app.main import app; print('BHIV Ready')"
```

---

# 📄 License
- BHIV Core — MIT  
- EmbedCore — Proprietary (Chandresh)  
- SummaryFlow/IntentFlow — Proprietary (Seeya)  
- TaskFlow — Proprietary (Sankalp)  

---

# 🎯 Roadmap
- More agent specialization  
- Tool expansion  
- Multi-modal support  
- Realtime collaboration  
- Autonomous workflows  
