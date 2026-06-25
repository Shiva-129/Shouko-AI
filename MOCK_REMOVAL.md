# Mock Removal Report

All mock, fallback, and sentinel patterns removed from the project. Every service and auth path now uses real credentials only.

## Backend (apps/api)

### `core/dependencies.py`
- **Removed** entire `MockUser` class (hardcoded fake user with id `00000000-...`, email `mock@shouko-ai.app`, plan `free`, pre-set interest profile)

### `core/security.py`
- **Removed** `from core.dependencies import MockUser` import
- **Removed** 3 MockUser fallback paths in `get_current_user()`:
  1. `ENVIRONMENT == "development"` → `MockUser()` when no auth header
  2. `token == "mock-token"` → `MockUser()` explicit dev bypass
  3. `JWT validation failed` → `MockUser()` dev fallback
- `get_current_user()` return type changed from `User | MockUser` to `User`
- Auth now always validates real Supabase RS256 JWTs, no bypasses

### `core/rate_limit.py`
- **Removed** `from core.dependencies import MockUser` import
- Type annotation changed from `User | MockUser` to `User`

### `core/config.py`
- Stripe defaults changed: `"mock-stripe-key"` → `""`, `"mock-webhook-secret"` → `""`, `"price_mockpropriceid"` → `""`

### `services/llm_service.py`
- **Removed** `!= "mock-key-for-now"` sentinel check on `OPENROUTER_API_KEY`; now only checks truthy

### `services/embedding_service.py`
- **Removed** `!= "mock-key-for-now"` sentinel check on `OPENROUTER_API_KEY`; now only checks truthy

### `services/email_service.py`
- **Removed** `!= "mock-key-for-now"` sentinel checks in both `send_digest()` and `send_welcome_email()`; now only checks `not self.api_key`

### `.env`
- `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`: `mock-key-for-now` → empty
- `STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRO_PRICE_ID`: mock values → empty
- `OPENROUTER_API_KEY` and `GROQ_API_KEY` kept (they were real keys)

## Tests (apps/api/tests)

### `conftest.py`
- **Added** `auth_user` autouse fixture — mocks `verify_supabase_jwt` to return a signed payload for the seeded test user (no more mock-token bypass needed)
- **Added** `auth_headers` fixture returning `{"Authorization": "Bearer real-test-token"}`
- Test user email changed from `mock@shouko-ai.app` → `test@shouko-ai.app`
- Extracted `TEST_USER_ID` and `TEST_USER_EMAIL` constants

### All test files (`test_auth.py`, `test_papers.py`, `test_chat.py`, `test_artifacts.py`, `test_annotations.py`, `test_collections.py`)
- All `headers = {"Authorization": "Bearer mock-token"}` replaced with `auth_headers` fixture parameter
- `unittest.mock.patch` usage (for external services) kept — those are legitimate test stubs, not mock auth fallbacks

## Frontend (apps/web)

### `lib/api.ts`
- `getAuthHeaders()`: **removed** fallback `return { Authorization: "Bearer mock-token" }` when no Supabase session; now returns empty object

### `lib/hooks/useSSEChat.ts`
- `getAuthHeaders()`: same fix — removed `Bearer mock-token` fallback

### `types/index.ts`
- **Removed** `mockQueries: string[]` field from `Paper` interface
- **Removed** `mockQAs: { question: string; answer: string }[]` field from `Paper` interface

## CI (.github/workflows/ci.yml)
- **Removed** mock env vars: `JWT_SECRET`, `SUPABASE_KEY`, `OPENAI_API_KEY`, `STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET`

## Verification
- All 14 modified Python files parse without syntax errors
- Zero imports of `MockUser` anywhere in the codebase
- Zero references to `mock-token` in source code (only `unittest.mock.patch` in tests remains, which is correct)
- TypeScript typecheck (`tsc --noEmit`) passes cleanly
- Frontend has zero `mock` references
