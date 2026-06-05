# Architecture Documentation

## 1. System Overview (C4 Context Level)
This diagram provides a high-level view of the entire Shouko-AI system. It shows the primary user interacting with the Next.js frontend, which connects to the FastAPI backend. The backend manages background tasks via Celery and APScheduler, stores data in PostgreSQL (with pgvector), caches in Redis, and communicates with various external APIs (OpenRouter, Groq, ArXiv, Stripe, Resend) to deliver AI research capabilities.

```mermaid
graph TB
    User((User Browser))

    subgraph Frontend [Next.js Frontend - Vercel]
        WebApp[Web Application]
    end

    subgraph Backend [FastAPI Backend - Railway]
        API[FastAPI Server]
        CeleryWorker[Celery Worker]
        Scheduler[APScheduler]
    end

    subgraph Data [Data Layer - Supabase/Upstash]
        DB[(PostgreSQL + pgvector)]
        Auth[Supabase Auth]
        Redis[(Redis)]
        Storage[(Cloudflare R2 - planned)]
    end

    subgraph External [External APIs]
        OpenRouter[OpenRouter API<br>LLM & Embeddings]
        Groq[Groq API<br>Discovery Agent]
        ArXiv[ArXiv API]
        Stripe[Stripe API]
        Resend[Resend API]
    end

    User --> WebApp
    User --> Auth
    WebApp --> API
    API --> DB
    API --> Redis
    API --> CeleryWorker
    API --> Scheduler

    CeleryWorker --> DB
    CeleryWorker --> Redis

    API --> Stripe
    API --> OpenRouter
    CeleryWorker --> OpenRouter
    CeleryWorker --> Groq
    CeleryWorker --> ArXiv
    CeleryWorker --> Resend
```

## 2. Paper Ingestion Pipeline
This sequence details the paper ingestion and artifact generation process. It starts with the user submitting a paper URL. The backend downloads and parses the PDF, chunks the text, and stores the embeddings. Then, it triggers an asynchronous Celery task to generate an artifact using the ArtifactAgent (via OpenRouter's LLM), eventually marking the artifact as "ready".

```mermaid
sequenceDiagram
    participant User
    participant Router as Papers & Artifacts Router
    participant Ingestion as Ingestion Service
    participant PDF as PDF Service
    participant Embed as Embedding Service
    participant DB as PostgreSQL (pgvector)
    participant Celery as Celery Worker
    participant Agent as ArtifactAgent
    participant LLM as LLMService (OpenRouter)

    User->>Router: POST /papers/ingest
    Router->>Ingestion: process paper
    Ingestion->>Ingestion: download PDF
    Ingestion->>PDF: extract_text_by_page()
    PDF-->>Ingestion: pages
    Ingestion->>PDF: chunk_text(pages)
    PDF-->>Ingestion: text chunks
    Ingestion->>Embed: get_embeddings(chunks)
    Embed-->>Ingestion: vectors
    Ingestion->>DB: store PaperChunks
    Ingestion-->>Router: return paper info
    Router-->>User: HTTP 201 Created

    User->>Router: POST /artifacts
    Router->>DB: create artifact (status: queued)
    Router->>Celery: queue generate_artifact task
    Router-->>User: HTTP 201 Created

    Celery->>Celery: update status -> ingesting
    Celery->>Agent: generate()
    Celery->>Celery: update status -> generating
    Agent->>LLM: generate_completion()
    LLM-->>Agent: JSON output
    Agent->>Agent: parse ArtifactOutput
    Agent->>DB: store to Artifact table
    Agent->>DB: update status -> ready
```

## 3. RAG Chat Flow
This sequence describes how the user interacts with the generated artifact via chat. The frontend streams the response from the backend. The backend retrieves the most relevant paper chunks using pgvector, compiles a RAG prompt, and streams the response back to the user via the LLMService connected to OpenRouter.

```mermaid
sequenceDiagram
    participant User
    participant Frontend as ChatPanel.tsx
    participant Router as Chat Router
    participant RAG as RAG Service
    participant DB as PostgreSQL (pgvector)
    participant LLM as LLMService (OpenRouter)

    User->>Frontend: types question
    Frontend->>Router: POST /conversations/{id}/chat (useSSEChat)
    Router->>Router: check rate_limit
    Router->>RAG: retrieve_context_chunks(question, artifact_id)
    RAG->>DB: cosine similarity search
    DB-->>RAG: top K chunks
    RAG->>RAG: compile_rag_prompt(chunks, question)
    RAG->>LLM: stream_chat_response(prompt)
    LLM-->>Router: OpenRouter SSE stream
    Router-->>Frontend: Server-Sent Events stream
    Frontend-->>User: render in MessageList.tsx
```

## 4. Daily Discovery & Digest Flow
This diagram illustrates the automated daily process that scans for new research papers and sends personalized digests to users. The APScheduler triggers the daily job which fetches new papers from ArXiv, scores them using the DiscoveryAgent, and stores the results. A subsequent task compiles and emails the digests via Resend.

```mermaid
sequenceDiagram
    participant Scheduler as APScheduler (06:00 UTC)
    participant ScanTask as scan_daily_research_papers (Celery)
    participant ArXiv as ArXiv API
    participant Agent as DiscoveryAgent (Groq/LLMService)
    participant DB as PostgreSQL
    participant CompileTask as compile_and_send_digests (Celery)
    participant DigestSvc as DigestService
    participant Email as Email Service (Resend)

    Scheduler->>ScanTask: daily_scan_job()
    ScanTask->>ArXiv: fetch by user categories
    ArXiv-->>ScanTask: recent papers
    ScanTask->>Agent: score_papers()
    Note right of Agent: Groq llama-3.1-8b-instant (primary)<br>Fallback: LLMService or keyword match
    Agent-->>ScanTask: paper scores and reasons
    ScanTask->>DB: store DailyDigest

    Scheduler->>CompileTask: compile_and_send_digests()
    CompileTask->>DigestSvc: compile_user_daily_digest()
    DigestSvc->>DB: retrieve digests
    DB-->>DigestSvc: digest data
    DigestSvc->>Email: send_digest_email()
    Email->>Resend: API request
```

## 5. Authentication Flow
This diagram outlines the authentication mechanisms. It covers the initial sign-in via Supabase OAuth, user creation in the local database upon callback, and the standard Bearer token validation for subsequent API requests using JWKS. It also notes a developer bypass mode for local testing.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Supabase as Supabase OAuth
    participant Callback as callback route (/auth/callback)
    participant API as FastAPI Backend
    participant DB as PostgreSQL

    User->>Frontend: First login
    Frontend->>Supabase: redirect to provider
    Supabase-->>Frontend: redirect with auth code
    Frontend->>Callback: handle code, get session
    Callback->>API: GET /users/me (with JWT)
    API->>API: security.py JWKS validation
    API->>DB: auto-create user
    API->>API: send_welcome_email()
    API-->>Callback: User model
    Callback-->>Frontend: authenticated state

    User->>Frontend: Subsequent requests
    Frontend->>API: API call (inject Bearer token)
    API->>API: get_current_user() (JWKS cache check)
    Note right of API: Dev mode: MockUser bypass available
    API->>DB: get user if not cached
    API-->>Frontend: Response
```

## 6. Full Backend Module Graph
This graph represents the modular architecture of the FastAPI backend. The codebase is organized into core components (config, DB, auth), services (business logic, external APIs), models (SQLAlchemy ORM), agents (AI logic with specific prompts), routers (API endpoints), and Celery tasks.

```mermaid
graph LR
    subgraph routers
        R_users[users.py]
        R_chat[chat.py]
        R_papers[papers.py]
        R_artifacts[artifacts.py]
        R_digests[digests.py]
        R_collections[collections.py]
        R_annotations[annotations.py]
        R_billing[billing.py]
    end

    subgraph services
        S_llm[llm_service.py]
        S_embed[embedding_service.py]
        S_pdf[pdf_service.py]
        S_ingest[ingestion_service.py]
        S_rag[rag_service.py]
        S_digest[digest_service.py]
        S_billing[billing_service.py]
        S_email[email_service.py]
    end

    subgraph agents
        A_artifact[artifact_agent.py]
        A_discovery[discovery_agent.py]
    end

    subgraph prompts
        P_artifact[artifact_generation.py]
        P_discovery[discovery.py]
        P_rag[rag_qa.py]
    end

    subgraph models
        M_user[user.py]
        M_paper[paper.py]
        M_chunk[chunk.py]
        M_artifact[artifact.py]
        M_conversation[conversation.py]
        M_digest[digest.py]
        M_collection[collection.py]
        M_annotation[annotation.py]
        M_usage[usage.py]
    end

    subgraph core
        C_config[config.py]
        C_db[database.py]
        C_security[security.py]
        C_celery[celery_app.py]
        C_deps[dependencies.py]
        C_sched[scheduler.py]
        C_redis[redis.py]
        C_limit[rate_limit.py]
    end

    subgraph tasks
        T_artifact[generate_artifact.py]
        T_digest[digest_tasks.py]
    end

    routers --> services
    routers --> core
    routers --> models
    services --> core
    services --> models
    agents --> services
    agents --> prompts
    tasks --> agents
    tasks --> services
    tasks --> core
```

## 7. Frontend Component Tree
This chart visualizes the Next.js frontend structure. It highlights the App Router layout hierarchy, primary pages (dashboard, library, digest, artifact), shared UI components, and the underlying custom hooks and API layer.

```mermaid
graph TD
    Root[app/layout.tsx] --> Providers[providers.tsx]
    Providers --> UpgradeModal[UpgradeModal.tsx]

    Root --> DashboardLayout[(dashboard)/layout.tsx]
    DashboardLayout --> Sidebar[Sidebar.tsx]
    DashboardLayout --> MobileHeader[MobileHeader.tsx]

    DashboardLayout --> DashboardPage[dashboard/page.tsx]
    DashboardLayout --> LibraryPage[library/page.tsx]
    DashboardLayout --> CollectionsPage[collections/page.tsx]
    DashboardLayout --> SettingsPage[settings/page.tsx]
    DashboardLayout --> DigestPage[digest/page.tsx]
    DashboardLayout --> ArtifactPage[artifact/:id/page.tsx]

    DigestPage --> PaperCard[PaperCard.tsx]

    ArtifactPage --> StatusBadge[StatusBadge.tsx]
    ArtifactPage --> InsightsList[InsightsList.tsx]
    ArtifactPage --> SuggestedExperiments[SuggestedExperiments.tsx]
    ArtifactPage --> AutoQA[AutoQA.tsx]
    ArtifactPage --> AnnotationsTab[AnnotationsTab.tsx]
    ArtifactPage --> ChatPanel[ChatPanel.tsx]

    ChatPanel --> MessageList[MessageList.tsx]
    MessageList --> StreamingMessage[StreamingMessage.tsx]
    ChatPanel --> MessageInput[MessageInput.tsx]

    subgraph Shared
        UsageBanner[UsageBanner.tsx]
        EmptyState[EmptyState.tsx]
        ErrorBoundary[ErrorBoundary.tsx]
    end

    subgraph Hooks
        useUser
        useArtifact
        useDigest
        useSSEChat
        useUpgradeModal
    end

    subgraph API
        api_client[lib/api.ts]
    end

    Hooks --> api_client
```

## 8. Data Model ERD
This Entity-Relationship Diagram defines the relational structure in the PostgreSQL database. It displays the central User table and its links to collections, artifacts, papers (with chunks for RAG), conversations, and billing events.

```mermaid
erDiagram
    USER ||--o{ PAPER : ingests
    USER ||--o{ COLLECTION : owns
    USER ||--o{ ARTIFACT : owns
    USER ||--o{ CONVERSATION : participates
    USER ||--o{ DAILY_DIGEST : receives
    USER ||--o{ USAGE_EVENT : generates

    PAPER ||--o{ PAPER_CHUNK : split_into
    PAPER ||--o{ ARTIFACT : analyzed_as

    ARTIFACT ||--o{ CONVERSATION : contextualizes
    ARTIFACT ||--o{ ANNOTATION : has

    COLLECTION ||--o{ ARTIFACT : contains

    USER {
        uuid id PK
        string email
        string plan
        string stripe_customer_id
    }

    PAPER {
        uuid id PK
        uuid user_id FK
        string title
        string url
    }

    PAPER_CHUNK {
        uuid id PK
        uuid paper_id FK
        vector embedding
        text content
    }

    ARTIFACT {
        uuid id PK
        uuid paper_id FK
        uuid user_id FK
        string status
        jsonb key_insights
    }

    CONVERSATION {
        uuid id PK
        uuid artifact_id FK
        uuid user_id FK
        jsonb history
    }

    DAILY_DIGEST {
        uuid id PK
        uuid user_id FK
        date date
        jsonb paper_scores
    }

    COLLECTION {
        uuid id PK
        uuid user_id FK
        string name
    }

    USAGE_EVENT {
        uuid id PK
        uuid user_id FK
        string event_type
    }

    ANNOTATION {
        uuid id PK
        uuid artifact_id FK
        string content
    }
```

## 9. Billing Flow
This diagram details the upgrade process and usage limit enforcement. Users can initiate a checkout via Stripe, with webhooks asynchronously updating their plan. Free-tier limits trigger interceptors that show the UpgradeModal globally.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API as BillingService
    participant Stripe
    participant Webhook as Webhook Route
    participant DB

    User->>Frontend: Clicks Upgrade
    Frontend->>API: POST /billing/checkout
    API->>Stripe: Create Checkout Session
    Stripe-->>API: checkout_url
    API-->>Frontend: redirect URL
    Frontend->>Stripe: Redirect user to Stripe
    User->>Stripe: Completes Payment

    Stripe->>Webhook: POST /billing/webhook (subscription.created)
    Webhook->>DB: user.plan = "pro"

    Note over User, DB: Downgrade Scenario
    Stripe->>Webhook: POST /billing/webhook (subscription.deleted)
    Webhook->>DB: user.plan = "free"

    Note over User, DB: Usage Limit Flow
    Frontend->>API: Request Action
    API-->>Frontend: 429 Too Many Requests (Free Limit)
    Frontend->>Frontend: api.ts intercepts 429
    Frontend->>Frontend: useUpgradeModal.open()
    Frontend->>User: UpgradeModal rendered globally
```
