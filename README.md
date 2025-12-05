# Assistant Core v3

Multi-Platform Brain & Integration Layer - A comprehensive AI assistant backend providing unified access to various AI services, voice processing, task management, and cross-platform integrations.

## Features

- **Multi-LLM Support**: Integrated support for OpenAI, Groq, Google Generative AI, and Mistral
- **Voice Processing**: Speech-to-text and text-to-speech capabilities using OpenAI Whisper and TTS
- **Task Management**: Intelligent task creation, summarization, and intent recognition
- **Decision Hub**: Advanced decision-making and reinforcement learning actions
- **Embedding Services**: Text embeddings and similarity computations
- **External Integrations**: Connect with Notion, Google Sheets, Trello, and custom applications
- **Security**: JWT-based authentication, API key support, rate limiting, and audit logging
- **Monitoring**: Built-in health checks, metrics, and Sentry integration
- **Multi-Platform**: Client adapters for Android, iOS, macOS, Windows, and Web

## Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd assistant-core-v3
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Metrics: http://localhost:8000/metrics

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Or run with Docker directly**
   ```bash
   docker build -t assistant-core .
   docker run -p 8000:8000 --env-file .env assistant-core
   ```

## Deployment Options

### Cloud Platforms

- **Render**: See `deploy/deploy_render.md` for Render deployment instructions
- **Vercel**: See `deploy/deploy_vercel.md` for Vercel deployment instructions
- **Docker**: See `deploy/docker_run.md` for standalone Docker deployment

### Production Considerations

- Set `ENV=production` in environment variables
- Configure proper database URL for production use
- Enable Sentry monitoring with `SENTRY_DSN`
- Use secure, randomly generated `API_KEY` and `JWT_SECRET_KEY`
- Configure log file path with `LOG_FILE`

## Module Architecture

### Core Modules

The application is built around several core modules that provide foundational functionality:

- **`core/database.py`**: Database connection and table management using SQLAlchemy with async support
- **`core/logging.py`**: Centralized logging configuration with file and console handlers
- **`core/security.py`**: Authentication, authorization, rate limiting, and audit logging
- **`core/llm_bridge.py`**: Unified interface to multiple LLM providers (OpenAI, Groq, Google, Mistral)
- **`core/decision_hub.py`**: Intelligent decision-making and workflow orchestration
- **`core/rl_selector.py`**: Reinforcement learning-based action selection
- **`core/external_integrations.py`**: Integration with external services (Notion, Google Sheets, Trello)

### API Routers

The API is organized into functional routers, each handling specific capabilities:

- **`/auth`**: User authentication and token management
- **`/api/summarize`**: Text summarization using LLMs
- **`/api/intent`**: Intent recognition and classification
- **`/api/task`**: Task creation, management, and execution
- **`/api/decision-hub`**: Complex decision-making workflows
- **`/api/rl-action`**: Reinforcement learning-based actions
- **`/api/embed`**: Text embeddings and similarity computations
- **`/api/respond`**: General AI response generation
- **`/api/voice-stt`**: Speech-to-text conversion
- **`/api/voice-tts`**: Text-to-speech synthesis
- **`/api/external-llm`**: Direct access to external LLM services
- **`/api/external-app`**: Integration with external applications

### Client Adapters

Platform-specific client implementations are provided in the `client_adapters/` directory:

- `android_adapter.md`: Android mobile application integration
- `ios_adapter.md`: iOS mobile application integration
- `macos_adapter.md`: macOS desktop application integration
- `windows_adapter.md`: Windows desktop application integration
- `web_adapter.md`: Web browser application integration

### Integration Hooks

Custom integration points are available in the `hooks/` directory:

- `coreauth.py`: Core authentication hooks
- `insightflow.py`: Data insight and analytics hooks
- `karma.py`: User karma and reputation system hooks

## Module Connections

The modules interconnect through a layered architecture:

1. **Client Layer**: Platform-specific adapters communicate with the API
2. **API Layer**: FastAPI routers handle HTTP requests and route to appropriate handlers
3. **Core Layer**: Business logic modules process requests and manage state
4. **Integration Layer**: External service hooks and adapters handle third-party connections
5. **Data Layer**: Database and caching layers persist information

Key connection points:
- All routers access core modules for shared functionality
- LLM Bridge provides unified AI service access across all text-processing routers
- Decision Hub coordinates complex workflows involving multiple modules
- External integrations are triggered by hooks in the core modules
- Security middleware wraps all API endpoints with authentication and rate limiting

## Configuration

Environment variables control application behavior. See `.env.example` for all available options.

Required for basic functionality:
- `API_KEY`: API key for authentication
- `JWT_SECRET_KEY`: Secret key for JWT token signing

Optional for extended features:
- AI service API keys (OPENAI_API_KEY, etc.)
- SENTRY_DSN for error monitoring
- DATABASE_URL for custom database configuration

## Development

### Running Tests

```bash
pytest tests/
```

### Code Structure

```
├── app/
│   ├── main.py              # FastAPI application setup
│   ├── core/                # Core business logic modules
│   └── routers/             # API endpoint handlers
├── client_adapters/         # Platform-specific client docs
├── deploy/                  # Deployment configurations
├── hooks/                   # Integration hooks
├── tests/                   # Test suite
├── data/                    # Data storage
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container build config
├── docker-compose.yml       # Multi-container setup
└── .env.example             # Environment template
```

## API Documentation

Once running, visit `/docs` for interactive API documentation powered by Swagger UI.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[Add your license information here]