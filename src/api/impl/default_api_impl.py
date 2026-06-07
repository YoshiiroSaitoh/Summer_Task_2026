from __future__ import annotations

import os
from datetime import datetime

from api.generated.apis.default_api_base import BaseDefaultApi
from api.generated.models.temperature_create_request import TemperatureCreateRequest
from api.generated.models.temperature_log import TemperatureLog as GeneratedTemperatureLog
from api.impl.base_api_impl import BaseApiImpl
from control.temperature_control import TemperatureControl
from dao.manager.postgresql_manager_impl import PostgreSQLManagerImpl


class DefaultApiImpl(BaseApiImpl, BaseDefaultApi):
    """Default API implementation backed by the control layer."""

    def __init__(self) -> None:
        super().__init__()
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://postgres:postgres@localhost:5432/postgres",
        )
        self._control = TemperatureControl(PostgreSQLManagerImpl(database_url))

    async def list_temperature_logs(
        self,
        probe_id: str | None,
        start_at: datetime | None,
        end_at: datetime | None,
    ) -> list[GeneratedTemperatureLog]:
        """Lists temperature logs for the generated API."""
        self.log_request("GET", "/temperatures")
        logs = self._control.list_temperature_logs(probe_id, start_at, end_at)
        self.log_response(200)
        return [self._to_generated_temperature_log(log) for log in logs]

    async def create_temperature_log(
        self,
        temperature_create_request: TemperatureCreateRequest,
    ) -> GeneratedTemperatureLog:
        """Creates a temperature log for the generated API."""
        self.log_request("POST", "/temperatures")
        temperature_log = self._control.register_temperature(
            temperature_create_request.probe_id,
            temperature_create_request.recorded_at,
            float(temperature_create_request.temperature),
        )
        self.log_response(201)
        return self._to_generated_temperature_log(temperature_log)

    async def get_latest_temperature_log(
        self,
        probe_id: str,
    ) -> GeneratedTemperatureLog:
        """Returns the latest temperature log for the generated API."""
        self.log_request("GET", f"/temperatures/latest/{probe_id}")
        temperature_log = self._control.get_latest_temperature(probe_id)
        self.log_response(200)
        return self._to_generated_temperature_log(temperature_log)

    def _to_generated_temperature_log(
        self,
        temperature_log,
    ) -> GeneratedTemperatureLog:
        return GeneratedTemperatureLog(
            id=temperature_log.id,
            probe_id=temperature_log.probe_id,
            recorded_at=temperature_log.recorded_at,
            temperature=float(temperature_log.temperature),
        )
