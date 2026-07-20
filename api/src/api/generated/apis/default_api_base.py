# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from datetime import datetime
from pydantic import StrictInt, StrictStr
from typing import List, Optional
from api.generated.models.error_response import ErrorResponse
from api.generated.models.experiment import Experiment
from api.generated.models.experiment_create_request import ExperimentCreateRequest
from api.generated.models.experiment_probe import ExperimentProbe
from api.generated.models.experiment_probe_create_request import ExperimentProbeCreateRequest
from api.generated.models.experiment_run import ExperimentRun
from api.generated.models.experiment_run_create_request import ExperimentRunCreateRequest
from api.generated.models.probe import Probe
from api.generated.models.temperature_create_request import TemperatureCreateRequest
from api.generated.models.temperature_log import TemperatureLog


class BaseDefaultApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseDefaultApi.subclasses = BaseDefaultApi.subclasses + (cls,)
    async def list_temperature_logs(
        self,
        probe_id: Optional[StrictStr],
        start_at: Optional[datetime],
        end_at: Optional[datetime],
    ) -> List[TemperatureLog]:
        ...


    async def create_temperature_log(
        self,
        temperature_create_request: TemperatureCreateRequest,
    ) -> TemperatureLog:
        ...


    async def create_temperature_logs(
        self,
        temperature_create_request: List[TemperatureCreateRequest],
    ) -> List[TemperatureLog]:
        ...


    async def get_latest_temperature_log(
        self,
        probe_id: StrictStr,
    ) -> TemperatureLog:
        ...


    async def list_probes(
        self,
    ) -> List[Probe]:
        ...


    async def delete_probe(
        self,
        probe_id: StrictStr,
    ) -> None:
        ...


    async def list_experiments(
        self,
    ) -> List[Experiment]:
        ...


    async def create_experiment(
        self,
        experiment_create_request: ExperimentCreateRequest,
    ) -> Experiment:
        ...


    async def get_current_experiment(
        self,
    ) -> Experiment:
        ...


    async def get_experiment(
        self,
        experiment_id: StrictInt,
    ) -> Experiment:
        ...


    async def start_experiment(
        self,
        experiment_id: StrictInt,
    ) -> Experiment:
        ...


    async def end_experiment(
        self,
        experiment_id: StrictInt,
    ) -> Experiment:
        ...


    async def list_experiment_probes(
        self,
        experiment_id: StrictInt,
    ) -> List[ExperimentProbe]:
        ...


    async def add_experiment_probe(
        self,
        experiment_id: StrictInt,
        experiment_probe_create_request: ExperimentProbeCreateRequest,
    ) -> ExperimentProbe:
        ...


    async def list_experiment_runs(
        self,
        experiment_id: StrictInt,
    ) -> List[ExperimentRun]:
        ...


    async def create_experiment_run(
        self,
        experiment_id: StrictInt,
        experiment_run_create_request: ExperimentRunCreateRequest,
    ) -> ExperimentRun:
        ...


    async def get_current_experiment_run(
        self,
        experiment_id: StrictInt,
    ) -> ExperimentRun:
        ...


    async def end_experiment_run(
        self,
        experiment_id: StrictInt,
        run_id: StrictInt,
    ) -> ExperimentRun:
        ...
