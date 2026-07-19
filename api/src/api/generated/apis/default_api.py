# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from api.generated.apis.default_api_base import BaseDefaultApi
import api.generated.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from api.generated.models.extra_models import TokenModel  # noqa: F401
from datetime import datetime
from pydantic import StrictInt, StrictStr
from typing import List, Optional
from api.generated.models.error_response import ErrorResponse
from api.generated.models.experiment import Experiment
from api.generated.models.experiment_create_request import ExperimentCreateRequest
from api.generated.models.experiment_probe import ExperimentProbe
from api.generated.models.experiment_probe_create_request import ExperimentProbeCreateRequest
from api.generated.models.temperature_create_request import TemperatureCreateRequest
from api.generated.models.temperature_log import TemperatureLog


router = APIRouter()

ns_pkg = api.generated.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/temperatures",
    responses={
        200: {"model": List[TemperatureLog], "description": "OK"},
    },
    tags=["default"],
    summary="Search temperature readings",
    response_model_by_alias=True,
)
async def list_temperature_logs(
    probe_id: Optional[StrictStr] = Query(None, description="", alias="probe_id"),
    start_at: Optional[datetime] = Query(None, description="", alias="start_at"),
    end_at: Optional[datetime] = Query(None, description="", alias="end_at"),
) -> List[TemperatureLog]:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().list_temperature_logs(probe_id, start_at, end_at)


@router.post(
    "/temperatures",
    responses={
        201: {"model": TemperatureLog, "description": "Created"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
    },
    tags=["default"],
    summary="Register a temperature reading",
    response_model_by_alias=True,
)
async def create_temperature_log(
    temperature_create_request: TemperatureCreateRequest = Body(None, description=""),
) -> TemperatureLog:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().create_temperature_log(temperature_create_request)


@router.post(
    "/temperatures/bulk",
    responses={
        201: {"model": List[TemperatureLog], "description": "Created"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
    },
    tags=["default"],
    summary="Register multiple temperature readings",
    response_model_by_alias=True,
)
async def create_temperature_logs(
    temperature_create_request: List[TemperatureCreateRequest] = Body(None, description=""),
) -> List[TemperatureLog]:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().create_temperature_logs(temperature_create_request)


@router.get(
    "/temperatures/latest/{probe_id}",
    responses={
        200: {"model": TemperatureLog, "description": "OK"},
        404: {"model": ErrorResponse, "description": "Not found"},
    },
    tags=["default"],
    summary="Get the latest temperature reading",
    response_model_by_alias=True,
)
async def get_latest_temperature_log(
    probe_id: StrictStr = Path(..., description=""),
) -> TemperatureLog:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().get_latest_temperature_log(probe_id)


@router.get(
    "/experiments",
    responses={
        200: {"model": List[Experiment], "description": "OK"},
    },
    tags=["default"],
    summary="List experiments",
    response_model_by_alias=True,
)
async def list_experiments(
) -> List[Experiment]:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().list_experiments()


@router.post(
    "/experiments",
    responses={
        201: {"model": Experiment, "description": "Created"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
    },
    tags=["default"],
    summary="Create a new experiment",
    response_model_by_alias=True,
)
async def create_experiment(
    experiment_create_request: ExperimentCreateRequest = Body(None, description=""),
) -> Experiment:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().create_experiment(experiment_create_request)


@router.get(
    "/experiments/current",
    responses={
        200: {"model": Experiment, "description": "OK"},
        404: {"model": ErrorResponse, "description": "Not found"},
    },
    tags=["default"],
    summary="Get the current experiment",
    response_model_by_alias=True,
)
async def get_current_experiment(
) -> Experiment:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().get_current_experiment()


@router.get(
    "/experiments/{experiment_id}",
    responses={
        200: {"model": Experiment, "description": "OK"},
        404: {"model": ErrorResponse, "description": "Not found"},
    },
    tags=["default"],
    summary="Get an experiment",
    response_model_by_alias=True,
)
async def get_experiment(
    experiment_id: StrictInt = Path(..., description=""),
) -> Experiment:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().get_experiment(experiment_id)


@router.post(
    "/experiments/{experiment_id}/start",
    responses={
        200: {"model": Experiment, "description": "OK"},
        404: {"model": ErrorResponse, "description": "Not found"},
        409: {"model": ErrorResponse, "description": "Invalid state"},
    },
    tags=["default"],
    summary="Start an experiment",
    response_model_by_alias=True,
)
async def start_experiment(
    experiment_id: StrictInt = Path(..., description=""),
) -> Experiment:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().start_experiment(experiment_id)


@router.post(
    "/experiments/{experiment_id}/end",
    responses={
        200: {"model": Experiment, "description": "OK"},
        404: {"model": ErrorResponse, "description": "Not found"},
        409: {"model": ErrorResponse, "description": "Invalid state"},
    },
    tags=["default"],
    summary="End an experiment",
    response_model_by_alias=True,
)
async def end_experiment(
    experiment_id: StrictInt = Path(..., description=""),
) -> Experiment:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().end_experiment(experiment_id)


@router.get(
    "/experiments/{experiment_id}/probes",
    responses={
        200: {"model": List[ExperimentProbe], "description": "OK"},
        404: {"model": ErrorResponse, "description": "Not found"},
    },
    tags=["default"],
    summary="List probes assigned to an experiment",
    response_model_by_alias=True,
)
async def list_experiment_probes(
    experiment_id: StrictInt = Path(..., description=""),
) -> List[ExperimentProbe]:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().list_experiment_probes(experiment_id)


@router.post(
    "/experiments/{experiment_id}/probes",
    responses={
        201: {"model": ExperimentProbe, "description": "Created"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        404: {"model": ErrorResponse, "description": "Not found"},
        409: {"model": ErrorResponse, "description": "Conflict"},
    },
    tags=["default"],
    summary="Assign a probe to an experiment",
    response_model_by_alias=True,
)
async def add_experiment_probe(
    experiment_id: StrictInt = Path(..., description=""),
    experiment_probe_create_request: ExperimentProbeCreateRequest = Body(None, description=""),
) -> ExperimentProbe:
    if not BaseDefaultApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDefaultApi.subclasses[0]().add_experiment_probe(experiment_id, experiment_probe_create_request)
