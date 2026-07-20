from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, MetaData, Numeric, String, Table


metadata = MetaData()
temperature_logs = Table(
    "temperature_logs",
    metadata,
    Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True),
    Column("experiment_id", BigInteger().with_variant(Integer, "sqlite"), nullable=True),
    Column("experiment_run_id", BigInteger().with_variant(Integer, "sqlite"), nullable=True),
    Column("probe_id", String(64), nullable=False),
    Column("recorded_at", DateTime(timezone=True), nullable=False),
    Column("elapsed_seconds", Numeric(12, 3), nullable=True),
    Column("temperature", Numeric(5, 2), nullable=False),
)


@dataclass(slots=True)
class TemperatureLog:
    """Represents a temperature reading persisted in the database."""

    id: int | None
    experiment_id: int | None
    experiment_run_id: int | None
    probe_id: str
    recorded_at: datetime
    elapsed_seconds: float | None
    temperature: float
