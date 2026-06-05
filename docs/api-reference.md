# PaperBrain — API Reference

> All endpoints use JSON. Auth via Bearer token (Supabase JWT) in Authorization header.
> Base URL: `https://api.paperbrain.app/v1`

---

## Standard Response Envelope

Every response follows this structure:

```json
// Success
{
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}

// Error
{
  "error": {
    "code": "ARTIFACT_NOT_FOUND",
    "message": "Human-readable message",
    "details": {}
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## Error Codes

| Code | HTTP | Description |
|---|---|---|
| `UNAUTHORIZED` | 401 | Missing or invalid JWT |
| `FORBIDDEN` | 403 | Resource belongs to another user |
| `NOT_FOUND` | 404 | Resource doesn't exist |
| `USAGE_LIMIT_REACHED` | 429 | Plan limit hit (not rate limit) |
| `RATE_LIMITED` | 429 | Too many requests |
| `ARTIFACT_NOT_READY` | 409 | Artifact still processing |
| `PDF_PARSE_FAILED` | 422 | Could not extract text from PDF |
| `INVALID_INPUT` | 400 | Validation error |
| `LLM_ERROR` | 503 | Upstream AI service error (retry) |

---

## Authentication

```
POST /auth/signup
POST /auth/login
POST /auth/logout
POST /auth/refresh
GET  /auth/me
```

Handled by Supabase Auth SDK on frontend. Backend validates JWT via Supabase public key.

---

## Users

### `GET /users/me`
Returns current user profile + plan info + usage summary.

**Response:**
```json
{
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "Alice",
    "plan": "pro",
    "interest_profile": {
      "topics": ["LLMs", "RAG"],
      "keywords": ["attention mechanism", "RLHF"],
      "authors": ["Andrej Karpathy"],
      "categories": ["cs.LG", "cs.AI"]
    },
    "usage": {
      "artifacts_this_month": 3,
      "artifacts_limit": 5,
      "questions_today": 12,
      "questions_limit": 20
    },
    "onboarded_at": "2024-01-01T00:00:00Z"
  }
}
```

### `PATCH /users/me`
Update profile, name, or interest profile.

**Body:**
```json
{
  "name": "Alice Smith",
  "interest_profile": {
    "topics": ["LLMs", "multimodal AI"],
    "keywords": ["chain of thought"],
    "authors": [],
    "categories": ["cs.LG"]
  }
}
```

---

## Papers

### `GET /papers/search`
Search ArXiv and Semantic Scholar. Does NOT save to DB — use for browse/discovery UI.

**Query params:** `q` (required), `source` (arxiv|semantic_scholar), `limit` (max 50), `date_from`

**Response:**
```json
{
  "data": {
    "papers": [
      {
        "arxiv_id": "2501.12345",
        "title": "Attention Is All You Need",
        "authors": [{"name": "Vaswani et al."}],
        "abstract": "...",
        "published_date": "2017-06-12",
        "categories": ["cs.LG"],
        "pdf_url": "https://arxiv.org/pdf/1706.03762",
        "has_artifact": false
      }
    ],
    "total": 100
  }
}
```

### `GET /papers/{paper_id}`
Get a specific paper by ID.

### `POST /papers/ingest`
Trigger PDF download + processing for a paper. Returns immediately, processing happens async.

**Body:**
```json
{
  "arxiv_id": "2501.12345"
}
```

**Response:**
```json
{
  "data": {
    "paper_id": "uuid",
    "status": "queued",
    "message": "Paper queued for processing"
  }
}
```

---

## Artifacts

### `GET /artifacts`
List user's artifacts with pagination.

**Query params:** `page`, `limit` (max 50), `status`, `collection_id`, `search` (semantic)

**Response:**
```json
{
  "data": {
    "artifacts": [
      {
        "id": "uuid",
        "paper": {
          "id": "uuid",
          "title": "...",
          "arxiv_id": "2501.12345",
          "authors": [...],
          "published_date": "2024-01-01"
        },
        "one_line_summary": "...",
        "status": "ready",
        "created_at": "..."
      }
    ],
    "total": 42,
    "page": 1
  }
}
```

### `POST /artifacts`
Create a new artifact for a paper. Triggers ingestion + generation pipeline.

**Rate limited:** 10/hour (free), 100/hour (pro)
**Usage limited:** 5/month (free), unlimited (pro)

**Body:**
```json
{
  "arxiv_id": "2501.12345"
}
```

**Response:**
```json
{
  "data": {
    "artifact_id": "uuid",
    "status": "queued",
    "estimated_ready_seconds": 120,
    "message": "Artifact creation started"
  }
}
```

### `GET /artifacts/{artifact_id}`
Get full artifact content. Returns 409 if status != 'ready'.

**Response:**
```json
{
  "data": {
    "id": "uuid",
    "status": "ready",
    "paper": { ... },
    "one_line_summary": "...",
    "summary": "300 word plain English summary...",
    "key_insights": [
      {
        "insight": "The model achieves 94.2% accuracy on GLUE benchmark...",
        "importance_score": 92,
        "section": "results"
      }
    ],
    "auto_qa": [
      {
        "question": "What problem does this paper solve?",
        "answer": "...",
        "difficulty": "easy"
      }
    ],
    "suggested_experiments": [
      {
        "description": "Reproduce the ablation study by removing...",
        "feasibility": "high",
        "expected_outcome": "..."
      }
    ],
    "created_at": "...",
    "updated_at": "..."
  }
}
```

### `GET /artifacts/{artifact_id}/status`
Poll artifact processing status. Use for progress UI.

**Response:**
```json
{
  "data": {
    "artifact_id": "uuid",
    "status": "generating",   // queued|ingesting|generating|ready|partial|failed
    "progress_message": "Generating key insights...",
    "error_message": null
  }
}
```

### `DELETE /artifacts/{artifact_id}`
Delete artifact and all associated conversations/annotations.

---

## Conversations (Chat)

### `GET /conversations/{artifact_id}`
Get full conversation history for an artifact.

**Response:**
```json
{
  "data": {
    "artifact_id": "uuid",
    "messages": [
      {
        "role": "user",
        "content": "What method does this paper use?",
        "timestamp": "..."
      },
      {
        "role": "assistant",
        "content": "The paper uses a transformer-based architecture...",
        "timestamp": "...",
        "sources": [
          { "section": "methods", "chunk_index": 5 }
        ]
      }
    ],
    "message_count": 4
  }
}
```

### `POST /conversations/{artifact_id}/chat`
Send a message. **Returns Server-Sent Events stream.**

**Rate limited:** 30/minute (all plans)
**Usage limited:** 20/day (free), unlimited (pro)

**Body:**
```json
{
  "message": "What experiments should I run to test this?"
}
```

**SSE Response format:**
```
data: {"type": "chunk", "content": "You could"}
data: {"type": "chunk", "content": " start by"}
data: {"type": "chunk", "content": " reproducing"}
data: {"type": "done", "sources": [{"section": "methods", "chunk_index": 3}]}
```

**Error during stream:**
```
data: {"type": "error", "code": "LLM_ERROR", "message": "Service temporarily unavailable"}
```

### `DELETE /conversations/{artifact_id}`
Clear conversation history for an artifact.

---

## Digests

### `GET /digests`
List user's daily digests.

**Query params:** `limit` (max 30), `status`

### `GET /digests/{date}`
Get digest for a specific date. Date format: `YYYY-MM-DD`

**Response:**
```json
{
  "data": {
    "date": "2024-01-15",
    "status": "ready",
    "papers": [
      {
        "arxiv_id": "2501.12345",
        "title": "...",
        "authors": [...],
        "relevance_score": 87,
        "relevance_reasons": [
          "Uses RAG architecture matching your interest in retrieval",
          "Authors include researchers you follow"
        ],
        "one_line_summary": "...",
        "has_artifact": false,
        "artifact_id": null
      }
    ],
    "paper_count": 5
  }
}
```

### `POST /digests/trigger`
Manually trigger a digest generation (useful for testing, throttled in production).

---

## Annotations

### `GET /annotations/{artifact_id}`
Get all annotations for an artifact.

### `POST /annotations/{artifact_id}`
Create a new annotation.

**Body:**
```json
{
  "type": "note",
  "content": "This approach could be applied to our use case at work",
  "metadata": {}
}
```

### `PATCH /annotations/{annotation_id}`
Update annotation content or metadata.

### `DELETE /annotations/{annotation_id}`

---

## Collections

### `GET /collections`
List user's collections.

### `POST /collections`
**Body:** `{ "name": "RAG Papers", "description": "...", "color": "#3B82F6" }`

### `POST /collections/{collection_id}/artifacts`
Add artifact to collection. **Body:** `{ "artifact_id": "uuid" }`

### `DELETE /collections/{collection_id}/artifacts/{artifact_id}`

---

## Billing

### `GET /billing/usage`
Current period usage stats for billing page.

### `POST /billing/create-checkout-session`
Create Stripe checkout. **Body:** `{ "plan": "pro", "period": "monthly" }`
**Response:** `{ "data": { "checkout_url": "https://checkout.stripe.com/..." } }`

### `POST /billing/create-portal-session`
Stripe customer portal for managing subscription.

### `POST /billing/webhook`
Stripe webhook endpoint. **No auth header** — verified via Stripe signature.
Handles: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`

---

## WebSocket / SSE Notes

- Chat uses SSE (POST + streaming response), not WebSocket
- Artifact status polling: use `GET /artifacts/{id}/status` every 3 seconds
- Supabase Realtime can also be used for artifact status updates if preferred

---

## Rate Limits

All limits enforced per `user_id` via Redis sliding window:

| Endpoint | Free | Pro | Team |
|---|---|---|---|
| `POST /artifacts` | 10/hour | 100/hour | 500/hour |
| `POST /conversations/*/chat` | 30/min | 30/min | 60/min |
| `GET /papers/search` | 60/min | 120/min | 120/min |
| `POST /papers/ingest` | 5/hour | 50/hour | 200/hour |
| All other GETs | 120/min | 300/min | 300/min |

Rate limit headers returned on all responses:
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 28
X-RateLimit-Reset: 1704067260
```
