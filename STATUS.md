# Shouko-AI — Status

## Sprint 1 ✅ Foundation & Auth (DONE)
- Alembic migrations + 9 models (pgvector, UUID, FKs)
- Supabase JWT auth (RS256, JWKS, auto-create users)
- Usage tracking + plan limits
- `GET/PATCH /users/me`
- Auth enforcer on papers, chat, digests, artifacts, billing, collections routers
- Route protection in middleware (`dashboard/*`, `library/*`, etc.)

## Sprint 2 ✅ Knowledge Graph & Discovery (DONE)
- `graphify-out/` — 684 nodes, 818 edges, 44 communities
- Discovery agent (Groq-powered) with scoring criteria
- Digests service + router
- Artifacts service + router

## Sprint 3 ✅ API Integration & Search (DONE)
- Papers router with Arxiv + PDF ingestion
- Chat router with LLM-backed streaming
- Embedding service (OpenRouter)
- Collections router

## Sprint 4 ⏳ Chat UI Polish (~20% DONE)
**Done:**
- `components/chat/ChatPanel.tsx` exists

**Remaining:**
- Extract `MessageList.tsx`, `MessageInput.tsx`, `StreamingMessage.tsx` from inline ChatPanel
- Create `components/shared/ErrorBoundary.tsx`
- Create `components/shared/LoadingSpinner.tsx`
- Add `loading.tsx` and `error.tsx` to all route segments
- Responsive/mobile layout
- Digest pages always say "Today's Digest" for past dates — fix

## Sprint 5 ⏳ Billing Frontend (~50% DONE — backend done)
**Done:**
- `routers/billing.py` + `services/billing_service.py` — registered in `main.py`
- Stripe webhooks (subscription lifecycle)
- Checkout + portal sessions

**Remaining:**
- `settings/billing/page.tsx` — frontend page
- `components/billing/UpgradeModal.tsx`
- `components/billing/UsageBanner.tsx`
- Real Stripe keys (currently mock)

## Sprint 6 ❌ Deployment & Testing (0% DONE)
- Dockerfiles (`Dockerfile.api`, `Dockerfile.celery`)
- `.github/workflows/` CI/CD
- Tests (unit + integration) — zero anywhere
- `next.config.js` — builds will fail in production
- Sentry error tracking
- PostHog analytics

## Environment Variables

### Backend `apps/api/.env`

| Variable | Status | Notes |
|----------|--------|-------|
| `DATABASE_URL` | ✅ Real | Supabase Postgres |
| `SUPABASE_URL` | ✅ Real | |
| `SUPABASE_SERVICE_KEY` | ✅ Real | |
| `OPENROUTER_API_KEY` | ✅ Real | LLM + embeddings |
| `GROQ_API_KEY` | ✅ Real | Discovery scoring |
| `REDIS_URL` | ⚠️ Local | Needs Upstash for prod |
| `RESEND_API_KEY` | ❌ Missing | Email — needed |
| `STRIPE_API_KEY` | ⚠️ Mock | |
| `STRIPE_WEBHOOK_SECRET` | ⚠️ Mock | |
| `STRIPE_PRO_PRICE_ID` | ⚠️ Mock | |
| `ENVIRONMENT` | ⚠️ `development` | Set to `production` |
| `APP_SECRET_KEY` | ⚠️ Hardcoded | Generate real key |
| `FRONTEND_URL` | ⚠️ `localhost:3000` | Update for prod |

### Frontend `apps/web/.env.local`

| Variable | Status | Notes |
|----------|--------|-------|
| `NEXT_PUBLIC_SUPABASE_URL` | ✅ Real | |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | ✅ Real | |
| `NEXT_PUBLIC_API_URL` | ⚠️ `localhost:8000` | Update for prod |
| `NEXT_PUBLIC_APP_URL` | ❌ Missing | Needed for prod |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | ❌ Missing | Billing |

### Infrastructure (not in code yet — from docs)

| Variable | Source |
|----------|--------|
| `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME` | Cloudflare R2 |
| `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN` | Upstash |
| `SENTRY_DSN` | Sentry |
| `NEXT_PUBLIC_POSTHOG_KEY`, `NEXT_PUBLIC_POSTHOG_HOST` | PostHog |

## Summary

| Sprint | % Done | Notes |
|--------|--------|-------|
| 1 — Auth & Foundation | 100% | |
| 2 — Knowledge Graph | 100% | |
| 3 — API Integration | 100% | |
| 4 — Chat UI Polish | ~20% | Components still inline, no loading/error states |
| 5 — Billing Frontend | ~50% | Backend + webhooks done, no frontend |
| 6 — Deployment & Tests | 0% | Nothing started |
