from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.exc import OperationalError

from control.exception.probe_not_found_exception import ProbeNotFoundException
from dao.manager.db_connection_manager import DBConnectionManager
from dao.model.probe import metadata as probe_metadata
from dao.model.probe import Probe
from dao.repository.temperature_log_repository import TemperatureLogRepository
from dao.repository.probe_repository import ProbeRepository


class ProbeControl:
    """Coordinates probe registry access."""

    def __init__(self, connection_manager: DBConnectionManager) -> None:
        self._connection_manager = connection_manager
        self._repository = ProbeRepository()
        self._temperature_log_repository = TemperatureLogRepository()

    def initialize_registry(self) -> None:
        with self._connection_manager.get_session() as session:
            probe_metadata.create_all(session.get_bind())
            observed_probe_ids = self._temperature_log_repository.list_distinct_probe_ids(session)
            observed_at = datetime.now(timezone.utc)
            for probe_id in observed_probe_ids:
                self._repository.upsert_observed_probe(session, probe_id, observed_at)
            session.commit()

    def ensure_probe(self, probe_id: str, observed_at: datetime) -> Probe | None:
        with self._connection_manager.get_session() as session:
            try:
                probe = self._repository.upsert_observed_probe(session, probe_id, observed_at)
                session.commit()
                return probe
            except OperationalError as exc:
                session.rollback()
                raise
            except Exception:
                session.rollback()
                raise

    def list_probes(self) -> list[Probe]:
        with self._connection_manager.get_session() as session:
            try:
                return list(self._repository.list_active(session))
            except OperationalError as exc:
                if "probes" in str(exc):
                    return []
                raise

    def delete_probe(self, probe_id: str) -> Probe:
        with self._connection_manager.get_session() as session:
            try:
                deleted_at = datetime.now(timezone.utc)
                probe = self._repository.delete_by_probe_id(session, probe_id, deleted_at)
                if probe is None:
                    raise ProbeNotFoundException(f"probe not found: {probe_id}")
                session.commit()
                return probe
            except ProbeNotFoundException:
                session.rollback()
                raise
            except OperationalError as exc:
                session.rollback()
                if "probes" in str(exc):
                    raise ProbeNotFoundException(f"probe not found: {probe_id}") from exc
                raise
            except Exception:
                session.rollback()
                raise
