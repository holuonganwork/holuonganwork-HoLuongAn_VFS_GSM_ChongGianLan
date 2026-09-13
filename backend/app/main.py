from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.services.cases import InvalidTransitionError, NotFoundError


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging(get_settings().log_level)
    yield


app = FastAPI(
    title="Driver Fraud Investigation System",
    description="Signals, correlated alerts, decision policy and exception review. Local API.",
    version="0.2.0",
    lifespan=lifespan,
)
app.include_router(router)


@app.exception_handler(NotFoundError)
async def not_found(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(InvalidTransitionError)
async def invalid_transition(request: Request, exc: InvalidTransitionError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})
