from __future__ import annotations

from datetime import datetime, timezone

from control.exception.temperature_not_found_exception import (
    TemperatureNotFoundException,
)
from dao.manager.db_connection_manager import DBConnectionManager
from dao.model.temperature_log import TemperatureLog
from dao.repository.temperature_log_repository import TemperatureLogRepository


class TemperatureControl:
    """Coordinates validation and transaction handling for temperature logs."""

    def __init__(self, connection_manager: DBConnectionManager) -> None:
        self._connection_manager = connection_manager
        self._repository = TemperatureLogRepository()

    def register_temperature(
        self,
        probe_id: str,
        recorded_at: datetime | None,
        temperature: float,
    ) -> TemperatureLog:
        """Registers a new temperature log.

        Args:
            probe_id:
                Probe identifier.
            recorded_at:
                Time of measurement. If omitted, the current UTC time is used.
            temperature:
                Measured temperature.

        Returns:
            The persisted temperature log.
        """
        effective_recorded_at = recorded_at or datetime.now(timezone.utc)
        self._validate_temperature(probe_id, effective_recorded_at, temperature)
        with self._connection_manager.get_session() as session:
            try:
                temperature_log = self._repository.insert(
                    session,
                    probe_id=probe_id,
                    recorded_at=effective_recorded_at,
                    temperature=temperature,
                )
                session.commit()
                return temperature_log
            except Exception:
                session.rollback()
                raise

    def register_temperatures(
        self,
        temperature_items: list[tuple[str, datetime | None, float]],
    ) -> list[TemperatureLog]:
        """Registers multiple temperature logs in a single transaction."""
        normalized_items = [
            (
                probe_id,
                recorded_at or datetime.now(timezone.utc),
                temperature,
            )
            for probe_id, recorded_at, temperature in temperature_items
        ]
        for probe_id, recorded_at, temperature in normalized_items:
            self._validate_temperature(probe_id, recorded_at, temperature)

        with self._connection_manager.get_session() as session:
            try:
                temperature_logs = [
                    self._repository.insert(
                        session,
                        probe_id=probe_id,
                        recorded_at=recorded_at,
                        temperature=temperature,
                    )
                    for probe_id, recorded_at, temperature in normalized_items
                ]
                session.commit()
                return temperature_logs
            except Exception:
                session.rollback()
                raise

    def get_latest_temperature(self, probe_id: str) -> TemperatureLog:
        """Gets the latest temperature log for a probe.

        Args:
            probe_id:
                Probe identifier.

        Returns:
            The latest temperature log.

        Raises:
            TemperatureNotFoundException:
                Raised when no temperature log exists for the probe.
        """
        with self._connection_manager.get_session() as session:
            temperature_log = self._repository.find_latest_by_probe_id(session, probe_id)
            if temperature_log is None:
                raise TemperatureNotFoundException(f"temperature not found for {probe_id}")
            return temperature_log

    def list_temperature_logs(
        self,
        probe_id: str | None,
        start_at: datetime | None,
        end_at: datetime | None,
    ) -> list[TemperatureLog]:
        """Lists temperature logs filtered by identifier and time range.

        Args:
            probe_id:
                Probe identifier filter.
            start_at:
                Inclusive start time filter.
            end_at:
                Inclusive end time filter.

        Returns:
            Matching temperature logs.
        """
        with self._connection_manager.get_session() as session:
            return list(
                self._repository.find_by_probe_id_and_range(
                    session,
                    probe_id,
                    start_at,
                    end_at,
                )
            )

    def _validate_temperature(
        self,
        probe_id: str,
        recorded_at: datetime,
        temperature: float,
    ) -> None:
        if not probe_id:
            raise ValueError("probe_id must not be empty")
        if recorded_at.tzinfo is None or recorded_at.tzinfo.utcoffset(recorded_at) is None:
            raise ValueError("recorded_at must be timezone aware")
        if not (-100.0 <= temperature <= 200.0):
            raise ValueError("temperature is out of range")
