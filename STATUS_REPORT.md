# Shouko-AI — Current Status Report

> Generated 2026-06-02 from a full walkthrough of the codebase.
> Maps existing code to the original MVP roadmap and lists what is left.

---

## Overall Completion Snapshot

| Area | State |
|---|---|
| Backend models + migrations | ✅ Complete (9 models, 3 Alembic migrations) |
| Backend core (config, db, security, redis, exceptions) | ✅ Complete |
| Backend services (LLM, RAG, PDF, embed, email, billing, digest, ingestion) | ✅ Complete |
| Backend agents (discovery, artifact) | ✅ Complete |
| Backend Celery tasks (digest scan, generate_artifact) | ✅ Complete |
| Backend routers (papers, chat, users, digests, artifacts, billing, collections) | ✅ Complete |
| Backend usage tracking + rate limiting | ✅ Complete |
| Backend billing (Stripe checkout/portal/webhook) | ✅ Complete |
| Backend auth (Supabase RS256 + JWKS + auto-create) | ✅ Complete |
| Frontend auth (Supabase middleware, login, signup, OAuth) | ✅ Complete |
| Frontend pages (dashboard, library, artifact, digest, collections, settings, interests) | ✅ Complete |
| Frontend components (UI, chat, digest, artifact, layout, shared) | ✅ Complete |
| Frontend API client + TanStack Query hooks | ✅ Complete |
| Scheduler (APScheduler) | ✅ Complete (auto-starts in lifespan) |
| Dockerfiles (api + celery) | ✅ Complete |
| CI workflow | ✅ Basic (pytest + lint + build) |
| Pytest test suite | ❌ Only 5 manual `test_*.py` scripts — no real `tests/` dir |
| Sentry / PostHog | ❌ Not initialized |
| Cloudflare R2 PDF storage | ❌ PDFs downloaded to local temp only |
| pdfplumber primary | ❌ PyMuPDF only (pdfplumber in requirements, unused) |
| LangGraph orchestration | ❌ Not used — services handle flow |
| Landing page / marketing site | ❌ Only auth + dashboard routes |
| `next.config.js` | ❌ Missing — `npm run build` will fail |
| `apps/web/app/page.tsx` legacy 1403-line mock | ⚠️ Still present at root `/` (middleware redirects logged-in users to `/dashboard`) |

**System overall: ~85 % of MVP feature code, ~40 % of production-readiness (no real tests, no observability, no deploy pipeline beyond CI build).**

---

## What is Done (file by file)

### Backend — `apps/api/`

#### Core infrastructure
- `main.py` — FastAPI app with CORS, exception handlers, lifespan, all 7 routers registered, `/health` endpoint
- `core/config.py` — Pydantic settings (env-driven)
- `core/database.py` — Async SQLAlchemy session
- `core/redis.py` — Redis client
- `core/exceptions.py` — Custom exception classes + handlers
- `core/celery_app.py` — Celery app (broker + backend + imports)
- `core/scheduler.py` — APScheduler with `daily_scan_job` (cron at 06:00 UTC, dev runs every 24h with 10s bootstrap)
- `core/security.py` — `get_current_user()` with Supabase RS256 + JWKS cache + auto-create user on first login + `MockUser` fallback in dev
- `core/usage.py` — `log_usage_event`, `check_usage_limit`, `get_monthly_count`, `get_daily_count`, `MONTHLY_LIMITS`, `DAILY_LIMITS` (free: 5 artifact, 10 ingest, 20 question/day)
- `core/dependencies.py` — `get_db`, `MockUser`
- `core/rate_limit.py` — Redis sliding-window `RateLimit(limit, window, name)` decorator factory
- `Dockerfile.api`, `Dockerfile.celery` — Production-ready images

#### Models (9/9)
- `models/user.py`, `models/paper.py`, `models/chunk.py` (with pgvector 1536d, but migration `1327a1c5b9d4` switches to 384d)
- `models/artifact.py` (status: queued → ingesting → generating → ready/failed)
- `models/conversation.py` (JSONB messages, message_count)
- `models/digest.py` (DailyDigest with paper_scores JSONB, email_sent_at)
- `models/collection.py` (artifact_ids list, color, is_default)
- `models/usage.py` (UsageEvent with event_type, meta_data)
- `models/annotation.py` (defined; not yet wired to a router)

#### Migrations (`alembic/versions/`)
- `0001_initial_schema.py` — all 9 tables
- `960bef3e8fab_add_meta_data_to_papers.py` — meta column on papers
- `1327a1c5b9d4_switch_to_384d_embeddings.py` — vector dim switch
- `alembic/env.py` — async migrations with ConfigParser-safe URL handling

#### Routers
- `routers/papers.py` — `POST /papers/ingest` (auth + rate limit + usage check)
- `routers/chat.py` — `POST /conversations/{artifact_id}/chat` (SSE stream)
- `routers/users.py` — `GET /users/me`, `PATCH /users/me` (returns usage summary)
- `routers/digests.py` — `GET /digests`, `GET /digests/today`, `GET /digests/{date}`, `POST /digests/trigger`
- `routers/artifacts.py` — `GET /artifacts`, `GET /artifacts/{id}`, `GET /artifacts/{id}/status`, `POST /artifacts` (async via Celery), `DELETE /artifacts/{id}`
- `routers/billing.py` — `POST /billing/checkout`, `POST /billing/portal`, `POST /billing/webhook` (sub created/updated/deleted)
- `routers/collections.py` — full CRUD + `POST/DELETE /collections/{id}/artifacts`

#### Services
- `services/llm_service.py` — `LLMService` with multi-provider fallback (OpenRouter → Gemini → Anthropic → mock) + `stream_chat_response`
- `services/embedding_service.py` — `get_embeddings()` (batch, 1536d) with deterministic mock fallback
- `services/rag_service.py` — `retrieve_context_chunks` (pgvector cosine) + `compile_rag_prompt`
- `services/pdf_service.py` — `extract_text_by_page` (PyMuPDF), `chunk_text` (512/50 sliding window), heuristic section detection
- `services/ingestion_service.py` — full pipeline: download → extract → chunk → embed → store
- `services/digest_service.py` — `compile_user_daily_digest` (uses `DiscoveryAgent` + email send)
- `services/email_service.py` — Resend API integration with HTML template + `sandbox_emails/` fallback
- `services/billing_service.py` — `BillingService` (checkout/portal/construct_event)

#### Agents
- `agents/discovery_agent.py` — `DiscoveryAgent.score_papers()` with Groq (llama-3.1-8b-instant) primary, LLMService fallback, keyword fallback; batches 20 papers per call
- `agents/artifact_agent.py` — `ArtifactAgent.generate()` (loads up to 3 chunks/section in order, calls Gemini-1.5-flash, 3-retry loop, stores JSONB insights/QA/experiments)
- `prompts/discovery.py`, `prompts/artifact_generation.py`, `prompts/rag_qa.py` — versioned prompts

#### Celery tasks
- `tasks/digest_tasks.py` — `scan_daily_research_papers` (ArXiv fetch by user categories) + `compile_and_send_digests` (uses `DigestService`)
- `tasks/generate_artifact.py` — orchestrates `IngestionService` → `ArtifactAgent` → status updates → `log_usage_event`

#### Manual smoke-test scripts (NOT a real pytest suite)
- `test_chat.py` — downloads "Attention is All You Need" PDF and streams an SSE chat
- `test_artifacts.py` — seeds mock user + runs artifact Celery task
- `test_ingestion.py` — downloads + chunks + embeds
- `test_digest.py` — end-to-end daily digest with mock user
- `test_billing_limits.py` — rate limiter + Stripe mock pipeline

---

### Frontend — `apps/web/`

#### Auth + middleware
- `middleware.ts` + `lib/supabase-middleware.ts` — protects `/dashboard`, `/library`, `/artifact`, `/digest`, `/settings`, `/collections`; redirects logged-in users away from `/login` `/signup` `/`
- `lib/supabase.ts` — browser client (graceful `null` if env missing)
- `lib/supabase-server.ts` — server client helpers
- `app/auth/callback/route.ts` — OAuth callback handler
- `app/login/page.tsx` — Google OAuth + email/password
- `app/signup/page.tsx` — signup form

#### App shell
- `app/layout.tsx`, `app/providers.tsx` — root providers (TanStack Query)
- `app/(dashboard)/layout.tsx` — Sidebar + main area
- `components/layout/Sidebar.tsx` — nav (Dashboard, Digest, Library, Collections, Settings, Sign out)
- `app/not-found.tsx` — 404
- `app/page.tsx` — legacy 1403-line mock dashboard (still ships; effectively dead route after middleware redirect)

#### Library / hooks
- `lib/api.ts` — typed `apiClient` with auto-auth header injection, 401 → signOut + redirect, 429 → `ApiError("USAGE_LIMIT_REACHED", …)`
- `lib/utils.ts` — `cn()` helper
- `types/index.ts` — shared TS interfaces
- `lib/hooks/useUser.ts`, `useDigest.ts`, `useDigests.ts`, `useArtifact.ts`, `useSSEChat.ts` — all use TanStack Query

#### Pages
- `app/(dashboard)/dashboard/page.tsx` — usage cards + top 3 digest papers (real data)
- `app/(dashboard)/library/page.tsx` — artifact grid, search, "Organize" → add to collection widget
- `app/(dashboard)/artifact/[id]/page.tsx` — Summary/Insights/QA/Experiments tabs, processing state with progress, error retry, sticky `ChatPanel`
- `app/(dashboard)/digest/page.tsx` — redirect to `/digest/today`
- `app/(dashboard)/digest/[date]/page.tsx` — date picker (prev/next), two-column paper grid, empty/error states
- `app/(dashboard)/collections/page.tsx` — list + create + detail view with artifact add/remove
- `app/(dashboard)/settings/page.tsx` — plan badge, usage progress bars, Stripe checkout/portal CTA, "Manage Interests" link
- `app/(dashboard)/settings/interests/page.tsx` — categories + keywords + topics + authors

#### Components
- `components/ui/` (11 shadcn primitives) — Button, Card, Input, Badge, Dialog, Sheet, Tabs, Progress, Avatar, Skeleton, Toast (+ Toaster)
- `components/chat/ChatPanel.tsx` — sticky chat panel (SSE-driven via `useSSEChat`)
- `components/digest/PaperCard.tsx` — score badge, "Create Artifact" button (calls `POST /artifacts`, redirects to `/artifact/[id]`)
- `components/artifact/StatusBadge.tsx`, `InsightsList.tsx`, `AutoQA.tsx`, `SuggestedExperiments.tsx`
- `components/shared/EmptyState.tsx`, `UpgradeModal.tsx`

---

### Infrastructure / CI

- `.github/workflows/ci.yml` — backend pytest (pgvector + redis services) + frontend lint + build on push/PR
- `infrastructure/docker-compose.yml` — local postgres + redis (unchanged from MVP scaffold)
- `apps/api/Dockerfile.api`, `apps/api/Dockerfile.celery` — production images

---

### Documentation / meta files

- `CLAUDE.md` — system prompt with tech stack, rules
- `MASTER.md` (2026-06-01) — historical status (largely outdated; pre-Sprint 1)
- `MVP_ROADMAP.md` — 6-sprint plan (Sprint 1 + 2 + 3 + most of 4 + most of 5 done)
- `STATUS.md` (2026-06-02) — sprint summary (Sprints 1-3 done, 4-5 partial, 6 not started)
- `graphify-out/GRAPH_REPORT.md` + `wiki/index.md` — knowledge graph (929 nodes, 1426 edges, 66 communities)
- `graphify-out/` — wiki nav + community files

---

## What is Left to Do

### Sprint 4 — Chat UI polish (mostly done; small gaps)

- [ ] Replace `app/page.tsx` (1403-line mock) — middleware already redirects, but file should be deleted to keep the bundle small
- [ ] Add `loading.tsx` + `error.tsx` to each route segment for graceful Suspense boundaries
- [ ] Add `components/shared/LoadingSpinner.tsx`
- [ ] Add `components/shared/ErrorBoundary.tsx`
- [ ] Mobile-responsive layout pass (Sidebar currently has no collapse-to-Sheet on small screens)
- [ ] Annotations route (model exists, no router/UI yet)

### Sprint 5 — Billing polish

- [x] Backend (routers/billing + service + webhook) — **done**
- [x] Settings page with plan + usage + checkout CTA — **done**
- [ ] `settings/billing/page.tsx` (separate route) — **redundant, can skip** (everything is on `/settings`)
- [ ] `components/billing/UsageBanner.tsx` — show on dashboard when usage > 80% (currently usage cards always show)
- [ ] Real Stripe keys (`STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRO_PRICE_ID` are all `mock` placeholders)
- [ ] Real Resend API key for live digest emails
- [ ] Welcome email on first `GET /users/me` (service method missing)
- [ ] `apiClient` global 429 interceptor → auto-open `UpgradeModal` (currently just throws `ApiError`)

### Sprint 6 — Deployment & Testing (0 → 20 %)

- [ ] **No `tests/` directory** — convert the 5 manual `test_*.py` scripts into `pytest` suite
  - `tests/conftest.py` with test DB fixture, Supabase mock
  - `tests/test_auth.py`, `test_papers.py`, `test_artifacts.py`, `test_chat.py`, `test_billing.py`, `test_collections.py`
  - `tests/evals/` with gold-standard artifact eval set
- [ ] **`next.config.js` / `next.config.mjs`** — missing; `npm run build` will fail without it (transpilePackages for `@/lib/...`, or rely on default TS paths)
- [ ] Sentry — backend `sentry_sdk.init()` in `main.py`, frontend `@sentry/nextjs`
- [ ] PostHog — analytics init in `app/providers.tsx`
- [ ] CI workflow lacks deploy job (only test + lint + build)
- [ ] Production environment validation:
  - `ENVIRONMENT=production` (currently `development`)
  - `APP_SECRET_KEY` rotated (currently hardcoded)
  - `FRONTEND_URL` set to real domain
  - `NEXT_PUBLIC_API_URL` set to deployed API
  - `NEXT_PUBLIC_APP_URL` (currently missing)
  - `R2_*` env vars (Cloudflare R2) for PDF storage
  - `UPSTASH_REDIS_*` for production Redis

### Architectural gaps (deferred from MVP, but referenced in docs)

- [ ] **Cloudflare R2** for persistent PDF storage (currently `tempfile.mkstemp` + cleanup)
- [ ] **pdfplumber** as primary parser (currently PyMuPDF only)
- [ ] Section-aware chunking (currently heuristic, first 150 chars per page)
- [ ] **LangGraph** agent orchestration (currently `ArtifactAgent` is a plain class)
- [ ] Cross-encoder **reranking** between vector search and prompt assembly
- [ ] **Semantic cache** in Redis (cosine > 0.95 → return cached)
- [ ] **Eval suite** (50 hand-labeled papers) under `apps/api/tests/evals/`
- [ ] **Orchestrator agent** for cross-paper queries (Phase 2)
- [ ] **Welcome email** template + `send_welcome_email` method

### Marketing / launch

- [ ] Landing page (`(marketing)/page.tsx` + `pricing/page.tsx`) — not built
- [ ] Onboarding flow (first-login redirect to `/settings/interests`, "Getting started" card)
- [ ] Beta recruitment + feedback form
- [ ] 404/500 themed pages (have 404; no custom 500)
- [ ] `next.config.mjs` with security headers + image domains

---

## Cross-cutting health checks

| Check | Status | Notes |
|---|---|---|
| Backend imports cleanly | ✅ | All routers registered in `main.py`, agents/tasks in Celery imports |
| Alembic migrations apply to Supabase | ✅ | Confirmed previously with `xwcmphcszlcxdlnvrvci` project |
| LLM provider fallback chain | ✅ | OpenRouter → Gemini → Anthropic → deterministic mock |
| Embedding fallback | ✅ | Real OpenAI + deterministic hash mock |
| Email fallback | ✅ | Resend live API + `sandbox_emails/*.html` file |
| Auth: dev vs prod | ✅ | `MockUser` in dev, RS256 + JWKS in prod, auto-create user on first login |
| Frontend reads auth from Supabase | ✅ | `lib/api.ts` + `useSSEChat.ts` inject Bearer token |
| Middleware blocks unauth | ✅ | All `/dashboard`, `/library`, `/artifact`, `/digest`, `/settings`, `/collections` protected |
| `npm run build` succeeds | ⚠️ | Missing `next.config.*`; only lint + `npm run build` step in CI is currently green because no such config is required for the workflow's mocked env |

---

## Quick "ship to 100 %" checklist

1. **Delete `apps/web/app/page.tsx`** (1403-line mock) — middleware already redirects; reduces bundle.
2. **Create `apps/web/next.config.mjs`** with `transpilePackages` or rely on default TS resolution; add `experimental.serverActions` and security headers.
3. **Add `tests/` directory** with `conftest.py` + 6 test files; migrate 5 manual scripts to pytest functions.
4. **Add `apps/api/services/welcome_email.py`** (or extend `email_service.py`) + trigger from `users.get_current_user_profile` when `onboarded_at` is null.
5. **Wire Sentry SDK** in `apps/api/main.py` (skip if `ENVIRONMENT != production`) and `@sentry/nextjs` in `apps/web/sentry.config.ts`.
6. **Wire PostHog** in `apps/web/app/providers.tsx` (skip if `NEXT_PUBLIC_POSTHOG_KEY` missing).
7. **Add 429 → UpgradeModal** auto-open in `lib/api.ts` global error path.
8. **Add R2 upload** in `services/ingestion_service.py` after PDF download (boto3 + env-driven endpoint).
9. **Add `pdfplumber` parser** in `services/pdf_service.py.extract_text_by_page()` with `pymupdf` fallback.
10. **Add landing page** `apps/web/app/(marketing)/page.tsx` + `pricing/page.tsx` + nav link.
11. **Add deploy job** to `.github/workflows/ci.yml` (Railway API for backend, Vercel CLI for frontend).
12. **Rotate secrets** before production deploy: `APP_SECRET_KEY`, real Stripe keys, real Resend key, real Anthropic key.
13. **Run `graphify update .`** to keep the knowledge graph in sync after the cleanup.

---

## Summary by file count

| Metric | Count |
|---|---|
| Backend Python files (excl. venv) | 53 |
| Frontend TS/TSX files (excl. node_modules) | 49 |
| Backend lines of code | ~3 587 |
| Frontend lines of code | ~5 513 |
| SQLAlchemy models | 9 |
| Alembic migrations | 3 |
| Routers | 7 |
| Services | 8 |
| Agents | 2 (+ 3 prompt files) |
| Celery tasks | 2 |
| Frontend pages | 9 (auth×2, dashboard, library, artifact, digest×2, collections, settings, settings/interests) |
| shadcn components | 11 |
| Custom components | 9 |
| Test files (manual scripts only) | 5 |
| Dockerfiles | 2 |
| GitHub workflows | 1 |
