# Shouko-AI — Development Roadmap

> 8-week MVP build plan for a solo founder. Strict scope — do not add features mid-sprint.

---

## Guiding Principles

1. **Ship something that works** over something that's complete
2. **Don't build what you don't need yet** — the knowledge graph can wait
3. **Real users beat perfect code** — get to beta by Week 8
4. **If a feature would take >3 days alone, cut it from MVP**

---

## Phase 1: MVP (Weeks 1–8)

### ✅ Week 1 — Foundation & Infrastructure

**Goal:** Working monorepo, auth, deployments running.

**Tasks:**
- [ ] Initialize monorepo structure (apps/web, apps/api, infrastructure/)
- [ ] Set up Next.js 14 with Tailwind + shadcn/ui (dark mode default)
- [ ] Set up FastAPI with Pydantic settings, CORS, health check
- [ ] Set up Supabase project (enable pgvector, configure RLS)
- [ ] Set up Docker Compose for local Postgres + Redis
- [ ] Implement auth: Supabase Google OAuth + email/password
- [ ] Protected routes in Next.js middleware
- [ ] Deploy frontend to Vercel
- [ ] Deploy backend to Railway (staging)
- [ ] Set up GitHub Actions: test + deploy pipeline
- [ ] Configure Cloudflare domain + DNS

**Deliverable:** Deployed app where users can sign up and log in. Nothing else yet.

---

### ✅ Week 2 — ArXiv Discovery Agent

**Goal:** System automatically fetches and scores ArXiv papers.

**Tasks:**
- [ ] Implement ArXiv API wrapper (`services/arxiv_service.py`)
- [ ] Build interest profile onboarding UI (topics, keywords, categories)
- [ ] Save interest profile to users table
- [ ] Build discovery agent (`agents/discovery_agent.py`)
  - Fetch papers by category/keyword
  - Batch score with Claude Haiku (20 papers per call)
  - Filter: score >= 70
- [ ] Store results in `papers` and `daily_digests` tables
- [ ] APScheduler job: run discovery at 6 AM UTC daily
- [ ] Build Digest UI: `/digest/[date]` page with paper cards
- [ ] Manual "Run digest now" button (dev/testing)

**Deliverable:** Log in, set interests, trigger a digest, see 5 recommended papers.

---

### ✅ Week 3 — PDF Ingestion Pipeline

**Goal:** System downloads and processes PDF papers into searchable chunks.

**Tasks:**
- [ ] Cloudflare R2 setup + boto3 S3-compatible upload
- [ ] PDF download from ArXiv URL → store to R2
- [ ] pdfplumber text extraction + section detection
- [ ] pymupdf fallback for failed extractions
- [ ] Text chunking: 512 tokens, 50 overlap, section-aware
- [ ] Batch embedding: OpenAI text-embedding-3-small
- [ ] Store chunks in `paper_chunks` with embeddings
- [ ] Celery task: `tasks/process_paper.py`
- [ ] Track paper ingestion status in `papers` table
- [ ] Error handling: malformed PDFs, extraction failures

**Deliverable:** Click a paper → PDF downloads and gets chunked (check DB to verify).

---

### ✅ Week 4 — Artifact Generator Agent

**Goal:** Generate structured living wiki from ingested paper.

**Tasks:**
- [ ] Build artifact generation prompt (`prompts/artifact_generation.py`)
- [ ] Implement artifact agent (`agents/artifact_agent.py`)
  - Load chunks by section
  - Call Claude Sonnet with structured prompt
  - Validate with Pydantic (ArtifactGenerationOutput)
  - Retry logic (max 3 attempts with backoff)
- [ ] Celery task: `tasks/generate_artifact.py`
- [ ] Status tracking: queued → ingesting → generating → ready/failed
- [ ] `POST /artifacts` endpoint (triggers pipeline)
- [ ] `GET /artifacts/{id}/status` endpoint (for polling)
- [ ] `GET /artifacts/{id}` endpoint (full content)
- [ ] Artifact detail page skeleton (just show JSON for now)
- [ ] Usage limit enforcement: 5/month for free users

**Deliverable:** Click [Create Artifact] → wait 2 min → see generated summary and insights.

---

### ✅ Week 5 — Chat Interface (RAG)

**Goal:** Users can ask questions about any artifact. Answers stream in real-time.

**Tasks:**
- [ ] Build RAG service (`services/rag_service.py`)
  - Embed query
  - Vector search (pgvector, top 8)
  - Simple reranking (keyword + semantic score)
  - Context assembly
- [ ] Build RAG Q&A prompt (`prompts/rag_qa.py`)
- [ ] SSE streaming endpoint: `POST /conversations/{id}/chat`
- [ ] Conversation history: store in `conversations` table
- [ ] Frontend: ChatPanel component (right side of artifact page)
- [ ] StreamingMessage component (renders tokens as they arrive)
- [ ] Rate limiting: 30 questions/minute
- [ ] Daily usage limit: 20 questions/day (free)
- [ ] Semantic cache (Redis): skip LLM if similar question asked before

**Deliverable:** Open artifact → ask a question → see answer stream word by word.

---

### ✅ Week 6 — Full UI & Dashboard

**Goal:** Polished, usable interface. Users can navigate the full product.

**Tasks:**
- [ ] Dashboard page: today's digest + recent artifacts grid
- [ ] Library page: all artifacts, search by title
- [ ] Artifact detail page: full UI with tabs (Summary, Insights, Q&A, Experiments)
- [ ] ArtifactCard component for library grid
- [ ] StatusBadge (processing/ready/failed)
- [ ] Empty states for all pages
- [ ] Loading skeletons for all async data
- [ ] Settings page: interest profile editor
- [ ] Mobile-responsive layout (sidebar collapses)
- [ ] Usage limit banner ("4 of 5 free artifacts used")
- [ ] Error boundary for failed artifact loads
- [ ] Toast notifications for async actions

**Deliverable:** Full UX from signup → digest → create artifact → chat.

---

### ✅ Week 7 — Payments + Polish

**Goal:** Stripe integrated. Users can upgrade. Product is production-ready.

**Tasks:**
- [ ] Create Stripe products: Pro Monthly ($19), Pro Yearly ($190)
- [ ] `POST /billing/create-checkout-session` endpoint
- [ ] `POST /billing/webhook` endpoint (handle subscription events)
- [ ] Update user plan in DB on Stripe webhook
- [ ] Billing settings page with current plan + usage
- [ ] Upgrade prompt modal (triggered when limit hit)
- [ ] Resend email: daily digest notification
- [ ] Resend email: welcome email on signup
- [ ] Sentry error tracking (frontend + backend)
- [ ] PostHog analytics (page views, key events)
- [ ] Rate limit middleware fully tested
- [ ] Full QA pass: create account, add interests, get digest, create artifact, chat, upgrade

**Deliverable:** Full product with working payments. Charge your first real card.

---

### ✅ Week 8 — Launch Preparation

**Goal:** 10 beta users using the product. Public launch ready.

**Tasks:**
- [ ] Landing page (shouko-ai.app) with waitlist capture
- [ ] Production environment fully configured
- [ ] Production smoke test (full user journey)
- [ ] Onboarding flow: 3-step wizard (interests → first digest → create artifact)
- [ ] "Getting started" tooltip hints
- [ ] Write Show HN post draft
- [ ] Write Product Hunt listing
- [ ] Recruit 10 beta users (DM AI researchers on X)
- [ ] Fix bugs from beta feedback
- [ ] Load test: simulate 100 concurrent users

**Deliverable:** 10 real people using the product. Public launch scheduled.

---

## Phase 2: Core Product (Weeks 9–18)

**Goal:** Reduce churn, add team features, increase retention.

### Week 9–10: Knowledge Graph (Basic)
- Connect related papers within a user's library
- Show "related artifacts" on each artifact page
- Cross-artifact semantic search

### Week 11–12: Orchestrator
- Multi-paper tasks: "compare these 3 papers"
- "Summarize everything I've read about RAG this month"
- Background orchestrator with task queue

### Week 13–14: Integrations
- Notion export (artifact → Notion page)
- Obsidian export (artifact → markdown vault file)
- Slack digest notification

### Week 15–16: Team Plan
- Teams table + team_members
- Shared artifact library
- Team Stripe subscription

### Week 17–18: Additional Sources
- Semantic Scholar integration
- PubMed integration (for biotech market)

---

## Phase 3: Growth (Weeks 19–30)

- Enterprise SSO (SAML)
- API access for developers
- White-label artifact exports
- AI-generated literature review reports
- Mobile app (React Native)
- More paper sources (IEEE, ACM, bioRxiv)
- Custom AI fine-tuning on user's reading patterns

---

## What NOT to Build in MVP

These are explicitly deferred. Do not scope creep:

| Feature | Reason Deferred |
|---|---|
| Knowledge graph | Complex, needs data accumulation first |
| Team/collaboration | Need individual PMF first |
| Multiple paper sources (PubMed, IEEE) | ArXiv is enough to validate |
| Mobile app | Desktop first for research workflows |
| Notion/Obsidian integration | Nice-to-have, not core value |
| Fine-tuning | Needs scale (10K+ users) |
| Public artifact sharing | Can add in Phase 2 |
| Comparison view | Build when users ask for it |
| Orchestrator | Build when core loop is stable |
| Literature review reports | Phase 3 upsell |

---

## Solo Founder Feasibility

**Honest assessment: Tight but doable.**

Week 1–2: Infrastructure-heavy. Mostly config, not complex code.
Week 3–4: Agent code is the hardest part. Budget extra time here.
Week 5: RAG + streaming is tricky. Allocate 2 extra days.
Week 6: UI is time-consuming. Use shadcn/ui components, don't custom-build.
Week 7: Stripe is well-documented. 2 days max.
Week 8: Marketing work, not code.

**Risk mitigations:**
- Use Claude heavily for boilerplate code
- Don't customize UI beyond what shadcn gives you
- If PDF parsing is problematic, use a managed service (Reducto.ai)
- If a feature is blocking, ship without it and add later
