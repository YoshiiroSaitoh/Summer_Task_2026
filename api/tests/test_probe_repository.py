from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from dao.model.probe import metadata
from dao.repository.probe_repository import ProbeRepository


def normalize_to_utc(datetime_value: datetime) -> datetime:
    if datetime_value.tzinfo is None or datetime_value.tzinfo.utcoffset(datetime_value) is None:
        return datetime_value.replace(tzinfo=timezone.utc)
    return datetime_value.astimezone(timezone.utc)


def test_upsert_list_and_soft_delete_probe() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    metadata.create_all(engine)
    repository = ProbeRepository()
    observed_at = datetime(2026, 6, 8, 12, 0, tzinfo=timezone.utc)

    with Session(engine) as session:
        repository.upsert_observed_probe(session, "probe-a", observed_at)
        repository.upsert_observed_probe(session, "probe-b", observed_at)
        probes = repository.list_active(session)
        deleted = repository.delete_by_probe_id(session, "probe-a", observed_at)

    assert [probe.probe_id for probe in probes] == ["probe-b", "probe-a"]
    assert deleted is not None
    assert normalize_to_utc(deleted.deleted_at) == observed_at
