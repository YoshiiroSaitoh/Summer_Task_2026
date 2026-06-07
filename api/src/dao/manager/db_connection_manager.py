from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Protocol

from sqlalchemy.orm import Session


class DBConnectionManager(Protocol):
    """Provides SQLAlchemy sessions to the application."""

    def get_session(self) -> AbstractContextManager[Session]:
        """Returns a context manager for a SQLAlchemy session."""
