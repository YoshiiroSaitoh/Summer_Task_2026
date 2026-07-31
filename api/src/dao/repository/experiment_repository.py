from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session

from dao.exception.db_exception import DBException
from dao.model.experiment import Experiment, experiments


class ExperimentRepository:
    """Provides SQLAlchemy Core access to experiments."""

    def insert(
        self,
        session: Session,
        name: str,
        description: str | None,
        status: str,
        started_at: datetime | None,
        ended_at: datetime | None,
        completed_at: datetime | None,
        archived_at: datetime | None,
        created_at: datetime,
        updated_at: datetime,
    ) -> Experiment:
        try:
            statement = insert(experiments).values(
                name=name,
                description=description,
                status=status,
                started_at=started_at,
                ended_at=ended_at,
                completed_at=completed_at,
                archived_at=archived_at,
                created_at=created_at,
                updated_at=updated_at,
            )
            result = session.execute(statement)
            inserted_id = result.inserted_primary_key[0]
            row = self._select_by_id(session, int(inserted_id))
            if row is None:
                raise DBException("failed to fetch inserted experiment")
            return row
        except Exception as exc:  # noqa: BLE001
            raise DBException("failed to insert experiment") from exc

    def list_all(self, session: Session) -> Sequence[Experiment]:
        statement = self._select_columns().where(experiments.c.archived_at.is_(None)).order_by(experiments.c.id.asc())
        rows = session.execute(statement).mappings()
        return [self._to_domain(row) for row in rows]

    def find_by_id(self, session: Session, experiment_id: int) -> Experiment | None:
        return self._select_by_id(session, experiment_id)

    def find_current(self, session: Session) -> Experiment | None:
        statement = (
            self._select_columns()
            .where(experiments.c.status == "running")
            .where(experiments.c.archived_at.is_(None))
            .order_by(experiments.c.started_at.desc(), experiments.c.id.desc())
            .limit(1)
        )
        row = session.execute(statement).mappings().first()
        if row is None:
            return None
        return self._to_domain(row)

    def update(
        self,
        session: Session,
        experiment: Experiment,
    ) -> Experiment:
        if experiment.id is None:
            raise DBException("experiment id is required for update")
        try:
            statement = (
                update(experiments)
                .where(experiments.c.id == experiment.id)
                .values(
                    name=experiment.name,
                    description=experiment.description,
                    status=experiment.status,
                    started_at=experiment.started_at,
                    ended_at=experiment.ended_at,
                    completed_at=experiment.completed_at,
                    archived_at=experiment.archived_at,
                    created_at=experiment.created_at,
                    updated_at=experiment.updated_at,
                )
            )
            session.execute(statement)
            row = self._select_by_id(session, experiment.id)
            if row is None:
                raise DBException("failed to fetch updated experiment")
            return row
        except Exception as exc:  # noqa: BLE001
            raise DBException("failed to update experiment") from exc

    def _select_by_id(self, session: Session, experiment_id: int) -> Experiment | None:
        statement = self._select_columns().where(experiments.c.id == experiment_id)
        row = session.execute(statement).mappings().first()
        if row is None:
            return None
        return self._to_domain(row)

    def _select_columns(self):
        return select(
            experiments.c.id,
            experiments.c.name,
            experiments.c.description,
            experiments.c.status,
            experiments.c.started_at,
            experiments.c.ended_at,
            experiments.c.completed_at,
            experiments.c.archived_at,
            experiments.c.created_at,
            experiments.c.updated_at,
        )

    def _to_domain(self, row: dict[str, object]) -> Experiment:
        return Experiment(
            id=int(row["id"]),
            name=str(row["name"]),
            description=row["description"],
            status=str(row["status"]),
            started_at=row["started_at"],
            ended_at=row["ended_at"],
            completed_at=row["completed_at"],
            archived_at=row["archived_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
