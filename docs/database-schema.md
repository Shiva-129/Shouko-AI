# Shouko-AI — Database Schema

> PostgreSQL via Supabase with pgvector extension. All tables have Row-Level Security (RLS) enabled.

---

## Setup

```sql
-- Enable vector extension (run once)
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

---

## Tables

### `users`
Extends Supabase auth.users. Created automatically on signup via trigger.

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  avatar_url TEXT,
  plan TEXT NOT NULL DEFAULT 'free'  -- free | pro | team | enterprise
    CHECK (plan IN ('free', 'pro', 'team', 'enterprise')),
  stripe_customer_id TEXT UNIQUE,
  stripe_subscription_id TEXT,
  interest_profile JSONB NOT NULL DEFAULT '{
    "topics": [],
    "keywords": [],
    "authors": [],
    "categories": []
  }',
  -- topics: e.g. ["LLMs", "computer vision", "RL"]
  -- categories: ArXiv categories e.g. ["cs.LG", "cs.AI"]
  onboarded_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only see their own data"
  ON users FOR ALL USING (auth.uid() = id);
```

---

### `papers`
Raw paper records. Shared across all users (one paper, many users can have artifacts for it).

```sql
CREATE TABLE papers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  arxiv_id TEXT UNIQUE,              -- e.g. "2501.12345"
  semantic_scholar_id TEXT UNIQUE,
  title TEXT NOT NULL,
  abstract TEXT,
  authors JSONB NOT NULL DEFAULT '[]',  -- [{name, affiliations}]
  categories TEXT[] NOT NULL DEFAULT '{}',  -- ArXiv categories
  published_date DATE,
  updated_date DATE,
  pdf_url TEXT NOT NULL,
  pdf_storage_path TEXT,             -- R2 path after download
  source TEXT NOT NULL DEFAULT 'arxiv'
    CHECK (source IN ('arxiv', 'semantic_scholar', 'pubmed', 'manual')),
  citation_count INTEGER DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}',  -- source-specific extras
  pdf_processed BOOLEAN DEFAULT FALSE,
  pdf_processed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_papers_arxiv_id ON papers(arxiv_id) WHERE arxiv_id IS NOT NULL;
CREATE INDEX idx_papers_published_date ON papers(published_date DESC);
CREATE INDEX idx_papers_categories ON papers USING GIN(categories);
```

---

### `artifacts`
The living wiki. One per (user, paper) pair.

```sql
CREATE TABLE artifacts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  paper_id UUID NOT NULL REFERENCES papers(id),

  -- Generated content
  one_line_summary TEXT,             -- Tweet-length
  summary TEXT,                      -- Plain English, ~300 words
  key_insights JSONB NOT NULL DEFAULT '[]',
  -- [{insight: str, importance_score: 0-100, section: str}]
  auto_qa JSONB NOT NULL DEFAULT '[]',
  -- [{question: str, answer: str, difficulty: easy|medium|hard}]
  suggested_experiments JSONB NOT NULL DEFAULT '[]',
  -- [{description: str, feasibility: str, expected_outcome: str}]
  related_paper_ids UUID[] DEFAULT '{}',

  -- Semantic search vector for the artifact itself
  embedding VECTOR(1536),

  -- Status tracking
  status TEXT NOT NULL DEFAULT 'queued'
    CHECK (status IN ('queued', 'ingesting', 'generating', 'ready', 'partial', 'failed')),
  error_message TEXT,                -- Set if status = 'failed'
  version INTEGER NOT NULL DEFAULT 1,
  generation_cost_usd DECIMAL(10,6), -- Track actual LLM cost

  UNIQUE(user_id, paper_id),         -- One artifact per user per paper
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_artifacts_user_id ON artifacts(user_id);
CREATE INDEX idx_artifacts_status ON artifacts(status);
CREATE INDEX idx_artifacts_embedding ON artifacts
  USING ivfflat(embedding vector_cosine_ops) WITH (lists = 100);

-- RLS
ALTER TABLE artifacts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users own their artifacts"
  ON artifacts FOR ALL USING (auth.uid() = user_id);
```

---

### `paper_chunks`
PDF split into searchable pieces. Used for RAG.

```sql
CREATE TABLE paper_chunks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  paper_id UUID NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
  artifact_id UUID REFERENCES artifacts(id) ON DELETE CASCADE,

  content TEXT NOT NULL,
  chunk_index INTEGER NOT NULL,  -- order within paper
  section TEXT,                  -- abstract|introduction|methods|results|discussion|conclusion|references|other
  page_number INTEGER,
  token_count INTEGER,
  embedding VECTOR(1536) NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'
);

CREATE INDEX idx_chunks_paper_id ON paper_chunks(paper_id);
CREATE INDEX idx_chunks_embedding ON paper_chunks
  USING ivfflat(embedding vector_cosine_ops) WITH (lists = 200);

-- Note: No RLS on chunks — access controlled at artifact level
-- Chunks are shared across users who have artifacts for the same paper
```

---

### `conversations`
Chat history per artifact per user.

```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  artifact_id UUID NOT NULL REFERENCES artifacts(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  messages JSONB NOT NULL DEFAULT '[]',
  -- [{role: user|assistant, content: str, timestamp: iso, sources: [{chunk_id, section}]}]
  message_count INTEGER NOT NULL DEFAULT 0,
  total_tokens_used INTEGER NOT NULL DEFAULT 0,

  UNIQUE(artifact_id, user_id),    -- One conversation thread per artifact
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_artifact ON conversations(artifact_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);

ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users own their conversations"
  ON conversations FOR ALL USING (auth.uid() = user_id);
```

---

### `annotations`
User notes, highlights, experiments attached to artifacts.

```sql
CREATE TABLE annotations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  artifact_id UUID NOT NULL REFERENCES artifacts(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type TEXT NOT NULL CHECK (type IN ('note', 'highlight', 'experiment', 'task', 'link')),
  content TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}',
  -- For highlight: {start_offset, end_offset, context_text}
  -- For experiment: {status: planned|running|done, result: str}
  -- For task: {completed: bool, due_date: str}
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE annotations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users own their annotations"
  ON annotations FOR ALL USING (auth.uid() = user_id);
```

---

### `collections`
User-organized groups of artifacts.

```sql
CREATE TABLE collections (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  color TEXT DEFAULT '#3B82F6',  -- hex color for UI
  artifact_ids UUID[] NOT NULL DEFAULT '{}',
  is_default BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE collections ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users own their collections"
  ON collections FOR ALL USING (auth.uid() = user_id);
```

---

### `daily_digests`
Output of daily discovery agent runs.

```sql
CREATE TABLE daily_digests (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  paper_scores JSONB NOT NULL DEFAULT '[]',
  -- [{paper_id, arxiv_id, title, relevance_score, relevance_reasons: [], one_line_summary}]
  paper_count INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'ready', 'sent', 'skipped')),
  email_sent_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  UNIQUE(user_id, date)
);

CREATE INDEX idx_digests_user_date ON daily_digests(user_id, date DESC);

ALTER TABLE daily_digests ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users own their digests"
  ON daily_digests FOR ALL USING (auth.uid() = user_id);
```

---

### `usage_events`
Billing and limit enforcement.

```sql
CREATE TABLE usage_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL
    CHECK (event_type IN ('artifact_created', 'question_asked', 'paper_ingested', 'report_generated')),
  metadata JSONB NOT NULL DEFAULT '{}',
  -- {artifact_id, paper_id, tokens_used, cost_usd}
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_usage_user_month ON usage_events(user_id, date_trunc('month', created_at));
CREATE INDEX idx_usage_type ON usage_events(user_id, event_type, created_at DESC);

-- Usage counting query (used in check_usage_limit middleware)
-- SELECT COUNT(*) FROM usage_events
-- WHERE user_id = $1 AND event_type = $2
-- AND created_at > date_trunc('month', NOW())
```

---

### `teams` + `team_members`
Phase 2. Multi-seat team plan.

```sql
CREATE TABLE teams (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  owner_id UUID NOT NULL REFERENCES users(id),
  plan TEXT NOT NULL DEFAULT 'team',
  stripe_subscription_id TEXT,
  max_seats INTEGER NOT NULL DEFAULT 5,
  settings JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE team_members (
  team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
  invited_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  joined_at TIMESTAMPTZ,
  PRIMARY KEY (team_id, user_id)
);
```

---

## Useful Queries

### Get user's artifacts with paper info
```sql
SELECT a.*, p.title, p.authors, p.published_date, p.arxiv_id
FROM artifacts a
JOIN papers p ON p.id = a.paper_id
WHERE a.user_id = $1 AND a.status = 'ready'
ORDER BY a.created_at DESC
LIMIT 20;
```

### Semantic search across user's library
```sql
SELECT a.id, a.one_line_summary, p.title,
       1 - (a.embedding <=> $1::vector) AS similarity
FROM artifacts a
JOIN papers p ON p.id = a.paper_id
WHERE a.user_id = $2 AND a.status = 'ready'
  AND 1 - (a.embedding <=> $1::vector) > 0.7
ORDER BY similarity DESC
LIMIT 10;
```

### Check monthly usage
```sql
SELECT event_type, COUNT(*) as count
FROM usage_events
WHERE user_id = $1
  AND created_at > date_trunc('month', NOW())
GROUP BY event_type;
```

### RAG chunk retrieval
```sql
SELECT pc.content, pc.section, pc.chunk_index, pc.page_number,
       1 - (pc.embedding <=> $1::vector) AS similarity
FROM paper_chunks pc
WHERE pc.paper_id = $2
  AND 1 - (pc.embedding <=> $1::vector) > 0.5
ORDER BY similarity DESC
LIMIT 8;
```
