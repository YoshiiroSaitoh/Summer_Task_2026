from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, MetaData, String, Table


metadata = MetaData()
experiment_runs = Table(
    "experiment_runs",
    metadata,
    Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True),
    Column("experiment_id", BigInteger().with_variant(Integer, "sqlite"), nullable=False),
    Column("label", String(128), nullable=False),
    Column("started_at", DateTime(timezone=True), nullable=False),
    Column("ended_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


@dataclass(slots=True)
class ExperimentRun:
    """Represents a single acquisition run within an experiment."""

    id: int | None
    experiment_id: int
    label: str
    started_at: datetime
    ended_at: datetime | None
    created_at: datetime
    updated_at: datetime
