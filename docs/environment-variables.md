# Shouko-AI — Environment Variables Reference

> Complete list of all environment variables needed to run the project.
> Never commit actual values. Use `.env.example` files with placeholder values.

---

## Backend (`apps/api/.env`)

### App Config
| Variable | Required | Example | Description |
|---|---|---|---|
| `ENVIRONMENT` | ✅ | `development` | `development` / `staging` / `production` |
| `APP_SECRET_KEY` | ✅ | `abc123...` | 32-char random string. Run: `openssl rand -hex 32` |
| `ALLOWED_ORIGINS` | ✅ | `http://localhost:3000` | Comma-separated CORS origins |
| `API_VERSION` | ❌ | `v1` | API version prefix (default: v1) |
| `LOG_LEVEL` | ❌ | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |

### Database
| Variable | Required | Example | Description |
|---|---|---|---|
| `DATABASE_URL` | ✅ | `postgresql+asyncpg://user:pass@localhost:5432/shouko` | Async PostgreSQL URL |
| `SUPABASE_URL` | ✅ | `https://abc.supabase.co` | Your Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | `eyJ...` | Service role key (has full DB access — keep secret!) |

### Redis / Cache
| Variable | Required | Example | Description |
|---|---|---|---|
| `REDIS_URL` | ✅ (local) | `redis://localhost:6379` | Local Redis URL |
| `UPSTASH_REDIS_REST_URL` | ✅ (prod) | `https://...upstash.io` | Upstash Redis REST URL (production) |
| `UPSTASH_REDIS_REST_TOKEN` | ✅ (prod) | `AX...` | Upstash Redis token (production) |

### AI APIs
| Variable | Required | Example | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | ✅ | `sk-ant-api03-...` | Claude API key — NEVER expose to frontend |
| `OPENAI_API_KEY` | ✅ | `sk-proj-...` | OpenAI key for embeddings (text-embedding-3-small) |

### Cloudflare R2 (File Storage)
| Variable | Required | Example | Description |
|---|---|---|---|
| `R2_ACCOUNT_ID` | ✅ | `abc123def456` | Cloudflare account ID |
| `R2_ACCESS_KEY_ID` | ✅ | `...` | R2 API token access key |
| `R2_SECRET_ACCESS_KEY` | ✅ | `...` | R2 API token secret |
| `R2_BUCKET_NAME` | ✅ | `shouko-pdfs` | R2 bucket name |
| `R2_PUBLIC_URL` | ✅ | `https://pdfs.shouko-ai.app` | Public URL for R2 bucket |

### Stripe (Payments)
| Variable | Required | Example | Description |
|---|---|---|---|
| `STRIPE_SECRET_KEY` | ✅ | `sk_live_...` | Stripe secret key (use `sk_test_...` for dev) |
| `STRIPE_WEBHOOK_SECRET` | ✅ | `whsec_...` | Stripe webhook signing secret |
| `STRIPE_PRO_MONTHLY_PRICE_ID` | ✅ | `price_...` | Stripe Price ID for Pro monthly |
| `STRIPE_PRO_YEARLY_PRICE_ID` | ✅ | `price_...` | Stripe Price ID for Pro yearly |
| `STRIPE_TEAM_MONTHLY_PRICE_ID` | ✅ | `price_...` | Stripe Price ID for Team monthly |

### Email
| Variable | Required | Example | Description |
|---|---|---|---|
| `RESEND_API_KEY` | ✅ | `re_...` | Resend API key for transactional email |
| `FROM_EMAIL` | ✅ | `hello@shouko-ai.app` | From address for outgoing emails |
| `FROM_NAME` | ❌ | `Shouko-AI` | From name (default: Shouko-AI) |

### Monitoring
| Variable | Required | Example | Description |
|---|---|---|---|
| `SENTRY_DSN` | ✅ (prod) | `https://...@sentry.io/...` | Sentry error tracking DSN |
| `LOGFIRE_TOKEN` | ❌ | `...` | Logfire structured logging token |

### Usage Limits
| Variable | Required | Default | Description |
|---|---|---|---|
| `FREE_ARTIFACTS_PER_MONTH` | ❌ | `5` | Max artifacts for free plan |
| `FREE_QUESTIONS_PER_DAY` | ❌ | `20` | Max chat questions for free plan |
| `FREE_PAPERS_PER_MONTH` | ❌ | `10` | Max paper ingestions for free plan |
| `MAX_PDF_SIZE_MB` | ❌ | `50` | Max allowed PDF size |
| `MAX_CHUNK_TOKENS` | ❌ | `512` | Tokens per chunk for RAG |

---

## Frontend (`apps/web/.env.local`)

| Variable | Required | Example | Description |
|---|---|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | ✅ | `https://abc.supabase.co` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | ✅ | `eyJ...` | Supabase anon key (safe for frontend) |
| `NEXT_PUBLIC_API_URL` | ✅ | `http://localhost:8000/v1` | Backend API base URL |
| `NEXT_PUBLIC_APP_URL` | ✅ | `http://localhost:3000` | Frontend app URL |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | ✅ | `pk_live_...` | Stripe publishable key (safe for frontend) |
| `NEXT_PUBLIC_POSTHOG_KEY` | ❌ | `phc_...` | PostHog analytics key |
| `NEXT_PUBLIC_POSTHOG_HOST` | ❌ | `https://app.posthog.com` | PostHog host |
| `NEXT_PUBLIC_SENTRY_DSN` | ❌ | `https://...@sentry.io` | Sentry (frontend) DSN |

---

## GitHub Actions Secrets

Set these in GitHub repo → Settings → Secrets and variables → Actions:

| Secret | Description |
|---|---|
| `RAILWAY_TOKEN` | Railway API token for deployment |
| `VERCEL_TOKEN` | Vercel API token for deployment |
| `VERCEL_ORG_ID` | Vercel org ID |
| `VERCEL_PROJECT_ID` | Vercel project ID |
| `TEST_DATABASE_URL` | Postgres URL for CI test DB |
| `TEST_ANTHROPIC_API_KEY` | API key for running evals in CI |

---

## `.env.example` Template (Backend)

```bash
# Copy this to .env and fill in your values
# DO NOT commit .env to git

ENVIRONMENT=development
APP_SECRET_KEY=change-me-32-chars-minimum-here
ALLOWED_ORIGINS=http://localhost:3000

DATABASE_URL=postgresql+asyncpg://postgres:localpass@localhost:5432/shouko
SUPABASE_URL=https://yourproject.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

REDIS_URL=redis://localhost:6379

ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
OPENAI_API_KEY=sk-proj-your-key-here

R2_ACCOUNT_ID=your-cloudflare-account-id
R2_ACCESS_KEY_ID=your-r2-access-key
R2_SECRET_ACCESS_KEY=your-r2-secret
R2_BUCKET_NAME=shouko-pdfs
R2_PUBLIC_URL=https://pdfs.yourdomain.com

STRIPE_SECRET_KEY=sk_test_your-test-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
STRIPE_PRO_MONTHLY_PRICE_ID=price_xxx
STRIPE_PRO_YEARLY_PRICE_ID=price_xxx
STRIPE_TEAM_MONTHLY_PRICE_ID=price_xxx

RESEND_API_KEY=re_your-key
FROM_EMAIL=hello@yourdomain.com

# Optional
SENTRY_DSN=
LOGFIRE_TOKEN=
```

---

## Security Notes

1. **Never** put `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in frontend env vars
2. **Never** put `SUPABASE_SERVICE_ROLE_KEY` in frontend — only `SUPABASE_ANON_KEY`
3. **Never** put `STRIPE_SECRET_KEY` in frontend — only `STRIPE_PUBLISHABLE_KEY`
4. Use `sk_test_` Stripe keys in development, `sk_live_` only in production
5. Rotate `APP_SECRET_KEY` if ever exposed — invalidates all existing sessions
6. Add `.env` and `.env.local` to `.gitignore` (should already be there)
