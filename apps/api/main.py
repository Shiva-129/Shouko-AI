from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from core.config import settings
from core.exceptions import (
    PaperBrainException,
    paperbrain_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from core.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="PaperBrain API",
    description="Multi-agent AI research intelligence system backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration
origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Exception Handlers
app.add_exception_handler(PaperBrainException, paperbrain_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include Routers
from routers import papers, chat, users, digests, artifacts, billing, collections
app.include_router(papers.router)
app.include_router(chat.router)
app.include_router(users.router)
app.include_router(digests.router)
app.include_router(artifacts.router)
app.include_router(billing.router)
app.include_router(collections.router)


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "api_version": "1.0.0",
    }
