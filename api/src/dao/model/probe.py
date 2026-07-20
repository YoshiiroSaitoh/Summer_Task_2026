from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, MetaData, String, Table


metadata = MetaData()
probes = Table(
    "probes",
    metadata,
    Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True),
    Column("probe_id", String(64), nullable=False, unique=True),
    Column("deleted_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


@dataclass(slots=True)
class Probe:
    """Represents a known probe registry entry."""

    id: int | None
    probe_id: str
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime
