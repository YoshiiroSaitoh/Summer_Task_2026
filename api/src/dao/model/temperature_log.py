from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, MetaData, Numeric, String, Table


metadata = MetaData()
temperature_logs = Table(
    "temperature_logs",
    metadata,
    Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True),
    Column("probe_id", String(64), nullable=False),
    Column("recorded_at", DateTime(timezone=True), nullable=False),
    Column("temperature", Numeric(5, 2), nullable=False),
)


@dataclass(slots=True)
class TemperatureLog:
    """Represents a temperature reading persisted in the database."""

    id: int | None
    probe_id: str
    recorded_at: datetime
    temperature: float
