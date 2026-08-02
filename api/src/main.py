from __future__ import annotations

import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

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
from control.experiment_run_control import ExperimentRunControl
from control.experiment_run_probe_control import ExperimentRunProbeControl
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
        "http://[::1]:3000",
        "http://[::1]:4173",
        "http://[::1]:5173",
        "http://experiment.local:3000",
        "http://experiment.local:4173",
        "http://experiment.local:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(generated_router)


class ExperimentRunProbeCreateRequest(BaseModel):
    probe_id: str
    role: str


def _connection_manager() -> PostgreSQLManagerImpl:
    return PostgreSQLManagerImpl(
        os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://postgres:postgres@localhost:5432/postgres",
        )
    )


def _serialize_run_probe(assignment) -> dict[str, object]:
    return {
        "id": assignment.id,
        "experiment_run_id": assignment.experiment_run_id,
        "probe_id": assignment.probe_id,
        "role": assignment.role,
        "created_at": assignment.created_at,
        "updated_at": assignment.updated_at,
    }


def _serialize_run(run) -> dict[str, object]:
    return {
        "id": run.id,
        "experiment_id": run.experiment_id,
        "label": run.label,
        "started_at": run.started_at,
        "ended_at": run.ended_at,
        "created_at": run.created_at,
        "updated_at": run.updated_at,
    }


@app.post("/experiments/{experiment_id}/runs/{run_id}/start")
def start_experiment_run(experiment_id: int, run_id: int) -> dict[str, object]:
    control = ExperimentRunControl(_connection_manager())
    return _serialize_run(control.start_experiment_run(experiment_id, run_id))


@app.get("/experiments/{experiment_id}/runs/{run_id}/probes")
def list_experiment_run_probes(experiment_id: int, run_id: int) -> list[dict[str, object]]:
    control = ExperimentRunProbeControl(_connection_manager())
    return [_serialize_run_probe(item) for item in control.list_assignments(experiment_id, run_id)]


@app.post("/experiments/{experiment_id}/runs/{run_id}/probes", status_code=201)
def add_experiment_run_probe(
    experiment_id: int,
    run_id: int,
    payload: ExperimentRunProbeCreateRequest,
) -> dict[str, object]:
    control = ExperimentRunProbeControl(_connection_manager())
    return _serialize_run_probe(
        control.add_assignment(experiment_id, run_id, payload.probe_id, payload.role)
    )


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
