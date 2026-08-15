import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import install_exception_handlers
from app.core.logging import configure_logging
from app.db.session import get_engine
from app.services.embedding_service import get_embedding_service
from app.services.reranking_service import get_reranking_service

configure_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Pre-warm DB engine and ML models to eliminate first-request cold-start
    get_engine()
    get_embedding_service()._load_model()
    get_reranking_service()._load_model()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next) -> Response:
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time_ms = (time.perf_counter() - start_time) * 1000.0
    response.headers["X-Process-Time"] = f"{process_time_ms:.2f}ms"
    response.headers["Server-Timing"] = f"total;dur={process_time_ms:.2f}"
    return response
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
install_exception_handlers(app)
app.include_router(api_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "OpenResearch Graph API", "docs": "/docs"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "environment": settings.environment}
