from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import control.temperature_control as temperature_control_module
from control.temperature_control import TemperatureControl
from dao.model.temperature_log import metadata


class SQLiteConnectionManager:
    def __init__(self, engine) -> None:
        self._engine = engine

    @contextmanager
    def get_session(self):
        with Session(self._engine) as session:
            yield session


def test_register_temperature_uses_current_time_when_missing_recorded_at() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    metadata.create_all(engine)
    control = TemperatureControl(SQLiteConnectionManager(engine))
    fixed_now = datetime(2026, 6, 8, 12, 34, 56, tzinfo=timezone.utc)

    class FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):  # noqa: ANN001
            return fixed_now

    original_datetime = temperature_control_module.datetime
    temperature_control_module.datetime = FixedDatetime
    try:
        temperature_log = control.register_temperature(
            probe_id="probe-a",
            recorded_at=None,
            temperature=23.5,
        )
    finally:
        temperature_control_module.datetime = original_datetime

    assert temperature_log.recorded_at == fixed_now
