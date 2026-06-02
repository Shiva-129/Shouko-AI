# Graph Report - paperbrain-ai  (2026-06-02)

## Corpus Check
- 55 files · ~530,840 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 532 nodes · 553 edges · 36 communities (29 shown, 7 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 49 edges (avg confidence: 0.63)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `912ac4e9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]

## God Nodes (most connected - your core abstractions)
1. `PaperBrain AI — MVP Roadmap Plan` - 12 edges
2. `PaperBrain — Security & Compliance` - 12 edges
3. `Base` - 11 edges
4. `PaperBrain — Implementation Status Master Report` - 11 edges
5. `PaperBrain — Marketing & Go-To-Market Strategy` - 11 edges
6. `PaperBrain — Deployment Guide` - 11 edges
7. `PaperBrain — Frontend (Next.js) Guide` - 11 edges
8. `EmbeddingService` - 10 edges
9. `IngestionService` - 10 edges
10. `Backend (`apps/api/.env`)` - 10 edges

## Surprising Connections (you probably didn't know these)
- `Paper` --uses--> `Base`  [INFERRED]
  apps/api/models/paper.py → apps/api/core/database.py
- `Conversation` --uses--> `Base`  [INFERRED]
  apps/api/models/conversation.py → apps/api/core/database.py
- `DigestService` --uses--> `Paper`  [INFERRED]
  apps/api/services/digest_service.py → apps/api/models/paper.py
- `ChatRequest` --uses--> `Artifact`  [INFERRED]
  apps/api/routers/chat.py → apps/api/models/artifact.py
- `RAGService` --uses--> `PaperChunk`  [INFERRED]
  apps/api/services/rag_service.py → apps/api/models/chunk.py

## Communities (36 total, 7 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (23): main(), main(), BaseModel, Conversation, Paper, chat_sse_endpoint(), ChatRequest, Submit a technical question about a paper artifact.      Queries pgvector, build (+15 more)

### Community 1 - "Community 1"
Cohesion: 0.04
Nodes (44): Approach: Full-Stack Vertical Slices, Backend, Backend, Backend, Backend, Backend, code:block1 (apps/web/app/), code:block2 (CREATE: apps/api/core/security.py) (+36 more)

### Community 2 - "Community 2"
Cohesion: 0.04
Nodes (44): Abuse Prevention, API Key Security, At Rest, Authentication Security, Authorization, Backend JWT Validation, Backup Strategy, code:python (# core/security.py) (+36 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (41): Backend (`apps/api/.env`), Backend (Railway → AWS ECS at scale), code:bash (# ── App ──────────────────────────────────────────────), code:bash (# Install Vercel CLI), code:bash (# Install Railway CLI), code:yaml (# .github/workflows/deploy.yml), code:bash (# Create new migration), code:block14 (paperbrain.app          → Vercel (frontend)) (+33 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (38): 1. Discovery Agent Prompt (`prompts/discovery.py`), 2. Artifact Generation Prompt (`prompts/artifact_generation.py`), 3. RAG Q&A Prompt (`prompts/rag_qa.py`), Automated Eval Metrics, Budget Alert System, Chunking Strategy, code:python (PROMPT_VERSION = "1.0"), code:python (# Reject uploads that are not academic papers) (+30 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (37): 🤖 Agent Architecture, Artifact Agent (`agents/artifact_agent.py`), ArXiv (`services/arxiv_service.py`), 💳 Billing & Usage Limits, Claude API (`services/claude_service.py`), code:block1 (apps/api/), code:python (# Always use the arxiv Python library), code:python (import anthropic) (+29 more)

### Community 6 - "Community 6"
Cohesion: 0.08
Nodes (17): run_digest_test(), Base, Base, DeclarativeBase, Annotation, Artifact, PaperChunk, Collection (+9 more)

### Community 7 - "Community 7"
Cohesion: 0.07
Nodes (29): "AI Paper of the Week", Build in Public on X/Twitter, code:block1 (Type 1: Progress update), code:block2 ("Used PaperBrain to read 'FlashAttention-3' today. Key insig), code:block3 (Hi [name],), Cold Outreach, Discord/Slack Community Deals, Free Public Artifacts (SEO hack) (+21 more)

### Community 8 - "Community 8"
Cohesion: 0.07
Nodes (28): Artifact Detail (`/artifact/[id]`), 🔐 Authentication, 💬 Chat Streaming (SSE), code:block1 (apps/web/), code:block2 (Background:  slate-950 (default dark)), code:typescript (// ✅ Correct pattern), code:typescript (['artifacts']              // all artifacts list), code:typescript (// lib/hooks/useChat.ts) (+20 more)

### Community 9 - "Community 9"
Cohesion: 0.07
Nodes (26): Backend: Planned Structure vs Reality, code:block1 (Backend:), Critical Path (Core Product Loop Broken Without These), Database: Models vs Migrations, Files That Need to Be Created (from Scratch), Frontend: Planned Structure vs Reality, High Priority (Product Incomplete Without These), Key Metrics (+18 more)

### Community 10 - "Community 10"
Cohesion: 0.08
Nodes (25): A. User Asks a Question (Chat), B. Daily Discovery Agent Run, C. Artifact Creation, code:block1 (┌───────────────────────────────────────────────────────────), code:block2 (1. User types question in ChatPanel.tsx), code:block3 (1. APScheduler fires at 6:00 AM UTC), code:block4 (1. User clicks [Create Artifact] on a paper), code:block5 (ArXiv API ──────────────────────────────────────────────────) (+17 more)

### Community 11 - "Community 11"
Cohesion: 0.1
Nodes (20): Guiding Principles, PaperBrain — Development Roadmap, Phase 1: MVP (Weeks 1–8), Phase 2: Core Product (Weeks 9–18), Phase 3: Growth (Weeks 19–30), Solo Founder Feasibility, Week 11–12: Orchestrator, Week 13–14: Integrations (+12 more)

### Community 12 - "Community 12"
Cohesion: 0.17
Nodes (9): get_current_user(), MockUser, BadRequestException, ForbiddenException, generic_exception_handler(), NotFoundException, PaperBrainException, UnauthorizedException (+1 more)

### Community 13 - "Community 13"
Cohesion: 0.12
Nodes (16): Code Style, code:block1 (Daily Cron → Discovery Agent → PDF Ingestion → Artifact Gene), code:block2 (paperbrain/), code:bash (# 1. Clone repo), ⚠️ Critical Constraints, 📋 Development Rules, ⚙️ Environment Variables, Git Workflow (+8 more)

### Community 14 - "Community 14"
Cohesion: 0.12
Nodes (16): AI APIs, App Config, Backend (`apps/api/.env`), Cloudflare R2 (File Storage), code:bash (# Copy this to .env and fill in your values), Database, Email, `.env.example` Template (Backend) (+8 more)

### Community 15 - "Community 15"
Cohesion: 0.33
Nodes (8): async_compile_and_send_digests(), async_scan_daily_research_papers(), compile_and_send_digests(), Helper to execute async coroutines from synchronous Celery workers., Scans the ArXiv API for newly published papers matching active user interest pro, Compiles matching DailyDigests and dispatches emails for all active users., run_async(), scan_daily_research_papers()

### Community 16 - "Community 16"
Cohesion: 0.29
Nodes (6): Run migrations in 'offline' mode.      This configures the context with just a U, In this scenario we need to create an Engine     and associate a connection with, Run migrations in 'online' mode., run_async_migrations(), run_migrations_offline(), run_migrations_online()

### Community 17 - "Community 17"
Cohesion: 0.4
Nodes (3): Message, NodePosition, Paper

## Knowledge Gaps
- **260 isolated node(s):** `Submit a technical question about a paper artifact.      Queries pgvector, build`, `Trigger the PDF ingestion flow.      Registers the paper in the database if new,`, `Run migrations in 'offline' mode.      This configures the context with just a U`, `In this scenario we need to create an Engine     and associate a connection with`, `Run migrations in 'online' mode.` (+255 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DigestService` connect `Community 6` to `Community 0`, `Community 15`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Why does `Paper` connect `Community 0` to `Community 6`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Why does `IngestionService` connect `Community 0` to `Community 6`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `Base` (e.g. with `Paper` and `DailyDigest`) actually correct?**
  _`Base` has 9 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Submit a technical question about a paper artifact.      Queries pgvector, build`, `Trigger the PDF ingestion flow.      Registers the paper in the database if new,`, `Run migrations in 'offline' mode.      This configures the context with just a U` to the rest of the system?**
  _260 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.06 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.04 - nodes in this community are weakly interconnected._