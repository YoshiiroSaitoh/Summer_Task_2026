from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import Select, insert, select
from sqlalchemy.orm import Session

from src.dao.exception.db_exception import DBException
from src.dao.model.temperature_log import TemperatureLog, temperature_logs


class TemperatureLogRepository:
    """Provides SQLAlchemy Core access to temperature_logs."""

    def insert(
        self,
        session: Session,
        probe_id: str,
        recorded_at: datetime,
        temperature: float,
    ) -> TemperatureLog:
        """Inserts a temperature log and returns the persisted entity."""
        try:
            statement = insert(temperature_logs).values(
                probe_id=probe_id,
                recorded_at=recorded_at,
                temperature=temperature,
            )
            result = session.execute(statement)
            inserted_id = result.inserted_primary_key[0]
            row = session.execute(
                select(
                    temperature_logs.c.id,
                    temperature_logs.c.probe_id,
                    temperature_logs.c.recorded_at,
                    temperature_logs.c.temperature,
                ).where(temperature_logs.c.id == inserted_id)
            ).mappings().one()
            return TemperatureLog(**row)
        except Exception as exc:  # noqa: BLE001
            raise DBException("failed to insert temperature log") from exc

    def find_latest_by_probe_id(
        self,
        session: Session,
        probe_id: str,
    ) -> TemperatureLog | None:
        """Returns the latest temperature log for a probe."""
        statement = (
            select(
                temperature_logs.c.id,
                temperature_logs.c.probe_id,
                temperature_logs.c.recorded_at,
                temperature_logs.c.temperature,
            )
            .where(temperature_logs.c.probe_id == probe_id)
            .order_by(temperature_logs.c.recorded_at.desc(), temperature_logs.c.id.desc())
            .limit(1)
        )
        row = session.execute(statement).mappings().first()
        if row is None:
            return None
        return TemperatureLog(**row)

    def find_by_probe_id_and_range(
        self,
        session: Session,
        probe_id: str | None,
        start_at: datetime | None,
        end_at: datetime | None,
    ) -> Sequence[TemperatureLog]:
        """Returns temperature logs filtered by probe identifier and time range."""
        statement: Select[tuple[int, str, datetime, float]] = select(
            temperature_logs.c.id,
            temperature_logs.c.probe_id,
            temperature_logs.c.recorded_at,
            temperature_logs.c.temperature,
        )
        if probe_id is not None:
            statement = statement.where(temperature_logs.c.probe_id == probe_id)
        if start_at is not None:
            statement = statement.where(temperature_logs.c.recorded_at >= start_at)
        if end_at is not None:
            statement = statement.where(temperature_logs.c.recorded_at <= end_at)

        rows = session.execute(statement.order_by(temperature_logs.c.recorded_at.asc())).mappings()
        return [TemperatureLog(**row) for row in rows]
