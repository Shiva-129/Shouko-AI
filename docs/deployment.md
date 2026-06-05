# PaperBrain — Deployment Guide

> MVP deploys on Vercel (frontend) + Railway (backend). Scale path: AWS ECS Fargate.

---

## Environment Variables

### Backend (`apps/api/.env`)

```bash
# ── App ──────────────────────────────────────────────
ENVIRONMENT=development        # development | staging | production
APP_SECRET_KEY=                # 32-char random string (openssl rand -hex 32)
ALLOWED_ORIGINS=http://localhost:3000,https://paperbrain.app

# ── Database ─────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/paperbrain
SUPABASE_URL=https://yourproject.supabase.co
SUPABASE_SERVICE_KEY=          # Service role key (NOT anon key)

# ── Redis ────────────────────────────────────────────
REDIS_URL=redis://localhost:6379
UPSTASH_REDIS_REST_URL=        # Production only
UPSTASH_REDIS_REST_TOKEN=      # Production only

# ── AI APIs ──────────────────────────────────────────
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...          # For text-embedding-3-small only

# ── Storage ──────────────────────────────────────────
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=paperbrain-pdfs
R2_PUBLIC_URL=https://pdfs.paperbrain.app

# ── Payments ─────────────────────────────────────────
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRO_PRICE_ID=price_...
STRIPE_TEAM_PRICE_ID=price_...

# ── Email ────────────────────────────────────────────
RESEND_API_KEY=re_...
FROM_EMAIL=hello@paperbrain.app

# ── Monitoring ───────────────────────────────────────
SENTRY_DSN=https://...@sentry.io/...
LOGFIRE_TOKEN=                 # Logfire (Pydantic) logging
```

### Frontend (`apps/web/.env.local`)

```bash
NEXT_PUBLIC_SUPABASE_URL=https://yourproject.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...    # Anon key (safe for frontend)
NEXT_PUBLIC_API_URL=http://localhost:8000/v1
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_POSTHOG_KEY=phc_...
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_...
```

---

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker Desktop
- psql CLI

### First-time setup

```bash
# 1. Clone
git clone https://github.com/yourname/paperbrain
cd paperbrain

# 2. Start infrastructure
docker-compose up -d
# Starts: postgres (port 5432), redis (port 6379)

# 3. Create DB + enable pgvector
psql postgresql://postgres:localpass@localhost:5432 -c "CREATE DATABASE paperbrain;"
psql postgresql://postgres:localpass@localhost:5432/paperbrain -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 4. Backend setup
cd apps/api
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# → Edit .env with your API keys

# 5. Run migrations
alembic upgrade head

# 6. Start API
uvicorn main:app --reload --port 8000

# 7. Start Celery (new terminal, same venv)
celery -A tasks worker --loglevel=info --concurrency=2

# 8. Start Celery beat (new terminal)
celery -A tasks beat --loglevel=info

# 9. Frontend setup (new terminal)
cd apps/web
npm install
cp .env.local.example .env.local
# → Edit .env.local
npm run dev   # → http://localhost:3000
```

### Docker Compose (local infrastructure only)

```yaml
# infrastructure/docker-compose.yml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: localpass
      POSTGRES_DB: paperbrain
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  postgres_data:
  redis_data:
```

---

## Docker (Production API)

```dockerfile
# infrastructure/Dockerfile.api
FROM python:3.11-slim

WORKDIR /app

# Install system deps for PDF parsing
RUN apt-get update && apt-get install -y \
    libpoppler-cpp-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run as non-root
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

For Celery worker:
```dockerfile
# Same image, different CMD
CMD ["celery", "-A", "tasks", "worker", "--loglevel=info", "--concurrency=4"]
```

---

## Staging Deployment (Railway)

### Setup
1. Create Railway account → New Project
2. Connect GitHub repo
3. Add services: `api`, `celery-worker`, `celery-beat`
4. Add Postgres plugin (Railway managed)
5. Add Redis plugin (Railway managed)

### Railway service config

**API service:**
```
Start command: uvicorn main:app --host 0.0.0.0 --port $PORT
Root directory: apps/api
```

**Celery worker:**
```
Start command: celery -A tasks worker --loglevel=info --concurrency=4
Root directory: apps/api
```

**Celery beat:**
```
Start command: celery -A tasks beat --loglevel=info
Root directory: apps/api
```

### Environment variables
Set all backend env vars in Railway dashboard. Use Railway's Postgres and Redis plugin URLs.

---

## Production Deployment

### Frontend (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# First deploy
cd apps/web
vercel

# Set env vars
vercel env add NEXT_PUBLIC_SUPABASE_URL production
vercel env add NEXT_PUBLIC_API_URL production
# ... add all env vars

# Deploy
vercel --prod
```

Vercel auto-deploys from `main` branch after initial setup.

### Backend (Railway → AWS ECS at scale)

**Railway MVP deploy:**
```bash
# Install Railway CLI
npm i -g @railway/cli

railway login
railway link  # link to your Railway project
railway up    # deploy from current directory
```

**GitHub Actions CI/CD:**
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r apps/api/requirements.txt
      - run: pytest apps/api/tests/ -v
        env:
          DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}

  deploy-api:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Railway
        run: |
          npm i -g @railway/cli
          railway up --service api
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  deploy-web:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Vercel
        run: vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

---

## Database Migrations

Using Alembic for schema migrations.

```bash
# Create new migration
alembic revision --autogenerate -m "add semantic cache table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

**Rule: Never edit migration files after they've been applied to production.**
**Always run `alembic upgrade head` in CI before deploying.**

---

## DNS & SSL

```
paperbrain.app          → Vercel (frontend)
api.paperbrain.app      → Railway/AWS (backend API)
pdfs.paperbrain.app     → Cloudflare R2 (PDF storage)
```

**Cloudflare setup:**
1. Add domain to Cloudflare
2. Point nameservers to Cloudflare
3. Add CNAME records:
   - `@` → Vercel deployment URL
   - `api` → Railway deployment URL
4. Enable proxying (orange cloud) for DDoS protection + SSL
5. SSL: Full (strict) mode
6. Force HTTPS: ON

---

## Production Hardening Checklist

Before going live:

- [ ] All env vars set in production (no .env files on server)
- [ ] CORS restricted to `paperbrain.app` only
- [ ] Rate limiting enabled on all endpoints
- [ ] Stripe webhook signature verification active
- [ ] Sentry DSN configured
- [ ] DB backups enabled (Supabase: automatic)
- [ ] R2 bucket versioning enabled
- [ ] HTTPS enforced (Cloudflare)
- [ ] JWT expiry set to 1 hour (refresh token: 7 days)
- [ ] Celery task timeout set (max 10 min per task)
- [ ] Health check endpoint: `GET /health` returns 200
- [ ] Smoke test: create account → get digest → create artifact → chat

---

## Scaling Path

| Users | Infrastructure | Monthly Infra Cost |
|---|---|---|
| 0–100 | Railway Starter + Supabase Free + Vercel Hobby | ~$20 |
| 100–1K | Railway Pro + Supabase Pro + Vercel Pro | ~$150 |
| 1K–10K | AWS ECS Fargate + RDS Postgres + ElastiCache | ~$800 |
| 10K–100K | ECS auto-scaling + Aurora Serverless + Qdrant cloud | ~$4,000 |
| 100K+ | Multi-region + dedicated embedding service | Custom |

**When to migrate from Railway to AWS:** When monthly Railway bill exceeds $300.

---

## Monitoring & Alerts

### Sentry (errors)
```python
# apps/api/main.py
import sentry_sdk
sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.1)
```

### Health check endpoint
```python
@app.get("/health")
async def health():
    # Check DB connection
    # Check Redis connection
    # Check Claude API (lightweight ping)
    return {"status": "ok", "timestamp": datetime.utcnow()}
```

### Uptime monitoring
Configure Better Uptime to ping `https://api.paperbrain.app/health` every 60 seconds.
Alert channel: Slack #alerts or SMS.

### Cost monitoring
Daily cron job logs total LLM spend to PostHog.
Alert if daily spend > $50 (adjust as revenue grows).
