"""FastAPI application entry point for the WellNow HRIS Simulated API.

Configures CORS, authentication middleware, structured logging,
global exception handling, and mounts all API routers.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import Response

from src.api.auth import APIKeyMiddleware
from src.api.config import settings
from src.api.routers import (
    health,
    locations,
    patient_volume,
    schedules,
    terminations,
    workers,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger("hris_api")


def _configure_logging() -> None:
    """Set up structured JSON logging based on config."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    if settings.log_format == "json":
        fmt = (
            '{"time":"%(asctime)s","level":"%(levelname)s",'
            '"logger":"%(name)s","message":"%(message)s"}'
        )
    else:
        fmt = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"

    logging.basicConfig(level=log_level, format=fmt, force=True)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown hooks."""
    _configure_logging()
    logger.info(
        "Starting %s v%s on port %d",
        settings.api_title,
        settings.api_version,
        settings.hris_api_port,
    )
    yield
    logger.info("Shutting down %s", settings.api_title)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API key auth (must be added after CORS so CORS preflight isn't blocked)
app.add_middleware(APIKeyMiddleware)


# ---------------------------------------------------------------------------
# Request/response logging middleware
# ---------------------------------------------------------------------------


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
    """Log every request with method, path, status, and duration."""
    start = time.perf_counter()
    response: Response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    logger.info(
        "%s %s -> %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch unhandled exceptions and return a structured error response."""
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal Server Error",
                "details": "An unexpected error occurred. Please try again later.",
            }
        },
    )


# ---------------------------------------------------------------------------
# Register routers
# ---------------------------------------------------------------------------

app.include_router(health.router)
app.include_router(workers.router)
app.include_router(schedules.router)
app.include_router(patient_volume.router)
app.include_router(locations.router)
app.include_router(terminations.router)
