from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from dao.exception.db_exception import DBException
from dao.model.experiment_probe import ExperimentProbe, experiment_probes


class ExperimentProbeRepository:
    """Provides SQLAlchemy Core access to experiment probe assignments."""

    def insert(
        self,
        session: Session,
        experiment_id: int,
        probe_id: str,
        role: str,
        valid_from: datetime | None,
        valid_to: datetime | None,
        created_at: datetime,
        updated_at: datetime,
    ) -> ExperimentProbe:
        try:
            statement = insert(experiment_probes).values(
                experiment_id=experiment_id,
                probe_id=probe_id,
                role=role,
                valid_from=valid_from,
                valid_to=valid_to,
                created_at=created_at,
                updated_at=updated_at,
            )
            result = session.execute(statement)
            inserted_id = result.inserted_primary_key[0]
            row = self._select_by_id(session, int(inserted_id))
            if row is None:
                raise DBException("failed to fetch inserted experiment probe")
            return row
        except Exception as exc:  # noqa: BLE001
            raise DBException("failed to insert experiment probe") from exc

    def list_by_experiment_id(self, session: Session, experiment_id: int) -> Sequence[ExperimentProbe]:
        statement = (
            select(
                experiment_probes.c.id,
                experiment_probes.c.experiment_id,
                experiment_probes.c.probe_id,
                experiment_probes.c.role,
                experiment_probes.c.valid_from,
                experiment_probes.c.valid_to,
                experiment_probes.c.created_at,
                experiment_probes.c.updated_at,
            )
            .where(experiment_probes.c.experiment_id == experiment_id)
            .order_by(experiment_probes.c.valid_from.desc(), experiment_probes.c.id.asc())
        )
        rows = session.execute(statement).mappings()
        return [self._to_domain(row) for row in rows]

    def find_active_by_probe_id(
        self,
        session: Session,
        probe_id: str,
        effective_at: datetime,
    ) -> ExperimentProbe | None:
        statement = (
            select(
                experiment_probes.c.id,
                experiment_probes.c.experiment_id,
                experiment_probes.c.probe_id,
                experiment_probes.c.role,
                experiment_probes.c.valid_from,
                experiment_probes.c.valid_to,
                experiment_probes.c.created_at,
                experiment_probes.c.updated_at,
            )
            .where(experiment_probes.c.probe_id == probe_id)
            .where(
                (experiment_probes.c.valid_from.is_(None) | (experiment_probes.c.valid_from <= effective_at))
            )
            .where(
                (experiment_probes.c.valid_to.is_(None) | (experiment_probes.c.valid_to > effective_at))
            )
            .order_by(experiment_probes.c.valid_from.desc(), experiment_probes.c.id.desc())
            .limit(1)
        )
        row = session.execute(statement).mappings().first()
        if row is None:
            return None
        return self._to_domain(row)

    def find_active_by_experiment_and_probe(
        self,
        session: Session,
        experiment_id: int,
        probe_id: str,
        effective_at: datetime,
    ) -> ExperimentProbe | None:
        statement = (
            select(
                experiment_probes.c.id,
                experiment_probes.c.experiment_id,
                experiment_probes.c.probe_id,
                experiment_probes.c.role,
                experiment_probes.c.valid_from,
                experiment_probes.c.valid_to,
                experiment_probes.c.created_at,
                experiment_probes.c.updated_at,
            )
            .where(experiment_probes.c.experiment_id == experiment_id)
            .where(experiment_probes.c.probe_id == probe_id)
            .where(
                (experiment_probes.c.valid_from.is_(None) | (experiment_probes.c.valid_from <= effective_at))
            )
            .where(
                (experiment_probes.c.valid_to.is_(None) | (experiment_probes.c.valid_to > effective_at))
            )
            .order_by(experiment_probes.c.valid_from.desc(), experiment_probes.c.id.desc())
            .limit(1)
        )
        row = session.execute(statement).mappings().first()
        if row is None:
            return None
        return self._to_domain(row)

    def _select_by_id(self, session: Session, experiment_probe_id: int) -> ExperimentProbe | None:
        statement = select(
            experiment_probes.c.id,
            experiment_probes.c.experiment_id,
            experiment_probes.c.probe_id,
            experiment_probes.c.role,
            experiment_probes.c.valid_from,
            experiment_probes.c.valid_to,
            experiment_probes.c.created_at,
            experiment_probes.c.updated_at,
        ).where(experiment_probes.c.id == experiment_probe_id)
        row = session.execute(statement).mappings().first()
        if row is None:
            return None
        return self._to_domain(row)

    def _to_domain(self, row: dict[str, object]) -> ExperimentProbe:
        return ExperimentProbe(
            id=int(row["id"]),
            experiment_id=int(row["experiment_id"]),
            probe_id=str(row["probe_id"]),
            role=str(row["role"]),
            valid_from=row["valid_from"],
            valid_to=row["valid_to"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
