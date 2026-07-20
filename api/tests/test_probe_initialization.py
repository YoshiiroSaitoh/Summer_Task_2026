from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import Session

from control.probe_control import ProbeControl
from dao.model.temperature_log import metadata as temperature_metadata


class SQLiteConnectionManager:
    def __init__(self, engine) -> None:
        self._engine = engine

    @contextmanager
    def get_session(self):
        with Session(self._engine) as session:
            yield session


def test_initialize_registry_creates_probe_table_and_backfills_ids() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    temperature_metadata.create_all(engine)

    with Session(engine) as session:
        session.execute(
            temperature_metadata.tables["temperature_logs"].insert(),
            [
                {
                    "probe_id": "probe-a",
                    "recorded_at": datetime(2026, 7, 20, 0, 0, tzinfo=timezone.utc),
                    "temperature": 23.5,
                },
                {
                    "probe_id": "probe-b",
                    "recorded_at": datetime(2026, 7, 20, 0, 1, tzinfo=timezone.utc),
                    "temperature": 24.5,
                },
            ],
        )
        session.commit()

    control = ProbeControl(SQLiteConnectionManager(engine))
    control.initialize_registry()

    with Session(engine) as session:
        rows = session.execute(text("SELECT probe_id FROM probes ORDER BY probe_id")).all()

    assert [row[0] for row in rows] == ["probe-a", "probe-b"]
