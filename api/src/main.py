from __future__ import annotations

import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.generated.apis.default_api import router as generated_router
from api.generated.models.error_response import ErrorResponse
from api.impl.default_api_impl import DefaultApiImpl  # noqa: F401
from control.exception.business_exception import BusinessException
from control.exception.experiment_not_found_exception import (
    ExperimentNotFoundException,
)
from control.exception.experiment_state_conflict_exception import (
    ExperimentStateConflictException,
)
from control.exception.experiment_run_not_found_exception import (
    ExperimentRunNotFoundException,
)
from control.exception.experiment_run_state_conflict_exception import (
    ExperimentRunStateConflictException,
)
from control.exception.probe_not_found_exception import ProbeNotFoundException
from control.exception.temperature_not_found_exception import (
    TemperatureNotFoundException,
)
from dao.exception.db_exception import DBException
from control.probe_control import ProbeControl
from dao.manager.postgresql_manager_impl import PostgreSQLManagerImpl

app = FastAPI(title="Temperature Log API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:4173",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:4173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(generated_router)


@app.on_event("startup")
async def bootstrap_probe_registry() -> None:
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/postgres",
    )
    connection_manager = PostgreSQLManagerImpl(database_url)
    ProbeControl(connection_manager).initialize_registry()


@app.get("/health")
def health_check() -> dict[str, str]:
    """Returns a simple health response."""

    return {"status": "ok"}


@app.exception_handler(BusinessException)
async def business_exception_handler(
    request: Request,
    exc: BusinessException,
) -> JSONResponse:
    """Maps business errors to HTTP 400 responses."""

    return JSONResponse(
        status_code=400,
        content=ErrorResponse(message=str(exc)).model_dump(by_alias=True),
    )


@app.exception_handler(TemperatureNotFoundException)
async def temperature_not_found_exception_handler(
    request: Request,
    exc: TemperatureNotFoundException,
) -> JSONResponse:
    """Maps missing temperature errors to HTTP 404 responses."""

    return JSONResponse(
        status_code=404,
        content=ErrorResponse(message=str(exc)).model_dump(by_alias=True),
    )


@app.exception_handler(ExperimentNotFoundException)
async def experiment_not_found_exception_handler(
    request: Request,
    exc: ExperimentNotFoundException,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(message=str(exc)).model_dump(by_alias=True),
    )


@app.exception_handler(ExperimentStateConflictException)
async def experiment_state_conflict_exception_handler(
    request: Request,
    exc: ExperimentStateConflictException,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content=ErrorResponse(message=str(exc)).model_dump(by_alias=True),
    )


@app.exception_handler(ExperimentRunNotFoundException)
async def experiment_run_not_found_exception_handler(
    request: Request,
    exc: ExperimentRunNotFoundException,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(message=str(exc)).model_dump(by_alias=True),
    )


@app.exception_handler(ExperimentRunStateConflictException)
async def experiment_run_state_conflict_exception_handler(
    request: Request,
    exc: ExperimentRunStateConflictException,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content=ErrorResponse(message=str(exc)).model_dump(by_alias=True),
    )


@app.exception_handler(ProbeNotFoundException)
async def probe_not_found_exception_handler(
    request: Request,
    exc: ProbeNotFoundException,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(message=str(exc)).model_dump(by_alias=True),
    )


@app.exception_handler(DBException)
async def db_exception_handler(
    request: Request,
    exc: DBException,
) -> JSONResponse:
    """Maps data layer errors to HTTP 500 responses."""

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(message=str(exc)).model_dump(by_alias=True),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Maps unexpected errors to HTTP 500 responses."""

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(message="internal server error").model_dump(by_alias=True),
    )
