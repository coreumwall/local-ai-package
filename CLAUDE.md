# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Local AI Package is a Docker Compose-based infrastructure for self-hosted AI development. It integrates multiple AI and low-code tools including n8n, Supabase, Ollama, Open WebUI, Flowise, Neo4j, Langfuse, SearXNG, and Caddy for a complete local AI development environment.

## Commands

### Initial Setup
```bash
# Clone and setup
git clone -b stable https://github.com/coleam00/local-ai-packaged.git
cd local-ai-packaged
cp .env.example .env  # Then configure all required secrets

# Start services (choose appropriate profile)
python start_services.py --profile gpu-nvidia  # For NVIDIA GPUs
python start_services.py --profile gpu-amd     # For AMD GPUs on Linux
python start_services.py --profile cpu         # For CPU-only
python start_services.py --profile none        # When running Ollama separately

# For public deployments
python start_services.py --profile gpu-nvidia --environment public
```

### Service Management
```bash
# Stop all services
docker compose -p localai -f docker-compose.yml --profile <your-profile> down

# Update containers to latest versions
docker compose -p localai -f docker-compose.yml --profile <your-profile> pull
python start_services.py --profile <your-profile>

# View logs
docker compose -p localai logs -f [service-name]
```

### Testing Services
```bash
# Check service health
curl http://localhost:5678  # n8n
curl http://localhost:3000  # Open WebUI
curl http://localhost:3001  # Flowise (if not using auth)
```

## Architecture

### Service Stack Structure
The project uses a unified Docker Compose architecture with project name "localai":
- **Supabase Stack**: Database, authentication, and vector storage (loaded from `supabase/docker/docker-compose.yml`)
- **AI Stack**: n8n, Ollama, Open WebUI, Flowise, Qdrant, Neo4j, Langfuse, SearXNG
- **Infrastructure**: Caddy for reverse proxy and HTTPS management

### Key Components

1. **n8n (port 5678)**: Low-code workflow automation with 400+ integrations
   - Configured to use Supabase PostgreSQL as database
   - Pre-loaded with AI agent workflows from `n8n/backup/`
   - Integrates with Open WebUI via webhook

2. **Supabase**: Complete backend-as-a-service
   - PostgreSQL database (host: `db`)
   - Vector storage for RAG applications
   - Authentication services
   - Kong API gateway

3. **Ollama**: Local LLM runtime
   - Automatically pulls qwen2.5:7b-instruct-q4_K_M and nomic-embed-text models
   - Accessible at `http://ollama:11434` from within containers

4. **Open WebUI (port 3000)**: ChatGPT-like interface
   - Integrates with n8n agents via `n8n_pipe.py` function
   - Connects to local Ollama instance

5. **Flowise (port 3001)**: Visual AI agent builder
   - Custom tools in `flowise/` directory for n8n integration

6. **Neo4j**: Graph database for knowledge graphs (GraphRAG, LightRAG, Graphiti)

7. **Caddy**: HTTPS reverse proxy for production deployments

### Environment Configuration

Critical environment variables (from `.env`):
- **n8n**: `N8N_ENCRYPTION_KEY`, `N8N_USER_MANAGEMENT_JWT_SECRET`
- **Supabase**: `POSTGRES_PASSWORD`, `JWT_SECRET`, `ANON_KEY`, `SERVICE_ROLE_KEY`
- **Neo4j**: `NEO4J_AUTH` (format: username/password)
- **Langfuse**: Various secrets for observability
- **Caddy** (production only): Domain names for each service

### Deployment Modes

1. **Private (default)**: All ports exposed for local development
2. **Public**: Only ports 80/443 exposed via Caddy, requires domain configuration

### GPU Configuration Profiles
- `gpu-nvidia`: NVIDIA GPU support via Docker GPU runtime
- `gpu-amd`: AMD GPU support on Linux
- `cpu`: CPU-only mode
- `none`: Use external Ollama instance (Mac users with local Ollama)

### Integration Points

1. **n8n ↔ Open WebUI**: Via webhook URL configured in n8n_pipe.py
2. **n8n ↔ Supabase**: Direct database connection (host: `db`)
3. **All services ↔ Ollama**: HTTP API at `http://ollama:11434`
4. **Flowise ↔ n8n**: Custom tools for workflow triggering

### Data Persistence

Docker volumes maintain state across restarts:
- `n8n_storage`: Workflows and credentials
- `ollama_storage`: Downloaded models
- `open-webui`: Chat history and settings
- `flowise`: Flow configurations
- Supabase volumes in `supabase/docker/volumes/`

### Security Considerations

- All secrets must be generated securely (use `openssl rand -hex 32`)
- Special characters in POSTGRES_PASSWORD may cause issues (avoid `@`)
- In public mode, all services run behind Caddy with HTTPS
- Default credentials exist for development but must be changed for production