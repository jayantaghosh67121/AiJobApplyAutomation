# Job Automation System — Detailed Development Plan

---

## Overview

| | |
|---|---|
| **Goal** | Build a system that scrapes job postings, scores them against your profile, generates tailored applications, and submits them automatically |
| **Stack** | Python · FastAPI · Playwright · PostgreSQL + pgvector · Redis · Celery · Claude API · Streamlit |
| **Total estimated time** | 10–14 weeks (solo developer, part-time) |
| **Approach** | Iterative — each phase produces something runnable before moving on |

---

## Phase 0 — Project setup (Days 1–3)

### Goals
Get the local dev environment running and lay down the project skeleton before writing any feature code.

### Tasks

**Repository & tooling**
- Init a GitHub repo with a `main` / `dev` branch strategy
- Set up `pyproject.toml` with `uv` or `poetry` for dependency management
- Configure `ruff` for linting and `black` for formatting
- Add `pre-commit` hooks (lint, format, no secrets)
- Write a root `Makefile` with shortcuts: `make dev`, `make test`, `make migrate`

**Docker Compose (local)**
```yaml
services:
  postgres:   image: pgvector/pgvector:pg16
  redis:      image: redis:7-alpine
  app:        build: .  (FastAPI)
  worker:     command: celery -A app.worker worker
  beat:       command: celery -A app.worker beat
  streamlit:  build: . command: streamlit run dashboard/app.py
```

**Project structure**
```
job-bot/
├── app/
│   ├── api/          # FastAPI routers
│   ├── scrapers/     # Playwright + Scrapy spiders
│   ├── matching/     # Embeddings + scoring
│   ├── llm/          # Claude / Ollama wrappers
│   ├── automation/   # Form-fill engine
│   ├── models/       # SQLAlchemy ORM models
│   └── worker.py     # Celery app
├── dashboard/        # Streamlit UI
├── tests/
├── alembic/          # DB migrations
├── docker-compose.yml
└── pyproject.toml
```

**Environment config**
- `.env.example` with all required keys documented
- `pydantic-settings` `Settings` class to load and validate env vars at startup
- Required secrets: `DATABASE_URL`, `REDIS_URL`, `ANTHROPIC_API_KEY`, `PROXY_URL`, `CAPTCHA_API_KEY`

### Deliverable
`docker compose up` starts all services. FastAPI returns `200` on `GET /healthz`. Database migrates cleanly.

---

## Phase 1 — Data models & database (Days 4–7)

### Goals
Design and migrate the core schema. Everything else builds on top of this.

### SQLAlchemy models

**`JobPosting`**
```
id, source (linkedin/indeed/…), external_id, title, company,
location, remote_type, salary_min, salary_max, description_raw,
description_parsed (JSONB), posted_at, scraped_at, is_active
```

**`JobMatch`**
```
id, job_id (FK), embedding (vector(768)), match_score (float),
llm_rank (int), llm_rationale (text), status (new/queued/skipped),
created_at
```

**`Application`**
```
id, job_id (FK), resume_variant_id (FK), cover_letter (text),
status (queued/applied/interview/rejected/offer),
applied_at, response_at, notes
```

**`ResumeVariant`**
```
id, base_resume_id, job_id (FK), content (text),
pdf_s3_key, created_at
```

**`UserProfile`**
```
id, full_name, email, phone, linkedin_url, github_url,
location, skills (text[]), experience_years,
preferences (JSONB: salary_floor, remote_only, blacklist_companies[])
```

### Tasks
- Write all SQLAlchemy models with proper indexes
- Create Alembic migration: `alembic revision --autogenerate -m "initial"`
- Enable `pgvector` extension: `CREATE EXTENSION IF NOT EXISTS vector`
- Add vector index: `CREATE INDEX ON job_match USING ivfflat (embedding vector_cosine_ops)`
- Write Pydantic v2 schemas for every model (request / response shapes)
- Seed script: insert your profile + 5 sample job postings for testing

### Deliverable
`alembic upgrade head` runs without errors. Seed data loads. All models queryable via a test script.

---

## Phase 2 — Job scraping layer (Days 8–16)

### Goals
Reliably pull job postings from at least two sources and store them deduplicated.

### Architecture

```
Celery Beat (cron)
    → scrape_jobs task
        → source-specific scraper
            → parse_posting()
            → deduplicate (external_id)
            → save to DB
```

### Scraper 1 — LinkedIn (Playwright)

LinkedIn blocks headless browsers. Use these mitigations:
- `playwright-stealth` plugin to mask automation signals
- Rotating residential proxies (Brightdata)
- Human-like delays between actions (`random.uniform(1.5, 3.5)` seconds)
- Session cookies stored and reused

```python
# app/scrapers/linkedin.py
async def scrape_linkedin(query: str, location: str, max_pages: int = 5):
    async with async_playwright() as p:
        browser = await p.chromium.launch(proxy={"server": PROXY_URL})
        page = await browser.new_page()
        await stealth_async(page)
        # navigate, scroll, extract job cards
        # yield JobPostingCreate objects
```

Key fields to extract: title, company, location, posted_date, description (click-through to full JD), job URL.

### Scraper 2 — Indeed / RemoteOK (Scrapy or requests)

Many smaller boards expose simpler HTML or RSS. Use `httpx` + `BeautifulSoup` for these — much faster than launching a browser.

```python
# app/scrapers/remoteok.py
async def scrape_remoteok(tags: list[str]):
    async with httpx.AsyncClient() as client:
        r = await client.get("https://remoteok.com/api", ...)
        # parse JSON response
```

### Deduplication logic

```python
async def upsert_job(session, posting: JobPostingCreate):
    existing = await session.scalar(
        select(JobPosting).where(
            JobPosting.source == posting.source,
            JobPosting.external_id == posting.external_id
        )
    )
    if existing:
        return  # skip duplicate
    session.add(JobPosting(**posting.model_dump()))
```

### Celery tasks

```python
@celery_app.task
def run_all_scrapers():
    run_linkedin.delay(query="python developer", location="remote")
    run_indeed.delay(query="backend engineer", location="remote")

# Schedule in celery beat:
# run_all_scrapers: every 4 hours
```

### Testing
- `pytest` with `pytest-playwright` for scraper unit tests
- Mock HTTP responses with `respx` to avoid hitting live sites during CI
- Assert: duplicate postings are not inserted twice

### Deliverable
Running `celery worker` + `celery beat` populates the `job_postings` table with real data on a schedule. At least 20 real job postings stored after first run.

---

## Phase 3 — AI matching engine (Days 17–28)

### Goals
Score every new job against your profile. Produce a ranked list of the best matches.

### Step 3a — JD parser

Extract structured data from raw description text using spaCy + regex:

```python
# app/matching/parser.py
class ParsedJD(BaseModel):
    required_skills: list[str]
    preferred_skills: list[str]
    seniority: str           # junior / mid / senior / lead
    remote_type: str         # remote / hybrid / onsite
    salary_min: int | None
    salary_max: int | None
    years_experience: int | None

def parse_jd(description: str) -> ParsedJD:
    doc = nlp(description)
    # NER for skills (custom spaCy model or rule-based matcher)
    # Regex for salary ranges: \$[\d,]+ ?[kK]?
    # Keyword matching for seniority signals
```

Train or download a skills NER model. `SkillNER` (open source) works well as a starting point.

### Step 3b — Embedding + vector similarity

Embed both the job description and your profile summary, then compute cosine similarity:

```python
# app/matching/embedder.py
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")   # 384-dim, fast
# or "BAAI/bge-large-en-v1.5" for higher accuracy (768-dim)

def embed(text: str) -> list[float]:
    return model.encode(text).tolist()

async def score_job(session, job: JobPosting, profile: UserProfile) -> float:
    job_vec = embed(job.description_raw)
    profile_vec = embed(build_profile_text(profile))
    # store job_vec in job_match.embedding
    # cosine similarity = dot(a,b) / (|a||b|)
    similarity = cosine_similarity(job_vec, profile_vec)
    return similarity
```

Store in pgvector for fast ANN queries later.

### Step 3c — Keyword overlap score

Beyond semantics, hard keyword matching matters (ATS systems care about exact terms):

```python
def keyword_score(parsed_jd: ParsedJD, profile: UserProfile) -> float:
    your_skills = set(s.lower() for s in profile.skills)
    required = set(s.lower() for s in parsed_jd.required_skills)
    preferred = set(s.lower() for s in parsed_jd.preferred_skills)
    
    required_match = len(your_skills & required) / max(len(required), 1)
    preferred_match = len(your_skills & preferred) / max(len(preferred), 1)
    
    return (required_match * 0.7) + (preferred_match * 0.3)
```

### Step 3d — Hard filters

Apply before any LLM cost is incurred:

```python
def passes_filters(job: JobPosting, prefs: UserPreferences) -> bool:
    if job.company in prefs.blacklist_companies:
        return False
    if prefs.salary_floor and job.salary_max and job.salary_max < prefs.salary_floor:
        return False
    if prefs.remote_only and job.remote_type == "onsite":
        return False
    return True
```

### Step 3e — LLM re-ranker (Claude API)

For the top 20 jobs that pass filters and score > 0.5, run a final LLM pass:

```python
# app/llm/ranker.py
async def llm_rank(job: JobPosting, profile: UserProfile) -> tuple[int, str]:
    prompt = f"""
    You are a career advisor. Score this job match from 1-100 and explain why.
    
    CANDIDATE PROFILE:
    {build_profile_text(profile)}
    
    JOB POSTING:
    {job.description_raw[:3000]}
    
    Respond as JSON: {{"score": int, "rationale": str, "strengths": [str], "gaps": [str]}}
    """
    response = await anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return parse_llm_response(response)
```

### Combined score

```python
FINAL_SCORE = (semantic_similarity * 0.4) + (keyword_score * 0.3) + (llm_score/100 * 0.3)
```

### Celery task

```python
@celery_app.task
def score_new_jobs():
    # fetch all JobPostings with no JobMatch record
    # run parser → embedder → keyword scorer → filter → llm ranker
    # save JobMatch records
```

### Deliverable
Every job posting in the DB gets a match score. `SELECT * FROM job_match ORDER BY match_score DESC LIMIT 10` returns sensible top matches.

---

## Phase 4 — Document generation (Days 29–36)

### Goals
Auto-generate a tailored resume variant and cover letter for each high-scoring job.

### Resume tailoring

Strategy: maintain a master resume in structured JSON, then use the LLM to rewrite the summary and reorder bullet points to emphasise skills that match the JD.

```python
# app/llm/resume_tailor.py
async def tailor_resume(base_resume: dict, job: JobPosting) -> str:
    prompt = f"""
    Tailor this resume for the job below. Rules:
    - Do NOT invent experience or skills
    - Rewrite the summary (3 sentences max) to highlight relevant experience
    - Reorder bullet points to put most relevant first
    - Inject keywords naturally: {parsed_jd.required_skills}
    - Output clean markdown
    
    BASE RESUME (JSON):
    {json.dumps(base_resume)}
    
    JOB DESCRIPTION:
    {job.description_raw[:2000]}
    """
    # call Claude API, return markdown string
```

### Cover letter generation

```python
async def generate_cover_letter(job: JobPosting, profile: UserProfile) -> str:
    prompt = f"""
    Write a concise 3-paragraph cover letter.
    Paragraph 1: Why this specific company/role excites me
    Paragraph 2: My top 2 relevant achievements with metrics
    Paragraph 3: Call to action
    
    Tone: professional but warm. No clichés. Max 250 words.
    
    PROFILE: {build_profile_text(profile)}
    JOB: {job.title} at {job.company}
    JD SUMMARY: {job.description_raw[:1500]}
    """
```

### PDF generation

Convert the tailored resume markdown to PDF using WeasyPrint:

```python
# app/documents/pdf_builder.py
from weasyprint import HTML
import markdown

def build_resume_pdf(markdown_content: str) -> bytes:
    html = markdown.markdown(markdown_content)
    styled = f"<style>{RESUME_CSS}</style>{html}"
    return HTML(string=styled).write_pdf()
```

Upload the PDF to S3/MinIO and store the key in `resume_variants.pdf_s3_key`.

### Deliverable
For any job with `match_score > 0.75`, a tailored resume PDF and cover letter text are auto-generated and stored. Inspect them via the Streamlit dashboard.

---

## Phase 5 — Application engine (Days 37–50)

### Goals
Actually submit applications. Start conservatively — human review for everything, then loosen thresholds.

### Form-fill engine (Playwright)

Each job board needs its own "apply strategy". Start with the two most common:

**LinkedIn Easy Apply**
```python
# app/automation/strategies/linkedin.py
async def apply_linkedin(page, job: JobPosting, app: Application):
    await page.goto(job.url)
    await page.click('[aria-label="Easy Apply"]')
    # multi-step form: personal info → resume upload → screening Qs → submit
    await fill_personal_info(page, profile)
    await upload_resume(page, app.resume_pdf_path)
    await handle_screening_questions(page)   # see below
    await page.click('[aria-label="Submit application"]')
```

**Screening questions handler** — the hard part. Most forms have radio buttons, dropdowns, and free-text fields. Use an LLM to answer them:

```python
async def handle_screening_questions(page):
    questions = await extract_questions(page)   # get all visible form labels
    for q in questions:
        answer = await llm_answer_question(q, profile)
        await fill_field(page, q.element, answer)
```

### State machine for application status

```
QUEUED → IN_PROGRESS → APPLIED → [RESPONSE_RECEIVED]
                    ↓
              NEEDS_HUMAN  (CAPTCHA / unusual form / score 50-79)
                    ↓
              SKIPPED / APPLIED (after human action)
```

### Human review queue

Before any auto-submission, all applications land in the review queue. Only graduate to auto-submit once you've reviewed 50+ manually and trust the system.

```python
# API endpoint for the dashboard
GET  /api/applications/pending   # list awaiting human review
POST /api/applications/{id}/approve  # mark for auto-submit
POST /api/applications/{id}/reject   # skip this job
```

### CAPTCHA handling

```python
async def solve_captcha(page) -> bool:
    captcha_img = await page.screenshot(clip=captcha_bbox)
    solution = await twocaptcha_client.solve_image(captcha_img)
    await page.fill('#captcha-input', solution)
    return True
```

For reCAPTCHA v2/v3, use the 2Captcha token injection method.

### Rate limiting & safety

- Max 15 applications per day (avoid looking like a bot to ATS systems)
- Minimum 8 minutes between submissions
- Randomise browser fingerprint between sessions (different viewport, user-agent)
- Store Playwright browser session state (cookies) per platform

### Celery task

```python
@celery_app.task
def process_application_queue():
    # fetch QUEUED applications with score >= AUTO_APPLY_THRESHOLD
    # for each: load strategy, run form-fill, update status
    # respect rate limits via Redis counter
```

### Deliverable
The system can successfully submit a test application on a sandbox / demo form. Human review queue works in the dashboard. Rate limiting is enforced.

---

## Phase 6 — Observability & feedback loop (Days 51–58)

### Goals
Know what's happening, catch failures fast, and use outcomes to improve scoring.

### Reply detector (Gmail integration)

Poll Gmail every 2 hours for recruiter replies using the Gmail API:

```python
# app/monitoring/gmail_watcher.py
def check_for_replies():
    messages = gmail.users().messages().list(
        userId='me',
        q='subject:(application OR interview OR position) newer_than:1d'
    ).execute()
    for msg in messages:
        company = extract_company(msg)
        sentiment = classify_reply(msg.body)  # interview_invite / rejection / auto_ack
        update_application_status(company, sentiment)
```

### Feedback loop

When an application gets a positive outcome (interview invite), update the match scorer:

```python
def record_outcome(application_id: str, outcome: str):
    app = get_application(application_id)
    job = app.job
    # positive signal: increase weight of features this job shared
    # store (job_embedding, outcome) pairs for future fine-tuning
    # short-term: adjust keyword weights based on which skills appeared
    # in successful vs rejected applications
```

### Metrics to track

Store in a `metrics` table and expose via Grafana:

- Applications sent per day
- Match score distribution (histogram)
- Reply rate by source (LinkedIn vs Indeed vs direct)
- Average days to response
- Cover letter word count vs response rate (correlation)
- Cost per application (Claude API tokens used)

### Streamlit dashboard pages

**Page 1 — Review queue**: table of pending applications, match score, rationale. Approve / reject buttons.

**Page 2 — Pipeline**: Kanban-style view (Applied → Replied → Interview → Offer).

**Page 3 — Analytics**: charts for daily applications, reply rates, score distributions.

**Page 4 — Settings**: edit blacklist, adjust score thresholds, toggle auto-apply on/off.

### Alerting

```python
# Slack webhook notifications
NOTIFY_ON = [
    "interview_invite_detected",
    "daily_apply_limit_reached",
    "scraper_error_repeated",
    "captcha_failure_rate_high",
]
```

### Deliverable
Dashboard is live. All application statuses are visible. Slack alerts fire on interview invites and errors.

---

## Phase 7 — Hardening & launch (Days 59–70)

### Goals
Make the system reliable enough to run unattended for weeks.

### Error handling & retries

Every Celery task should have:

```python
@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,    # 5 minutes
    autoretry_for=(ScraperError, NetworkError),
)
def scrape_linkedin(self, ...):
    try:
        ...
    except RateLimitError as e:
        raise self.retry(countdown=3600)  # back off 1 hour
```

### Testing strategy

| Layer | Tool | Coverage target |
|---|---|---|
| Models / schemas | `pytest` | 90% |
| Scraper parsers | `pytest` + recorded HTML fixtures | 80% |
| Matching logic | `pytest` | 85% |
| LLM wrappers | `pytest` + mocked responses | 70% |
| API endpoints | `httpx` + `TestClient` | 80% |
| E2E apply flow | `pytest-playwright` + sandbox form | manual |

### GitHub Actions CI

```yaml
on: [push, pull_request]
jobs:
  test:
    steps:
      - pip install .[dev]
      - alembic upgrade head
      - pytest tests/ --cov=app --cov-report=xml
      - ruff check .
```

### Security checklist

- All secrets in `.env`, never committed
- Rotate API keys every 90 days
- PostgreSQL accessible only within Docker network
- Redis password set in production
- Rate-limit the FastAPI endpoints (`slowapi`)
- Log scrubbing: never log full JD or cover letter text (PII risk)

### Deployment (Railway or VPS)

```
railway up
  → PostgreSQL (managed)
  → Redis (managed)
  → app (FastAPI)
  → worker (Celery)
  → beat (Celery Beat)
  → dashboard (Streamlit, private URL)
```

Set `APPLY_THRESHOLD=0.80` for the first 2 weeks. Lower to `0.70` once you've reviewed 30+ auto-applied jobs and are happy with quality.

---

## Milestone summary

| Phase | Duration | Key deliverable |
|---|---|---|
| 0 — Setup | Days 1–3 | Docker stack running, project skeleton |
| 1 — Data models | Days 4–7 | Schema migrated, seed data loads |
| 2 — Scraping | Days 8–16 | Jobs auto-collected from 2 sources |
| 3 — Matching | Days 17–28 | Every job scored, top matches ranked |
| 4 — Documents | Days 29–36 | Tailored resume + cover letter per job |
| 5 — Applications | Days 37–50 | Human-reviewed submissions working |
| 6 — Observability | Days 51–58 | Dashboard live, reply detection active |
| 7 — Hardening | Days 59–70 | Production-ready, running unattended |

---

## Quick-start checklist (first day)

- [ ] Create GitHub repo
- [ ] Copy `.env.example`, fill in keys
- [ ] `docker compose up -d`
- [ ] `alembic upgrade head`
- [ ] `python scripts/seed.py`
- [ ] Verify `GET http://localhost:8000/healthz` returns `{"status": "ok"}`
- [ ] Open Streamlit at `http://localhost:8501`

---

## Cost estimate (monthly, running at ~15 apps/day)

| Service | Est. cost |
|---|---|
| Claude API (cover letters + ranking) | ~$8–15 |
| Brightdata proxies | ~$20–40 |
| 2Captcha | ~$5–10 |
| Railway hosting | ~$10–20 |
| **Total** | **~$43–85 / month** |

Costs drop significantly if you use Ollama for bulk scoring and only call Claude for final-pass ranking and cover letter generation.
