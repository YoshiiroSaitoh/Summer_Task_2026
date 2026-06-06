from __future__ import annotations

from datetime import datetime

from src.control.exception.temperature_not_found_exception import (
    TemperatureNotFoundException,
)
from src.dao.manager.db_connection_manager import DBConnectionManager
from src.dao.model.temperature_log import TemperatureLog
from src.dao.repository.temperature_log_repository import TemperatureLogRepository


class TemperatureControl:
    """Coordinates validation and transaction handling for temperature logs."""

    def __init__(self, connection_manager: DBConnectionManager) -> None:
        self._connection_manager = connection_manager
        self._repository = TemperatureLogRepository()

    def register_temperature(
        self,
        probe_id: str,
        recorded_at: datetime,
        temperature: float,
    ) -> TemperatureLog:
        """Registers a new temperature log.

        Args:
            probe_id:
                Probe identifier.
            recorded_at:
                Time of measurement.
            temperature:
                Measured temperature.

        Returns:
            The persisted temperature log.
        """
        self._validate_temperature(probe_id, recorded_at, temperature)
        with self._connection_manager.get_session() as session:
            try:
                temperature_log = self._repository.insert(
                    session,
                    probe_id=probe_id,
                    recorded_at=recorded_at,
                    temperature=temperature,
                )
                session.commit()
                return temperature_log
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
