from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session

from dao.exception.db_exception import DBException
from dao.model.experiment_run import ExperimentRun, experiment_runs


class ExperimentRunRepository:
    """Provides SQLAlchemy Core access to experiment runs."""

    def insert(
        self,
        session: Session,
        experiment_id: int,
        label: str,
        started_at: datetime,
        ended_at: datetime | None,
        created_at: datetime,
        updated_at: datetime,
    ) -> ExperimentRun:
        try:
            statement = insert(experiment_runs).values(
                experiment_id=experiment_id,
                label=label,
                started_at=started_at,
                ended_at=ended_at,
                created_at=created_at,
                updated_at=updated_at,
            )
            result = session.execute(statement)
            inserted_id = int(result.inserted_primary_key[0])
            row = self._select_by_id(session, inserted_id)
            if row is None:
                raise DBException("failed to fetch inserted experiment run")
            return row
        except Exception as exc:  # noqa: BLE001
            raise DBException("failed to insert experiment run") from exc

    def list_by_experiment_id(
        self,
        session: Session,
        experiment_id: int,
    ) -> Sequence[ExperimentRun]:
        statement = (
            select(
                experiment_runs.c.id,
                experiment_runs.c.experiment_id,
                experiment_runs.c.label,
                experiment_runs.c.started_at,
                experiment_runs.c.ended_at,
                experiment_runs.c.created_at,
                experiment_runs.c.updated_at,
            )
            .where(experiment_runs.c.experiment_id == experiment_id)
            .order_by(experiment_runs.c.started_at.asc(), experiment_runs.c.id.asc())
        )
        rows = session.execute(statement).mappings()
        return [self._to_domain(row) for row in rows]

    def find_current_by_experiment_id(
        self,
        session: Session,
        experiment_id: int,
    ) -> ExperimentRun | None:
        statement = (
            select(
                experiment_runs.c.id,
                experiment_runs.c.experiment_id,
                experiment_runs.c.label,
                experiment_runs.c.started_at,
                experiment_runs.c.ended_at,
                experiment_runs.c.created_at,
                experiment_runs.c.updated_at,
            )
            .where(experiment_runs.c.experiment_id == experiment_id)
            .where(experiment_runs.c.ended_at.is_(None))
            .order_by(experiment_runs.c.started_at.desc(), experiment_runs.c.id.desc())
            .limit(1)
        )
        row = session.execute(statement).mappings().first()
        if row is None:
            return None
        return self._to_domain(row)

    def find_by_id(self, session: Session, run_id: int) -> ExperimentRun | None:
        return self._select_by_id(session, run_id)

    def update(self, session: Session, run: ExperimentRun) -> ExperimentRun:
        if run.id is None:
            raise DBException("experiment run id is required for update")
        try:
            statement = (
                update(experiment_runs)
                .where(experiment_runs.c.id == run.id)
                .values(
                    label=run.label,
                    started_at=run.started_at,
                    ended_at=run.ended_at,
                    created_at=run.created_at,
                    updated_at=run.updated_at,
                )
            )
            session.execute(statement)
            row = self._select_by_id(session, run.id)
            if row is None:
                raise DBException("failed to fetch updated experiment run")
            return row
        except Exception as exc:  # noqa: BLE001
            raise DBException("failed to update experiment run") from exc

    def _select_by_id(self, session: Session, run_id: int) -> ExperimentRun | None:
        statement = select(
            experiment_runs.c.id,
            experiment_runs.c.experiment_id,
            experiment_runs.c.label,
            experiment_runs.c.started_at,
            experiment_runs.c.ended_at,
            experiment_runs.c.created_at,
            experiment_runs.c.updated_at,
        ).where(experiment_runs.c.id == run_id)
        row = session.execute(statement).mappings().first()
        if row is None:
            return None
        return self._to_domain(row)

    def _to_domain(self, row: dict[str, object]) -> ExperimentRun:
        return ExperimentRun(
            id=int(row["id"]),
            experiment_id=int(row["experiment_id"]),
            label=str(row["label"]),
            started_at=row["started_at"],
            ended_at=row["ended_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
