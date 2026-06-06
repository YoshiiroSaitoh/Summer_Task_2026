from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.dao.model.temperature_log import metadata
from src.dao.repository.temperature_log_repository import TemperatureLogRepository


def test_insert_and_latest_lookup() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    metadata.create_all(engine)
    repository = TemperatureLogRepository()

    with Session(engine) as session:
        first = repository.insert(
            session,
            probe_id="probe-a",
            recorded_at=datetime(2026, 6, 7, 9, 0, tzinfo=timezone.utc),
            temperature=23.5,
        )
        repository.insert(
            session,
            probe_id="probe-a",
            recorded_at=datetime(2026, 6, 7, 10, 0, tzinfo=timezone.utc),
            temperature=24.25,
        )

        latest = repository.find_latest_by_probe_id(session, "probe-a")

    assert first.id is not None
    assert latest is not None
    assert latest.temperature == 24.25
