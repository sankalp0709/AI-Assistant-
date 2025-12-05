import sys
import os

# Add project root to Python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

import os
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

# Initialize Sentry if enabled
if os.getenv("SENTRY_DSN"):
    import sentry_sdk
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        traces_sample_rate=1.0,
        environment=os.getenv("ENV", "development"),
    )

# Local imports (WORK NOW because sys.path is fixed)
from .core.logging import setup_logging, get_logger
from .core.database import create_tables
from .core.security import authenticate_user, rate_limit, audit_log

from app.routers import (
    summarize,
    intent,
    task,
    decision_hub,
    rl_action,
    embed,
    respond,
    voice_stt,
    voice_tts,
    external_llm,
    external_app,
    auth
)

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(
    title="Assistant Core v3",
    description="Multi-Platform Brain & Integration Layer",
    version="3.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security middleware
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    if not request.url.path.startswith("/api"):
        return await call_next(request)

    rate_limit(request)

    user = None
    api_key = request.headers.get("X-API-Key")
    auth_header = request.headers.get("Authorization")

    if api_key and api_key == os.getenv("API_KEY"):
        user = "api_key_user"

    elif auth_header and auth_header.startswith("Bearer "):
        from .core.security import verify_token_string
        token = auth_header.split(" ")[1]
        try:
            token_data = verify_token_string(token)
            user = token_data.username
        except:
            pass

    if not user:
        return JSONResponse(status_code=401, content={"detail": "Authentication failed"})

    audit_log(request, user)

    return await call_next(request)


# Routers
app.include_router(auth.router, tags=["Auth"])
app.include_router(summarize.router, prefix="/api", tags=["Summarize"])
app.include_router(intent.router, prefix="/api", tags=["Intent"])
app.include_router(task.router, prefix="/api", tags=["Task"])
app.include_router(decision_hub.router, prefix="/api", tags=["Decision Hub"])
app.include_router(rl_action.router, prefix="/api", tags=["RL Action"])
app.include_router(embed.router, prefix="/api", tags=["Embed"])
app.include_router(respond.router, prefix="/api", tags=["Respond"])
app.include_router(voice_stt.router, prefix="/api", tags=["Voice STT"])
app.include_router(voice_tts.router, prefix="/api", tags=["Voice TTS"])
app.include_router(external_llm.router, prefix="/api", tags=["External LLM"])
app.include_router(external_app.router, prefix="/api", tags=["External App"])


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "3.0.0"
    }


@app.get("/metrics")
async def metrics():
    import psutil
    import time
    return {
        "uptime": time.time() - psutil.boot_time(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent
        },
        "disk": {
            "total": psutil.disk_usage('/').total,
            "free": psutil.disk_usage('/').free,
            "percent": psutil.disk_usage('/').percent
        }
    }


@app.get("/")
async def root():
    return {"message": "Assistant Core v3 API", "status": "running"}
