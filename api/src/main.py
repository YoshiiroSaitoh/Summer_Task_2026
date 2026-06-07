from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.generated.apis.default_api import router as generated_router
from api.generated.models.error_response import ErrorResponse
from api.impl.default_api_impl import DefaultApiImpl  # noqa: F401
from control.exception.business_exception import BusinessException
from control.exception.temperature_not_found_exception import (
    TemperatureNotFoundException,
)
from dao.exception.db_exception import DBException

app = FastAPI(title="Temperature Log API", version="0.1.0")
app.include_router(generated_router)


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
