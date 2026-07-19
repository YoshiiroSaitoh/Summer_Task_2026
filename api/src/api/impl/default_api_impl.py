from __future__ import annotations

import os
from datetime import datetime

from api.generated.apis.default_api_base import BaseDefaultApi
from api.generated.models.experiment import Experiment as GeneratedExperiment
from api.generated.models.experiment_create_request import ExperimentCreateRequest
from api.generated.models.experiment_probe import ExperimentProbe as GeneratedExperimentProbe
from api.generated.models.experiment_probe_create_request import (
    ExperimentProbeCreateRequest,
)
from api.generated.models.temperature_create_request import TemperatureCreateRequest
from api.generated.models.temperature_log import TemperatureLog as GeneratedTemperatureLog
from api.impl.base_api_impl import BaseApiImpl
from control.experiment_control import ExperimentControl
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
        connection_manager = PostgreSQLManagerImpl(database_url)
        self._experiment_control = ExperimentControl(connection_manager)
        self._control = TemperatureControl(connection_manager)

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

    async def create_temperature_logs(
        self,
        temperature_create_request: list[TemperatureCreateRequest],
    ) -> list[GeneratedTemperatureLog]:
        """Creates multiple temperature logs for the generated API."""
        self.log_request("POST", "/temperatures/bulk")
        temperature_logs = self._control.register_temperatures(
            [
                (
                    request.probe_id,
                    request.recorded_at,
                    float(request.temperature),
                )
                for request in temperature_create_request
            ]
        )
        self.log_response(201)
        return [self._to_generated_temperature_log(temperature_log) for temperature_log in temperature_logs]

    async def get_latest_temperature_log(
        self,
        probe_id: str,
    ) -> GeneratedTemperatureLog:
        """Returns the latest temperature log for the generated API."""
        self.log_request("GET", f"/temperatures/latest/{probe_id}")
        temperature_log = self._control.get_latest_temperature(probe_id)
        self.log_response(200)
        return self._to_generated_temperature_log(temperature_log)

    async def list_experiments(self) -> list[GeneratedExperiment]:
        self.log_request("GET", "/experiments")
        experiments = self._experiment_control.list_experiments()
        self.log_response(200)
        return [self._to_generated_experiment(experiment) for experiment in experiments]

    async def create_experiment(
        self,
        experiment_create_request: ExperimentCreateRequest,
    ) -> GeneratedExperiment:
        self.log_request("POST", "/experiments")
        experiment = self._experiment_control.create_experiment(experiment_create_request.name)
        self.log_response(201)
        return self._to_generated_experiment(experiment)

    async def get_current_experiment(self) -> GeneratedExperiment:
        self.log_request("GET", "/experiments/current")
        experiment = self._experiment_control.get_current_experiment()
        self.log_response(200)
        return self._to_generated_experiment(experiment)

    async def get_experiment(self, experiment_id: int) -> GeneratedExperiment:
        self.log_request("GET", f"/experiments/{experiment_id}")
        experiment = self._experiment_control.get_experiment(experiment_id)
        self.log_response(200)
        return self._to_generated_experiment(experiment)

    async def start_experiment(self, experiment_id: int) -> GeneratedExperiment:
        self.log_request("POST", f"/experiments/{experiment_id}/start")
        experiment = self._experiment_control.start_experiment(experiment_id)
        self.log_response(200)
        return self._to_generated_experiment(experiment)

    async def end_experiment(self, experiment_id: int) -> GeneratedExperiment:
        self.log_request("POST", f"/experiments/{experiment_id}/end")
        experiment = self._experiment_control.end_experiment(experiment_id)
        self.log_response(200)
        return self._to_generated_experiment(experiment)

    async def list_experiment_probes(self, experiment_id: int) -> list[GeneratedExperimentProbe]:
        self.log_request("GET", f"/experiments/{experiment_id}/probes")
        experiment_probes = self._experiment_control.list_experiment_probes(experiment_id)
        self.log_response(200)
        return [self._to_generated_experiment_probe(experiment_probe) for experiment_probe in experiment_probes]

    async def add_experiment_probe(
        self,
        experiment_id: int,
        experiment_probe_create_request: ExperimentProbeCreateRequest,
    ) -> GeneratedExperimentProbe:
        self.log_request("POST", f"/experiments/{experiment_id}/probes")
        experiment_probe = self._experiment_control.add_experiment_probe(
            experiment_id,
            experiment_probe_create_request.probe_id,
            experiment_probe_create_request.role,
            experiment_probe_create_request.valid_from,
            experiment_probe_create_request.valid_to,
        )
        self.log_response(201)
        return self._to_generated_experiment_probe(experiment_probe)

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

    def _to_generated_experiment(self, experiment) -> GeneratedExperiment:
        return GeneratedExperiment(
            id=experiment.id,
            name=experiment.name,
            status=experiment.status,
            started_at=experiment.started_at,
            ended_at=experiment.ended_at,
            created_at=experiment.created_at,
            updated_at=experiment.updated_at,
        )

    def _to_generated_experiment_probe(self, experiment_probe) -> GeneratedExperimentProbe:
        return GeneratedExperimentProbe(
            id=experiment_probe.id,
            experiment_id=experiment_probe.experiment_id,
            probe_id=experiment_probe.probe_id,
            role=experiment_probe.role,
            valid_from=experiment_probe.valid_from,
            valid_to=experiment_probe.valid_to,
            created_at=experiment_probe.created_at,
            updated_at=experiment_probe.updated_at,
        )
