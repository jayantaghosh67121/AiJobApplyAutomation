# 🤖 Job Automation Bot

AI-powered job application automation system that scrapes job postings, scores them against your profile, generates tailored applications, and submits them automatically.

## 🎯 Features (Planned)

- **Intelligent Job Scraping**: Automatically collect job postings from LinkedIn, Indeed, RemoteOK, and more
- **Smart Matching**: AI-powered job matching using semantic similarity and keyword scoring
- **Document Generation**: Auto-generate tailored resumes and cover letters for each job
- **Automated Applications**: Fill and submit job applications automatically
- **Reply Detection**: Monitor Gmail for recruiter responses and interview invites
- **Analytics Dashboard**: Track applications, response rates, and success metrics
- **Rate Limiting**: Intelligent throttling to avoid being detected as a bot

## 📋 Phase Progress

| Phase | Status | Duration | Deliverable |
|-------|--------|----------|-------------|
| 0 — Setup | ✅ Complete | Days 1–3 | Docker stack, project skeleton |
| 1 — Data models | ⏳ Pending | Days 4–7 | Database schema |
| 2 — Scraping | ⏳ Pending | Days 8–16 | Job collection |
| 3 — Matching | ⏳ Pending | Days 17–28 | Job scoring |
| 4 — Documents | ⏳ Pending | Days 29–36 | Resume & cover letter |
| 5 — Applications | ⏳ Pending | Days 37–50 | Auto-submission |
| 6 — Observability | ⏳ Pending | Days 51–58 | Monitoring & feedback |
| 7 — Hardening | ⏳ Pending | Days 59–70 | Production ready |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- `uv` or `poetry` for dependency management

### Option 1: Docker Compose (Recommended)

```bash
# Clone and navigate to project
cd AiJobApplyAutomation

# Copy environment file
cp .env.example .env

# Update .env with your API keys
# - ANTHROPIC_API_KEY (required)
# - PROXY_URL (optional, for LinkedIn scraping)
# - CAPTCHA_API_KEY (optional)

# Start services
docker-compose up -d

# Run migrations
docker-compose exec app alembic upgrade head

# Seed database
docker-compose exec app python scripts/seed.py

# Access services:
# - FastAPI: http://localhost:8000
# - Docs: http://localhost:8000/docs
# - Dashboard: http://localhost:8501
```

### Option 2: Local Development

```bash
# Create virtual environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
uv sync

# Copy and configure environment
cp .env.example .env

# Start dependencies with Docker
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password pgvector/pgvector:pg16
docker run -d -p 6379:6379 redis:7-alpine

# Run migrations and seed
alembic upgrade head
python scripts/seed.py

# Start development servers (in separate terminals)
make dev           # FastAPI on :8000
make worker        # Celery worker
make beat          # Celery Beat scheduler
make dashboard     # Streamlit on :8501
```

## 📚 Project Structure

```
AiJobApplyAutomation/
├── app/
│   ├── api/           # FastAPI routers & endpoints
│   ├── scrapers/      # Web scraping modules
│   ├── matching/      # Job matching & scoring
│   ├── llm/           # LLM integration (Claude)
│   ├── automation/    # Application automation
│   ├── models/        # SQLAlchemy ORM models
│   ├── config.py      # Configuration
│   ├── database.py    # Database setup
│   ├── main.py        # FastAPI application
│   └── worker.py      # Celery task queue
├── dashboard/         # Streamlit web UI
├── tests/             # Test suite
├── scripts/           # Utility scripts (seed, migrate)
├── alembic/           # Database migrations
├── docker-compose.yml # Services orchestration
├── pyproject.toml     # Dependencies & metadata
└── Makefile           # Development commands
```

## 🛠️ Common Commands

```bash
# Development
make dev              # Start FastAPI dev server with reload
make worker           # Start Celery worker
make beat             # Start Celery Beat scheduler
make dashboard        # Start Streamlit dashboard

# Code Quality
make lint             # Run Ruff linter
make format           # Format with Black
make type-check       # Run mypy type checker

# Testing
make test             # Run all tests
make test-cov         # Run tests with coverage report

# Database
make migrate          # Run pending migrations
make migrate-new MSG="description"  # Create migration
make seed             # Populate database with sample data

# Docker
make docker-up        # Start all Docker services
make docker-down      # Stop Docker services
make docker-logs      # View Docker logs
```

## 📖 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

**Required for operation:**
- `ANTHROPIC_API_KEY` - Claude API key from [Anthropic](https://console.anthropic.com/)
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

**Optional:**
- `PROXY_URL` - Residential proxy for LinkedIn (e.g., Brightdata)
- `CAPTCHA_API_KEY` - 2Captcha API key for CAPTCHA solving
- `SLACK_WEBHOOK_URL` - Slack notifications
- `GMAIL_CREDENTIALS_FILE` - Gmail API for reply monitoring

See `.env.example` for all available configuration options.

## 🗄️ Database

### Migrations

```bash
# Create new migration after model changes
alembic revision --autogenerate -m "add user table"

# Apply pending migrations
alembic upgrade head

# Revert last migration
alembic downgrade -1
```

### Seeding

```bash
# Load sample data
python scripts/seed.py
```

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_matching.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

## 📊 API Endpoints

### Health Check
```
GET /healthz
```

### Jobs (Phase 2+)
```
GET    /api/jobs              # List jobs
POST   /api/jobs              # Create job
GET    /api/jobs/{id}         # Get job details
GET    /api/jobs/search       # Search jobs
```

### Matches (Phase 3+)
```
GET    /api/matches           # List job matches
GET    /api/matches/{id}      # Get match details
POST   /api/matches/{id}/score # Rescore job
```

### Applications (Phase 5+)
```
GET    /api/applications                 # List applications
POST   /api/applications                 # Create application
GET    /api/applications/{id}            # Get application
POST   /api/applications/{id}/submit     # Submit application
POST   /api/applications/{id}/approve    # Approve for auto-submit
```

## 📈 Stack Overview

| Component | Technology | Purpose |
|-----------|-----------|---------|
| API | FastAPI | REST API backend |
| Database | PostgreSQL + pgvector | Data storage + embeddings |
| Cache | Redis | Caching & job queue |
| Task Queue | Celery | Async job processing |
| Scraping | Playwright | Browser automation |
| LLM | Anthropic Claude | Text generation & ranking |
| Embeddings | Sentence Transformers | Vector similarity |
| Dashboard | Streamlit | Web UI & analytics |
| Container | Docker | Development & deployment |

## 🔐 Security

- Environment variables for all secrets (`.env` file)
- No secrets committed to version control
- Database accessible only within Docker network
- Rate limiting on API endpoints
- CAPTCHA support for form submissions
- Proxy rotation for web scraping

## 🚦 Development Workflow

1. **Create feature branch**: `git checkout -b feature/your-feature`
2. **Make changes** and test them
3. **Run linter**: `make lint` → `make format`
4. **Run tests**: `make test`
5. **Commit**: `git commit -m "Feature: description"`
6. **Push**: `git push origin feature/your-feature`
7. **Create Pull Request** on GitHub

## 📚 Documentation

- [Development Setup](DEVELOPMENT.md) - Detailed setup & troubleshooting
- [Project Plan](projectPlan.md) - Full development roadmap
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)

## 💾 Cost Estimate

Running at ~15 applications/day:

| Service | Monthly Cost |
|---------|------------|
| Claude API | $8–15 |
| Residential Proxies | $20–40 |
| CAPTCHA Solving | $5–10 |
| Hosting | $10–20 |
| **Total** | **~$43–85** |

Costs decrease with:
- Using Ollama for bulk scoring (free)
- Fewer applications/day (< 10)
- Using public proxies (free but slower)

## 🤝 Contributing

Contributions are welcome! Please:

1. Follow the existing code style (Black, Ruff)
2. Write tests for new features
3. Update documentation
4. Create descriptive commit messages

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support & Troubleshooting

See [DEVELOPMENT.md](DEVELOPMENT.md#troubleshooting) for:
- Port conflicts
- Database connection issues
- Celery problems
- Docker issues

## 🎓 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Playwright Documentation](https://playwright.dev/python/)
- [Anthropic API Docs](https://docs.anthropic.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Status**: Phase 0 — Setup ✅ Complete

**Next Phase**: Phase 1 — Data Models & Database (Days 4–7)

Last Updated: May 16, 2026