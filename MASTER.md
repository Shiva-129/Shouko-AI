# Shouko-AI — Implementation Status Master Report

> Generated 2026-06-01. Maps every document-planned feature against actual code.

---

## Overall Completion Score

| Area | Done | Missing |
|---|---|---|
| Documentation | 100% | — |
| Backend Models | 100% | — |
| Backend Core Infrastructure | 85% | Auth, rate limiting, usage enforcement |
| Backend Services | 70% | Artifact generation, R2 storage, proper section detection |
| Backend API Routes | 15% | Only 2 of ~25 planned endpoints exist |
| Backend Agents & Prompts | 0% | Entire agents/ and prompts/ directories missing |
| Backend Testing | 5% | 3 manual scripts only; no pytest suite, no evals |
| Frontend | 8% | Single mock page; no components, routes, auth, or data fetching |
| Infrastructure & CI/CD | 20% | Docker Compose only; no app containerization, no CI |
| **System Overall** | **~30%** | Core data models and service engine built; everything else is scaffolding or missing |

---

## Phase 1 MVP — Week-by-Week Status

### Week 1: Foundation & Infrastructure

| Task | Status | Reality |
|---|---|---|
| Initialize monorepo structure | ⚠️ Partial | `apps/web/` and `apps/api/` exist. `packages/` does NOT exist. No root `package.json`. |
| Set up Next.js 14 + Tailwind + shadcn/ui | ⚠️ Partial | Next.js 14 runs, Tailwind configured with custom design tokens. shadcn/ui **NOT installed** — not in package.json, no `components.json`, no `ui/` directory. |
| Set up FastAPI with Pydantic, CORS, health check | ✅ Done | `main.py` fully implemented with CORS, exception handlers, `/health` endpoint |
| Set up Supabase project (pgvector, RLS) | ❌ Not Started | No Supabase connection in code. `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` exist in config but have empty defaults. |
| Docker Compose for local Postgres + Redis | ✅ Done | `docker-compose.yml` works — pgvector + Redis |
| Implement auth (Supabase Google OAuth + email) | ❌ Not Started | `dependencies.py` has `MockUser` class. No real JWT validation, no Supabase auth integration. |
| Protected routes (Next.js middleware) | ❌ Not Started | No `middleware.ts` exists |
| Deploy frontend to Vercel | ❌ Not Started | No Vercel config, no deployments |
| Deploy backend to Railway (staging) | ❌ Not Started | No Railway config |
| GitHub Actions test + deploy pipeline | ❌ Not Started | `.github/workflows/` does not exist |
| Cloudflare domain + DNS | ❌ Not Started | No domain configured |

### Week 2: ArXiv Discovery Agent

| Task | Status | Reality |
|---|---|---|
| Implement ArXiv API wrapper | ✅ Done | `tasks/digest_tasks.py` uses the `arxiv` Python library to search by category |
| Interest profile onboarding UI | ❌ Not Started | No settings/interests page on frontend |
| Save interest profile to users table | ✅ Done | `User.interest_profile` column exists (JSONB with topics/keywords/authors/categories) |
| Build discovery agent (fetch → score → filter) | ⚠️ Partial | Celery task `scan_daily_research_papers` fetches papers but does **NOT** score with Claude Haiku. It just stores them. The interest-matching logic in `digest_service.py` uses simple keyword matching (not LLM). |
| Store results in papers + daily_digests tables | ✅ Done | Both models exist and are populated |
| APScheduler job at 6 AM UTC | ❌ Not Started | No APScheduler installed. Relies on Celery Beat (manual setup, not automated). |
| Digest UI page | ❌ Not Started | No `/digest/[date]` route exists |
| Manual "Run digest now" button | ❌ Not Started | No button exists |

### Week 3: PDF Ingestion Pipeline

| Task | Status | Reality |
|---|---|---|
| Cloudflare R2 setup | ❌ Not Started | No R2 integration. PDFs are downloaded to local temp files only. |
| PDF download from ArXiv | ✅ Done | `ingestion_service.py` downloads via httpx |
| pdfplumber text extraction | ❌ Not Started | Uses PyMuPDF (`fitz`) only. pdfplumber is in requirements.txt but unused. |
| pymupdf fallback | ❌ N/A | pymupdf is the primary (not a fallback), contrary to docs |
| Text chunking (512 tokens, 50 overlap) | ✅ Done | `pdf_service.py` `chunk_text()` with sliding window of 512 words/50 overlap |
| Section detection | ⚠️ Basic | Heuristic detection of abstract/introduction/methods/references by first 150 chars only. Not the sophisticated approach in docs. |
| Batch embedding (OpenAI) | ✅ Done | `embedding_service.py` batches all chunks in one API call |
| Store chunks in paper_chunks with embeddings | ✅ Done | `paper_chunks` table populated with Vector(1536) |
| Celery task: process_paper.py | ⚠️ Partial | No separate Celery task. Ingestion runs synchronously via the endpoint router. |
| Track paper ingestion status | ✅ Done | `paper.pdf_processed` and `pdf_processed_at` are set |
| Error handling for malformed PDFs | ⚠️ Basic | Generic try/except with rollback. No specific PDF validation. |

### Week 4: Artifact Generator Agent

| Task | Status | Reality |
|---|---|---|
| Artifact generation prompt | ❌ Not Started | `prompts/` directory does not exist |
| Artifact agent (load chunks → Claude Sonnet → validate) | ❌ Not Started | `agents/` directory does not exist. No code calls Claude for artifact generation. |
| Celery task: generate_artifact.py | ❌ Not Started | File does not exist |
| POST /artifacts endpoint | ❌ Not Started | No artifacts router exists |
| GET /artifacts/{id}/status | ❌ Not Started | Not implemented |
| GET /artifacts/{id} | ❌ Not Started | Not implemented |
| Artifact detail page | ❌ Not Started | No `/artifact/[id]` route exists |
| Usage limit enforcement (5/month free) | ❌ Not Started | No usage checking middleware exists |

### Week 5: Chat Interface (RAG)

| Task | Status | Reality |
|---|---|---|
| RAG service (embed → vector search → rerank → context) | ✅ Done | `rag_service.py` has `retrieve_context_chunks()` (pgvector cosine distance) and `compile_rag_prompt()`. No separate reranking step — uses raw similarity ordering. |
| RAG Q&A prompt | ✅ Done | System/user prompt compiled inline in `rag_service.py` |
| SSE streaming endpoint | ✅ Done | `POST /conversations/{artifact_id}/chat` streams via SSE token-by-token |
| Conversation history | ✅ Done | Stored in `conversations` table as JSONB messages array |
| ChatPanel component | ⚠️ Basic | Inline chat UI in `page.tsx` (not a separate component) |
| StreamingMessage component | ⚠️ Basic | Inline rendering in `page.tsx` |
| Rate limiting (30 questions/min) | ❌ Not Started | No rate limiter exists |
| Daily usage limit (20 questions/day free) | ❌ Not Started | Not enforced |
| Semantic cache (Redis) | ❌ Not Started | Not implemented |

### Week 6: Full UI & Dashboard

| Task | Status | Reality |
|---|---|---|
| Dashboard page | ⚠️ Proto | `page.tsx` (1404 lines) is a single mock-dashboard with 6 hardcoded papers, mindmap, and chat. No real data. |
| Library page | ❌ Not Started | No route, no page |
| Artifact detail page | ❌ Not Started | No route, no page |
| ArtifactCard component | ❌ Not Started | No components/ directory exists |
| StatusBadge | ❌ Not Started | Not created |
| Empty states | ❌ Not Started | Not created |
| Loading skeletons | ❌ Not Started | Not created |
| Settings page | ❌ Not Started | No route, no page |
| Mobile responsiveness | ❌ Not Started | No responsive breakpoints |
| Usage limit banner | ❌ Not Started | Not created |
| Error boundary | ❌ Not Started | Not created |
| Toast notifications | ❌ Not Started | Not created |

### Week 7: Payments + Polish

| Task | Status | Reality |
|---|---|---|
| Stripe products | ❌ Not Started | No Stripe integration exists |
| POST /billing/create-checkout-session | ❌ Not Started | No billing router |
| POST /billing/webhook | ❌ Not Started | No webhook handler |
| Update user plan on webhook | ❌ Not Started | Not implemented |
| Billing settings page | ❌ Not Started | No route |
| Upgrade prompt modal | ❌ Not Started | Not created |
| Resend daily digest email | ✅ Done | `email_service.py` with Resend API integration + HTML template + sandbox fallback |
| Resend welcome email | ❌ Not Started | Not implemented |
| Sentry error tracking | ❌ Not Started | DSN listed in config but no Sentry init in code |
| PostHog analytics | ❌ Not Started | Not implemented |
| Rate limit middleware | ❌ Not Started | Not created |
| Full QA pass | ❌ Not Started | Not done |

### Week 8: Launch Preparation

| Task | Status | Reality |
|---|---|---|
| Landing page | ❌ Not Started | No marketing page routes |
| Production environment | ❌ Not Started | No deployment configs |
| Production smoke test | ❌ Not Started | Not done |
| Onboarding flow | ❌ Not Started | Not created |
| Show HN / Product Hunt prep | ❌ Not Started | Not done |
| Beta user recruitment | ❌ Not Started | 10 carousel/ marketing images exist, but no actual user outreach |
| Load testing | ❌ Not Started | Not done |

---

## What Actually Works (End-to-End)

These flows work when you run the system:

| Flow | What Happens |
|---|---|
| **Paper Ingestion** | `POST /papers/ingest` → downloads PDF → extracts text with PyMuPDF → chunks into 512-word windows → generates OpenAI embeddings → stores in `paper_chunks` table with pgvector |
| **RAG Chat** | `POST /conversations/{artifact_id}/chat` → embeds query → pgvector cosine search → compiles prompt with history → streams Claude/Gemini/OpenRouter response via SSE → stores conversation history |
| **Daily Digest** | Celery task searches ArXiv by user interest categories → stores new papers → matches against user profiles by keyword → compiles HTML email → sends via Resend (or writes to sandbox_emails/) |
| **Frontend Demo** | `npm run dev` shows a 1404-line mock dashboard with 6 paper cards, draggable mindmap, simulated chat streaming (real SSE if backend at localhost:8000) |
| **Local Infrastructure** | `docker compose up` starts pgvector Postgres + Redis with health checks |

---

## What's Implemented vs Document Architecture

### Backend: Planned Structure vs Reality

| Planned (CLAUDE.md) | Reality |
|---|---|
| 6 routers (papers, artifacts, conversations, digests, users, billing) | **2 routers** (papers, chat) |
| 4 agents (discovery, ingestion, artifact, orchestrator) | **0 agents** — all logic lives in services/ |
| 3 prompt files (discovery.py, artifact_generation.py, rag_qa.py) | **0 prompt files** — prompts are inline strings in services |
| LangGraph for agent orchestration | **Not used** — no langgraph dependency |
| APScheduler for daily scans | **Not used** — Celery Beat only |
| pdfplumber primary, pymupdf fallback | **PyMuPDF only** — pdfplumber unused |
| Cloudflare R2 for PDF storage | **Not used** — local temp downloads only |
| Semantic cache (Redis) | **Not implemented** |
| Eval suite (tests/evals/) | **Not created** |
| 70% test coverage | **No test files at all** (3 manual scripts only) |
| Supabase Auth with JWT validation | **MockUser** hardcoded in dependencies.py |

### Frontend: Planned Structure vs Reality

| Planned (CLAUDE.md) | Reality |
|---|---|
| 7 route groups (auth, dashboard, library, artifact, digest, collections, settings) | **1 page** (`app/page.tsx`) — all UI in one file |
| 15+ components across 6 directories | **0 components** — all UI inlined in page.tsx |
| TanStack Query for data fetching | **Not installed** — no tanstack/react-query in package.json |
| Supabase Auth middleware | **Not implemented** — no supabase-js, no middleware.ts |
| Zustand store | **Installed but unused** — no store/ directory |
| API client (lib/api.ts) | **Not created** |
| shadcn/ui component library | **Not installed** — no shadcn init, no components.json |
| TypeScript type definitions | **No types/ directory** |

---

## Database: Models vs Migrations

All **9 SQLAlchemy models** are fully defined with columns, constraints, foreign keys, and indexes matching the docs specification. However:

- `alembic/versions/` is **empty** — zero migrations have been generated
- No database has ever been created from these models
- Tests run against mock data or empty DBs handled gracefully

---

## LLM Architecture: Planned vs Reality

| Planned (ai-architecture.md) | Reality |
|---|---|
| Claude Sonnet for artifact generation + chat | **Multi-provider fallback chain**: Gemini → OpenRouter → Anthropic → mock |
| Claude Haiku for discovery scoring | **Not used** — keyword matching instead |
| text-embedding-3-small for embeddings | ✅ Used (with deterministic mock fallback) |
| Batch scoring 20 papers per LLM call | **Not implemented** — no LLM scoring at all |
| $0.09 per artifact cost estimation | **Not relevant** — artifact generation doesn't exist |
| Artifact caching (same paper = never regenerate) | **Not applicable** — no artifact generation |

---

## Security: Planned vs Reality

| Planned (security.md) | Reality |
|---|---|
| JWT validation with Supabase RS256 | **Mock auth** — any Bearer token accepted |
| Rate limiting (Redis sliding window) | **Not implemented** |
| Prompt injection prevention | **Not implemented** |
| PDF validation (magic bytes, max 50MB) | **Not implemented** — no file upload endpoint exists |
| Row-Level Security on all tables | **Not set up** — no Supabase connection, no RLS-enabled DB exists |
| Usage limit enforcement | **Not implemented** |
| Content filtering | **Not implemented** |
| Input sanitization | **Not implemented** |
| GDPR data export/delete | **Not implemented** |

---

## Priority Roadmap to MVP Completion

### Critical Path (Core Product Loop Broken Without These)

1. **Real Auth** — Replace MockUser with Supabase JWT validation. Create `middleware.ts`. Set up login/signup pages.
2. **Artifact Generator** — Build `agents/artifact_agent.py`, `prompts/artifact_generation.py`. Call Claude Sonnet to generate summary, insights, Q&A, experiments from ingested chunks. Create `POST /artifacts` and `GET /artifacts/{id}` endpoints.
3. **Discovery Agent (real scoring)** — Add Claude Haiku batch scoring (20 papers/call) instead of keyword matching in digest_service.py.
4. **Frontend pages** — Break 1404-line page.tsx into components. Create `/dashboard`, `/library`, `/artifact/[id]`, `/digest/[date]`, `/settings`, `/login`, `/signup` routes.
5. **Usage limits & billing** — Implement usage tracking middleware, Stripe checkout, plan upgrade flow.

### High Priority (Product Incomplete Without These)

6. **Alembic migrations** — Generate initial migration from models, test against real DB.
7. **Rate limiting** — Implement Redis sliding window rate limiter on all endpoints.
8. **API client & TanStack Query** — Wire frontend to real backend (not mock data).
9. **Error handling & loading states** — Every async component needs skeletons, error boundaries, empty states.
10. **Semantic cache** — Skip LLM call for near-identical questions on same artifact.

### Medium Priority (Needed Before Launch)

11. **Cloudflare R2 integration** — Store PDFs, not just download to temp.
12. **PDF validation** — Magic bytes check, size limit, malware scanning.
13. **Prompt injection prevention** — Input sanitization before LLM calls.
14. **Section-aware chunking** — Upgrade from heuristic first-150-char detection to proper section boundary detection.
15. **Sentry + PostHog** — Initialize error tracking and analytics.
16. **shadcn/ui initialization** — Run `npx shadcn-ui init` and build proper component library.
17. **Reranking** — Add simple cross-encoder or keyword+semantic reranking between vector search and prompt assembly.

### Low Priority (Launch Without These)

18. **Packages/shared-types** — Shared TypeScript types package.
19. **Landing page** — Marketing site.
20. **CI/CD pipelines** — GitHub Actions for test + deploy.
21. **Eval suite** — 50 gold-standard papers for LLM quality testing.
22. **Orchestrator agent** — Multi-paper cross-referencing (Phase 2).
23. **APScheduler** — Replace Celery Beat or keep as-is.

---

## Files That Need to Be Created (from Scratch)

```
Backend:
  apps/api/agents/discovery_agent.py
  apps/api/agents/artifact_agent.py
  apps/api/agents/orchestrator.py
  apps/api/prompts/discovery.py
  apps/api/prompts/artifact_generation.py
  apps/api/prompts/rag_qa.py
  apps/api/routers/artifacts.py
  apps/api/routers/users.py
  apps/api/routers/digests.py
  apps/api/routers/billing.py
  apps/api/routers/annotations.py
  apps/api/routers/collections.py
  apps/api/tasks/process_paper.py
  apps/api/tasks/generate_artifact.py
  apps/api/core/rate_limit.py
  apps/api/core/security.py (real JWT validation)
  apps/api/tests/ (entire directory structure)

Frontend:
  apps/web/.env.local
  apps/web/middleware.ts
  apps/web/next.config.ts (or next.config.mjs)
  apps/web/components/ (entire directory tree)
  apps/web/store/useAppStore.ts
  apps/web/types/index.ts
  apps/web/lib/api.ts
  apps/web/lib/supabase.ts
  apps/web/lib/hooks/useArtifact.ts
  apps/web/lib/hooks/useDigest.ts
  apps/web/lib/hooks/useUsage.ts
  apps/web/app/(auth)/login/page.tsx
  apps/web/app/(auth)/signup/page.tsx
  apps/web/app/(dashboard)/layout.tsx
  apps/web/app/(dashboard)/dashboard/page.tsx
  apps/web/app/(dashboard)/library/page.tsx
  apps/web/app/(dashboard)/artifact/[id]/page.tsx
  apps/web/app/(dashboard)/digest/[date]/page.tsx
  apps/web/app/(dashboard)/collections/page.tsx
  apps/web/app/(dashboard)/settings/page.tsx
  apps/web/app/(dashboard)/settings/billing/page.tsx
  apps/web/app/(dashboard)/settings/interests/page.tsx

Infrastructure:
  packages/shared-types/ (entire directory)
  infrastructure/Dockerfile.api
  infrastructure/Dockerfile.celery
  infrastructure/nginx.conf
  .github/workflows/deploy.yml
  .github/workflows/test.yml
```

---

## Key Metrics

| Metric | Count |
|---|---|
| Python files with real implementation | 22 |
| TypeScript files with real implementation | 4 |
| SQLAlchemy models | 9 (all complete) |
| API endpoints implemented | 3 (`/health`, `/papers/ingest`, `/conversations/{id}/chat`) |
| API endpoints in docs spec | ~25 |
| Backend services | 7 |
| Celery tasks | 2 |
| Frontend pages | 1 (mock dashboard) |
| Frontend pages planned | ~15 |
| Docker containers defined | 2 (both infrastructure only) |
| Test files | 3 (manual scripts, no test framework) |
| Lines of documentation | ~2,800 (excellent) |
| Lines of backend implementation code | ~1,600 |
| Lines of frontend implementation code | ~1,400 (single file) |
