# 🚀 Quick Start Checklist

Complete this checklist to get the Job Automation Bot running.

## ☑️ Initial Setup (5 minutes)

- [ ] Navigate to project directory
  ```bash
  cd AiJobApplyAutomation
  ```

- [ ] Copy environment file
  ```bash
  cp .env.example .env
  ```

- [ ] Edit `.env` and add your API keys
  - [ ] `ANTHROPIC_API_KEY=sk-ant-...` (required, from https://console.anthropic.com/)
  - [ ] `PROXY_URL=...` (optional, for LinkedIn scraping)
  - [ ] `CAPTCHA_API_KEY=...` (optional, from https://2captcha.com/)

## ☑️ Choose Your Setup Option

### Option A: Docker Compose (Easiest) ⭐

- [ ] Install [Docker Desktop](https://www.docker.com/products/docker-desktop)

- [ ] Start all services
  ```bash
  docker-compose up -d
  ```
  
  Wait for all containers to be healthy (1-2 minutes)

- [ ] Run database migrations
  ```bash
  docker-compose exec app alembic upgrade head
  ```

- [ ] Seed database with sample data
  ```bash
  docker-compose exec app python scripts/seed.py
  ```

- [ ] Verify services are running
  ```bash
  docker-compose ps
  ```

✅ **Done!** Services are ready (see Access Services below)

### Option B: Local Development

- [ ] Install Python 3.11+
  ```bash
  python --version  # Should be 3.11+
  ```

- [ ] Install `uv` package manager
  
  **Windows (PowerShell):**
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
  
  **macOS/Linux:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
  
  **Alternative (all platforms):**
  ```bash
  pip install uv
  ```

- [ ] Create virtual environment
  ```bash
  uv venv
  ```
  
  Activate the environment:
  - **Windows (Command Prompt):** `.venv\Scripts\activate`
  - **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
  - **macOS/Linux:** `source .venv/bin/activate`

- [ ] Install dependencies
  ```bash
  uv sync
  ```

- [ ] Start PostgreSQL and Redis (using Docker)
  ```bash
  docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password pgvector/pgvector:pg16
  docker run -d -p 6379:6379 redis:7-alpine
  ```

- [ ] Initialize database
  ```bash
  alembic upgrade head
  python scripts/seed.py
  ```

- [ ] Start development servers (in separate terminals)
  ```bash
  # Terminal 1
  make dev
  
  # Terminal 2
  make worker
  
  # Terminal 3
  make beat
  
  # Terminal 4
  make dashboard
  ```

✅ **Done!** Services are ready (see Access Services below)

## ☑️ Access Services

Once running, access these URLs:

| Service | URL | Purpose |
|---------|-----|---------|
| FastAPI | http://localhost:8000 | API root |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| Dashboard | http://localhost:8501 | Streamlit UI |
| MinIO Console | http://localhost:9001 | File storage (user: minioadmin / pass: minioadmin) |

## ☑️ Verify Setup

Test that everything works:

```bash
# Check FastAPI health
curl http://localhost:8000/healthz

# Expected response:
# {"status":"ok","service":"Job Automation Bot"}
```

## ☑️ Useful Commands

```bash
# View all available commands
make help

# Run code linter
make lint

# Format code
make format

# Run tests
make test

# View Docker logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## ⚠️ Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000 (macOS/Linux)
lsof -ti:8000 | xargs kill -9

# Windows (PowerShell)
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check if database exists
psql -U job_bot_user -d job_bot_db -c "SELECT 1"
```

### Redis Connection Error
```bash
# Check if Redis is running
docker ps | grep redis

# Test Redis connection
redis-cli ping
```

### Docker Container Won't Start
```bash
# View logs
docker-compose logs app

# Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

## 📚 Next Steps

After setup is complete:

1. **Read the documentation**
   - [DEVELOPMENT.md](DEVELOPMENT.md) - Detailed setup guide
   - [README.md](README.md) - Project overview
   - [projectPlan.md](projectPlan.md) - Full development roadmap

2. **Review current status**
   - Phase 0 (Setup) is complete ✅
   - Phase 1 (Data Models) is next

3. **Configure your profile**
   - Go to Streamlit dashboard: http://localhost:8501
   - Enter your profile information in Settings page
   - Set your job preferences

4. **Start Phase 1: Data Models**
   - See [projectPlan.md](projectPlan.md#phase-1--data-models--database-days-4-7)

## ✅ Setup Complete!

Your Job Automation Bot is now ready for development.

**Current Phase**: 0 — Setup ✅  
**Next Phase**: 1 — Data Models & Database  
**Estimated Time**: 10–14 weeks (part-time)

---

Need help? Check [DEVELOPMENT.md](DEVELOPMENT.md#troubleshooting) for detailed troubleshooting.
