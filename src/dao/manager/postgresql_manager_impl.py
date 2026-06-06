from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


class PostgreSQLManagerImpl:
    """Creates and reuses a PostgreSQL SQLAlchemy engine and sessions."""

    _engine: Engine | None = None
    _session_factory: sessionmaker[Session] | None = None

    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._ensure_engine()

    def _ensure_engine(self) -> None:
        if PostgreSQLManagerImpl._engine is None:
            PostgreSQLManagerImpl._engine = create_engine(self._database_url, pool_pre_ping=True)
            PostgreSQLManagerImpl._session_factory = sessionmaker(
                bind=PostgreSQLManagerImpl._engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=False,
            )

    @contextmanager
    def get_session(self) -> Iterator[Session]:
        """Yields a SQLAlchemy session."""
        if PostgreSQLManagerImpl._session_factory is None:
            raise RuntimeError("session factory is not initialized")
        session = PostgreSQLManagerImpl._session_factory()
        try:
            yield session
        finally:
            session.close()
