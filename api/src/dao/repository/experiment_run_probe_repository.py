from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from dao.exception.db_exception import DBException
from dao.model.experiment_run_probe import ExperimentRunProbe, experiment_run_probes


class ExperimentRunProbeRepository:
    """Provides access to run-specific probe assignments."""

    def insert(
        self,
        session: Session,
        experiment_run_id: int,
        probe_id: str,
        role: str,
        created_at: datetime,
        updated_at: datetime,
    ) -> ExperimentRunProbe:
        try:
            result = session.execute(
                insert(experiment_run_probes).values(
                    experiment_run_id=experiment_run_id,
                    probe_id=probe_id,
                    role=role,
                    created_at=created_at,
                    updated_at=updated_at,
                )
            )
            row = self._select_by_id(session, int(result.inserted_primary_key[0]))
            if row is None:
                raise DBException("failed to fetch inserted experiment run probe")
            return row
        except Exception as exc:  # noqa: BLE001
            raise DBException("failed to insert experiment run probe") from exc

    def list_by_run_id(self, session: Session, run_id: int) -> Sequence[ExperimentRunProbe]:
        rows = session.execute(
            self._select_columns()
            .where(experiment_run_probes.c.experiment_run_id == run_id)
            .order_by(experiment_run_probes.c.id.asc())
        ).mappings()
        return [self._to_domain(row) for row in rows]

    def find_by_run_and_probe(
        self,
        session: Session,
        run_id: int,
        probe_id: str,
    ) -> ExperimentRunProbe | None:
        row = session.execute(
            self._select_columns()
            .where(experiment_run_probes.c.experiment_run_id == run_id)
            .where(experiment_run_probes.c.probe_id == probe_id)
            .limit(1)
        ).mappings().first()
        return None if row is None else self._to_domain(row)

    def _select_by_id(self, session: Session, assignment_id: int) -> ExperimentRunProbe | None:
        row = session.execute(
            self._select_columns().where(experiment_run_probes.c.id == assignment_id)
        ).mappings().first()
        return None if row is None else self._to_domain(row)

    def _select_columns(self):
        return select(
            experiment_run_probes.c.id,
            experiment_run_probes.c.experiment_run_id,
            experiment_run_probes.c.probe_id,
            experiment_run_probes.c.role,
            experiment_run_probes.c.created_at,
            experiment_run_probes.c.updated_at,
        )

    def _to_domain(self, row: dict[str, object]) -> ExperimentRunProbe:
        return ExperimentRunProbe(
            id=int(row["id"]),
            experiment_run_id=int(row["experiment_run_id"]),
            probe_id=str(row["probe_id"]),
            role=str(row["role"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
