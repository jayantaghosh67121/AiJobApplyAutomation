# Development Setup Guide

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- `uv` package manager (or `poetry`)

### Option 1: Using Docker Compose (Recommended)

1. **Clone the repository and navigate to project:**
   ```bash
   cd AiJobApplyAutomation
   ```

2. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Build and start services:**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations:**
   ```bash
   docker-compose exec app alembic upgrade head
   ```

5. **Seed the database:**
   ```bash
   docker-compose exec app python scripts/seed.py
   ```

6. **Access services:**
   - FastAPI: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Streamlit Dashboard: http://localhost:8501
   - MinIO Console: http://localhost:9001 (minioadmin / minioadmin)

### Option 2: Local Development (Without Docker)

1. **Create virtual environment:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

4. **Update `.env` with your local database credentials:**
   ```
   DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/job_bot_db
   REDIS_URL=redis://localhost:6379/0
   ```

5. **Start PostgreSQL and Redis locally** (or use Docker just for these):
   ```bash
   docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password pgvector/pgvector:pg16
   docker run -d -p 6379:6379 redis:7-alpine
   ```

6. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

7. **Seed the database:**
   ```bash
   python scripts/seed.py
   ```

8. **Start development servers (in separate terminals):**
   ```bash
   # Terminal 1: FastAPI
   make dev

   # Terminal 2: Celery Worker
   make worker

   # Terminal 3: Celery Beat
   make beat

   # Terminal 4: Streamlit
   make dashboard
   ```

## Project Structure

```
AiJobApplyAutomation/
├── app/                    # Main application code
│   ├── api/               # FastAPI routers
│   ├── scrapers/          # Web scrapers
│   ├── matching/          # Job matching logic
│   ├── llm/               # LLM integration
│   ├── automation/        # Application automation
│   ├── models/            # SQLAlchemy ORM models
│   ├── config.py          # Configuration
│   ├── database.py        # Database setup
│   ├── main.py            # FastAPI app factory
│   └── worker.py          # Celery configuration
├── dashboard/             # Streamlit dashboard
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── alembic/               # Database migrations
├── pyproject.toml         # Project metadata & dependencies
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # FastAPI Docker image
├── Makefile               # Development commands
└── README.md              # Project documentation
```

## Common Commands

### Development
- `make dev` - Start FastAPI development server
- `make worker` - Start Celery worker
- `make beat` - Start Celery Beat scheduler
- `make dashboard` - Start Streamlit dashboard

### Code Quality
- `make lint` - Run code linter
- `make format` - Format code with Black
- `make type-check` - Run type checker

### Testing
- `make test` - Run all tests
- `make test-cov` - Run tests with coverage report

### Database
- `make migrate` - Run database migrations
- `make migrate-new MSG="description"` - Create new migration
- `make seed` - Seed database with sample data

### Docker
- `make docker-up` - Start Docker Compose services
- `make docker-down` - Stop Docker Compose services
- `make docker-logs` - View Docker logs

## Configuration

### Environment Variables
Copy `.env.example` to `.env` and update the following:

**Required:**
- `ANTHROPIC_API_KEY` - Claude API key from Anthropic
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

**Optional:**
- `PROXY_URL` - Residential proxy URL (for LinkedIn scraping)
- `CAPTCHA_API_KEY` - 2Captcha API key
- `SLACK_WEBHOOK_URL` - Slack webhook for notifications
- `GMAIL_CREDENTIALS_FILE` - Gmail API credentials

## Database Migrations

### Create a new migration
```bash
alembic revision --autogenerate -m "add new table"
```

### Apply migrations
```bash
alembic upgrade head
```

### Revert to previous migration
```bash
alembic downgrade -1
```

## Testing

### Run all tests
```bash
pytest tests/ -v
```

### Run specific test
```bash
pytest tests/unit/test_matching.py -v
```

### With coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

## Debugging

### Enable debug logging
Set `DEBUG=True` in `.env`

### View Celery tasks
```bash
celery -A app.worker inspect active
```

### View Redis data
```bash
redis-cli
KEYS *
```

## Performance Tips

1. **Database Indexes**: Ensure indexes are created on frequently queried columns
2. **Caching**: Use Redis for caching expensive computations
3. **Async Operations**: Use async/await for I/O operations
4. **Worker Concurrency**: Adjust `CELERY_CONCURRENCY` based on CPU count

## Troubleshooting

### Port already in use
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Database connection issues
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check database exists
psql -U job_bot_user -d job_bot_db -c "SELECT 1"
```

### Celery not working
```bash
# Check Redis is running
redis-cli ping

# Check Celery worker logs
celery -A app.worker inspect active
```

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and run tests: `make test`
3. Format code: `make format`
4. Commit changes: `git commit -m "Feature: description"`
5. Push to branch: `git push origin feature/your-feature`
6. Create Pull Request

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Playwright Documentation](https://playwright.dev/python/)
- [Anthropic API Documentation](https://docs.anthropic.com/)

## License

MIT License - see LICENSE file for details
