# PaperBrain — Security & Compliance

> Security rules, GDPR requirements, abuse prevention, and backup strategy.

---

## Authentication Security

### JWT Tokens (Supabase Auth)
- Access token expiry: **1 hour**
- Refresh token expiry: **7 days** (rotated on each use)
- Algorithm: RS256 (asymmetric — backend verifies with public key only)
- Session invalidation: triggered on password change, manual logout

### Backend JWT Validation
```python
# core/security.py
from supabase import create_client

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

async def get_current_user(authorization: str = Header(...)) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing bearer token")
    token = authorization[7:]
    try:
        # Supabase validates signature, expiry, and issuer
        user = supabase.auth.get_user(token)
        return user
    except Exception:
        raise HTTPException(401, "Invalid or expired token")
```

### Password Policy
- Minimum 8 characters (enforced by Supabase)
- No maximum (allow passphrases)
- Bcrypt hashing (handled by Supabase)
- Password reset via email OTP (Supabase magic link)

---

## Authorization

**Rule: Never trust user-supplied IDs. Always verify ownership.**

```python
# ✅ Correct: always join with user_id from JWT
async def get_artifact(artifact_id: UUID, current_user: User = Depends(get_current_user), db = Depends(get_db)):
    artifact = await db.execute(
        select(Artifact).where(
            Artifact.id == artifact_id,
            Artifact.user_id == current_user.id  # ← ownership check
        )
    )
    if not artifact:
        raise HTTPException(404, "Artifact not found")  # not 403 — don't reveal existence

# ❌ Wrong: lookup by ID alone
artifact = await db.get(Artifact, artifact_id)  # could belong to anyone
```

---

## Rate Limiting

Implemented in `core/rate_limit.py` using Redis sliding window.

```python
class RateLimiter:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def check(self, key: str, limit: int, window_seconds: int) -> bool:
        pipe = self.redis.pipeline()
        now = time.time()
        window_start = now - window_seconds

        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, window_seconds)
        results = await pipe.execute()

        count = results[2]
        return count <= limit
```

**Rate limit keys:** `rate:{user_id}:{endpoint}` — per user, per endpoint.

**Limits:**
```
POST /artifacts          → 10/hour (free), 100/hour (pro)
POST /conversations/chat → 30/min (all plans)
GET  /papers/search      → 60/min (all plans)
POST /auth/*             → 10/min (all plans, brute force protection)
All other endpoints      → 120/min (free), 300/min (pro)
```

**Headers returned:**
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 27
X-RateLimit-Reset: 1704067260  (Unix timestamp)
```

---

## Input Sanitization

### Prompt Injection Prevention
```python
# core/security.py
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above|prior)\s+instructions",
    r"you\s+are\s+now",
    r"new\s+system\s+prompt",
    r"forget\s+everything",
    r"act\s+as\s+(?!a\s+researcher)",
    r"jailbreak",
    r"<\|im_start\|>",      # ChatML injection
    r"\[INST\]",            # Llama injection
    r"SYSTEM:",             # System prompt injection
]

def sanitize_user_input(text: str) -> str:
    """Sanitize user input before it reaches any LLM prompt."""
    if len(text) > 2000:
        raise ValueError("Input exceeds maximum length")

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            raise HTTPException(400, {
                "code": "INVALID_INPUT",
                "message": "Input contains prohibited content"
            })

    # Remove null bytes and control characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text.strip()
```

### PDF Validation
```python
ALLOWED_MIME_TYPES = {"application/pdf"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB

async def validate_pdf(file: UploadFile) -> bytes:
    content = await file.read()

    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(400, "File exceeds 50MB limit")

    # Check magic bytes (PDF starts with %PDF-)
    if not content[:5] == b'%PDF-':
        raise HTTPException(400, "Invalid PDF file")

    return content
```

---

## Encryption

### At Rest
- PostgreSQL data: encrypted by Supabase (AES-256)
- R2 PDF storage: encrypted by Cloudflare (AES-256)
- Redis: data is ephemeral (cache + queues), not sensitive

### In Transit
- All HTTP: TLS 1.3 via Cloudflare (enforced, HTTP → HTTPS redirect)
- DB connections: TLS required (`sslmode=require` in DATABASE_URL)
- Redis: TLS for Upstash (`rediss://` URL scheme)

### Sensitive Fields
```python
# API keys in DB (if stored): encrypt with Fernet before storing
from cryptography.fernet import Fernet

fernet = Fernet(settings.ENCRYPTION_KEY)

def encrypt(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()

def decrypt(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()
```

---

## GDPR Compliance

### Data We Collect
| Data | Purpose | Retention |
|---|---|---|
| Email address | Auth, notifications | Until account deletion |
| Name | Display | Until account deletion |
| Interest profile | Paper recommendations | Until account deletion |
| Paper artifacts | Core product value | Until account deletion |
| Conversation history | Chat continuity | Until cleared or account deleted |
| Usage events | Billing, limits | 13 months |
| Stripe customer ID | Payment management | Per Stripe's retention policy |

### User Rights Implementation

**Right to access (data export):**
```
GET /users/me/export
```
Returns ZIP of all user data: artifacts, conversations, annotations as JSON.

**Right to erasure (account deletion):**
```
DELETE /users/me
```
- Deletes all user data from all tables (CASCADE)
- Cancels Stripe subscription
- Triggers Supabase auth user deletion
- Must complete within 30 days (our implementation: immediate)

**Right to rectification:**
- Users can update email, name, interest profile at any time

### Required Legal Pages (before launch)
- [ ] Privacy Policy (what data you collect, how you use it, third parties)
- [ ] Terms of Service (usage rules, liability limits)
- [ ] Cookie Policy (PostHog cookies, Supabase session cookies)

### Cookie Consent
- Use a lightweight cookie banner (e.g., Cookieyes or custom)
- Only analytics cookies require consent (auth cookies are necessary)
- Respect user choice: if declined, don't initialize PostHog

---

## API Key Security

**Rules (non-negotiable):**
1. `ANTHROPIC_API_KEY` — backend only, never in frontend code, never in logs
2. `OPENAI_API_KEY` — backend only
3. `STRIPE_SECRET_KEY` — backend only (use publishable key on frontend)
4. `SUPABASE_SERVICE_KEY` — backend only (use anon key on frontend)
5. Never log API keys even partially (no `key[:10]` in logs)
6. Rotate immediately if any key appears in git history

**Scanning for leaked secrets:**
```bash
# Install trufflehog
pip install trufflehog

# Scan entire git history before pushing
trufflehog git file://. --only-verified

# Add to pre-commit hook
# .git/hooks/pre-commit
trufflehog git file://. --only-verified --fail
```

---

## Abuse Prevention

### Suspicious Activity Detection
```python
# Flag accounts for review if:
ABUSE_THRESHOLDS = {
    "artifacts_per_hour": 20,     # Normal max: 10/hour
    "questions_per_minute": 60,   # Normal max: 30/min
    "pdf_uploads_per_hour": 10,   # Normal max: 5/hour
    "failed_auth_attempts": 10,   # Per IP, per hour
}

# Action: flag in DB, send alert to admin, throttle requests
```

### Content Filtering
- Reject PDFs that are not academic papers (check for abstract, references)
- Reject user inputs containing hate speech, illegal content (basic pattern check)
- Never process PDFs containing executable content

---

## Backup Strategy

### Database (Supabase)
- Automatic daily backups (included in Supabase Pro: 30-day retention)
- Point-in-time recovery: enabled
- Weekly backup test: automated restore to staging and verify

### File Storage (R2)
- Versioning: enabled on R2 bucket
- Deletion protection: deleted files retained for 30 days
- Cross-region replication: add in Phase 2 for enterprise customers

### Configuration Backups
- All infrastructure config in Git
- Environment variables documented in `docs/environment-variables.md`
- Railway/Vercel config exported to `infrastructure/` directory

---

## Disaster Recovery

### RTO and RPO
- **RTO** (Recovery Time Objective): **4 hours** — time to restore service
- **RPO** (Recovery Point Objective): **24 hours** — max data loss acceptable

### Incident Playbook

**API is down:**
1. Check Railway dashboard for error logs
2. Check Sentry for recent errors
3. Check DB connection (Supabase status page)
4. Restart API service in Railway
5. If persistent: rollback to previous deployment

**Database corrupted:**
1. Stop all API servers (prevent further writes)
2. Create Supabase support ticket
3. Restore from latest backup (Supabase dashboard)
4. Replay any lost events from Celery logs
5. Restart API servers

**LLM API outage (Anthropic down):**
1. Artifact generation: queue jobs, retry when service resumes
2. Chat: return 503 with "AI service temporarily unavailable"
3. Discovery agent: skip run, resume next day
4. User communication: status page update

### Status Page
- Use Better Uptime's free status page (status.paperbrain.app)
- Monitors: API health endpoint, frontend, database connectivity
- Auto-post incidents to status page

---

## SOC2 Readiness (Phase 3, Enterprise)

Not required for MVP. When enterprise customers ask:

**Controls to implement:**
- [ ] Audit logging: all admin actions logged to immutable store
- [ ] Access reviews: quarterly review of who has production access
- [ ] Vulnerability scanning: automated dependency scanning (Dependabot)
- [ ] Penetration testing: annual third-party pentest
- [ ] Security training: annual security awareness (even if solo)
- [ ] Incident response plan: written and tested
- [ ] Employee background checks: if hiring

**Estimated timeline to SOC2 Type 1:** 3-4 months once you decide to pursue it.
**Cost:** $15,000–30,000 (auditor fees + tooling).
