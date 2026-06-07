# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from datetime import datetime
from pydantic import StrictStr
from typing import List, Optional
from api.generated.models.error_response import ErrorResponse
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


    async def get_latest_temperature_log(
        self,
        probe_id: StrictStr,
    ) -> TemperatureLog:
        ...
