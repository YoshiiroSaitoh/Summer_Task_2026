from __future__ import annotations

from datetime import datetime, timezone

from control.exception.business_exception import BusinessException
from control.exception.experiment_run_not_found_exception import ExperimentRunNotFoundException
from control.exception.experiment_run_state_conflict_exception import ExperimentRunStateConflictException
from dao.manager.db_connection_manager import DBConnectionManager
from dao.model.experiment_run_probe import ExperimentRunProbe
from dao.repository.experiment_run_probe_repository import ExperimentRunProbeRepository
from dao.repository.experiment_run_repository import ExperimentRunRepository


class ExperimentRunProbeControl:
    """Coordinates run-specific probe assignments."""

    def __init__(self, connection_manager: DBConnectionManager) -> None:
        self._connection_manager = connection_manager
        self._run_repository = ExperimentRunRepository()
        self._assignment_repository = ExperimentRunProbeRepository()

    def list_assignments(self, experiment_id: int, run_id: int) -> list[ExperimentRunProbe]:
        with self._connection_manager.get_session() as session:
            self._ensure_run(session, experiment_id, run_id)
            return list(self._assignment_repository.list_by_run_id(session, run_id))

    def add_assignment(
        self,
        experiment_id: int,
        run_id: int,
        probe_id: str,
        role: str,
    ) -> ExperimentRunProbe:
        if not probe_id or not role:
            raise BusinessException("probe_id and role must not be empty")
        now = datetime.now(timezone.utc)
        with self._connection_manager.get_session() as session:
            try:
                run = self._ensure_run(session, experiment_id, run_id)
                if run.ended_at is not None:
                    raise ExperimentRunStateConflictException("finished run cannot be modified")
                if self._assignment_repository.find_by_run_and_probe(session, run_id, probe_id) is not None:
                    raise ExperimentRunStateConflictException("probe is already assigned to this run")
                assignment = self._assignment_repository.insert(
                    session,
                    experiment_run_id=run_id,
                    probe_id=probe_id,
                    role=role,
                    created_at=now,
                    updated_at=now,
                )
                session.commit()
                return assignment
            except Exception:
                session.rollback()
                raise

    def _ensure_run(self, session, experiment_id: int, run_id: int):
        run = self._run_repository.find_by_id(session, run_id)
        if run is None or run.experiment_id != experiment_id:
            raise ExperimentRunNotFoundException(f"experiment run not found for {run_id}")
        return run
