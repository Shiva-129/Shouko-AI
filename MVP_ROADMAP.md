# PaperBrain AI — MVP Roadmap Plan

## Context

PaperBrain is ~30% complete. The backend has solid foundations (9 SQLAlchemy models, 7 services, 2 API endpoints, Celery tasks, Docker Compose). The frontend is a single 1404-line mock page with no real components or routing. The docs are comprehensive (~2,800 lines) but the code gaps are large: no auth, no agents, no artifact generation, no billing, no tests, no deployment.

This plan creates a realistic 6-sprint roadmap (~14 weeks) that builds on what exists to reach a shippable MVP with the complete core loop: **discover → ingest → artifact → chat → upgrade**.

---

## Approach: Full-Stack Vertical Slices

Each sprint delivers a working end-to-end increment. Sprint duration: ~10 working days (~2 calendar weeks). Sprints 1-2 are foundation-heavy, Sprints 3-4 are the hardest (agents + frontend), Sprint 5 adds billing, Sprint 6 is deploy + launch.

---

## Sprint 1: Foundation & Auth (Days 1–10)

**Goal**: Real auth, DB migrations, frontend scaffolding. A user can sign up and see an empty dashboard.

### Backend

1. **Generate Alembic migrations** from existing 9 models
   - Run `alembic revision --autogenerate -m "initial_schema"`
   - Test against local Docker Postgres (`docker compose up -d`)
   - Fix any migration issues (Vector columns, ARRAY types)
   - File: `apps/api/alembic/versions/` (new migration file)

2. **Supabase project setup**
   - Create Supabase project, enable pgvector extension
   - Configure RLS policies on all tables (match `docs/database-schema.md`)
   - Create auth trigger: new Supabase auth user → insert into `users` table
   - Update `apps/api/.env.example` with Supabase vars

3. **Replace MockUser with real JWT validation**
   - New file: `apps/api/core/security.py`
   - Validate Supabase JWT RS256 using `python-jose` (already in requirements)
   - `get_current_user()` dependency extracts `user_id` from validated JWT
   - Keep MockUser path active when `ENVIRONMENT=development` and no `SUPABASE_URL`
   - Update `apps/api/routers/papers.py` and `apps/api/routers/chat.py` to use `get_current_user`
   - Update `apps/api/core/dependencies.py`

4. **User router** — `apps/api/routers/users.py` (new file)
   - `GET /users/me` — returns user profile + plan + usage summary
   - `PATCH /users/me` — update profile, name, interest_profile
   - Register in `apps/api/main.py`

5. **Usage tracking foundation** — `apps/api/core/usage.py` (new file)
   - `log_usage_event(db, user_id, event_type, metadata)` function
   - `check_usage_limit(db, user_id, event_type, limit)` — returns bool
   - Don't enforce yet — just track and log

### Frontend

6. **Initialize shadcn/ui**
   - Run `npx shadcn-ui@latest init` with dark theme
   - Install components: Button, Card, Input, Avatar, Skeleton, Toast, Dialog, Tabs, Badge, Sheet
   - New files: `apps/web/components/ui/` (shadcn generated)

7. **Supabase client setup**
   - Install: `@supabase/supabase-js`, `@supabase/ssr`
   - New file: `apps/web/lib/supabase.ts`
   - New file: `apps/web/middleware.ts` — protect all routes except `/login`, `/signup`
   - New file: `apps/web/.env.local.example`

8. **Auth pages** (new files)
   - `apps/web/app/(auth)/login/page.tsx` — Google OAuth + email/password
   - `apps/web/app/(auth)/signup/page.tsx`
   - Minimal styling with shadcn Card + Input

9. **Route group scaffolding** (new files)
   ```
   apps/web/app/
   ├── (auth)/login, signup
   ├── (dashboard)/
   │   ├── layout.tsx        ← sidebar + top nav shell
   │   ├── dashboard/page.tsx
   │   ├── library/page.tsx
   │   ├── artifact/[id]/page.tsx
   │   ├── digest/[date]/page.tsx
   │   └── settings/page.tsx
   └── layout.tsx (refactored)
   ```

10. **Extract Sidebar component** from `page.tsx`
    - New file: `apps/web/components/layout/Sidebar.tsx`
    - New file: `apps/web/components/layout/TopNav.tsx`
    - Update `(dashboard)/layout.tsx` to use them
    - Keep old `page.tsx` as reference until Sprint 4

### Deliverable
- User can sign up via Supabase, log in, see dashboard shell with sidebar
- All existing endpoints require real JWT
- Alembic migrations running against local DB
- `GET /users/me` returns real user data

### Key Files to Create/Modify
```
CREATE: apps/api/core/security.py
CREATE: apps/api/core/usage.py
CREATE: apps/api/routers/users.py
CREATE: apps/api/alembic/versions/xxxx_initial_schema.py
MODIFY: apps/api/core/dependencies.py
MODIFY: apps/api/routers/papers.py (add auth)
MODIFY: apps/api/routers/chat.py (add auth)
MODIFY: apps/api/main.py (register users router)
MODIFY: apps/api/.env.example

CREATE: apps/web/lib/supabase.ts
CREATE: apps/web/middleware.ts
CREATE: apps/web/.env.local.example
CREATE: apps/web/app/(auth)/login/page.tsx
CREATE: apps/web/app/(auth)/signup/page.tsx
CREATE: apps/web/app/(dashboard)/layout.tsx
CREATE: apps/web/app/(dashboard)/dashboard/page.tsx
CREATE: apps/web/app/(dashboard)/library/page.tsx
CREATE: apps/web/app/(dashboard)/artifact/[id]/page.tsx
CREATE: apps/web/app/(dashboard)/digest/[date]/page.tsx
CREATE: apps/web/app/(dashboard)/settings/page.tsx
CREATE: apps/web/components/layout/Sidebar.tsx
CREATE: apps/web/components/layout/TopNav.tsx
CREATE: apps/web/components/ui/ (shadcn generated)
```

---

## Sprint 2: Discovery Agent & Digest (Days 11–20)

**Goal**: Real LLM-scored paper discovery. User sets interests, gets a daily digest with relevance-scored papers.

### Backend

1. **Prompt registry** — `apps/api/prompts/__init__.py` (new dir + file)
   - Establish prompt versioning pattern

2. **Discovery prompt** — `apps/api/prompts/discovery.py` (new file)
   - Implement from `docs/ai-architecture.md`: SYSTEM_PROMPT + `build_user_prompt()` + `DiscoveryOutput` Pydantic model
   - Batch scoring: 20 papers per LLM call, score 0-100, filter ≥ 70

3. **Discovery agent** — `apps/api/agents/discovery_agent.py` (new dir + file)
   - Replace keyword matching in `digest_service.py` with Claude Haiku batch scoring
   - Flow: fetch papers by category → batch 20 per LLM call → parse JSON → filter score ≥ 70 → store
   - Use `LLMService` with Haiku model override
   - Keep keyword matching as fallback when no LLM key

4. **Upgrade `apps/api/services/digest_service.py`**
   - Import and call discovery agent instead of keyword matching
   - Preserve existing email sending logic

5. **Digest router** — `apps/api/routers/digests.py` (new file)
   - `GET /digests` — list user's digests with pagination
   - `GET /digests/{date}` — specific date digest with paper details
   - `POST /digests/trigger` — manual trigger (dev/testing, rate limited in prod)
   - All behind auth, filtered by `user_id`
   - Register in `apps/api/main.py`

6. **Update Celery task** — `apps/api/tasks/digest_tasks.py`
   - `scan_daily_research_papers` now calls discovery agent
   - Add Celery beat schedule configuration

### Frontend

7. **API client** — `apps/web/lib/api.ts` (new file)
   - Typed fetch wrapper with auth header injection from Supabase session
   - Standard response envelope parsing: `{data, meta}` and `{error, meta}`
   - Auto-redirect to `/login` on 401

8. **TanStack Query setup**
   - Install `@tanstack/react-query`
   - Configure `QueryClientProvider` in root layout
   - New files: `apps/web/lib/hooks/useUser.ts`, `apps/web/lib/hooks/useDigest.ts`, `apps/web/lib/hooks/useDigests.ts`

9. **Interest profile page** — `apps/web/app/(dashboard)/settings/interests/page.tsx` (new file)
   - Multi-select for ArXiv categories (cs.LG, cs.AI, cs.CL, etc.)
   - Tag input for keywords
   - Text input for favorite authors
   - Save via `PATCH /users/me`
   - Shadcn components: Input, Badge, Button, Card

10. **Digest page** — `apps/web/app/(dashboard)/digest/[date]/page.tsx` (update from Sprint 1 scaffold)
    - Paper cards: title, relevance score badge (colored 0-100), relevance reasons, one-line summary
    - "Create Artifact" button on each card (placeholder — wired in Sprint 3)
    - Date picker navigation (prev/next day)
    - Loading skeletons while fetching
    - Empty state: "No papers found for this date"

11. **Update dashboard** — `apps/web/app/(dashboard)/dashboard/page.tsx`
    - Today's digest summary (top 3 papers)
    - "View full digest" link to `/digest/[today]`

### Deliverable
- User sets interests → triggers digest → sees 5 LLM-scored papers with relevance reasons
- Digest page with real data from backend
- Celery task runs discovery agent daily or on manual trigger

### Key Files to Create/Modify
```
CREATE: apps/api/prompts/__init__.py
CREATE: apps/api/prompts/discovery.py
CREATE: apps/api/agents/__init__.py
CREATE: apps/api/agents/discovery_agent.py
MODIFY: apps/api/services/digest_service.py (use agent)
MODIFY: apps/api/tasks/digest_tasks.py (use agent)
CREATE: apps/api/routers/digests.py
MODIFY: apps/api/main.py (register digests router)

CREATE: apps/web/lib/api.ts
CREATE: apps/web/lib/hooks/useUser.ts
CREATE: apps/web/lib/hooks/useDigest.ts
CREATE: apps/web/lib/hooks/useDigests.ts
MODIFY: apps/web/app/layout.tsx (add QueryClientProvider)
UPDATE: apps/web/app/(dashboard)/settings/interests/page.tsx
UPDATE: apps/web/app/(dashboard)/digest/[date]/page.tsx
UPDATE: apps/web/app/(dashboard)/dashboard/page.tsx
```

---

## Sprint 3: Artifact Generation Pipeline (Days 21–32)

**Goal**: The core value prop. User clicks "Create Artifact" → waits ~2 min → gets a structured knowledge artifact.

### Backend

1. **Artifact generation prompt** — `apps/api/prompts/artifact_generation.py` (new file)
   - Implement from `docs/ai-architecture.md`: system prompt, `build_user_prompt(paper_title, paper_chunks)`, Pydantic schemas
   - Output models: `ArtifactGenerationOutput`, `Insight`, `QAPair`, `SuggestedExperiment`
   - Sections: one_line_summary, summary (300 words), 5-8 insights, 10-15 Q&A pairs, 3-5 experiments

2. **Artifact agent** — `apps/api/agents/artifact_agent.py` (new file)
   - Load paper chunks grouped by section (max 3 chunks per section)
   - Call Claude Sonnet (via `LLMService`) with artifact generation prompt
   - Validate output with Pydantic (`ArtifactGenerationOutput`)
   - Retry up to 3 times with exponential backoff (tenacity)
   - Return structured artifact data

3. **Artifact Celery task** — `apps/api/tasks/generate_artifact.py` (new file)
   - Orchestrates full pipeline:
     - Update status to `ingesting`
     - If paper not yet ingested, call `IngestionService.ingest_paper()`
     - Update status to `generating`
     - Call `ArtifactAgent.generate()` with chunks
     - Store results in `artifacts` table
     - Update status to `ready` (or `partial`/`failed`)
   - Track `generation_cost_usd`

4. **Refactor ingestion to be async**
   - Current `POST /papers/ingest` runs synchronously — change to dispatch Celery task
   - Return `{paper_id, status: "queued"}` immediately
   - Update `apps/api/routers/papers.py`

5. **Artifact router** — `apps/api/routers/artifacts.py` (new file)
   - `POST /artifacts` — create artifact for a paper (dispatches Celery task, returns immediately)
   - `GET /artifacts` — list user's artifacts with pagination, JOIN with papers table
   - `GET /artifacts/{id}` — full artifact content (409 if status != `ready`)
   - `GET /artifacts/{id}/status` — poll status for progress UI
   - `DELETE /artifacts/{id}` — delete artifact + cascade
   - All behind auth, filtered by `user_id`
   - Register in `apps/api/main.py`

6. **Usage enforcement** — activate tracking from Sprint 1
   - `POST /artifacts` checks monthly artifact count against plan limit (5 free)
   - Return 429 with `USAGE_LIMIT_REACHED` code when exceeded

### Frontend

7. **Artifact hooks**
   - `apps/web/lib/hooks/useArtifact.ts` — TanStack Query for artifact data + status polling
   - `apps/web/lib/hooks/useArtifacts.ts` — list artifacts
   - Poll `GET /artifacts/{id}/status` every 3s while not `ready`
   - Auto-refetch artifact content when status becomes `ready`

8. **Artifact detail page** — update `apps/web/app/(dashboard)/artifact/[id]/page.tsx`
   - Tab 1: Summary — one-line summary, full summary, paper metadata (title, authors, ArXiv link)
   - Tab 2: Insights — key insights cards sorted by `importance_score`, section tags
   - Tab 3: Q&A — auto-generated pairs as expandable accordions, difficulty badges
   - Tab 4: Experiments — suggested experiments with feasibility badges
   - Processing state: progress bar + status message (`queued` → `ingesting` → `generating`)
   - Error state: retry button if `failed`
   - Shadcn: Tabs, Card, Accordion, Badge, Progress

9. **Library page** — update `apps/web/app/(dashboard)/library/page.tsx`
   - Grid of artifact cards (title, one-line summary, status badge, created date)
   - Search input (filter by title client-side for MVP)
   - Empty state: "Create your first artifact" CTA linking to digest

10. **Wire "Create Artifact" buttons**
    - Digest page: each paper card has "Create Artifact" → `POST /artifacts`
    - On success: redirect to `/artifact/[id]` (which starts polling)
    - On 429 limit: show toast with upgrade prompt (proper modal in Sprint 5)

### Deliverable
- Full pipeline: ArXiv paper → PDF ingestion → chunking → embedding → artifact generation
- User sees structured artifact with summary, insights, Q&A, experiments
- Library page shows all created artifacts
- Processing state visible during ~2 min generation
- Free tier: 5 artifacts/month enforced

### Key Files to Create/Modify
```
CREATE: apps/api/prompts/artifact_generation.py
CREATE: apps/api/agents/artifact_agent.py
CREATE: apps/api/tasks/generate_artifact.py
CREATE: apps/api/routers/artifacts.py
MODIFY: apps/api/routers/papers.py (async ingestion)
MODIFY: apps/api/main.py (register artifacts router)

CREATE: apps/web/lib/hooks/useArtifact.ts
CREATE: apps/web/lib/hooks/useArtifacts.ts
UPDATE: apps/web/app/(dashboard)/artifact/[id]/page.tsx
UPDATE: apps/web/app/(dashboard)/library/page.tsx
UPDATE: apps/web/app/(dashboard)/digest/[date]/page.tsx (wire Create Artifact button)
```

---

## Sprint 4: Chat Interface & Frontend Polish (Days 33–44)

**Goal**: Complete the core loop with RAG chat. Polish the UI into a shippable experience.

### Backend

1. **RAG prompt refactor** — `apps/api/prompts/rag_qa.py` (new file)
   - Extract inline prompt from `apps/api/services/rag_service.py` into proper prompt file
   - Implement from `docs/ai-architecture.md`: grounding rules, section-labeled context
   - Update `rag_service.py` to import from prompt file

2. **Conversation endpoints** — update `apps/api/routers/chat.py`
   - `GET /conversations/{artifact_id}` — conversation history
   - `DELETE /conversations/{artifact_id}` — clear history
   - Ensure all queries filter by `user_id` from JWT

3. **Rate limiting** — `apps/api/core/rate_limit.py` (new file)
   - Redis sliding window implementation (pattern from `docs/security.md`)
   - Apply to chat: 30 req/min per user
   - Apply to artifact creation: 10/hour free, 100/hour pro
   - Return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers

4. **Input sanitization** — update `apps/api/core/security.py`
   - Prompt injection pattern detection (patterns from `docs/security.md`)
   - Input length cap (2000 chars)
   - Apply to chat endpoint before reaching LLM

### Frontend

5. **Component extraction** from `apps/web/app/page.tsx`
   - `apps/web/components/papers/PaperCard.tsx`
   - `apps/web/components/chat/ChatPanel.tsx`
   - `apps/web/components/chat/MessageBubble.tsx`
   - `apps/web/components/chat/StreamingMessage.tsx`
   - `apps/web/components/shared/StatusBadge.tsx`
   - `apps/web/components/shared/EmptyState.tsx`
   - `apps/web/components/shared/LoadingSpinner.tsx`
   - Keep mock data as reference; components will be used with real data

6. **Real chat integration on artifact page**
   - Add ChatPanel as a tab or side drawer on artifact detail page
   - Use `useSSEChat.ts` hook (already exists) with real auth headers from Supabase
   - Show sources from RAG context in assistant messages
   - Load conversation history on page open via `GET /conversations/{artifact_id}`
   - New hook: `apps/web/lib/hooks/useChat.ts`

7. **Dashboard page** — update `apps/web/app/(dashboard)/dashboard/page.tsx`
   - Today's digest summary (top 3 papers with scores)
   - Recent artifacts grid (last 5 with status badges)
   - Quick stats: artifacts this month, questions today
   - Empty states for first-time users

8. **Settings page** — update `apps/web/app/(dashboard)/settings/page.tsx`
   - Profile section: name, email (read-only)
   - Link to interest profile editor
   - Link to billing page (placeholder for Sprint 5)
   - Plan info display

9. **Responsive design**
   - Sidebar collapses to hamburger menu on mobile (`Sheet` component)
   - Cards stack vertically on small screens
   - Chat panel becomes full-width on mobile
   - Loading skeletons on every async page
   - Toast notifications for create/delete/error actions

10. **Error handling**
    - `apps/web/components/shared/ErrorBoundary.tsx`
    - 404 page, 500 page
    - TanStack Query retry config (3 retries with exponential backoff)

### Deliverable
- Complete core loop: discover → ingest → artifact → chat
- Real SSE streaming chat with RAG context and conversation history
- Polished dashboard, library, artifact detail, digest, settings pages
- Rate limiting and input sanitization active
- Mobile-responsive layout
- Error boundaries and loading states throughout

### Key Files to Create/Modify
```
CREATE: apps/api/prompts/rag_qa.py
MODIFY: apps/api/services/rag_service.py (import from prompt file)
MODIFY: apps/api/routers/chat.py (add history + clear endpoints)
CREATE: apps/api/core/rate_limit.py
MODIFY: apps/api/core/security.py (add input sanitization)

CREATE: apps/web/components/papers/PaperCard.tsx
CREATE: apps/web/components/chat/ChatPanel.tsx
CREATE: apps/web/components/chat/MessageBubble.tsx
CREATE: apps/web/components/chat/StreamingMessage.tsx
CREATE: apps/web/components/shared/StatusBadge.tsx
CREATE: apps/web/components/shared/EmptyState.tsx
CREATE: apps/web/components/shared/LoadingSpinner.tsx
CREATE: apps/web/components/shared/ErrorBoundary.tsx
CREATE: apps/web/lib/hooks/useChat.ts
UPDATE: apps/web/app/(dashboard)/artifact/[id]/page.tsx (add chat)
UPDATE: apps/web/app/(dashboard)/dashboard/page.tsx
UPDATE: apps/web/app/(dashboard)/settings/page.tsx
DELETE: apps/web/app/page.tsx (replace with proper routing)
```

---

## Sprint 5: Billing & Usage Enforcement (Days 45–56)

**Goal**: Stripe integrated. Users can upgrade. Free tier limits enforced with upgrade prompts.

### Backend

1. **Stripe service** — `apps/api/services/billing_service.py` (new file)
   - Install `stripe` Python package
   - `create_checkout_session(user_id, plan, period)` → returns Stripe checkout URL
   - `create_portal_session(stripe_customer_id)` → returns Stripe portal URL
   - `handle_webhook(payload, signature)` → processes subscription events

2. **Billing router** — `apps/api/routers/billing.py` (new file)
   - `POST /billing/create-checkout-session`
   - `POST /billing/create-portal-session`
   - `POST /billing/webhook` — no auth (Stripe signature verified)
   - `GET /billing/usage` — current period usage stats
   - Handles events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`
   - Register in `apps/api/main.py`

3. **Usage enforcement** — update `apps/api/core/usage.py`
   - Upgrade from tracking-only to enforcement
   - Free: 5 artifacts/month, 20 questions/day, 10 ingestions/month
   - Pro: unlimited
   - Return 429 `USAGE_LIMIT_REACHED` with usage details
   - Apply to: `POST /artifacts`, `POST /conversations/*/chat`, `POST /papers/ingest`

4. **Welcome email** — update `apps/api/services/email_service.py`
   - `send_welcome_email(to_email, user_name)` method
   - Trigger on first `GET /users/me` call (if `onboarded_at` is null)

### Frontend

5. **Billing settings page** — `apps/web/app/(dashboard)/settings/billing/page.tsx` (new file)
   - Current plan display with badge
   - Usage meters (artifacts: 3/5, questions: 12/20) — progress bars
   - Upgrade button → Stripe checkout (opens in new tab)
   - Manage subscription button → Stripe portal (if pro)
   - Shadcn: Card, Progress, Button

6. **Upgrade prompt modal** — `apps/web/components/billing/UpgradeModal.tsx` (new file)
   - Triggered when API returns 429 `USAGE_LIMIT_REACHED`
   - Shows current usage, plan comparison table, upgrade CTA
   - Dismissible but re-shows on next limit hit
   - Intercept 429 in `apps/web/lib/api.ts` global error handler

7. **Usage banner** — `apps/web/components/billing/UsageBanner.tsx` (new file)
   - Shows on dashboard when usage > 80%
   - "4 of 5 free artifacts used this month"
   - Disappears after upgrade

8. **Error handling polish**
   - Global error interceptor in API client
   - Toast notifications for all async operations
   - Specific error states: rate limited, usage exceeded, network error

### Deliverable
- Working Stripe checkout and portal
- Free tier limits enforced with clear upgrade path
- Billing page showing usage and plan management
- Upgrade modal appears on limit hit
- Usage banner on dashboard

### Key Files to Create/Modify
```
CREATE: apps/api/services/billing_service.py
CREATE: apps/api/routers/billing.py
MODIFY: apps/api/core/usage.py (enforcement)
MODIFY: apps/api/services/email_service.py (welcome email)
MODIFY: apps/api/routers/artifacts.py (add usage check)
MODIFY: apps/api/routers/chat.py (add usage check)
MODIFY: apps/api/main.py (register billing router)

CREATE: apps/web/app/(dashboard)/settings/billing/page.tsx
CREATE: apps/web/components/billing/UpgradeModal.tsx
CREATE: apps/web/components/billing/UsageBanner.tsx
MODIFY: apps/web/lib/api.ts (429 interceptor)
UPDATE: apps/web/app/(dashboard)/dashboard/page.tsx (add UsageBanner)
UPDATE: apps/web/app/(dashboard)/settings/page.tsx (add billing link)
```

---

## Sprint 6: Deployment, Testing & Launch (Days 57–70)

**Goal**: Deployed to production. Tested. 10 beta users onboarded.

### Infrastructure

1. **Dockerfiles** (new files)
   - `infrastructure/Dockerfile.api` — FastAPI app (from `docs/deployment.md`)
   - `infrastructure/Dockerfile.celery` — Celery worker + beat
   - Update `infrastructure/docker-compose.yml` to include app services

2. **Production Supabase**
   - Production Supabase project with pgvector
   - Run `alembic upgrade head` against production DB
   - Configure RLS policies
   - Google OAuth credentials for production

3. **Railway deployment**
   - 3 services: `api`, `celery-worker`, `celery-beat`
   - Environment variables configured
   - Custom domain: `api.paperbrain.app`

4. **Vercel deployment**
   - Connect GitHub repo, env vars configured
   - Custom domain: `paperbrain.app`

5. **GitHub Actions** — `.github/workflows/` (new dir)
   - `test.yml`: run pytest on PR
   - `deploy.yml`: deploy to Railway + Vercel on merge to main

### Testing

6. **Pytest foundation**
   - `apps/api/tests/conftest.py` — test DB fixture, auth helper, test factories
   - `apps/api/tests/factories.py` — User, Paper, Artifact factories

7. **Critical path tests**
   - `apps/api/tests/test_auth.py` — signup → JWT → protected endpoint
   - `apps/api/tests/test_ingestion.py` — ingest → chunks stored → embeddings
   - `apps/api/tests/test_artifacts.py` — create → Celery task → status → ready
   - `apps/api/tests/test_chat.py` — message → RAG → SSE → conversation saved
   - `apps/api/tests/test_billing.py` — checkout → webhook → plan updated
   - Target: 70% coverage on routers + services

### Launch Prep

8. **Sentry integration**
   - Backend: `sentry_sdk.init()` in `apps/api/main.py`
   - Frontend: `@sentry/nextjs` in `apps/web`

9. **Onboarding flow**
   - First-login redirect to `/settings/interests`
   - "Getting started" card on empty dashboard
   - Tooltip hints on key UI elements

10. **Beta recruitment**
    - DM 30 AI researchers on X
    - Offer free Pro for 3 months
    - Create feedback form

11. **Bug fixes from beta testing**

### Deliverable
- Production deployment on Vercel + Railway
- CI/CD pipeline running
- Critical path tests passing (70% coverage)
- 10 beta users with working accounts
- Sentry monitoring active

### Key Files to Create/Modify
```
CREATE: infrastructure/Dockerfile.api
CREATE: infrastructure/Dockerfile.celery
MODIFY: infrastructure/docker-compose.yml
CREATE: .github/workflows/test.yml
CREATE: .github/workflows/deploy.yml

CREATE: apps/api/tests/conftest.py
CREATE: apps/api/tests/factories.py
CREATE: apps/api/tests/test_auth.py
CREATE: apps/api/tests/test_ingestion.py
CREATE: apps/api/tests/test_artifacts.py
CREATE: apps/api/tests/test_chat.py
CREATE: apps/api/tests/test_billing.py

MODIFY: apps/api/main.py (add Sentry)
MODIFY: apps/web/package.json (add @sentry/nextjs)
```

---

## What's Explicitly Deferred (Not in MVP)

| Feature | Why Deferred |
|---|---|
| Knowledge graph / cross-paper links | Needs library accumulation first |
| Multi-paper orchestrator | Core loop must work first |
| Notion/Obsidian export | Nice-to-have, not core value |
| Semantic cache (Redis) | Performance optimization, not correctness |
| Teams / multi-seat | Need individual PMF first |
| Mobile app | Desktop research workflow |
| Landing page / marketing site | Ship product first |
| Eval suite (50 gold papers) | Can add post-launch |
| Reranking (cross-encoder) | Current cosine search works for MVP |
| Cloudflare R2 for PDFs | Local temp files work for MVP volume |
| pdfplumber as primary | PyMuPDF works fine |
| LangGraph agent framework | Service classes work fine for MVP |
| APScheduler | Celery Beat works fine |

---

## Risk Mitigations

| Risk | Mitigation |
|---|---|
| Artifact generation quality poor | Iterate on prompt in Sprint 3; mock fallback exists; test with well-known papers |
| Supabase JWT integration tricky | Supabase docs are excellent; `python-jose` with JWKS endpoint as fallback |
| Celery task reliability | Task retry with backoff; status tracking allows recovery; manual re-trigger button |
| Solo founder burnout | Strict scope control; ship imperfect things; each sprint has visible deliverable |
| LLM API costs during dev | Mock fallback exists for every service; real keys only needed for final testing |
| Stripe webhook debugging | Stripe CLI for local testing; well-documented |

---

## Verification

After each sprint, verify:
1. **Sprint 1**: Can sign up, log in, see dashboard shell. `GET /users/me` returns real data. Migrations run cleanly.
2. **Sprint 2**: Can set interests, trigger digest, see LLM-scored papers with relevance reasons.
3. **Sprint 3**: Can create artifact from digest, see processing states, view completed artifact with summary/insights/Q&A.
4. **Sprint 4**: Can chat with artifact, see streaming responses with RAG context. Full UI navigable on mobile.
5. **Sprint 5**: Can hit usage limit, see upgrade modal, complete Stripe checkout, see plan updated.
6. **Sprint 6**: Full smoke test passes in production. 10 beta users have working accounts.

Final smoke test checklist:
- [ ] Sign up with Google OAuth
- [ ] Set interest profile (topics + keywords)
- [ ] Trigger digest → see 5 scored papers
- [ ] Click "Create Artifact" → wait for processing → see artifact
- [ ] Ask 3 questions in artifact chat → see streaming answers
- [ ] Create 5 artifacts → hit free limit → see upgrade prompt
- [ ] Upgrade to Pro via Stripe → limits removed
- [ ] All pages load without errors on mobile
- [ ] Sentry captures a test error
