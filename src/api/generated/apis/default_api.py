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
from pydantic import StrictStr
from typing import List, Optional
from api.generated.models.error_response import ErrorResponse
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
