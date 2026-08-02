from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, MetaData, String, Table


metadata = MetaData()
experiment_run_probes = Table(
    "experiment_run_probes",
    metadata,
    Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True),
    Column("experiment_run_id", BigInteger().with_variant(Integer, "sqlite"), nullable=False),
    Column("probe_id", String(64), nullable=False),
    Column("role", String(64), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


@dataclass(slots=True)
class ExperimentRunProbe:
    """Represents a probe assignment for one acquisition run."""

    id: int | None
    experiment_run_id: int
    probe_id: str
    role: str
    created_at: datetime
    updated_at: datetime
