from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, MetaData, String, Table


metadata = MetaData()
experiments = Table(
    "experiments",
    metadata,
    Column("id", BigInteger().with_variant(Integer, "sqlite"), primary_key=True),
    Column("name", String(128), nullable=False),
    Column("description", String(512), nullable=True),
    Column("status", String(32), nullable=False),
    Column("started_at", DateTime(timezone=True), nullable=True),
    Column("ended_at", DateTime(timezone=True), nullable=True),
    Column("completed_at", DateTime(timezone=True), nullable=True),
    Column("archived_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


@dataclass(slots=True)
class Experiment:
    """Represents an experiment persisted in the database."""

    id: int | None
    name: str
    description: str | None
    status: str
    started_at: datetime | None
    ended_at: datetime | None
    completed_at: datetime | None
    archived_at: datetime | None
    created_at: datetime
    updated_at: datetime
