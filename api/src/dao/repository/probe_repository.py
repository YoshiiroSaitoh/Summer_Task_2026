from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import insert, select, update
from sqlalchemy.orm import Session

from dao.exception.db_exception import DBException
from dao.model.probe import Probe, probes


class ProbeRepository:
    """Provides SQLAlchemy Core access to probe registry entries."""

    def upsert_observed_probe(
        self,
        session: Session,
        probe_id: str,
        observed_at: datetime,
    ) -> Probe | None:
        existing = self.find_by_probe_id(session, probe_id)
        try:
            if existing is None:
                statement = insert(probes).values(
                    probe_id=probe_id,
                    deleted_at=None,
                    created_at=observed_at,
                    updated_at=observed_at,
                )
                result = session.execute(statement)
                inserted_id = result.inserted_primary_key[0]
                row = self._select_by_id(session, int(inserted_id))
                if row is None:
                    raise DBException("failed to fetch inserted probe")
                return row

            statement = (
                update(probes)
                .where(probes.c.id == existing.id)
                .values(
                    deleted_at=None,
                    updated_at=observed_at,
                )
            )
            session.execute(statement)
            row = self._select_by_id(session, existing.id)
            if row is None:
                raise DBException("failed to fetch updated probe")
            return row
        except Exception as exc:  # noqa: BLE001
            raise DBException("failed to upsert probe") from exc

    def list_active(self, session: Session) -> Sequence[Probe]:
        statement = (
            select(
                probes.c.id,
                probes.c.probe_id,
                probes.c.deleted_at,
                probes.c.created_at,
                probes.c.updated_at,
            )
            .where(probes.c.deleted_at.is_(None))
            .order_by(probes.c.updated_at.desc(), probes.c.id.desc())
        )
        rows = session.execute(statement).mappings()
        return [self._to_domain(row) for row in rows]

    def delete_by_probe_id(self, session: Session, probe_id: str, deleted_at: datetime) -> Probe | None:
        existing = self.find_by_probe_id(session, probe_id)
        if existing is None or existing.deleted_at is not None:
            return None

        try:
            statement = (
                update(probes)
                .where(probes.c.id == existing.id)
                .values(
                    deleted_at=deleted_at,
                    updated_at=deleted_at,
                )
            )
            session.execute(statement)
            return self._select_by_id(session, existing.id)
        except Exception as exc:  # noqa: BLE001
            raise DBException("failed to delete probe") from exc

    def find_by_probe_id(self, session: Session, probe_id: str) -> Probe | None:
        statement = (
            select(
                probes.c.id,
                probes.c.probe_id,
                probes.c.deleted_at,
                probes.c.created_at,
                probes.c.updated_at,
            )
            .where(probes.c.probe_id == probe_id)
            .limit(1)
        )
        row = session.execute(statement).mappings().first()
        if row is None:
            return None
        return self._to_domain(row)

    def _select_by_id(self, session: Session, probe_id: int) -> Probe | None:
        statement = select(
            probes.c.id,
            probes.c.probe_id,
            probes.c.deleted_at,
            probes.c.created_at,
            probes.c.updated_at,
        ).where(probes.c.id == probe_id)
        row = session.execute(statement).mappings().first()
        if row is None:
            return None
        return self._to_domain(row)

    def _to_domain(self, row: dict[str, object]) -> Probe:
        return Probe(
            id=int(row["id"]),
            probe_id=str(row["probe_id"]),
            deleted_at=row["deleted_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
