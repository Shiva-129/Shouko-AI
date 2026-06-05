# PaperBrain — System Architecture

> High-level system design, data flow, and infrastructure decisions.

---

## System Overview

```
┌──────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│              Next.js 14 (Vercel Edge Network)                │
│                                                              │
│  Dashboard │ Artifact View │ Chat Interface │ Digest Feed    │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTPS / SSE
┌────────────────────────▼─────────────────────────────────────┐
│                      BACKEND API                             │
│               FastAPI (Railway / AWS ECS)                    │
│                                                              │
│  routers/ │ services/ │ core/ │ agents/                      │
└─────┬──────────┬──────────┬──────────────────────────────────┘
      │          │          │
      ▼          ▼          ▼
   Supabase   Upstash    Cloudflare
   Postgres    Redis        R2
   pgvector   (cache +   (PDF files)
   (data +    task queue)
   vectors)
      │
      ▼
┌─────────────────────────────────┐
│         CELERY WORKERS          │
│    (Railway / AWS ECS Fargate)  │
│                                 │
│  discovery_agent                │
│  ingestion_agent                │
│  artifact_agent                 │
│  orchestrator                   │
└────────────┬────────────────────┘
             │
     ┌───────┴────────┐
     ▼                ▼
  Anthropic        OpenAI
  Claude API    Embeddings API
  (Sonnet +       (text-embedding
   Haiku)         -3-small)
             │
             ▼
          ArXiv API
       Semantic Scholar API
```

---

## Request Lifecycle

### A. User Asks a Question (Chat)

```
1. User types question in ChatPanel.tsx
2. POST /conversations/{artifact_id}/chat (with Bearer token)
3. FastAPI middleware:
   a. Validate JWT (Supabase)
   b. Check rate limit (Redis: 30/min per user)
   c. Check daily usage limit (usage_events table)
   d. Sanitize input (prompt injection check)
4. rag_service.py:
   a. Embed question → OpenAI text-embedding-3-small
   b. Check semantic cache (Redis) → if hit, stream cached answer
   c. Vector search → pgvector on paper_chunks
   d. Rerank top 8 → keep 5
   e. Load conversation history (last 6 messages from conversations table)
   f. Build prompt with context + history
5. Stream → Claude Sonnet via Anthropic API
6. Log usage event (usage_events table)
7. Update conversation history (conversations table)
8. SSE chunks → frontend
9. Frontend StreamingMessage.tsx renders tokens as they arrive
```

### B. Daily Discovery Agent Run

```
1. APScheduler fires at 6:00 AM UTC
2. Celery task: daily_scan.py
3. For each user with notifications enabled:
   a. Fetch interest_profile from users table
   b. Call arxiv_service.py → fetch last 24h papers for their categories
   c. Filter to max 100 papers
   d. Batch score with Claude Haiku (20 papers per call)
   e. Filter: relevance_score >= 70
   f. Save top 5 to daily_digests table
   g. Send digest email via Resend (if email notifications on)
4. Total per user: ~$0.005 in API costs
```

### C. Artifact Creation

```
1. User clicks [Create Artifact] on a paper
2. POST /artifacts (with paper arxiv_id)
3. FastAPI:
   a. Check usage limit (5/month free, unlimited pro)
   b. Lookup paper in papers table (or create new record)
   c. Create artifact record (status: 'queued')
   d. Dispatch Celery task: process_paper.delay(paper_id, artifact_id, user_id)
   e. Return immediately: {artifact_id, status: 'queued'}
4. Frontend polls GET /artifacts/{id}/status every 3s
5. Celery worker (ingestion_agent.py):
   a. Update status: 'ingesting'
   b. Download PDF from arxiv → store to R2
   c. Extract text (pdfplumber)
   d. Detect sections
   e. Chunk text (512 tokens, 50 overlap)
   f. Batch embed chunks (OpenAI, 100 at a time)
   g. Store chunks + embeddings in paper_chunks table
   h. Update status: 'generating'
6. Celery worker (artifact_agent.py):
   a. Load top chunks by section coverage
   b. Call Claude Sonnet with artifact generation prompt
   c. Validate output (Pydantic)
   d. If validation fails → retry (max 3)
   e. Store artifact data in artifacts table
   f. Generate artifact-level embedding (embed the summary)
   g. Update status: 'ready'
7. Frontend poll detects status = 'ready' → redirect to artifact page
```

---

## Data Flow Diagram

```
ArXiv API ──────────────────────────────────────────────────────┐
                                                                 │
                                                                 ▼
                                                         papers table
                                                                 │
                                                                 ▼
                                                    PDF downloaded to R2
                                                                 │
                                                                 ▼
                                              pdfplumber → text extraction
                                                                 │
                                                                 ▼
                                                  chunking → paper_chunks
                                                                 │
                                                                 ▼
                                             OpenAI embeddings → pgvector
                                                                 │
                                                                 ▼
                                              Claude Sonnet → artifacts table
                                                                 │
                                              ┌──────────────────┘
                                              │
                                              ▼
User question → embed → vector search → chunks → Claude → SSE stream
```

---

## Key Architecture Decisions

### Why FastAPI over Django/Flask?
- Native async support — critical for concurrent LLM streaming calls
- Pydantic-native — automatic request/response validation
- OpenAPI docs auto-generated — useful for frontend team
- Best-in-class performance for I/O-bound AI workloads

### Why LangGraph over LangChain?
- LangGraph supports stateful, cyclical agent workflows (retry loops)
- Better control over agent execution steps
- Easier to debug (explicit graph of nodes and edges)
- LangChain is too abstracted for production AI systems

### Why Celery over FastAPI BackgroundTasks?
- BackgroundTasks die if the API server restarts (PDF processing takes 2 min)
- Celery tasks survive server restarts — jobs don't get lost
- Celery supports task retries with backoff
- Celery Beat handles scheduled daily scans cleanly
- Celery allows scaling workers independently from API

### Why pgvector over Pinecone/Weaviate (at MVP)?
- Same Postgres DB = fewer services to manage
- Supabase includes pgvector out of the box
- Performant up to ~500K vectors
- When to migrate: >500K total chunks or vector queries >200ms

### Why Supabase over raw Postgres?
- Auth built-in (save 2 weeks of auth code)
- Row-Level Security built-in (multi-tenancy for free)
- Realtime subscriptions (artifact status updates)
- Storage (fallback if R2 setup is delayed)
- Managed backups

### Why Cloudflare R2 over AWS S3?
- Zero egress fees (S3 charges for download)
- Same S3-compatible API (easy to switch if needed)
- Integrated with Cloudflare CDN for fast PDF delivery

### Why SSE over WebSocket for chat?
- SSE is simpler: standard HTTP, works through proxies and load balancers
- LLM streaming is one-directional (server → client)
- WebSocket adds complexity without benefit for this use case
- SSE reconnects automatically on connection drop

---

## Security Architecture

```
Internet
   │
   ▼
Cloudflare (DDoS protection + SSL termination + WAF)
   │
   ▼
Vercel (frontend) ←──── Next.js middleware (auth check)
   │
   │ HTTPS only
   ▼
FastAPI (Railway)
   │
   ├── JWT validation (every request)
   ├── Rate limiting (Redis sliding window)
   ├── Usage limit check (DB query)
   ├── Input sanitization (prompt injection)
   ├── CORS (allowed origins only)
   │
   ▼
PostgreSQL (Supabase)
   │
   └── Row-Level Security (data isolation)
```

**Trust boundary:** Everything in FastAPI is considered untrusted input. JWT is validated cryptographically. user_id is always taken from the validated JWT, never from the request body.

---

## Scalability Bottlenecks

| Bottleneck | Hits at | Solution |
|---|---|---|
| pgvector index size | ~500K chunks | Migrate to Qdrant |
| Celery worker concurrency | ~1K concurrent jobs | Add more workers (horizontal scale) |
| API server memory | ~1K concurrent connections | Scale API horizontally (ECS) |
| LLM API rate limits | ~100 req/min (Anthropic default) | Request rate limit increase from Anthropic |
| Postgres connection pool | ~10K users | Add PgBouncer connection pooler |
| ArXiv API rate limit | ~3 req/sec | Implement per-user request queuing |

---

## Multi-tenancy Model

**Approach: Shared database, isolated data via user_id**

- Every table has `user_id` column
- All queries include `WHERE user_id = $current_user_id`
- Supabase RLS adds database-level enforcement as backup
- `papers` table is shared (same paper ≠ duplicated for each user)
- `artifacts`, `conversations`, `annotations` are fully private per user

**No cross-tenant data leakage is possible because:**
1. JWT contains user_id (cryptographically signed)
2. All queries filter by user_id from JWT (not request body)
3. RLS prevents direct DB access from returning other users' data

---

## Monitoring Stack

| Tool | What it monitors | Alert threshold |
|---|---|---|
| Sentry | API errors, frontend errors | Any 5xx error |
| Better Uptime | API health endpoint | Downtime > 2 min |
| PostHog | User behavior, funnel analytics | Manual review |
| Logfire | LLM call logs, agent traces | Cost > $50/day |
| Railway dashboard | CPU, memory, deploy status | CPU > 80% |
