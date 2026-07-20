from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from control.probe_control import ProbeControl
from dao.model.probe import metadata


class SQLiteConnectionManager:
    def __init__(self, engine) -> None:
        self._engine = engine

    @contextmanager
    def get_session(self):
        with Session(self._engine) as session:
            yield session


def test_delete_probe_marks_entry_as_deleted() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    metadata.create_all(engine)
    control = ProbeControl(SQLiteConnectionManager(engine))
    observed_at = datetime(2026, 6, 8, 12, 0, tzinfo=timezone.utc)

    control.ensure_probe("probe-a", observed_at)
    deleted = control.delete_probe("probe-a")

    assert deleted.probe_id == "probe-a"
    assert deleted.deleted_at is not None
    assert control.list_probes() == []
