from __future__ import annotations

from datetime import datetime, timezone

from control.exception.business_exception import BusinessException
from control.exception.experiment_run_not_found_exception import ExperimentRunNotFoundException
from control.exception.experiment_run_state_conflict_exception import (
    ExperimentRunStateConflictException,
)
from control.exception.experiment_not_found_exception import ExperimentNotFoundException
from dao.manager.db_connection_manager import DBConnectionManager
from dao.model.experiment_run import ExperimentRun
from dao.repository.experiment_repository import ExperimentRepository
from dao.repository.experiment_run_repository import ExperimentRunRepository


class ExperimentRunControl:
    """Coordinates validation and transaction handling for acquisition runs."""

    def __init__(self, connection_manager: DBConnectionManager) -> None:
        self._connection_manager = connection_manager
        self._experiment_repository = ExperimentRepository()
        self._experiment_run_repository = ExperimentRunRepository()

    def create_experiment_run(self, experiment_id: int, label: str) -> ExperimentRun:
        self._validate_label(label)
        now = datetime.now(timezone.utc)
        with self._connection_manager.get_session() as session:
            try:
                experiment = self._experiment_repository.find_by_id(session, experiment_id)
                if experiment is None:
                    raise ExperimentNotFoundException(f"experiment not found for {experiment_id}")
                experiment_run = self._experiment_run_repository.insert(
                    session,
                    experiment_id=experiment_id,
                    label=label,
                    started_at=None,
                    ended_at=None,
                    created_at=now,
                    updated_at=now,
                )
                session.commit()
                return experiment_run
            except Exception:
                session.rollback()
                raise

    def start_experiment_run(self, experiment_id: int, run_id: int) -> ExperimentRun:
        now = datetime.now(timezone.utc)
        with self._connection_manager.get_session() as session:
            try:
                experiment = self._experiment_repository.find_by_id(session, experiment_id)
                if experiment is None:
                    raise ExperimentNotFoundException(f"experiment not found for {experiment_id}")
                if experiment.status != "running":
                    raise ExperimentRunStateConflictException("experiment must be running before a run can start")
                experiment_run = self._experiment_run_repository.find_by_id(session, run_id)
                if experiment_run is None or experiment_run.experiment_id != experiment_id:
                    raise ExperimentRunNotFoundException(f"experiment run not found for {run_id}")
                if experiment_run.started_at is not None:
                    raise ExperimentRunStateConflictException("experiment run is already started")
                current_run = self._experiment_run_repository.find_current_by_experiment_id(session, experiment_id)
                if current_run is not None:
                    raise ExperimentRunStateConflictException("another run is already active")
                experiment_run.started_at = now
                experiment_run.updated_at = now
                updated_run = self._experiment_run_repository.update(session, experiment_run)
                session.commit()
                return updated_run
            except Exception:
                session.rollback()
                raise

    def list_experiment_runs(self, experiment_id: int) -> list[ExperimentRun]:
        with self._connection_manager.get_session() as session:
            self._ensure_experiment_exists(session, experiment_id)
            return list(self._experiment_run_repository.list_by_experiment_id(session, experiment_id))

    def get_current_experiment_run(self, experiment_id: int) -> ExperimentRun:
        with self._connection_manager.get_session() as session:
            experiment_run = self._experiment_run_repository.find_current_by_experiment_id(session, experiment_id)
            if experiment_run is None:
                raise ExperimentRunNotFoundException(f"current run not found for {experiment_id}")
            return experiment_run

    def end_experiment_run(self, experiment_id: int, run_id: int) -> ExperimentRun:
        now = datetime.now(timezone.utc)
        with self._connection_manager.get_session() as session:
            try:
                experiment_run = self._experiment_run_repository.find_by_id(session, run_id)
                if experiment_run is None or experiment_run.experiment_id != experiment_id:
                    raise ExperimentRunNotFoundException(f"experiment run not found for {run_id}")
                if experiment_run.started_at is None:
                    raise ExperimentRunStateConflictException("experiment run has not started")
                if experiment_run.ended_at is not None:
                    raise ExperimentRunStateConflictException("experiment run is already finished")
                experiment_run.ended_at = now
                experiment_run.updated_at = now
                updated_run = self._experiment_run_repository.update(session, experiment_run)
                session.commit()
                return updated_run
            except Exception:
                session.rollback()
                raise

    def _ensure_experiment_exists(self, session, experiment_id: int) -> None:
        if self._experiment_repository.find_by_id(session, experiment_id) is None:
            raise ExperimentNotFoundException(f"experiment not found for {experiment_id}")

    def _validate_label(self, label: str) -> None:
        if not label:
            raise BusinessException("label must not be empty")
