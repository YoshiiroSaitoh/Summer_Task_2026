from __future__ import annotations

from datetime import datetime, timezone

from control.exception.business_exception import BusinessException
from control.exception.experiment_not_found_exception import ExperimentNotFoundException
from control.exception.experiment_state_conflict_exception import ExperimentStateConflictException
from dao.manager.db_connection_manager import DBConnectionManager
from dao.model.experiment import Experiment
from dao.model.experiment_probe import ExperimentProbe
from dao.repository.experiment_probe_repository import ExperimentProbeRepository
from dao.repository.experiment_repository import ExperimentRepository


class ExperimentControl:
    """Coordinates validation and transaction handling for experiments."""

    def __init__(self, connection_manager: DBConnectionManager) -> None:
        self._connection_manager = connection_manager
        self._experiment_repository = ExperimentRepository()
        self._experiment_probe_repository = ExperimentProbeRepository()

    def create_experiment(self, name: str) -> Experiment:
        self._validate_name(name)
        now = datetime.now(timezone.utc)
        with self._connection_manager.get_session() as session:
            try:
                experiment = self._experiment_repository.insert(
                    session,
                    name=name,
                    status="planned",
                    started_at=None,
                    ended_at=None,
                    created_at=now,
                    updated_at=now,
                )
                session.commit()
                return experiment
            except Exception:
                session.rollback()
                raise

    def list_experiments(self) -> list[Experiment]:
        with self._connection_manager.get_session() as session:
            return list(self._experiment_repository.list_all(session))

    def get_current_experiment(self) -> Experiment:
        with self._connection_manager.get_session() as session:
            experiment = self._experiment_repository.find_current(session)
            if experiment is None:
                raise ExperimentNotFoundException("current experiment not found")
            return experiment

    def get_experiment(self, experiment_id: int) -> Experiment:
        with self._connection_manager.get_session() as session:
            experiment = self._experiment_repository.find_by_id(session, experiment_id)
            if experiment is None:
                raise ExperimentNotFoundException(f"experiment not found for {experiment_id}")
            return experiment

    def start_experiment(self, experiment_id: int) -> Experiment:
        now = datetime.now(timezone.utc)
        with self._connection_manager.get_session() as session:
            try:
                current_experiment = self._experiment_repository.find_current(session)
                if current_experiment is not None and current_experiment.id != experiment_id:
                    raise ExperimentStateConflictException("another experiment is already running")
                experiment = self._experiment_repository.find_by_id(session, experiment_id)
                if experiment is None:
                    raise ExperimentNotFoundException(f"experiment not found for {experiment_id}")
                if experiment.status == "finished":
                    raise ExperimentStateConflictException("finished experiment cannot be restarted")
                if experiment.status == "running":
                    return experiment
                experiment.status = "running"
                experiment.started_at = experiment.started_at or now
                experiment.updated_at = now
                updated_experiment = self._experiment_repository.update(session, experiment)
                session.commit()
                return updated_experiment
            except Exception:
                session.rollback()
                raise

    def end_experiment(self, experiment_id: int) -> Experiment:
        now = datetime.now(timezone.utc)
        with self._connection_manager.get_session() as session:
            try:
                experiment = self._experiment_repository.find_by_id(session, experiment_id)
                if experiment is None:
                    raise ExperimentNotFoundException(f"experiment not found for {experiment_id}")
                if experiment.status != "running":
                    raise ExperimentStateConflictException("running experiment is required")
                experiment.status = "finished"
                experiment.ended_at = now
                experiment.updated_at = now
                updated_experiment = self._experiment_repository.update(session, experiment)
                session.commit()
                return updated_experiment
            except Exception:
                session.rollback()
                raise

    def list_experiment_probes(self, experiment_id: int) -> list[ExperimentProbe]:
        with self._connection_manager.get_session() as session:
            self._ensure_experiment_exists(session, experiment_id)
            return list(self._experiment_probe_repository.list_by_experiment_id(session, experiment_id))

    def add_experiment_probe(
        self,
        experiment_id: int,
        probe_id: str,
        role: str,
        valid_from: datetime | None,
        valid_to: datetime | None,
    ) -> ExperimentProbe:
        self._validate_probe_assignment(probe_id, role, valid_from, valid_to)
        now = datetime.now(timezone.utc)
        effective_valid_from = valid_from or now
        with self._connection_manager.get_session() as session:
            try:
                experiment = self._ensure_experiment_exists(session, experiment_id)
                if experiment.status == "finished":
                    raise ExperimentStateConflictException("finished experiment cannot be modified")
                active_assignment = self._experiment_probe_repository.find_active_by_probe_id(
                    session,
                    probe_id,
                    effective_valid_from,
                )
                if active_assignment is not None and active_assignment.experiment_id != experiment_id:
                    raise ExperimentStateConflictException("probe is already assigned to another experiment")
                existing_assignment = self._experiment_probe_repository.find_active_by_experiment_and_probe(
                    session,
                    experiment_id,
                    probe_id,
                    effective_valid_from,
                )
                if existing_assignment is not None:
                    raise ExperimentStateConflictException("probe is already assigned to this experiment")
                experiment_probe = self._experiment_probe_repository.insert(
                    session,
                    experiment_id=experiment_id,
                    probe_id=probe_id,
                    role=role,
                    valid_from=effective_valid_from,
                    valid_to=valid_to,
                    created_at=now,
                    updated_at=now,
                )
                session.commit()
                return experiment_probe
            except Exception:
                session.rollback()
                raise

    def resolve_experiment_for_probe(
        self,
        probe_id: str,
        effective_at: datetime,
    ) -> int | None:
        with self._connection_manager.get_session() as session:
            assignment = self._experiment_probe_repository.find_active_by_probe_id(
                session,
                probe_id,
                effective_at,
            )
            return None if assignment is None else assignment.experiment_id

    def _ensure_experiment_exists(
        self,
        session,
        experiment_id: int,
    ) -> Experiment:
        experiment = self._experiment_repository.find_by_id(session, experiment_id)
        if experiment is None:
            raise ExperimentNotFoundException(f"experiment not found for {experiment_id}")
        return experiment

    def _validate_name(self, name: str) -> None:
        if not name:
            raise BusinessException("experiment name must not be empty")

    def _validate_probe_assignment(
        self,
        probe_id: str,
        role: str,
        valid_from: datetime | None,
        valid_to: datetime | None,
    ) -> None:
        if not probe_id:
            raise BusinessException("probe_id must not be empty")
        if not role:
            raise BusinessException("role must not be empty")
        if valid_from is not None and (valid_from.tzinfo is None or valid_from.tzinfo.utcoffset(valid_from) is None):
            raise BusinessException("valid_from must be timezone aware")
        if valid_to is not None and (valid_to.tzinfo is None or valid_to.tzinfo.utcoffset(valid_to) is None):
            raise BusinessException("valid_to must be timezone aware")
        if valid_from is not None and valid_to is not None and valid_to <= valid_from:
            raise BusinessException("valid_to must be after valid_from")
