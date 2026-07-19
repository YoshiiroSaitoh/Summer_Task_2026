from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, MetaData, String, Table


metadata = MetaData()
experiment_probes = Table(
    "experiment_probes",
    metadata,
    Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True),
    Column("experiment_id", BigInteger().with_variant(Integer, "sqlite"), nullable=False),
    Column("probe_id", String(64), nullable=False),
    Column("role", String(64), nullable=False),
    Column("valid_from", DateTime(timezone=True), nullable=True),
    Column("valid_to", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


@dataclass(slots=True)
class ExperimentProbe:
    """Represents a probe assignment for an experiment."""

    id: int | None
    experiment_id: int
    probe_id: str
    role: str
    valid_from: datetime | None
    valid_to: datetime | None
    created_at: datetime
    updated_at: datetime
