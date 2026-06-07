from __future__ import annotations

import logging


class BaseApiImpl:
    """Provides shared API implementation behavior."""

    def __init__(self) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)

    def log_request(self, method: str, path: str, trace_id: str | None = None) -> None:
        """Logs an incoming request.

        Args:
            method:
                HTTP method.
            path:
                Request path.
            trace_id:
                Optional trace identifier.
        """
        self._logger.info(
            "request received",
            extra={"method": method, "path": path, "trace_id": trace_id},
        )

    def log_response(self, status_code: int, trace_id: str | None = None) -> None:
        """Logs an outgoing response.

        Args:
            status_code:
                HTTP status code.
            trace_id:
                Optional trace identifier.
        """
        self._logger.info(
            "response sent",
            extra={"status_code": status_code, "trace_id": trace_id},
        )
