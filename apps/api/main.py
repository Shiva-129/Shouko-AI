from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from core.config import settings
from core.exceptions import (
    ShoukoAIException,
    shouko_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from core.scheduler import start_scheduler, stop_scheduler
from services.storage_service import storage_service
import os
import sentry_sdk
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

if os.getenv("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Supabase Storage bucket (production only)
    await storage_service.ensure_bucket()
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Shouko-AI API",
    description="Multi-agent AI research intelligence system backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration
origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]
print(f"[CORS] Allowed Origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def debug_cors_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        origin = request.headers.get("origin")
        print(f"[CORS Debug] OPTIONS request to {request.url.path} | Origin header: '{origin}' | Match: {origin in origins}")
    return await call_next(request)

# Register Exception Handlers
app.add_exception_handler(ShoukoAIException, shouko_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include Routers
from routers import papers, chat, users, digests, artifacts, billing, collections, annotations
app.include_router(papers.router)
app.include_router(chat.router)
app.include_router(users.router)
app.include_router(digests.router)
app.include_router(artifacts.router)
app.include_router(billing.router)
app.include_router(collections.router)
app.include_router(annotations.router)


@app.get("/health", tags=["System"])
async def health_check():
    db_ok = False
    try:
        from core.database import engine
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        db_ok = False
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
        "environment": settings.ENVIRONMENT,
        "api_version": "1.0.0",
    }
